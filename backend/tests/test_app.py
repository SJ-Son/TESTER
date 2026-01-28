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
        mock_generate.return_value = "def test_mock(): pass"
        
        at = AppTest.from_file("src/app.py")
        at.run()
        
        at.text_area[0].input("def foo(): pass").run()
        at.button[0].click().run()
        
        assert len(at.success) > 0
        assert len(at.code) > 0
        assert "def test_mock(): pass" in at.code[0].value

    def test_invalid_python_code(self):
        """유효하지 않은 파이썬 문법 입력 시 경고 메시지 확인."""
        at = AppTest.from_file("src/app.py")
        at.run()
        
        # 괄호가 닫히지 않은 문법 오류 코드
        at.text_area[0].input("def foo(: print('error')").run()
        at.button[0].click().run()
        
        assert len(at.warning) > 0
        assert "문법을 확인해주세요" in at.warning[0].value

    def test_rate_limit(self):
        """짧은 시간 내 재요청 시 경고 메시지 확인."""
        at = AppTest.from_file("src/app.py")
        at.run()
        
        at.text_area[0].input("def foo(): pass").run()
        
        # 첫 번째 클릭 (성공 예상 - Mock이 없으면 에러날 수 있으나 여기선 Rate Limit만 봄)
        # 하지만 실제 서비스 호출 시 에러가 나면 error toast가 뜸.
        # Rate Limit은 서비스 호출 '전'에 체크하므로 
        # 두 번째 클릭에서 warning이 뜨는지 확인.
        
        # 1차 클릭
        at.button[0].click().run()
        
        # 2차 클릭 (즉시 실행)
        at.button[0].click().run()
        
        # 경고 메시지 중 "요청이 너무 빠릅니다"가 있는지 확인
        found = False
        for w in at.warning:
            if "요청이 너무 빠릅니다" in w.value:
                found = True
                break
        assert found
