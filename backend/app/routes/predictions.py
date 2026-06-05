from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.detection import Detection
from app.models.file import FileRecord
from app.schemas.prediction_schema import (
    DetectionRequest, DetectionTaskResponse, DetectionStatusResponse,
    DetectionResultResponse, RerunRequest, PeakInfo, SummaryInfo,
)
from app.services.user_service import get_db
from app.services.detection_service import create_detection, run_detection, get_detection_by_id
from app.services.result_service import get_result_by_detection_id
from app.services.file_service import get_file_by_id
from app.middleware.auth import get_current_user
from app.tasks.celery_tasks import run_detection_task
from app.utils.logger import logger

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/detect", response_model=DetectionTaskResponse)
async def start_detection(
    data: DetectionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    edf_file = await get_file_by_id(db, data.edf_file_id)
    if not edf_file or str(edf_file.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="EDF file not found")

    seizures_file = await get_file_by_id(db, data.seizures_file_id)
    if not seizures_file or str(seizures_file.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Seizures file not found")

    detection = await create_detection(db, user, data.edf_file_id, data.seizures_file_id, data.threshold)

    try:
        task = run_detection_task.delay(str(detection.id))
        detection.task_id = task.id
        await db.commit()
        logger.info(f"Detection task created: {detection.id}, celery_task={task.id}")
    except Exception as e:
        logger.warning(f"Celery not available, running sync: {e}")
        await run_detection(db, detection)

    return DetectionTaskResponse(
        task_id=str(detection.id),
        status=detection.status,
        estimated_time=60,
    )


@router.get("/{task_id}/status", response_model=DetectionStatusResponse)
async def get_detection_status(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    detection = await get_detection_by_id(db, task_id)
    if not detection or str(detection.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Detection not found")

    progress = 0
    if detection.status == "processing":
        progress = 50
    elif detection.status == "completed":
        progress = 100
    elif detection.status == "failed":
        progress = 0

    return DetectionStatusResponse(
        task_id=str(detection.id),
        status=detection.status,
        progress=progress,
    )


@router.get("/{task_id}/results", response_model=DetectionResultResponse)
async def get_detection_results(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    detection = await get_detection_by_id(db, task_id)
    if not detection or str(detection.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Detection not found")

    if detection.status != "completed":
        raise HTTPException(status_code=400, detail=f"Detection not completed yet. Status: {detection.status}")

    result = await get_result_by_detection_id(db, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Results not found")

    import base64
    viz_b64 = base64.b64encode(result.visualization_data).decode("utf-8") if result.visualization_data else None

    peaks_info = []
    if result.detected_peaks:
        for p in result.detected_peaks:
            if isinstance(p, dict):
                peaks_info.append(PeakInfo(
                    timestamp=p.get("timestamp", 0),
                    probability=p.get("probability", 0),
                    index=p.get("index", 0),
                ))

    return DetectionResultResponse(
        id=str(result.id),
        detection_id=str(result.detection_id),
        raw_predictions=result.raw_predictions or [],
        smoothed_predictions=result.smoothed_predictions or [],
        detected_peaks=peaks_info,
        summary=SummaryInfo(
            seizure_detected=result.summary.get("seizure_detected", False) if result.summary else False,
            max_probability=result.summary.get("max_probability", 0) if result.summary else 0,
            num_peaks=result.summary.get("num_peaks", 0) if result.summary else 0,
            threshold_used=result.summary.get("threshold_used", 0.5) if result.summary else 0.5,
            total_windows=result.summary.get("total_windows", 0) if result.summary else 0,
        ),
        visualization_data=viz_b64,
        created_at=result.created_at,
    )


@router.post("/{task_id}/rerun", response_model=DetectionTaskResponse)
async def rerun_detection(
    task_id: str,
    data: RerunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    detection = await get_detection_by_id(db, task_id)
    if not detection or str(detection.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Detection not found")

    new_detection = await create_detection(
        db, user, str(detection.edf_file_id), str(detection.seizures_file_id), data.threshold
    )

    try:
        task = run_detection_task.delay(str(new_detection.id))
        new_detection.task_id = task.id
        await db.commit()
    except Exception as e:
        logger.warning(f"Celery not available, running sync on rerun: {e}")
        await run_detection(db, new_detection)

    return DetectionTaskResponse(
        task_id=str(new_detection.id),
        status=new_detection.status,
        estimated_time=60,
    )
