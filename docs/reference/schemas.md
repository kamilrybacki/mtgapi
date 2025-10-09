# Schemas

The JSON Schemas for key domain models are generated from Pydantic models.

Generation pipeline:

1. `scripts/export_schemas.py` writes raw schema JSON into `docs/_generated_schemas/*.schema.json`.
2. `scripts/update_schemas_markdown.py` embeds those schemas below.

Regenerate locally:

```bash
task export-schemas && python scripts/update_schemas_markdown.py
```

<!-- SCHEMAS:BEGIN -->
Generated schema documentation. Do not edit within markers; run scripts/update_schemas_markdown.py instead.

#### Summary

| Model | File | Size (bytes) | Top-level keys |
|-------|------|-------------|----------------|
| Mana Value | `mana_value.schema.json` | 1162 | 4 |
| MTG Card | `mtg_card.schema.json` | 9361 | 6 |
| MTGio Card | `mtgio_card.schema.json` | 6611 | 6 |

### Mana Value

???+ note "Mana Value JSON Schema"
    ```json
    {
      "description": "Represents the mana value of a Magic: The Gathering card.",
      "properties": {
        "generic": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "string"
            }
          ],
          "default": 0,
          "description": "Generic mana cost",
          "title": "Generic"
        },
        "colorless": {
          "default": 0,
          "description": "Colorless mana cost",
          "title": "Colorless",
          "type": "integer"
        },
        "white": {
          "default": 0,
          "description": "White mana cost",
          "title": "White",
          "type": "integer"
        },
        "blue": {
          "default": 0,
          "description": "Blue mana cost",
          "title": "Blue",
          "type": "integer"
        },
        "black": {
          "default": 0,
          "description": "Black mana cost",
          "title": "Black",
          "type": "integer"
        },
        "red": {
          "default": 0,
          "description": "Red mana cost",
          "title": "Red",
          "type": "integer"
        },
        "green": {
          "default": 0,
          "description": "Green mana cost",
          "title": "Green",
          "type": "integer"
        }
      },
      "title": "ManaValue",
      "type": "object"
    }
    ```

### MTG Card

???+ note "MTG Card JSON Schema"
    ```json
    {
      "$defs": {
        "Keyword": {
          "description": "Enumeration for different types of counters that can be on a Magic: The Gathering card.",
          "enum": [
            "Deathtouch",
            "Defender",
            "Double Strike",
            "Enchant",
            "Equip",
            "First Strike",
            "Flash",
            "Flying",
            "Haste",
            "Hexproof",
            "Indestructible",
            "Intimidate",
            "Forestwalk",
            "Islandwalk",
            "Mountainwalk",
            "Plainswalk",
            "Swampwalk",
            "Lifelink",
            "Protection",
            "Reach",
            "Shroud",
            "Trample",
            "Vigilance",
            "Ward",
            "Banding",
            "Rampage",
            "Cumulative Upkeep",
            "Flanking",
            "Phasing",
            "Buyback",
            "Shadow",
            "Cycling",
            "Echo",
            "Horsemanship",
            "Fading",
            "Kicker",
            "Flashback",
            "Madness",
            "Fear",
            "Morph",
            "Amplify",
            "Provoke",
            "Storm",
            "Affinity",
            "Entwine",
            "Modular",
            "Sunburst",
            "Bushido",
            "Soulshift",
            "Splice",
            "Offering",
            "Ninjutsu",
            "Epic",
            "Convoke",
            "Dredge",
            "Transmute",
            "Bloodthirst",
            "Haunt",
            "Replicate",
            "Forecast",
            "Graft",
            "Recover",
            "Ripple",
            "Split Second",
            "Suspend",
            "Vanishing",
            "Absorb",
            "Aura Swap",
            "Delve",
            "Fortify",
            "Frenzy",
            "Gravestorm",
            "Poisonous",
            "Transfigure",
            "Champion",
            "Changeling",
            "Evoke",
            "Hideaway",
            "Prowl",
            "Reinforce",
            "Conspire",
            "Persist",
            "Wither",
            "Retrace",
            "Devour",
            "Exalted",
            "Unearth",
            "Cascade",
            "Annihilator",
            "Level Up",
            "Rebound",
            "Umbra Armor",
            "Infect",
            "Battle Cry",
            "Living Weapon",
            "Undying",
            "Miracle",
            "Soulbond",
            "Overload",
            "Scavenge",
            "Unleash",
            "Cipher",
            "Evolve",
            "Extort",
            "Fuse",
            "Bestow",
            "Tribute",
            "Dethrone",
            "Hidden Agenda",
            "Outlast",
            "Prowess",
            "Dash",
            "Exploit",
            "Menace",
            "Renown",
            "Awaken",
            "Devoid",
            "Ingest",
            "Myriad",
            "Surge",
            "Skulk",
            "Emerge",
            "Escalate",
            "Melee",
            "Crew",
            "Fabricate",
            "Partner",
            "Undaunted",
            "Improvise",
            "Aftermath",
            "Embalm",
            "Eternalize",
            "Afflict",
            "Ascend",
            "Assist",
            "Jump-Start",
            "Mentor",
            "Afterlife",
            "Riot",
            "Spectacle",
            "Escape",
            "Companion",
            "Mutate",
            "Encore",
            "Boast",
            "Foretell",
            "Demonstrate",
            "Daybound and Nightbound",
            "Disturb",
            "Decayed",
            "Cleave",
            "Training",
            "Compleated",
            "Reconfigure",
            "Blitz",
            "Casualty",
            "Enlist",
            "Read Ahead",
            "Ravenous",
            "Squad",
            "Space Sculptor",
            "Visit",
            "Prototype",
            "Living Metal",
            "More Than Meets the Eye",
            "For Mirrodin!",
            "Toxic",
            "Backup",
            "Bargain",
            "Craft",
            "Disguise",
            "Solved",
            "Plot",
            "Saddle",
            "Spree",
            "Freerunning",
            "Gift",
            "Offspring",
            "Impending",
            "Exhaust",
            "Max Speed",
            "Start Your Engines!",
            "Harmonize",
            "Mobilize"
          ],
          "title": "Keyword",
          "type": "string"
        },
        "MTGCardAlias": {
          "description": "Represents a foreign name for a Magic: The Gathering card.",
          "properties": {
            "name": {
              "title": "Name",
              "type": "string"
            },
            "language": {
              "title": "Language",
              "type": "string"
            }
          },
          "required": [
            "name",
            "language"
          ],
          "title": "MTGCardAlias",
          "type": "object"
        },
        "MTGCardRuling": {
          "description": "Represents a ruling for a Magic: The Gathering card.",
          "properties": {
            "date": {
              "title": "Date",
              "type": "string"
            },
            "text": {
              "title": "Text",
              "type": "string"
            }
          },
          "required": [
            "date",
            "text"
          ],
          "title": "MTGCardRuling",
          "type": "object"
        },
        "ManaValue": {
          "description": "Represents the mana value of a Magic: The Gathering card.",
          "properties": {
            "generic": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "string"
                }
              ],
              "default": 0,
              "description": "Generic mana cost",
              "title": "Generic"
            },
            "colorless": {
              "default": 0,
              "description": "Colorless mana cost",
              "title": "Colorless",
              "type": "integer"
            },
            "white": {
              "default": 0,
              "description": "White mana cost",
              "title": "White",
              "type": "integer"
            },
            "blue": {
              "default": 0,
              "description": "Blue mana cost",
              "title": "Blue",
              "type": "integer"
            },
            "black": {
              "default": 0,
              "description": "Black mana cost",
              "title": "Black",
              "type": "integer"
            },
            "red": {
              "default": 0,
              "description": "Red mana cost",
              "title": "Red",
              "type": "integer"
            },
            "green": {
              "default": 0,
              "description": "Green mana cost",
              "title": "Green",
              "type": "integer"
            }
          },
          "title": "ManaValue",
          "type": "object"
        }
      },
      "description": "Represents a Magic: The Gathering card.",
      "properties": {
        "id": {
          "description": "Unique identifier for the card",
          "title": "Id",
          "type": "string"
        },
        "multiverse_id": {
          "description": "Multiverse ID of the card, if available",
          "title": "Multiverse Id",
          "type": "string"
        },
        "name": {
          "description": "Name of the card",
          "title": "Name",
          "type": "string"
        },
        "aliases": {
          "description": "List of foreign names for the card",
          "items": {
            "$ref": "#/$defs/MTGCardAlias"
          },
          "title": "Aliases",
          "type": "array"
        },
        "rulings": {
          "description": "List of rulings for the card",
          "items": {
            "$ref": "#/$defs/MTGCardRuling"
          },
          "title": "Rulings",
          "type": "array"
        },
        "mana_value": {
          "$ref": "#/$defs/ManaValue",
          "description": "Mana value of the card"
        },
        "types": {
          "description": "List of types the card belongs to",
          "items": {
            "type": "string"
          },
          "title": "Types",
          "type": "array"
        },
        "subtypes": {
          "description": "List of subtypes the card belongs to",
          "items": {
            "type": "string"
          },
          "title": "Subtypes",
          "type": "array"
        },
        "keywords": {
          "description": "List of counters on the card",
          "items": {
            "$ref": "#/$defs/Keyword"
          },
          "title": "Keywords",
          "type": "array"
        },
        "text": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": "",
          "description": "Text on the card, such as rules text or abilities",
          "title": "Text"
        },
        "flavor": {
          "default": "",
          "description": "Flavor text of the card, if any",
          "title": "Flavor",
          "type": "string"
        },
        "power": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Power of the creature card",
          "title": "Power"
        },
        "toughness": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Toughness of the creature card",
          "title": "Toughness"
        },
        "rarity": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Rarity of the card",
          "title": "Rarity"
        },
        "set_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Set name where the card belongs",
          "title": "Set Name"
        },
        "image_url": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": "",
          "description": "URL to the card's image",
          "title": "Image Url"
        }
      },
      "required": [
        "id",
        "multiverse_id",
        "name",
        "mana_value"
      ],
      "title": "MTGCard",
      "type": "object"
    }
    ```

### MTGio Card

???+ note "MTGio Card JSON Schema"
    ```json
    {
      "$defs": {
        "MTGCardAlias": {
          "description": "Represents a foreign name for a Magic: The Gathering card.",
          "properties": {
            "name": {
              "title": "Name",
              "type": "string"
            },
            "language": {
              "title": "Language",
              "type": "string"
            }
          },
          "required": [
            "name",
            "language"
          ],
          "title": "MTGCardAlias",
          "type": "object"
        },
        "MTGCardRuling": {
          "description": "Represents a ruling for a Magic: The Gathering card.",
          "properties": {
            "date": {
              "title": "Date",
              "type": "string"
            },
            "text": {
              "title": "Text",
              "type": "string"
            }
          },
          "required": [
            "date",
            "text"
          ],
          "title": "MTGCardRuling",
          "type": "object"
        }
      },
      "description": "Represents a Magic: The Gathering card with additional fields for MTGIO.",
      "properties": {
        "names": {
          "description": "List of names the card can have",
          "examples": [
            [
              "Lightning Bolt"
            ]
          ],
          "items": {
            "type": "string"
          },
          "title": "Names",
          "type": "array"
        },
        "mana_cost": {
          "description": "Mana cost of the card in {X}({C}*) format",
          "examples": [
            "{3}{W}{U}"
          ],
          "title": "Mana Cost",
          "type": "string"
        },
        "colors": {
          "description": "List of colors the card belongs to",
          "examples": [
            [
              "Red"
            ],
            [
              "Blue",
              "Red"
            ]
          ],
          "items": {
            "type": "string"
          },
          "title": "Colors",
          "type": "array"
        },
        "color_identity": {
          "description": "List of colors that define the card's identity (color codes, e.g. ['R', 'U'])",
          "examples": [
            [
              "R"
            ],
            [
              "R",
              "U"
            ]
          ],
          "items": {
            "type": "string"
          },
          "title": "Color Identity",
          "type": "array"
        },
        "rarity": {
          "default": "common",
          "description": "Rarity of the card (e.g., common, uncommon, rare, mythic)",
          "examples": [
            "common",
            "uncommon",
            "rare",
            "mythic"
          ],
          "maxLength": 10,
          "minLength": 1,
          "title": "Rarity",
          "type": "string"
        },
        "types": {
          "description": "List of types the card belongs to (e.g. Creature, Instant, Sorcery, Artifact, Enchantment, Land, Planeswalker)",
          "examples": [
            [
              "Creature"
            ],
            [
              "Instant"
            ]
          ],
          "items": {
            "type": "string"
          },
          "minItems": 1,
          "title": "Types",
          "type": "array"
        },
        "subtypes": {
          "description": "List of subtypes the card belongs to (e.g. Human, Wizard, Squirrel)",
          "examples": [
            [
              "Human"
            ],
            [
              "Rat",
              "Squirrel"
            ]
          ],
          "items": {
            "type": "string"
          },
          "title": "Subtypes",
          "type": "array"
        },
        "supertypes": {
          "description": "List of supertypes the card belongs to (e.g. Basic, Legendary, Snow, World, Ongoing)",
          "examples": [
            [
              "Legendary"
            ]
          ],
          "items": {
            "type": "string"
          },
          "title": "Supertypes",
          "type": "array"
        },
        "text": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Oracle text of the card. May contain mana symbols and other symbols.",
          "examples": [
            "Flying, Vigilance"
          ],
          "title": "Text"
        },
        "flavor": {
          "default": "",
          "description": "Flavor text of the card, if any",
          "examples": [
            "\"The storm is coming.\""
          ],
          "title": "Flavor",
          "type": "string"
        },
        "power": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Power of the creature card (e.g. '3', 'X')",
          "examples": [
            "3",
            "X"
          ],
          "title": "Power"
        },
        "toughness": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Toughness of the creature card (e.g. '3', 'X')",
          "examples": [
            "3",
            "X"
          ],
          "title": "Toughness"
        },
        "layout": {
          "default": "normal",
          "description": "Layout of the card (e.g., normal, split, flip, double-faced, token, plane, scheme, phenomenon, leveler, vanguard, aftermath)",
          "examples": [
            "normal",
            "split",
            "flip",
            "double-faced",
            "token",
            "plane",
            "scheme",
            "phenomenon",
            "leveler",
            "vanguard",
            "aftermath"
          ],
          "maxLength": 12,
          "minLength": 1,
          "title": "Layout",
          "type": "string"
        },
        "rulings": {
          "description": "List of rulings for the card",
          "items": {
            "$ref": "#/$defs/MTGCardRuling"
          },
          "title": "Rulings",
          "type": "array"
        },
        "foreign_names": {
          "description": "List of foreign names for the card",
          "items": {
            "$ref": "#/$defs/MTGCardAlias"
          },
          "title": "Foreign Names",
          "type": "array"
        },
        "printings": {
          "description": "List of sets the card has been printed in",
          "examples": [
            [
              "LEA",
              "2ED"
            ]
          ],
          "items": {
            "type": "string"
          },
          "title": "Printings",
          "type": "array"
        },
        "id": {
          "description": "Unique identifier for the card in the MTGIO database (SHA1 hash of setCode + cardName + cardImageName)",
          "examples": [
            "a1b2c3d4e5f6g7h8i9j0"
          ],
          "title": "Id",
          "type": "string"
        },
        "multiverse_id": {
          "default": "",
          "description": "Multiverse ID of the card, if available",
          "examples": [
            "123456"
          ],
          "title": "Multiverse Id",
          "type": "string"
        },
        "image_url": {
          "description": "URL to the card's image in the MTGIO database",
          "examples": [
            "http://example.com/image.jpg"
          ],
          "title": "Image Url",
          "type": "string"
        }
      },
      "required": [
        "mana_cost",
        "id",
        "image_url"
      ],
      "title": "MTGIOCard",
      "type": "object"
    }
    ```

<!-- SCHEMAS:END -->
