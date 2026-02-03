from unittest.mock import patch

from backend.src.config.settings import settings

VALID_KEY = settings.TESTER_INTERNAL_SECRET


def test_unauthorized_access(client):
    """인증 정보 없이 요청 시 401 에러가 발생하는지 확인."""
    payload = {
        "input_code": "def foo(): pass",
        "language": "Python",
        "model": "gemini-3-flash-preview",
        "recaptcha_token": "fake",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 401


@patch("backend.src.main.verify_recaptcha")
def test_recaptcha_failure(mock_verify, client, mock_user_auth):
    """reCAPTCHA 검증 실패 시 403 에러가 발생하는지 확인."""
    mock_verify.return_value = False
    payload = {
        "input_code": "def foo(): pass",
        "language": "Python",
        "model": "gemini-3-flash-preview",
        "recaptcha_token": "bad_token",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 403
    assert "reCAPTCHA" in response.json()["detail"]


def test_rate_limiting(client, mock_user_auth, mock_recaptcha_success):
    """짧은 시간 내 5회 초과 요청 시 429 에러가 발생하는지 확인."""
    # Note: This test can be sensitive if other tests hit the same endpoint.
    payload = {
        "input_code": "def foo(): pass",
        "language": "Python",
        "model": "gemini-3-flash-preview",
        "recaptcha_token": "fake",
    }

    with patch("backend.src.main.gemini_service") as mock_service:

        async def mock_gen(*args, **kwargs):
            yield "ok"

        mock_service.generate_test_code.return_value = mock_gen()

        # We try until it hits 429, instead of assuming we start at 0.
        # But we expect it to hit 429 relatively soon.
        found_429 = False
        for _ in range(10):  # Try up to 10 times to force 429
            res = client.post("/api/generate", json=payload)
            if res.status_code == 429:
                found_429 = True
                break
            assert res.status_code == 200

        assert found_429 is True
