from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class DetectionRequest(BaseModel):
    edf_file_id: str
    seizures_file_id: str
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    smoothing_window: int = Field(default=3, ge=1, le=20)


class DetectionTaskResponse(BaseModel):
    task_id: str
    status: str = "pending"
    estimated_time: int = 60


class DetectionStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0


class PeakInfo(BaseModel):
    timestamp: float
    probability: float
    index: int


class SummaryInfo(BaseModel):
    seizure_detected: bool
    max_probability: float
    num_peaks: int
    threshold_used: float
    total_windows: int


class DetectionResultResponse(BaseModel):
    id: str
    detection_id: str
    raw_predictions: list[float]
    smoothed_predictions: list[float]
    detected_peaks: list[PeakInfo]
    summary: SummaryInfo
    visualization_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RerunRequest(BaseModel):
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class DetectionHistoryItem(BaseModel):
    id: str
    edf_filename: Optional[str] = None
    seizures_filename: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    seizure_detected: Optional[bool] = None
    max_probability: Optional[float] = None
    threshold_used: float

    class Config:
        from_attributes = True


class DetectionHistoryResponse(BaseModel):
    detections: list[DetectionHistoryItem]
    total: int
    page: int
    limit: int
    total_pages: int
