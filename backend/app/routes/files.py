from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.user import User
from app.models.file import FileRecord
from app.services.file_service import upload_file, get_user_files, get_file_by_id, delete_file_record
from app.services.user_service import get_db
from app.middleware.auth import get_current_user
from app.schemas.file_schema import FileUploadResponse, FileListResponse, FileListItem
from app.utils.logger import logger
import math

router = APIRouter(prefix="/api/files", tags=["Files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_edf_file(
    file: UploadFile = File(...),
    file_type: str = Query("edf", pattern="^(edf|seizures)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    try:
        record = await upload_file(db, user, content, file.filename, file_type)
        return FileUploadResponse(
            id=str(record.id),
            original_filename=record.original_filename,
            file_type=record.file_type.value,
            file_size=record.file_size,
            uploaded_at=record.uploaded_at,
            file_metadata=record.file_metadata,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None, pattern="^(edf|seizures)?$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    files, total = await get_user_files(db, str(user.id), page, limit, file_type)
    total_pages = math.ceil(total / limit) if total > 0 else 1

    return FileListResponse(
        files=[
            FileListItem(
                id=str(f.id),
                original_filename=f.original_filename,
                file_type=f.file_type.value,
                file_size=f.file_size,
                uploaded_at=f.uploaded_at,
                file_metadata=f.file_metadata,
            )
            for f in files
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/{file_id}")
async def get_file(
    file_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file = await get_file_by_id(db, file_id)
    if not file or str(file.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="File not found")

    return FileUploadResponse(
        id=str(file.id),
        original_filename=file.original_filename,
        file_type=file.file_type.value,
        file_size=file.file_size,
        uploaded_at=file.uploaded_at,
        file_metadata=file.file_metadata,
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import FileResponse
    file = await get_file_by_id(db, file_id)
    if not file or str(file.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file.file_path,
        filename=file.original_filename,
        media_type="application/octet-stream",
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file = await get_file_by_id(db, file_id)
    if not file or str(file.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="File not found")

    await delete_file_record(db, file)
