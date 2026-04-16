import pandas as pd
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..config import REQUIRED_IMPORT_COLUMNS, MAX_IMPORT_ROWS
from ..utils import decode_base64_file, dataframe_from_file, check_required_columns, validate_import_row, prepare_import_preview
from ..models.db_models import Student

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def preview_import(self, file_data: str, file_type: str) -> Dict[str, Any]:
        file_bytes = decode_base64_file(file_data)
        df = dataframe_from_file(file_bytes, file_type)
        missing = check_required_columns(df)
        if missing:
            raise ValueError(f"缺少必要欄位: {', '.join(missing)}")
        if len(df) > MAX_IMPORT_ROWS:
            raise ValueError(f"最多支持匯入 {MAX_IMPORT_ROWS} 筆記錄")
        return prepare_import_preview(df)

    def import_file(self, file_data: str, file_type: str) -> Dict[str, Any]:
        file_bytes = decode_base64_file(file_data)
        df = dataframe_from_file(file_bytes, file_type)
        missing = check_required_columns(df)
        if missing:
            raise ValueError(f"缺少必要欄位: {', '.join(missing)}")
        if len(df) > MAX_IMPORT_ROWS:
            raise ValueError(f"最多支持匯入 {MAX_IMPORT_ROWS} 筆記錄")

        imported = 0
        skipped = 0
        errors: List[str] = []

        for index, row in df.iterrows():
            record = row.to_dict()
            row_errors = validate_import_row(record)
            if row_errors:
                errors.append(f"第 {index + 1} 行: {'; '.join(row_errors)}")
                skipped += 1
                continue

            student_id = str(record["student_id"]).strip()
            existing = self.db.query(Student).filter(Student.student_id == student_id).first()
            usual = float(record["usual"])
            midterm = float(record["midterm"])
            final = float(record["final"])
            total = round(usual * 0.3 + midterm * 0.3 + final * 0.4, 2)

            if existing:
                existing.name = str(record["name"]).strip()
                existing.usual = usual
                existing.midterm = midterm
                existing.final = final
                existing.total = total
                imported += 1
            else:
                student = Student(
                    student_id=student_id,
                    name=str(record["name"]).strip(),
                    usual=usual,
                    midterm=midterm,
                    final=final,
                    total=total
                )
                self.db.add(student)
                imported += 1

        self.db.commit()
        message = f"匯入完成: {imported} 筆，跳過 {skipped} 筆。"
        if errors:
            message += " 詳細錯誤請查看 errors。"
        return {"success": True, "imported": imported, "skipped": skipped, "errors": errors, "message": message}
