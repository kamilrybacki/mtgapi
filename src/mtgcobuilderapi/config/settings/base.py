import contextlib
import os
from collections.abc import Generator
from enum import StrEnum
from typing import Self

import environ


@environ.config()
class ServiceAbstractConfigurationBase:
    """Abstract base class for service configuration."""

    @classmethod
    @contextlib.contextmanager
    def use(cls) -> Generator[Self, None, None]:
        """Context manager to use the configuration."""
        yield cls.from_environ(environ=os.environ)  # type: ignore


@environ.config()
class NullConfiguration(ServiceAbstractConfigurationBase):
    """Null configuration class that does nothing."""

    @classmethod
    def from_environ(cls, _: dict[str, str]) -> Self:
        """Create a NullConfiguration instance from environment variables."""
        return cls()


@environ.config()
class AsyncHTTPServiceConfigurationBase(ServiceAbstractConfigurationBase):
    """Configuration for asynchronous API services."""

    base_url: str = environ.var(help="Base URL for the API service.", converter=str)
    timeout: int = environ.var(default=30, help="Timeout for API requests in seconds.", converter=int)
    retries: int = environ.var(
        default=3,
        help="Number of retries for failed API requests.",
        converter=int,
    )
    exponential_backoff: bool = environ.var(
        default=True,
        help="Use exponential backoff for retries.",
        converter=bool,
    )
    minimum_wait: int = environ.var(
        default=1,
        help="Minimum wait time between retries in seconds.",
        converter=int,
    )
    maximum_wait: int = environ.var(
        default=10,
        help="Maximum wait time between retries in seconds.",
        converter=int,
    )
    reraise_exceptions: bool = environ.var(
        default=True,
        help="Whether to reraise exceptions after retries.",
        converter=bool,
    )
    rate_limit: int = environ.var(
        default=0,
        help="Rate limit for API requests per second. 0 means no rate limit.",
        converter=int,
    )
    follow_redirects: bool = environ.var(
        default=True,
        help="Whether to follow redirects in API requests.",
        converter=bool,
    )


APP_CONFIGURATION_PREFIX = "MTGCOBUILDER"


class ServiceConfigurationPrefixes(StrEnum):
    API = f"{APP_CONFIGURATION_PREFIX}_API_"
    DATABASE = f"{APP_CONFIGURATION_PREFIX}_DATABASE_"
    MTGIO = f"{APP_CONFIGURATION_PREFIX}_MTGIO_"
