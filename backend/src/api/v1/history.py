import logging

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
    created_at: str


@router.get("/", response_model=list[HistoryItem])
def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    repository: GenerationRepository = Depends(get_generation_repository),
):
    """Retrieve generation history for the current user."""
    # Repository now returns decrypted data models
    history = repository.get_user_history(current_user["id"], limit)
    return history
