import os
from typing import Any, Optional

import httpx
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionService:
    """격리된 워커 환경에서 코드를 실행하는 서비스 (Singleton).

    안전한 샌드박스 Docker 환경을 갖춘 워커 VM으로 실행 요청을 프록시합니다.
    모든 요청에 대해 단일 httpx.AsyncClient 인스턴스를 재사용하여 성능을 최적화합니다.
    """

    _instance: Optional["ExecutionService"] = None
    _client: Optional[httpx.AsyncClient] = None

    def __new__(cls) -> "ExecutionService":
        """Singleton 인스턴스를 반환합니다."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """ExecutionService 인스턴스를 초기화합니다.

        이미 초기화된 경우(Singleton) 재실행하지 않습니다.
        워커 URL 및 인증 토큰을 환경 변수에서 로드하고,
        HTTP 클라이언트를 초기화합니다.
        """
        # Singleton 초기화 방지: 이미 클라이언트가 설정되어 있으면 스킵
        if self._client is not None:
            return

        self.worker_url = os.getenv("WORKER_URL", "http://localhost:5000")
        self.worker_token = os.getenv("WORKER_AUTH_TOKEN")

        # HTTP 클라이언트 초기화 (Connection Pooling, Keep-Alive)
        # 타임아웃 60초 설정
        self._client = httpx.AsyncClient(timeout=60.0)

        if not self.worker_token:
            logger.warning(
                "WORKER_AUTH_TOKEN이 설정되지 않았습니다. 인증이 필요한 경우 워커 요청이 실패할 수 있습니다"
            )
        else:
            logger.info("Worker 인증 토큰이 성공적으로 로드되었습니다")

    @property
    def client(self) -> httpx.AsyncClient:
        """초기화된 HTTP 클라이언트를 반환합니다.

        클라이언트가 예기치 않게 None일 경우 재생성합니다.
        """
        if self._client is None:
            logger.warning("HTTP Client가 초기화되지 않았거나 닫혔습니다. 재생성합니다.")
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def execute_code(self, input_code: str, test_code: str, language: str) -> dict[str, Any]:
        """Worker VM에 코드와 테스트 실행을 요청합니다.

        Args:
            input_code: 테스트 대상 소스 코드.
            test_code: 검증용 테스트 코드.
            language: 프로그래밍 언어 (예: 'python').

        Returns:
            실행 결과 딕셔너리 (success, output, error 등).

        Raises:
            InfrastructureError: Worker 연결 실패 또는 실행 오류 시.
        """
        try:
            is_token_loaded = bool(self.worker_token)
            logger.info_ctx(
                "Worker 실행 요청",
                language=language,
                worker_url=self.worker_url,
                auth_loaded=is_token_loaded,
            )

            headers = {}
            if self.worker_token:
                headers["Authorization"] = f"Bearer {self.worker_token}"

            # 재사용 가능한 클라이언트 사용 (Connection Reuse)
            response = await self.client.post(
                f"{self.worker_url}/execute",
                json={"input_code": input_code, "test_code": test_code, "language": language},
                headers=headers,
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401 or response.status_code == 403:
                logger.error(f"Worker 인증 실패: {response.text}")
                return {
                    "success": False,
                    "error": "실행 서버 인증에 실패했습니다",
                    "output": "",
                }
            else:
                error_msg = f"Worker API 오류: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": "실행 서버가 오류를 반환했습니다",
                    "output": error_msg,
                }

        except httpx.RequestError as e:
            logger.error(f"Worker 연결 실패: {e}")
            return {
                "success": False,
                "error": "실행 서비스에 연결할 수 없습니다",
                "output": "",
            }
        except Exception as e:
            logger.error(f"실행 서비스 예기치 않은 오류: {e}")
            return {
                "success": False,
                "error": f"내부 서버 오류: {str(e)}",
                "output": "",
            }

    async def close(self) -> None:
        """HTTP 클라이언트 연결을 종료하고 리소스를 해제합니다."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("ExecutionService HTTP 클라이언트가 종료되었습니다")
