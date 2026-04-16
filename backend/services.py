import random
import string
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import io
import base64
from .models import Student, Grade, ScoringScheme, AdjustmentRule, StatisticsResponse, AtRiskStudent, DistributionData

class GradeService:
    def __init__(self):
        self.students: List[Student] = []
        self.scoring_schemes: List[ScoringScheme] = []
        self.adjustment_rules: List[AdjustmentRule] = []
        self.backup_status = {"last_backup": None, "status": "idle", "message": None}

    def generate_mock_data(self, count: int = 30) -> List[Student]:
        """生成模擬學生數據"""
        self.students = []
        for i in range(count):
            name = ''.join(random.choices(string.ascii_letters, k=3)) + str(i+1)
            student_id = f"2024{random.randint(10000, 99999)}"
            usual = round(random.uniform(60, 100), 1)
            midterm = round(random.uniform(50, 100), 1)
            final = round(random.uniform(40, 100), 1)
            total = round(usual * 0.3 + midterm * 0.3 + final * 0.4, 1)

            grade = Grade(
                student_id=student_id,
                usual=usual,
                midterm=midterm,
                final=final,
                total=total
            )
            student = Student(
                name=name,
                student_id=student_id,
                grades=grade
            )
            self.students.append(student)
        return self.students

    def import_grades(self, file_data: str, file_type: str) -> Dict[str, Any]:
        """匯入成績數據"""
        try:
            if file_type == 'csv':
                data = pd.read_csv(io.StringIO(base64.b64decode(file_data).decode('utf-8')))
            elif file_type == 'excel':
                data = pd.read_excel(io.BytesIO(base64.b64decode(file_data)))
            else:
                raise ValueError("不支持的檔案格式")

            # 驗證欄位
            required_cols = ['name', 'student_id', 'usual', 'midterm', 'final']
            if not all(col in data.columns for col in required_cols):
                raise ValueError("檔案缺少必要欄位")

            imported_count = 0
            for _, row in data.iterrows():
                if pd.isna(row['name']) or pd.isna(row['student_id']):
                    continue
                grade = Grade(
                    student_id=str(row['student_id']),
                    usual=float(row['usual']) if not pd.isna(row['usual']) else 0,
                    midterm=float(row['midterm']) if not pd.isna(row['midterm']) else 0,
                    final=float(row['final']) if not pd.isna(row['final']) else 0,
                    total=None
                )
                student = Student(
                    name=str(row['name']),
                    student_id=str(row['student_id']),
                    grades=grade
                )
                self.students.append(student)
                imported_count += 1

            return {"success": True, "imported_count": imported_count, "message": f"成功匯入 {imported_count} 筆數據"}
        except Exception as e:
            return {"success": False, "message": f"匯入失敗: {str(e)}"}

    def get_students(self) -> List[Student]:
        """獲取所有學生"""
        return self.students

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """根據學號獲取學生"""
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def calculate_statistics(self) -> StatisticsResponse:
        """計算成績統計"""
        if not self.students:
            return StatisticsResponse(
                average=0, median=0, std_dev=0, min_score=0, max_score=0,
                pass_rate=0, distribution={}
            )

        totals = [s.grades.total or 0 for s in self.students]
        average = sum(totals) / len(totals)
        median = sorted(totals)[len(totals)//2]
        std_dev = (sum((x - average)**2 for x in totals) / len(totals))**0.5
        min_score = min(totals)
        max_score = max(totals)
        pass_rate = len([t for t in totals if t >= 60]) / len(totals) * 100

        # 分佈
        distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for total in totals:
            if total >= 90: distribution["A"] += 1
            elif total >= 80: distribution["B"] += 1
            elif total >= 70: distribution["C"] += 1
            elif total >= 60: distribution["D"] += 1
            else: distribution["F"] += 1

        return StatisticsResponse(
            average=round(average, 2),
            median=round(median, 2),
            std_dev=round(std_dev, 2),
            min_score=min_score,
            max_score=max_score,
            pass_rate=round(pass_rate, 2),
            distribution=distribution
        )

    def identify_at_risk_students(self, threshold: float = 60) -> List[AtRiskStudent]:
        """識別風險學生"""
        at_risk = []
        for student in self.students:
            total = student.grades.total or 0
            risk_level = "low"
            reasons = []

            if total < threshold:
                risk_level = "high"
                reasons.append(f"總成績 {total} 分低於 {threshold} 分")
            elif total < threshold + 10:
                risk_level = "medium"
                reasons.append(f"總成績 {total} 分接近不及格")

            if student.grades.final < 50:
                reasons.append("期末成績過低")
                if risk_level == "low":
                    risk_level = "medium"

            if reasons:
                at_risk.append(AtRiskStudent(
                    student=student,
                    risk_level=risk_level,
                    reasons=reasons
                ))

        return sorted(at_risk, key=lambda x: x.student.grades.total or 0)

    def get_distribution_data(self) -> DistributionData:
        """獲取成績分佈數據"""
        if not self.students:
            return DistributionData(grades=[], bins=[], counts=[])

        totals = [s.grades.total or 0 for s in self.students]
        bins = list(range(0, 101, 10))
        counts = [0] * (len(bins) - 1)

        for total in totals:
            for i in range(len(bins) - 1):
                if bins[i] <= total < bins[i+1]:
                    counts[i] += 1
                    break

        return DistributionData(grades=totals, bins=bins, counts=counts)

    def apply_scoring_scheme(self, scheme: ScoringScheme) -> Dict[str, Any]:
        """應用自訂評分方案"""
        try:
            for student in self.students:
                g = student.grades
                total = (g.usual * scheme.weights.get('usual', 0) +
                        g.midterm * scheme.weights.get('midterm', 0) +
                        g.final * scheme.weights.get('final', 0))
                student.grades.total = round(total, 1)
                student.updated_at = datetime.now()

            self.scoring_schemes.append(scheme)
            return {"success": True, "message": f"已應用評分方案: {scheme.name}"}
        except Exception as e:
            return {"success": False, "message": f"應用失敗: {str(e)}"}

    def apply_adjustment_rule(self, rule: AdjustmentRule) -> Dict[str, Any]:
        """應用自動調整規則"""
        try:
            affected_count = 0
            for student in self.students:
                # 簡單條件檢查，這裡可以擴展為更複雜的邏輯
                if "attendance" in rule.condition:
                    # 模擬出勤率
                    attendance = random.uniform(70, 100)
                    if eval(rule.condition.replace("attendance", str(attendance))):
                        student.grades.total = (student.grades.total or 0) + rule.adjustment
                        student.grades.total = max(0, min(100, student.grades.total))
                        affected_count += 1

            self.adjustment_rules.append(rule)
            return {"success": True, "affected_count": affected_count, "message": f"調整了 {affected_count} 位學生的成績"}
        except Exception as e:
            return {"success": False, "message": f"應用失敗: {str(e)}"}

    def edit_grade(self, student_id: str, grade_type: str, new_value: float, reason: str) -> Dict[str, Any]:
        """編輯單個成績"""
        student = self.get_student_by_id(student_id)
        if not student:
            return {"success": False, "message": "學生不存在"}

        try:
            setattr(student.grades, grade_type, new_value)
            # 重新計算總分（假設預設權重）
            g = student.grades
            g.total = round(g.usual * 0.3 + g.midterm * 0.3 + g.final * 0.4, 1)
            student.updated_at = datetime.now()

            # 記錄修改歷史（這裡簡化，實際應存到數據庫）
            print(f"修改記錄: {student_id} 的 {grade_type} 從 ... 改為 {new_value}, 原因: {reason}")

            return {"success": True, "message": "成績已更新"}
        except Exception as e:
            return {"success": False, "message": f"更新失敗: {str(e)}"}

    def export_report(self, format_type: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """匯出成績報告"""
        try:
            data = []
            for student in self.students:
                if filters:
                    # 簡單篩選邏輯
                    if 'min_score' in filters and (student.grades.total or 0) < filters['min_score']:
                        continue
                    if 'max_score' in filters and (student.grades.total or 0) > filters['max_score']:
                        continue

                data.append({
                    "學號": student.student_id,
                    "姓名": student.name,
                    "平時": student.grades.usual,
                    "期中": student.grades.midterm,
                    "期末": student.grades.final,
                    "總分": student.grades.total
                })

            df = pd.DataFrame(data)

            if format_type == 'csv':
                output = df.to_csv(index=False)
            elif format_type == 'excel':
                output = io.BytesIO()
                df.to_excel(output, index=False)
                output = base64.b64encode(output.getvalue()).decode()
            else:
                return {"success": False, "message": "不支持的匯出格式"}

            return {"success": True, "data": output, "filename": f"grade_report.{format_type}"}
        except Exception as e:
            return {"success": False, "message": f"匯出失敗: {str(e)}"}

    def trigger_backup(self) -> Dict[str, Any]:
        """觸發備份"""
        try:
            self.backup_status["status"] = "running"
            # 模擬備份過程
            import time
            time.sleep(1)  # 模擬延遲

            self.backup_status["last_backup"] = datetime.now()
            self.backup_status["status"] = "success"
            self.backup_status["message"] = "備份完成"

            return {"success": True, "message": "備份成功"}
        except Exception as e:
            self.backup_status["status"] = "failed"
            self.backup_status["message"] = str(e)
            return {"success": False, "message": f"備份失敗: {str(e)}"}

    def get_backup_status(self) -> Dict[str, Any]:
        """獲取備份狀態"""
        return self.backup_status