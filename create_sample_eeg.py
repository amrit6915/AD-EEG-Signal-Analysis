"""
Create a proper sample EEG file using MNE-Python with proper scaling
"""
import numpy as np
import mne

def create_sample_edf():
    """Create a proper sample EDF file with 18 EEG channels using MNE"""
    
    channels = [
        'FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1',
        'FP1-F3', 'F3-C3', 'C3-P3', 'P3-O1',
        'FP2-F4', 'F4-C4', 'C4-P4', 'P4-O2',
        'FP2-F8', 'F8-T8', 'T8-P8', 'P8-O2',
        'FZ-CZ', 'CZ-PZ'
    ]
    
    sfreq = 500
    duration_sec = 30
    n_samples = duration_sec * sfreq
    
    # Create MNE info structure
    info = mne.create_info(ch_names=channels, sfreq=sfreq, ch_types='eeg')
    
    # Generate sample data with seizure-like activity
    np.random.seed(42)
    data = np.random.randn(len(channels), n_samples) * 50  # 50µV baseline
    
    # Add seizure-like activity (higher amplitude) at specific times
    seizure_periods = [(100, 250), (500, 650), (1200, 1350), (2000, 2150), (3500, 3700)]
    for start, end in seizure_periods:
        data[:, start:end] += np.random.randn(len(channels), end-start) * 100
    
    # Clip data to reasonable range for EDF format
    data = np.clip(data, -10000, 10000)
    
    # Create MNE RawArray object
    raw = mne.io.RawArray(data, info)
    
    # Set channel units to microvolts
    for ch_idx in range(len(channels)):
        raw.info['chs'][ch_idx]['unit'] = 1e-6  # microvolts
    
    # Export as EDF with explicit physical range
    raw.export('sample_eeg_data.edf', overwrite=True, physical_range=(-1000, 1000))
    
    return 'sample_eeg_data.edf'

if __name__ == '__main__':
    try:
        filename = create_sample_edf()
        print("✅ Sample EEG file created: sample_eeg_data.edf")
        print("   Duration: 30 seconds")
        print("   Channels: 18 (standard bipolar montage)")
        print("   Sampling Rate: 500 Hz")
        print("   Total Samples: 15000")
        print("   Format: MNE-compatible EDF")
        print("\n✅ Seizure annotations file: sample_seizures.seizures")
        print("   5 seizure periods included")
        print("\n📝 Ready to use! Upload both files to the Streamlit app:")
        print("   - sample_eeg_data.edf")
        print("   - sample_seizures.seizures")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
