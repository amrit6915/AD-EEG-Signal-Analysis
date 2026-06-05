import io
import base64
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from app.config import settings


def plot_predictions(
    raw_pred: list[float],
    true_labels: list[float] = None,
    smoothed_pred: list[float] = None,
    peaks: list[int] = None,
    time_step: int = None,
) -> bytes:
    if time_step is None:
        time_step = settings.EEG_STEP_SECONDS

    raw = np.array(raw_pred)
    mv_win = settings.SMOOTHING_WINDOW

    if smoothed_pred is None:
        smoothed = np.convolve(raw, np.ones(mv_win) / mv_win, mode="valid")
    else:
        smoothed = np.array(smoothed_pred)

    if peaks is None:
        detected_peaks, _ = find_peaks(smoothed, height=settings.PEAK_HEIGHT_THRESHOLD, distance=settings.PEAK_DISTANCE)
    else:
        detected_peaks = np.array(peaks)

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

    time_axis = np.arange(len(raw)) * time_step
    axes[0].plot(time_axis, raw, alpha=0.7, color="tab:blue", linewidth=0.8)
    axes[0].set_ylabel("Probability")
    axes[0].set_title("Raw Predictions")
    axes[0].axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].grid(True, alpha=0.3)

    if true_labels is not None:
        true = np.array(true_labels)
        time_true = np.arange(len(true)) * time_step
        axes[1].bar(time_true, true, width=time_step * 0.8, alpha=0.6, color="tab:green", label="True Labels")
        axes[1].set_ylabel("Seizure")
        axes[1].set_title("True Labels")
        axes[1].set_ylim(-0.05, 1.05)
        axes[1].grid(True, alpha=0.3)

    time_smoothed = np.arange(len(smoothed)) * time_step
    axes[2].plot(time_smoothed, smoothed, alpha=0.9, color="tab:pink", linewidth=1.2)
    axes[2].fill_between(time_smoothed, smoothed, alpha=0.2, color="tab:pink")
    axes[2].set_ylabel("Probability")
    axes[2].set_title("Smoothed Predictions")
    axes[2].axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    axes[2].set_ylim(-0.05, 1.05)
    axes[2].grid(True, alpha=0.3)

    if len(detected_peaks) > 0:
        axes[2].scatter(
            time_smoothed[detected_peaks],
            smoothed[detected_peaks],
            s=40, color="tab:red", label="Seizure Peaks", zorder=5
        )
        axes[2].legend()

    if len(detected_peaks) > 0:
        seizure_regions = np.zeros_like(smoothed)
        for p in detected_peaks:
            start = max(0, p - 2)
            end = min(len(smoothed), p + 3)
            seizure_regions[start:end] = 1
        axes[3].fill_between(time_smoothed, seizure_regions, alpha=0.4, color="tab:red", step="pre")
        axes[3].set_ylabel("Active")
        axes[3].set_title("Detected Seizure Regions")
        axes[3].set_ylim(-0.05, 1.05)
    else:
        axes[3].text(0.5, 0.5, "No seizure regions detected", ha="center", va="center", transform=axes[3].transAxes)
        axes[3].set_title("Detected Seizure Regions")

    axes[3].set_xlabel("Time (s)")
    axes[3].grid(True, alpha=0.3)

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def encode_plot_to_base64(png_bytes: bytes) -> str:
    return base64.b64encode(png_bytes).decode("utf-8")
