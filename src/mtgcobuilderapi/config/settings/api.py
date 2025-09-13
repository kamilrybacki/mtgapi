import os

import environ

from mtgcobuilderapi import __version__
from mtgcobuilderapi.config.settings.base import ServiceAbstractConfigurationBase, ServiceConfigurationPrefixes

VERSION: str = os.environ.get(f"{ServiceConfigurationPrefixes.API}_VERSION", f"v{__version__.split('.')[0]}")


@environ.config(prefix=ServiceConfigurationPrefixes.API)
class APIConfiguration(ServiceAbstractConfigurationBase):
    root_path: str = environ.var(
        default=f"/api/{VERSION}",
        help="Root path for the API, used to prefix all endpoints. "
        "Useful for deployment in subdirectories or with reverse proxies.",
        converter=lambda path: path.rstrip("/"),
    )
