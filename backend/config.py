from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'gradeinsight.db'}"
BACKUP_DIR = DATA_DIR / "backups"
MAX_IMPORT_ROWS = 500
REQUIRED_IMPORT_COLUMNS = ["name", "student_id", "usual", "midterm", "final"]
