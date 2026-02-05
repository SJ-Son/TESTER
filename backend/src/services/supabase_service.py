from src.config.settings import settings
from src.utils.logger import get_logger
from supabase import Client, create_client

logger = get_logger(__name__)


class SupabaseService:
    """Supabase 클라이언트 관리 서비스 (Singleton)"""

    _instance = None
    _client: Client = None

    def __new__(cls):
        """Singleton 패턴: 인스턴스가 하나만 생성되도록 보장"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """클라이언트 초기화 (한 번만 실행)"""
        if self._client is not None:
            return  # 이미 초기화됨

        try:
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_KEY

            if not url or not key:
                logger.warning("Supabase credentials not found. DB features will be disabled.")
                return

            self._client = create_client(url, key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self._client = None

    @property
    def client(self) -> Client:
        if not self._client:
            raise RuntimeError("Supabase client is not initialized")
        return self._client

    def get_connection_status(self) -> dict:
        """상세 연결 상태 반환"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
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

    def get_history(self, user_id: str, limit: int = 50):
        """사용자 기록 조회"""
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
