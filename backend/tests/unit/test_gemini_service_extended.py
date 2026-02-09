from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.config.settings import settings
from src.services.gemini_service import GeminiService


class TestGeminiServiceExtended:
    @pytest.fixture
    def mock_cache_service(self):
        with patch("src.services.gemini_service.CacheService") as MockCache:
            mock_instance = MockCache.return_value
            # Default behavior
            mock_instance.generate_key.return_value = ("test_key", 3600)
            mock_instance.get.return_value = None
            yield mock_instance

    @pytest.fixture
    def service(self, mock_cache_service):
        with patch("src.services.gemini_service.genai.configure"):
            return GeminiService(model_name="gemini-3-flash-preview")


    @pytest.mark.asyncio
    async def test_empty_source_code(self, service):
        results = []
        async for chunk in service.generate_test_code("   "):
            results.append(chunk)

        assert len(results) == 1
        assert "# 코드를 입력해주세요" in results[0]
        # Cache should not be called
        service.cache.generate_key.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_hit(self, service):
        # Setup cache hit
        service.cache.get.return_value = "Cached Result"

        results = []
        async for chunk in service.generate_test_code("valid code", is_regenerate=False):
            results.append(chunk)

        assert "".join(results) == "Cached Result"
        # API should not be initialized or called
        # We can check if _get_model was NOT called, but it's private.
        # Instead verify cache.get called
        service.cache.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_regenerate_true_ignores_cache(self, service):
        # Setup cache hit available BUT regenerate turned on
        service.cache.get.return_value = "Cached Result"

        # Mock API
        with patch.object(service, "_get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_get_model.return_value = mock_model

            async def mock_gen(*args, **kwargs):
                yield MagicMock(text="New Result")

            mock_model.generate_content_async = AsyncMock(return_value=mock_gen())

            results = []
            async for chunk in service.generate_test_code("code", is_regenerate=True):
                results.append(chunk)

            assert "New Result" in "".join(results)
            # Cache get should NOT be called
            service.cache.get.assert_not_called()
            # Temperature checks
            args, kwargs = mock_model.generate_content_async.call_args
            config = kwargs["generation_config"]
            assert config.temperature == 0.7  # Regenerate -> High creativity

    @pytest.mark.asyncio
    async def test_api_call_and_cache_save(self, service):
        # Cache miss
        service.cache.get.return_value = None

        with patch.object(service, "_get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_get_model.return_value = mock_model

            async def mock_gen(*args, **kwargs):
                yield MagicMock(text="Generated Content")

            mock_model.generate_content_async = AsyncMock(return_value=mock_gen())

            results = []
            async for chunk in service.generate_test_code("code", stream=True):
                results.append(chunk)

            final_text = "".join(results)
            assert final_text == "Generated Content"

            # Verify save
            service.cache.set.assert_called_once()
            args, _ = service.cache.set.call_args
            assert args[0] == "test_key"
            assert args[1] == "Generated Content"

    @pytest.mark.asyncio
    async def test_api_error_propagation(self, service):
        service.cache.get.return_value = None

        with patch.object(service, "_get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_get_model.return_value = mock_model
            # Simulate API Error
            mock_model.generate_content_async = AsyncMock(side_effect=Exception("Google API Error"))

            with pytest.raises(Exception, match="Google API Error"):
                async for _ in service.generate_test_code("code"):
                    pass

    @pytest.mark.asyncio
    async def test_non_stream_mode(self, service):
        service.cache.get.return_value = None

        with patch.object(service, "_get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_get_model.return_value = mock_model

            # Non-stream response mocking
            mock_response = MagicMock()
            mock_response.text = "Non-stream response"
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)

            results = []
            async for chunk in service.generate_test_code("code", stream=False):
                results.append(chunk)

            assert results[0] == "Non-stream response"
