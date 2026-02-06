import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.config.settings import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# create_access_token and verify_google_token removed as we delegate auth to Supabase


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Supabase JWT 검증 및 사용자 식별 (via Remote API)
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Supabase URL이 설정되지 않은 경우
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        logger.error("SUPABASE_URL or SUPABASE_ANON_KEY is not set!")
        raise HTTPException(status_code=500, detail="Server misconfiguration: Auth keys missing")

    try:
        # Remote Verification: Supabase Auth Server에 직접 토큰 유효성 확인
        # (알고리즘이 HS256이든 ES256이든 상관없이 확실하게 검증됨)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
                timeout=10.0,
            )

            if response.status_code != 200:
                logger.warning(f"Supabase Token Verification Failed: {response.text}")
                raise HTTPException(status_code=401, detail="Could not validate credentials")

            user_data = response.json()
            # user_data 구조: {"id": "...", "email": "...", ...}
            return {"id": user_data["id"], "email": user_data.get("email")}

    except httpx.RequestError as e:
        logger.error(f"Auth Service Internal Error: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from e
    except Exception as e:
        logger.error(f"Unexpected Auth Error: {e}")
        # 401을 반환해야 프론트엔드가 로그아웃 처리 등을 할 수 있음
        raise HTTPException(status_code=401, detail="Authentication failed") from e


async def verify_turnstile(token: str) -> bool:
    """Verify Cloudflare Turnstile token."""
    if not settings.TURNSTILE_SECRET_KEY:
        # Secret key가 없으면 검증을 건너뜁니다 (개발 환경 대비)
        logger.warning("TURNSTILE_SECRET_KEY not set. Skipping verification.")
        return True

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            json={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
        )
        result = response.json()

        if not result.get("success"):
            error_codes = result.get("error-codes", [])
            logger.error(f"Turnstile verification failed: {error_codes}")
            return False

        return True
