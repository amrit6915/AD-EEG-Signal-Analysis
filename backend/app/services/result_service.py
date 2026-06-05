from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.result import Result
from app.models.detection import Detection
from app.models.file import FileRecord


async def get_result_by_detection_id(db: AsyncSession, detection_id: str) -> Result | None:
    result = await db.execute(select(Result).where(Result.detection_id == detection_id))
    return result.scalar_one_or_none()


async def get_result_by_id(db: AsyncSession, result_id: str) -> Result | None:
    result = await db.execute(select(Result).where(Result.id == result_id))
    return result.scalar_one_or_none()


async def delete_result(db: AsyncSession, result: Result) -> bool:
    await db.delete(result)
    await db.commit()
    return True


async def get_user_results(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Result], int]:
    query = select(Result).where(Result.user_id == user_id)
    count_query = select(func.count()).select_from(Result).where(Result.user_id == user_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Result.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    results = result.scalars().all()

    return list(results), total
