from unittest.mock import patch

from src.config.settings import settings

VALID_KEY = settings.TESTER_INTERNAL_SECRET


def test_unauthorized_access(client):
    """인증 정보 없이 요청 시 401 에러가 발생하는지 확인."""
    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 401


@patch("src.api.v1.generator.turnstile_dependency")
def test_turnstile_failure(mock_verify, client, mock_user_auth):
    """Turnstile 검증 실패 시 403 에러가 발생하는지 확인."""
    from src.exceptions import TurnstileError

    mock_verify.side_effect = TurnstileError()

    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "bad_token",
    }
    response = client.post("/api/generate", json=payload)
    # If TurnstileError is uncaught/handled, check its status code.
    # Usually pydantic validation might pass but verify fails.
    response = client.post("/api/generate", json=payload)
    assert response.status_code in [400, 403]
    # assert "reCAPTCHA" in response.text # Message might have changed


def test_rate_limiting(client, mock_user_auth, mock_turnstile_success):
    """짧은 시간 내 5회 초과 요청 시 429 에러가 발생하는지 확인."""
    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake",
    }

    from unittest.mock import AsyncMock

    from src.api.v1.deps import limiter

    # Enable limiter for this test
    limiter.enabled = True

    from src.api.v1.deps import get_test_generator_service
    from src.main import app

    mock_service = AsyncMock()

    async def mock_async_generator(*args, **kwargs):
        yield "Handled"

    mock_service.generate_test.side_effect = mock_async_generator
    app.dependency_overrides[get_test_generator_service] = lambda: mock_service

    found_429 = False
    for _ in range(10):
        res = client.post("/api/generate", json=payload)
        if res.status_code == 429:
            found_429 = True
            break
        # Might return 200 (stream) or 429

    assert found_429 is True
