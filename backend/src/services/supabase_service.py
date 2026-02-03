from supabase import Client, create_client

from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseService:
    """Supabase 클라이언트 관리 서비스"""

    _client: Client = None

    def __init__(self):
        self._initialize_client()

    def _initialize_client(self):
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

    def is_connected(self) -> bool:
        """Supabase 연결 상태 확인 (실제 쿼리 수행)"""
        if not self._client:
            return False
        try:
            # 간단한 쿼리로 연결 테스트 (test_logs 테이블 존재 여부 확인)
            # head=True를 사용하여 데이터 전송 최소화
            self._client.table("test_logs").select("id", count="exact", head=True).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection check failed: {e}")
            return False
