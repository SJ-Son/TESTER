from unittest.mock import MagicMock, patch

import pytest
from src.services.supabase_service import SupabaseService


@pytest.fixture
def mock_supabase_client():
    with patch("src.services.supabase_service.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def supabase_service(mock_supabase_client):
    with (
        patch("src.config.settings.settings.SUPABASE_URL", "http://test.com"),
        patch("src.config.settings.settings.SUPABASE_SERVICE_ROLE_KEY", "test_key"),
    ):
        service = SupabaseService()
        yield service


def test_check_weekly_quota_success(supabase_service, mock_supabase_client):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.count = 5

    # Mock the chain: table().select().eq().gte().execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = mock_response

    count = supabase_service.check_weekly_quota("user_123")

    assert count == 5
    # Verify chain calls
    mock_supabase_client.table.assert_called_with("generation_history")
    mock_supabase_client.table().select.assert_called_with("id", count="exact", head=True)


def test_check_weekly_quota_error(supabase_service, mock_supabase_client):
    # Mock exception
    mock_supabase_client.table.side_effect = Exception("DB Error")

    count = supabase_service.check_weekly_quota("user_123")

    # Should fail open (return 0) on error
    assert count == 0
