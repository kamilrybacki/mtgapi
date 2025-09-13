import re

import pytest
from pydantic import BaseModel

from mtgcobuilderapi.common.exceptions import EmptyPydanticModelError
from mtgcobuilderapi.domain.card import MTGCard
from mtgcobuilderapi.domain.conversions import (
    TypeAnnotationToSQLFieldType,
    convert_pydantic_model_to_sqlalchemy_base,
)
from tests.common.samples import LIGHTNING_BOLT_MTG_CARD_DATA


@pytest.mark.offline
def test_if_converts_pydantic_model_with_valid_fields() -> None:
    class SamplePydanticModel(BaseModel):
        id: int
        name: str
        is_active: bool | None

    sqlalchemy_model = convert_pydantic_model_to_sqlalchemy_base(SamplePydanticModel)
    assert sqlalchemy_model.__tablename__ == SamplePydanticModel.__name__.lower()
    assert hasattr(sqlalchemy_model, "id")
    assert isinstance(sqlalchemy_model.id.type, TypeAnnotationToSQLFieldType.int.value)
    assert hasattr(sqlalchemy_model, "name")
    assert isinstance(sqlalchemy_model.name.type, TypeAnnotationToSQLFieldType.str.value)
    assert hasattr(sqlalchemy_model, "is_active")
    assert isinstance(sqlalchemy_model.is_active.type, TypeAnnotationToSQLFieldType.bool.value)


@pytest.mark.offline
def test_converting_model_with_list_field() -> None:
    class SamplePydanticModelWithList(BaseModel):
        id: int
        tags: list[str]

    sqlalchemy_model = convert_pydantic_model_to_sqlalchemy_base(SamplePydanticModelWithList)
    assert sqlalchemy_model.__tablename__ == SamplePydanticModelWithList.__name__.lower()
    assert hasattr(sqlalchemy_model, "id")
    assert isinstance(sqlalchemy_model.id.type, TypeAnnotationToSQLFieldType.int.value)
    assert hasattr(sqlalchemy_model, "tags")
    assert isinstance(sqlalchemy_model.tags.type, TypeAnnotationToSQLFieldType.list.value)
    assert isinstance(sqlalchemy_model.tags.type.item_type, TypeAnnotationToSQLFieldType.str.value)


@pytest.mark.offline
def test_if_handles_empty_pydantic_model() -> None:
    class EmptyModel(BaseModel):
        pass

    with pytest.raises(EmptyPydanticModelError, match=EmptyPydanticModelError.__message__):
        convert_pydantic_model_to_sqlalchemy_base(EmptyModel)


@pytest.mark.offline
@pytest.mark.order(after=["test_if_converts_pydantic_model_with_valid_fields", "test_if_handles_empty_pydantic_model"])
def test_if_data_held_by_both_models_is_equal(caplog: pytest.LogCaptureFixture) -> None:
    mtg_card_sql_model = convert_pydantic_model_to_sqlalchemy_base(MTGCard)

    assert mtg_card_sql_model.__tablename__ == MTGCard.__name__.lower()

    for line in caplog.text.splitlines():
        if "JSON" in line:
            # Find field name enclosed in [[ and ]] brackets
            match = re.search(r"\[\[(.*?)\]\]", line)
            if match is not None:
                non_primitive_field_name = match.group(1)
                assert hasattr(mtg_card_sql_model, non_primitive_field_name)
                assert isinstance(
                    getattr(mtg_card_sql_model, non_primitive_field_name).type, TypeAnnotationToSQLFieldType.dict.value
                ), f"Field {non_primitive_field_name} should be of type dict, but is not."
    assert hasattr(mtg_card_sql_model, "id")

    original_model_instance = MTGCard(**LIGHTNING_BOLT_MTG_CARD_DATA)  # type: ignore
    sqlalchemy_model_instance = mtg_card_sql_model(**LIGHTNING_BOLT_MTG_CARD_DATA)

    for field in MTGCard.model_fields.keys():
        original_value = getattr(original_model_instance, field)
        sqlalchemy_value = getattr(sqlalchemy_model_instance, field)
        assert original_value == sqlalchemy_value, (
            f"Field {field} does not match: {original_value} != {sqlalchemy_value}"
        )
