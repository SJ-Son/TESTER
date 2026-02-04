import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from src.config.settings import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_google_token(token: str) -> Optional[dict]:
    try:
        # id_token.verify_oauth2_token 검증
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

        # 유효한 발행처인지 확인 (accounts.google.com)
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        return idinfo
    except Exception as e:
        logger.error(f"Google token verification failed: {e}")
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": payload.get("email")}
    except JWTError:
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
