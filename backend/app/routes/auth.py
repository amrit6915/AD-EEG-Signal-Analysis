from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schema import UserRegister, UserLogin, TokenResponse, RefreshRequest
from app.schemas.user_schema import UserResponse
from app.services.user_service import get_db, get_user_by_email, get_user_by_username, create_user, update_last_login
from app.services.user_service import verify_password
from app.models.login_history import LoginHistory
from app.utils.jwt_utils import create_access_token, create_refresh_token, decode_token
from app.utils.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, request: Request, db: AsyncSession = Depends(get_db)):
    existing_email = await get_user_by_email(db, data.email)
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    existing_username = await get_user_by_username(db, data.username)
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already taken")

    user = await create_user(db, data.email, data.username, data.password, data.full_name)
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    await update_last_login(db, user)

    history = LoginHistory(
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(history)
    await db.commit()

    logger.info(f"User registered: {data.email}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    await update_last_login(db, user)

    history = LoginHistory(
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(history)
    await db.commit()

    logger.info(f"User logged in: {data.email}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    from app.services.user_service import get_user_by_id
    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30,
    )


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
