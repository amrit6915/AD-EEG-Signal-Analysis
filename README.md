# EEG Seizure Detection System

A deep learning-based EEG seizure detection system built using TensorFlow, MNE-Python, and Streamlit. The project analyzes EEG recordings from the CHB-MIT Scalp EEG Database and predicts seizure events with probability scoring, peak detection, and visualization.

The repository also includes a scalable FastAPI backend and React frontend architecture for future deployment and production use.

---

## Features

### EEG Seizure Detection

* Upload EEG recordings in EDF format
* Deep learning-based seizure prediction
* Real-time seizure probability estimation
* Peak seizure event detection
* Interactive visualization dashboard
* Support for CHB-MIT EEG dataset

### Machine Learning

* TensorFlow neural network model
* MNE-Python EEG processing pipeline
* Signal normalization and preprocessing
* Sliding-window inference
* Moving-average smoothing
* Seizure peak identification

### Full-Stack Architecture

* FastAPI backend
* React + TypeScript frontend
* PostgreSQL database support
* Redis caching and task queue
* Docker deployment support
* REST API architecture

---

## Project Structure

```text
├── backend/
├── frontend/
├── docker-compose.yml
├── requirements.txt
├── CHB_MIT_sz_detec_demo.h5
├── run.py
└── uploads/
```

---

## Quick Start (Streamlit Demo)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run run.py
```

### Open in Browser

```text
http://localhost:8501
```

---

## Example Dataset

This project was tested using recordings from the CHB-MIT EEG Database.

### Verified Detection Results

#### chb01_03.edf

Ground Truth:

```text
Seizure Start: 2996 seconds
Seizure End:   3036 seconds
```

Model Prediction:

```text
Peak Detection Time: 3008 seconds
Probability: 98.56%
```

Result:

```text
Correct Detection
Peak lies inside annotated seizure interval
```

---

#### chb01_04.edf

Ground Truth:

```text
Seizure Start: 1467 seconds
Seizure End:   1494 seconds
```

Model Prediction:

```text
Peak Detection Time: 1476 seconds
Probability: 83.98%
```

Result:

```text
Correct Detection
Peak lies inside annotated seizure interval
```

---

## EEG Processing Pipeline

1. Load EDF EEG recording
2. Extract bipolar EEG channels
3. Normalize EEG signals
4. Create overlapping windows
5. Generate TensorFlow predictions
6. Apply smoothing
7. Detect seizure peaks
8. Visualize predictions and seizure events

---

## Model Information

| Property   | Value                    |
| ---------- | ------------------------ |
| Framework  | TensorFlow               |
| Dataset    | CHB-MIT EEG Database     |
| Input      | 18 Channels × 8 Seconds  |
| Output     | Seizure Probability      |
| Model File | CHB_MIT_sz_detec_demo.h5 |

---

## Technology Stack

### Machine Learning

* TensorFlow
* NumPy
* SciPy
* MNE-Python
* Matplotlib

### Frontend

* React
* TypeScript
* Material UI
* Redux Toolkit
* Recharts

### Backend

* FastAPI
* SQLAlchemy
* Celery
* PostgreSQL
* Redis

### DevOps

* Docker
* Docker Compose
* Nginx

---

## Future Enhancements

* Multi-patient analysis
* Real-time EEG streaming
* Clinical report generation
* Cloud deployment
* Mobile dashboard support
* Model retraining pipeline

---

## License

MIT License


HOW TO RUN LOCAL:-

cd "C:\Users\KIIT\Desktop\PROJECTS\EEG SIGNAL ANALYSIS\AD-EEG-Signal-Analysis-main"
streamlit run run.py