from typing import Dict
from sqlalchemy.orm import Session
from ..models.db_models import Student

class StatisticsService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_summary(self) -> Dict[str, any]:
        students = self.db.query(Student).all()
        totals = [student.total for student in students]
        if not totals:
            return {
                "average": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "pass_rate": 0.0,
                "distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            }

        totals_sorted = sorted(totals)
        average = sum(totals) / len(totals)
        median = totals_sorted[len(totals) // 2]
        variance = sum((x - average) ** 2 for x in totals) / len(totals)
        std_dev = variance ** 0.5
        pass_rate = len([score for score in totals if score >= 60]) / len(totals) * 100

        distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for score in totals:
            if score >= 90:
                distribution["A"] += 1
            elif score >= 80:
                distribution["B"] += 1
            elif score >= 70:
                distribution["C"] += 1
            elif score >= 60:
                distribution["D"] += 1
            else:
                distribution["F"] += 1

        return {
            "average": round(average, 2),
            "median": round(median, 2),
            "std_dev": round(std_dev, 2),
            "min_score": round(min(totals), 2),
            "max_score": round(max(totals), 2),
            "pass_rate": round(pass_rate, 2),
            "distribution": distribution
        }

    def distribution_data(self) -> Dict[str, any]:
        students = self.db.query(Student).all()
        totals = [student.total for student in students]
        bins = list(range(0, 101, 10))
        counts = [0] * (len(bins) - 1)
        for score in totals:
            for idx in range(len(bins) - 1):
                if bins[idx] <= score < bins[idx + 1]:
                    counts[idx] += 1
                    break
        return {"bins": bins, "counts": counts, "totals": totals}
