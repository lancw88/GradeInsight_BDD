from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from backend.models.schemas import (
    ImportRequest, ImportResultResponse, ImportPreviewResponse, StudentResponse,
    StatisticsResponse, DistributionResponse, ExportRequest, EditGradeRequest,
    BackupStatusResponse, BackupResultResponse, AdjustmentRuleCreate,
    ScoringSchemeCreate, NotificationRequest
)
from backend.services import (
    ImportService, GradeService, StatisticsService,
    ExportService, NotificationService, BackupService, DataGenerator
)

app = FastAPI(title="GradeInsight API", description="成績管理系統後端 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backup_service = BackupService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    init_db()
    db = SessionLocal()
    try:
        from backend.models.db_models import Student
        count = db.query(Student).count()
        if count == 0:
            DataGenerator(db).generate_mock_data(30)
    finally:
        db.close()


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "GradeInsight 後端已啟動"}


@app.post("/api/data/generate-sample")
def generate_sample(db: Session = Depends(get_db)):
    service = DataGenerator(db)
    return service.generate_mock_data()


@app.post("/api/grades/import/preview", response_model=ImportPreviewResponse)
def import_preview(request: ImportRequest, db: Session = Depends(get_db)):
    service = ImportService(db)
    try:
        return service.preview_import(request.file_data, request.file_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/grades/import", response_model=ImportResultResponse)
def import_grades(request: ImportRequest, db: Session = Depends(get_db)):
    service = ImportService(db)
    try:
        return service.import_file(request.file_data, request.file_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/grades", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    service = GradeService(db)
    return service.list_students()


@app.get("/api/grades/student/{student_id}", response_model=StudentResponse)
def get_student(student_id: str, db: Session = Depends(get_db)):
    service = GradeService(db)
    student = service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="學生不存在")
    return student


@app.put("/api/grades/student/{student_id}")
def edit_student_grade(student_id: str, payload: EditGradeRequest, db: Session = Depends(get_db)):
    service = GradeService(db)
    result = service.edit_grade(student_id, payload.grade_type, payload.new_value, payload.reason)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/api/grades/scoring-scheme")
def apply_scoring_scheme(payload: ScoringSchemeCreate, db: Session = Depends(get_db)):
    service = GradeService(db)
    return service.apply_scoring_scheme(payload.dict())


@app.post("/api/grades/adjustment-rule")
def apply_adjustment_rule(payload: AdjustmentRuleCreate, db: Session = Depends(get_db)):
    service = GradeService(db)
    return service.apply_adjustment_rule(payload.dict())


@app.get("/api/statistics/summary", response_model=StatisticsResponse)
def statistics_summary(db: Session = Depends(get_db)):
    service = StatisticsService(db)
    return service.calculate_summary()


@app.get("/api/statistics/distribution", response_model=DistributionResponse)
def statistics_distribution(db: Session = Depends(get_db)):
    service = StatisticsService(db)
    return service.distribution_data()


@app.post("/api/export/class-report")
def export_class_report(payload: ExportRequest, db: Session = Depends(get_db)):
    service = ExportService(db)
    try:
        return service.export(payload.format, payload.filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/export/student-report/{student_id}")
def export_student_report(student_id: str, payload: ExportRequest, db: Session = Depends(get_db)):
    student = GradeService(db).get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="學生不存在")
    service = ExportService(db)
    try:
        filters = {"student_id": student_id}
        return service.export(payload.format, filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/export/batch")
def export_batch(payload: ExportRequest, db: Session = Depends(get_db)):
    service = ExportService(db)
    try:
        return service.export(payload.format, payload.filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/notify")
def send_notification(payload: NotificationRequest):
    service = NotificationService()
    return service.send_notification(payload.dict())


@app.post("/api/backup/run", response_model=BackupResultResponse)
def run_backup():
    return backup_service.run_backup()


@app.get("/api/backup/status", response_model=BackupStatusResponse)
def backup_status():
    return backup_service.get_status()
