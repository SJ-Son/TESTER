import os

# Set up test environment variables BEFORE imports to pass strict validation
os.environ.setdefault("GEMINI_API_KEY", "AIzaSyDummyTestKey123456789012345678")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("TURNSTILE_SECRET_KEY", "test_turnstile_key")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test_supabase_key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test_service_role_key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test_jwt_secret_min_32_chars_len!")
# Valid Fernet key generated with Fernet.generate_key()
os.environ.setdefault("DATA_ENCRYPTION_KEY", "6J5FNvK8aF2hq0rP3xZ9yWcN7dB1mT4vL8jG2kH5sX0=")
os.environ.setdefault("TESTER_INTERNAL_SECRET", "test_internal_secret")
# Disable worker auth enforce for backend tests, although backend doesn't use it directly
os.environ.setdefault("DISABLE_WORKER_AUTH", "true")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from src.auth import get_current_user, verify_turnstile  # noqa: E402
from src.main import app  # noqa: E402


def pytest_configure(config):
    """Pytest configuration hook."""
    # Env vars are already set above
    pass


@pytest.fixture(scope="session", autouse=True)
def mock_redis_globally():
    """Mock Redis globally for all tests to prevent connection errors in CI."""
    from unittest.mock import Mock, patch

    with patch("redis.from_url") as mock_from_url:
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.setex.return_value = True
        mock_from_url.return_value = mock_client
        yield mock_client


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_overrides():
    """Clear dependency overrides before each test."""
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_auth():
    """Override user authentication for testing."""
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "test_user",
        "email": "test@example.com",
    }
    yield
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def mock_turnstile_success():
    """Override Turnstile verification for testing."""
    app.dependency_overrides[verify_turnstile] = lambda: True
    yield
    if verify_turnstile in app.dependency_overrides:
        del app.dependency_overrides[verify_turnstile]


@pytest.fixture(autouse=True)
def disable_rate_limit():
    """Disable rate limiting for tests."""
    from src.api.v1.deps import limiter

    limiter.enabled = False
    yield
    limiter.enabled = True
