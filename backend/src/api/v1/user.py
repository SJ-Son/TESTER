from fastapi import APIRouter, Depends, HTTPException, Request
from src.api.v1.deps import limiter
from src.auth import get_current_user
from src.services.supabase_service import SupabaseService
from src.types import AuthenticatedUser
from src.utils.logger import get_logger
from starlette.concurrency import run_in_threadpool

router = APIRouter()
logger = get_logger(__name__)


@router.get("/status")
@limiter.limit("10/minute")
async def get_user_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """사용자의 현재 상태 및 쿼터 사용량을 조회합니다.

    Args:
        request: HTTP 요청 객체 (Rate Limiting용).
        current_user: 인증된 사용자 정보.

    Returns:
        사용자 상태 정보 (ID, 이메일, 주간 쿼터 사용량 등).

    Raises:
        HTTPException: 데이터베이스 조회 실패 등의 내부 오류 시 (500).
    """
    try:
        supabase = SupabaseService()
        current_usage = await run_in_threadpool(supabase.check_weekly_quota, current_user["id"])

        # 로그에 이모지 제거 및 구조화된 컨텍스트 추가
        logger.info_ctx(
            "사용자 상태 조회",
            user_id=current_user["id"],
            usage=current_usage,
        )

        return {
            "user": current_user,
            "quota": {
                "limit": 30,  # 주간 30회 제한 (하드코딩된 정책)
                "used": current_usage,
                "remaining": max(0, 30 - current_usage),
            },
        }
    except Exception as e:
        logger.error(f"사용자 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="사용자 상태를 불러오는데 실패했습니다") from e
