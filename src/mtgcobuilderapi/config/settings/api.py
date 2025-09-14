import os

import environ

from mtgcobuilderapi import __version__
from mtgcobuilderapi.config.settings.base import ServiceAbstractConfigurationBase, ServiceConfigurationPrefixes

VERSION: str = os.environ.get(f"{ServiceConfigurationPrefixes.API}_VERSION", f"v{__version__.split('.')[0]}")


@environ.config(prefix=ServiceConfigurationPrefixes.API)
class APIConfiguration(ServiceAbstractConfigurationBase):
    @environ.config()
    class Logging:
        level: str = environ.var(
            default="INFO",
            help="Logging level for the API service. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
            converter=str,
        )
        message_format: str = environ.var(
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            help="Logging format for the API service.",
            converter=str,
        )
        date_format: str = environ.var(
            default="%Y-%m-%d %H:%M:%S",
            help="Date format for the API service logging.",
            converter=str,
        )

    logging: Logging = environ.group(Logging)

    root_path: str = environ.var(
        default=f"/api/{VERSION}",
        help="Root path for the API, used to prefix all endpoints. "
        "Useful for deployment in subdirectories or with reverse proxies.",
        converter=lambda path: path.rstrip("/"),
    )
