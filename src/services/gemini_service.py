import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.config.settings import Settings
from src.utils.logger import get_logger
from src.utils.prompts import SYSTEM_INSTRUCTION

class GeminiService:
    """Google Gemini API 연동 서비스."""

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        """API 설정 및 모델 초기화."""
        self.logger = get_logger(__name__)
        self._configure_api()
        self.model = genai.GenerativeModel(
            model_name=model_name, 
            system_instruction=SYSTEM_INSTRUCTION
        )

    def _configure_api(self):
        """API Key 설정."""
        try:
            genai.configure(api_key=Settings.GEMINI_API_KEY)
        except Exception as e:
            self.logger.error(f"API 설정 실패: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def generate_test_code(self, source_code: str) -> str:
        """
        테스트 코드를 생성합니다. (재시도 로직 포함)
        """
        if not source_code.strip():
            self.logger.warning("빈 코드가 입력되었습니다.")
            return "테스트 코드를 생성할 소스 코드를 입력해주세요."

        self.logger.info("테스트 코드 생성 시작")
        
        try:
            response = self.model.generate_content(source_code)
            if response.text:
                self.logger.info("테스트 코드 생성 성공")
                return response.text
            return "응답을 생성하지 못했습니다."
                
        except Exception as e:
            self.logger.error(f"API 호출 오류 (재시도 예정): {e}")
            raise
