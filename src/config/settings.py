import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """애플리케이션 설정을 관리합니다."""

    @property
    def GEMINI_API_KEY(self) -> str:
        """
        Gemini API 키를 반환합니다.
        우선순위: os.getenv (.env 또는 시스템 환경변수)
        """
        return os.getenv("GEMINI_API_KEY", "")

    def validate(self):
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 설정이 필요합니다 (.env 또는 secrets.toml)")

settings = Settings()
