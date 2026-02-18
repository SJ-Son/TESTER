from fastapi import APIRouter, Depends, HTTPException, Request
from src.api.v1.deps import get_token_service, limiter
from src.auth import get_current_user
from src.services.token_service import TokenService
from src.types import AuthenticatedUser
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/status")
@limiter.limit("10/minute")
async def get_user_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    token_service: TokenService = Depends(get_token_service),
):
    """사용자의 현재 상태 및 토큰 정보를 조회합니다.

    일일 보너스 미수령 시 자동으로 지급 처리합니다.

    Args:
        request: HTTP 요청 객체 (Rate Limiting용).
        current_user: 인증된 사용자 정보.
        token_service: 토큰 서비스 의존성.

    Returns:
        사용자 상태 정보 (ID, 이메일, 토큰 잔액, 일일 보너스 상태 등).

    Raises:
        HTTPException: 데이터베이스 조회 실패 등의 내부 오류 시 (500).
    """
    try:
        token_info = await token_service.get_token_info(current_user["id"])

        logger.info_ctx(
            "사용자 상태 조회",
            user_id=current_user["id"],
            tokens=token_info.current_tokens,
        )

        return {
            "user": current_user,
            "token_info": token_info.model_dump(),
            # 하위 호환성 유지 (Deprecated, 향후 제거 예정)
            "quota": {
                "limit": 30,
                "used": 0,
                "remaining": token_info.current_tokens // token_info.cost_per_generation
                if token_info.cost_per_generation > 0
                else 0,
            },
        }
    except Exception as e:
        logger.error(f"사용자 상태 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail="사용자 상태를 불러오는데 실패했습니다"
        ) from e
