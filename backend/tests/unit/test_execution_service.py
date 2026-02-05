from unittest.mock import MagicMock, patch

import pytest
from src.services.execution_service import ExecutionService


@pytest.fixture
def mock_docker():
    with patch("src.services.execution_service.docker") as mock:
        yield mock


def test_execution_service_initialization(mock_docker):
    service = ExecutionService()
    assert service.client is not None
    mock_docker.from_env.assert_called_once()


def test_execute_code_success(mock_docker):
    service = ExecutionService()
    mock_client = service.client
    mock_container = MagicMock()
    mock_client.containers.run.return_value = mock_container

    # Mock exec_run for file writing (success)
    mock_container.exec_run.side_effect = [
        (0, b""),  # Write file success
        MagicMock(exit_code=0, output=b"test output"),  # Run pytest success
    ]

    result = service.execute_code("print('hello')", "test_code", "python")

    assert result["success"] is True
    assert result["output"] == "test output"
    mock_client.containers.run.assert_called()
    mock_container.kill.assert_called()


def test_execute_code_unsupported_language(mock_docker):
    service = ExecutionService()
    result = service.execute_code("console.log('hi')", "test_code", "javascript")
    assert result["success"] is False
    assert "Only Python is supported" in result["error"]


def test_execute_code_container_failure(mock_docker):
    service = ExecutionService()
    mock_client = service.client
    mock_client.containers.run.side_effect = Exception("Docker error")

    result = service.execute_code("code", "test_code", "python")

    assert result["success"] is False
    assert "Docker error" in result["error"]
