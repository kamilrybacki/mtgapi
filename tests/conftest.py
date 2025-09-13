from collections.abc import Generator

import pytest
import testcontainers.core.config
import testcontainers.core.container
import testcontainers.core.waiting_utils
from dependency_injector.containers import DynamicContainer

import tests.common.helpers
from mtgcobuilderapi.config.wiring import wire_services

pytest_plugins = [
    "tests.common.services",
]


@pytest.fixture(autouse=True, scope="session")
def setup_logging_for_tests() -> None:
    tests.common.helpers.setup_logging()


@pytest.fixture(autouse=True)
def configure_testcontainers_via_env() -> None:
    """
    Configures testcontainers to use the environment variables defined in the .env file.
    This is necessary for testcontainers to work correctly with the environment variables.
    """
    testcontainers.core.config.RYUK_DISABLED = True


@pytest.fixture(scope="function", autouse=True)
def auto_wire_services() -> Generator[None, None, None]:
    container: DynamicContainer = wire_services()
    yield
    container.shutdown_resources()
    container.unwire()
