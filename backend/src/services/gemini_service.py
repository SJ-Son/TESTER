import google.generativeai as genai
from src.config.settings import settings
from src.services.cache_service import CacheService
from src.utils.logger import get_logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class GeminiService:
    """Gemini API를 통한 테스트 코드 생성 서비스"""

    def __init__(self, model_name: str | None = None):
        self.logger = get_logger(__name__)
        self.model_name = model_name or settings.DEFAULT_GEMINI_MODEL
        self._configure_api()
        # CacheService 초기화 (Redis 연결)
        self.cache = CacheService()

    def _configure_api(self) -> None:
        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY 미설정")
            genai.configure(api_key=api_key)
        except Exception as e:
            self.logger.error(f"API 설정 실패: {e}")
            raise

    def _get_model(self, model_name: str, system_instruction: str = None):
        """모델 인스턴스 생성"""
        # lru_cache는 프롬프트 캐싱을 위해 남겨둘 수 있으나,
        # 여기서는 매번 생성해도 가벼운 객체이므로 제거하거나 단순화
        return genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate_test_code(
        self,
        source_code: str,
        system_instruction: str = None,
        stream: bool = True,
        is_regenerate: bool = False,
    ):
        """
        Args:
            source_code: 테스트할 소스 코드
            system_instruction: 언어별 시스템 프롬프트
            stream: 스트리밍 여부
            is_regenerate: 재생성 요청 여부 (True면 캐시 무시 및 창의성 증가)
        """
        if not source_code.strip():
            msg = "# 코드를 입력해주세요."
            yield msg
            return

        # 1. Generate Cache Key with TTL
        cache_key, ttl = self.cache.generate_key(self.model_name, source_code, system_instruction)

        # 2. Check Cache (Hit) - Skip if regenerating
        if not is_regenerate:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.logger.info_ctx("Cache Hit", cache_key=cache_key[:16])
                yield cached_result
                return

        try:
            # 3. Cache Miss or Regenerate - Call API
            model = self._get_model(self.model_name, system_instruction)

            # Temperature 설정: 재생성이면 0.7 (창의적), 아니면 0.2 (안정적)
            # 0.0은 너무 딱딱하므로 0.2로 완화하여 자연스러운 일관성 유지
            temperature = 0.7 if is_regenerate else 0.2
            generation_config = genai.types.GenerationConfig(temperature=temperature)

            response = await model.generate_content_async(
                source_code,
                stream=stream,
                generation_config=generation_config,
            )

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

            # 4. Save to Cache (Redis) with strategy-based TTL
            if full_response_text:
                self.cache.set(cache_key, full_response_text, ttl=ttl)
                self.logger.info_ctx("Cache Saved", cache_key=cache_key[:16], ttl=ttl)

        except Exception as e:
            self.logger.error_ctx("API Error", error=str(e))
            raise
