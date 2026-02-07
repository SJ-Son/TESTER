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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
WORKER_AUTH_TOKEN = os.getenv("WORKER_AUTH_TOKEN")
DOCKER_IMAGE = "tester-sandbox"

# Global Docker Client
docker_client: Optional[DockerClient] = None

if not WORKER_AUTH_TOKEN:
    logger.warning("WORKER_AUTH_TOKEN is not set! Security execution is disabled.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage Docker client lifecycle.
    Initializes the client on startup and closes it on shutdown.
    """
    global docker_client
    try:
        docker_client = docker.from_env()
        logger.info("Docker client initialized successfully.")

        # Pre-check image availability
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
    input_code: str
    test_code: str
    language: str


def verify_token(authorization: Optional[str] = Header(None)):
    if not WORKER_AUTH_TOKEN:
        return  # Skip if not configured (Dev mode)

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header Format")

    token = authorization.split(" ")[1]
    if token != WORKER_AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Worker Token")


def create_tar_archive(file_name: str, content: str) -> bytes:
    """
    Create a tar archive containing a single file with the given content.
    Returns bytes ready for put_archive.
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
    status = "active" if docker_client else "degraded (docker error)"
    return {"status": "ok", "worker": status}


@app.post("/execute", dependencies=[Depends(verify_token)])
async def execute_code(request: ExecutionRequest):
    """
    Executes code inside a secure Docker container.
    Internal execution logic runs in a separate thread to prevent blocking main loop.
    """
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker service unavailable on worker")

    loop = asyncio.get_running_loop()

    # Define the blocking execution logic as a synchronous function
    def _run_sync():
        if request.language.lower() != "python":
            return {
                "success": False,
                "error": f"Language runner not implemented for {request.language}",
                "output": "",
            }

        container = None
        try:
            # 1. Check Image (Fast check since we checked at startup, but good for safety)
            try:
                docker_client.images.get(DOCKER_IMAGE)
            except ImageNotFound:
                raise HTTPException(
                    status_code=500,
                    detail=f"Docker image '{DOCKER_IMAGE}' not found. Please build it.",
                ) from None

            # 2. Start Container
            combined_code = f"{request.input_code}\n\n# --- Test Code ---\n\n{request.test_code}"

            container = docker_client.containers.run(
                DOCKER_IMAGE,
                command="tail -f /dev/null",  # Keep alive
                detach=True,
                mem_limit="128m",
                nano_cpus=500000000,  # 0.5 CPU
                network_disabled=True,
                pids_limit=50,
                security_opt=["no-new-privileges"],
                cap_drop=["ALL"],
                read_only=False,  # We need write access to /app
                remove=True,  # Auto-remove on stop is handled, but we explicitly kill/remove in finally
            )

            # 3. Inject Code using Tar Archive (Safe Method)
            tar_data = create_tar_archive("test_run.py", combined_code)
            container.put_archive("/app", tar_data)

            # 4. Execute Test
            # /app is WORKDIR defined in Dockerfile
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
            # 5. Cleanup
            if container:
                try:
                    container.kill()
                except Exception as e:
                    # Ignore 404/409 errors if container is already gone
                    logger.warning(f"Container cleanup warning: {e}")

    # Offload blocking Docker calls to thread pool
    return await loop.run_in_executor(None, _run_sync)
