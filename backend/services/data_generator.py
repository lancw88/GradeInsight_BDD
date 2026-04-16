import random
import string
from sqlalchemy.orm import Session
from ..models.db_models import Student

class DataGenerator:
    def __init__(self, db: Session):
        self.db = db

    def generate_mock_data(self, count: int = 30) -> dict:
        existing = self.db.query(Student).count()
        if existing:
            return {"success": False, "message": "資料庫已有現有資料，請先清除或使用其他方法生成"}

        for i in range(count):
            name = f"學生{random.randint(100,999)}"
            student_id = f"2024{random.randint(10000, 99999)}"
            usual = round(random.uniform(60, 100), 1)
            midterm = round(random.uniform(50, 100), 1)
            final = round(random.uniform(40, 100), 1)
            total = round(usual * 0.3 + midterm * 0.3 + final * 0.4, 2)
            student = Student(
                name=name,
                student_id=student_id,
                usual=usual,
                midterm=midterm,
                final=final,
                total=total
            )
            self.db.add(student)
        self.db.commit()
        return {"success": True, "message": f"已生成 {count} 筆模擬資料"}
