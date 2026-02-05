import logging
import os
from typing import Optional

import docker
from docker.errors import ImageNotFound
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment Variables
WORKER_AUTH_TOKEN = os.getenv("WORKER_AUTH_TOKEN")
DOCKER_IMAGE = "tester-sandbox"

if not WORKER_AUTH_TOKEN:
    logger.warning("WORKER_AUTH_TOKEN is not set! Security execution is disabled.")


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


@app.get("/health")
def health_check():
    return {"status": "ok", "worker": "active"}


@app.post("/execute", dependencies=[Depends(verify_token)])
def execute_code(request: ExecutionRequest):
    """
    Executes code inside a secure Docker container.
    This logic is moved from the main backend's ExecutionService.
    """
    try:
        client = docker.from_env()
    except Exception as e:
        logger.error(f"Failed to initialize Docker client: {e}")
        raise HTTPException(status_code=503, detail="Docker service unavailable on worker") from e

    if request.language != "python":
        raise HTTPException(status_code=400, detail="Only Python is supported in sandbox currently")

    # Image Check
    image_name = DOCKER_IMAGE
    try:
        client.images.get(image_name)
    except ImageNotFound:
        logger.warning(f"Image {image_name} not found. Falling back to python:3.9-slim.")
        image_name = "python:3.9-slim"

    container = None
    try:
        # Combine Input Code and Test Code
        combined_code = f"{request.input_code}\n\n# --- Test Code ---\n\n{request.test_code}"

        container = client.containers.run(
            image_name,
            command="tail -f /dev/null",  # Keep alive
            detach=True,
            mem_limit="128m",
            nano_cpus=500000000,  # 0.5 CPU
            network_disabled=True,
            pids_limit=50,
            security_opt=["no-new-privileges"],
            cap_drop=["ALL"],
            read_only=False,
            remove=True,
        )

        # Write combined code to file
        setup_cmd = [
            "python3",
            "-c",
            f"with open('test_run.py', 'w') as f: f.write({repr(combined_code)})",
        ]
        exit_code, output = container.exec_run(setup_cmd)

        if exit_code != 0:
            logger.error(f"Failed to write code to container: {output.decode('utf-8')}")
            return {
                "success": False,
                "error": "Failed to prepare execution environment",
                "output": output.decode("utf-8"),
            }

        # Run pytest with timeout
        run_cmd = ["timeout", "10s", "pytest", "test_run.py"]
        exec_result = container.exec_run(run_cmd, workdir="/")

        output_str = exec_result.output.decode("utf-8")
        success = exec_result.exit_code == 0

        return {
            "success": success,
            "output": output_str,
            "error": "" if success else "Test execution failed",
        }

    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return {"success": False, "error": str(e), "output": ""}

    finally:
        if container:
            try:
                container.kill()
            except Exception as e:
                logger.warning(f"Failed to cleanup container: {e}")
