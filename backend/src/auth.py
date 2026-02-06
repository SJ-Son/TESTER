import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.config.settings import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# create_access_token and verify_google_token removed as we delegate auth to Supabase


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Supabase JWT 검증 및 사용자 식별
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not settings.SUPABASE_JWT_SECRET:
        # JWT Secret이 설정되지 않은 경우 (개발 환경 등)
        # 하지만 프로덕션에서는 필수입니다.
        logger.error("SUPABASE_JWT_SECRET is not set! Cannot verify tokens.")
        raise HTTPException(
            status_code=500, detail="Server misconfiguration: Authentication unavailable"
        )

    try:
        # Supabase JWT는 HS256 알고리즘 사용
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",  # Supabase 기본 aud
            options={"verify_aud": False},  # aud가 다를 수 있으므로 일단 끔 (필요시 활성화)
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")

        return {"id": user_id, "email": payload.get("email")}

    except JWTError as e:
        logger.warning(f"JWT Verification failed: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials") from None


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
