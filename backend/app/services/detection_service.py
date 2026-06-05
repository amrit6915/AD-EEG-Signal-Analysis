from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.detection import Detection
from app.models.file import FileRecord
from app.models.result import Result
from app.models.user import User
from app.ml_engine.eeg_processor import (
    read_edf_file,
    extract_channels,
    normalize_signal,
    create_windows,
    load_seizure_annotations,
    create_seizure_labels,
    compute_windowed_seizure_indices,
)
from app.ml_engine.predictor import run_full_detection
from app.ml_engine.visualization import plot_predictions, encode_plot_to_base64
from app.config import settings
from app.utils.logger import logger


async def create_detection(
    db: AsyncSession,
    user: User,
    edf_file_id: str,
    seizures_file_id: str,
    threshold: float = 0.5,
) -> Detection:
    detection = Detection(
        user_id=user.id,
        edf_file_id=edf_file_id,
        seizures_file_id=seizures_file_id,
        status="pending",
        threshold_used=threshold,
    )
    db.add(detection)
    await db.commit()
    await db.refresh(detection)
    return detection


async def run_detection(
    db: AsyncSession,
    detection: Detection,
):
    try:
        detection.status = "processing"
        await db.commit()

        result = await db.execute(select(FileRecord).where(FileRecord.id == detection.edf_file_id))
        edf_file = result.scalar_one_or_none()

        result2 = await db.execute(select(FileRecord).where(FileRecord.id == detection.seizures_file_id))
        seizures_file = result2.scalar_one_or_none()

        if not edf_file:
            raise FileNotFoundError("EDF file not found")
        if not seizures_file:
            raise FileNotFoundError("Seizures file not found")

        signals, sfreq, channels, n_times = read_edf_file(edf_file.file_path)
        if signals is None:
            raise ValueError("Failed to read EDF file")

        extracted = extract_channels(signals, channels, settings.CHANNEL_LABELS)
        if extracted is None:
            raise ValueError("No valid channels extracted")

        normalized = normalize_signal(extracted)
        windows = create_windows(normalized, settings.EEG_WINDOW_SECONDS, settings.EEG_STEP_SECONDS, sfreq)
        if windows is None:
            raise ValueError("Failed to create windows from signal")

        seizure_annotations = load_seizure_annotations(seizures_file.file_path)
        seizure_labels = create_seizure_labels(seizure_annotations, n_times)

        win_size = int(settings.EEG_WINDOW_SECONDS * sfreq)
        step = int(settings.EEG_STEP_SECONDS * sfreq)
        windowed_sz = compute_windowed_seizure_indices(seizure_labels, n_times, win_size, step)

        result_data = run_full_detection(
            windows,
            threshold=detection.threshold_used,
            smoothing_window=settings.SMOOTHING_WINDOW,
        )

        viz_png = plot_predictions(
            raw_pred=result_data["raw_predictions"],
            true_labels=windowed_sz.tolist(),
            smoothed_pred=result_data["smoothed_predictions"],
            peaks=[p["index"] for p in result_data["peaks"]],
        )

        viz_b64 = encode_plot_to_base64(viz_png)

        db_result = Result(
            detection_id=detection.id,
            user_id=detection.user_id,
            raw_predictions=result_data["raw_predictions"],
            smoothed_predictions=result_data["smoothed_predictions"],
            detected_peaks=result_data["peaks"],
            peak_timestamps=[p["timestamp"] for p in result_data["peaks"]],
            peak_probabilities=[p["probability"] for p in result_data["peaks"]],
            visualization_data=viz_png,
            summary=result_data["summary"],
        )
        db.add(db_result)

        detection.status = "completed"
        detection.seizure_detected = result_data["summary"]["seizure_detected"]
        detection.max_probability = result_data["summary"]["max_probability"]
        detection.completed_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Detection {detection.id} completed: seizure={result_data['summary']['seizure_detected']}, max_prob={result_data['summary']['max_probability']:.4f}")

    except Exception as e:
        detection.status = "failed"
        detection.error_message = str(e)
        detection.completed_at = datetime.utcnow()
        await db.commit()
        logger.error(f"Detection {detection.id} failed: {e}")


async def get_detection_by_id(db: AsyncSession, detection_id: str) -> Detection | None:
    result = await db.execute(select(Detection).where(Detection.id == detection_id))
    return result.scalar_one_or_none()


async def get_user_detections(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
) -> tuple[list[Detection], int]:
    query = select(Detection).where(Detection.user_id == user_id)
    count_query = select(func.count()).select_from(Detection).where(Detection.user_id == user_id)

    if status:
        query = query.where(Detection.status == status)
        count_query = count_query.where(Detection.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Detection.started_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    detections = result.scalars().all()

    return list(detections), total
