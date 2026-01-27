import pytest
from unittest.mock import MagicMock, patch
from src.services.gemini_service import GeminiService

class TestGeminiService:
    """
    GeminiService 클래스의 단위 테스트입니다.
    외부 API 호출은 Mocking하여 비용 발생을 방지합니다.
    """

    @pytest.fixture
    def mock_genai(self, mocker):
        """
        google.generativeai 모듈 전체를 Mocking합니다.
        """
        return mocker.patch("src.services.gemini_service.genai")

    @pytest.fixture
    def service(self, mock_genai):
        """
        GeminiService 인스턴스를 생성하는 Fixture입니다.
        Settings.GEMINI_API_KEY가 필요하므로 환경 변수도 Mock 처리할 수 있으나,
        여기서는 __init__에서 API 설정을 하므로 mock_genai가 먼저 적용되어야 합니다.
        """
        return GeminiService()

    def test_configure_api_called(self, mock_genai):
        """
        서비스 초기화 시 API 설정(configure)이 호출되는지 확인합니다.
        """
        GeminiService()
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once()

    def test_generate_test_code_success(self, service, mock_genai):
        """
        정상적으로 코드가 입력되었을 때 API 응답을 반환하는지 테스트합니다.
        """
        # Mock Response 설정
        mock_response = MagicMock()
        mock_response.text = "```python\ndef test_example(): pass\n```"
        
        # model.generate_content 메서드의 리턴값 설정
        service.model.generate_content.return_value = mock_response

        input_code = "def example(): pass"
        result = service.generate_test_code(input_code)

        # 검증
        service.model.generate_content.assert_called_once_with(input_code)
        assert result == mock_response.text

    def test_generate_test_code_empty_input(self, service):
        """
        빈 문자열이 입력되었을 때 API 호출을 하지 않고 경고 메시지를 반환하는지 테스트합니다.
        """
        input_code = "   "
        result = service.generate_test_code(input_code)

        # API 호출이 없어야 함
        service.model.generate_content.assert_not_called()
        assert "입력해주세요" in result

    def test_generate_test_code_api_error(self, service):
        """
        API 호출 중 예외가 발생했을 때 적절히 전파되는지 테스트합니다.
        """
        service.model.generate_content.side_effect = Exception("API Error")

        with pytest.raises(Exception) as excinfo:
            service.generate_test_code("print('hello')")
        
        assert "API Error" in str(excinfo.value)
