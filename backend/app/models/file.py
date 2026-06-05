import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base


class FileType(str, enum.Enum):
    EDF = "edf"
    SEIZURES = "seizures"


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)
    file_type = Column(SAEnum(FileType), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_path = Column(String(1000), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    file_metadata = Column("metadata", JSON, nullable=True)

    user = relationship("User", back_populates="files")
    edf_detections = relationship("Detection", foreign_keys="Detection.edf_file_id", back_populates="edf_file", cascade="all, delete-orphan")
    seizures_detections = relationship("Detection", foreign_keys="Detection.seizures_file_id", back_populates="seizures_file", cascade="all, delete-orphan")
