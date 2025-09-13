from typing import Any


class InvalidServiceDefinitionError(TypeError):
    """Exception raised when a service definition is invalid."""


class DatabaseConnectionError(Exception):
    """Exception raised when a database connection fails."""


class InvalidPydanticModelError(Exception):
    """Exception raised when invalid Pydantic model is encountered"""


class EmptyPydanticModelError(InvalidPydanticModelError):
    """Exception raised when Pydantic model is empty"""

    __message__ = "Empty Pydantic model"

    def __init__(self, msg=__message__, *args: Any, **kwargs: Any) -> "EmptyPydanticModelError":  # type: ignore
        super().__init__(msg, *args, **kwargs)
