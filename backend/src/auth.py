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


async def validate_turnstile_token(token: str, ip: str | None = None) -> None:
    """Cloudflare Turnstile 토큰을 검증합니다.

    Args:
        token: 클라이언트가 제출한 Turnstile 토큰.
        ip: 클라이언트 IP 주소 (선택 사항).

    Raises:
        TurnstileError: 토큰 검증에 실패한 경우.
    """
    from src.exceptions import TurnstileError

    if not settings.TURNSTILE_SECRET_KEY:
        # 개발 환경 등에서 키가 설정되지 않은 경우 검증 패스 (로그 경고)
        logger.warning("TURNSTILE_SECRET_KEY가 설정되지 않아 검증을 건너킵니다")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": settings.TURNSTILE_SECRET_KEY.get_secret_value(),
                    "response": token,
                    "remoteip": ip,
                },
                timeout=5.0,
            )
            result = response.json()

            if not result.get("success"):
                error_codes = result.get("error-codes", [])
                logger.warning(
                    "Turnstile 검증 실패",
                    extra={"error_codes": error_codes, "ip": ip},
                )
                raise TurnstileError(
                    message="Turnstile 검증에 실패했습니다",
                    token_preview=token,
                )

    except httpx.RequestError as e:
        logger.error(f"Turnstile 서버 연결 실패: {e}")
        # Fail open: 외부 서비스 장애로 인한 차단 방지
        return
    except TurnstileError:
        raise
    except Exception as e:
        logger.error(f"Turnstile 검증 중 예기치 않은 오류: {e}")
        # 예기치 않은 오류 시 안전하게 통과 (Fail open)
        return
