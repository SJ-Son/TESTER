from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 설정 및 검증"""

    # API Keys
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    TURNSTILE_SECRET_KEY: str = Field(default="", description="Cloudflare Turnstile Secret")

    # Security
    SUPABASE_JWT_SECRET: str = Field(
        default="",
        description="Supabase JWT Secret for token verification (Available in Supabase Dashboard > API)",
    )
    TESTER_INTERNAL_SECRET: str = Field(
        default="default-secret-change-me", description="Internal API Secret"
    )

    # CORS Settings
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        description="CORS Allowed Origins (comma-separated)",
    )

    # AI Configuration
    DEFAULT_GEMINI_MODEL: str = Field(
        default="gemini-3-flash-preview", description="Default Gemini model for test generation"
    )

    # Application (Cloud Run은 ENV 환경 변수 사용)
    ENV: str = Field(
        default="development", description="Environment: development/production/staging"
    )

    # Infrastructure
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis Connection URL")

    # Supabase
    SUPABASE_URL: str = Field(default="", description="Supabase Project URL")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="", description="Supabase Service Role Key (for Admin Access)"
    )

    # Security (Encryption)
    DATA_ENCRYPTION_KEY: str = Field(default="", description="AES Key for column encryption")

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"), env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        """Gemini API 키 형식 검증"""
        # 필수 값 체크 (빈 문자열 허용 안 함)
        if not v:
            raise ValueError("GEMINI_API_KEY is required.")

        if v != "your_gemini_api_key_here" and not v.startswith("AI"):
            raise ValueError("Invalid Gemini API key format (must start with 'AI')")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        """CORS Origins를 환경별로 제공"""
        if self.is_production:
            # Production: localhost 제거, 명시적으로 설정된 도메인만 허용
            origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
            return [o for o in origins if not o.startswith("http://localhost")]
        # Development: 모든 설정 허용
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENV.lower() == "production"

    # Legacy validate() method removed in favor of Pydantic validation


settings = Settings()
