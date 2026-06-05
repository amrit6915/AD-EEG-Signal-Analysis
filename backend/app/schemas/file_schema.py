from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class FileUploadResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    file_metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class FileListItem(BaseModel):
    id: str
    original_filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    file_metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    files: list[FileListItem]
    total: int
    page: int
    limit: int
    total_pages: int
