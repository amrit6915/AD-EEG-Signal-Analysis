import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    edf_file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    seizures_file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    task_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), default="pending", nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    seizure_detected = Column(Boolean, nullable=True)
    max_probability = Column(Float, nullable=True)
    threshold_used = Column(Float, default=0.5, nullable=False)
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="detections")
    edf_file = relationship("FileRecord", foreign_keys=[edf_file_id], back_populates="edf_detections")
    seizures_file = relationship("FileRecord", foreign_keys=[seizures_file_id], back_populates="seizures_detections")
    result = relationship("Result", back_populates="detection", uselist=False, cascade="all, delete-orphan")
