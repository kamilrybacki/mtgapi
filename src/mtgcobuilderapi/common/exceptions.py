from typing import Any


class InvalidServiceDefinitionError(TypeError):
    """Exception raised when a service definition is invalid."""


class DatabaseConnectionError(Exception):
    """Exception raised when a database connection fails."""


class InvalidPydanticModel(Exception):
    """Exception raised when invalid Pydantic model is encountered"""


class EmptyPydanticModel(InvalidPydanticModel):
    """Exception raised when Pydantic model is empty"""

    __message__ = "Empty Pydantic model"

    def __init__(self, msg=__message__, *args: Any, **kwargs: Any) -> "EmptyPydanticModel":
        super().__init__(msg, *args, **kwargs)
