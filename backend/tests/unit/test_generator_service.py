from unittest.mock import MagicMock, patch

import pytest
from src.repositories.generation_repository import GenerationRepository
from src.services.gemini_service import GeminiService
from src.services.test_generator_service import TestGeneratorService


class TestTestGeneratorService:
    @pytest.mark.asyncio
    async def test_generate_test_validation_error(self):
        """코드 검증 실패 시 ValidationError 발생 테스트.

        유효하지 않은 코드가 전달되었을 때 ValidationError가 발생하는지 검증합니다.
        """
        mock_gemini_service = MagicMock(spec=GeminiService)
        mock_generation_repository = MagicMock(spec=GenerationRepository)
        service = TestGeneratorService(
            gemini_service=mock_gemini_service, generation_repository=mock_generation_repository
        )

        code = "invalid python code ("  # Syntax error
        language = "python"
        model = "gemini-pro"

        with patch(
            "src.services.test_generator_service.LanguageFactory.get_strategy"
        ) as mock_get_strategy:
            mock_strategy = MagicMock()
            mock_strategy.validate_code.return_value.is_valid = False
            mock_strategy.validate_code.return_value.error_message = "Syntax Error"
            mock_get_strategy.return_value = mock_strategy

            from src.exceptions import ValidationError

            with pytest.raises(ValidationError) as exc:
                async for _ in service.generate_test(code, language, model):
                    pass

            assert exc.value.message == "Syntax Error"

    @pytest.mark.asyncio
    async def test_generate_test_success(self):
        """테스트 코드 생성 성공 및 RAG 로직 연동 검증.

        정상적인 흐름에서 임베딩 검색, 프롬프트 주입 및 청크 반환이
        올바르게 동작하는지 확인합니다.
        """
        mock_gemini_service = MagicMock(spec=GeminiService)
        # AsyncMock for generate_embedding
        from unittest.mock import AsyncMock

        mock_gemini_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])

        mock_generation_repository = MagicMock(spec=GenerationRepository)
        # Mock successful generation item
        from src.repositories.generation_repository import GenerationModel

        mock_history = GenerationModel(
            input_code="def add(a, b): return a + b",
            generated_code="def test_add(): assert add(1, 2) == 3",
            language="python",
            model="gemini-pro",
        )
        mock_generation_repository.get_similar_successful_generations = AsyncMock(
            return_value=[mock_history]
        )

        service = TestGeneratorService(
            gemini_service=mock_gemini_service, generation_repository=mock_generation_repository
        )

        code = "def valid_python_code(): pass"
        language = "python"
        model = "gemini-pro"

        with (
            patch(
                "src.services.test_generator_service.LanguageFactory.get_strategy"
            ) as mock_get_strategy,
            patch("src.services.test_generator_service.GeminiService") as MockGeminiService,
        ):
            mock_strategy = MagicMock()
            mock_strategy.validate_code.return_value.is_valid = True
            mock_strategy.get_system_instruction.return_value = "Base instructional prompt."
            mock_get_strategy.return_value = mock_strategy

            mock_gemini_instance = MagicMock()

            async def mock_generate_test_code(*args, **kwargs):
                yield "test chunk 1"
                yield "test chunk 2"

            mock_gemini_instance.generate_test_code = mock_generate_test_code
            MockGeminiService.return_value = mock_gemini_instance

            # Execute the generator
            chunks = []
            async for chunk in service.generate_test(code, language, model):
                chunks.append(chunk)

            assert chunks == ["test chunk 1", "test chunk 2"]
            assert service.last_embedding == [0.1, 0.2, 0.3]

            mock_gemini_service.generate_embedding.assert_called_once_with(code)
            mock_generation_repository.get_similar_successful_generations.assert_called_once_with(
                embedding=[0.1, 0.2, 0.3], limit=2, language=language
            )
