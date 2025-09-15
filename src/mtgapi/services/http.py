import abc
import dataclasses
import logging
from collections.abc import Callable, Coroutine
from typing import Any
from urllib.parse import urljoin

import httpx
import tenacity
from dependency_injector.wiring import Provide, inject

from mtgapi.config.settings.base import AsyncHTTPServiceConfigurationBase
from mtgapi.services import AuxiliaryServiceNames
from mtgapi.services.base import AbstractAsyncService
from mtgapi.services.proxy import AbstractProxyService, NullProxyService


@dataclasses.dataclass
class AbstractAsyncHTTPClientService(AbstractAsyncService, abc.ABC):
    """
    Abstract base class for asynchronous API services.
    """

    base_url: str = dataclasses.field(init=False)
    _proxy_provider: AbstractProxyService | None = dataclasses.field(init=False, repr=False)
    __client: Callable[[], Coroutine[None, None, httpx.AsyncClient]] | None = dataclasses.field(init=False, repr=False)
    __follow_redirects: bool = dataclasses.field(init=False, default=True)

    @abc.abstractmethod
    def construct_headers(self, config: AsyncHTTPServiceConfigurationBase) -> dict[str, str]:
        """
        Construct headers for the HTTP request.

        :param config: The configuration for the API service.
        :return: A dictionary of headers.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def construct_auth(self, config: AsyncHTTPServiceConfigurationBase) -> httpx.Auth | None:
        """
        Construct authentication for the HTTP request.

        :param config: The configuration for the API service.
        :return: A httpx.Auth object or None if no authentication is needed.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def check_rate_limit(self, response: httpx.Response) -> bool:  # noqa: ARG002
        """
        Check the rate limit of the response.

        :param response: The HTTP response to check.
        :return: True if the rate limit is not exceeded, False otherwise.
        """
        return False

    @inject
    def get_proxy_provider(
        self,
        proxy_service: AbstractProxyService = Provide[AuxiliaryServiceNames.PROXY],
    ) -> AbstractProxyService:
        if AbstractProxyService not in proxy_service.__class__.__bases__:
            logging.error("[HTTP] Injected proxy service is not an instance of AbstractProxyService.")
            return NullProxyService()
        return proxy_service

    async def initialize(self, config: AsyncHTTPServiceConfigurationBase) -> None:  # type: ignore
        self._proxy_provider = self.get_proxy_provider()
        self.__follow_redirects = config.follow_redirects
        retry_strategy = tenacity.retry(
            stop=tenacity.stop_after_attempt(config.retries),
            wait=tenacity.wait_exponential(
                multiplier=config.exponential_backoff,
                min=config.minimum_wait,
                max=config.maximum_wait,
            ),
            reraise=config.reraise_exceptions,
            retry=tenacity.retry_if_exception_type(httpx.HTTPError),
        )
        self.base_url = config.base_url

        async def __spawn_client() -> httpx.AsyncClient:
            """
            Create an instance of httpx.AsyncClient with the provided configuration.
            """
            if self._proxy_provider is None:
                logging.warning("[HTTP] Proxy provider is not initialized. Using no proxy.")
                return httpx.AsyncClient(
                    timeout=httpx.Timeout(config.timeout),
                    headers=self.construct_headers(config),
                    auth=self.construct_auth(config),
                )
            proxy = await self._proxy_provider.get_proxy()

            if proxy is None or (not proxy.http and not proxy.https):
                logging.info("[HTTP] No proxy configured. Connecting directly.")
                return httpx.AsyncClient(
                    timeout=httpx.Timeout(config.timeout),
                    headers=self.construct_headers(config),
                    auth=self.construct_auth(config),
                )

            return httpx.AsyncClient(
                timeout=httpx.Timeout(config.timeout),
                headers=self.construct_headers(config),
                auth=self.construct_auth(config),
                proxy=proxy.to_httpx_proxy(),
            )

        self.__client = __spawn_client

        self._request = retry_strategy(self._request)  # type: ignore

    async def _request(self, verb: str, url: str, override_base: bool = False) -> httpx.Response:
        """
        Send an HTTP request using the configured client.

        :param verb: The HTTP method to use (e.g., 'GET', 'POST').
        :return: The HTTP response.
        """
        full_url = urljoin(self.base_url, url) if not override_base else url
        if not self.__client:
            raise RuntimeError("[HTTP] Client was not initialized.")
        async with await self.__client() as spawned_client:
            response = await spawned_client.request(verb, full_url, follow_redirects=self.__follow_redirects)
            response.raise_for_status()
            return response

    async def disconnect(self) -> None:
        """
        Disconnect the HTTP client.
        """
        if self.__client:
            self.__client = None
        else:
            raise RuntimeError("Client is not initialized or already closed.")

    # HTTP methods

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a GET request to the specified URL.

        :param url: The URL to send the GET request to.
        :return: The HTTP response.
        """
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a POST request to the specified URL.

        :param url: The URL to send the POST request to.
        :return: The HTTP response.
        """
        return await self._request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a PUT request to the specified URL.

        :param url: The URL to send the PUT request to.
        :return: The HTTP response.
        """
        return await self._request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a DELETE request to the specified URL.

        :param url: The URL to send the DELETE request to.
        :return: The HTTP response.
        """
        return await self._request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a PATCH request to the specified URL.

        :param url: The URL to send the PATCH request to.
        :return: The HTTP response.
        """
        return await self._request("PATCH", url, **kwargs)

    async def options(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send an OPTIONS request to the specified URL.

        :param url: The URL to send the OPTIONS request to.
        :return: The HTTP response.
        """
        return await self._request("OPTIONS", url, **kwargs)

    async def head(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a HEAD request to the specified URL.

        :param url: The URL to send the HEAD request to.
        :return: The HTTP response.
        """
        return await self._request("HEAD", url, **kwargs)

    async def trace(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a TRACE request to the specified URL.

        :param url: The URL to send the TRACE request to.
        :return: The HTTP response.
        """
        return await self._request("TRACE", url, **kwargs)

    async def connect(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Send a CONNECT request to the specified URL.

        :param url: The URL to send the CONNECT request to.
        :return: The HTTP response.
        """
        return await self._request("CONNECT", url, **kwargs)
