import numpy as np
from pathlib import Path
from app.config import settings
from app.utils.logger import logger

try:
    from tensorflow.keras.models import load_model as tf_load_model
    _tf_available = True
except ImportError:
    tf_load_model = None
    _tf_available = False
    logger.warning("TensorFlow not available - model loading disabled")

_model_instance = None
_model_loaded = False


def load_model(model_path: str = None) -> object:
    global _model_instance, _model_loaded
    if _model_loaded and _model_instance is not None:
        return _model_instance

    if not _tf_available:
        logger.warning("TensorFlow not available - cannot load model")
        return None

    path = model_path or settings.MODEL_PATH
    path_obj = Path(path)

    if not path_obj.exists():
        logger.error(f"Model file not found at {path}")
        _model_loaded = False
        return None

    try:
        logger.info(f"Loading model from {path}")
        _model_instance = tf_load_model(str(path_obj))
        _model_loaded = True
        logger.info("Model loaded successfully")
        return _model_instance
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model_loaded = False
        return None


def get_model() -> object:
    return load_model()


def is_model_loaded() -> bool:
    return _model_loaded and _model_instance is not None


def get_model_info() -> dict:
    model = get_model()
    if model is None:
        return {"loaded": False, "input_shape": None, "output_shape": None}

    return {
        "loaded": True,
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
        "params": model.count_params(),
    }


def unload_model():
    global _model_instance, _model_loaded
    _model_instance = None
    _model_loaded = False
    import gc
    gc.collect()
