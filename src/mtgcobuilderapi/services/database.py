import abc
import asyncio
import atexit
import dataclasses
import logging
from collections.abc import Sequence
from typing import Any, TypeVar

import sqlalchemy
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm.decl_api import DeclarativeBase

from mtgcobuilderapi.common.exceptions import DatabaseConnectionError
from mtgcobuilderapi.config.settings.base import ServiceAbstractConfigurationBase
from mtgcobuilderapi.config.settings.services import PostgresConfiguration
from mtgcobuilderapi.domain.conversions import convert_pydantic_model_to_sqlalchemy_base
from mtgcobuilderapi.services.base import AbstractAsyncService

DatabaseClient = TypeVar("DatabaseClient")


@dataclasses.dataclass
class AbstractDatabaseService(AbstractAsyncService, abc.ABC):
    """
    Abstract class for database services.
    """

    client: Any | None = dataclasses.field(default=None, init=False)

    async def initialize(self, config: ServiceAbstractConfigurationBase) -> None:
        """
        Initializes the database service with the given configuration.
        """
        await self._connect(config)

    async def _connect(self, config: ServiceAbstractConfigurationBase) -> None:
        """
        Connects to the database using the provided configuration.
        This method is intended to be overridden by subclasses.
        """
        logging.info("[DatabaseService] Initializing database connection.")
        try:
            await self.connect(config)
        except Exception as could_not_connect:
            raise DatabaseConnectionError(
                f"Could not connect to the database: {could_not_connect}"
            ) from could_not_connect

    @abc.abstractmethod
    async def connect(self, config: ServiceAbstractConfigurationBase) -> None:
        """
        Connects to the database using the provided configuration.
        """

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnects from the database.
        """

    @abc.abstractmethod
    async def query(self, query: str, *args: Any, **kwargs: Any) -> Any:
        """
        Executes a query against the database and returns the results.
        """


@dataclasses.dataclass
class PostgresDatabaseService(AbstractDatabaseService, config=PostgresConfiguration):
    """
    PostgresSQL database service using SQLAlchemy as the ORM.
    """

    client: AsyncConnection | None = dataclasses.field(default=None, init=False)
    session: async_sessionmaker[AsyncSession] | None = dataclasses.field(default=None, init=False)
    __models_cache: dict[str, type[DeclarativeBase]] = dataclasses.field(default_factory=dict)

    async def connect(self, config: PostgresConfiguration) -> None:  # type: ignore
        """
        Connects to the PostgreSQL database using the provided configuration.
        """
        logging.info("[DB] Initializing PostgreSQL connection.")
        engine = create_async_engine(
            url=config.connection_string,
        )
        self.client = await engine.connect()
        await self.client.execution_options(isolation_level="AUTOCOMMIT")
        self.session = async_sessionmaker(bind=self.client)
        logging.info("[DB] PostgreSQL connection established.")

        synchronous_disconnect_handler = lambda: asyncio.run(self.disconnect())  # noqa: E731
        atexit.register(synchronous_disconnect_handler)

    async def disconnect(self) -> None:
        """
        Disconnects from the PostgreSQL database.
        """
        logging.info("[DB] Disconnecting PostgreSQL connection.")
        if self.client:
            await self.client.close()
            self.client = None
            self.session = None

    async def query(self, query: str, *args: Any, **kwargs: Any) -> Any:
        """
        Executes a query against the PostgreSQL database and returns the results.
        """
        if not self.session:
            raise RuntimeError("Database session is not initialized.")

        async with self.session.begin() as session:
            query_cast_to_text = sqlalchemy.text(query)
            result = await session.execute(query_cast_to_text, *args, **kwargs)
            session.expunge_all()
            return result.fetchall()

    async def get_objects(
        self, object_type: type[BaseModel] | type[DeclarativeBase], filters: dict[str, Any] | None = None
    ) -> Sequence[DeclarativeBase]:
        """
        Retrieves objects from the database based on the provided object type and filters.
        This method supports both SQLAlchemy models and Pydantic models by converting the latter to SQLAlchemy base models.

        :param object_type: Data model type to retrieve from the database.
        :param filters: Optional dictionary of filters to apply to the query in form of kwargs passed to .filter_by method
        :return: Sequence of retrieved Postgres members
        """
        compatible_object_type = (
            object_type
            if not issubclass(object_type, BaseModel)
            else convert_pydantic_model_to_sqlalchemy_base(object_type)
        )

        if not self.session:
            raise RuntimeError("[DB] Database session is not initialized.")

        query = sqlalchemy.select(compatible_object_type)
        if filters:
            query = query.filter_by(**filters)

        async with self.session.begin() as session:
            result = await session.execute(query)
            session.expunge_all()
            return result.scalars().all()

    async def insert(self, instance: BaseModel) -> bool:
        if not self.session:
            raise RuntimeError("[DB] Database session is not initialized.")

        async with self.session.begin() as session:
            connection = await session.connection()
            if instance.__class__.__name__ not in self.__models_cache:
                new_model = convert_pydantic_model_to_sqlalchemy_base(instance.__class__)
                self.__models_cache[instance.__class__.__name__] = new_model
                asyncio.run(connection.run_sync(new_model.metadata.create_all))

            instance_data = instance.model_dump()
            new_entry = self.__models_cache[instance.__class__.__name__](**instance_data)

            if not connection:
                raise RuntimeError("Database session is not initialized.")

            try:
                session.add(new_entry)
                await session.commit()
            except Exception as entry_insertion_error:
                logging.exception("Failed to insert instance", exc_info=entry_insertion_error)
                await session.rollback()
                return False
            else:
                return True
