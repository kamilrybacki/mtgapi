import dataclasses
import logging
from collections.abc import Generator
from typing import AsyncGenerator
from unittest.mock import patch
import pytest_asyncio

import environ
import httpx
from mtgcobuilderapi.config.wiring import wire_services
import pytest
from httpx import ASGITransport, AsyncClient
from mypy.metastore import random_string
from testcontainers.core.container import DockerContainer

from mtgcobuilderapi.entrypoint import API
from mtgcobuilderapi.config.settings.base import (
    APP_CONFIGURATION_PREFIX,
    AsyncHTTPServiceConfigurationBase,
    ServiceAbstractConfigurationBase,
    ServiceConfigurationPrefixes,
)
from mtgcobuilderapi.config.settings.defaults import MTGIO_API_VERSION, MTGIO_BASE_URL, MTGIO_RATE_LIMIT_HEADER
from mtgcobuilderapi.services.apis.mtgio import MTGIOAPIService
from mtgcobuilderapi.services.base import AbstractSyncService
from mtgcobuilderapi.services.http import AbstractAsyncHTTPClientService
from mtgcobuilderapi.services.proxy import AbstractProxyService, Proxy
from tests.common.helpers import TemporaryEnvContext, use_postgres_container

TEST_HTTP_CONFIGURATION_PREFIX = "TEST_HTTP_SERVICE_"
TEST_HTTP_SERVICE_BASE_URL = "https://pokeapi.co/api/v2/"

TEST_PROXY_CONFIGURATION_PREFIX = "TEST_PROXY_SERVICE_"

MOCK_CONFIGURATION_PREFIX = APP_CONFIGURATION_PREFIX + "_MOCK_"
MOCK_SERVICE_SETTINGS = {"mock_setting": "mock_value", "another_mock_setting": 2000}


@environ.config(prefix=MOCK_CONFIGURATION_PREFIX)
class MockConfiguration(ServiceAbstractConfigurationBase):
    """
    Mock configuration class for testing purposes.
    This class is used to simulate configurations in tests without affecting the actual environment.
    """

    mock_setting: str = environ.var(default="default_value", help="A mock setting for testing purposes.")
    another_mock_setting: int = environ.var(
        default=42, help="Another mock setting for testing purposes.", converter=int
    )


@dataclasses.dataclass
class MockService(AbstractSyncService, config=MockConfiguration):
    """
    Mock service class for testing purposes.
    This class is used to simulate a service in tests without affecting the actual service implementation.
    """

    message: str = dataclasses.field(init=False)

    @staticmethod
    def construct_message(first_part: str, second_part: str) -> str:
        """
        Constructs a message from the provided parts.
        """
        return f"{first_part} - {second_part}"

    def initialize(self, config: MockConfiguration) -> None:  # type: ignore
        """
        Initialize the mock service with the provided configuration.
        """
        self.message = self.construct_message(config.mock_setting, str(config.another_mock_setting))


@pytest.fixture(scope="function")
def mock_service_environment() -> Generator[None, None, None]:
    """
    Fixture to mock the service environment for testing purposes.
    This fixture can be used to set up any necessary environment variables or configurations
    that the service requires during tests.
    """
    with patch.dict(
        "os.environ",
        {
            MOCK_CONFIGURATION_PREFIX + "_" + setting_name.upper(): str(setting_value)
            for setting_name, setting_value in MOCK_SERVICE_SETTINGS.items()
        },
    ):
        yield


@environ.config(prefix=TEST_HTTP_CONFIGURATION_PREFIX)
class TestHTTPServiceConfiguration(AsyncHTTPServiceConfigurationBase): ...


class PokeAPIClientService(AbstractAsyncHTTPClientService, config=TestHTTPServiceConfiguration):
    def construct_headers(self, config: AsyncHTTPServiceConfigurationBase) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def construct_auth(self, config: AsyncHTTPServiceConfigurationBase) -> httpx.Auth | None:
        return None


@environ.config(prefix=TEST_PROXY_CONFIGURATION_PREFIX)
class ThreeProxyConfiguration(ServiceAbstractConfigurationBase):
    """
    Configuration for the ThreeProxyService.
    """

    username: str = environ.var(default="")
    password: str = environ.var(default="")
    host: str = environ.var(default="")
    port: int = environ.var(default=3128, converter=int)


@dataclasses.dataclass
class ThreeProxyService(AbstractProxyService, config=ThreeProxyConfiguration):
    """
    A mock proxy service that returns a fixed proxy configuration.
    """

    _proxy_address: str = dataclasses.field(init=False)
    _auth: str = dataclasses.field(init=False)

    async def initialize(self, config: ThreeProxyConfiguration) -> None:  # type: ignore
        self._proxy_address = f"{config.host}:{config.port}"
        if config.username and config.password:
            self._auth = f"{config.username}:{config.password}@"
        else:
            self._auth = ""

    async def get_proxy(self) -> Proxy | None:
        """
        Returns a fixed proxy configuration.
        """
        endpoint = f"http://{self._auth}{self._proxy_address}"
        return Proxy(
            http=endpoint,
            https=endpoint,
        )


@pytest.fixture(scope="function")
def pokeapi_service() -> PokeAPIClientService:
    with TemporaryEnvContext(**{TEST_HTTP_CONFIGURATION_PREFIX + "_BASE_URL": TEST_HTTP_SERVICE_BASE_URL}):
        return PokeAPIClientService()


@pytest.fixture(scope="function")
def three_proxy_service() -> Generator[ThreeProxyService, None, None]:
    (random_login, random_password) = (random_string(), random_string())
    with (
        DockerContainer(image="riftbit/3proxy:latest")
        .with_env("PROXY_LOGIN", random_login)
        .with_env("PROXY_PASSWORD", random_password)
        .with_exposed_ports(3128)
        .with_exposed_ports(80)
    ) as three_proxy_server:
        logging.info(
            f"[TEST] ThreeProxy server started at {three_proxy_server.get_container_host_ip()}:{three_proxy_server.get_exposed_port(3128)}"
        )
        with TemporaryEnvContext(
            **{
                TEST_PROXY_CONFIGURATION_PREFIX + "_HOST": three_proxy_server.get_container_host_ip(),
                TEST_PROXY_CONFIGURATION_PREFIX + "_PORT": three_proxy_server.get_exposed_port(3128),
                TEST_PROXY_CONFIGURATION_PREFIX + "_USERNAME": random_login,
                TEST_PROXY_CONFIGURATION_PREFIX + "_PASSWORD": random_password,
            }
        ):
            yield ThreeProxyService()
        logging.info("[TEST] Stopping ThreeProxy server...")


@pytest.fixture(scope="function")
def test_mtgio_service(
    three_proxy_service: ThreeProxyService,
) -> Generator[MTGIOAPIService, None, None]:
    with TemporaryEnvContext(
        **{
            f"{ServiceConfigurationPrefixes.MTGIO}_BASE_URL": MTGIO_BASE_URL,
            f"{ServiceConfigurationPrefixes.MTGIO}_VERSION": MTGIO_API_VERSION,
            f"{ServiceConfigurationPrefixes.MTGIO}_RATE_LIMIT_HEADER": MTGIO_RATE_LIMIT_HEADER,
        }
    ):
        initialized_service = MTGIOAPIService()
        initialized_service._proxy_provider = three_proxy_service
        yield initialized_service


@pytest_asyncio.fixture(scope="function")
async def test_cobuilder_api_client() -> AsyncGenerator[AsyncClient, None]:
    with use_postgres_container():
        wire_services()
        full_base_url = f"http://testservers.com/{API.root_path.removeprefix('/')}"
        async with AsyncClient(transport=ASGITransport(app=API), base_url=full_base_url) as client:
            yield client
