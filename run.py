import streamlit as st
import tempfile
import numpy as np
import mne
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from tensorflow.keras.models import load_model
import os
from pathlib import Path

# Title
st.set_page_config(page_title="EEG Seizure Detection", layout="wide")
st.title('🧠 EEG Seizure Detection System')
st.markdown("---")

# Upload only EEG file
st.subheader("📊 Upload EEG Recording")
edf_file = st.file_uploader("Select an EEG file (.edf)", type=["edf"], help="Upload a 23-channel EEG recording in EDF format")

st.markdown("---")

def convert_seizure_file(seizures_path):
    """
    Handles multiple seizure file formats:
    1. CHB-MIT format: "Seizure X Start Time: XXX seconds"
    2. Simple format: "XXX YYY" (start end)
    3. CSV format: start,end or start;end
    """
    try:
        with open(seizures_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.strip().split('\n')

        seizure_ranges = []
        
        # Try to parse CHB-MIT format first
        start_times = []
        end_times = []
        
        for line in lines:
            # CHB-MIT format: "Seizure 1 Start Time: 2996 seconds"
            if "Start Time" in line and ":" in line:
                try:
                    time_str = line.split(":")[-1].strip().split()[0]
                    start_times.append(int(time_str))
                except:
                    pass
            
            # CHB-MIT format: "Seizure 1 End Time: 3036 seconds"
            elif "End Time" in line and ":" in line:
                try:
                    time_str = line.split(":")[-1].strip().split()[0]
                    end_times.append(int(time_str))
                except:
                    pass
        
        # If CHB-MIT format found, pair them
        if start_times and end_times:
            seizure_ranges = list(zip(start_times, end_times))
        
        # If not CHB-MIT format, try simple number format
        if not seizure_ranges:
            for line in lines:
                # Skip headers and empty lines
                if not line.strip() or any(x in line.lower() for x in ['seizure', 'file', 'number']):
                    continue
                
                # Try to extract two numbers from the line (comma, space, or semicolon separated)
                line_clean = line.replace(',', ' ').replace(';', ' ').strip()
                numbers = []
                for part in line_clean.split():
                    try:
                        numbers.append(int(float(part)))
                    except:
                        pass
                
                if len(numbers) >= 2:
                    seizure_ranges.append((numbers[0], numbers[1]))
        
        if not seizure_ranges:
            raise ValueError("No valid seizure start-end pairs found in any supported format.")

        cleaned_path = seizures_path + "_cleaned"
        with open(cleaned_path, "w") as f:
            for start, end in seizure_ranges:
                f.write(f"{start} {end}\n")

        return cleaned_path
    except Exception as e:
        st.error(f"Error in processing seizure file: {e}")
        return None

def extract_seizure_annotations(raw_edf, fs):
    """Extract seizure annotations from EDF file metadata"""
    seizure_labels = np.zeros((raw_edf.n_times,))
    
    try:
        # Try to read annotations from EDF file
        if raw_edf.annotations is not None and len(raw_edf.annotations) > 0:
            for annotation in raw_edf.annotations:
                # Look for seizure-related annotations
                if 'seizure' in str(annotation['description']).lower():
                    start_sample = int(annotation['onset'] * fs)
                    duration_samples = int(annotation['duration'] * fs)
                    end_sample = start_sample + duration_samples
                    
                    # Ensure indices are within bounds
                    end_sample = min(end_sample, raw_edf.n_times)
                    if start_sample < raw_edf.n_times:
                        seizure_labels[start_sample:end_sample] = 1
    except:
        pass  # No annotations available
    
    return seizure_labels

def preprocessing(edf_path, seizures_path, ch_labels):
    try:
        raw_edf = mne.io.read_raw_edf(edf_path, preload=True)
        available_channels = set(raw_edf.ch_names)
        valid_channels = [ch for ch in ch_labels if ch in available_channels]

        if not valid_channels:
            st.error("No valid EEG channels found in the file.")
            return None, None

        signals = raw_edf.get_data(picks=valid_channels) * 1e6
        fs = int(raw_edf.info['sfreq'])
        
        # Initialize seizure labels
        seizure_labels = np.zeros((raw_edf.n_times,))
        has_annotations = False

        # Try to extract annotations from EDF file first
        seizure_labels = extract_seizure_annotations(raw_edf, fs)
        if np.sum(seizure_labels) > 0:
            has_annotations = True

        # If no annotations in EDF, try to load from separate file
        if not has_annotations and seizures_path:
            seizures_path = convert_seizure_file(seizures_path)
            if seizures_path is not None:
                try:
                    with open(seizures_path, "r") as f:
                        seizure_ranges = [list(map(int, line.strip().split())) for line in f.readlines()]
                        for start, end in seizure_ranges:
                            seizure_labels[start:end] = 1
                    has_annotations = True
                except Exception as e:
                    st.warning(f"Could not parse seizure file: {e}")

        time_window, time_step = 8, 4
        step_window, step = time_window * fs, time_step * fs

        segment_count = (raw_edf.n_times - step_window) // step
        if segment_count <= 0:
            st.error("EEG file is too short for analysis.")
            return None, None

        signals_segments = np.array([signals[:, i * step : i * step + step_window] for i in range(segment_count)])
        seizure_indices = np.array([seizure_labels[i * step : i * step + step_window].sum() / step_window for i in range(segment_count)])

        return signals_segments, seizure_indices
    except Exception as e:
        st.error(f"Error in preprocessing: {e}")
        return None, None

def plot_prediction(pred, true_labels, time_step, mv_win=3):
    fig, ax = plt.subplots(figsize=(12, 2))
    time_axis = np.arange(pred.size) * time_step
    ax.plot(time_axis, pred.flatten(), alpha=0.7, label='Model Prediction')
    ax.plot(time_axis, true_labels, alpha=0.7, label='True Labels')

    pred_moving_ave = np.convolve(pred.flatten(), np.ones(mv_win) / mv_win, mode='valid')
    time_axis_smoothed = np.arange(pred.size - mv_win + 1) * time_step
    ax.plot(time_axis_smoothed, pred_moving_ave, alpha=0.9, label='Smoothed Prediction', color='tab:pink')

    pred_peaks, _ = find_peaks(pred_moving_ave, height=0.95, distance=6)
    ax.scatter(time_axis_smoothed[pred_peaks], pred_moving_ave[pred_peaks], s=20, color='tab:red', label='Seizure Peaks')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Prediction Probability')
    ax.legend(loc='upper right')
    st.pyplot(fig)

# Load model
try:
    model_dir = Path(__file__).parent
    model_path = model_dir / "CHB_MIT_sz_detec_demo.h5"
    
    if not model_path.exists():
        st.error(f"Model file not found at {model_path}. Please ensure CHB_MIT_sz_detec_demo.h5 is in the project directory.")
        model = None
    else:
        model = load_model(str(model_path))
        st.success("Model loaded successfully!")
except Exception as e:
    st.error(f"Error loading model: {e}")
    model = None

if edf_file:
    # EEG file provided - pure prediction mode
    if model is None:
        st.error("❌ Model not loaded. Please ensure CHB_MIT_sz_detec_demo.h5 exists.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as tmp_edf:
            tmp_edf.write(edf_file.getvalue())
            edf_path = tmp_edf.name

        ch_labels = ['FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1', 'FP1-F3', 'F3-C3', 'C3-P3', 'P3-O1',
                    'FP2-F4', 'F4-C4', 'C4-P4', 'P4-O2', 'FP2-F8', 'F8-T8', 'T8-P8', 'P8-O2',
                    'FZ-CZ', 'CZ-PZ']

        with st.spinner("🔄 Analyzing EEG data..."):
            try:
                raw_edf = mne.io.read_raw_edf(edf_path, preload=True)
                available_channels = set(raw_edf.ch_names)
                valid_channels = [ch for ch in ch_labels if ch in available_channels]

                if not valid_channels:
                    st.error("❌ No valid EEG channels found in this file.")
                else:
                    st.success(f"✅ Loaded {len(valid_channels)} EEG channels")
                    
                    signals = raw_edf.get_data(picks=valid_channels) * 1e6
                    fs = int(raw_edf.info['sfreq'])
                    time_window, time_step = 8, 4
                    step_window, step = time_window * fs, time_step * fs

                    segment_count = (raw_edf.n_times - step_window) // step
                    if segment_count <= 0:
                        st.error("❌ EEG file is too short (minimum 8 seconds required).")
                    else:
                        signals_segments = np.array([signals[:, i * step : i * step + step_window] for i in range(segment_count)])
                        array_signals = signals_segments[:, :, ::2, np.newaxis]
                        
                        # Get predictions
                        predictions = model.predict(array_signals, verbose=0)
                        
                        # Create visualization
                        fig, ax = plt.subplots(figsize=(14, 3))
                        time_axis = np.arange(predictions.size) * time_step
                        ax.plot(time_axis, predictions.flatten(), alpha=0.7, color='#1f77b4', linewidth=2, label='Model Prediction')
                        
                        # Smoothed prediction
                        pred_moving_ave = np.convolve(predictions.flatten(), np.ones(3) / 3, mode='valid')
                        time_axis_smoothed = np.arange(predictions.size - 3 + 1) * time_step
                        ax.plot(time_axis_smoothed, pred_moving_ave, alpha=0.9, color='#ff7f0e', linewidth=2, label='Smoothed Prediction')
                        
                        # Detected peaks
                        pred_peaks, _ = find_peaks(pred_moving_ave, height=0.5, distance=2)
                        if len(pred_peaks) > 0:
                            ax.scatter(time_axis_smoothed[pred_peaks], pred_moving_ave[pred_peaks], s=100, color='#d62728', marker='v', label='Seizure Events', zorder=5)
                        
                        ax.set_xlabel('Time (seconds)', fontsize=11)
                        ax.set_ylabel('Seizure Probability', fontsize=11)
                        ax.set_ylim([0, 1.05])
                        ax.grid(True, alpha=0.3)
                        ax.legend(loc='upper right', fontsize=10)
                        ax.set_title('Seizure Prediction Timeline', fontsize=12, fontweight='bold')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Professional results
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        max_pred = np.max(predictions)

                        max_time = np.argmax(predictions) * time_step

                        seizure_count = max(len(pred_peaks), 1) if max_pred > 0.7 else len(pred_peaks)
                        
                        with col1:
                            st.metric("🔴 Overall Seizure Probability", f"{max_pred*100:.2f}%", 
                                     delta="High Risk" if max_pred > 0.5 else "Low Risk")
                        
                        with col2:
                            st.metric("⏱️ Peak Detection Time", f"{max_time:.1f}s", 
                                     delta=f"{seizure_count} events" if seizure_count > 0 else "No events")
                        
                        st.markdown("---")
                        
                        # Final diagnosis
                        if max_pred > 0.7:
                            st.error(f"⚠️ **HIGH RISK - SEIZURE LIKELY DETECTED**\n\nModel Confidence: **{max_pred*100:.2f}%**\n\nDetected at approximately **{max_time:.1f} seconds** into the recording.", icon="🚨")
                        elif max_pred > 0.5:
                            st.warning(f"⚠️ **MODERATE RISK - POSSIBLE SEIZURE ACTIVITY**\n\nModel Confidence: **{max_pred*100:.2f}%**\n\nDetected at approximately **{max_time:.1f} seconds** into the recording.")
                        else:
                            st.success(f"✅ **LOW RISK - NO SEIZURE DETECTED**\n\nModel Confidence: **{max_pred*100:.2f}%**\n\nEEG recording appears normal.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
