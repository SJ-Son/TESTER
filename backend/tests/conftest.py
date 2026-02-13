import os

# Set up test environment variables BEFORE imports to pass strict validation
os.environ.setdefault("GEMINI_API_KEY", "AIzaSyDummyTestKey123456789012345678")
# Use memory:// so slowapi/limiter uses MemoryStorage and doesn't connect to Redis
os.environ.setdefault("REDIS_URL", "memory://")
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
from src.auth import get_current_user  # noqa: E402
from src.main import app  # noqa: E402


def pytest_configure(config):
    """Pytest 설정 훅."""
    # Env vars are already set above
    pass


@pytest.fixture(scope="session", autouse=True)
def mock_redis_globally():
    """CI 환경에서 연결 오류를 방지하기 위해 Redis를 전역적으로 모의(Mock)합니다.

    redis.asyncio.from_url을 패치하고 AsyncMock을 반환하며,
    redis.from_url (동기)도 패치하여 Mock을 반환합니다.
    """
    from unittest.mock import AsyncMock, Mock, patch

    # Patch redis.asyncio.from_url (crucial for CacheService which uses memory://)
    with patch("redis.asyncio.from_url") as mock_async_from_url, \
         patch("redis.from_url") as mock_sync_from_url:

        # Async Mock (for CacheService)
        mock_async_client = AsyncMock()
        mock_async_client.ping.return_value = True
        mock_async_client.get.return_value = None
        mock_async_client.setex.return_value = True
        mock_async_client.set.return_value = True
        mock_async_client.keys.return_value = []
        mock_async_client.delete.return_value = True
        mock_async_client.close.return_value = None
        mock_async_from_url.return_value = mock_async_client

        # Sync Mock (for potential sync usage, though limiter should use MemoryStorage)
        mock_sync_client = Mock()
        mock_sync_client.ping.return_value = True
        mock_sync_client.get.return_value = None
        mock_sync_client.setex.return_value = True
        mock_sync_client.incr.return_value = 1
        mock_sync_client.evalsha.return_value = 1
        mock_sync_from_url.return_value = mock_sync_client

        yield mock_async_client


@pytest.fixture
def client():
    """FastAPI TestClient 픽스처."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_overrides():
    """각 테스트 전에 의존성 오버라이드를 초기화합니다."""
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_auth():
    """테스트를 위해 사용자 인증을 오버라이드합니다."""
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "test_user",
        "email": "test@example.com",
    }
    yield
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def mock_turnstile_success():
    """테스트를 위해 Turnstile 검증을 오버라이드합니다."""
    from unittest.mock import patch

    # Mock the direct function call in generator.py
    with patch("src.api.v1.generator.validate_turnstile_token") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture(autouse=True)
def disable_rate_limit():
    """테스트를 위해 속도 제한(Rate Limiting)을 비활성화합니다."""
    from src.api.v1.deps import limiter

    limiter.enabled = False
    yield
    limiter.enabled = True
