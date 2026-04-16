from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL, DATA_DIR
from pathlib import Path

DATA_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


def init_db():
    from .models.db_models import Student, GradeEditLog, ScoringScheme, AdjustmentRule
    Base.metadata.create_all(bind=engine)
