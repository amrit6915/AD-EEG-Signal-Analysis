from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception(f"Unhandled error: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(e)},
            )
