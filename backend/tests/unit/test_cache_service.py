from unittest.mock import Mock, patch

import pytest
from src.exceptions import CacheError
from src.services.cache_service import CacheService, _redis_clients


@pytest.fixture
def mock_redis():
    # Clear the global cache before each test
    _redis_clients.clear()

    # Need to patch redis.from_url where it is used in cache_service.py
    with patch("src.services.cache_service.redis.from_url") as mock_from_url:
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        yield mock_client

    # Clear it after test too
    _redis_clients.clear()


def test_cache_service_init(mock_redis):
    service = CacheService(redis_url="redis://test:6379", ttl=3600)
    assert service.default_ttl == 3600
    mock_redis.ping.assert_called_once()


def test_get_success(mock_redis):
    service = CacheService()
    service.redis_client.get.return_value = "cached_value"

    result = service.get("test_key")

    assert result == "cached_value"
    service.redis_client.get.assert_called_with("test_key")


def test_get_failure(mock_redis):
    service = CacheService()
    import redis

    service.redis_client.get.side_effect = redis.RedisError("Redis error")

    with pytest.raises(CacheError, match="캐시 조회 실패"):
        service.get("test_key")


def test_set_success(mock_redis):
    service = CacheService()
    # CacheService.set returns None, not True
    result = service.set("test_key", "value", ttl=100)

    assert result is None
    service.redis_client.setex.assert_called_with("test_key", 100, "value")


def test_generate_key(mock_redis):
    service = CacheService()
    metadata_1 = service.generate_key("model", "code", "instruction")
    metadata_2 = service.generate_key("model", "code", "instruction")
    metadata_3 = service.generate_key("other", "code", "instruction")

    assert metadata_1.key == metadata_2.key
    assert metadata_1.key != metadata_3.key
    assert metadata_1.ttl > 0
