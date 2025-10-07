"""
Export the FastAPI OpenAPI schema to ``docs/_generated_openapi/openapi.json``.

The application instance is imported from ``mtgapi.entrypoint``; the resulting
OpenAPI document is JSON-encoded for inclusion in published documentation.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from mtgapi.entrypoint import API

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "_generated_openapi"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUTPUT_DIR / "openapi.json"

def export() -> Path:
    """Generate and write the OpenAPI schema; return the path written."""
    schema = API.openapi()
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(jsonable_encoder(schema), f, indent=2, ensure_ascii=False)
    return OUT_FILE

if __name__ == "__main__":  # pragma: no cover
    # Avoid stdout noise (Ruff T201) - just ensure export occurs.
    export()
