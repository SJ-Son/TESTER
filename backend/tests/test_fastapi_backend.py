import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth import get_current_user, verify_recaptcha
from unittest.mock import MagicMock, patch, AsyncMock

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_overrides():
    # Clear overrides before each test
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}

def test_health_check():
    """Verify the API health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("backend.src.main.gemini_service")
def test_generate_code_api(mock_service):
    """Verify the streaming API works and returns raw text."""
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: {"id": "test_user", "email": "test@example.com"}
    app.dependency_overrides[verify_recaptcha] = lambda: True

    # Mocking async generator
    async def mock_async_generator(*args, **kwargs):
        yield "public class "
        yield "Test {}"
    
    mock_service.generate_test_code.return_value = mock_async_generator()
    mock_service.model_name = "gemini-3-flash-preview"

    payload = {
        "input_code": "class Test {}",
        "language": "Java",
        "model": "gemini-3-flash-preview",
        "recaptcha_token": "fake_token"
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = "".join(response.iter_text())
        assert "public class Test {}" in content

@patch("backend.src.main.gemini_service")
def test_validation_error(mock_service):
    """Verify invalid code returns a raw error message."""
    app.dependency_overrides[get_current_user] = lambda: {"id": "test_user", "email": "test@example.com"}
    app.dependency_overrides[verify_recaptcha] = lambda: True

    payload = {
        "input_code": "Just some random text",
        "language": "Python",
        "model": "gemini-3-flash-preview",
        "recaptcha_token": "fake_token"
    }
    
    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = response.read().decode()
        assert "ERROR:" in content
