# EEG Seizure Detection System

A professional, production-ready full-stack web application for detecting seizures in EEG (electroencephalogram) signals using deep learning. Originally a Streamlit-based application, now transformed into a scalable microservices architecture with React frontend and FastAPI backend.

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Frontend    │───▶│  Backend     │───▶│  PostgreSQL  │
│  React + TS  │    │  FastAPI     │    │  Database    │
│  Port 3000   │    │  Port 5000   │    │  Port 5432   │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────▼───────┐    ┌──────────────┐
                    │  Celery      │───▶│  Redis       │
                    │  Worker      │    │  Cache/Queue │
                    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────▼───────┐
                    │  ML Engine   │
                    │  TensorFlow  │
                    │  + MNE-Python│
                    └──────────────┘
```

## Features

### Backend (FastAPI)
- **Authentication**: JWT-based with refresh tokens, bcrypt password hashing
- **File Management**: Secure upload/download of .edf and .seizures files (max 500MB)
- **ML Pipeline**: Async seizure detection via Celery + Redis task queue
- **REST API**: 15+ endpoints with Pydantic validation, OpenAPI/Swagger docs
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Caching**: Redis for task queue and result caching
- **Visualization**: Matplotlib-generated plots with base64 encoding

### Frontend (React + TypeScript)
- **Modern UI**: Material-UI (MUI v5) with light/dark theme support
- **State Management**: Redux Toolkit for global state
- **Data Fetching**: React Query with automatic caching and retry
- **Charts**: Recharts for interactive visualization
- **Routing**: React Router v6 with protected routes
- **Forms**: React Hook Form + Yup validation
- **Responsive**: Mobile-first design with sidebar navigation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript 5, MUI 5, Redux Toolkit, Recharts |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0, Celery |
| **Database** | PostgreSQL 15, Redis 7 |
| **ML** | TensorFlow 2.13, MNE-Python, SciPy, Matplotlib |
| **DevOps** | Docker, Docker Compose, Nginx |

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.11+, Node.js 18+ (manual setup)

### Docker Setup (Recommended)
```bash
# Clone the repository
git clone <repo-url> && cd AD-EEG-Signal-Analysis-main

# Start all services
docker-compose up --build

# Access the application
Frontend: http://localhost:3000
Backend API: http://localhost:5000
API Docs: http://localhost:5000/docs
```

### Manual Setup

#### Backend
```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy model file
cp ../CHB_MIT_sz_detec_demo.h5 ./models/

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Database
```bash
# Ensure PostgreSQL and Redis are running
# Create the database
createdb eeg_db

# Run migrations
cd backend
alembic upgrade head
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Sign in
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Sign out

### Users
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/profile/statistics` - Get user stats
- `GET /api/users/login-history` - View login history
- `POST /api/users/change-password` - Change password
- `DELETE /api/users/account` - Delete account

### Files
- `POST /api/files/upload` - Upload .edf or .seizures file
- `GET /api/files/list` - List uploaded files
- `GET /api/files/{id}` - Get file metadata
- `GET /api/files/{id}/download` - Download file
- `DELETE /api/files/{id}` - Delete file

### Predictions
- `POST /api/predictions/detect` - Start seizure detection
- `GET /api/predictions/{taskId}/status` - Check detection status
- `GET /api/predictions/{taskId}/results` - Get detection results
- `POST /api/predictions/{taskId}/rerun` - Re-run with new threshold

### Results
- `GET /api/results/history` - View detection history
- `GET /api/results/{resultId}` - Get detailed results
- `DELETE /api/results/{resultId}` - Delete result
- `POST /api/results/{resultId}/export` - Export results (JSON/CSV)

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/trends` - Time-series trend data

### Health
- `GET /api/health` - API health check

## EEG Processing Pipeline

1. **File Loading**: EDF file read using MNE-Python
2. **Channel Extraction**: 18 bipolar EEG channels
3. **Normalization**: Convert to microvolts (µV)
4. **Windowing**: Create 8-second windows with 4-second overlap
5. **Prediction**: TensorFlow model classifies each window
6. **Smoothing**: 3-sample moving average applied
7. **Peak Detection**: Peaks identified above 0.95 threshold
8. **Visualization**: 4-panel plot (raw predictions, true labels, smoothed, seizure regions)

## Database Schema

- **users**: User accounts with bcrypt-hashed passwords
- **files**: Uploaded EDF and seizure annotation files
- **detections**: Detection job tracking with Celery task IDs
- **results**: Detection output with predictions, peaks, visualizations
- **login_history**: User login audit trail

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── middleware/          # Auth, CORS, error handling
│   │   ├── routes/             # API endpoints (7 route files)
│   │   ├── models/             # SQLAlchemy ORM models (5 models)
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── ml_engine/          # EEG processing, model, prediction
│   │   ├── services/           # Business logic layer
│   │   ├── tasks/              # Celery async tasks
│   │   └── utils/              # JWT, logging, file utilities
│   ├── alembic/                # Database migrations
│   ├── models/                 # Trained ML model
│   ├── uploads/                # File storage
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   ├── pages/              # Route pages (9 pages)
│   │   ├── store/              # Redux state management
│   │   ├── services/           # API client services
│   │   ├── hooks/              # Custom React hooks
│   │   ├── types/              # TypeScript interfaces
│   │   ├── utils/              # Formatters, validators
│   │   └── styles/             # MUI theme configuration
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Multi-container orchestration
├── CHB_MIT_sz_detec_demo.h5   # Pre-trained TensorFlow model
└── run.py                      # Original Streamlit app (legacy)
```

## Deployment

### Production Options
1. **AWS**: ECS Fargate + RDS + ElastiCache + S3
2. **Google Cloud**: Cloud Run + Cloud SQL + Memorystore
3. **DigitalOcean**: App Platform + Managed PostgreSQL
4. **Single Server**: Docker Compose with Nginx reverse proxy

### Environment Variables
See `.env.example` files in `backend/` and `frontend/` for configuration.

## Testing

### Backend Tests
```bash
cd backend
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Security

- **Authentication**: JWT with refresh token rotation
- **Passwords**: Bcrypt hashing (12 rounds)
- **API**: Rate limiting, input validation, CORS configuration
- **Files**: Type validation, size limits, secure storage
- **Database**: SQL injection prevention via ORM
- **XSS**: React automatic escaping

## Model Information

- **Architecture**: Pre-trained TensorFlow neural network
- **Training Data**: CHB-MIT EEG Database
- **Input**: 18 channels × 8 seconds @ 500Hz (shape: [batch, 18, 4000, 1])
- **Output**: Single probability value per window
- **Threshold**: Default 0.5 (configurable)
- **File**: `CHB_MIT_sz_detec_demo.h5`

## EEG Channel Configuration

Standard 18 bipolar channels:
- FP1-F7, F7-T7, T7-P7, P7-O1
- FP1-F3, F3-C3, C3-P3, P3-O1
- FP2-F4, F4-C4, C4-P4, P4-O2
- FP2-F8, F8-T8, T8-P8, P8-O2
- FZ-CZ, CZ-PZ

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files.
