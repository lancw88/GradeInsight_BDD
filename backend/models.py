from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class Grade(BaseModel):
    student_id: str
    usual: float = Field(..., ge=0, le=100, description="平時成績")
    midterm: float = Field(..., ge=0, le=100, description="期中成績")
    final: float = Field(..., ge=0, le=100, description="期末成績")
    total: Optional[float] = Field(None, ge=0, le=100, description="總成績")

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    student_id: str
    grades: Grade
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ImportRequest(BaseModel):
    file_data: str  # Base64 encoded file content
    file_type: str  # 'csv' or 'excel'

class ScoringScheme(BaseModel):
    name: str
    weights: Dict[str, float]  # e.g., {"usual": 0.3, "midterm": 0.3, "final": 0.4}
    description: Optional[str] = None

class AdjustmentRule(BaseModel):
    name: str
    condition: str  # e.g., "attendance < 80"
    adjustment: float  # points to add/subtract
    description: Optional[str] = None

class ExportRequest(BaseModel):
    format: str = "pdf"  # 'pdf', 'csv', 'excel'
    filters: Optional[Dict[str, Any]] = None

class EditGradeRequest(BaseModel):
    student_id: str
    grade_type: str  # 'usual', 'midterm', 'final'
    new_value: float
    reason: str

class BackupStatus(BaseModel):
    last_backup: Optional[datetime] = None
    status: str = "idle"  # 'idle', 'running', 'success', 'failed'
    message: Optional[str] = None

class StatisticsResponse(BaseModel):
    average: float
    median: float
    std_dev: float
    min_score: float
    max_score: float
    pass_rate: float
    distribution: Dict[str, int]  # e.g., {"A": 10, "B": 15, ...}

class AtRiskStudent(BaseModel):
    student: Student
    risk_level: str  # 'high', 'medium', 'low'
    reasons: List[str]

class DistributionData(BaseModel):
    grades: List[float]
    bins: List[float]
    counts: List[int]

class StudentDetail(BaseModel):
    student: Student
    trend: List[Dict[str, Any]]  # historical grades
    statistics: Dict[str, float]