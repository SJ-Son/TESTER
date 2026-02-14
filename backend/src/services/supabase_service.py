from datetime import datetime, timedelta, timezone
from typing import Optional

from postgrest.exceptions import APIError
from src.config.settings import settings
from src.exceptions import ConfigurationError
from src.services.cache_service import CacheService
from src.utils.logger import get_logger
from starlette.concurrency import run_in_threadpool
from supabase import Client, create_client

logger = get_logger(__name__)


class SupabaseService:
    """Supabase 클라이언트 관리 서비스 (Singleton).

    애플리케이션 전역에서 단일 Supabase 클라이언트 인스턴스를 공유하며,
    주간 쿼터 확인 시 Redis 캐싱을 통해 성능을 최적화합니다.
    """

    _instance: Optional["SupabaseService"] = None
    _client: Optional[Client] = None
    _cache: Optional[CacheService] = None

    def __new__(cls) -> "SupabaseService":
        """Singleton 인스턴스를 반환합니다."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Supabase 데이터베이스 클라이언트 래퍼를 초기화합니다.

        이미 초기화된 경우(Singleton) 재실행하지 않습니다.
        """
        # Singleton 패턴: 이미 초기화된 경우 스킵
        if self._client is not None:
            return

        # 필수 설정 검증
        if not settings.SUPABASE_URL:
            raise ConfigurationError(
                "Supabase URL이 설정되지 않았습니다. 환경 변수 SUPABASE_URL을 확인해주세요.",
                missing_keys=["SUPABASE_URL"],
            )

        if not settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value():
            raise ConfigurationError(
                "Supabase Service Role Key가 설정되지 않았습니다. 환경 변수 SUPABASE_SERVICE_ROLE_KEY를 확인해주세요.",
                missing_keys=["SUPABASE_SERVICE_ROLE_KEY"],
            )

        try:
            self._client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value()
            )
            self._cache = CacheService()
            logger.info("✅ Supabase 클라이언트 및 캐시 서비스 초기화 성공")
        except Exception as e:
            raise ConfigurationError(
                f"Supabase 클라이언트 생성 실패: {e}",
                missing_keys=["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
            ) from e

    @property
    def client(self) -> Client:
        """초기화된 Supabase 클라이언트를 반환합니다."""
        if not self._client:
            raise RuntimeError("Supabase client is not initialized")
        return self._client

    @property
    def cache(self) -> CacheService:
        """초기화된 Cache 서비스를 반환합니다."""
        if not self._cache:
            raise RuntimeError("Cache service is not initialized")
        return self._cache

    def get_connection_status(self) -> dict:
        """상세 연결 상태 반환"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value():
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

    def _get_week_start(self) -> datetime:
        """현재 주(월요일 시작)의 시작 시각을 반환합니다 (UTC)."""
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=now.weekday())
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    def _get_quota_cache_key(self, user_id: str) -> str:
        """사용자별 주간 쿼터 캐시 키를 생성합니다.

        키 형식: quota:weekly:{user_id}:{start_of_week_date}
        예: quota:weekly:12345:2024-05-20
        """
        start_date = self._get_week_start().date().isoformat()
        return f"quota:weekly:{user_id}:{start_date}"

    def _fetch_weekly_quota_from_db(self, user_id: str) -> int:
        """DB에서 사용자의 이번 주 생성 횟수를 직접 조회합니다 (동기).

        이번 주 월요일부터 현재까지의 'generation_history' 테이블 레코드 수를 카운트합니다.

        Args:
            user_id: 사용자 ID.

        Returns:
            이번 주 생성 횟수.

        Raises:
            Exception: 데이터베이스 쿼리 실패 시.
        """
        try:
            start_of_week = self._get_week_start()

            # count='exact', head=True로 실제 데이터는 가져오지 않고 개수만 확인
            response = (
                self.client.table("generation_history")
                .select("id", count="exact", head=True)
                .eq("user_id", user_id)
                .gte("created_at", start_of_week.isoformat())
                .execute()
            )
            return response.count if response.count is not None else 0

        except APIError as e:
            logger.error(f"주간 쿼터 확인 중 API 오류: {e.message}")
            raise
        except Exception as e:
            logger.error(f"주간 쿼터 확인 실패: {e}")
            raise

    async def get_weekly_quota(self, user_id: str) -> int:
        """사용자의 주간 쿼터 사용량을 조회합니다 (비동기, 캐싱 적용).

        Redis 캐시를 먼저 확인하고, 없으면 DB에서 조회 후 캐싱합니다.
        캐시 TTL은 1시간으로 설정되며, 주(Week)가 바뀌면 키가 변경되어 자동 초기화됩니다.

        Args:
            user_id: 사용자 ID.

        Returns:
            주간 생성 횟수.
        """
        cache_key = self._get_quota_cache_key(user_id)

        # 1. 캐시 확인
        cached_count = await self.cache.get(cache_key)
        if cached_count is not None:
            return int(cached_count)

        # 2. DB 조회 (동기 함수를 스레드풀에서 실행)
        count = await run_in_threadpool(self._fetch_weekly_quota_from_db, user_id)

        # 3. 캐시 저장 (TTL: 1시간 = 3600초)
        await self.cache.set(cache_key, str(count), ttl=3600)

        return count

    async def increment_quota_cache(self, user_id: str) -> None:
        """캐시된 주간 쿼터 사용량을 1 증가시킵니다 (Atomic, Safe).

        생성 성공 시 호출되어 캐시 데이터의 정합성을 유지합니다.
        캐시 키가 존재하는 경우에만 증가시킵니다.
        키가 만료된 경우 아무 작업도 하지 않아, 다음 조회 시 DB에서 최신 값을 가져오게 합니다.

        Args:
            user_id: 사용자 ID.
        """
        cache_key = self._get_quota_cache_key(user_id)

        try:
            # 키 존재 여부 확인 후 증가 (Race Condition 최소화를 위해 Lua 스크립트 사용 가능하지만,
            # 여기서는 단순히 존재 여부만 체크하고 진행하거나,
            # Redis INCR의 특성(없으면 생성)을 피하기 위해 exists 체크 후 진행)
            # 가장 안전한 방법: 캐시를 삭제하여 다음 요청 시 강제 갱신
            # 또는 exists -> incr (약간의 race condition 존재하나 허용 가능 범위)

            # 여기서는 캐시 삭제 전략을 선택: 가장 안전하고 구현이 간단함.
            # 하지만 빈번한 삭제는 캐시 효율을 떨어뜨리므로,
            # "키가 있으면 증가, 없으면 무시"가 베스트.
            # python redis client의 incr은 키가 없으면 생성해버림.

            lua_script = """
            if redis.call("EXISTS", KEYS[1]) == 1 then
                return redis.call("INCR", KEYS[1])
            else
                return nil
            end
            """
            await self.cache.redis_client.eval(lua_script, 1, cache_key)

        except Exception as e:
            logger.warning(f"쿼터 캐시 증가 실패 (DB 데이터는 안전함): {e}")
