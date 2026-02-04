"""
Application Constants
"""


class APIConstants:
    """API related constants"""

    RATE_LIMIT = "5/minute"
    DEFAULT_CACHE_TTL = 3600
    MAX_CODE_LENGTH = 100000
    MIN_CODE_LENGTH = 10


class CacheConstants:
    """Cache TTL constants (in seconds)"""

    GEMINI_TTL = 7200  # 2 hours
    HISTORY_TTL = 1800  # 30 minutes
    VALIDATION_TTL = 86400  # 24 hours


class ModelConstants:
    """AI Model constants"""

    DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
    TEMPERATURE_REGENERATE = 0.7  # Creative
    TEMPERATURE_NORMAL = 0.2  # Stable


class SecurityConstants:
    """Security related constants"""

    DANGEROUS_KEYWORDS = [
        "eval",
        "exec",
        "compile",
        "__import__",
        "subprocess",
        "os.system",
    ]
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 1440  # 24 hours
