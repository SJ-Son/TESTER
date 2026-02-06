from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.services.execution_service import ExecutionService


@pytest.fixture
def mock_httpx_client():
    with patch("src.services.execution_service.httpx.AsyncClient") as mock:
        yield mock


@pytest.mark.asyncio
async def test_execution_service_initialization():
    service = ExecutionService()
    assert service.worker_url is not None


@pytest.mark.asyncio
async def test_execute_code_success(mock_httpx_client):
    service = ExecutionService()

    # Mock response (MagicMock because json() is synchronous)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "output": "test output", "error": ""}

    # Setup context manager mock
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

    result = await service.execute_code("print('hello')", "test_code", "python")

    assert result["success"] is True
    assert result["output"] == "test output"
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_execute_code_unsupported_language(mock_httpx_client):
    service = ExecutionService()

    # Mock response for unsupported language from worker
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": False,
        "error": "Language runner not implemented for javascript",
        "output": ""
    }

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

    result = await service.execute_code("console.log('hi')", "test_code", "javascript")

    assert result["success"] is False
    assert "Language runner not implemented" in result["error"]


@pytest.mark.asyncio
async def test_execute_code_worker_failure(mock_httpx_client):
    service = ExecutionService()

    # Mock response error
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

    result = await service.execute_code("code", "test_code", "python")

    assert result["success"] is False
    assert "Execution worker returned error" in result["error"]
