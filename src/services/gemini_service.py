import google.generativeai as genai
from typing import Optional
from src.config.settings import Settings
from src.utils.logger import get_logger
from src.utils.prompts import SYSTEM_INSTRUCTION

class GeminiService:
    """
    Google Gemini API와 상호작용하여 콘텐츠를 생성하는 서비스 클래스입니다.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        GeminiService 초기화 메서드.
        API Key를 설정하고 로거를 초기화합니다.
        
        Args:
            model_name (str): 사용할 Gemini 모델 이름 (기본값: "gemini-1.5-flash")
        """
        self.logger = get_logger(__name__)
        self._configure_api()
        self.model = genai.GenerativeModel(
            model_name=model_name, 
            system_instruction=SYSTEM_INSTRUCTION
        )

    def _configure_api(self):
        """
        Google Generative AI 라이브러리에 API Key를 설정합니다.
        """
        try:
            genai.configure(api_key=Settings.GEMINI_API_KEY)
            self.logger.info("Gemini API 설정이 완료되었습니다.")
        except Exception as e:
            self.logger.error(f"API 설정 중 오류 발생: {e}")
            raise

    def generate_test_code(self, source_code: str) -> str:
        """
        입력받은 파이썬 소스 코드에 대한 테스트 코드를 생성합니다.

        Args:
            source_code (str): 테스트 코드를 생성할 원본 파이썬 코드

        Returns:
            str: 생성된 테스트 코드 (Markdown 코드 블록 포함)

        Raises:
            Exception: API 호출 실패 시 예외를 다시 발생시킵니다.
        """
        if not source_code.strip():
            self.logger.warning("빈 코드가 입력되었습니다.")
            return "테스트 코드를 생성할 소스 코드를 입력해주세요."

        self.logger.info("테스트 코드 생성 요청을 시작합니다.")
        
        try:
            # 동기적 API 호출
            response = self.model.generate_content(source_code)
            
            if response.text:
                self.logger.info("테스트 코드가 성공적으로 생성되었습니다.")
                return response.text
            else:
                self.logger.warning("API 응답이 비어있습니다.")
                return "응답을 생성하지 못했습니다."
                
        except Exception as e:
            self.logger.error(f"Gemini API 호출 중 오류 발생: {e}")
            raise
