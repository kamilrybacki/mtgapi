import abc
import asyncio
import dataclasses
import logging
from typing import Any, ClassVar

import nest_asyncio

from mtgcobuilderapi.common.exceptions import InvalidServiceDefinitionError
from mtgcobuilderapi.config.settings.base import ServiceAbstractConfigurationBase


@dataclasses.dataclass
class AbstractServiceBase(abc.ABC):
    """
    Abstract base class for services.
    """

    config: ClassVar[type[ServiceAbstractConfigurationBase]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if abc.ABC in cls.__bases__:
            return

        config_model_for_subclass = kwargs.get("config")
        if config_model_for_subclass is None:
            raise InvalidServiceDefinitionError(f"Service subclass {cls.__name__} must define a config model.")

        if getattr(config_model_for_subclass, "from_environ", None) is None:
            raise InvalidServiceDefinitionError(
                f"Service subclass {cls.__name__} config model must inherit from ServiceAbstractConfigurationBase."
            )

        cls.config = config_model_for_subclass

    def _post_init(self, config: ServiceAbstractConfigurationBase) -> None:  # noqa: ARG002
        """
        Post-initialization method that can be overridden by subclasses.
        This method is called after the service has been initialized with the configuration.
        """
        logging.info(f"[Service] Initialized service {self.__class__.__name__}")

    @abc.abstractmethod
    def _initialize(self, config: ServiceAbstractConfigurationBase) -> None:
        """
        Initialize the service with the provided configuration.
        """
        raise NotImplementedError("initialize method not implemented.")

    def __post_init__(self) -> None:
        with self.config.use() as initialized_config:
            self._initialize(initialized_config)
            self._post_init(initialized_config)


@dataclasses.dataclass
class AbstractSyncService(AbstractServiceBase, abc.ABC):
    config: ClassVar[type[ServiceAbstractConfigurationBase]]

    @abc.abstractmethod
    def initialize(self, config: ServiceAbstractConfigurationBase) -> None:
        """Initialize the service. This method should be called before using the service."""
        raise NotImplementedError("initialize method not implemented.")

    def _initialize(self, config: ServiceAbstractConfigurationBase) -> None:
        self.initialize(config)


@dataclasses.dataclass
class AbstractAsyncService(AbstractServiceBase, abc.ABC):
    """
    Abstract class for asynchronous services.
    """

    _loop: asyncio.AbstractEventLoop | None = dataclasses.field(default=None, init=False)

    @abc.abstractmethod
    async def initialize(self, config: ServiceAbstractConfigurationBase) -> None:
        """Initialize the service. This method should be called before using the service."""
        raise NotImplementedError("initialize method not implemented.")

    def _initialize(self, config: ServiceAbstractConfigurationBase) -> None:
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there is no current event loop, create a new one
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        if self._loop.is_closed() or self._loop is None:
            self._loop = asyncio.new_event_loop()

        asyncio.set_event_loop(self._loop)
        if self._loop.is_running():
            nest_asyncio.apply(self._loop)

        self._loop.run_until_complete(self.initialize(config))
