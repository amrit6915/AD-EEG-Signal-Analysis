from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.middleware.cors import setup_cors
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.utils.logger import logger
from app.ml_engine.model_loader import load_model

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Model path: {settings.MODEL_PATH}")
    model = load_model()
    if model:
        logger.info("Model loaded successfully on startup")
    else:
        logger.warning("Model not found at startup - will be loaded on demand")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

setup_cors(app)
app.add_middleware(ErrorHandlerMiddleware)

from app.routes import health, auth, users, files, predictions, results, analytics

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(files.router)
app.include_router(predictions.router)
app.include_router(results.router)
app.include_router(analytics.router)
