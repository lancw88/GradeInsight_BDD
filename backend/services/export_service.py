import base64
import io
import pandas as pd
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..models.db_models import Student

class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def build_export_dataframe(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        students = self.db.query(Student).all()
        rows = []
        for student in students:
            if filters:
                if filters.get("student_id") and student.student_id != filters.get("student_id"):
                    continue
                total = student.total
                if filters.get("min_score") is not None and total < filters.get("min_score"):
                    continue
                if filters.get("max_score") is not None and total > filters.get("max_score"):
                    continue
            rows.append({
                "學號": student.student_id,
                "姓名": student.name,
                "平時": student.usual,
                "期中": student.midterm,
                "期末": student.final,
                "總成績": student.total
            })
        return pd.DataFrame(rows)

    def export(self, format_type: str, filters: Optional[Dict] = None) -> Dict[str, any]:
        df = self.build_export_dataframe(filters)
        if format_type == "csv":
            content = df.to_csv(index=False)
            payload = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        elif format_type == "excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            payload = base64.b64encode(buffer.getvalue()).decode("utf-8")
        else:
            raise ValueError("不支持的匯出格式")
        return {"success": True, "filename": f"grade_report.{format_type}", "data": payload}
