"""
Generate the schemas section in docs/schemas.md with embedded JSON.

Process:
1. Scan docs/_generated_schemas/*.json
2. Build a summary table (Model | File | Size (bytes) | Top-level keys)
3. Embed each schema as a fenced JSON block under its own heading.
4. Replace content between <!-- SCHEMAS:BEGIN --> and <!-- SCHEMAS:END --> markers in docs/schemas.md

Safe to run multiple times (idempotent). Avoids mkdocs-include-markdown dependency for these files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = ROOT / "docs" / "_generated_schemas"
TARGET_MD = ROOT / "docs" / "reference" / "schemas.md"
BEGIN_MARK = "<!-- SCHEMAS:BEGIN -->"
END_MARK = "<!-- SCHEMAS:END -->"


def _load_schema_files() -> list[Path]:
    return sorted(SCHEMAS_DIR.glob("*.schema.json"))


def _model_name_from_filename(path: Path) -> str:
    base = path.name.replace(".schema.json", "")
    return base.replace("_", " ").title().replace("Mtg", "MTG")


def _summary_table(schema_paths: list[Path]) -> str:
    lines = ["| Model | File | Size (bytes) | Top-level keys |", "|-------|------|-------------|----------------|"]
    for p in schema_paths:
        data = json.loads(p.read_text("utf-8"))
        top_keys = len(data.keys())
        lines.append(f"| {_model_name_from_filename(p)} | `{p.name}` | {p.stat().st_size} | {top_keys} |")
    return "\n".join(lines)


def _schema_blocks(schema_paths: list[Path]) -> str:
    blocks: list[str] = []
    for p in schema_paths:
        model_name = _model_name_from_filename(p)
        json_text = json.dumps(json.loads(p.read_text("utf-8")), indent=2, ensure_ascii=False)
        blocks.append(f"### {model_name}\n\n```json\n{json_text}\n```\n")
    return "\n".join(blocks)


def _inject(content: str, replacement: str) -> str:
    if BEGIN_MARK not in content or END_MARK not in content:
        raise RuntimeError("schemas.md missing required BEGIN/END markers")
    pattern = re.compile(rf"{re.escape(BEGIN_MARK)}.*?{re.escape(END_MARK)}", re.DOTALL)
    return pattern.sub(f"{BEGIN_MARK}\n{replacement}\n{END_MARK}", content)


def main() -> None:
    schema_paths = _load_schema_files()
    if not schema_paths:
        raise SystemExit("No schema files found in docs/_generated_schemas. Run export_schemas first.")
    summary = _summary_table(schema_paths)
    blocks = _schema_blocks(schema_paths)
    generated = (
        "Generated schema documentation. Do not edit within markers; run scripts/update_schemas_markdown.py instead.\n\n"
        "#### Summary\n\n"
        f"{summary}\n\n"
        f"{blocks}"
    )
    original = TARGET_MD.read_text("utf-8")
    updated = _inject(original, generated)
    if updated != original:
        TARGET_MD.write_text(updated, "utf-8")


if __name__ == "__main__":  # pragma: no cover
    main()
