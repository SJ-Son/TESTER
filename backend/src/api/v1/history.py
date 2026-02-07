import logging
from datetime import datetime  # datetime 임포트 추가

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api.v1.deps import get_generation_repository
from src.auth import get_current_user
from src.repositories.generation_repository import GenerationRepository

router = APIRouter()
logger = logging.getLogger(__name__)


class HistoryItem(BaseModel):
    id: str
    input_code: str
    generated_code: str
    language: str
    model: str
    # [수정] str -> datetime으로 변경.
    # FastAPI가 자동으로 ISO Format String으로 변환하여 응답합니다.
    created_at: datetime


@router.get("/", response_model=list[HistoryItem])
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    repository: GenerationRepository = Depends(get_generation_repository),
):
    """Retrieve generation history for the current user."""
    # Repository now returns decrypted data models
    history = repository.get_user_history(current_user["id"], limit)
    return history
