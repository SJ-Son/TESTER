"""Gemini API 기반 테스트 코드 생성 서비스.

Google Gemini API를 활용하여 소스 코드에 대한 테스트 코드를 생성하며,
Redis 캐싱과 재시도 로직을 통해 안정성과 성능을 보장합니다.
"""

from collections.abc import AsyncGenerator
from typing import Final, Optional

import google.generativeai as genai
from src.config.constants import AIConstants
from src.config.settings import settings
from src.exceptions import ConfigurationError, GenerationError
from src.services.cache_service import CacheService
from src.types import CacheStrategyType, ModelName
from src.utils.logger import get_logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class GeminiService:
    """Gemini API를 통한 테스트 코드 생성 서비스.

    Features:
        - 스트리밍 응답 지원
        - 재시도 로직 (최대 3회)
        - Redis 캐싱으로 중복 요청 최적화
        - 재생성 시 temperature 조정
    """

    _DEFAULT_MODEL: Final[ModelName] = "gemini-2.0-flash-exp"
    """기본 Gemini 모델"""

    def __init__(self, model_name: Optional[str] = None) -> None:
        """GeminiService 인스턴스를 초기화합니다.

        Args:
            model_name: 사용할 Gemini 모델명 (None일 경우 기본값 사용).

        Raises:
            ConfigurationError: API 키가 설정되지 않은 경우.
        """
        self.logger = get_logger(__name__)
        self.model_name: Final[str] = model_name or settings.DEFAULT_GEMINI_MODEL
        self._configure_api()
        self.cache: Final[CacheService] = CacheService()

    def _configure_api(self) -> None:
        """Gemini API 키를 설정합니다.

        Raises:
            ConfigurationError: API 키가 없거나 잘못된 경우.
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다",
                missing_keys=["GEMINI_API_KEY"],
            )

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            raise ConfigurationError(
                "Gemini API 설정 실패",
                missing_keys=["GEMINI_API_KEY"],
            ) from e

    def _get_model(
        self, model_name: str, system_instruction: Optional[str] = None
    ) -> genai.GenerativeModel:
        """Gemini 모델 인스턴스를 생성합니다.

        Args:
            model_name: 모델 이름.
            system_instruction: 시스템 프롬프트.

        Returns:
            GenerativeModel 인스턴스.
        """
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
        )

    @retry(
        stop=stop_after_attempt(AIConstants.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate_test_code(
        self,
        source_code: str,
        system_instruction: Optional[str] = None,
        stream: bool = True,
        is_regenerate: bool = False,
    ) -> AsyncGenerator[str, None]:
        """테스트 코드를 생성합니다.

        Args:
            source_code: 테스트할 소스 코드.
            system_instruction: 언어별 시스템 프롬프트.
            stream: 스트리밍 여부.
            is_regenerate: 재생성 요청 여부 (True면 캐시 무시 및 창의성 증가).

        Yields:
            생성된 테스트 코드 청크.

        Raises:
            AIServiceError: API 호출 실패 시.
        """
        if not source_code.strip():
            yield "# 코드를 입력해주세요."
            return

        cache_strategy: CacheStrategyType = "gemini"
        cache_metadata = self.cache.generate_key(
            self.model_name,
            source_code,
            system_instruction or "",
            strategy=cache_strategy,
        )

        # 캐시 확인 (재생성 요청이 아닐 때만)
        if not is_regenerate:
            cached_result = self.cache.get(cache_metadata.key)
            if cached_result:
                self.logger.info_ctx("Cache Hit", cache_key=cache_metadata.key[:16])
                yield cached_result
                return

        try:
            model = self._get_model(self.model_name, system_instruction)

            # Temperature 설정: 재생성이면 창의적, 아니면 안정적
            temperature = (
                AIConstants.TEMPERATURE_CREATIVE
                if is_regenerate
                else AIConstants.TEMPERATURE_STABLE
            )
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

            # 캐시 저장
            if full_response_text:
                self.cache.set(
                    cache_metadata.key,
                    full_response_text,
                    ttl=cache_metadata.ttl,
                )
                self.logger.info_ctx(
                    "Cache Saved",
                    cache_key=cache_metadata.key[:16],
                    ttl=cache_metadata.ttl,
                )

        except Exception as e:
            self.logger.error_ctx("Gemini API Error", error=str(e))
            raise GenerationError(
                "테스트 코드 생성 중 오류가 발생했습니다",
                model=self.model_name,
            ) from e
