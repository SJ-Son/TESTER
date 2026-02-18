import asyncio
import io
import logging
import os
import tarfile
import time
from contextlib import asynccontextmanager
from typing import Optional

import docker
from docker.client import DockerClient
from docker.errors import ImageNotFound
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from security import SecurityChecker, SecurityViolation

# 기본 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 설정
WORKER_AUTH_TOKEN = os.getenv("WORKER_AUTH_TOKEN")
DISABLE_WORKER_AUTH = os.getenv("DISABLE_WORKER_AUTH", "false").lower() == "true"
DOCKER_RUNTIME = os.getenv("DOCKER_RUNTIME", "runsc")  # 보안을 위해 gVisor(runsc) 기본 사용
DOCKER_IMAGE = "tester-sandbox"

# Docker 클라이언트 전역 변수
docker_client: Optional[DockerClient] = None

if not WORKER_AUTH_TOKEN and not DISABLE_WORKER_AUTH:
    logger.critical(
        "WORKER_AUTH_TOKEN is not set and DISABLE_WORKER_AUTH is not true. "
        "Worker cannot start securely."
    )
    # 안전한 시작을 위해 토큰 필수 검증
    raise RuntimeError("WORKER_AUTH_TOKEN is required unless DISABLE_WORKER_AUTH=true")
else:
    # 토큰 로드 확인 로그 (값 노출 X)
    logger.info(f"Worker Config - Token Loaded: {bool(WORKER_AUTH_TOKEN)}")

if DISABLE_WORKER_AUTH:
    logger.warning("WARNING: Worker authentication is DISABLED. This is unsafe for production.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 수명 주기를 관리합니다.

    Docker 클라이언트를 초기화하고 종료 시 리소스를 정리합니다.
    시작 시 Docker 이미지가 존재하는지 확인합니다.

    Args:
        app: FastAPI 애플리케이션 인스턴스.
    """
    global docker_client
    try:
        docker_client = docker.from_env()
        logger.info("Docker client initialized successfully.")

        # 이미지 존재 여부 사전 확인
        try:
            docker_client.images.get(DOCKER_IMAGE)
            logger.info(f"Docker image '{DOCKER_IMAGE}' found.")
        except ImageNotFound:
            logger.warning(
                f"Docker image '{DOCKER_IMAGE}' not found. "
                "Requests will fail until 'docker build -t tester-sandbox -f Dockerfile.sandbox .' is run."
            )
        except Exception as e:
            logger.warning(f"Failed to check Docker image: {e}")

    except Exception as e:
        logger.error(f"Failed to initialize Docker client: {e}")
        docker_client = None

    yield

    if docker_client:
        try:
            docker_client.close()
            logger.info("Docker client closed.")
        except Exception as e:
            logger.error(f"Error closing Docker client: {e}")


app = FastAPI(lifespan=lifespan)


class ExecutionRequest(BaseModel):
    """코드 실행 요청 모델.

    Attributes:
        input_code: 사용자가 입력한 소스 코드.
        test_code: 검증을 위한 테스트 코드.
        language: 프로그래밍 언어 (python 등).
    """

    input_code: str
    test_code: str
    language: str


def verify_token(authorization: Optional[str] = Header(None)):
    """Worker 인증 토큰을 검증합니다.

    보안을 위해 상수 시간 비교(constant-time comparison)를 사용합니다.

    Args:
        authorization: Authorization 헤더 값 (Bearer Token).

    Raises:
        HTTPException: 인증 헤더가 없거나 형식이 잘못되었거나 토큰이 유효하지 않은 경우 (401/403).
    """
    if DISABLE_WORKER_AUTH:
        return  # 개발 모드 등에서 명시적으로 비활성화된 경우 건너뜀

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header Format")

    token = authorization.split(" ")[1]
    # 타이밍 공격 방지를 위한 상수 시간 비교 사용
    import secrets

    if not secrets.compare_digest(token, WORKER_AUTH_TOKEN):
        raise HTTPException(status_code=403, detail="Invalid Worker Token")


def create_tar_archive(file_name: str, content: str) -> bytes:
    """단일 파일을 포함하는 tar 아카이브를 생성합니다.

    Docker 컨테이너에 파일을 주입하기 위해 사용됩니다.

    Args:
        file_name: 아카이브 내 파일 이름.
        content: 파일 내용 (문자열).

    Returns:
        put_archive에 사용할 수 있는 bytes 형태의 tar 데이터.
    """
    file_data = content.encode("utf-8")
    tar_stream = io.BytesIO()

    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        tar_info = tarfile.TarInfo(name=file_name)
        tar_info.size = len(file_data)
        tar_info.mtime = time.time()
        tar.addfile(tarinfo=tar_info, fileobj=io.BytesIO(file_data))

    return tar_stream.getvalue()


@app.get("/health")
def health_check():
    """Worker 상태 및 Docker 클라이언트 상태를 확인합니다."""
    status = "active" if docker_client else "degraded (docker error)"
    return {"status": "ok", "worker": status}


@app.post("/execute", dependencies=[Depends(verify_token)])
async def execute_code(request: ExecutionRequest):
    """격리된 Docker 컨테이너에서 코드를 실행합니다.

    보안 검사 후 Docker Sandbox에서 코드를 실행하고 결과를 반환합니다.
    메인 루프 차단을 방지하기 위해 별도 스레드에서 실행됩니다.

    Args:
        request: 실행할 코드 및 설정 정보.

    Returns:
        실행 결과 객체 (성공 여부, 표준 출력, 에러 메시지).

    Raises:
        HTTPException: 지원하지 않는 언어이거나 Docker 서비스 사용 불가 시.
    """
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker service unavailable on worker")

    loop = asyncio.get_running_loop()

    # 블로킹 실행 로직 (동기 함수)
    def _run_sync():
        if request.language.lower() != "python":
            return {
                "success": False,
                "error": f"Language runner not implemented for {request.language}",
                "output": "",
            }

        # 0. 정적 보안 검사
        try:
            checker = SecurityChecker()
            checker.check_code(request.input_code)
            checker.check_code(request.test_code)
        except SecurityViolation as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
            }

        container = None
        try:
            # 1. 이미지 확인 (빠른 체크)
            try:
                docker_client.images.get(DOCKER_IMAGE)
            except ImageNotFound:
                raise HTTPException(
                    status_code=500,
                    detail=f"Docker image '{DOCKER_IMAGE}' not found. Please build it.",
                ) from None

            # 2. 컨테이너 시작
            combined_code = f"{request.input_code}\n\n# --- Test Code ---\n\n{request.test_code}"

            container = docker_client.containers.run(
                DOCKER_IMAGE,
                command="tail -f /dev/null",  # Keep alive
                detach=True,
                mem_limit="128m",
                nano_cpus=500000000,  # 0.5 CPU
                network_disabled=True,
                network_mode="none",  # 네트워크 완전 차단
                pids_limit=50,
                security_opt=["no-new-privileges"],
                cap_drop=["ALL"],
                read_only=True,  # 루트 파일시스템 읽기 전용
                # pytest 캐시 등을 위해 tmp는 쓰기 가능해야 함
                tmpfs={"/tmp": "", "/app": ""},
                remove=True,
                runtime=DOCKER_RUNTIME,
            )

            # 3. 코드 주입 (tar 방식)
            tar_data = create_tar_archive("test_run.py", combined_code)
            container.put_archive("/app", tar_data)

            # 4. 테스트 실행
            # /app은 Dockerfile에 정의된 WORKDIR
            run_cmd = ["timeout", "10s", "pytest", "test_run.py"]
            exec_result = container.exec_run(run_cmd, workdir="/app")

            output_str = exec_result.output.decode("utf-8", errors="replace")
            success = exec_result.exit_code == 0

            return {
                "success": success,
                "output": output_str,
                "error": "" if success else "Test execution failed",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {"success": False, "error": str(e), "output": ""}

        finally:
            # 5. 리소스 정리
            if container:
                try:
                    container.kill()
                except Exception as e:
                    # 이미 삭제된 경우 무시
                    logger.warning(f"Container cleanup warning: {e}")

    # 스레드 풀에서 실행 (Non-blocking)
    return await loop.run_in_executor(None, _run_sync)
