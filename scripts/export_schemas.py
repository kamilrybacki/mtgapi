"""
Export JSON Schemas for publicly relevant domain models.

Currently exports the following domain models:
    - MTGCard
    - MTGIOCard
    - ManaValue

Schemas are written to ``docs/_generated_schemas/*.json`` for inclusion in the
documentation site (embedded via the include-markdown plugin).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Tuple

from mtgapi.domain.card import MTGCard, MTGIOCard, ManaValue

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "_generated_schemas"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS: Dict[str, Any] = {
    "mtg_card.schema.json": MTGCard,
    "mtgio_card.schema.json": MTGIOCard,
    "mana_value.schema.json": ManaValue,
}

def _get_schema(model: Any) -> Dict[str, Any]:
    """Return a JSON schema for the given Pydantic model.

    Uses ``model_json_schema`` (Pydantic v2). If running under a subtly
    different environment (type checker / plugin discrepancy), falls back to
    ``schema()`` to satisfy mypy attr checks.
    """
    if hasattr(model, "model_json_schema"):
        return getattr(model, "model_json_schema")()  # type: ignore[no-any-return]
    if hasattr(model, "schema"):
        return getattr(model, "schema")()  # type: ignore[no-any-return]
    raise AttributeError(f"Model {model!r} lacks a known schema export method")


def export() -> Iterable[Tuple[str, Path]]:
    """Export all configured model schemas.

    Returns an iterable of (filename, path) pairs for potential logging or
    downstream processing.
    """
    for filename, model in MODELS.items():
        schema = _get_schema(model)
        out_path = OUTPUT_DIR / filename
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        yield filename, out_path

if __name__ == "__main__":  # pragma: no cover
    # Intentionally avoid prints (Ruff T201). A caller / CI step can echo results
    # if desired; here we just force materialization.
    list(export())
