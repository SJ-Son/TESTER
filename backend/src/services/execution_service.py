import logging

import docker
from docker.errors import ImageNotFound

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None

    def execute_code(self, input_code: str, test_code: str, language: str) -> dict:
        if not self.client:
            return {
                "success": False,
                "error": "Execution service unavailable (Docker not connected)",
                "output": "",
            }

        # Only Python supported for now
        if language != "python":
            return {
                "success": False,
                "error": "Only Python is supported in sandbox currently",
                "output": "",
            }

        # Image to use
        image_name = "tester-sandbox"

        try:
            self.client.images.get(image_name)
        except ImageNotFound:
            logger.warning(f"Image {image_name} not found. Falling back to python:3.9-slim.")
            image_name = "python:3.9-slim"

        container = None
        try:
            # Combine Input Code and Test Code
            # We append test code to input code so tests can see the functions
            # Warning: If generated code uses 'import', it might fail if file structure isn't there.
            # We assume simple snippet generation for now.
            combined_code = f"{input_code}\n\n# --- Test Code ---\n\n{test_code}"

            container = self.client.containers.run(
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

            # Run pytest
            # Run pytest with timeout
            # We use 'timeout' command from coreutils (standard in slim)
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
                    # container.remove() # Auto-remove might conflict if we kill?
                    # If we used remove=True in run, checking status might be tricky.
                    # But we used detach=True. `remove=True` in run means it removes after it stops.
                    # Killing it stops it.
                except Exception as e:
                    logger.warning(f"Failed to cleanup container: {e}")
