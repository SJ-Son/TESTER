"""Redis 기반 캐싱 서비스.

캐시 전략별로 TTL을 관리하며, 연결 풀링을 통해 성능을 최적화합니다.
모든 설정은 불변이며, 예외는 호출자에게 전파됩니다.
"""

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, Optional

import redis
from src.config.constants import CacheConstants
from src.config.settings import settings
from src.exceptions import CacheError
from src.types import CacheKey, CacheMetadata, CacheStrategyType
from src.utils.logger import get_logger


@dataclass(frozen=True)
class CacheStrategy:
    """캐시 전략을 나타내는 불변 데이터 구조.

    Attributes:
        name: 전략 이름 ('gemini', 'history', 'validation').
        ttl: 캐시 유지 시간 (초).
    """

    name: CacheStrategyType
    ttl: int

    @staticmethod
    def from_name(name: CacheStrategyType) -> "CacheStrategy":
        """전략 이름으로부터 CacheStrategy 인스턴스를 생성합니다.

        Args:
            name: 전략 이름.

        Returns:
            CacheStrategy: 해당 전략의 인스턴스.
        """
        ttl = CacheConstants.TTL_MAPPING.get(name, CacheConstants.DEFAULT_TTL)
        return CacheStrategy(name=name, ttl=ttl)


# Redis 클라이언트 전역 캐시 (연결 풀 재사용)
_redis_clients: dict[str, redis.Redis] = {}


class CacheService:
    """Redis 기반 캐싱 서비스.

    전략별 TTL을 적용하여 데이터를 캐싱하고 조회합니다.
    연결 실패 시 명확한 예외를 발생시킵니다.
    """

    _TTL_MAPPING: Final[Mapping[str, int]] = CacheConstants.TTL_MAPPING
    """캐시 전략별 TTL 매핑 (불변)"""

    def __init__(self, redis_url: str = settings.REDIS_URL, ttl: int = CacheConstants.DEFAULT_TTL):
        """CacheService 인스턴스를 초기화합니다.

        Args:
            redis_url: Redis 연결 URL.
            ttl: 기본 TTL (초).

        Raises:
            CacheError: Redis 연결 실패 시.
        """
        self.logger = get_logger(__name__)
        self.default_ttl: Final[int] = ttl

        global _redis_clients
        if redis_url not in _redis_clients:
            client = redis.from_url(redis_url, decode_responses=True)
            self._verify_connection(client)
            _redis_clients[redis_url] = client

        self.redis_client: Final[redis.Redis] = _redis_clients[redis_url]

    def _verify_connection(self, client: redis.Redis) -> None:
        """Redis 연결 상태를 검증합니다.

        Args:
            client: 검증할 Redis 클라이언트.

        Raises:
            CacheError: 연결 실패 시.
        """
        try:
            masked_host = client.connection_pool.connection_kwargs.get("host", "unknown")
            port = client.connection_pool.connection_kwargs.get("port", "unknown")
            self.logger.info(f"Redis 연결 시도: {masked_host}:{port}")

            client.ping()
            self.logger.info("Redis 연결 성공")
        except redis.ConnectionError as e:
            raise CacheError(
                message=f"Redis 연결 실패: {masked_host}:{port}",
                operation="connect",
            ) from e

    def get(self, key: str) -> Optional[str]:
        """캐시에서 값을 조회합니다.

        Args:
            key: 캐시 키.

        Returns:
            캐시된 값 (문자열) 또는 None (캐시 미스).

        Raises:
            CacheError: Redis 조회 실패 시.
        """
        try:
            return self.redis_client.get(key)
        except redis.RedisError as e:
            raise CacheError(
                message="캐시 조회 실패",
                operation="get",
                key=key,
            ) from e

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """캐시에 값을 저장합니다.

        Args:
            key: 캐시 키.
            value: 저장할 값.
            ttl: TTL (초), None일 경우 기본값 사용.

        Raises:
            CacheError: Redis 저장 실패 시.
        """
        effective_ttl = ttl if ttl is not None else self.default_ttl

        try:
            self.redis_client.setex(key, effective_ttl, value)
        except redis.RedisError as e:
            raise CacheError(
                message="캐시 저장 실패",
                operation="set",
                key=key,
            ) from e

    def generate_key(
        self,
        *args: str,
        strategy: CacheStrategyType = "gemini",
    ) -> CacheMetadata:
        """캐시 키와 TTL을 생성합니다.

        Args:
            *args: 키 생성에 사용할 인자들.
            strategy: 캐시 전략 ('gemini', 'history', 'validation').

        Returns:
            CacheMetadata: 생성된 캐시 키와 TTL을 포함한 메타데이터.

        Example:
            >>> service = CacheService()
            >>> metadata = service.generate_key("model", "code", strategy="gemini")
            >>> metadata.ttl
            7200
        """
        cache_strategy = CacheStrategy.from_name(strategy)
        key_input = f"{cache_strategy.name}:" + ":".join(str(arg) for arg in args)
        hashed_key = hashlib.sha256(key_input.encode()).hexdigest()

        return CacheMetadata(
            key=CacheKey(hashed_key),
            ttl=cache_strategy.ttl,
        )

    def clear(self, pattern: str = "*") -> None:
        """패턴에 맞는 캐시 키를 삭제합니다.

        주의: 프로덕션 환경에서는 신중히 사용해야 합니다.

        Args:
            pattern: 삭제할 키 패턴 (glob 스타일).

        Raises:
            CacheError: Redis 삭제 실패 시.
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except redis.RedisError as e:
            raise CacheError(
                message=f"캐시 클리어 실패: {pattern}",
                operation="clear",
            ) from e
