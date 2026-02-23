from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api.v1.deps import get_generation_repository
from src.auth import get_current_user
from src.repositories.generation_repository import GenerationRepository
from src.types import AuthenticatedUser
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class HistoryItem(BaseModel):
    id: UUID
    input_code: str
    generated_code: str
    language: str
    model: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2: orm_mode 대체


@router.get("/", response_model=list[HistoryItem])
async def get_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
    repository: GenerationRepository = Depends(get_generation_repository),
):
    """사용자의 생성 이력 목록을 조회합니다.

    최근 생성된 순서대로 정렬하여 반환하며, 암호화된 코드는 복호화되어 전달됩니다.

    Args:
        current_user: 인증된 사용자 정보.
        repository: 생성 이력 저장소 의존성.

    Returns:
        HistoryItem 객체의 리스트.

    Raises:
        HTTPException: 조회 실패 시 (500).
    """
    try:
        history = await repository.get_user_history(current_user["id"])

        logger.info_ctx(
            "생성 이력 조회 성공",
            user_id=current_user["id"],
            count=len(history),
        )
        return history
    except Exception as e:
        logger.error(f"이력 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="이력을 불러오는데 실패했습니다") from e
