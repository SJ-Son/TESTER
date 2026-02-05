#!/bin/bash

# Wait for apt lock
echo "Checking for apt locks..."
while sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1 || sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1 || sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do
  echo "Waiting for apt lock..."
  sleep 5
done

# Update and install Docker
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Create Worker Files (Embed to avoid SCP issues)
cat <<EOF > requirements.txt
fastapi==0.109.2
uvicorn==0.27.1
docker==7.0.0
pydantic==2.6.1
pytest==8.0.0
EOF

cat <<EOF > Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
EOF

cat <<EOF > main.py
import os
import logging
import docker
from docker.errors import ImageNotFound
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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
        return 
    
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
    try:
        client = docker.from_env()
    except Exception as e:
        logger.error(f"Failed to initialize Docker client: {e}")
        raise HTTPException(status_code=503, detail="Docker service unavailable on worker")

    if request.language != "python":
        raise HTTPException(status_code=400, detail="Only Python is supported in sandbox currently")

    image_name = DOCKER_IMAGE
    try:
        client.images.get(image_name)
    except ImageNotFound:
        logger.warning(f"Image {image_name} not found. Falling back to python:3.9-slim.")
        image_name = "python:3.9-slim"

    container = None
    try:
        combined_code = f"{request.input_code}\n\n# --- Test Code ---\n\n{request.test_code}"

        container = client.containers.run(
            image_name,
            command="tail -f /dev/null", 
            detach=True,
            mem_limit="128m",
            nano_cpus=500000000, 
            network_disabled=True,
            pids_limit=50,
            security_opt=["no-new-privileges"],
            cap_drop=["ALL"],
            read_only=False,
            remove=True,
        )

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
                "output": output.decode('utf-8'),
            }

        run_cmd = ["timeout", "10s", "pytest", "test_run.py"]
        exec_result = container.exec_run(run_cmd, workdir="/app")

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
EOF

# Build Worker Image
echo "Current directory contents:"
ls -la

sudo docker build -t tester-worker .

# Build Sandbox Image
cat <<EOF > Dockerfile.sandbox
FROM python:3.12-slim
RUN pip install pytest
EOF

sudo docker build -t tester-sandbox -f Dockerfile.sandbox .

# Check if container is running and stop it
if [ "$(sudo docker ps -q -f name=tester-worker)" ]; then
    sudo docker stop tester-worker
    sudo docker rm tester-worker
fi

# Run Worker
export WORKER_AUTH_TOKEN="YOUR_SECRET_TOKEN_HERE" 

sudo docker run -d \
  --name tester-worker \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e WORKER_AUTH_TOKEN=$WORKER_AUTH_TOKEN \
  --restart unless-stopped \
  tester-worker
