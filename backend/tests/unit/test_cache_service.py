from unittest.mock import Mock, patch

import pytest

from backend.src.services.cache_service import CacheService


@pytest.fixture
def mock_redis():
    with patch("redis.from_url") as mock_from_url:
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        yield mock_client


def test_cache_service_init(mock_redis):
    service = CacheService(redis_url="redis://test:6379", ttl=3600)
    assert service.ttl == 3600
    mock_redis.ping.assert_called_once()


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

    result = service.get("test_key")

    assert result is None


def test_set_success(mock_redis):
    service = CacheService()
    mock_redis.setex.return_value = True

    result = service.set("test_key", "value", ttl=100)

    assert result is True
    mock_redis.setex.assert_called_with("test_key", 100, "value")


def test_generate_key():
    service = CacheService()
    key1 = service.generate_key("model", "code", "instruction")
    key2 = service.generate_key("model", "code", "instruction")
    key3 = service.generate_key("other", "code", "instruction")

    assert key1 == key2
    assert key1 != key3
