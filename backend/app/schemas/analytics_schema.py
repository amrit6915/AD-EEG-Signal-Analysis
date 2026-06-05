from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DashboardResponse(BaseModel):
    total_detections: int
    seizures_detected: int
    detection_rate: float
    avg_probability: float
    total_files: int
    recent_detections: list[dict[str, Any]]


class TrendsResponse(BaseModel):
    dates: list[str]
    detection_counts: list[int]
    seizure_counts: list[int]
    avg_probabilities: list[float]
