from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.repositories.generation_repository import GenerationRepository


@pytest.fixture
def mock_supabase_service():
    # Patch where BaseRepository imports it
    with patch("src.repositories.base_repository.SupabaseService") as mock:
        yield mock

@pytest.fixture
def mock_cache_service():
    # Patch where GenerationRepository imports it
    with patch("src.repositories.generation_repository.CacheService") as mock:
        instance = mock.return_value
        instance.get = AsyncMock(return_value=None)
        instance.set = AsyncMock()
        instance.clear = AsyncMock()
        instance.incr = AsyncMock(return_value=1)
        yield instance

@pytest.fixture
def repo(mock_supabase_service, mock_cache_service):
    # Patch EncryptionService to avoid errors
    with patch("src.repositories.generation_repository.EncryptionService"):
        # We need to mock the client on the SupabaseService instance
        mock_client = MagicMock()
        mock_instance = mock_supabase_service.return_value
        mock_instance.client = mock_client

        # GenerationRepository expects an argument but passes it to nothing?
        # Actually GenerationRepository.__init__ calls super().__init__ which doesn't take the service.
        # But GenerationRepository takes it in __init__.
        # We pass the mock instance.
        return GenerationRepository(mock_instance)

@pytest.mark.asyncio
async def test_get_user_history_uses_versioned_key(repo, mock_cache_service):
    # Setup
    user_id = "test_user"

    async def get_side_effect(key):
        if key.startswith("version:"):
            return "5"
        return None

    mock_cache_service.get.side_effect = get_side_effect

    # Mock run_in_threadpool to avoid DB call for history retrieval
    with patch("src.repositories.generation_repository.run_in_threadpool", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = [] # Return empty list

        # Act
        await repo.get_user_history(user_id)

    # Assert
    # This assertion expects the NEW behavior
    mock_cache_service.get.assert_any_call(f"version:history:{user_id}")
    mock_cache_service.get.assert_any_call(f"history:{user_id}:v:5:limit:50")

@pytest.mark.asyncio
async def test_create_history_increments_version(repo, mock_cache_service):
    # Setup
    user_id = "test_user"

    # Act
    with patch("src.repositories.generation_repository.run_in_threadpool", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = MagicMock()
        await repo.create_history(user_id, "input", "output", "python", "model")

    # Assert
    # This assertion expects the NEW behavior
    mock_cache_service.incr.assert_called_with(f"version:history:{user_id}")
    # Ensure we are NOT calling clear anymore
    mock_cache_service.clear.assert_not_called()
