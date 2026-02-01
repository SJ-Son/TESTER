import logging

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.src.config.settings import settings

logger = logging.getLogger(__name__)


# Rate Limiting Setup
def get_user_identifier(request: Request):
    """
    Identify user for rate limiting.
    Uses user ID if authenticated, otherwise request IP.
    """
    user = getattr(request.state, "user", None)
    if user:
        return f"user_{user['id']}"
    return get_remote_address(request)


limiter = Limiter(key_func=get_user_identifier)

# Security - Internal API Key
API_KEY_NAME = "X-TESTER-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != settings.TESTER_INTERNAL_SECRET:
        logger.warning(f"Unauthorized access attempt with key: {api_key}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Internal API Key")
    return api_key
