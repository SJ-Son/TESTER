"""광고 보상 API 라우터.

광고 시청 완료 후 토큰 보상을 처리합니다.
S2S 검증 및 중복 방지 로직이 포함되어 있습니다.
"""

from fastapi import APIRouter, Depends, Request
from src.api.v1.deps import get_token_service, limiter
from src.auth import get_current_user
from src.exceptions import AdRewardLimitError, DuplicateTransactionError
from src.services.token_service import TokenService
from src.types import AdRewardRequest, AdRewardResponse, AuthenticatedUser
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/reward", response_model=AdRewardResponse)
@limiter.limit("15/minute")
async def claim_ad_reward(
    request: Request,
    data: AdRewardRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    token_service: TokenService = Depends(get_token_service),
):
    """광고 시청 완료 후 토큰 보상을 처리합니다.

    클라이언트에서 광고 시청 완료 콜백을 받은 후 호출됩니다.
    트랜잭션 ID를 기반으로 중복 지급을 방지합니다.

    Args:
        request: HTTP 요청 객체 (Rate Limiting용).
        data: 광고 보상 요청 데이터 (ad_network, transaction_id, timestamp).
        current_user: 인증된 사용자 정보.
        token_service: 토큰 관리 서비스 의존성.

    Returns:
        AdRewardResponse: 보상 처리 결과.

    Raises:
        AdRewardLimitError: 일일 광고 한도 초과 시.
        DuplicateTransactionError: 중복 보상 요청 시.
    """
    logger.info_ctx(
        "광고 보상 요청",
        user_id=current_user["id"],
        ad_network=data.ad_network,
        transaction_id=data.transaction_id[:16],
    )

    result = await token_service.process_ad_reward(
        user_id=current_user["id"],
        transaction_id=data.transaction_id,
    )

    return AdRewardResponse(
        success=result.get("success", False),
        added_tokens=result.get("added", 0),
        current_tokens=result.get("current_balance", 0),
    )
