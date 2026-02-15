from unittest.mock import MagicMock, patch

import pytest
from src.services.gemini_service import GeminiService
from src.services.test_generator_service import TestGeneratorService


class TestTestGeneratorService:
    def test_get_gemini_service_caching(self):
        """GeminiService 인스턴스 캐싱 테스트.

        동일한 모델명에 대해 서비스 인스턴스가 캐싱되어 재사용되는지 검증합니다.
        """
        mock_gemini_service = MagicMock(spec=GeminiService)
        service = TestGeneratorService(gemini_service=mock_gemini_service)

        model_name = "test-model"

        with patch(
            "src.services.test_generator_service.GeminiService"
        ) as MockGeminiServiceConstructor:
            instance1 = service._get_gemini_service(model_name)

            MockGeminiServiceConstructor.assert_called_once_with(model_name=model_name)

            MockGeminiServiceConstructor.reset_mock()
            instance2 = service._get_gemini_service(model_name)

            MockGeminiServiceConstructor.assert_not_called()

            assert instance1 is instance2

    @pytest.mark.asyncio
    async def test_generate_test_validation_error(self):
        """코드 검증 실패 시 ValidationError 발생 테스트.

        유효하지 않은 코드가 전달되었을 때 ValidationError가 발생하는지 검증합니다.
        """
        mock_gemini_service = MagicMock(spec=GeminiService)
        service = TestGeneratorService(gemini_service=mock_gemini_service)

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
