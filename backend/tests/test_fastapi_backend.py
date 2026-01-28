import pytest
from fastapi.testclient import TestClient
# We run from the root, so we import backend.src.main
from backend.src.main import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_health_check():
    """Verify the API health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("backend.src.main.gemini_service")
def test_generate_code_api(mock_service):
    """Verify the streaming API works and returns raw text."""
    # Mocking generator
    def mock_generator(*args, **kwargs):
        yield "public class "
        yield "Test {}"
    
    mock_service.generate_test_code.return_value = mock_generator()
    mock_service.model_name = "gemini-3-flash-preview"

    payload = {
        "input_code": "class Test {}",
        "language": "Java",
        "model": "gemini-3-flash-preview",
        "use_reflection": False
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        # Check if we get text stream
        content = ""
        for chunk in response.iter_text():
            content += chunk
        
        # Verify Content is raw text, not HTML
        assert "public class Test {}" in content
        assert "<div>" not in content

@patch("backend.src.main.gemini_service")
def test_validation_error(mock_service):
    """Verify invalid code returns a raw error message."""
    payload = {
        "input_code": "Just some random text",
        "language": "Python",
        "model": "gemini-3-flash-preview"
    }
    
    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = response.read().decode()
        # Should contain ERROR prefix
        assert "ERROR:" in content
