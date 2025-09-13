import importlib
import logging

from dependency_injector.containers import DynamicContainer
from dependency_injector.providers import Singleton

from mtgcobuilderapi.services import InjectedServiceNames
from mtgcobuilderapi.services.apis.mtgio import MTGIOAPIService
from mtgcobuilderapi.services.database import PostgresDatabaseService
from mtgcobuilderapi.services.proxy import NullProxyService

MODULES_TO_WIRE = [
    "mtgcobuilderapi.services.http",
    "mtgcobuilderapi.api.middleware.cache",
    "mtgcobuilderapi.api.main",
]

SERVICES_MAP = {
    InjectedServiceNames.PROXY: NullProxyService,
    InjectedServiceNames.DATABASE: PostgresDatabaseService,
    InjectedServiceNames.MTGIO: MTGIOAPIService,
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
