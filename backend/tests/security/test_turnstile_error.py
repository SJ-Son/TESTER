from unittest.mock import patch

import httpx


async def test_turnstile_http_exception(client, mock_user_auth):
    """Turnstile HTTP 예외가 발생했을 때 500 에러가 아닌 적절한 응답을 반환하는지 테스트합니다."""

    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "valid_token_structure",
    }

    with patch(
        "src.auth.httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection failed")
    ):
        response = client.post("/api/generate", json=payload)

        # 500 에러가 아니어야 함 (Fail Open 또는 클라이언트 에러)
        assert response.status_code != 500
