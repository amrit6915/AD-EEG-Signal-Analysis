import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "backend" / "models"
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"


class Settings:
    APP_NAME: str = "EEG Seizure Detection API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/eeg_db"
    )
    DATABASE_URL_SYNC: str = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql://postgres:postgres@localhost:5432/eeg_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production-32chars")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    MODEL_PATH: str = os.getenv("MODEL_PATH", str(MODEL_DIR / "CHB_MIT_sz_detec_demo.h5"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(UPLOAD_DIR))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(500 * 1024 * 1024)))

    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

    EEG_WINDOW_SECONDS: int = 8
    EEG_STEP_SECONDS: int = 4
    SMOOTHING_WINDOW: int = 3
    PEAK_HEIGHT_THRESHOLD: float = 0.95
    PEAK_DISTANCE: int = 6
    DEFAULT_DETECTION_THRESHOLD: float = 0.5
    CHANNEL_LABELS: list[str] = [
        "FP1-F7", "F7-T7", "T7-P7", "P7-O1",
        "FP1-F3", "F3-C3", "C3-P3", "P3-O1",
        "FP2-F4", "F4-C4", "C4-P4", "P4-O2",
        "FP2-F8", "F8-T8", "T8-P8", "P8-O2",
        "FZ-CZ", "CZ-PZ",
    ]


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(str(Path(settings.MODEL_PATH).parent), exist_ok=True)
