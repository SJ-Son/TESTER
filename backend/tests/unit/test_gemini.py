import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.src.services.gemini_service import GeminiService

class TestGeminiService:
    @pytest.fixture
    def service(self):
        with patch("backend.src.services.gemini_service.genai.configure"):
            return GeminiService(model_name="gemini-3-flash-preview")

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        assert service.model_name == "gemini-3-flash-preview"

    @pytest.mark.asyncio
    @patch("backend.src.services.gemini_service.genai.GenerativeModel")
    async def test_generate_test_code_success(self, mock_model_class, service):
        mock_model = mock_model_class.return_value
        
        async def mock_async_gen():
            yield MagicMock(text="def test_example():")
            yield MagicMock(text="\n    assert True")

        mock_model.generate_content_async = AsyncMock(return_value=mock_async_gen())
        
        results = []
        async for chunk in service.generate_test_code("def example(): pass"):
            results.append(chunk)
        
        result = "".join(results)
        assert "def test_example" in result
        mock_model.generate_content_async.assert_called_once()
