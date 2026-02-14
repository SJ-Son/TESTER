from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr
from src.services.supabase_service import SupabaseService


@pytest.fixture
def mock_supabase_client():
    with patch("src.services.supabase_service.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_cache_service():
    with patch("src.services.supabase_service.CacheService") as mock_cache_cls:
        mock_cache_instance = MagicMock()
        # Ensure async methods are AsyncMock
        mock_cache_instance.get = AsyncMock(return_value=None)  # Default: cache miss
        mock_cache_instance.set = AsyncMock()
        mock_cache_cls.return_value = mock_cache_instance
        yield mock_cache_instance


@pytest.fixture
def supabase_service(mock_supabase_client, mock_cache_service):
    # Reset singleton
    SupabaseService._instance = None
    SupabaseService._client = None
    SupabaseService._cache = None

    with (
        patch("src.config.settings.settings.SUPABASE_URL", "http://test.com"),
        patch("src.config.settings.settings.SUPABASE_SERVICE_ROLE_KEY", SecretStr("test_key")),
    ):
        service = SupabaseService()
        yield service


@pytest.mark.asyncio
async def test_get_weekly_quota_cache_hit(
    supabase_service, mock_cache_service, mock_supabase_client
):
    """캐시 적중 시 DB 조회 없이 캐시된 값을 반환해야 함"""
    # Setup cache hit
    mock_cache_service.get.return_value = "10"

    count = await supabase_service.get_weekly_quota("user_123")

    assert count == 10
    mock_cache_service.get.assert_awaited_once()
    # DB access should NOT happen
    mock_supabase_client.table.assert_not_called()


@pytest.mark.asyncio
async def test_get_weekly_quota_cache_miss_db_success(
    supabase_service, mock_cache_service, mock_supabase_client
):
    """캐시 미스 시 DB에서 조회하고 캐시에 저장해야 함"""
    # Setup cache miss
    mock_cache_service.get.return_value = None

    # Setup DB response
    mock_response = MagicMock()
    mock_response.count = 5
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = mock_response

    count = await supabase_service.get_weekly_quota("user_123")

    assert count == 5
    # Verify DB called
    mock_supabase_client.table.assert_called_with("generation_history")
    # Verify cache set called
    mock_cache_service.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_weekly_quota_db_error(
    supabase_service, mock_cache_service, mock_supabase_client
):
    """DB 오류 시 예외가 발생해야 함"""
    # Setup cache miss
    mock_cache_service.get.return_value = None

    # Setup DB error
    mock_supabase_client.table.side_effect = Exception("DB Error")

    with pytest.raises(Exception, match="DB Error"):
        await supabase_service.get_weekly_quota("user_123")
