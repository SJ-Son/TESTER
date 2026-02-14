from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_user_identifier():
    """Rate Limiting 사용자 식별 로직 테스트.

    인증된 사용자는 ID, 비로그인 사용자는 IP를 반환하는지 검증합니다.
    """
    from unittest.mock import MagicMock, patch

    from fastapi import Request
    from src.api.v1.deps import get_user_identifier

    request = MagicMock(spec=Request)
    request.state.user = {"id": "123"}
    assert get_user_identifier(request) == "user_123"

    request.state.user = None
    with patch("src.api.v1.deps.get_remote_address", return_value="1.2.3.4"):
        assert get_user_identifier(request) == "1.2.3.4"


def test_encryption_service():
    """EncryptionService 암호화/복호화 기능 테스트.

    정상적인 암호화/복호화 동작과 빈 문자열 처리를 검증합니다.
    """
    from unittest.mock import patch

    from cryptography.fernet import Fernet
    from src.utils.security import EncryptionService

    key = Fernet.generate_key().decode()

    with patch(
        "src.config.settings.settings.DATA_ENCRYPTION_KEY.get_secret_value", return_value=key
    ):
        service = EncryptionService()

        original = "my_secret_data"
        encrypted = service.encrypt(original)
        assert encrypted != original
        assert service.decrypt(encrypted) == original

        assert service.encrypt("") == ""
        assert service.decrypt("") == ""


def test_content_length_limit():
    headers = {"Content-Length": str(15 * 1024 * 1024)}  # 15MB
    response = client.post("/api/generate", headers=headers, json={})

    assert response.status_code == 413
    assert response.json() == {"detail": "Request entity too large"}


def test_content_length_within_limit():
    headers = {"Content-Length": str(1024)}  # 1KB
    response = client.post("/api/generate", headers=headers, json={})
    assert response.status_code != 413


@patch("src.main.logger")
def test_global_exception_handler_strips_details(mock_logger):
    with patch("src.main.api_router", side_effect=Exception("Database Connection Failed")):
        pass

    @app.get("/force_error")
    def force_error():
        raise Exception("Super Secret Database Info")

    with TestClient(app, raise_server_exceptions=False) as local_client:
        response = local_client.get("/force_error")
        assert response.status_code == 500
        data = response.json()
        assert data["message"] == "Internal Server Error"
        assert data["code"] == "INTERNAL_ERROR"
        assert "Super Secret Database Info" not in str(data)  # Ensure no leak


@pytest.mark.asyncio
async def test_api_key_verification():
    """API 키 인증 로직 및 Timing Attack 방지 테스트.

    유효한 키, 잘못된 키, 빈 키에 대한 검증을 수행합니다.
    """
    from fastapi import HTTPException
    from src.api.v1.deps import verify_api_key
    from src.config.settings import settings

    valid_key = settings.TESTER_INTERNAL_SECRET.get_secret_value()

    result = await verify_api_key(valid_key)
    assert result == valid_key

    with pytest.raises(HTTPException) as exc:
        await verify_api_key("wrong_key")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Unauthorized: Invalid Internal API Key"

    with pytest.raises(HTTPException) as exc:
        await verify_api_key("")
    assert exc.value.status_code == 401

    with pytest.raises(HTTPException) as exc:
        await verify_api_key(None)
    assert exc.value.status_code == 401
