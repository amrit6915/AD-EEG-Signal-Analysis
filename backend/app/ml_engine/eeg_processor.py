import numpy as np
import mne
from typing import Optional
from app.config import settings
from app.utils.logger import logger


def read_edf_file(filepath: str) -> tuple[Optional[np.ndarray], Optional[float], Optional[list[str]], Optional[int]]:
    try:
        raw = mne.io.read_raw_edf(filepath, preload=True)
        signals = raw.get_data()
        sfreq = raw.info["sfreq"]
        channels = raw.ch_names
        n_times = raw.n_times
        logger.info(f"Loaded EDF: {filepath} | {n_times} samples @ {sfreq} Hz | {len(channels)} channels")
        return signals, sfreq, channels, n_times
    except Exception as e:
        logger.error(f"Failed to read EDF file {filepath}: {e}")
        return None, None, None, None


def extract_channels(signals: np.ndarray, channel_names: list[str], desired_channels: list[str]) -> Optional[np.ndarray]:
    available = set(channel_names)
    valid = [ch for ch in desired_channels if ch in available]
    if not valid:
        logger.error("No valid EEG channels found in file")
        return None

    indices = [channel_names.index(ch) for ch in valid]
    extracted = signals[indices, :]
    logger.info(f"Extracted {len(valid)}/{len(desired_channels)} channels")
    return extracted


def normalize_signal(signals: np.ndarray) -> np.ndarray:
    return signals * 1e6


def create_windows(signals: np.ndarray, window_duration: int, step_duration: int, fs: float) -> Optional[np.ndarray]:
    step_window = int(window_duration * fs)
    step = int(step_duration * fs)
    n_times = signals.shape[1]

    segment_count = (n_times - step_window) // step
    if segment_count <= 0:
        logger.error("EEG file is too short for analysis")
        return None

    segments = np.array([signals[:, i * step : i * step + step_window] for i in range(segment_count)])
    logger.info(f"Created {segment_count} windows of {window_duration}s (step={step_duration}s)")
    return segments


def validate_edf_file(filepath: str) -> dict:
    try:
        raw = mne.io.read_raw_edf(filepath, preload=False)
        return {
            "is_valid": True,
            "duration": raw.n_times / raw.info["sfreq"],
            "sampling_rate": raw.info["sfreq"],
            "channels": raw.ch_names,
            "num_samples": raw.n_times,
            "errors": [],
        }
    except Exception as e:
        return {
            "is_valid": False,
            "duration": 0,
            "sampling_rate": 0,
            "channels": [],
            "num_samples": 0,
            "errors": [str(e)],
        }


def load_seizure_annotations(filepath: str) -> np.ndarray:
    seizure_labels = []
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    start, end = int(parts[0]), int(parts[1])
                    seizure_labels.append((start, end))
                except ValueError:
                    continue
    return np.array(seizure_labels) if seizure_labels else np.array([])


def create_seizure_labels(seizure_ranges: np.ndarray, n_times: int) -> np.ndarray:
    labels = np.zeros(n_times, dtype=np.float32)
    if len(seizure_ranges) > 0:
        for start, end in seizure_ranges:
            labels[start:end] = 1.0
    return labels


def compute_windowed_seizure_indices(seizure_labels: np.ndarray, n_times: int, step_window: int, step: int) -> np.ndarray:
    segment_count = (n_times - step_window) // step
    indices = np.array([
        seizure_labels[i * step : i * step + step_window].sum() / step_window
        for i in range(segment_count)
    ])
    return indices
