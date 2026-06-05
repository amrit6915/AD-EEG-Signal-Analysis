from celery import Celery
from app.config import settings
from app.utils.logger import logger

celery_app = Celery(
    "eeg_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
)


@celery_app.task(bind=True, name="run_detection")
def run_detection_task(self, detection_id: str):
    logger.info(f"Starting detection task for detection_id={detection_id}")
    try:
        import asyncio
        from app.services.user_service import async_session
        from app.models.detection import Detection
        from app.services.detection_service import run_detection
        from sqlalchemy import select

        async def _run():
            async with async_session() as db:
                result = await db.execute(select(Detection).where(Detection.id == detection_id))
                detection = result.scalar_one_or_none()
                if detection:
                    await run_detection(db, detection)

        asyncio.run(_run())
        logger.info(f"Detection task completed for detection_id={detection_id}")
        return {"status": "completed", "detection_id": detection_id}
    except Exception as e:
        logger.error(f"Detection task failed for detection_id={detection_id}: {e}")
        return {"status": "failed", "detection_id": detection_id, "error": str(e)}
