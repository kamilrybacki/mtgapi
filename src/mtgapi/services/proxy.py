import abc
import dataclasses

import httpx

from mtgapi.config.settings.base import NullConfiguration
from mtgapi.services.base import AbstractAsyncService


@dataclasses.dataclass(frozen=True)
class Proxy:
    """
    TypedDict for proxy configuration.
    This defines the structure of a proxy configuration.
    """

    http: str
    https: str

    def to_httpx_proxy(self) -> httpx.Proxy | None:
        """
        Convert the Proxy instance to a dictionary suitable for httpx proxy configuration.

        """
        try:
            return httpx.Proxy(url=self.http)
        except ValueError:
            return None

    @staticmethod
    def _obfuscate_url(url: str) -> str:
        """
        Obfuscate the URL by replacing the username and password with '***'.
        This is useful for logging or debugging purposes to avoid exposing sensitive information.

        :param url: The URL to obfuscate.
        :return: The obfuscated URL.
        """
        if "@" in url:
            user_info, rest = url.split("@", 1)
            return f"***@{rest}"
        return url

    def __str__(self) -> str:
        """
        Return a string representation of the proxy configuration.
        This is useful for logging or debugging purposes.

        :return: A string representation of the proxy configuration.
        """
        obfuscated_http = self._obfuscate_url(self.http)
        obfuscated_https = self._obfuscate_url(self.https)
        return f"Proxy(http={obfuscated_http}, https={obfuscated_https})"

    def __repr__(self) -> str:
        """
        Return a string representation of the proxy configuration for debugging.

        :return: A string representation of the proxy configuration.
        """
        return self.__str__()


class AbstractProxyService(AbstractAsyncService, abc.ABC):
    """
    Abstract base class for proxy services.
    This class defines the interface for proxy services,
    which can be used to route requests through a proxy server.
    """

    async def get_proxy(self) -> Proxy | None:
        """
        Get the proxy URL to be used for requests.

        :return: The proxy URL as a string.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class NullProxyService(AbstractProxyService, config=NullConfiguration):
    """
    A proxy service that does not use any proxy.
    This is a no-op implementation of the AbstractProxyService.
    """

    async def initialize(self, config: AbstractProxyService) -> None:  # type: ignore
        """
        Initialize the NullProxyService.
        This method does not perform any actions as no proxy is used.

        :param config: The configuration for the proxy service.
        """

    async def get_proxy(self) -> Proxy | None:
        """
        Return an empty string as no proxy is used.

        :return: An empty string indicating no proxy.
        """
        return Proxy(http="", https="")
