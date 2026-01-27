import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """애플리케이션 환경 변수 관리."""
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    @staticmethod
    def validate():
        """필수 환경 변수 검증."""
        if not Settings.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
