from unittest.mock import patch

from fastapi.testclient import TestClient
from src.main import app

# Mock Redis to avoid needing a real Redis instance for unit tests
# We patch the Limiter's storage or the rate limit mechanism if possible
# But slowapi is hard to mock without a real storage or memory storage.
# For simplicity in this environment, we might skip strict Redis verification here
# and focus on Content-Length and overall error handling.

client = TestClient(app)


def test_content_length_limit():
    # Test with a header indicating large content
    # Note: TestClient might not strictly enforce this as a real server would,
    # but the middleware reads the header.

    headers = {"Content-Length": str(15 * 1024 * 1024)}  # 15MB
    response = client.post("/api/generate", headers=headers, json={})

    # Expect 413 Payload Too Large
    assert response.status_code == 413
    assert response.json() == {"detail": "Request entity too large"}


def test_content_length_within_limit():
    headers = {"Content-Length": str(1024)}  # 1KB
    # This will fail with 404 or something else because we aren't sending valid auth/data
    # but it shouldn't be 413.
    response = client.post("/api/generate", headers=headers, json={})
    assert response.status_code != 413


@patch("src.main.logger")
def test_global_exception_handler_strips_details(mock_logger):
    # Simulate an internal error
    # We can do this by mocking a dependency to raise an exception

    with patch("src.main.api_router", side_effect=Exception("Database Connection Failed")):
        # This is hard to trigger from outside without a known crashing endpoint.
        # Let's try to access an endpoint that might crash if we mock something deep.
        pass

    # Alternatively, defined a route that crashes
    @app.get("/force_error")
    def force_error():
        raise Exception("Super Secret Database Info")

    # Use a local client with raise_server_exceptions=False to test the handler
    with TestClient(app, raise_server_exceptions=False) as local_client:
        response = local_client.get("/force_error")
        assert response.status_code == 500
        data = response.json()
        assert data["message"] == "Internal Server Error"
        assert data["code"] == "INTERNAL_ERROR"
        assert "Super Secret Database Info" not in str(data)  # Ensure no leak
