from app.tasks.celery_tasks import celery_app, run_detection_task

__all__ = ["celery_app", "run_detection_task"]
