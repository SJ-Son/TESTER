import os
from typing import Any

import httpx
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionService:
    """격리된 워커 환경에서 코드를 실행하는 서비스.

    안전한 샌드박스 Docker 환경을 갖춘 워커 VM으로 실행 요청을 프록시합니다.
    """

    def __init__(self) -> None:
        """ExecutionService 인스턴스를 초기화합니다.

        워커 URL 및 인증 토큰을 환경 변수에서 로드합니다.
        WORKER_AUTH_TOKEN 미설정 시 경고 로그를 출력합니다.
        """
        self.worker_url = os.getenv("WORKER_URL", "http://localhost:5000")
        self.worker_token = os.getenv("WORKER_AUTH_TOKEN")

        if not self.worker_token:
            logger.warning(
                "WORKER_AUTH_TOKEN이 설정되지 않았습니다. 인증이 필요한 경우 워커 요청이 실패할 수 있습니다"
            )
        else:
            logger.info("Worker 인증 토큰이 성공적으로 로드되었습니다")

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
        # 실행 타임아웃 60초 설정
        try:
            is_token_loaded = bool(self.worker_token)
            logger.info_ctx(
                "Worker 실행 요청",
                language=language,
                worker_url=self.worker_url,
                auth_loaded=is_token_loaded,
            )

            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {}
                if self.worker_token:
                    headers["Authorization"] = f"Bearer {self.worker_token}"

                response = await client.post(
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
