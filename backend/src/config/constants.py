"""애플리케이션 전역 상수 정의.

모든 매직 넘버와 매직 스트링을 중앙 집중식으로 관리합니다.
상수는 불변성을 보장하며, 도메인별로 그룹화되어 있습니다.
"""

from typing import Final

# === API 레이어 상수 ===


class APIConstants:
    """API 엔드포인트 관련 상수."""

    RATE_LIMIT: Final[str] = "5/minute"
    """요청 제한: 분당 5회"""

    MAX_CODE_LENGTH: Final[int] = 100_000
    """코드 입력 최대 길이 (문자)"""

    MIN_CODE_LENGTH: Final[int] = 10
    """코드 입력 최소 길이 (문자)"""

    DEFAULT_HISTORY_LIMIT: Final[int] = 50
    """기본 히스토리 조회 개수"""

    CHUNK_YIELD_INTERVAL: Final[int] = 100
    """스트리밍 중 이벤트 루프에 제어를 양보하는 청크 간격"""


# === 캐싱 레이어 상수 ===


class CacheConstants:
    """캐싱 관련 상수"""

    # TTL 설정 (초 단위)
    GEMINI_CACHE_TTL: Final[int] = 7200  # 2시간 (AI 응답은 재활용 가치 높음)
    VALIDATION_CACHE_TTL: Final[int] = 3600  # 1시간 (문법 검증은 변경 적음)
    HISTORY_CACHE_TTL: Final[int] = 600  # 10분 (사용자 이력은 자주 변경됨)
    DEFAULT_TTL: Final[int] = 3600  # 1시간

    # TTL 매핑
    TTL_MAPPING: Final[dict[str, int]] = {
        "gemini": GEMINI_CACHE_TTL,
        "validation": VALIDATION_CACHE_TTL,
        "history": HISTORY_CACHE_TTL,
    }


# === AI 모델 상수 ===


class AIConstants:
    """AI 서비스 (Gemini) 관련 상수."""

    DEFAULT_MODEL: Final[str] = "gemini-3-flash-preview"
    """기본 Gemini 모델명"""

    TEMPERATURE_CREATIVE: Final[float] = 0.7
    """재생성 요청 시 창의성 증가를 위한 temperature"""

    TEMPERATURE_STABLE: Final[float] = 0.2
    """일반 생성 시 일관성 유지를 위한 temperature"""

    MAX_RETRY_ATTEMPTS: Final[int] = 3
    """API 호출 실패 시 최대 재시도 횟수"""

    RETRY_WAIT_MIN: Final[int] = 2
    """재시도 대기 최소 시간 (초)"""

    RETRY_WAIT_MAX: Final[int] = 10
    """재시도 대기 최대 시간 (초)"""

    RETRY_MULTIPLIER: Final[int] = 1
    """지수 백오프 승수"""


# === 보안 상수 ===


class SecurityConstants:
    """보안 및 인증 관련 상수."""

    DANGEROUS_KEYWORDS: Final[tuple[str, ...]] = (
        "eval",
        "exec",
        "compile",
        "__import__",
        "subprocess",
        "os.system",
    )
    """코드 실행 시 위험한 키워드 목록 (불변 튜플)"""

    JWT_ALGORITHM: Final[str] = "HS256"
    """JWT 토큰 서명 알고리즘"""

    JWT_EXPIRE_MINUTES: Final[int] = 1440
    """JWT 토큰 만료 시간: 24시간"""

    MIN_PASSWORD_LENGTH: Final[int] = 8
    """최소 비밀번호 길이"""


# === 데이터베이스 상수 ===


class DatabaseConstants:
    """데이터베이스 (Supabase) 관련 상수."""

    GENERATION_HISTORY_TABLE: Final[str] = "generation_history"
    """생성 이력 테이블명"""

    DEFAULT_QUERY_LIMIT: Final[int] = 50
    """기본 쿼리 결과 제한"""


# === 검증 상수 ===


class ValidationConstants:
    """코드 검증 관련 상수."""

    EMPTY_CODE_ERROR: Final[str] = "코드를 입력해주세요."
    """빈 코드 입력 시 에러 메시지"""

    PYTHON_SYNTAX_ERROR: Final[str] = "유효한 파이썬 코드가 아닙니다."
    """Python 문법 오류 메시지"""

    JAVASCRIPT_SYNTAX_ERROR: Final[str] = "유효한 JavaScript 코드가 아닙니다."
    """JavaScript 문법 오류 메시지"""

    JAVA_SYNTAX_ERROR: Final[str] = "유효한 Java 코드가 아닙니다."
    """Java 문법 오류 메시지"""


# === 에러 메시지 상수 ===


class ErrorMessages:
    """사용자 대면 에러 메시지 (한글)."""

    # === 인증 관련 ===
    AUTH_FAILED: Final[str] = "인증에 실패했습니다"
    AUTH_TOKEN_MISSING: Final[str] = "인증 토큰이 필요합니다"
    AUTH_SERVICE_UNAVAILABLE: Final[str] = "인증 서비스를 사용할 수 없습니다"
    AUTH_INVALID_CREDENTIALS: Final[str] = "인증 정보가 올바르지 않습니다"

    # === 검증 관련 ===
    CODE_EMPTY: Final[str] = "코드를 입력해주세요"
    CODE_INVALID_SYNTAX: Final[str] = "코드 문법이 올바르지 않습니다"
    LANGUAGE_NOT_SUPPORTED: Final[str] = "지원하지 않는 프로그래밍 언어입니다"

    # === 서비스 관련 ===
    CACHE_CONNECTION_FAILED: Final[str] = "캐시 서버 연결에 실패했습니다"
    DB_CONNECTION_FAILED: Final[str] = "데이터베이스 연결에 실패했습니다"
    AI_SERVICE_ERROR: Final[str] = "AI 서비스 오류가 발생했습니다"
    GENERATION_FAILED: Final[str] = "코드 생성 중 오류가 발생했습니다"

    # === 데이터 관련 ===
    ENCRYPTION_FAILED: Final[str] = "데이터 암호화에 실패했습니다"
    DECRYPTION_FAILED: Final[str] = "데이터 복호화에 실패했습니다"
    SAVE_FAILED: Final[str] = "데이터 저장에 실패했습니다"
    HISTORY_SAVE_WARNING: Final[
        str
    ] = "코드 저장에 실패했습니다. 생성된 코드를 복사하여 별도로 저장해주세요."

    # === Turnstile 관련 ===
    TURNSTILE_VERIFICATION_FAILED: Final[str] = "보안 검증에 실패했습니다"
    TURNSTILE_TOKEN_MISSING: Final[str] = "보안 토큰이 필요합니다"


# === 네트워크 상수 ===


class NetworkConstants:
    """네트워크 및 연결 관련 상수."""

    # HTTP Timeouts
    HTTP_TIMEOUT_SECONDS: Final[int] = 10
    """기본 HTTP 요청 타임아웃"""

    TURNSTILE_TIMEOUT_SECONDS: Final[int] = 5
    """Turnstile 검증 타임아웃"""

    # Compression
    GZIP_MIN_SIZE_BYTES: Final[int] = 500
    """GZip 압축 최소 크기"""

    # Redis Connection Pool
    REDIS_MAX_CONNECTIONS: Final[int] = 10
    """Redis 최대 연결 수"""

    REDIS_KEEPALIVE_IDLE: Final[int] = 60
    """TCP Keepalive idle 시간 (초)"""

    REDIS_KEEPALIVE_INTERVAL: Final[int] = 10
    """TCP Keepalive 전송 간격 (초)"""

    REDIS_KEEPALIVE_COUNT: Final[int] = 3
    """TCP Keepalive 최대 재시도 횟수"""
