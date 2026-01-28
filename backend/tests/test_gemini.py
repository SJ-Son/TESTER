"""
GeminiService의 단위 테스트입니다.
pytest-mock을 사용하여 실제 API 호출 없이 테스트합니다.
"""
import pytest
from unittest.mock import MagicMock, patch

from src.services.gemini_service import GeminiService


class TestGeminiService:
    """GeminiService 클래스에 대한 테스트 모음입니다."""

    @pytest.fixture
    def service(self):
        """테스트용 GeminiService 인스턴스를 생성합니다."""
        with patch("src.services.gemini_service.genai.configure"):
            return GeminiService(model_name="gemini-3-flash-preview")

    def test_service_initialization(self, service):
        """서비스가 올바르게 초기화되는지 테스트합니다."""
        assert service is not None
        assert service.model is not None

    @patch("src.services.gemini_service.genai.GenerativeModel")
    def test_generate_test_code_success(self, mock_model_class, service):
        """정상적인 코드 입력 시 테스트 코드가 생성되는지 확인합니다."""
        # Mock 설정
        mock_response = MagicMock()
        mock_response.text = "def test_example():\n    assert True"
        
        service.model.generate_content = MagicMock(return_value=mock_response)
        
        # 실행
        result = service.generate_test_code("def example(): pass")
        
        # 검증
        assert "def test_example" in result
        service.model.generate_content.assert_called_once()

    def test_generate_test_code_empty_input(self, service):
        """빈 입력에 대한 처리를 테스트합니다."""
        result = service.generate_test_code("")
        assert "소스 코드" in result or "입력" in result

    @patch("src.services.gemini_service.genai.GenerativeModel")
    def test_generate_test_code_api_error(self, mock_model_class, service):
        """API 오류 발생 시 재시도 로직을 테스트합니다."""
        # tenacity의 stop_after_attempt(3): 최대 3번 시도 (초기 1회 + 재시도 2회)
        service.model.generate_content = MagicMock(
            side_effect=Exception("API Error")
        )
        
        # 재시도 후 최종 실패 예상
        with pytest.raises(Exception):
            service.generate_test_code("def test(): pass")
        
        # stop_after_attempt(3) = 총 3번 호출
        assert service.model.generate_content.call_count == 3

    @patch("src.services.gemini_service.genai.GenerativeModel")
    def test_generate_test_code_empty_response(self, mock_model_class, service):
        """API가 빈 응답을 반환할 때의 처리를 테스트합니다."""
        mock_response = MagicMock()
        mock_response.text = ""
        
        service.model.generate_content = MagicMock(return_value=mock_response)
        
        result = service.generate_test_code("def test(): pass")
        
        assert "응답" in result or "생성하지 못" in result
