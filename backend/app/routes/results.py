from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.detection import Detection
from app.models.file import FileRecord
from app.models.result import Result
from app.schemas.prediction_schema import DetectionHistoryResponse, DetectionHistoryItem
from app.services.user_service import get_db
from app.services.detection_service import get_user_detections, get_detection_by_id
from app.services.result_service import get_result_by_id, delete_result
from app.middleware.auth import get_current_user
from typing import Optional
import math

router = APIRouter(prefix="/api/results", tags=["Results"])


@router.get("/history", response_model=DetectionHistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|processing|completed|failed)?$"),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    detections, total = await get_user_detections(db, str(user.id), page, limit, status)
    total_pages = math.ceil(total / limit) if total > 0 else 1

    items = []
    for d in detections:
        edf_name = None
        seizures_name = None
        if d.edf_file_id:
            from sqlalchemy import select
            result = await db.execute(select(FileRecord).where(FileRecord.id == d.edf_file_id))
            ef = result.scalar_one_or_none()
            if ef:
                edf_name = ef.original_filename
        if d.seizures_file_id:
            from sqlalchemy import select
            result = await db.execute(select(FileRecord).where(FileRecord.id == d.seizures_file_id))
            sf = result.scalar_one_or_none()
            if sf:
                seizures_name = sf.original_filename

        items.append(DetectionHistoryItem(
            id=str(d.id),
            edf_filename=edf_name,
            seizures_filename=seizures_name,
            status=d.status,
            started_at=d.started_at,
            completed_at=d.completed_at,
            seizure_detected=d.seizure_detected,
            max_probability=d.max_probability,
            threshold_used=d.threshold_used,
        ))

    return DetectionHistoryResponse(
        detections=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/{result_id}")
async def get_result_detail(
    result_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await get_result_by_id(db, result_id)
    if not result or str(result.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Result not found")

    import base64
    viz_b64 = base64.b64encode(result.visualization_data).decode("utf-8") if result.visualization_data else None

    return {
        "id": str(result.id),
        "detection_id": str(result.detection_id),
        "raw_predictions": result.raw_predictions,
        "smoothed_predictions": result.smoothed_predictions,
        "detected_peaks": result.detected_peaks,
        "summary": result.summary,
        "visualization_data": viz_b64,
        "created_at": result.created_at.isoformat(),
    }


@router.delete("/{result_id}", status_code=204)
async def delete_result_endpoint(
    result_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await get_result_by_id(db, result_id)
    if not result or str(result.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Result not found")

    await delete_result(db, result)


@router.post("/{result_id}/export")
async def export_result(
    result_id: str,
    format: str = Query("json", pattern="^(json|csv|pdf)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import StreamingResponse
    import json, io, csv

    result = await get_result_by_id(db, result_id)
    if not result or str(result.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Result not found")

    data = {
        "id": str(result.id),
        "summary": result.summary,
        "raw_predictions": result.raw_predictions,
        "smoothed_predictions": result.smoothed_predictions,
        "detected_peaks": result.detected_peaks,
        "created_at": result.created_at.isoformat(),
    }

    if format == "json":
        content = json.dumps(data, indent=2)
        return StreamingResponse(io.StringIO(content), media_type="application/json", headers={"Content-Disposition": f"attachment; filename=result_{result_id}.json"})
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["type", "value"])
        if result.summary:
            for k, v in result.summary.items():
                writer.writerow([k, v])
        if result.raw_predictions:
            for i, v in enumerate(result.raw_predictions):
                writer.writerow([f"raw_pred_{i}", v])
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=result_{result_id}.csv"})
    else:
        return {"message": "PDF export not yet implemented", "data": data}
