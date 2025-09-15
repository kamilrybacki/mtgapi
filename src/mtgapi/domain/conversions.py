import enum
import logging
from types import NoneType, UnionType
from typing import get_args, get_origin

import sqlalchemy
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeBase

from mtgapi.common.exceptions import EmptyPydanticModelError
from mtgapi.config.settings.defaults import CONVERTED_PYDANTIC_MODEL_SUFFIX


class TypeAnnotationToSQLFieldType(enum.Enum):
    """
    Class which maps the type annotations of Pydantic models to SQLAlchemy field types
    e.g. the int type hint gets mapped to the sqlalchemy.Integer type for a column
    """

    int = sqlalchemy.Integer
    str = sqlalchemy.String
    float = sqlalchemy.Float
    bool = sqlalchemy.Boolean
    datetime = sqlalchemy.DateTime
    bytes = sqlalchemy.LargeBinary
    list = sqlalchemy.ARRAY
    dict = sqlalchemy.JSON


def convert_pydantic_model_to_sqlalchemy_base(model: type[BaseModel]) -> type[DeclarativeBase]:  # noqa: PLR0912
    """
    Converts a Pydantic model to a SQLAlchemy base model.

    :param model: Pydantic model to convert.
    :return: SQLAlchemy base model class.
    :raises EmptyPydanticModel: If Pydantic model is empty.
    """
    base = declarative_base(class_registry={})

    column_definitions: dict[str, sqlalchemy.Column] = {}
    if len(model.model_fields.keys()) == 0:
        raise EmptyPydanticModelError

    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        if field_type is None:
            logging.debug(f"[DEBUG] Field {field_name} has no annotation")
            continue

        if isinstance(field_type, UnionType):
            field_type = get_args(field_type)[0]  # type: ignore

        try:
            type_name = get_origin(field_type).__name__  # type: ignore
        except AttributeError:
            type_name = field_type.__name__

        logging.info(f"[DEBUG] Field {field_name} is {type_name}")

        if type_name not in TypeAnnotationToSQLFieldType.__members__:
            logging.debug(f"[DEBUG] Field [[{field_name}]] type {field_type} is not a primitive! Using JSON type.")
            mapped_column_type = TypeAnnotationToSQLFieldType.dict
        else:
            mapped_column_type = TypeAnnotationToSQLFieldType[type_name]

        if mapped_column_type == TypeAnnotationToSQLFieldType.list:
            type_arguments = get_args(field_type)
            field_nested_type_name = type_arguments[0].__name__ if type_arguments else NoneType.__name__
            if field_nested_type_name not in TypeAnnotationToSQLFieldType.__members__:
                logging.debug(
                    f"[DEBUG] Field [[{field_name}]] nested members type is not a primitive! Using JSON type."
                )
                nested_type = TypeAnnotationToSQLFieldType.dict.value
            else:
                nested_type = TypeAnnotationToSQLFieldType[field_nested_type_name].value  # type: ignore

            mapped_column_type = mapped_column_type.value(item_type=nested_type)
        else:
            mapped_column_type = mapped_column_type.value

        new_column_from_field = sqlalchemy.Column(type_=mapped_column_type)  # type: ignore
        column_definitions[field_name] = new_column_from_field

    if "id" not in column_definitions:
        logging.debug("[DEBUG] No 'id' field found in the Pydantic model, adding an auto-incrementing primary key.")
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
