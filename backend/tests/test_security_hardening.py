import pytest
import time
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.config.settings import settings
from unittest.mock import patch

client = TestClient(app)
VALID_KEY = settings.TESTER_INTERNAL_SECRET

def test_unauthorized_access():
    """인증키 없이 요청 시 401 에러가 발생하는지 확인."""
    payload = {
        "input_code": "def foo(): pass",
        "language": "Python",
        "model": "gemini-3-flash-preview"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["detail"]

def test_authorized_access():
    """올바른 인증키 사용 시 요청이 수락되는지 확인 (Gemini 호출은 Mock)."""
    payload = {
        "input_code": "def foo():\n    return 1",
        "language": "Python",
        "model": "gemini-3-flash-preview"
    }
    headers = {"X-TESTER-KEY": VALID_KEY}
    
    with patch("backend.src.main.gemini_service") as mock_service:
        # Mock generator
        def mock_generator(*args, **kwargs):
            yield "test passed"
        mock_service.generate_test_code.return_value = mock_generator()
        
        response = client.post("/api/generate", json=payload, headers=headers)
        assert response.status_code == 200

def test_input_length_limit():
    """입력 코드가 너무 길면 422 에러가 발생하는지 확인."""
    payload = {
        "input_code": "A" * 10001,  # limit is 10000
        "language": "Python",
        "model": "gemini-3-flash-preview"
    }
    headers = {"X-TESTER-KEY": VALID_KEY}
    response = client.post("/api/generate", json=payload, headers=headers)
    assert response.status_code == 422
    assert "input_code" in response.text

def test_rate_limiting():
    """짧은 시간 내 5회 초과 요청 시 429 에러가 발생하는지 확인."""
    payload = {
        "input_code": "def foo(): pass",
        "language": "Python",
        "model": "gemini-3-flash-preview"
    }
    headers = {"X-TESTER-KEY": VALID_KEY}
    
    # 이 테스트는 실제 limiter의 상태를 건드리므로 주의 필요
    # 5회까지는 성공 (Mock 처리)
    with patch("backend.src.main.gemini_service") as mock_service:
        def mock_generator(*args, **kwargs):
            yield "ok"
        mock_service.generate_test_code.return_value = mock_generator()
        
        for _ in range(5):
            res = client.post("/api/generate", json=payload, headers=headers)
            assert res.status_code == 200
            
        # 6번째 시도
        res = client.post("/api/generate", json=payload, headers=headers)
        assert res.status_code == 429
