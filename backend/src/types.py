"""공유 타입 정의 및 불변 데이터 구조.

이 모듈은 도메인 개념을 명확히 표현하는 커스텀 타입과 불변 데이터 구조를 정의합니다.
타입 안전성을 강화하고 코드의 의도를 명확히 합니다.
"""

from dataclasses import dataclass
from typing import Literal, NewType, TypedDict

# === 도메인 타입 정의 ===


class AuthenticatedUser(TypedDict):
    """Supabase JWT 검증으로부터 반환된 인증된 사용자 데이터.

    Attributes:
        id: 사용자 고유 식별자 (UUID를 문자열로 표현)
        email: 사용자 이메일 주소 (선택적)
    """

    id: str
    email: str | None


UserId = NewType("UserId", str)
"""사용자 식별자 타입."""

EncryptedData = NewType("EncryptedData", str)
"""암호화된 데이터 타입."""

CacheKey = NewType("CacheKey", str)
"""캐시 키 타입."""

# === 리터럴 타입 정의 ===

LanguageCode = Literal["python", "javascript", "java"]
"""지원되는 프로그래밍 언어 코드."""

ModelName = Literal[
    "gemini-3-flash-preview",
    "gemini-2-flash-preview",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
"""사용 가능한 AI 모델 이름."""

CacheStrategyType = Literal["gemini", "history", "validation"]
"""캐시 전략 타입."""


# === 불변 데이터 구조 ===


@dataclass(frozen=True)
class ValidationResult:
    """코드 검증 결과를 나타내는 불변 데이터 구조.

    Attributes:
        is_valid: 검증 성공 여부.
        error_message: 검증 실패 시 에러 메시지 (성공 시 빈 문자열).
    """

    is_valid: bool
    error_message: str = ""

    @property
    def success(self) -> bool:
        """검증 성공 여부를 반환하는 헬퍼 속성."""
        return self.is_valid

    @property
    def failed(self) -> bool:
        """검증 실패 여부를 반환하는 헬퍼 속성."""
        return not self.is_valid


@dataclass(frozen=True)
class CacheMetadata:
    """캐시 메타데이터를 나타내는 불변 데이터 구조.

    Attributes:
        key: 캐시 키.
        ttl: 캐시 만료 시간(초).
    """

    key: CacheKey
    ttl: int

    def __post_init__(self) -> None:
        """TTL 유효성 검증."""
        if self.ttl <= 0:
            raise ValueError(f"TTL은 양수여야 합니다: {self.ttl}")
