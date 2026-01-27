"""
Gemini API와 상호작용하는 서비스 클래스입니다.
성능 최적화(캐싱 준비), 에러 핸들링, 재시도 로직이 포함되어 있습니다.
"""
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.prompts import SYSTEM_INSTRUCTION


class GeminiService:
    """
    Google Gemini API를 사용하여 테스트 코드를 생성하는 서비스입니다.
    """

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        """
        GeminiService를 초기화합니다.
        
        Args:
            model_name: 사용할 Gemini 모델 이름
        """
        self.logger = get_logger(__name__)
        self.logger.info(f"GeminiService 초기화 중: 모델={model_name}")
        
        self._configure_api()
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        self.logger.info("GeminiService 초기화 완료")

    def _configure_api(self) -> None:
        """Gemini API 키를 설정합니다."""
        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
            
            genai.configure(api_key=api_key)
            self.logger.info("Gemini API 설정 완료")
            
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
        주어진 소스 코드에 대한 테스트 코드를 생성합니다.
        실패 시 최대 3번까지 재시도합니다.
        
        Args:
            source_code: 테스트할 파이썬 소스 코드
            
        Returns:
            생성된 테스트 코드 문자열
            
        Raises:
            Exception: API 호출 실패 시
        """
        if not source_code.strip():
            self.logger.warning("빈 코드 입력 감지")
            return "# 테스트할 소스 코드를 입력해주세요."

        self.logger.info("테스트 코드 생성 시작")
        
        try:
            response = self.model.generate_content(source_code)
            
            if not response or not response.text:
                self.logger.error("API 응답이 비어있습니다.")
                return "# 응답을 생성하지 못했습니다. 다시 시도해주세요."
            
            self.logger.info("테스트 코드 생성 성공")
            return response.text
            
        except Exception as e:
            self.logger.error(f"API 호출 오류 (재시도 예정): {e}")
            raise
