"""TokenService 단위 테스트.

토큰 조회, 차감, 적립, 환불, 일일 보너스 로직을 테스트합니다.
모든 외부 의존성(Supabase)은 Mock 처리합니다.
"""

from unittest.mock import MagicMock

import pytest
from src.config.constants import TokenConstants
from src.exceptions import (
    DuplicateTransactionError,
    InsufficientTokensError,
)
from src.services.token_service import TokenService


@pytest.fixture
def mock_supabase_service():
    """SupabaseService Mock을 생성합니다."""
    service = MagicMock()
    service.client = MagicMock()
    return service


@pytest.fixture
def token_service(mock_supabase_service):
    """테스트용 TokenService 인스턴스를 생성합니다."""
    return TokenService(supabase_service=mock_supabase_service)


# === 토큰 차감 테스트 ===


@pytest.mark.asyncio
async def test_deduct_tokens_success(token_service, mock_supabase_service):
    """토큰 차감 성공 시 올바른 결과를 반환해야 함."""
    mock_response = MagicMock()
    mock_response.data = {"success": True, "deducted": 10, "current_balance": 40}
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_response

    result = await token_service.deduct_tokens(user_id="user_123", amount=10)

    assert result.success is True
    assert result.deducted == 10
    assert result.current_balance == 40
    mock_supabase_service.client.rpc.assert_called_once_with(
        "deduct_tokens",
        {"p_user_id": "user_123", "p_amount": 10},
    )


@pytest.mark.asyncio
async def test_deduct_tokens_insufficient(token_service, mock_supabase_service):
    """토큰 부족 시 InsufficientTokensError를 발생시켜야 함."""
    mock_response = MagicMock()
    mock_response.data = {
        "success": False,
        "error": "INSUFFICIENT_TOKENS",
        "current_balance": 5,
        "required": 10,
    }
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_response

    with pytest.raises(InsufficientTokensError) as exc_info:
        await token_service.deduct_tokens(user_id="user_123", amount=10)

    assert exc_info.value.current == 5
    assert exc_info.value.required == 10


@pytest.mark.asyncio
async def test_deduct_tokens_user_not_found(token_service, mock_supabase_service):
    """존재하지 않는 사용자에 대해 실패 결과를 반환해야 함."""
    mock_response = MagicMock()
    mock_response.data = {
        "success": False,
        "error": "USER_NOT_FOUND",
        "current_balance": 0,
    }
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_response

    result = await token_service.deduct_tokens(user_id="nonexistent", amount=10)

    assert result.success is False
    assert result.error == "USER_NOT_FOUND"


# === 토큰 환불 테스트 ===


@pytest.mark.asyncio
async def test_refund_tokens_success(token_service, mock_supabase_service):
    """토큰 환불 성공 시 True를 반환해야 함."""
    mock_response = MagicMock()
    mock_response.data = {"success": True, "refunded": 10, "current_balance": 50}
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_response

    result = await token_service.refund_tokens(user_id="user_123", amount=10)

    assert result is True


@pytest.mark.asyncio
async def test_refund_tokens_failure(token_service, mock_supabase_service):
    """환불 RPC 실패 시 False를 반환해야 함."""
    mock_supabase_service.client.rpc.side_effect = Exception("DB Error")

    result = await token_service.refund_tokens(user_id="user_123", amount=10)

    assert result is False


# === 토큰 적립 테스트 ===


@pytest.mark.asyncio
async def test_add_tokens_success(token_service, mock_supabase_service):
    """토큰 적립 성공 시 올바른 결과를 반환해야 함."""
    mock_response = MagicMock()
    mock_response.data = {"success": True, "added": 5, "current_balance": 55}
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_response

    result = await token_service.add_tokens(
        user_id="user_123",
        amount=5,
        token_type="ad_reward",
        description="광고 시청 보상",
        reference_id="txn_abc123",
    )

    assert result["success"] is True
    assert result["added"] == 5


@pytest.mark.asyncio
async def test_add_tokens_duplicate_transaction(token_service, mock_supabase_service):
    """중복 트랜잭션 시 DuplicateTransactionError를 발생시켜야 함."""
    mock_response = MagicMock()
    mock_response.data = {"success": False, "error": "DUPLICATE_TRANSACTION"}
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_response

    with pytest.raises(DuplicateTransactionError):
        await token_service.add_tokens(
            user_id="user_123",
            amount=5,
            token_type="ad_reward",
            reference_id="txn_abc123",
        )


# === 토큰 정보 조회 테스트 ===


@pytest.mark.asyncio
async def test_get_token_info_existing_user(token_service, mock_supabase_service):
    """기존 사용자의 토큰 정보를 정상 조회해야 함."""
    from datetime import date

    # Mock: 일일 보너스 RPC (이미 수령)
    mock_bonus_response = MagicMock()
    mock_bonus_response.data = {
        "success": False,
        "already_claimed": True,
        "current_balance": 40,
    }
    mock_supabase_service.client.rpc.return_value.execute.return_value = mock_bonus_response

    # Mock: 토큰 데이터 조회
    mock_select_response = MagicMock()
    mock_select_response.data = {
        "balance": 40,
        "daily_ad_count": 2,
        "daily_ad_reset_at": str(date.today()),
        "last_daily_bonus_at": str(date.today()),
    }
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_select_response

    result = await token_service.get_token_info("user_123")

    assert result.current_tokens == 40
    assert result.daily_bonus_claimed is True
    assert result.cost_per_generation == TokenConstants.COST_PER_GENERATION


@pytest.mark.asyncio
async def test_get_token_info_new_user(token_service, mock_supabase_service):
    """신규 사용자에게 웰컴 보너스와 일일 보너스를 모두 지급해야 함."""
    from datetime import date

    # 1. Mock RPC calls
    mock_init_response = MagicMock()
    mock_init_response.data = {"success": True, "created": True, "balance": 50}

    mock_bonus_response = MagicMock()
    mock_bonus_response.data = {"success": True, "added": 30, "current_balance": 80}

    def rpc_side_effect(func_name, params):
        if func_name == "initialize_user_wallet":
            return MagicMock(execute=MagicMock(return_value=mock_init_response))
        if func_name == "claim_daily_bonus":
            return MagicMock(execute=MagicMock(return_value=mock_bonus_response))
        return MagicMock()

    mock_supabase_service.client.rpc.side_effect = rpc_side_effect

    # 2. Mock: Token Data Fetch
    mock_select_response = MagicMock()
    mock_select_response.data = {
        "balance": 80,  # Welcome(50) + Daily(30)
        "daily_ad_count": 0,
        "last_daily_bonus_at": str(date.today()),
    }
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_select_response

    result = await token_service.get_token_info("new_user_123")

    assert result.current_tokens == 80  # 50 + 30


# === 에러 메시지 검증 테스트 ===


def test_insufficient_tokens_error_attributes():
    """InsufficientTokensError 예외의 속성이 올바르게 설정되어야 함."""
    error = InsufficientTokensError(current=5, required=10)

    assert error.current == 5
    assert error.required == 10
    assert error.code == "INSUFFICIENT_TOKENS"
    assert "토큰이 부족합니다" in error.message


def test_duplicate_transaction_error_truncation():
    """DuplicateTransactionError가 transaction_id를 16자로 절단해야 함."""
    long_id = "a" * 100
    error = DuplicateTransactionError(long_id)

    assert len(error.context["transaction_id"]) == 16
