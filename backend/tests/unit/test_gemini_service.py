from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.services.gemini_service import GeminiService


class TestGeminiService:
    @pytest.mark.asyncio
    @patch("src.services.gemini_service.genai.embed_content_async")
    async def test_generate_embedding_success(self, mock_embed_content_async):
        """임베딩 정상 반환 테스트"""
        mock_embed_content_async.return_value = {"embedding": [0.1, 0.2, 0.3]}

        service = GeminiService()
        result = await service.generate_embedding("def test(): pass")

        assert result == [0.1, 0.2, 0.3]
        mock_embed_content_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.gemini_service.genai.embed_content_async")
    async def test_generate_embedding_empty_text(self, mock_embed_content_async):
        """빈 텍스트일 때 빈 리스트 반환 테스트"""
        service = GeminiService()
        result = await service.generate_embedding("   ")

        assert result == []
        mock_embed_content_async.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.services.gemini_service.genai.embed_content_async")
    async def test_generate_embedding_error(self, mock_embed_content_async):
        """API 호출 실패 시 빈 리스트 반환 테스트"""
        mock_embed_content_async.side_effect = Exception("API Error")

        service = GeminiService()
        result = await service.generate_embedding("def test(): pass")

        assert result == []

    @pytest.mark.asyncio
    async def test_generate_test_code_empty_code(self):
        """빈 텍스트일 때 에러 문구 반환 테스트"""
        service = GeminiService()
        chunks = []
        async for chunk in service.generate_test_code("   "):
            chunks.append(chunk)

        assert chunks == ["# 코드를 입력해주세요."]

    @pytest.mark.asyncio
    @patch("src.services.gemini_service.CacheService")
    @patch("src.services.gemini_service.genai.GenerativeModel")
    async def test_generate_test_code_cache_hit(self, MockGenerativeModel, MockCacheService):
        """캐시 성공 시 AI 호출 없이 캐시 응답 반환 테스트"""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = "cached test code"
        # Mocking generate_key to return a dummy metadata
        mock_metadata = MagicMock()
        mock_metadata.key = "fake_key"
        mock_cache.generate_key = MagicMock(return_value=mock_metadata)
        MockCacheService.return_value = mock_cache

        service = GeminiService()
        chunks = []
        async for chunk in service.generate_test_code("code", is_regenerate=False):
            chunks.append(chunk)

        assert chunks == ["cached test code"]
        MockGenerativeModel.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.services.gemini_service.CacheService")
    @patch("src.services.gemini_service.genai.GenerativeModel")
    async def test_generate_test_code_api_call(self, MockGenerativeModel, MockCacheService):
        """캐시 실패 시 AI 모델 호출 테스트"""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None
        mock_metadata = MagicMock()
        mock_metadata.key = "fake_key"
        mock_metadata.ttl = 3600
        mock_cache.generate_key = MagicMock(return_value=mock_metadata)
        MockCacheService.return_value = mock_cache

        mock_model_instance = MagicMock()

        # Async generator mock for generate_content_async
        async def mock_response():
            class Chunk:
                def __init__(self, text):
                    self.text = text

            yield Chunk("generated ")
            yield Chunk("code")

        mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response())
        MockGenerativeModel.return_value = mock_model_instance

        service = GeminiService()
        chunks = []
        async for chunk in service.generate_test_code("code", stream=True, is_regenerate=True):
            chunks.append(chunk)

        assert chunks == ["generated ", "code"]
        mock_cache.set.assert_called_once_with("fake_key", "generated code", ttl=3600)
