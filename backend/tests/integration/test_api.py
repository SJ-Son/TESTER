from unittest.mock import patch


def test_health_check(client):
    """Verify the API health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("backend.src.main.gemini_service")
def test_generate_code_api(mock_service, client, mock_user_auth, mock_turnstile_success):
    """Verify the streaming API works and returns raw text."""

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
        "turnstile_token": "fake_token",
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = "".join(response.iter_text())
        assert "public class Test {}" in content


@patch("backend.src.main.gemini_service")
def test_validation_error(mock_service, client, mock_user_auth, mock_turnstile_success):
    """Verify invalid code returns a raw error message."""
    payload = {
        "input_code": "Just some random text",
        "language": "Python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake_token",
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = response.read().decode()
        assert "ERROR:" in content
