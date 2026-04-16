from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .services import GradeService
from .models import (
    Student, ImportRequest, ScoringScheme, AdjustmentRule,
    ExportRequest, EditGradeRequest, StatisticsResponse,
    AtRiskStudent, DistributionData, StudentDetail
)
from typing import List
import base64
import io

app = FastAPI(title="GradeInsight API", description="成績管理系統後端 API", version="1.0.0")

# CORS 中間件，允許前端訪問
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服務
grade_service = GradeService()

@app.on_event("startup")
async def startup_event():
    """應用啟動時生成模擬數據"""
    grade_service.generate_mock_data(30)

@app.get("/")
async def root():
    return {"message": "歡迎使用 GradeInsight 成績管理系統"}

@app.get("/students", response_model=List[Student])
async def get_students():
    """獲取所有學生列表"""
    return grade_service.get_students()

@app.get("/students/{student_id}", response_model=StudentDetail)
async def get_student_detail(student_id: str):
    """獲取學生詳情"""
    student = grade_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="學生不存在")

    # 模擬趨勢數據
    trend = [
        {"date": "2024-01-01", "score": student.grades.usual},
        {"date": "2024-03-01", "score": student.grades.midterm},
        {"date": "2024-06-01", "score": student.grades.final},
    ]

    stats = grade_service.calculate_statistics()
    return StudentDetail(
        student=student,
        trend=trend,
        statistics={
            "average": stats.average,
            "median": stats.median,
            "std_dev": stats.std_dev
        }
    )

@app.post("/import")
async def import_grades(request: ImportRequest):
    """匯入成績數據"""
    result = grade_service.import_grades(request.file_data, request.file_type)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """獲取成績統計"""
    return grade_service.calculate_statistics()

@app.get("/at-risk", response_model=List[AtRiskStudent])
async def get_at_risk_students(threshold: float = 60):
    """獲取風險學生列表"""
    return grade_service.identify_at_risk_students(threshold)

@app.get("/distribution", response_model=DistributionData)
async def get_distribution():
    """獲取成績分佈數據"""
    return grade_service.get_distribution_data()

@app.post("/scoring-scheme")
async def apply_scoring_scheme(scheme: ScoringScheme):
    """應用自訂評分方案"""
    result = grade_service.apply_scoring_scheme(scheme)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/adjustment-rule")
async def apply_adjustment_rule(rule: AdjustmentRule):
    """應用自動調整規則"""
    result = grade_service.apply_adjustment_rule(rule)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.put("/edit-grade")
async def edit_grade(request: EditGradeRequest):
    """編輯單個成績"""
    result = grade_service.edit_grade(
        request.student_id,
        request.grade_type,
        request.new_value,
        request.reason
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/export")
async def export_report(request: ExportRequest):
    """匯出成績報告"""
    result = grade_service.export_report(request.format, request.filters)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/backup")
async def trigger_backup():
    """觸發備份"""
    result = grade_service.trigger_backup()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.get("/backup/status")
async def get_backup_status():
    """獲取備份狀態"""
    return grade_service.get_backup_status()

@app.post("/generate-mock-data")
async def generate_mock_data(count: int = 30):
    """重新生成模擬數據"""
    grade_service.generate_mock_data(count)
    return {"message": f"已生成 {count} 筆模擬數據"}