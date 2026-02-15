import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.execution_service import ExecutionService
import httpx

@pytest.mark.asyncio
async def test_execution_service_instantiation_count():
    # Reset Singleton state to ensure test isolation
    ExecutionService._instance = None
    if ExecutionService._client:
        await ExecutionService._client.aclose()
    ExecutionService._client = None

    # Mock httpx.AsyncClient
    with patch("src.services.execution_service.httpx.AsyncClient") as mock_client_cls:
        # Create mock instance
        mock_client_instance = AsyncMock()
        mock_client_cls.return_value = mock_client_instance

        # Setup response object (synchronous mock since it's the result of await)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "output": "test"}
        mock_response.text = "OK"

        # Configure post method
        # AsyncMock.post automatically returns a coroutine.
        # Its return_value is what the coroutine resolves to.
        mock_client_instance.post.return_value = mock_response

        service = ExecutionService()

        # Call execute_code 5 times
        for _ in range(5):
            await service.execute_code("print('hello')", "test", "python")

        # Assert instantiation count
        # Should be called exactly once (Singleton init)
        print(f"DEBUG: AsyncClient called {mock_client_cls.call_count} times")
        assert mock_client_cls.call_count == 1

        # Verify post was called 5 times
        assert mock_client_instance.post.call_count == 5

        # Cleanup
        await service.close()
