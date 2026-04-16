from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    usual = Column(Float, default=0.0)
    midterm = Column(Float, default=0.0)
    final = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    edits = relationship("GradeEditLog", back_populates="student")

class GradeEditLog(Base):
    __tablename__ = "grade_edit_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    grade_type = Column(String(50), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    edited_at = Column(DateTime, default=datetime.utcnow)
    editor = Column(String(100), default="系統")

    student = relationship("Student", back_populates="edits")

class ScoringScheme(Base):
    __tablename__ = "scoring_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    usual_weight = Column(Float, default=0.3)
    midterm_weight = Column(Float, default=0.3)
    final_weight = Column(Float, default=0.4)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdjustmentRule(Base):
    __tablename__ = "adjustment_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    condition = Column(String(255), nullable=False)
    adjustment = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
