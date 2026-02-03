from unittest.mock import Mock, patch

import pytest

from backend.src.repositories.test_log_repository import TestLogRepository
from backend.src.services.supabase_service import SupabaseService


@pytest.fixture
def mock_supabase_client():
    with patch("backend.src.services.supabase_service.create_client") as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        yield mock_client


def test_supabase_service_init(mock_supabase_client):
    # Mock settings
    with patch("backend.src.services.supabase_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "https://test.supabase.co"
        mock_settings.SUPABASE_KEY = "test-key"

        service = SupabaseService()

        assert service._client is not None
        assert service.is_connected() is True


def test_supabase_service_no_creds():
    with patch("backend.src.services.supabase_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = ""
        mock_settings.SUPABASE_KEY = ""

        service = SupabaseService()

        assert service.is_connected() is False


def test_repository_create(mock_supabase_client):
    # Setup Service with mocked client
    service = Mock(spec=SupabaseService)
    service.client = mock_supabase_client

    repo = TestLogRepository(service)

    # Mock DB Response
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "input_code": "print('hello')",
            "language": "python",
            "model": "gpt-4",
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]

    # Test Create
    result = repo.create_log(None, "print('hello')", "python", "gpt-4")

    assert result is not None
    assert result.input_code == "print('hello')"
    assert str(result.id) == "123e4567-e89b-12d3-a456-426614174000"
