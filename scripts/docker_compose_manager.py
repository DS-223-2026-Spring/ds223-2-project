import argparse
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from prefect import flow, get_run_logger, task

# Assumes this file is in:
# repo/scripts/docker_compose_manager.py
ROOT = Path(__file__).resolve().parents[1]


def find_docker_compose_command() -> list[str]:
    """
    Detect whether to use:
    - docker compose
    - docker-compose
    """

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

    raise RuntimeError(
        "Docker Compose was not found. "
        "Install Docker Desktop or Docker Compose "
        "and ensure it is on your PATH."
    )


@task(name="RunComposeCommand", retries=2, retry_delay_seconds=5)
def run_compose_command(args: list[str]) -> None:
    """
    Execute a docker compose command.
    """

    logger = get_run_logger()

    cmd = [*find_docker_compose_command(), *args]

    logger.info(f"Running command: {' '.join(cmd)}")

    subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
    )


@task(name="ComposeUp", retries=2, retry_delay_seconds=5)
def compose_up_task(
    detach: bool = True,
    build: bool = True,
    profiles: list[str] | None = None,
) -> None:
    """
    Bring up the Docker Compose stack.
    """

    args = ["up"]

    if detach:
        args.append("-d")

    if build:
        args.append("--build")

    if profiles:
        for profile in profiles:
            args.extend(["--profile", profile])

    run_compose_command(args)

    logger = get_run_logger()
    logger.info("Docker Compose stack is up.")


@task(name="ComposeDown", retries=2, retry_delay_seconds=5)
def compose_down_task(
    remove_volumes: bool = False,
    remove_orphans: bool = True,
) -> None:
    """
    Tear down the Docker Compose stack.
    """

    args = ["down"]

    if remove_volumes:
        args.append("-v")

    if remove_orphans:
        args.append("--remove-orphans")

    run_compose_command(args)

    logger = get_run_logger()
    logger.info("Docker Compose stack is down.")


@flow(name="Docker Compose Manager")
def compose_flow(
    command: str,
    detach: bool = True,
    build: bool = True,
    profiles: list[str] | None = None,
    remove_volumes: bool = False,
) -> None:
    """
    Main Prefect flow for managing Docker Compose.
    """

    logger = get_run_logger()

    logger.info(f"Executing compose command: {command}")

    if command == "up":
        compose_up_task(
            detach=detach,
            build=build,
            profiles=profiles,
        )

    elif command == "down":
        compose_down_task(
            remove_volumes=remove_volumes,
        )

    elif command == "restart":
        compose_down_task(
            remove_volumes=remove_volumes,
        )

        compose_up_task(
            detach=detach,
            build=build,
            profiles=profiles,
        )

    else:
        raise ValueError(f"Unsupported command: {command}")


def wait_for_stop_signal() -> None:
    """
    Wait until Ctrl+C is pressed.
    Mainly useful for local usage, not UI deployments.
    """

    stop_requested = False

    def handle_signal(signum, frame):
        nonlocal stop_requested
        stop_requested = True
        print(f"Received signal {signum}; stopping stack...")

    signal.signal(signal.SIGINT, handle_signal)

    try:
        signal.signal(signal.SIGTERM, handle_signal)

    except AttributeError:
        # Windows may not support SIGTERM
        pass

    print("Press Ctrl+C to stop the stack and exit.")

    while not stop_requested:
        time.sleep(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage the AdVise Docker Compose stack with Prefect."
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["up", "down", "start", "restart"],
        help="Compose action to perform.",
    )

    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Register the Prefect deployment.",
    )

    parser.add_argument(
        "--profile",
        action="append",
        help="Optional Compose profile(s) to enable.",
    )

    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Do not run docker compose up --build.",
    )

    parser.add_argument(
        "--volumes",
        action="store_true",
        help="Remove volumes when tearing down the stack.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Require command unless deploying
    if not args.command:
        print("A command is required unless using --deploy.")
        return 1

    build = not args.no_build

    try:
        if args.command == "up":

            compose_flow(
                command="up",
                detach=True,
                build=build,
                profiles=args.profile,
            )

        elif args.command == "down":

            compose_flow(
                command="down",
                remove_volumes=args.volumes,
            )

        elif args.command == "start":

            compose_flow(
                command="up",
                detach=True,
                build=build,
                profiles=args.profile,
            )

            wait_for_stop_signal()

            compose_flow(
                command="down",
                remove_volumes=args.volumes,
            )

        elif args.command == "restart":

            compose_flow(
                command="restart",
                detach=True,
                build=build,
                profiles=args.profile,
                remove_volumes=args.volumes,
            )

        return 0

    except subprocess.CalledProcessError as exc:

        print(f"Command failed with exit code {exc.returncode}.")
        return exc.returncode

    except RuntimeError as exc:

        print(exc)
        return 1

    except ValueError as exc:

        print(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())