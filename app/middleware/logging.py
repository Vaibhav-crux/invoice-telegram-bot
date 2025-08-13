from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

access_logger = logging.getLogger("access")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        access_logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        process_time = time.time() - start_time
        access_logger.info(f"Completed request: {request.method} {request.url} in {process_time:.2f}s with status {response.status_code}")
        return response

def add_logging_middleware(app: FastAPI):
    app.add_middleware(LoggingMiddleware)