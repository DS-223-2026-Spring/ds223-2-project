#!/usr/bin/env python3
"""
Automatic Database Update Flow - ETL refresh + API restart.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from prefect import flow, get_run_logger, task

ROOT = Path(__file__).resolve().parents[1]


def find_docker_compose_command() -> list[str]:
    import shutil

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


@task(retries=2, retry_delay_seconds=5)
def run_compose(args: list[str]) -> None:
    cmd = [*find_docker_compose_command(), *args]
    subprocess.run(cmd, cwd=ROOT, check=True)


@task
def run_etl():
    """
    Rebuild database using ETL container.
    """
    run_compose(["up", "etl_db"])


@task
def restart_api():
    """
    Restart backend after DB refresh.
    """
    run_compose(["restart", "back"])


@flow(name="Automatic Database Update Flow")
def auto_db_update_flow():
    logger = get_run_logger()

    logger.info("Starting DB update (ETL refresh)")

    try:
        run_etl()
        logger.info("ETL completed successfully")

        restart_api()
        logger.info("API restarted successfully")

    except Exception as e:
        logger.error(f"DB update failed: {e}")
        raise


if __name__ == "__main__":
    auto_db_update_flow()