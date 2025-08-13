from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic_core import ValidationError
import logging

logger = logging.getLogger(__name__)

def custom_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, ValidationError):
        # Handle Pydantic validation errors
        error_message = exc.errors()[0]["msg"] if exc.errors() else "Invalid input"
        logger.warning(f"Validation error: {error_message} for {request.method} {request.url}")
        return JSONResponse(
            status_code=422,
            content={"detail": error_message}
        )
    if isinstance(exc, StarletteHTTPException):
        # Handle FastAPI HTTP exceptions
        logger.warning(f"HTTP error: {exc.status_code} - {exc.detail} for {request.method} {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )
    elif isinstance(exc, HTTPException):
        # Handle custom HTTP exceptions
        logger.warning(f"Custom HTTP error: {exc.status_code} - {exc.detail} for {request.method} {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )
    else:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(exc)} for {request.method} {request.url}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

def add_error_middleware(app: FastAPI):
    # handle customs errors
    app.exception_handler(ValidationError)(custom_error_handler)
    app.exception_handler(StarletteHTTPException)(custom_error_handler)
    app.exception_handler(Exception)(custom_error_handler)