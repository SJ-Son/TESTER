"""Redis 기반 캐싱 서비스.

캐시 전략별로 TTL을 관리하며, 연결 풀링을 통해 성능을 최적화합니다.
모든 설정은 불변이며, 예외는 호출자에게 전파됩니다.
"""

import hashlib
import socket
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
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


class RedisConnectionManager:
    """Redis 연결을 관리하는 싱글톤 클래스.

    Redis 클라이언트 인스턴스를 하나만 생성하고 공유하여 리소스 효율성을 높입니다.
    """

    _instance: Optional["RedisConnectionManager"] = None
    _client: Optional[redis.Redis] = None

    @classmethod
    def get_instance(cls) -> "RedisConnectionManager":
        """RedisConnectionManager의 싱글톤 인스턴스를 반환합니다.

        Returns:
            RedisConnectionManager 인스턴스.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_client(self, redis_url: str) -> redis.Redis:
        """Redis 클라이언트(Connection Pool)를 반환합니다.

        Args:
            redis_url: Redis 연결 URL.

        Returns:
            Redis 클라이언트 객체.
        """
        if self._client is None:
            # 플랫폼별 Keepalive 옵션 설정
            keepalive_options = {}
            # Linux: TCP_KEEPIDLE, macOS: TCP_KEEPALIVE
            if hasattr(socket, "TCP_KEEPIDLE"):
                keepalive_options[socket.TCP_KEEPIDLE] = 60
            elif hasattr(socket, "TCP_KEEPALIVE"):
                keepalive_options[socket.TCP_KEEPALIVE] = 60

            if hasattr(socket, "TCP_KEEPINTVL"):
                keepalive_options[socket.TCP_KEEPINTVL] = 10

            if hasattr(socket, "TCP_KEEPCNT"):
                keepalive_options[socket.TCP_KEEPCNT] = 3

            self._client = redis.from_url(
                redis_url,
                decode_responses=True,
                max_connections=10,  # 연결 풀 크기 제한
                socket_keepalive=True,  # TCP Keepalive 활성화
                socket_keepalive_options=keepalive_options if keepalive_options else None,
            )
        return self._client

    def close(self) -> None:
        """Redis 연결을 종료하고 리소스를 해제합니다."""
        if self._client:
            self._client.close()
            self._client = None


# LRU 캐시를 사용한 키 해싱 (성능 최적화)
@lru_cache(maxsize=1000)
def _compute_cache_key(key_input: str) -> str:
    """캐시 키 해싱 함수 (LRU 캐시 적용).

    동일한 입력에 대해 반복적인 SHA256 연산을 피하기 위해
    최근 1000개의 결과를 메모리에 캐싱합니다.

    Args:
        key_input: 해시할 입력 문자열.

    Returns:
        str: SHA256 해시값 (hexdigest).
    """
    return hashlib.sha256(key_input.encode()).hexdigest()


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

        manager = RedisConnectionManager.get_instance()
        self.redis_client: Final[redis.Redis] = manager.get_client(redis_url)

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

        # LRU 캐싱된 해시 함수 사용
        hashed_key = _compute_cache_key(key_input)

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
