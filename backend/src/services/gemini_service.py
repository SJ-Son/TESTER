"""
Gemini API 연동 서비스.
"""
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger


class GeminiService:
    """Gemini API를 통한 테스트 코드 생성 서비스"""

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.logger = get_logger(__name__)
        self.model_name = model_name
        self._configure_api()

    def _configure_api(self) -> None:
        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY 미설정")
            genai.configure(api_key=api_key)
        except Exception as e:
            self.logger.error(f"API 설정 실패: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def generate_test_code(self, source_code: str, system_instruction: str = None, stream: bool = True):
        """
        Args:
            source_code: 테스트할 소스 코드
            system_instruction: 언어별 시스템 프롬프트
            stream: 스트리밍 여부 (True: AsyncGenerator, False: str)
        """
        if not source_code.strip():
            msg = "# 코드를 입력해주세요."
            yield msg
            return

        try:
            # 동적으로 모델 인스턴스 생성
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            
            # 비동기 호출 (async API 사용)
            response = await model.generate_content_async(source_code, stream=stream)
        
            if stream:
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                if not response.text:
                    yield "# 응답 생성 실패"
                else:
                    yield response.text
                return
                
        except Exception as e:
            self.logger.error(f"API 호출 오류: {e}")
            raise
