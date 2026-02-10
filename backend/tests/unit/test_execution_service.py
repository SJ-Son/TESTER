"""ExecutionService 단위 테스트."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.services.execution_service import ExecutionService


class TestExecutionService:
    """ExecutionService 테스트 스위트."""

    @pytest.fixture
    def service(self):
        """ExecutionService 인스턴스 생성."""
        with patch.dict(
            "os.environ",
            {"WORKER_URL": "http://test-worker:5000", "WORKER_AUTH_TOKEN": "test-token"},
        ):
            return ExecutionService()

    @pytest.fixture
    def service_no_token(self):
        """인증 토큰 없는 ExecutionService."""
        with patch.dict("os.environ", {"WORKER_URL": "http://test-worker:5000"}, clear=True):
            return ExecutionService()

    # === 정상 실행 테스트 ===

    @pytest.mark.asyncio
    async def test_execute_code_success(self, service):
        """코드 실행 성공 시나리오."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            # Mock response 설정
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(
                return_value={
                    "success": True,
                    "output": "All tests passed!",
                    "exit_code": 0,
                }
            )

            # AsyncClient context manager와 post 메서드 설정
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await service.execute_code(
                input_code="def add(a, b): return a + b",
                test_code="assert add(1, 2) == 3",
                language="python",
            )

            assert result["success"] is True
            assert "passed" in result["output"].lower()
            assert result["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_execute_code_with_auth_token(self, service):
        """인증 토큰이 포함된 요청 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "OK"})

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await service.execute_code("code", "test", "python")

            # Authorization 헤더가 포함되었는지 확인
            call_args = mock_post.call_args
            assert "Authorization" in call_args[1]["headers"]
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_execute_code_without_token(self, service_no_token):
        """인증 토큰 없이 요청 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "OK"})

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await service_no_token.execute_code("code", "test", "python")

            # Authorization 헤더가 없어야 함
            call_args = mock_post.call_args
            assert "Authorization" not in call_args[1]["headers"]

    # === 에러 처리 테스트 ===

    @pytest.mark.asyncio
    async def test_execute_code_test_failure(self, service):
        """테스트 실패 시나리오."""
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(
                return_value={
                    "success": False,
                    "output": "AssertionError: expected 3, got 4",
                    "exit_code": 1,
                }
            )

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert "AssertionError" in result["output"]
            assert result["exit_code"] == 1

    @pytest.mark.asyncio
    async def test_execute_code_auth_failure_401(self, service):
        """인증 실패 (401) 처리 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert "authentication failed" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_code_auth_failure_403(self, service):
        """권한 부족 (403) 처리 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 403
            mock_response.text = "Forbidden"

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert "authentication failed" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_code_worker_error_500(self, service):
        """Worker 서버 에러 (500) 처리 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert "worker returned error" in result["error"].lower()
            assert "500" in result["output"]

    @pytest.mark.asyncio
    async def test_execute_code_connection_error(self, service):
        """Worker 연결 실패 처리 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert (
                "unavailable" in result["error"].lower()
                or "connection failed" in result["error"].lower()
            )

    @pytest.mark.asyncio
    async def test_execute_code_timeout_error(self, service):
        """타임아웃 에러 처리 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert "unavailable" in result["error"].lower() or "failed" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_code_unexpected_exception(self, service):
        """예상치 못한 예외 처리 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=ValueError("Unexpected error")
            )

            result = await service.execute_code("code", "test", "python")

            assert result["success"] is False
            assert "internal server error" in result["error"].lower()

    # === 다양한 언어 테스트 ===

    @pytest.mark.asyncio
    async def test_execute_javascript_code(self, service):
        """JavaScript 코드 실행 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "Test passed"})

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await service.execute_code("const x = 1;", "assert(x === 1);", "javascript")

            # language 파라미터가 올바르게 전달되었는지 확인
            call_args = mock_post.call_args
            assert call_args[1]["json"]["language"] == "javascript"

    @pytest.mark.asyncio
    async def test_execute_go_code(self, service):
        """Go 코드 실행 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "PASS"})

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await service.execute_code("package main", "// test", "go")

            call_args = mock_post.call_args
            assert call_args[1]["json"]["language"] == "go"

    # === 타임아웃 설정 테스트 ===

    @pytest.mark.asyncio
    async def test_execute_code_timeout_configuration(self, service):
        """HTTP 클라이언트 타임아웃 설정 확인."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "OK"})

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            await service.execute_code("code", "test", "python")

            # AsyncClient가 60초 타임아웃으로 생성되었는지 확인
            assert mock_client.call_args[1]["timeout"] == 60.0

    # === 요청 페이로드 검증 ===

    @pytest.mark.asyncio
    async def test_execute_code_request_payload(self, service):
        """요청 페이로드가 올바르게 구성되는지 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "OK"})

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            input_code = "def foo(): pass"
            test_code = "assert foo() is None"
            language = "python"

            await service.execute_code(input_code, test_code, language)

            # 페이로드 검증
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["input_code"] == input_code
            assert payload["test_code"] == test_code
            assert payload["language"] == language

    @pytest.mark.asyncio
    async def test_execute_code_worker_url(self, service):
        """Worker URL이 올바르게 호출되는지 테스트."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"success": True, "output": "OK"})

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await service.execute_code("code", "test", "python")

            # URL 확인
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://test-worker:5000/execute"
