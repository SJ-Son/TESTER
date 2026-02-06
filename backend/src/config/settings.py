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
    WORKER_URL: str = Field(default="http://localhost:5000", description="Execution Worker URL")
    WORKER_AUTH_TOKEN: str = Field(default="", description="Token for Worker Authentication")

    # Supabase
    SUPABASE_URL: str = Field(default="", description="Supabase Project URL")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="", description="Supabase Service Role Key (for Admin Access)"
    )
    SUPABASE_ANON_KEY: str = Field(
        default="", description="Supabase Anon Key (for User Verification)"
    )

    # Security (Encryption)
    DATA_ENCRYPTION_KEY: str = Field(default="", description="AES Key for column encryption")

    # Content Security Policy
    CONTENT_SECURITY_POLICY: str = Field(
        default=(
            "default-src 'self' https://accounts.google.com https://www.gstatic.com https://www.google.com https://challenges.cloudflare.com; "
            "script-src 'self' 'unsafe-inline' https://accounts.google.com https://www.google.com https://www.gstatic.com https://apis.google.com https://challenges.cloudflare.com https://www.googletagmanager.com; "
            "style-src 'self' 'unsafe-inline' https://accounts.google.com https://fonts.googleapis.com https://www.gstatic.com; "
            "img-src 'self' data: https://*.googleusercontent.com https://www.gstatic.com https://www.google.com https://www.googletagmanager.com https://www.google-analytics.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "connect-src 'self' https://*.supabase.co https://accounts.google.com https://www.google.com https://challenges.cloudflare.com https://www.google-analytics.com https://analytics.google.com https://www.googletagmanager.com; "
            "frame-src 'self' https://accounts.google.com https://challenges.cloudflare.com; "
            "frame-ancestors 'self' https://accounts.google.com;"
        ),
        description="Content Security Policy Header",
    )

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
