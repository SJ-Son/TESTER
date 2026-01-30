from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    """애플리케이션 설정을 관리합니다."""
    
    # API Keys & Secrets
    GEMINI_API_KEY: str = ""
    TESTER_INTERNAL_SECRET: str = "default-secret-change-me"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    JWT_SECRET: str = "yoursecretkey-change-me-in-production"
    RECAPTCHA_SECRET_KEY: str = ""
    
    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8080"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    def validate(self):
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 설정이 필요합니다 (.env 또는 환경변수)")

settings = Settings()
