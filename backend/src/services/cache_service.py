import hashlib
from typing import Any, Optional

import redis

from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis기반 캐싱 서비스"""

    def __init__(self, redis_url: str = settings.REDIS_URL, ttl: int = 3600):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl  # 기본 1시간
        self._check_connection()

    def _check_connection(self):
        try:
            self.redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except redis.ConnectionError:
            logger.warning("Failed to connect to Redis. Caching might be disabled.")

    def get(self, key: str) -> Optional[str]:
        """캐시된 값 조회"""
        try:
            return self.redis_client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """캐시 저장"""
        try:
            return self.redis_client.setex(key, ttl or self.ttl, value)
        except redis.RedisError as e:
            logger.error(f"Redis set error: {e}")
            return False

    def generate_key(self, *args: Any) -> str:
        """MD5 해시 키 생성"""
        key_input = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_input.encode()).hexdigest()

    def clear(self, pattern: str = "*"):
        """패턴에 맞는 키 삭제 (주의)"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except redis.RedisError as e:
            logger.error(f"Redis clear error: {e}")
