from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.db_models import Student, GradeEditLog, ScoringScheme, AdjustmentRule
from datetime import datetime

class GradeService:
    def __init__(self, db: Session):
        self.db = db

    def list_students(self) -> List[Student]:
        return self.db.query(Student).order_by(Student.name).all()

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.db.query(Student).filter(Student.student_id == student_id).first()

    def edit_grade(self, student_id: str, grade_type: str, new_value: float, reason: str) -> dict:
        student = self.get_student(student_id)
        if not student:
            return {"success": False, "message": "學生不存在"}
        if grade_type not in {"usual", "midterm", "final"}:
            return {"success": False, "message": "成績類型錯誤"}

        old_value = getattr(student, grade_type)
        setattr(student, grade_type, new_value)
        student.total = round(student.usual * 0.3 + student.midterm * 0.3 + student.final * 0.4, 2)
        student.updated_at = datetime.utcnow()

        log = GradeEditLog(
            student_id=student.id,
            grade_type=grade_type,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            edited_at=datetime.utcnow(),
            editor="系統"
        )
        self.db.add(log)
        self.db.commit()
        return {"success": True, "message": "成績已更新", "student_id": student_id}

    def apply_scoring_scheme(self, scheme_data: dict) -> dict:
        scheme = ScoringScheme(
            name=scheme_data["name"],
            usual_weight=scheme_data.get("usual_weight", 0.3),
            midterm_weight=scheme_data.get("midterm_weight", 0.3),
            final_weight=scheme_data.get("final_weight", 0.4),
            description=scheme_data.get("description")
        )
        self.db.add(scheme)
        self.db.commit()

        students = self.list_students()
        for student in students:
            student.total = round(
                student.usual * scheme.usual_weight +
                student.midterm * scheme.midterm_weight +
                student.final * scheme.final_weight,
                2
            )
        self.db.commit()
        return {"success": True, "message": f"已套用評分方案: {scheme.name}"}

    def apply_adjustment_rule(self, rule_data: dict) -> dict:
        rule = AdjustmentRule(
            name=rule_data["name"],
            condition=rule_data["condition"],
            adjustment=rule_data["adjustment"],
            description=rule_data.get("description")
        )
        self.db.add(rule)
        self.db.commit()

        affected = 0
        for student in self.list_students():
            if "attendance" in rule.condition:
                attendance = 100 - student.final * 0.1
                try:
                    if eval(rule.condition.replace("attendance", str(attendance))):
                        student.total = max(0.0, min(100.0, student.total + rule.adjustment))
                        affected += 1
                except Exception:
                    continue
        self.db.commit()
        return {"success": True, "affected": affected, "message": f"已套用規則: {rule.name}"}
