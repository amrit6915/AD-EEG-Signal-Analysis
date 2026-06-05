import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_predictions = Column(JSON, nullable=True)
    smoothed_predictions = Column(JSON, nullable=True)
    detected_peaks = Column(JSON, nullable=True)
    peak_timestamps = Column(ARRAY(Float), nullable=True)
    peak_probabilities = Column(ARRAY(Float), nullable=True)
    visualization_data = Column(LargeBinary, nullable=True)
    summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    detection = relationship("Detection", back_populates="result")
    user = relationship("User", back_populates="results")
