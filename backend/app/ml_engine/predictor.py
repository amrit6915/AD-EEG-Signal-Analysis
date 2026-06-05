import numpy as np
from scipy.signal import find_peaks
from app.ml_engine.model_loader import get_model
from app.config import settings
from app.utils.logger import logger


def predict(signal_windows: np.ndarray) -> np.ndarray:
    model = get_model()
    if model is None:
        raise RuntimeError("Model not loaded")

    if signal_windows.ndim == 3:
        signal_windows = signal_windows[:, :, :, np.newaxis]

    expected_features = model.input_shape[-2] if len(model.input_shape) > 2 else model.input_shape[1]
    if signal_windows.shape[2] != expected_features:
        signal_windows = signal_windows[:, :, ::2, :] if signal_windows.shape[2] > expected_features else np.repeat(signal_windows, 2, axis=2)[:, :, :expected_features, :]

    logger.info(f"Running prediction on {signal_windows.shape[0]} windows, shape={signal_windows.shape}")
    predictions = model.predict(signal_windows, verbose=0)
    logger.info(f"Predictions completed, shape={predictions.shape}")
    return predictions.flatten()


def smooth_predictions(predictions: np.ndarray, window_size: int = None) -> np.ndarray:
    if window_size is None:
        window_size = settings.SMOOTHING_WINDOW
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(predictions, window, mode="valid")
    return smoothed


def find_detection_peaks(smoothed_predictions: np.ndarray, height_threshold: float = None, distance: int = None) -> tuple[np.ndarray, dict]:
    if height_threshold is None:
        height_threshold = settings.PEAK_HEIGHT_THRESHOLD
    if distance is None:
        distance = settings.PEAK_DISTANCE
    peaks, properties = find_peaks(smoothed_predictions, height=height_threshold, distance=distance)
    return peaks, properties


def detect_seizure(predictions: np.ndarray, threshold: float = None) -> tuple[bool, float, int]:
    if threshold is None:
        threshold = settings.DEFAULT_DETECTION_THRESHOLD
    max_pred = float(np.max(predictions))
    detected = max_pred > threshold
    max_idx = int(np.argmax(predictions))
    return detected, max_pred, max_idx


def run_full_detection(signal_windows: np.ndarray, threshold: float = None, smoothing_window: int = None) -> dict:
    if threshold is None:
        threshold = settings.DEFAULT_DETECTION_THRESHOLD
    if smoothing_window is None:
        smoothing_window = settings.SMOOTHING_WINDOW

    raw_preds = predict(signal_windows)
    smoothed = smooth_predictions(raw_preds, smoothing_window)
    peaks, peak_props = find_detection_peaks(smoothed)
    detected, max_prob, max_idx = detect_seizure(raw_preds, threshold)

    time_step = settings.EEG_STEP_SECONDS
    peak_times = (peaks + (smoothing_window - 1) // 2).astype(float) * time_step
    peak_probs = smoothed[peaks].tolist() if len(peaks) > 0 else []

    return {
        "raw_predictions": raw_preds.tolist(),
        "smoothed_predictions": smoothed.tolist(),
        "peaks": [
            {"timestamp": float(t), "probability": float(p), "index": int(i)}
            for t, p, i in zip(peak_times, peak_probs, peaks.tolist())
        ],
        "summary": {
            "seizure_detected": detected,
            "max_probability": max_prob,
            "num_peaks": len(peaks),
            "threshold_used": threshold,
            "total_windows": len(raw_preds),
        },
    }
