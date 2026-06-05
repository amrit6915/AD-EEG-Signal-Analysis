from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from sqlalchemy.sql import extract
from datetime import datetime, timedelta
from app.models.user import User
from app.models.detection import Detection
from app.services.user_service import get_db
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total = await db.execute(
        select(func.count()).select_from(Detection).where(Detection.user_id == user.id)
    )
    total_detections = total.scalar() or 0

    seizures = await db.execute(
        select(func.count()).select_from(Detection).where(
            Detection.user_id == user.id,
            Detection.seizure_detected == True,
        )
    )
    seizures_detected = seizures.scalar() or 0

    avg_prob = await db.execute(
        select(func.avg(Detection.max_probability)).where(
            Detection.user_id == user.id,
            Detection.max_probability.isnot(None),
        )
    )
    avg_probability = round(float(avg_prob.scalar() or 0), 4)

    recent = await db.execute(
        select(Detection)
        .where(Detection.user_id == user.id)
        .order_by(Detection.started_at.desc())
        .limit(5)
    )
    recent_detections = [
        {
            "id": str(d.id),
            "status": d.status,
            "seizure_detected": d.seizure_detected,
            "max_probability": d.max_probability,
            "started_at": d.started_at.isoformat() if d.started_at else None,
        }
        for d in recent.scalars().all()
    ]

    from app.models.file import FileRecord
    file_count = await db.execute(
        select(func.count()).select_from(FileRecord).where(
            FileRecord.user_id == user.id,
            FileRecord.is_deleted == False,
        )
    )

    return {
        "total_detections": total_detections,
        "seizures_detected": seizures_detected,
        "detection_rate": round(seizures_detected / total_detections * 100, 2) if total_detections > 0 else 0,
        "avg_probability": avg_probability,
        "total_files": file_count.scalar() or 0,
        "recent_detections": recent_detections,
    }


@router.get("/trends")
async def get_trends(
    date_range: str = Query("30d", pattern="^(7d|30d|90d)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    days = int(date_range.replace("d", ""))
    since = datetime.utcnow() - timedelta(days=days)

    detections_result = await db.execute(
        select(
            func.date(Detection.started_at).label("date"),
            func.count().label("count"),
            func.sum(
                cast(Detection.seizure_detected, func.INTEGER)
            ).label("seizure_count"),
            func.avg(Detection.max_probability).label("avg_prob"),
        )
        .where(
            Detection.user_id == user.id,
            Detection.started_at >= since,
        )
        .group_by(func.date(Detection.started_at))
        .order_by(func.date(Detection.started_at))
    )
    rows = detections_result.all()

    dates = []
    detection_counts = []
    seizure_counts = []
    avg_probabilities = []

    for row in rows:
        dates.append(str(row.date))
        detection_counts.append(int(row.count))
        seizure_counts.append(int(row.seizure_count or 0))
        avg_probabilities.append(round(float(row.avg_prob or 0), 4))

    return {
        "dates": dates,
        "detection_counts": detection_counts,
        "seizure_counts": seizure_counts,
        "avg_probabilities": avg_probabilities,
    }
