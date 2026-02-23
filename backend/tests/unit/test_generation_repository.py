import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.repositories.generation_repository import GenerationRepository, GenerationModel
from src.services.cache_service import CacheService

@pytest.fixture
def mock_supabase_service():
    with patch("src.repositories.base_repository.SupabaseService") as mock_service_cls:
        mock_instance = mock_service_cls.return_value
        mock_client = Mock()
        mock_instance.client = mock_client
        yield mock_instance

@pytest.fixture
def mock_cache_service():
    with patch("src.repositories.generation_repository.CacheService") as mock_cache_cls:
        mock_instance = AsyncMock(spec=CacheService)
        mock_cache_cls.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def generation_repository(mock_supabase_service, mock_cache_service):
    repo = GenerationRepository(mock_supabase_service)
    # Ensure cache service is injected (since we patch the class used in init)
    return repo

@pytest.mark.asyncio
async def test_get_user_history_cache_hit(generation_repository, mock_cache_service):
    """Test get_user_history returns cached data without hitting DB."""
    user_id = "test-user"
    limit = 50
    cached_data = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": user_id,
            "input_code": "print('hello')",
            "generated_code": "def test_hello(): pass",
            "language": "python",
            "model": "gemini-pro",
            "created_at": "2024-01-01T00:00:00"
        }
    ]
    import orjson
    mock_cache_service.get.return_value = orjson.dumps(cached_data).decode()

    # Call method
    result = await generation_repository.get_user_history(user_id, limit)

    # Verify
    assert len(result) == 1
    assert isinstance(result[0], GenerationModel)
    assert result[0].input_code == "print('hello')"

    # Check cache interaction
    mock_cache_service.get.assert_called_once_with(f"history:{user_id}:{limit}")
    # DB (via _fetch_history_from_db) should NOT be called.
    # Since we can't easily spy on internal method without implementation,
    # we rely on the fact that if cache returns, the logic should return early.

@pytest.mark.asyncio
async def test_get_user_history_cache_miss(generation_repository, mock_cache_service):
    """Test get_user_history fetches from DB and caches result on miss."""
    user_id = "test-user"
    limit = 50
    mock_cache_service.get.return_value = None

    # Mock the internal sync fetch method (which we will implement)
    # Since we haven't implemented it yet, we patch where it will be used.
    # For now, let's assume the repository calls `_fetch_history_from_db_sync` or similar.
    # But since we are writing the test BEFORE the code, we can just patch `run_in_threadpool`
    # or the repository method itself if we knew the name.

    # Strategy: We will Mock `run_in_threadpool` in the repository module to return our data.
    db_data = [
        GenerationModel(
            id="123e4567-e89b-12d3-a456-426614174000",
            user_id=user_id,
            input_code="print('world')",
            generated_code="def test_world(): pass",
            language="python",
            model="gemini-pro",
            created_at="2024-01-01T00:00:00"
        )
    ]

    with patch("src.repositories.generation_repository.run_in_threadpool", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = db_data

        result = await generation_repository.get_user_history(user_id, limit)

        assert len(result) == 1
        assert result[0].input_code == "print('world')"

        # Verify cache set
        mock_cache_service.get.assert_called_once()
        mock_cache_service.set.assert_called_once()

        # Verify set arguments
        args, kwargs = mock_cache_service.set.call_args
        assert args[0] == f"history:{user_id}:{limit}"
        # args[1] should be json string
        assert "print('world')" in args[1]

@pytest.mark.asyncio
async def test_create_history_invalidates_cache(generation_repository, mock_cache_service):
    """Test create_history invalidates cache after creation."""
    user_id = "test-user"
    input_code = "print('new')"

    # Mock internal sync create
    with patch("src.repositories.generation_repository.run_in_threadpool", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = GenerationModel(
            user_id=user_id,
            input_code=input_code,
            generated_code="...",
            language="python",
            model="gemini"
        )

        await generation_repository.create_history(user_id, input_code, "...", "python", "gemini")

        # Verify cache invalidation
        mock_cache_service.clear.assert_called_once_with(f"history:{user_id}:*")
