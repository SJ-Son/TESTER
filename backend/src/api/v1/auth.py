from datetime import timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_google_token

router = APIRouter()


class TokenRequest(BaseModel):
    id_token: str


@router.post("/google")
async def google_auth(data: TokenRequest):
    user_info = verify_google_token(data.id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Google Token")

    access_token = create_access_token(
        data={"sub": user_info["sub"], "email": user_info["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
