import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from functools import lru_cache
from collections import OrderedDict
import hashlib
import asyncio

from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger


class GeminiService:
    """Gemini API를 통한 테스트 코드 생성 서비스"""

    # In-Memory Cache (Class Level)
    _cache = OrderedDict()
    _CACHE_LIMIT = 50

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

    @lru_cache(maxsize=10)
    def _get_model(self, model_name: str, system_instruction: str = None):
        """모델 인스턴스 생성을 캐싱하여 성능을 최적화합니다."""
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )

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

        # 1. Generate Cache Key
        key_input = f"{self.model_name}:{source_code}:{system_instruction}"
        cache_key = hashlib.md5(key_input.encode()).hexdigest()

        # 2. Check Cache (Hit)
        if cache_key in self._cache:
            self.logger.info(f"Cache Hit for key: {cache_key}")
            self._cache.move_to_end(cache_key)  # Mark as recently used
            yield self._cache[cache_key]
            return

        try:
            # 3. Cache Miss - Call API
            model = self._get_model(self.model_name, system_instruction)
            
            # 비동기 호출 (async API 사용)
            response = await model.generate_content_async(source_code, stream=stream)
            
            full_response_text = ""
        
            if stream:
                async for chunk in response:
                    if chunk.text:
                        full_response_text += chunk.text
                        yield chunk.text
            else:
                if not response.text:
                    yield "# 응답 생성 실패"
                else:
                    full_response_text = response.text
                    yield response.text
            
            # 4. Save to Cache
            if full_response_text:
                self._cache[cache_key] = full_response_text
                # Enforce LRU Limit
                if len(self._cache) > self._CACHE_LIMIT:
                    self._cache.popitem(last=False)
                    
        except Exception as e:
            self.logger.error(f"API 호출 오류: {e}")
            raise
