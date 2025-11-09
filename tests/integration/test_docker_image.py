from __future__ import annotations

import json
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib import error, request

import pytest

from mtgapi.config.settings.base import ServiceConfigurationPrefixes
from mtgapi.config.settings.defaults import MTGIO_BASE_URL

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = PROJECT_ROOT / "deploy" / "Dockerfile"


def _docker_cli_available() -> bool:
    """Return True when the Docker CLI is available and the daemon responds."""
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return True


pytestmark = [
    pytest.mark.docker,
    pytest.mark.skipif(not _docker_cli_available(), reason="Docker CLI is not available"),
]


@pytest.fixture(scope="session")
def built_image() -> Iterator[str]:
    """Build the application image once per test session."""
    image_tag = f"mtgcobuilder-api-test:{uuid.uuid4().hex[:12]}"
    build_cmd = [
        "docker",
        "build",
        "-f",
        str(DOCKERFILE_PATH),
        "-t",
        image_tag,
        str(PROJECT_ROOT),
    ]
    subprocess.run(build_cmd, check=True)
    yield image_tag
    subprocess.run(
        ["docker", "rmi", "-f", image_tag],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@dataclass
class PostgresBackend:
    container_name: str
    connection_string: str
    network: str


def _wait_for_postgres(container_name: str, username: str, database: str) -> bool:
    deadline = time.time() + 60
    while time.time() < deadline:
        probe = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "pg_isready",
                "-U",
                username,
                "-d",
                database,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if probe.returncode == 0:
            return True
        time.sleep(2)
    return False


@pytest.fixture(scope="function")
def docker_network() -> Iterator[str]:
    network_name = f"mtgcobuilder-api-test-net-{uuid.uuid4().hex[:12]}"
    subprocess.run(
        ["docker", "network", "create", network_name],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        yield network_name
    finally:
        subprocess.run(
            ["docker", "network", "rm", network_name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


@pytest.fixture(scope="function")
def postgres_backend(docker_network: str) -> Iterator[PostgresBackend]:
    container_name = f"mtgcobuilder-api-postgres-{uuid.uuid4().hex[:12]}"
    username = "testuser"
    password = "testpassword"
    database = "testdb"
    run_proc = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "--network",
            docker_network,
            "-e",
            f"POSTGRES_USER={username}",
            "-e",
            f"POSTGRES_PASSWORD={password}",
            "-e",
            f"POSTGRES_DB={database}",
            "postgres:13",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    container_id = run_proc.stdout.strip()
    try:
        if not _wait_for_postgres(container_name, username, database):
            logs_proc = subprocess.run(
                ["docker", "logs", container_name],
                check=False,
                capture_output=True,
                text=True,
            )
            pytest.fail(f"Postgres container did not become ready within the allotted time. Logs:\n{logs_proc.stdout}")
        connection_string = f"postgresql+asyncpg://{username}:{password}@{container_name}:5432/{database}"
        yield PostgresBackend(
            container_name=container_name,
            connection_string=connection_string,
            network=docker_network,
        )
    finally:
        subprocess.run(
            ["docker", "rm", "-f", container_id or container_name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def test_docker_image_builds(built_image: str) -> None:
    """The Dockerfile must produce an image with the expected startup command."""
    inspect_proc = subprocess.run(
        ["docker", "image", "inspect", built_image],
        check=True,
        capture_output=True,
        text=True,
    )
    image_info = json.loads(inspect_proc.stdout)[0]
    assert image_info["Config"]["Cmd"] == [
        "python",
        "-m",
        "uvicorn",
        "mtgapi.entrypoint:API",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]


def test_docker_image_serves_application(built_image: str, postgres_backend: PostgresBackend) -> None:
    """Run the image and confirm the FastAPI docs endpoint becomes reachable."""
    container_name = f"mtgcobuilder-api-test-{uuid.uuid4().hex[:12]}"
    run_proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "--network",
            postgres_backend.network,
            "-p",
            "0:8000",
            "--name",
            container_name,
            "-e",
            f"{ServiceConfigurationPrefixes.DATABASE}CONNECTION_STRING={postgres_backend.connection_string}",
            "-e",
            f"{ServiceConfigurationPrefixes.API}ROOT_PATH=/",
            "-e",
            f"{ServiceConfigurationPrefixes.MTGIO}BASE_URL={MTGIO_BASE_URL}",
            built_image,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    container_id = run_proc.stdout.strip()
    try:
        port_proc = subprocess.run(
            ["docker", "port", container_id, "8000/tcp"],
            check=True,
            capture_output=True,
            text=True,
        )
        port_mapping = port_proc.stdout.strip().splitlines()[0]
        host_port = port_mapping.rsplit(":", 1)[-1]
        target_url = f"http://127.0.0.1:{host_port}/docs"

        # Give the application time to start and expose the docs endpoint.
        deadline = time.time() + 120
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                with request.urlopen(target_url, timeout=2) as response:
                    body = response.read()
                    content_type = response.headers.get("content-type", "")
                    assert response.status == 200
                    assert content_type.startswith("text/html")
                    assert b"SwaggerUIBundle" in body
                break
            except (error.URLError, OSError) as exc:
                last_error = exc
                time.sleep(2)
        else:
            logs_proc = subprocess.run(
                ["docker", "logs", container_id],
                check=False,
                capture_output=True,
                text=True,
            )
            pytest.fail(
                "Container did not become ready within 120 seconds. "
                f"Last error: {last_error}\nLogs:\n{logs_proc.stdout}"
            )
    finally:
        subprocess.run(
            ["docker", "stop", container_id],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
