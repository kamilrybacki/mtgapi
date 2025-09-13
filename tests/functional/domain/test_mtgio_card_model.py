import pytest

from tests.common.samples import LIGHTNING_BOLT_MTGIO_CARD_DATA
from mtgcobuilderapi.domain.card import CARD_POSSIBLE_LAYOUTS, MTGIOCard, ManaValue, Keyword

from pydantic import ValidationError
from typing import Any


def test_mtg_iocard_valid() -> None:
    card = MTGIOCard(**LIGHTNING_BOLT_MTGIO_CARD_DATA)
    for field, expected in LIGHTNING_BOLT_MTGIO_CARD_DATA.items():
        actual = getattr(card, field)
        if field in {"rulings", "foreign_names"} and expected:
            assert actual[0] == expected[0]
        elif field == "printings":
            assert set(actual) == set(expected)
        else:
            assert actual == expected


@pytest.mark.parametrize(
    "mana_cost,should_raise",
    [
        ("{2}{W}{U}", False),  # valid
        ("{10}{G}", False),  # valid
        ("{X}{R}", False),  # valid (if X is allowed)
        ("{0}", False),  # valid
        ("ABC", True),  # invalid
        ("{1}{Z}", True),  # invalid color
        ("{-1}{W}", True),  # invalid negative
        ("{}", True),  # invalid empty braces
    ],
)
def test_check_mana_cost_format_format(mana_cost: str, should_raise: bool) -> None:
    if should_raise:
        with pytest.raises(ValueError):
            MTGIOCard.check_mana_cost_format(value=mana_cost)
    else:
        MTGIOCard.check_mana_cost_format(value=mana_cost)


def test_total_mana_value_with_zero_values() -> None:
    mana_value = ManaValue(colorless=0, white=0, blue=0, black=0, red=0, green=0)
    assert mana_value.total() == 0


def test_raises_for_empty_printings_list() -> None:
    with pytest.raises(ValueError, match="Printings cannot be empty."):
        MTGIOCard.validate_printings([])


def test_error_for_non_string_printings() -> None:
    with pytest.raises(ValueError, match="All printings must be strings."):
        MTGIOCard.validate_printings(["Set1", 123, "Set3"])


def test_error_for_empty_string_in_printings() -> None:
    with pytest.raises(ValueError, match="Printings cannot contain empty strings."):
        MTGIOCard.validate_printings(["Set1", "", "Set3"])


def test_sorted_unique_printings() -> None:
    result = MTGIOCard.validate_printings(["Set3", "Set1", "Set2", "Set1"])
    assert result == ["SET1", "SET2", "SET3"]


# B is Black, W is White, G is Green, U is Blue, R is Red
@pytest.mark.parametrize(
    "mana_cost,expected_generic,expected_colorless,expected_white,expected_green,expected_blue,expected_black,expected_red",
    [
        ("{2}{W}{U}", 2, 0, 1, 0, 1, 0, 0),  # 2 generic, 1 white, 1 blue
        ("{10}{G}", 10, 0, 0, 1, 0, 0, 0),  # 10 generic, 1 green
        ("{X}{R}", "X", 0, 0, 0, 0, 0, 1),  # X is treated as generic here
        ("{0}", 0, 0, 0, 0, 0, 0, 0),  # Zero mana cost
        ("{3}{B}{R}", 3, 0, 0, 0, 0, 1, 1),  # 3 generic, 1 blue, 1 red
        ("{5}{W}{G}", 5, 0, 1, 1, 0, 0, 0),  # Mixed costs with white and green
        ("{1}{C}{C}", 1, 2, 0, 0, 0, 0, 0),  # Colorless mana
    ],
)
@pytest.mark.offline
def test_mtgio_cost_string_with_multiple_digits_correctly(
    mana_cost: str,
    expected_generic: int | str,
    expected_colorless: int,
    expected_white: int,
    expected_green: int,
    expected_blue: int,
    expected_black: int,
    expected_red: int,
) -> None:
    mana_value = ManaValue.from_mtgio_cost_string(mana_cost)
    assert mana_value.generic == expected_generic
    assert mana_value.colorless == expected_colorless
    assert mana_value.white == expected_white
    assert mana_value.green == expected_green
    assert mana_value.blue == expected_blue
    assert mana_value.black == expected_black
    assert mana_value.red == expected_red


@pytest.mark.offline
def test_error_for_negative_colorless_value() -> None:
    with pytest.raises(ValueError, match="Invalid mana color: -1 in cost string '{-1}{W}'"):
        ManaValue.from_mtgio_cost_string("{-1}{W}")


@pytest.mark.parametrize(
    "text,expected_keywords",
    [
        ("Flying, Trample, and Haste are abilities of this card.", [Keyword.FLYING, Keyword.TRAMPLE, Keyword.HASTE]),
        ("Vigilance and Lifelink.", [Keyword.VIGILANCE, Keyword.LIFELINK]),
        ("", []),
        (None, []),
        ("This card has no abilities.", []),
    ],
)
@pytest.mark.offline
def test_keywords_from_card_text_correctly(text: str, expected_keywords: list[Keyword]) -> None:
    keywords = MTGIOCard.extract_keywords_from_card_text(text)
    for keyword in expected_keywords:
        assert keyword in keywords
    assert len(keywords) == len(expected_keywords)


@pytest.mark.offline
def test_empty_keywords_for_none_text() -> None:
    keywords = MTGIOCard.extract_keywords_from_card_text(None)
    assert keywords == []


@pytest.mark.parametrize(
    "field, value, should_raise",
    [
        ("names", ["Name"], False),
        ("types", ["Instant"], False),
        ("subtypes", ["Spell"], False),
        ("layout", "normal", False),
        ("layout", "", True),
        ("layout", "x" * (max(len(l) for l in CARD_POSSIBLE_LAYOUTS) + 1), True),
        ("printings", [], True),
        ("printings", ["lea", "LEA", "2ed"], False),
        ("printings", ["LEA", 123], True),
        ("printings", ["LEA", ""], True),
        ("names", [], True),
        ("types", [], True),
        ("subtypes", [], False),
        ("layout", "", True),
        ("layout", "x" * (max(len(l) for l in CARD_POSSIBLE_LAYOUTS) + 1), True),
        ("printings", [], True),
        ("printings", ["lea", "LEA", "2ed"], False),
        ("printings", ["LEA", 123], True),
        ("printings", ["LEA", ""], True),
    ],
)
@pytest.mark.offline
def test_mtgiocard_field_validations(field: str, value: Any, should_raise: bool) -> None:
    kwargs = {
        "names": ["Name"],
        "mana_cost": "{R}",
        "colors": [],
        "color_identity": [],
        "types": ["Instant"],
        "subtypes": ["Spell"],
        "id": "id",
        "image_url": "url",
        field: value,
    }

    if should_raise:
        with pytest.raises(ValidationError):
            MTGIOCard(**kwargs)
