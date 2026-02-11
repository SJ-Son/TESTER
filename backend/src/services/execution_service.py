import logging
import os

import httpx

logger = logging.getLogger(__name__)


class ExecutionService:
    """격리된 워커 환경에서 코드를 실행하는 서비스.

    안전한 샌드박스 Docker 환경을 갖춘 워커 VM으로 실행 요청을 프록시합니다.
    """

    def __init__(self):
        """워커 URL 및 인증 토큰 초기화.

        WORKER_AUTH_TOKEN 미설정 시 경고 로그를 출력합니다.
        """
        self.worker_url = os.getenv("WORKER_URL", "http://localhost:5000")
        self.worker_token = os.getenv("WORKER_AUTH_TOKEN")

        if not self.worker_token:
            logger.warning(
                "WORKER_AUTH_TOKEN not set in main backend. Requests to worker may fail if auth is enabled."
            )
        else:
            logger.info(f"Worker Auth Token loaded successfully: {bool(self.worker_token)}")

    async def execute_code(self, input_code: str, test_code: str, language: str):
        """워커 VM에 코드와 테스트 실행을 요청합니다.

        Args:
            input_code: 테스트 대상 소스 코드
            test_code: 검증용 테스트 코드
            language: 프로그래밍 언어 (예: 'python')

        Returns:
            dict: 실행 결과 {"success": bool, "output": str, "error": str}
        """
        # 실행 타임아웃 60초 설정
        try:
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
                    logger.error(f"Worker authentication failed: {response.text}")
                    return {
                        "success": False,
                        "error": "Execution worker authentication failed",
                        "output": "",
                    }
                else:
                    error_msg = f"Worker API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": "Execution worker returned error",
                        "output": error_msg,
                    }

        except httpx.RequestError as e:
            logger.error(f"Failed to connect to execution worker: {e}")
            return {
                "success": False,
                "error": "Execution service unavailable (Worker connection failed)",
                "output": "",
            }
        except Exception as e:
            logger.error(f"Unexpected error in execution service: {e}")
            return {
                "success": False,
                "error": f"Internal server error: {str(e)}",
                "output": "",
            }
