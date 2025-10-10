"""Tests for schema export helper script.

Focused on verifying that the export function writes files to the expected
locations. Paths are redirected to a temporary directory to avoid polluting
real docs output during the test run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Tuple

import pytest

import scripts.export_schemas as export_schemas


@pytest.fixture()
def temp_docs_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "docs" / "_generated"
    # Patch schema export output dir
    monkeypatch.setattr(export_schemas, "OUTPUT_DIR", target / "schemas", raising=False)
    export_schemas.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return target


def _collect_files(base: Path) -> set[Path]:
    return {p for p in base.rglob("*.json") if p.is_file()}


def test_schema_export_writes_all_models(temp_docs_dir: Path) -> None:
    results: Iterable[Tuple[str, Path]] = export_schemas.export()
    produced = {name for name, _ in results}
    # Ensure each expected filename was produced
    assert produced == set(export_schemas.MODELS.keys())
    # Ensure files exist & contain valid JSON
    for filename in produced:
        path = export_schemas.OUTPUT_DIR / filename
        assert path.exists(), f"Missing exported schema file: {path}"
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        assert "$schema" in loaded or "title" in loaded  # minimal sanity
