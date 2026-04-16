import base64
import io
import pandas as pd
from typing import Dict, Any, List
from .config import REQUIRED_IMPORT_COLUMNS


def decode_base64_file(data: str) -> bytes:
    return base64.b64decode(data)


def validate_import_row(row: Dict[str, Any]) -> List[str]:
    errors = []
    if not row.get("name"):
        errors.append("姓名缺失")
    if not row.get("student_id"):
        errors.append("學號缺失")
    for key in ["usual", "midterm", "final"]:
        value = row.get(key)
        if value is None or value == "":
            errors.append(f"{key} 成績缺失")
            continue
        try:
            score = float(value)
            if score < 0 or score > 100:
                errors.append(f"{key} 成績必須在 0 到 100 之間")
        except (TypeError, ValueError):
            errors.append(f"{key} 成績格式錯誤")
    return errors


def dataframe_from_file(file_bytes: bytes, file_type: str) -> pd.DataFrame:
    if file_type == "csv":
        return pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
    elif file_type == "excel":
        return pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError("不支持的檔案格式")


def prepare_import_preview(df: pd.DataFrame) -> Dict[str, Any]:
    sample = df.head(10).to_dict(orient="records")
    return {
        "preview": sample,
        "columns": list(df.columns),
        "rows": len(df)
    }


def check_required_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in REQUIRED_IMPORT_COLUMNS if col not in df.columns]
