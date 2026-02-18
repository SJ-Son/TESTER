"""Ko-fi Webhook 라우터.

Ko-fi 결제 이벤트(후원, 구독, 상품 구매)를 수신하고
토큰을 자동 충전합니다.
"""

import json
import secrets
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Form, HTTPException
from src.api.v1.deps import get_token_service
from src.config.constants import TokenConstants
from src.config.settings import settings
from src.services.token_service import TokenService
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _resolve_token_amount(kofi_type: str, amount: str) -> int:
    """Ko-fi 결제 유형과 금액에 따른 토큰 수를 결정합니다.

    Args:
        kofi_type: Ko-fi 이벤트 유형 (Donation, Subscription, Shop Order).
        amount: 결제 금액 (문자열).

    Returns:
        int: 적립할 토큰 수.
    """
    if kofi_type == "Subscription":
        return TokenConstants.KOFI_SUBSCRIPTION_TOKENS

    # Ko-fi Shop Order 또는 Donation 모두 금액 기반 처리 시도
    if kofi_type in ("Shop Order", "Donation"):
        try:
            usd = Decimal(amount)
        except (InvalidOperation, TypeError):
            # 금액 파싱 실패 시 기본 Donation 보상 지급 (Donation인 경우만)
            return TokenConstants.KOFI_DONATION_TOKENS if kofi_type == "Donation" else 0

        # 금액에 따른 토큰 지급 (Decimal 비교 보장)
        for threshold, tokens in sorted(TokenConstants.KOFI_TOKEN_PACKS.items(), reverse=True):
            if usd >= Decimal(str(threshold)):
                return tokens

        # 일치하는 팩이 없으면 기본 Donation 보상
        if kofi_type == "Donation":
            return TokenConstants.KOFI_DONATION_TOKENS

        return 0

    return 0


@router.post("/webhook")
async def kofi_webhook(data: str = Form(...)):
    """Ko-fi Webhook 수신 엔드포인트.

    Ko-fi에서 결제 완료 시 이 엔드포인트로 POST 요청을 보냅니다.
    verification_token으로 요청 유효성을 검증한 후 토큰을 적립합니다.

    Args:
        data: Ko-fi가 Form 데이터로 전송하는 JSON 문자열.

    Returns:
        dict: 처리 결과.

    Raises:
        HTTPException: 검증 실패(403) 또는 처리 오류(400).
    """
    try:
        payload = json.loads(data)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Ko-fi Webhook: 잘못된 JSON 데이터 수신")
        raise HTTPException(status_code=400, detail="잘못된 데이터 형식") from None

    verification_token = payload.get("verification_token", "")
    expected_token = settings.KOFI_VERIFICATION_TOKEN.get_secret_value()

    if not expected_token or not secrets.compare_digest(verification_token, expected_token):
        logger.warning("Ko-fi Webhook: 유효하지 않은 verification_token")
        raise HTTPException(status_code=403, detail="인증 실패")

    kofi_type = payload.get("type", "")
    email = payload.get("email", "")
    amount = payload.get("amount", "0")
    kofi_txn_id = payload.get("kofi_transaction_id", "")
    from_name = payload.get("from_name", "익명")

    logger.info_ctx(
        "Ko-fi Webhook 수신",
        kofi_type=kofi_type,
        email=email[:16] if email else "",
        amount=amount,
    )

    tokens_to_add = _resolve_token_amount(kofi_type, amount)

    if tokens_to_add <= 0:
        logger.info_ctx("Ko-fi Webhook: 토큰 적립 대상 아님", kofi_type=kofi_type)
        return {"status": "ok", "tokens_added": 0}

    token_service: TokenService = get_token_service()

    user_id = await _find_user_by_email(email)
    if not user_id:
        logger.warning(
            "Ko-fi Webhook: 매칭되는 사용자 없음",
            extra={"email_prefix": email[:8] if email else ""},
        )
        # 200 OK를 반환하여 Webhook 재시도를 방지 (사용자 없음은 영구적 오류일 가능성 높음)
        return {"status": "ok", "tokens_added": 0, "note": "사용자 미매칭"}

    token_type_map = {
        "Donation": "kofi_donation",
        "Subscription": "kofi_subscription",
        "Shop Order": "kofi_purchase",
    }

    await token_service.add_tokens(
        user_id=user_id,
        amount=tokens_to_add,
        token_type=token_type_map.get(kofi_type, "kofi_other"),
        description=f"Ko-fi {kofi_type} by {from_name}",
        reference_id=f"kofi_{kofi_txn_id}" if kofi_txn_id else None,
    )

    logger.info_ctx(
        "Ko-fi 토큰 적립 완료",
        user_id=user_id,
        tokens_added=tokens_to_add,
        kofi_type=kofi_type,
    )

    return {
        "status": "ok",
        "tokens_added": tokens_to_add,
    }


async def _find_user_by_email(email: str) -> str | None:
    """이메일로 Supabase 사용자를 검색합니다.

    보안을 위해 RPC 함수 `get_user_id_by_email`을 사용합니다.

    Args:
        email: Ko-fi에서 전달된 사용자 이메일.

    Returns:
        str | None: 사용자 UUID 또는 None.
    """
    if not email:
        return None

    from src.services.supabase_service import SupabaseService

    try:
        supa = SupabaseService()

        # RPC 호출로 변경 (O(1) 조회)
        response = supa.client.rpc("get_user_id_by_email", {"p_email": email}).execute()

        return response.data
    except Exception as e:
        logger.error(f"사용자 이메일 검색 실패: {e}")
        return None
