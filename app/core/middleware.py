import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log incoming request
        logger.info(f"→ {request.method} {request.url.path}")

        response = await call_next(request)

        # Log response
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"← {request.method} {request.url.path} {response.status_code} ({duration}ms)")

        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract org_id from token if present
        from jose import jwt, JWTError
        from app.core.config import settings

        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                request.state.org_id = payload.get("org_id")
                request.state.user_email = payload.get("sub")
                request.state.user_role = payload.get("role")
            except JWTError:
                request.state.org_id = None
                request.state.user_email = None
                request.state.user_role = None
        else:
            request.state.org_id = None
            request.state.user_email = None
            request.state.user_role = None

        response = await call_next(request)
        return response