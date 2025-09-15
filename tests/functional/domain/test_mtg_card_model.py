import pytest
from pydantic import ValidationError

from mtgapi.domain.card import MTGCard, MTGIOCard
from tests.common.samples import LIGHTNING_BOLT_MTG_CARD_DATA, LIGHTNING_BOLT_MTGIO_CARD_DATA


@pytest.mark.offline
def test_mtgcard_valid() -> None:
    card = MTGCard(**LIGHTNING_BOLT_MTG_CARD_DATA)  # type: ignore
    for field, expected in LIGHTNING_BOLT_MTG_CARD_DATA.items():
        actual = getattr(card, field)
        if field == "keywords":
            assert set(actual) == set(expected)  # type: ignore
        else:
            assert actual == expected


@pytest.mark.offline
def test_mtgcard_str() -> None:
    card = MTGCard(**LIGHTNING_BOLT_MTG_CARD_DATA)  # type: ignore
    assert (
        str(card)
        == f"{LIGHTNING_BOLT_MTG_CARD_DATA['name']} ({LIGHTNING_BOLT_MTG_CARD_DATA['id']}) - {LIGHTNING_BOLT_MTG_CARD_DATA['set_name']}"
    )


@pytest.mark.offline
def test_mtgcard_from_mtgio_card() -> None:
    mtgio_card = MTGIOCard(**LIGHTNING_BOLT_MTGIO_CARD_DATA)  # type: ignore
    card = MTGCard.from_mtgio_card(mtgio_card)

    assert isinstance(card, MTGCard)
    assert card.id == mtgio_card.id
    assert card.id == LIGHTNING_BOLT_MTG_CARD_DATA["id"]

    assert card.name == mtgio_card.names[0]
    assert card.name == LIGHTNING_BOLT_MTG_CARD_DATA["name"]


@pytest.mark.offline
def test_mtgcard_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        MTGCard(  # type: ignore
            id="abc123",
            name="Test Card",
            # missing mana_value
            types=[],
            subtypes=[],
            keywords=[],
        )
