from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 설정 및 검증"""

    # API 키 설정
    GEMINI_API_KEY: SecretStr = Field(default="", description="Google Gemini API Key")
    TURNSTILE_SECRET_KEY: SecretStr = Field(default="", description="Cloudflare Turnstile Secret")

    # 보안 설정
    SUPABASE_JWT_SECRET: SecretStr = Field(
        default="",
        description="Supabase JWT 검증용 시크릿 (Supabase Dashboard > API)",
    )
    TESTER_INTERNAL_SECRET: SecretStr = Field(
        default="default-secret-change-me", description="내부 API 통신용 시크릿"
    )

    # 워커 인증 토큰
    WORKER_AUTH_TOKEN: SecretStr = Field(default="", description="Worker authentication token")

    # CORS 설정
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        description="허용할 CORS 오리진 (쉼표로 구분)",
    )

    # AI 모델 설정
    DEFAULT_GEMINI_MODEL: str = Field(
        default="gemini-3-flash-preview", description="기본 Gemini 모델"
    )

    # 앱 환경 설정 (Cloud Run: ENV 변수 사용)
    ENV: str = Field(
        default="development", description="Environment: development/production/staging"
    )

    # 인프라 설정 (Redis)
    REDIS_HOST: str = Field(default="localhost", description="Redis 호스트")
    REDIS_PORT: int = Field(default=6379, description="Redis 포트")
    REDIS_URL: str = Field(default="", description="Redis 연결 URL")

    @model_validator(mode="after")
    def assemble_redis_url(self):
        """REDIS_URL이 없으면 호스트/포트로 조합"""
        if not self.REDIS_URL:
            host = self.REDIS_HOST
            port = self.REDIS_PORT
            self.REDIS_URL = f"redis://{host}:{port}"
        return self

    # Supabase 설정
    SUPABASE_URL: str = Field(default="", description="Supabase 프로젝트 URL")
    SUPABASE_SERVICE_ROLE_KEY: SecretStr = Field(
        default="", description="Supabase Service Role Key (관리자용)"
    )
    SUPABASE_ANON_KEY: SecretStr = Field(
        default="", description="Supabase Anon Key (사용자 검증용)"
    )

    # 데이터 암호화 키
    DATA_ENCRYPTION_KEY: SecretStr = Field(default="", description="DB 컬럼 암호화용 AES 키")

    # 후원 설정
    KOFI_URL: str = Field(default="", description="Ko-fi 후원 페이지 URL")
    KOFI_VERIFICATION_TOKEN: SecretStr = Field(default="", description="Ko-fi Webhook 검증 토큰")

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"), env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def validate_production_security(self):
        """Production Security Validation"""
        if self.ENV.lower() != "development":
            if self.TESTER_INTERNAL_SECRET.get_secret_value() == "default-secret-change-me":
                raise RuntimeError(
                    "❌ SECURITY ERROR: TESTER_INTERNAL_SECRET is set to default value in non-development environment!"
                )
        return self

    @model_validator(mode="after")
    def validate_critical_keys(self):
        """Startup Validation for Critical Keys"""
        if not self.GEMINI_API_KEY.get_secret_value():
            raise RuntimeError("❌ CRITICAL: GEMINI_API_KEY is missing!")
        if not self.SUPABASE_SERVICE_ROLE_KEY.get_secret_value():
            raise RuntimeError("❌ CRITICAL: SUPABASE_SERVICE_ROLE_KEY is missing!")
        return self

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_key(cls, v: SecretStr) -> SecretStr:
        """Gemini API 키 형식 검증"""
        # 필수 값 체크 (빈 문자열 허용 안 함) already handled by validate_critical_keys but good for specific field

        value = v.get_secret_value() if v else ""
        if not value:
            return v

        if value != "your_gemini_api_key_here" and not value.startswith("AI"):
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


settings = Settings()
