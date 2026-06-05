from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext
from app.config import settings
from app.models.user import User
from app.models.base import Base
from app.utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_size=10, max_overflow=20)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(db: AsyncSession, email: str, username: str, password: str, full_name: str = None) -> User:
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"Created user: {email}")
    return user


async def update_user(db: AsyncSession, user: User, updates: dict) -> User:
    for key, value in updates.items():
        if value is not None:
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def update_last_login(db: AsyncSession, user: User):
    from datetime import datetime
    user.last_login = datetime.utcnow()
    await db.commit()
