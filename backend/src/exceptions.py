"""TESTER 애플리케이션을 위한 커스텀 예외 클래스.

계층적 예외 구조를 통해 명확한 에러 처리와 디버깅을 지원합니다.
모든 예외는 구조화된 에러 코드와 컨텍스트 정보를 포함합니다.
"""

from datetime import datetime
from typing import Any


class TesterException(Exception):
    """모든 TESTER 관련 예외의 기본 클래스.

    Attributes:
        message: 사용자 대면 에러 메시지.
        code: 구조화된 에러 코드 (예: "DB_CONNECTION_FAILED").
        context: 디버깅을 위한 추가 컨텍스트 정보.
        timestamp: 예외 발생 시각.
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.context = context or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

    def __str__(self) -> str:
        """디버깅 친화적인 문자열 표현."""
        context_str = f", context={self.context}" if self.context else ""
        return f"[{self.code}] {self.message}{context_str}"

    def to_dict(self) -> dict[str, Any]:
        """API 응답을 위한 딕셔너리 변환."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "context": self.context,
                "timestamp": self.timestamp.isoformat(),
            }
        }


# === 검증 레이어 예외 ===


class ValidationError(TesterException):
    """입력 검증 실패 시 발생하는 예외.

    사용자 입력이 유효하지 않을 때 사용합니다.
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="VALIDATION_ERROR", context=context)


class CodeValidationError(ValidationError):
    """코드 검증 실패 시 발생하는 예외.

    잘못된 문법이나 지원하지 않는 언어일 때 사용합니다.
    """

    def __init__(
        self,
        message: str,
        language: str | None = None,
        code_snippet: str | None = None,
    ) -> None:
        context = {}
        if language:
            context["language"] = language
        if code_snippet:
            context["code_preview"] = code_snippet[:100]
        super().__init__(message, context=context)


# === 인증 레이어 예외 ===


class AuthenticationError(TesterException):
    """인증 실패 시 발생하는 예외."""

    def __init__(
        self,
        message: str = "인증에 실패했습니다",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="AUTH_ERROR", context=context)


class TurnstileError(TesterException):
    """Cloudflare Turnstile 검증 실패 시 발생하는 예외."""

    def __init__(
        self,
        message: str = "봇 감지 검증에 실패했습니다",
        token_preview: str | None = None,
    ) -> None:
        context = {}
        if token_preview:
            context["token_preview"] = token_preview[:16]
        super().__init__(message, code="TURNSTILE_FAILED", context=context)


# === AI 서비스 레이어 예외 ===


class GenerationError(TesterException):
    """AI 코드 생성 실패 시 발생하는 예외."""

    def __init__(
        self,
        message: str,
        model: str | None = None,
        retry_count: int | None = None,
    ) -> None:
        context = {}
        if model:
            context["model"] = model
        if retry_count is not None:
            context["retry_attempts"] = retry_count
        super().__init__(message, code="GENERATION_ERROR", context=context)


class AIServiceUnavailableError(GenerationError):
    """AI 서비스를 사용할 수 없을 때 발생하는 예외."""

    def __init__(
        self,
        message: str = "AI 서비스를 일시적으로 사용할 수 없습니다",
        service_name: str = "Gemini",
    ) -> None:
        super().__init__(message, model=service_name)


# === 인프라 레이어 예외 ===


class InfrastructureError(TesterException):
    """인프라 관련 예외 (Redis, Supabase 등)."""

    def __init__(
        self,
        message: str,
        code: str = "INFRASTRUCTURE_ERROR",
        service: str | None = None,
    ) -> None:
        context = {"service": service} if service else {}
        super().__init__(message, code=code, context=context)


class CacheError(InfrastructureError):
    """Redis 캐시 작업 실패 시 발생하는 예외."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        key: str | None = None,
    ) -> None:
        context = {}
        if operation:
            context["operation"] = operation
        if key:
            context["cache_key"] = key[:16]
        super().__init__(message, code="CACHE_ERROR", service="Redis")
        self.context.update(context)


class DatabaseError(InfrastructureError):
    """데이터베이스 작업 실패 시 발생하는 예외."""

    def __init__(
        self,
        message: str,
        table: str | None = None,
        operation: str | None = None,
    ) -> None:
        context = {}
        if table:
            context["table"] = table
        if operation:
            context["operation"] = operation
        super().__init__(message, code="DATABASE_ERROR", service="Supabase")
        self.context.update(context)


# === 설정 레이어 예외 ===


class ConfigurationError(TesterException):
    """설정 오류 시 발생하는 예외 (환경 변수 누락, 잘못된 형식 등)."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        missing_keys: list[str] | None = None,
    ) -> None:
        context = {}
        if config_key:
            context["config_key"] = config_key
        if missing_keys:
            context["missing_keys"] = missing_keys
        super().__init__(message, code="CONFIG_ERROR", context=context)


class MissingConfigurationError(ConfigurationError):
    """필수 설정이 누락되었을 때 발생하는 예외."""

    def __init__(self, config_key: str) -> None:
        message = f"필수 설정이 누락되었습니다: {config_key}"
        super().__init__(message, config_key=config_key)


# === 보안 레이어 예외 ===


class SecurityError(TesterException):
    """보안 관련 예외 (암호화, 복호화 실패 등)."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
    ) -> None:
        context = {"operation": operation} if operation else {}
        super().__init__(message, code="SECURITY_ERROR", context=context)


class EncryptionError(SecurityError):
    """암호화 실패 시 발생하는 예외."""

    def __init__(self, message: str = "데이터 암호화에 실패했습니다") -> None:
        super().__init__(message, operation="encrypt")


class DecryptionError(SecurityError):
    """복호화 실패 시 발생하는 예외."""

    def __init__(self, message: str = "데이터 복호화에 실패했습니다") -> None:
        super().__init__(message, operation="decrypt")


# === 토큰/결제 레이어 예외 ===


class InsufficientTokensError(TesterException):
    """토큰 부족 시 발생하는 예외 (HTTP 402).

    테스트 생성 요청 시 사용자의 토큰 잔액이 필요량보다 적을 때 발생합니다.
    글로벌 예외 핸들러에서 402 Payment Required로 변환됩니다.

    Attributes:
        current: 현재 보유 토큰.
        required: 필요한 토큰.
    """

    def __init__(
        self,
        current: int,
        required: int,
    ) -> None:
        context = {"current": current, "required": required}
        super().__init__(
            message="토큰이 부족합니다",
            code="INSUFFICIENT_TOKENS",
            context=context,
        )
        self.current = current
        self.required = required


class DuplicateTransactionError(TesterException):
    """중복 보상 요청 시 발생하는 예외.

    같은 `transaction_id`로 토큰 적립을 2회 이상 시도할 때 발생합니다.
    Idempotency 보장을 위해 사용됩니다.
    """

    def __init__(self, transaction_id: str) -> None:
        super().__init__(
            message="이미 처리된 보상 요청입니다",
            code="DUPLICATE_TRANSACTION",
            context={"transaction_id": transaction_id[:16]},
        )
