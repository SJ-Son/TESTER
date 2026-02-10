from src.config.settings import settings
from src.exceptions import ConfigurationError
from src.utils.logger import get_logger
from supabase import Client, create_client

logger = get_logger(__name__)


class SupabaseService:
    """Supabase 클라이언트 관리 서비스 (Singleton)"""

    _instance = None
    _client: Client = None

    def __init__(self):
        """Supabase 데이터베이스 클라이언트 래퍼."""
        # Singleton 패턴: 이미 초기화된 경우 스킵
        if self._client is not None:
            return

        # 필수 설정 검증
        if not settings.SUPABASE_URL:
            raise ConfigurationError(
                "Supabase URL이 설정되지 않았습니다. 환경 변수 SUPABASE_URL을 확인해주세요.",
                missing_keys=["SUPABASE_URL"],
            )

        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ConfigurationError(
                "Supabase Service Role Key가 설정되지 않았습니다. 환경 변수 SUPABASE_SERVICE_ROLE_KEY를 확인해주세요.",
                missing_keys=["SUPABASE_SERVICE_ROLE_KEY"],
            )

        try:
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            logger.info("✅ Supabase 클라이언트 초기화 성공")
        except Exception as e:
            raise ConfigurationError(
                f"Supabase 클라이언트 생성 실패: {e}",
                missing_keys=["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
            ) from e

    @property
    def client(self) -> Client:
        if not self._client:
            raise RuntimeError("Supabase client is not initialized")
        return self._client

    def get_connection_status(self) -> dict:
        """상세 연결 상태 반환"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            return {"connected": False, "reason": "Environment variables missing"}

        if not self._client:
            return {"connected": False, "reason": "Client initialization failed"}

        try:
            # 테이블 존재 확인 및 권한 테스트
            self._client.table("generation_history").select(
                "id", count="exact", head=True
            ).execute()
            return {"connected": True, "reason": "OK"}
        except Exception as e:
            error_msg = str(e)
            if 'relation "public.generation_history" does not exist' in error_msg.lower():
                return {
                    "connected": False,
                    "reason": "Table 'generation_history' not found (schema.sql not applied)",
                }
            return {"connected": False, "reason": f"Query failed: {error_msg}"}

    def is_connected(self) -> bool:
        return self.get_connection_status()["connected"]

    def save_generation(
        self, user_id: str, input_code: str, generated_code: str, language: str, model: str
    ):
        """생성 기록 저장"""
        if not self._client:
            logger.warning("Supabase client not initialized. Skipping save.")
            return None

        try:
            data = {
                "user_id": user_id,
                "input_code": input_code,
                "generated_code": generated_code,
                "language": language,
                "model": model,
            }
            response = self._client.table("generation_history").insert(data).execute()
            return response
        except Exception as e:
            logger.error(f"Failed to save generation history: {e}")
            return None

    def get_history(self, user_id: str, limit: int = 50) -> list[dict]:
        """사용자의 생성 이력을 조회합니다.

        Args:
            user_id: 사용자 ID.
            limit: 조회할 레코드 수 (기본값: 50).

        Returns:
            list[dict]: 생성 이력 리스트. 실패 시 빈 리스트 반환.
        """
        if not self._client:
            return []

        try:
            response = (
                self._client.table("generation_history")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return []
