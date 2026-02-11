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

    # Supabase URL/Key 미설정 시 500 에러
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY.get_secret_value():
        logger.error("SUPABASE_URL or SUPABASE_ANON_KEY is not set!")
        raise HTTPException(status_code=500, detail=ErrorMessages.AUTH_SERVICE_UNAVAILABLE)

    try:
        # Supabase Auth 서버에 직접 토큰 검증 요청
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

            try:
                user_data = response.json()
                return {"id": user_data["id"], "email": user_data.get("email")}
            except (ValueError, KeyError) as e:
                logger.error(f"Invalid auth response: {e}, body: {response.text[:100]}")
                raise HTTPException(
                    status_code=401, detail=ErrorMessages.AUTH_INVALID_CREDENTIALS
                ) from e

    except httpx.RequestError as e:
        logger.error(f"Auth Service Internal Error: {e}")
        # 인증 서버 연결 실패 시 보안을 위해 503(Service Unavailable) 반환
        raise HTTPException(status_code=503, detail=ErrorMessages.AUTH_SERVICE_UNAVAILABLE) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected Auth Error: {e}")
        raise HTTPException(status_code=401, detail=ErrorMessages.AUTH_FAILED) from e


async def verify_turnstile(token: str) -> bool:
    """Cloudflare Turnstile 토큰 검증"""
    if not settings.TURNSTILE_SECRET_KEY.get_secret_value():
        logger.warning("TURNSTILE_SECRET_KEY 미설정. 검증 건너뜀.")
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
                logger.error(f"Turnstile 검증 실패: {error_codes}")
                return False

            return True
    except httpx.RequestError as e:
        logger.error(f"Turnstile 연결 실패: {e}. 요청 허용 (Fail-Open).")
        return True


async def validate_turnstile_token(token: str) -> None:
    """FastAPI Dependency for Turnstile validation."""
    from src.exceptions import TurnstileError

    if not await verify_turnstile(token):
        raise TurnstileError(token_preview=token)
