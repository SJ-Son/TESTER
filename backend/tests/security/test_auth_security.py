from unittest.mock import AsyncMock, patch

from src.config.settings import settings
from src.exceptions import TurnstileError

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


def test_turnstile_failure(client, mock_user_auth):
    """Turnstile 검증 실패 시 400 에러가 발생하는지 확인."""
    # Patch the direct function call to raise TurnstileError
    with patch("src.api.v1.generator.validate_turnstile_token", side_effect=TurnstileError()):
        payload = {
            "input_code": "def foo(): pass",
            "language": "python",
            "model": "gemini-3-flash-preview",
            "turnstile_token": "bad_token",
        }
        response = client.post("/api/generate", json=payload)

        # 400 Bad Request is returned by exception handler
        assert response.status_code == 400


def test_rate_limiting(client, mock_user_auth, mock_turnstile_success):
    """짧은 시간 내 5회 초과 요청 시 429 에러가 발생하는지 확인."""
    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake",
    }

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
    headers = {"Authorization": "Bearer dummy_token"}
    for _ in range(10):
        res = client.post("/api/generate", json=payload, headers=headers)
        if res.status_code == 429:
            found_429 = True
            break
        # Might return 200 (stream) or 429

    assert found_429 is True
