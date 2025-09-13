import os

from PIL import Image

from mtgcobuilderapi.domain.card import ManaValue
from tests.globals import ASSETS_DIRECTORY

LIGHTNING_BOLT_MTGIO_CARD_DATA = {
    "names": ["Lightning Bolt"],
    "mana_cost": "{R}",
    "colors": ["Red"],
    "color_identity": ["R"],
    "types": ["Instant"],
    "subtypes": ["Spell"],
    "supertypes": ["Basic"],
    "text": "Deal 3 damage to any target.",
    "layout": "normal",
    "rulings": [{"date": "2020-01-01", "text": "Sample ruling"}],
    "foreign_names": [{"name": "Foudre", "language": "French"}],
    "printings": ["LEA", "2ED"],
    "id": "a1b2c3d4e5f6g7h8i9j0",
    "image_url": "http://example.com/image.jpg",
}

LIGHTNING_BOLT_MTG_CARD_DATA = {
    "name": "Lightning Bolt",
    "id": "a1b2c3d4e5f6g7h8i9j0",
    "aliases": [],
    "rulings": [],
    "mana_value": ManaValue(colorless=0, red=1),
    "types": ["Instant"],
    "subtypes": ["Spell"],
    "keywords": [],
    "text": "Deal 3 damage to any target.",
    "flavor": "",
    "power": None,
    "toughness": None,
    "rarity": "Common",
    "set_name": "Test Set",
    "image_url": "http://example.com/image.jpg",
}

TEST_MTGIO_CARD_ID = 597
TEST_MTGIO_CARD_IMAGE = Image.open(os.path.join(ASSETS_DIRECTORY, f"card_{TEST_MTGIO_CARD_ID}.webp"))
