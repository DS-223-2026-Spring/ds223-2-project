from __future__ import annotations

import subprocess
import time
from pathlib import Path
import shutil

from prefect import flow, get_run_logger, task

ROOT = Path(__file__).resolve().parents[1]


def find_docker_compose_command() -> list[str]:
    if shutil.which("docker"):
        try:
            subprocess.run(
                ["docker", "compose", "version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return ["docker", "compose"]
        except subprocess.CalledProcessError:
            pass

    if shutil.which("docker-compose"):
        return ["docker-compose"]

    raise RuntimeError("Docker Compose not found")


@task
def run_compose(args: list[str]) -> None:
    cmd = [*find_docker_compose_command(), *args]
    subprocess.run(cmd, cwd=ROOT, check=True)


@task
def cleanup():
    run_compose(["down", "--remove-orphans"])


@flow(name="Safe Docker Compose Up with Recovery")
def safe_compose_up_flow(max_retries: int = 3, delay_seconds: int = 5):

    logger = get_run_logger()

    for i in range(max_retries):
        try:
            logger.info(f"Attempt {i+1}/{max_retries}")

            run_compose(["up", "-d", "--build"])

            logger.info("Stack started successfully")
            return

        except Exception as e:
            logger.error(f"Failed attempt {i+1}: {e}")

            cleanup()

            if i < max_retries - 1:
                logger.info(f"Retrying in {delay_seconds}s...")
                time.sleep(delay_seconds)

    raise RuntimeError("All retries failed")


if __name__ == "__main__":
    safe_compose_up_flow()