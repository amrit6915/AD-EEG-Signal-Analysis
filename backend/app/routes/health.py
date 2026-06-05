from fastapi import APIRouter
from datetime import datetime
from app.config import settings
from app.ml_engine.model_loader import is_model_loaded

router = APIRouter(tags=["Health"])


@router.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "model_loaded": is_model_loaded(),
    }
