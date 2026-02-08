import logging
import os

import httpx

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self):
        self.worker_url = os.getenv("WORKER_URL", "http://localhost:5000")
        self.worker_token = os.getenv("WORKER_AUTH_TOKEN")

        if not self.worker_token:
            logger.warning(
                "WORKER_AUTH_TOKEN not set in main backend. Requests to worker may fail if auth is enabled."
            )

    async def execute_code(self, input_code: str, test_code: str, language: str) -> dict:
        """
        Forwards execution request to the isolated Worker VM.
        Timeout is set to 60 seconds to allow for test execution.
        """
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
