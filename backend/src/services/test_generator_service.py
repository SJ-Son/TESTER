from collections.abc import AsyncGenerator

from src.exceptions import ValidationError
from src.languages.factory import LanguageFactory
from src.services.gemini_service import GeminiService


class TestGeneratorService:
    """
    테스트 코드 생성 비즈니스 로직을 담당하는 서비스

    Responsibilities:
    1. 언어별 전략 선택 및 검증
    2. Prompt 컨텍스트 생성
    3. AI 서비스 호출 (GeminiService)
    """

    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def generate_test(
        self, code: str, language: str, model: str, is_regenerate: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        테스트 코드를 생성합니다.

        Args:
            code: 소스 코드
            language: 프로그래밍 언어
            model: 사용할 AI 모델명

        Yields:
            str: 생성된 테스트 코드 청크 (스트리밍)

        Raises:
            ValidationError: 코드 검증 실패 시
        """
        # 1. 언어 전략 선택
        strategy = LanguageFactory.get_strategy(language)

        # 2. 코드 검증
        result = strategy.validate_code(code)
        if not result.is_valid:
            raise ValidationError(result.error_message)

        # 3. 시스템 프롬프트 생성
        system_instruction = strategy.get_system_instruction()

        # 4. Gemini 모델 설정 (필요시)
        self.gemini_service.model_name = model

        # 5. AI 생성 호출 (캐싱은 GeminiService 내부에서 처리됨)
        async for chunk in self.gemini_service.generate_test_code(
            source_code=code,
            system_instruction=system_instruction,
            stream=True,
            is_regenerate=is_regenerate,
        ):
            yield chunk
