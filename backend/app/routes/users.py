from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas.user_schema import UserResponse, UserUpdate, ChangePasswordRequest
from app.models.user import User
from app.models.detection import Detection
from app.models.login_history import LoginHistory
from app.services.user_service import get_db, get_user_by_id, update_user, verify_password, hash_password
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updates = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if not updates:
        return UserResponse(
            id=str(user.id), email=user.email, username=user.username,
            full_name=user.full_name, is_active=user.is_active,
            created_at=user.created_at, last_login=user.last_login,
        )
    updated = await update_user(db, user, updates)
    return UserResponse(
        id=str(updated.id), email=updated.email, username=updated.username,
        full_name=updated.full_name, is_active=updated.is_active,
        created_at=updated.created_at, last_login=updated.last_login,
    )


@router.get("/profile/statistics")
async def get_statistics(
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

    return {
        "total_detections": total_detections,
        "seizures_detected": seizures_detected,
        "detection_rate": round(seizures_detected / total_detections * 100, 2) if total_detections > 0 else 0,
    }


@router.get("/login-history")
async def get_login_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LoginHistory)
        .where(LoginHistory.user_id == user.id)
        .order_by(LoginHistory.login_time.desc())
        .limit(50)
    )
    history = result.scalars().all()
    return [
        {
            "id": str(h.id),
            "login_time": h.login_time.isoformat(),
            "ip_address": h.ip_address,
            "user_agent": h.user_agent,
        }
        for h in history
    ]


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.delete("/account", status_code=204)
async def delete_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.is_active = False
    await db.commit()
