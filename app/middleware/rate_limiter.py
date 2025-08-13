from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.session_tracker import SessionTracker
from app.core.config import get_settings
from app.core.auth import verify_token
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.tracker = SessionTracker()

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        # Extract user ID from JWT token (if present)
        user_id = "anonymous"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if payload and "sub" in payload:
                user_id = payload["sub"]

        # Check rate limit
        if not self.tracker.add_request(user_id, settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW):
            logger.warning(f"Rate limit exceeded for user: {user_id} on {request.method} {request.url}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        return response

def add_rate_limit_middleware(app: FastAPI):
    app.add_middleware(RateLimitMiddleware)