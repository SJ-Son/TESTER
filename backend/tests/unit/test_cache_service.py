from unittest.mock import Mock, patch

import pytest
from src.exceptions import CacheError
from src.services.cache_service import CacheService
from src.types import CacheMetadata


@pytest.fixture
def mock_redis():
    # Clear the singleton instance before each test
    from src.services.cache_service import RedisConnectionManager

    RedisConnectionManager._instance = None
    RedisConnectionManager._redis = None

    with patch("redis.from_url") as mock_from_url:
        mock_client = Mock()
        # Mock ping for _verify_connection
        mock_client.ping.return_value = True
        mock_from_url.return_value = mock_client
        yield mock_client

    # Clear it after test too
    RedisConnectionManager._instance = None
    RedisConnectionManager._redis = None


def test_cache_service_init(mock_redis):
    CacheService(redis_url="redis://test:6379")
    # CacheService no longer has ttl attribute (uses strategy-based TTL)
    mock_redis.ping.assert_not_called()  # Removed ping on init for performance


def test_get_success(mock_redis):
    service = CacheService()
    mock_redis.get.return_value = "cached_value"

    result = service.get("test_key")

    assert result == "cached_value"
    mock_redis.get.assert_called_with("test_key")


def test_get_failure(mock_redis):
    service = CacheService()
    import redis

    mock_redis.get.side_effect = redis.RedisError("Redis error")

    # After refactoring, errors are raised, not silently returned as None
    with pytest.raises(CacheError):
        service.get("test_key")


def test_set_success(mock_redis):
    service = CacheService()
    mock_redis.setex.return_value = True

    # After refactoring, set() returns None
    result = service.set("test_key", "value", ttl=100)

    assert result is None
    mock_redis.setex.assert_called_with("test_key", 100, "value")


def test_generate_key(mock_redis):
    service = CacheService()

    # After refactoring, generate_key returns CacheMetadata object
    # Note: strategy parameter defaults to "gemini"
    metadata1 = service.generate_key("model", "code", "instruction")
    metadata2 = service.generate_key("model", "code", "instruction")
    metadata3 = service.generate_key("other", "code", "instruction")

    # Check that keys are CacheMetadata objects
    assert isinstance(metadata1, CacheMetadata)
    assert isinstance(metadata2, CacheMetadata)
    assert isinstance(metadata3, CacheMetadata)

    # Keys should be consistent for same inputs
    assert metadata1.key == metadata2.key
    assert metadata1.key != metadata3.key

    # TTL should be set
    assert metadata1.ttl > 0
