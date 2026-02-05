import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api.v1.deps import get_supabase_service
from src.auth import get_current_user
from src.services.supabase_service import SupabaseService

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
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    supabase_service: SupabaseService = Depends(get_supabase_service),
):
    """Retrieve generation history for the current user."""
    history = supabase_service.get_history(current_user["id"], limit)
    return history
