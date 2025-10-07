"""Export JSON Schemas for publicly relevant domain models.

Currently exports:
- MTGCard
- MTGIOCard
- ManaValue

Schemas are written to docs/_generated_schemas/*.json for inclusion in documentation.
"""
from __future__ import annotations

import json
from pathlib import Path

from mtgapi.domain.card import MTGCard, MTGIOCard, ManaValue

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "_generated_schemas"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    "mtg_card.schema.json": MTGCard,
    "mtgio_card.schema.json": MTGIOCard,
    "mana_value.schema.json": ManaValue,
}

def export() -> None:
    for filename, model in MODELS.items():
        schema = model.model_json_schema()  # Pydantic v2 method
        out_path = OUTPUT_DIR / filename
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        print(f"Exported {model.__name__} schema -> {out_path}")

if __name__ == "__main__":  # pragma: no cover
    export()
