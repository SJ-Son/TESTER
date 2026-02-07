import hashlib
import logging
from enum import Enum
from typing import Any, Optional

import redis
from src.config.settings import settings


class CacheStrategy(str, Enum):
    """Cache TTL strategies for different data types"""

    GEMINI_RESPONSE = "gemini"  # 2 hours
    USER_HISTORY = "history"  # 30 minutes
    VALIDATION_RULE = "validation"  # 24 hours

    @property
    def ttl(self) -> int:
        """Get TTL in seconds for this strategy"""
        ttl_map = {
            self.GEMINI_RESPONSE: 7200,
            self.USER_HISTORY: 1800,
            self.VALIDATION_RULE: 86400,
        }
        return ttl_map.get(self, 3600)  # Default 1 hour


logger = logging.getLogger(__name__)


class CacheService:
    """Redis 기반 캐싱 서비스"""

    def __init__(self, redis_url: str = settings.REDIS_URL, ttl: int = 3600):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl  # 기본 1시간
        self._check_connection()

    def _check_connection(self):
        try:
            # Mask the password for logging
            masked_url = self.redis_client.connection_pool.connection_kwargs.get("host", "unknown")
            port = self.redis_client.connection_pool.connection_kwargs.get("port", "unknown")
            logger.info(f"Attempting to connect to Redis at {masked_url}:{port}")

            self.redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except redis.ConnectionError as e:
            logger.warning(f"Failed to connect to Redis at {masked_url}:{port}. Error: {e}")
            logger.warning("Caching might be disabled.")

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

    def generate_key(
        self,
        *args: Any,
        strategy: CacheStrategy = CacheStrategy.GEMINI_RESPONSE,
    ) -> tuple[str, int]:
        """캐시 키 생성 with strategy-based TTL

        Returns:
            tuple: (cache_key, ttl_seconds)
        """
        prefix = strategy.value
        key_input = f"{prefix}:" + ":".join(str(arg) for arg in args)
        key = hashlib.sha256(key_input.encode()).hexdigest()
        return key, strategy.ttl

    def clear(self, pattern: str = "*"):
        """패턴에 맞는 키 삭제 (주의)"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except redis.RedisError as e:
            logger.error(f"Redis clear error: {e}")
