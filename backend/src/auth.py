import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.config.constants import ErrorMessages, NetworkConstants, SecurityConstants
from src.config.settings import settings
from src.types import AuthenticatedUser

logger = logging.getLogger(__name__)

ALGORITHM = SecurityConstants.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = SecurityConstants.JWT_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# create_access_token and verify_google_token removed as we delegate auth to Supabase


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """
    Supabase JWT 검증 및 사용자 식별 (via Remote API)
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.AUTH_TOKEN_MISSING,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Supabase URL이 설정되지 않은 경우
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY.get_secret_value():
        logger.error("SUPABASE_URL or SUPABASE_ANON_KEY is not set!")
        raise HTTPException(status_code=500, detail=ErrorMessages.AUTH_SERVICE_UNAVAILABLE)

    try:
        # Remote Verification: Supabase Auth Server에 직접 토큰 유효성 확인
        # (알고리즘이 HS256이든 ES256이든 상관없이 확실하게 검증됨)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY.get_secret_value(),
                },
                timeout=NetworkConstants.HTTP_TIMEOUT_SECONDS,
            )

            if response.status_code != 200:
                logger.warning(f"Supabase Token Verification Failed: {response.text}")
                raise HTTPException(status_code=401, detail=ErrorMessages.AUTH_INVALID_CREDENTIALS)

            user_data = response.json()
            # user_data 구조: {"id": "...", "email": "...", ...}
            return {"id": user_data["id"], "email": user_data.get("email")}

    except httpx.RequestError as e:
        logger.error(f"Auth Service Internal Error: {e}")
        # In staging/production, completely blocking auth due to network blip is bad,
        # but failing open for AUTH is dangerous.
        # We must return 503 or 401.
        # But if it crashes with 500, user sees "Internal Server Error".
        # We want to catch this and return 503 "Service Unavailable" cleanly.
        raise HTTPException(status_code=503, detail=ErrorMessages.AUTH_SERVICE_UNAVAILABLE) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected Auth Error: {e}")
        # 401을 반환해야 프론트엔드가 로그아웃 처리 등을 할 수 있음
        raise HTTPException(status_code=401, detail=ErrorMessages.AUTH_FAILED) from e


async def verify_turnstile(token: str) -> bool:
    """Verify Cloudflare Turnstile token."""
    if not settings.TURNSTILE_SECRET_KEY.get_secret_value():
        # Secret key가 없으면 검증을 건너뜁니다 (개발 환경 대비)
        logger.warning("TURNSTILE_SECRET_KEY not set. Skipping verification.")
        return True

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                json={
                    "secret": settings.TURNSTILE_SECRET_KEY.get_secret_value(),
                    "response": token,
                },
                timeout=NetworkConstants.HTTP_TIMEOUT_SECONDS,
            )
            result = response.json()

            if not result.get("success"):
                error_codes = result.get("error-codes", [])
                logger.error(f"Turnstile verification failed: {error_codes}")
                return False

            return True
    except httpx.RequestError as e:
        logger.error(f"Turnstile connection failed: {e}. allowing request (fail-open).")
        return True


async def validate_turnstile_token(token: str) -> None:
    """FastAPI Dependency for Turnstile validation."""
    from src.exceptions import TurnstileError

    if not await verify_turnstile(token):
        raise TurnstileError(token_preview=token)
