"""
User-facing Messages
"""


class ErrorMessages:
    """Error messages for users"""

    EMPTY_CODE = "# 코드를 입력해주세요."
    CODE_TOO_SHORT = "코드가 너무 짧습니다 (최소 {min_length}자)"
    CODE_TOO_LONG = "코드가 너무 깁니다 (최대 {max_length}자)"
    DANGEROUS_KEYWORD = "위험한 키워드 감지: '{keyword}' 사용 불가"
    API_KEY_MISSING = "GEMINI_API_KEY 설정이 필요합니다"
    API_KEY_INVALID = "Invalid Gemini API key format (must start with 'AI')"
    VALIDATION_FAILED = "입력 코드를 확인해주세요"
    UNAUTHORIZED = "인증이 필요합니다"
    TURNSTILE_FAILED = "Turnstile 검증 실패"
    RATE_LIMIT_EXCEEDED = "요청 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
    UNSUPPORTED_LANGUAGE = "지원하지 않는 언어: {language}"


class InfoMessages:
    """Informational messages"""

    CACHE_HIT = "캐시에서 결과를 불러왔습니다"
    CACHE_SAVED = "결과가 캐시에 저장되었습니다"
    GENERATION_STARTED = "테스트 코드 생성 중..."
    GENERATION_COMPLETE = "테스트 코드 생성 완료"
    API_RESPONSE_EMPTY = "# 응답 생성 실패"


class LogMessages:
    """Internal log messages (English)"""

    REDIS_CONNECTED = "Connected to Redis successfully"
    REDIS_FAILED = "Failed to connect to Redis. Caching might be disabled"
    SERVER_STARTED = "Starting server on port {port}"
    FRONTEND_FOUND = "Found frontend at {path}"
    FRONTEND_NOTFOUND = "Frontend dist not found at {path}. Serving API only"
    CACHE_HIT_LOG = "Cache Hit"
    CACHE_MISS_LOG = "Cache Miss"
    VALIDATION_FAILED_LOG = "Validation failed: {message}"
    API_ERROR_LOG = "API Error: {error}"
    STREAMING_ERROR_LOG = "Streaming error: {error}"
