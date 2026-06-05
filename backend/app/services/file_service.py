import shutil
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.file import FileRecord, FileType
from app.models.user import User
from app.utils.file_utils import (
    generate_stored_filename,
    get_file_path,
    get_file_size,
    is_valid_edf,
    is_valid_seizures,
    validate_file_size,
    delete_file as util_delete_file,
)
from app.ml_engine.eeg_processor import validate_edf_file
from app.utils.logger import logger
import uuid


async def upload_file(
    db: AsyncSession,
    user: User,
    file_content: bytes,
    original_filename: str,
    file_type: str,
) -> FileRecord:
    ft = FileType(file_type)

    if ft == FileType.EDF and not is_valid_edf(original_filename):
        raise ValueError("Invalid EDF file extension. Expected .edf")
    if ft == FileType.SEIZURES and not is_valid_seizures(original_filename):
        raise ValueError("Invalid seizures file extension. Expected .seizures")

    file_size = len(file_content)
    if not validate_file_size(file_size):
        raise ValueError(f"File too large. Max size: {500 * 1024 * 1024} bytes")

    stored_filename = generate_stored_filename(original_filename)
    file_path = get_file_path(file_type, stored_filename)

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_content)

    metadata = None
    if ft == FileType.EDF:
        metadata = validate_edf_file(file_path)

    record = FileRecord(
        user_id=user.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_type=ft,
        file_size=file_size,
        file_path=file_path,
        file_metadata=metadata,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    logger.info(f"Uploaded file: {original_filename} ({file_type}, {file_size} bytes)")
    return record


async def get_user_files(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    file_type: str = None,
) -> tuple[list[FileRecord], int]:
    query = select(FileRecord).where(
        FileRecord.user_id == user_id,
        FileRecord.is_deleted == False,
    )
    count_query = select(func.count()).select_from(FileRecord).where(
        FileRecord.user_id == user_id,
        FileRecord.is_deleted == False,
    )

    if file_type:
        query = query.where(FileRecord.file_type == FileType(file_type))
        count_query = count_query.where(FileRecord.file_type == FileType(file_type))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(FileRecord.uploaded_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    files = result.scalars().all()

    return list(files), total


async def get_file_by_id(db: AsyncSession, file_id: str) -> FileRecord | None:
    result = await db.execute(select(FileRecord).where(FileRecord.id == file_id, FileRecord.is_deleted == False))
    return result.scalar_one_or_none()


async def delete_file_record(db: AsyncSession, file: FileRecord) -> bool:
    util_delete_file(file.file_path)
    file.is_deleted = True
    await db.commit()
    logger.info(f"Deleted file record: {file.original_filename}")
    return True
