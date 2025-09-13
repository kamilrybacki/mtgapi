import contextlib
import copy
import logging
import os
import random
from collections.abc import Generator
from typing import Any

import testcontainers.core.config
from testcontainers.postgres import PostgresContainer

from mtgcobuilderapi.config.settings.base import ServiceConfigurationPrefixes
from mtgcobuilderapi.domain.card import MTGCard
from mtgcobuilderapi.domain.conversions import convert_pydantic_model_to_sqlalchemy_base
from tests.globals import DEFAULT_POSTGRES_CONTAINER_IMAGE, LOG_LEVEL

__LOGGING_CONFIGURED = False


class TemporaryEnvContext:
    def __init__(self, **kwargs: Any) -> None:
        self.env_vars = kwargs

    def __enter__(self) -> None:
        self.old_values = copy.deepcopy(os.environ)
        for key, value in self.env_vars.items():
            os.environ[key] = value

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:  # type: ignore
        os.environ = self.old_values


def setup_logging() -> None:
    """
    Sets up logging for the tests based on the LOG_LEVEL environment variable.
    """
    logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.root.handlers.clear()

    new_logger = logging.getLogger()
    new_logger.setLevel(LOG_LEVEL)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    new_logger.addHandler(stream_handler)
    new_logger.propagate = False
    logging.root = new_logger  # type: ignore
    testcontainers.core.waiting_utils.logger = new_logger
    testcontainers.core.container.logger = new_logger
    __LOGGING_CONFIGURED = True


@contextlib.contextmanager
def use_postgres_container(image: str = DEFAULT_POSTGRES_CONTAINER_IMAGE) -> Generator[PostgresContainer, None, None]:
    with PostgresContainer(image=image) as test_postgres_server:
        with TemporaryEnvContext(
            **{
                ServiceConfigurationPrefixes.DATABASE + "_CONNECTION_STRING": test_postgres_server.get_connection_url(
                    driver="asyncpg"
                )
            }
        ):
            yield test_postgres_server


def generate_random_card_ids(count: int) -> list[int]:
    """
    Generates a list of UNIQUE random card IDs for testing purposes.
    The IDs are generated in the range of 100 to 1000 and are constantly created
    until the specified count is reached.
    """
    random_card_ids: set[int] = set()
    while len(random_card_ids) < count:
        random_card_ids.add(random.randint(100, 1000))
    return list(random_card_ids)


MTGCARD_SQLALCHEMY_BASE = convert_pydantic_model_to_sqlalchemy_base(MTGCard)
