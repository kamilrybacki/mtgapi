from enum import StrEnum

import environ

from mtgapi.config.settings.base import (
    AsyncHTTPServiceConfigurationBase,
    ServiceAbstractConfigurationBase,
    ServiceConfigurationPrefixes,
)


@environ.config(prefix=ServiceConfigurationPrefixes.DATABASE)
class PostgresConfiguration(ServiceAbstractConfigurationBase):
    """
    Configuration class for database services.
    This class holds the necessary configuration values for the database services.
    """

    connection_string: str = environ.var(help="Database connection URL")

    @connection_string.validator  # type: ignore
    def validate_connection_string(self, _: str, value: str) -> None:
        """
        Validates the database connection string.
        Raises an error if the connection string is empty or invalid.
        """
        if not value:
            raise ValueError("Database connection string cannot be empty.")
        if "postgresql+asyncpg" not in value:
            raise ValueError("Database connection string must use the 'postgresql+asyncpg' driver.")


@environ.config(prefix=ServiceConfigurationPrefixes.MTGIO)
class MTGIOAPIConfiguration(AsyncHTTPServiceConfigurationBase):
    """
    Configuration class for the MTGIO API service.
    This class holds the necessary configuration values for the MTGIO API service.
    """

    version: str = environ.var(
        default="v1",
        help="Version of the MTGIO API to use, e.g., 'v1'.",
    )
    rate_limit_header: str = environ.var(
        default="RateLimit-Remaining",
        help="Header name for the rate limit in the MTGIO API responses.",
    )

    class APIEndpoints(StrEnum):
        """
        Enum for the API endpoints of the MTGIO service.
        This enum defines the available endpoints for the MTGIO API.
        """

        CARDS = "cards"
        SETS = "sets"
