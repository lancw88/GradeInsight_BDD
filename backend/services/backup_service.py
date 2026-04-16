from pathlib import Path
from datetime import datetime
from ..config import BACKUP_DIR, DATA_DIR

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

class BackupService:
    def __init__(self):
        self.status = {"status": "idle", "last_run": None, "message": None}

    def run_backup(self) -> dict:
        source = DATA_DIR / "gradeinsight.db"
        if not source.exists():
            self.status.update({"status": "failed", "message": "資料庫檔案不存在"})
            return {"success": False, "message": "資料庫檔案不存在"}

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"gradeinsight_backup_{timestamp}.db"
        try:
            with source.open("rb") as src, backup_file.open("wb") as dst:
                dst.write(src.read())
            self.status.update({"status": "success", "last_run": datetime.utcnow(), "message": "備份完成"})
            return {"success": True, "message": "備份完成"}
        except Exception as exc:
            self.status.update({"status": "failed", "message": str(exc)})
            return {"success": False, "message": str(exc)}

    def get_status(self) -> dict:
        return self.status
