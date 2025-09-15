import importlib
import logging

from dependency_injector.containers import DynamicContainer
from dependency_injector.providers import Singleton

from mtgapi.services import AuxiliaryServiceNames
from mtgapi.services.database import PostgresDatabaseService
from mtgapi.services.proxy import NullProxyService

MODULES_TO_WIRE = [
    "mtgapi.services.http",
    "mtgapi.services.cache",
]

SERVICES_MAP = {
    AuxiliaryServiceNames.PROXY: NullProxyService,
    AuxiliaryServiceNames.DATABASE: PostgresDatabaseService,
}


def wire_services() -> DynamicContainer:
    container = DynamicContainer()

    for service_name, implementation in SERVICES_MAP.items():
        provider = Singleton(implementation)
        setattr(container, service_name, provider)
        logging.info(f"[INFO] Registered {service_name} with {implementation.__name__}")

    for module in MODULES_TO_WIRE:
        setattr(importlib.import_module(module), container.__class__.__name__, container)
        logging.info(f"[INFO] Wiring container to {module}")

    container.wire(modules=MODULES_TO_WIRE)
    container.reset_singletons()
    return container
