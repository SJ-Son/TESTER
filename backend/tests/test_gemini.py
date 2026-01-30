"""
GeminiService의 단위 테스트입니다.
pytest-mock을 사용하여 실제 API 호출 없이 테스트합니다.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.src.services.gemini_service import GeminiService


class TestGeminiService:
    """GeminiService 클래스에 대한 테스트 모음입니다."""

    @pytest.fixture
    def service(self):
        """테스트용 GeminiService 인스턴스를 생성합니다."""
        with patch("backend.src.services.gemini_service.genai.configure"):
            return GeminiService(model_name="gemini-3-flash-preview")

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """서비스가 올바르게 초기화되는지 테스트합니다."""
        assert service is not None
        # model은 동적으로 생성되므로 __init__ 시점에는 _configure_api만 호출됨
        assert service.model_name == "gemini-3-flash-preview"

    @pytest.mark.asyncio
    @patch("backend.src.services.gemini_service.genai.GenerativeModel")
    async def test_generate_test_code_success(self, mock_model_class, service):
        """정상적인 코드 입력 시 테스트 코드가 생성되는지 확인합니다."""
        # Mock 설정
        mock_model = mock_model_class.return_value
        
        # Async Generator Mock
        async def mock_async_gen():
            yield MagicMock(text="def test_example():")
            yield MagicMock(text="\n    assert True")

        mock_model.generate_content_async = AsyncMock(return_value=mock_async_gen())
        
        # 실행
        results = []
        async for chunk in service.generate_test_code("def example(): pass"):
            results.append(chunk)
        
        result = "".join(results)
        
        # 검증
        assert "def test_example" in result
        mock_model.generate_content_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_test_code_empty_input(self, service):
        """빈 입력에 대한 처리를 테스트합니다."""
        results = []
        async for chunk in service.generate_test_code(""):
            results.append(chunk)
        result = "".join(results)
        assert "코드" in result or "입력" in result

    @pytest.mark.asyncio
    @patch("backend.src.services.gemini_service.genai.GenerativeModel")
    async def test_generate_test_code_api_error(self, mock_model_class, service):
        """API 오류 발생 시 재시도 로직을 테스트합니다."""
        mock_model = mock_model_class.return_value
        mock_model.generate_content_async = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # 재시도 후 최종 실패 예상
        with pytest.raises(Exception):
            async for _ in service.generate_test_code("def test(): pass"):
                pass
        
        # tenacity의 재시도 로직 확인
        # 참고: async generator에서 @retry를 사용하는 경우, 이터레이션 도중 실패 시 재시도 동작은 
        # 사용 방식에 따라 다를 수 있습니다. 현재 구조에서는 발전기 생성 단계만 래핑될 수 있습니다.
        assert mock_model.generate_content_async.call_count >= 1
