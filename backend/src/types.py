"""공유 타입 정의 및 불변 데이터 구조.

이 모듈은 도메인 개념을 명확히 표현하는 커스텀 타입과 불변 데이터 구조를 정의합니다.
타입 안전성을 강화하고 코드의 의도를 명확히 합니다.
"""

from dataclasses import dataclass
from typing import Literal, NewType, TypedDict

from pydantic import BaseModel, Field, field_validator
from src.config.settings import settings

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


class GenerateRequest(BaseModel):
    """테스트 코드 생성 요청 모델.

    Attributes:
        input_code: 테스트를 생성할 원본 소스 코드.
        language: 프로그래밍 언어 (python, java, javascript 등).
        model: 사용할 AI 모델 (기본값 설정됨).
        turnstile_token: Cloudflare Turnstile 검증 토큰.
        is_regenerate: 재생성 요청 여부 (기본값: False).
    """

    input_code: str
    language: str
    model: str = settings.DEFAULT_GEMINI_MODEL
    turnstile_token: str = Field(..., description="Cloudflare Turnstile 검증 토큰")
    is_regenerate: bool = False

    @field_validator("input_code")
    @classmethod
    def validate_code_length(cls, v: str) -> str:
        """코드 길이 검증 (10자 이상, 10,000자 이하)."""
        if len(v) > 10000:
            raise ValueError("코드가 너무 깁니다 (최대 10,000자)")
        if len(v.strip()) < 10:
            raise ValueError("코드가 너무 짧습니다 (최소 10자)")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """지원 가능한 언어인지 검증."""
        supported = ["python", "java", "typescript", "javascript"]
        if v.lower() not in supported:
            raise ValueError(f"지원하지 않는 언어입니다: {v}")
        return v.lower()


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
