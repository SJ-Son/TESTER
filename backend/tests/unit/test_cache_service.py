from unittest.mock import AsyncMock, patch

import pytest
import redis.asyncio as redis
from src.exceptions import CacheError
from src.services.cache_service import CacheService, RedisConnectionManager
from src.types import CacheMetadata


@pytest.fixture
def mock_redis():
    RedisConnectionManager._instance = None
    RedisConnectionManager._client = None

    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client
        yield mock_client

    RedisConnectionManager._instance = None
    RedisConnectionManager._client = None


def test_cache_service_init(mock_redis):
    CacheService(redis_url="redis://test:6379")
    mock_redis.ping.assert_not_called()  # Removed ping on init for performance


@pytest.mark.asyncio
async def test_get_success(mock_redis):
    service = CacheService()
    mock_redis.get.return_value = "cached_value"

    result = await service.get("test_key")

    assert result == "cached_value"
    mock_redis.get.assert_awaited_with("test_key")


@pytest.mark.asyncio
async def test_get_failure(mock_redis):
    service = CacheService()
    mock_redis.get.side_effect = redis.RedisError("Redis error")

    with pytest.raises(CacheError):
        await service.get("test_key")


@pytest.mark.asyncio
async def test_set_success(mock_redis):
    service = CacheService()
    mock_redis.setex.return_value = True

    result = await service.set("test_key", "value", ttl=100)

    assert result is None
    mock_redis.setex.assert_awaited_with("test_key", 100, "value")


@pytest.mark.asyncio
async def test_clear_success(mock_redis):
    service = CacheService()
    mock_redis.keys.return_value = ["key1", "key2"]

    await service.clear("pattern*")

    mock_redis.keys.assert_awaited_with("pattern*")
    mock_redis.delete.assert_awaited_with("key1", "key2")


@pytest.mark.asyncio
async def test_ping_success(mock_redis):
    service = CacheService()
    mock_redis.ping.return_value = True

    result = await service.ping()

    assert result is True
    mock_redis.ping.assert_awaited_once()


def test_generate_key(mock_redis):
    service = CacheService()

    metadata1 = service.generate_key("model", "code", "instruction")
    metadata2 = service.generate_key("model", "code", "instruction")
    metadata3 = service.generate_key("other", "code", "instruction")

    assert isinstance(metadata1, CacheMetadata)
    assert isinstance(metadata2, CacheMetadata)
    assert isinstance(metadata3, CacheMetadata)

    assert metadata1.key == metadata2.key
    assert metadata1.key != metadata3.key

    assert metadata1.ttl > 0
