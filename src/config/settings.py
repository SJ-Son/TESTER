import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    환경 변수에서 필요한 값을 로드하여 정적 변수로 제공합니다.
    """
    
    # Google Gemini API 키
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    @staticmethod
    def validate():
        """
        필수 환경 변수가 설정되어 있는지 검증합니다.
        설정이 누락된 경우 ValueError를 발생시킵니다.
        """
        if not Settings.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")

# 설정 검증 실행 (임포트 시점에 체크)
# 주의: 테스트 환경 등에서 API 키 없이 임포트해야 하는 경우 이 줄을 주석 처리할 수 있습니다.
# Settings.validate() 
