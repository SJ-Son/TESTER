def test_health_check(client):
    """Verify the API health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_code_api(client, mock_user_auth, mock_turnstile_success):
    """Verify the streaming API works and returns raw text."""
    from unittest.mock import MagicMock

    mock_service = MagicMock()

    async def mock_async_generator(*args, **kwargs):
        yield "public class "
        yield "Test {}"

    # Service layer method is generate_test
    # side_effect에 비동기 제너레이터 함수를 할당하면 호출 시 코루틴/제너레이터를 반환
    mock_service.generate_test.side_effect = mock_async_generator

    # Override dependency
    from src.api.v1.deps import get_test_generator_service
    from src.main import app

    app.dependency_overrides[get_test_generator_service] = lambda: mock_service

    payload = {
        "input_code": "class Test {}",
        "language": "Java",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake_token",
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = "".join(response.iter_text())
        # Validate SSE format presence
        assert 'data: {"type": "chunk", "content": "public class "}' in content
        assert 'data: {"type": "chunk", "content": "Test {}"}' in content


def test_validation_error(client, mock_user_auth, mock_turnstile_success):
    """Verify invalid code returns a raw error message."""
    from unittest.mock import MagicMock

    from src.exceptions import ValidationError

    mock_service = MagicMock()

    # Mock validation error during generation
    async def mock_error_gen(*args, **kwargs):
        if False:
            yield  # make it async generator
        raise ValidationError("Invalid Code Pattern", "INVALID_CODE")

    mock_service.generate_test.side_effect = mock_error_gen

    from src.api.v1.deps import get_test_generator_service
    from src.main import app

    app.dependency_overrides[get_test_generator_service] = lambda: mock_service

    payload = {
        "input_code": "Just some random text",
        "language": "Python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake_token",
    }

    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200
        content = response.read().decode()
        assert "error" in content.lower()
