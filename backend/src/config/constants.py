"""애플리케이션 전역 상수 정의.

모든 매직 넘버와 매직 스트링을 중앙 집중식으로 관리합니다.
상수는 불변성을 보장하며, 도메인별로 그룹화되어 있습니다.
"""

from collections.abc import Mapping
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
    """Redis 캐싱 관련 상수."""

    GEMINI_RESPONSE_TTL: Final[int] = 7200
    """Gemini API 응답 캐시 유지 시간: 2시간"""

    USER_HISTORY_TTL: Final[int] = 1800
    """사용자 히스토리 캐시 유지 시간: 30분"""

    VALIDATION_RULE_TTL: Final[int] = 86400
    """검증 규칙 캐시 유지 시간: 24시간"""

    DEFAULT_TTL: Final[int] = 3600
    """기본 캐시 유지 시간: 1시간"""

    TTL_MAPPING: Final[Mapping[str, int]] = {
        "gemini": GEMINI_RESPONSE_TTL,
        "history": USER_HISTORY_TTL,
        "validation": VALIDATION_RULE_TTL,
    }
    """캐시 전략별 TTL 매핑 (불변)"""


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
