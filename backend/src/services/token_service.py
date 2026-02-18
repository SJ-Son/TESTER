"""토큰 관리 서비스.

사용자 토큰의 조회, 적립, 차감을 담당합니다.
모든 토큰 변동은 Supabase RPC를 통해 Atomic하게 처리됩니다.
"""

from src.config.constants import TokenConstants
from src.exceptions import (
    DuplicateTransactionError,
    InsufficientTokensError,
)
from src.services.supabase_service import SupabaseService
from src.types import TokenDeductResult, TokenInfo
from src.utils.logger import get_logger
from starlette.concurrency import run_in_threadpool

logger = get_logger(__name__)


class TokenService:
    """토큰 관련 비즈니스 로직을 처리하는 서비스.

    Supabase RPC 함수를 호출하여 토큰 잔액의 원자적(Atomic) 변경을 보장합니다.
    Redis 캐싱은 조회 성능 최적화를 위해 선택적으로 적용됩니다.

    Attributes:
        _supabase: Supabase 서비스 인스턴스.
    """

    def __init__(self, supabase_service: SupabaseService) -> None:
        """TokenService를 초기화합니다.

        Args:
            supabase_service: Supabase 서비스 의존성.
        """
        self._supabase = supabase_service

    async def get_token_info(self, user_id: str) -> TokenInfo:
        """사용자의 토큰 상태를 조회합니다.

        user_tokens 레코드가 없으면 자동으로 생성(웰컴 보너스 지급)합니다.
        일일 보너스 미수령 시 자동으로 지급 처리합니다.

        Args:
            user_id: 사용자 ID.

        Returns:
            TokenInfo: 현재 토큰 상태 정보.
        """
        # 1. 지갑 초기화 (신규 사용자 Atomic Welcome Bonus 지급)
        await self._initialize_wallet(user_id)

        # 2. 일일 보너스 처리 (Atomic Check & Add)
        bonus_result = await self._claim_daily_bonus_internal(user_id)

        # 3. 최종 상태 조회
        token_data = await run_in_threadpool(self._fetch_user_tokens, user_id)

        daily_bonus_claimed = bonus_result.get("already_claimed", False) or bonus_result.get(
            "success", False
        )

        return TokenInfo(
            current_tokens=token_data.get("balance", 0) if token_data else 0,
            daily_bonus_claimed=daily_bonus_claimed,
            cost_per_generation=TokenConstants.COST_PER_GENERATION,
        )

    async def deduct_tokens(self, user_id: str, amount: int) -> TokenDeductResult:
        """테스트 생성 시 토큰을 차감합니다.

        Supabase RPC `deduct_tokens`를 호출하여 Atomic하게 처리합니다.
        잔액 부족 시 InsufficientTokensError를 발생시킵니다.

        Args:
            user_id: 사용자 ID.
            amount: 차감할 토큰 수.

        Returns:
            TokenDeductResult: 차감 결과.

        Raises:
            InsufficientTokensError: 토큰 잔액 부족 시.
        """
        try:
            result = await run_in_threadpool(self._call_deduct_rpc, user_id, amount)

            if not result.get("success", False):
                error_code = result.get("error", "")
                current_balance = result.get("current_balance", 0)

                if error_code == "INSUFFICIENT_TOKENS":
                    raise InsufficientTokensError(
                        current=current_balance,
                        required=amount,
                    )

                logger.error(f"토큰 차감 실패: user_id={user_id}, error={error_code}")
                return TokenDeductResult(
                    success=False,
                    current_balance=current_balance,
                    error=error_code,
                )

            logger.info_ctx(
                "토큰 차감 완료",
                user_id=user_id,
                deducted=amount,
                remaining=result.get("current_balance", 0),
            )

            return TokenDeductResult(
                success=True,
                deducted=amount,
                current_balance=result.get("current_balance", 0),
            )
        except InsufficientTokensError:
            raise
        except Exception as e:
            logger.error(f"토큰 차감 중 예외 발생: {e}")
            raise

    async def refund_tokens(self, user_id: str, amount: int) -> bool:
        """생성 실패 시 토큰을 환불합니다.

        Args:
            user_id: 사용자 ID.
            amount: 환불할 토큰 수.

        Returns:
            bool: 환불 성공 여부.
        """
        try:
            result = await run_in_threadpool(self._call_refund_rpc, user_id, amount)
            success = result.get("success", False)
            if success:
                logger.info_ctx(
                    "토큰 환불 완료",
                    user_id=user_id,
                    refunded=amount,
                )
            return success
        except Exception as e:
            logger.error(f"토큰 환불 실패: {e}")
            return False

    async def add_tokens(
        self,
        user_id: str,
        amount: int,
        token_type: str,
        description: str | None = None,
        reference_id: str | None = None,
    ) -> dict:
        """토큰을 적립합니다.

        Args:
            user_id: 사용자 ID.
            amount: 적립할 토큰 수.
            token_type: 적립 유형 (daily_bonus, ad_reward, welcome, admin).
            description: 설명 (선택).
            reference_id: 외부 참조 ID (광고 Transaction ID 등).

        Returns:
            dict: RPC 결과 (success, added, current_balance).

        Raises:
            DuplicateTransactionError: 중복 보상 요청 시.
        """
        try:
            result = await run_in_threadpool(
                self._call_add_rpc,
                user_id,
                amount,
                token_type,
                description,
                reference_id,
            )

            if not result.get("success", False):
                error_code = result.get("error", "")
                if error_code == "DUPLICATE_TRANSACTION" and reference_id:
                    raise DuplicateTransactionError(reference_id)
                logger.error(f"토큰 적립 실패: {error_code}")
                return result

            logger.info_ctx(
                "토큰 적립 완료",
                user_id=user_id,
                amount=amount,
                type=token_type,
            )
            return result
        except DuplicateTransactionError:
            raise
        except Exception as e:
            logger.error(f"토큰 적립 중 예외 발생: {e}")
            raise

    # === Private: Supabase RPC Wrappers ===

    def _fetch_user_tokens(self, user_id: str) -> dict | None:
        """user_tokens 테이블에서 사용자 토큰 데이터를 조회합니다 (동기).

        Args:
            user_id: 사용자 ID.

        Returns:
            dict | None: 토큰 데이터 또는 None.
        """
        try:
            response = (
                self._supabase.client.table("user_tokens")
                .select("*")
                .eq("user_id", user_id)
                .maybe_single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"토큰 데이터 조회 실패: {e}")
            return None

    def _call_deduct_rpc(self, user_id: str, amount: int) -> dict:
        """deduct_tokens RPC를 호출합니다 (동기).

        Args:
            user_id: 사용자 ID.
            amount: 차감할 토큰 수.

        Returns:
            dict: RPC 결과.
        """
        response = self._supabase.client.rpc(
            "deduct_tokens",
            {"p_user_id": user_id, "p_amount": amount},
        ).execute()
        return response.data

    def _call_add_rpc(
        self,
        user_id: str,
        amount: int,
        token_type: str,
        description: str | None,
        reference_id: str | None,
    ) -> dict:
        """add_tokens RPC를 호출합니다 (동기).

        Args:
            user_id: 사용자 ID.
            amount: 적립할 토큰 수.
            token_type: 적립 유형.
            description: 설명.
            reference_id: 외부 참조 ID.

        Returns:
            dict: RPC 결과.
        """
        response = self._supabase.client.rpc(
            "add_tokens",
            {
                "p_user_id": user_id,
                "p_amount": amount,
                "p_type": token_type,
                "p_description": description,
                "p_reference_id": reference_id,
            },
        ).execute()
        return response.data

    def _call_refund_rpc(self, user_id: str, amount: int) -> dict:
        """refund_tokens RPC를 호출합니다 (동기).

        Args:
            user_id: 사용자 ID.
            amount: 환불할 토큰 수.

        Returns:
            dict: RPC 결과.
        """
        response = self._supabase.client.rpc(
            "refund_tokens",
            {"p_user_id": user_id, "p_amount": amount},
        ).execute()
        return response.data

    def _call_daily_bonus_rpc(self, user_id: str) -> dict:
        """claim_daily_bonus RPC를 호출합니다 (동기).

        Args:
            user_id: 사용자 ID.

        Returns:
            dict: RPC 결과.
        """
        response = self._supabase.client.rpc(
            "claim_daily_bonus",
            {
                "p_user_id": user_id,
                "p_bonus_amount": TokenConstants.DAILY_BONUS,
            },
        ).execute()
        return response.data

    async def _claim_daily_bonus_internal(self, user_id: str) -> dict:
        """일일 보너스를 내부적으로 처리합니다 (비동기).

        Args:
            user_id: 사용자 ID.

        Returns:
            dict: RPC 결과.
        """
        try:
            result = await run_in_threadpool(self._call_daily_bonus_rpc, user_id)
            if result.get("success", False):
                logger.info_ctx(
                    "일일 보너스 지급 완료",
                    user_id=user_id,
                    amount=TokenConstants.DAILY_BONUS,
                )
            return result
        except Exception as e:
            logger.error(f"일일 보너스 처리 실패: {e}")
            return {"success": False, "error": str(e)}

    async def _initialize_wallet(self, user_id: str) -> None:
        """사용자 지갑을 초기화합니다 (신규 사용자 Welcome Bonus).

        Args:
            user_id: 사용자 ID.
        """
        try:
            await run_in_threadpool(
                self._call_initialize_wallet_rpc,
                user_id,
                TokenConstants.WELCOME_BONUS,
            )
        except Exception as e:
            logger.error(f"지갑 초기화 실패: {e}")

    def _call_initialize_wallet_rpc(self, user_id: str, amount: int) -> dict:
        """initialize_user_wallet RPC를 호출합니다 (동기).

        Args:
            user_id: 사용자 ID.
            amount: 웰컴 보너스 금액.

        Returns:
            dict: RPC 결과.
        """
        response = self._supabase.client.rpc(
            "initialize_user_wallet",
            {
                "p_user_id": user_id,
                "p_default_amount": amount,
                "p_description": "신규 가입 웰컴 보너스",
            },
        ).execute()
        return response.data
