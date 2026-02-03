from unittest.mock import Mock, patch

import pytest

from backend.src.exceptions import ValidationError
from backend.src.services.test_generator_service import TestGeneratorService


@pytest.fixture
def mock_gemini_service():
    service = Mock()
    # verify_turnstile etc might need AsyncMock, but generate_test_code is an async generator
    # so we use Mock() and set side_effect to an async generator function
    service.generate_test_code = Mock()
    return service


@pytest.fixture
def test_service(mock_gemini_service):
    return TestGeneratorService(gemini_service=mock_gemini_service)


async def mock_async_gen(*args, **kwargs):
    yield "chunk1"
    yield "chunk2"


@pytest.mark.asyncio
async def test_generate_test_success(test_service, mock_gemini_service):
    # Mock Language Strategy verification
    with patch("backend.src.services.test_generator_service.LanguageFactory") as MockFactory:
        mock_strategy = Mock()
        mock_strategy.validate_code.return_value = (True, "")
        mock_strategy.get_system_instruction.return_value = "sys_instruct"
        MockFactory.get_strategy.return_value = mock_strategy

        # Mock Generator Output (Assign the async generator function as side_effect)
        # We need to make sure the mock acts like an async generator when called
        mock_gemini_service.generate_test_code.side_effect = mock_async_gen

        # Execute
        chunks = []
        async for chunk in test_service.generate_test("code", "python", "model"):
            chunks.append(chunk)

        # Assert
        assert chunks == ["chunk1", "chunk2"]
        mock_strategy.validate_code.assert_called_with("code")
        mock_gemini_service.generate_test_code.assert_called_once()
        assert test_service.gemini_service.model_name == "model"


@pytest.mark.asyncio
async def test_generate_test_validation_error(test_service):
    with patch("backend.src.services.test_generator_service.LanguageFactory") as MockFactory:
        mock_strategy = Mock()
        mock_strategy.validate_code.return_value = (False, "Invalid code")
        MockFactory.get_strategy.return_value = mock_strategy

        with pytest.raises(ValidationError) as exc:
            async for _ in test_service.generate_test("bad_code", "python", "model"):
                pass

        assert str(exc.value) == "Invalid code"
