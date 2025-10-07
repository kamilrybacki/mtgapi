"""Export the FastAPI OpenAPI schema to docs/_generated_openapi/openapi.json.

This script imports the application instance from mtgapi.entrypoint and writes the schema.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from mtgapi.entrypoint import API

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "_generated_openapi"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUTPUT_DIR / "openapi.json"

def export() -> None:
    schema = API.openapi()
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(jsonable_encoder(schema), f, indent=2, ensure_ascii=False)
    print(f"Exported OpenAPI schema -> {OUT_FILE}")

if __name__ == "__main__":  # pragma: no cover
    export()
