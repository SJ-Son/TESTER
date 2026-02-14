from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from src.api.v1.deps import get_test_generator_service
from src.main import app


def test_global_exception_handler_does_not_leak_details(mock_user_auth, mock_turnstile_success):
    """
    전역 예외 처리기가 일반적인 500 에러를 반환하고,
    내부 예외 메시지(예: 민감한 정보)를 노출하지 않는지 확인합니다.
    """
    client = TestClient(app, raise_server_exceptions=False)

    def mock_dependency_raise():
        raise Exception("SENSITIVE_DB_CONNECTION_STRING_LEAKED")

    app.dependency_overrides[get_test_generator_service] = mock_dependency_raise

    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake_token",
    }

    try:
        response = client.post("/api/generate", json=payload)

        assert response.status_code == 500

        data = response.json()

        assert "SENSITIVE_DB_CONNECTION_STRING_LEAKED" not in str(data), (
            f"VULNERABILITY DETECTED: Sensitive info leaked in error response: {data}"
        )

    finally:
        if get_test_generator_service in app.dependency_overrides:
            del app.dependency_overrides[get_test_generator_service]


def test_streaming_error_does_not_leak_details(mock_user_auth, mock_turnstile_success):
    """
    스트리밍 중에 예외가 발생해도 민감한 정보가 노출되지 않는지 확인합니다.
    """
    client = TestClient(app, raise_server_exceptions=False)

    mock_service = MagicMock()

    async def mock_generate_stream(*args, **kwargs):
        yield "chunk1"
        raise Exception("SENSITIVE_STREAM_ERROR")

    mock_service.generate_test.side_effect = mock_generate_stream

    app.dependency_overrides[get_test_generator_service] = lambda: mock_service

    payload = {
        "input_code": "def foo(): pass",
        "language": "python",
        "model": "gemini-3-flash-preview",
        "turnstile_token": "fake_token",
    }

    try:
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 200

        content = response.text
        assert "chunk1" in content
        assert "error" in content

        assert "SENSITIVE_STREAM_ERROR" not in content, (
            f"VULNERABILITY DETECTED: Sensitive info leaked in stream error: {content}"
        )

    finally:
        if get_test_generator_service in app.dependency_overrides:
            del app.dependency_overrides[get_test_generator_service]
