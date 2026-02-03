from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 설정 및 검증"""

    # API Keys
    GEMINI_API_KEY: str = Field(default="", min_length=10, description="Google Gemini API Key")
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth Client Secret")
    TURNSTILE_SECRET_KEY: str = Field(default="", description="Cloudflare Turnstile Secret")

    # Security
    JWT_SECRET: str = Field(
        default="yoursecretkey-change-me-in-production",
        min_length=32,
        description="JWT Signing Secret",
    )
    TESTER_INTERNAL_SECRET: str = Field(
        default="default-secret-change-me", description="Internal API Secret"
    )

    # CORS Settings
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        description="CORS Allowed Origins (comma-separated)",
    )

    # Application
    ENVIRONMENT: str = Field(
        default="development", description="Environment: development/production"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        """Gemini API 키 형식 검증"""
        if v and not v.startswith("AI"):
            raise ValueError("Invalid Gemini API key format (must start with 'AI')")
        return v

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """JWT Secret 보안 검증"""
        insecure_values = {"changeme", "secret", "password", "12345", "yoursecretkey"}
        if any(insecure in v.lower() for insecure in insecure_values):
            raise ValueError(
                "JWT_SECRET contains insecure patterns. Use a strong random value in production."
            )
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters for security")
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """환경 값 검증"""
        allowed = {"development", "production", "staging", "test"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v.lower()

    @property
    def allowed_origins_list(self) -> list[str]:
        """CORS Origins를 리스트로 변환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENVIRONMENT == "production"

    def validate(self):
        """레거시 호환성을 위한 검증 메서드 (Pydantic validator로 대체됨)"""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 설정이 필요합니다 (.env 또는 환경변수)")


settings = Settings()
