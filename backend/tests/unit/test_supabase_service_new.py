from unittest.mock import MagicMock, patch

import pytest
from src.services.supabase_service import SupabaseService


@pytest.fixture
def mock_supabase_client():
    with patch("src.services.supabase_service.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


def test_save_generation_success(mock_supabase_client):
    # Setup
    SupabaseService._instance = None  # Reset singleton
    with patch("src.services.supabase_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "http://test.com"
        mock_settings.SUPABASE_KEY = "key"
        service = SupabaseService()

    mock_table = mock_supabase_client.table.return_value
    mock_insert = mock_table.insert.return_value
    mock_insert.execute.return_value = MagicMock(data=[{"id": "123"}])

    # Test
    result = service.save_generation(
        user_id="user-123",
        input_code="print('hi')",
        generated_code="test_code",
        language="python",
        model="gemini",
    )

    # Verify
    assert result is not None
    mock_supabase_client.table.assert_called_with("generation_history")
    mock_table.insert.assert_called_with(
        {
            "user_id": "user-123",
            "input_code": "print('hi')",
            "generated_code": "test_code",
            "language": "python",
            "model": "gemini",
        }
    )


def test_get_history_success(mock_supabase_client):
    # Setup
    SupabaseService._instance = None
    with patch("src.services.supabase_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "http://test.com"
        mock_settings.SUPABASE_KEY = "key"
        service = SupabaseService()

    mock_table = mock_supabase_client.table.return_value
    mock_select = mock_table.select.return_value
    mock_eq = mock_select.eq.return_value
    mock_order = mock_eq.order.return_value
    mock_limit = mock_order.limit.return_value
    mock_limit.execute.return_value = MagicMock(data=[{"id": "1"}])

    # Test
    history = service.get_history("user-123", limit=10)

    # Verify
    assert len(history) == 1
    mock_limit.execute.assert_called()
