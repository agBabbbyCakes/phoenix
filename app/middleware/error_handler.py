"""Global error handling middleware."""
from __future__ import annotations

import logging
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def exception_handler_middleware(request: Request, call_next: Callable):
    """Global exception handler middleware."""
    try:
        response = await call_next(request)
        return response
    except StarletteHTTPException as exc:
        # Handle HTTP exceptions
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_exception",
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )
    except RequestValidationError as exc:
        # Handle validation errors
        logger.warning(f"Validation error: {exc.errors()} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "detail": exc.errors(),
                "status_code": 422,
            },
        )
    except Exception as exc:
        # Handle all other exceptions
        logger.exception(f"Unhandled exception: {exc} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "detail": "An internal server error occurred. Please try again later.",
                "status_code": 500,
            },
        )

