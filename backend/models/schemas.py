from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GradeCreate(BaseModel):
    name: str
    student_id: str
    usual: float = Field(..., ge=0, le=100)
    midterm: float = Field(..., ge=0, le=100)
    final: float = Field(..., ge=0, le=100)

class StudentCreate(GradeCreate):
    pass

class GradeResponse(BaseModel):
    usual: float
    midterm: float
    final: float
    total: float

class StudentResponse(BaseModel):
    id: int
    student_id: str
    name: str
    usual: float
    midterm: float
    final: float
    total: float
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ImportPreviewResponse(BaseModel):
    preview: List[Dict[str, Any]]
    columns: List[str]
    rows: int

class ImportRequest(BaseModel):
    file_data: str
    file_type: str

class ImportResultResponse(BaseModel):
    success: bool
    imported: int
    skipped: int
    errors: List[str]
    message: str

class StatisticsResponse(BaseModel):
    average: float
    median: float
    std_dev: float
    min_score: float
    max_score: float
    pass_rate: float
    distribution: Dict[str, int]

class DistributionResponse(BaseModel):
    bins: List[int]
    counts: List[int]
    totals: List[float]

class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(csv|excel)$")
    filters: Optional[Dict[str, Any]] = None

class EditGradeRequest(BaseModel):
    student_id: str
    grade_type: str
    new_value: float = Field(..., ge=0, le=100)
    reason: str

class BackupStatusResponse(BaseModel):
    status: str
    last_run: Optional[datetime] = None
    message: Optional[str] = None

class BackupResultResponse(BaseModel):
    success: bool
    message: str

class AdjustmentRuleCreate(BaseModel):
    name: str
    condition: str
    adjustment: float
    description: Optional[str] = None

class ScoringSchemeCreate(BaseModel):
    name: str
    usual_weight: float = Field(0.3, ge=0, le=1)
    midterm_weight: float = Field(0.3, ge=0, le=1)
    final_weight: float = Field(0.4, ge=0, le=1)
    description: Optional[str] = None

class NotificationRequest(BaseModel):
    subject: str
    message: str
    recipients: List[str]
