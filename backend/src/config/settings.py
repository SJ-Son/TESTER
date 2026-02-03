from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 설정 및 검증"""

    # API Keys
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth Client Secret")
    TURNSTILE_SECRET_KEY: str = Field(default="", description="Cloudflare Turnstile Secret")

    # Security
    JWT_SECRET: str = Field(
        default="yoursecretkey-change-me-in-production",
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

    # Application (Cloud Run은 ENV 환경 변수 사용)
    ENV: str = Field(
        default="development", description="Environment: development/production/staging"
    )

    # Infrastructure
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis Connection URL")

    # Supabase (Optional for now)
    SUPABASE_URL: str = Field(default="", description="Supabase Project URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase Anon/Service Key")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        """Gemini API 키 형식 검증 (값이 있을 때만)"""
        if v and not v.startswith("AI"):
            raise ValueError("Invalid Gemini API key format (must start with 'AI')")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        """CORS Origins를 리스트로 변환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENV.lower() == "production"

    def validate(self):
        """레거시 호환성을 위한 검증 메서드"""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 설정이 필요합니다 (.env 또는 환경변수)")


settings = Settings()
