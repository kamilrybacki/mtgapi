import enum
import logging
from types import NoneType
from typing import Any, get_args, get_origin

import sqlalchemy
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeBase

from mtgapi.common.exceptions import EmptyPydanticModelError
from mtgapi.config.settings.defaults import CONVERTED_PYDANTIC_MODEL_SUFFIX

logger = logging.getLogger(__name__)


class TypeAnnotationToSQLFieldType(enum.Enum):
    """Backward-compatible enum used by tests to assert mapped SQLAlchemy types."""

    int = sqlalchemy.Integer
    str = sqlalchemy.String
    float = sqlalchemy.Float
    bool = sqlalchemy.Boolean
    datetime = sqlalchemy.DateTime
    bytes = sqlalchemy.LargeBinary
    list = sqlalchemy.ARRAY
    dict = sqlalchemy.JSON


# Internal mapping drives conversion logic (mirrors enum values)
PRIMITIVE_TYPE_MAP: dict[str, Any] = {
    name: member.value for name, member in TypeAnnotationToSQLFieldType.__members__.items()
}


def convert_pydantic_model_to_sqlalchemy_base(model: type[BaseModel]) -> type[DeclarativeBase]:  # noqa: PLR0912
    """
    Converts a Pydantic model to a SQLAlchemy base model.

    :param model: Pydantic model to convert.
    :return: SQLAlchemy base model class.
    :raises EmptyPydanticModel: If Pydantic model is empty.
    """
    base = declarative_base(class_registry={})

    column_definitions: dict[str, sqlalchemy.Column[Any]] = {}
    if len(model.model_fields.keys()) == 0:
        raise EmptyPydanticModelError

    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        if field_type is None:
            logger.debug("Field %s has no annotation", field_name)
            continue

        origin_union = get_origin(field_type)
        # Unwrap Optional/Union: take first non-None argument
        if origin_union is not None and origin_union is getattr(field_type, "__class__", object()):
            union_args = [a for a in get_args(field_type) if a is not type(None)]
            if union_args:
                field_type = union_args[0]

        origin = get_origin(field_type)  # e.g. list[int]
        if origin is not None:  # generic alias like list[int]
            type_name = origin.__name__
        else:
            # Might be a class/typeobject
            type_name = getattr(field_type, "__name__", field_type.__class__.__name__)

        logger.debug("Field %s is %s", field_name, type_name)

        if type_name not in PRIMITIVE_TYPE_MAP:
            logger.debug("Field [[%s]] type %s not primitive. Using JSON.", field_name, field_type)
            sa_type: Any = PRIMITIVE_TYPE_MAP["dict"]
        else:
            sa_type = PRIMITIVE_TYPE_MAP[type_name]

        if sa_type is PRIMITIVE_TYPE_MAP["list"]:
            type_args = get_args(field_type)
            nested_type_name = type_args[0].__name__ if type_args else NoneType.__name__
            if nested_type_name not in PRIMITIVE_TYPE_MAP:
                logger.debug(
                    "Field [[%s]] nested member type %s not primitive. Using JSON element type.",
                    field_name,
                    nested_type_name,
                )
                element_type: Any = PRIMITIVE_TYPE_MAP["dict"]
            else:
                element_type = PRIMITIVE_TYPE_MAP[nested_type_name]
            # build an ARRAY of the element type
            resolved_column_type: Any = sa_type(element_type)
        else:
            resolved_column_type = sa_type

        new_column_from_field: sqlalchemy.Column[Any] = sqlalchemy.Column(type_=resolved_column_type)
        column_definitions[field_name] = new_column_from_field

    if "id" not in column_definitions:
        logger.debug("No 'id' field found in the Pydantic model, adding an auto-incrementing primary key.")
        column_definitions["id"] = sqlalchemy.Column(
            type_=sqlalchemy.Integer,
        )

    column_definitions["id"].primary_key = True
    column_definitions["id"].nullable = False

    class _NewModelColumnsMeta: ...

    for column_name, column_type in column_definitions.items():
        setattr(_NewModelColumnsMeta, column_name, column_type)

    class _NewModel(_NewModelColumnsMeta, base):  # type: ignore
        __tablename__ = model.__name__.lower()
        __table_args__ = {"extend_existing": True}  # noqa: RUF012

    _NewModel.__name__ = f"{model.__name__}{CONVERTED_PYDANTIC_MODEL_SUFFIX}"

    return _NewModel
