from __future__ import annotations

import subprocess
import time
from pathlib import Path
import shutil

from prefect import flow, get_run_logger, task

ROOT = Path(__file__).resolve().parents[1]


def _compose_file() -> Path:
    return ROOT / "docker-compose.yml"


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
    logger = get_run_logger()
    if not _compose_file().is_file():
        raise FileNotFoundError(
            f"Expected docker-compose.yml at {_compose_file()} (cwd for compose is {ROOT}). "
            "Prefect worker must run with repo root as the parent of scripts/."
        )

    cmd = [*find_docker_compose_command(), *args]
    logger.info("Running: %s (cwd=%s)", " ".join(cmd), ROOT)
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        logger.error(
            "Command failed exit=%s cmd=%s\n--- stdout ---\n%s\n--- stderr ---\n%s",
            proc.returncode,
            cmd,
            proc.stdout or "",
            proc.stderr or "",
        )
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr
        )


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