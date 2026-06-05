import os
import uuid
from pathlib import Path
from typing import Optional
from app.config import settings


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_valid_edf(filename: str) -> bool:
    ext = get_file_extension(filename)
    return ext in (".edf", ".edf+")


def is_valid_seizures(filename: str) -> bool:
    ext = get_file_extension(filename)
    return ext == ".seizures"


def generate_stored_filename(original_filename: str) -> str:
    ext = get_file_extension(original_filename)
    return f"{uuid.uuid4().hex}{ext}"


def get_file_path(file_type: str, stored_filename: str) -> str:
    subdir = file_type
    dir_path = Path(settings.UPLOAD_DIR) / subdir
    dir_path.mkdir(parents=True, exist_ok=True)
    return str(dir_path / stored_filename)


def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)


def delete_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def validate_file_size(file_size: int) -> bool:
    return file_size <= settings.MAX_FILE_SIZE
