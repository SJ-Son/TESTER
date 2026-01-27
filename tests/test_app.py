from streamlit.testing.v1 import AppTest
import pytest
from unittest.mock import patch

class TestStreamlitApp:
    """Streamlit UI 통합 테스트 (AppTest 사용)."""

    def test_app_smoke(self):
        """앱이 에러 없이 실행되는지 확인 (Smoke Test)."""
        at = AppTest.from_file("src/app.py")
        at.run()
        assert not at.exception
        assert "Code Tester AI" in at.title[0].value

    def test_empty_input_warning(self):
        """빈 입력값에 대해 경고 메시지가 표시되는지 확인."""
        at = AppTest.from_file("src/app.py")
        at.run()
        
        # 버튼 클릭
        at.button[0].click().run()
        
        # 경고 메시지 확인 (warning 요소가 하나 이상 있어야 함)
        assert len(at.warning) > 0
        assert "코드를 입력해주세요" in at.warning[0].value

    @patch("src.services.gemini_service.GeminiService.generate_test_code")
    def test_generate_code_success(self, mock_generate):
        """정상 입력 시 결과가 출력되는지 확인 (Mock 적용)."""
        # Mock 반환값 설정
        mock_generate.return_value = "def test_mock(): pass"
        
        at = AppTest.from_file("src/app.py")
        at.run()
        
        # 텍스트 입력
        at.text_area[0].input("def foo(): pass").run()
        
        # 버튼 클릭 (AppTest 실행 시 import된 모듈의 mock이 적용됨)
        at.button[0].click().run()
        
        # 성공 메시지 및 결과 코드 확인
        assert len(at.success) > 0
        assert len(at.code) > 0
        assert "def test_mock(): pass" in at.code[0].value
