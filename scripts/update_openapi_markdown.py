"""
Embed the OpenAPI JSON document into reference/openapi.md.

Process:
1. Ensure docs/_generated_openapi/openapi.json exists (produced by export_openapi.py).
2. Produce a short summary section (endpoint counts by method, total paths, component schemas count if present).
3. Replace content between <!-- OPENAPI:BEGIN --> and <!-- OPENAPI:END --> markers.

Idempotent - safe to run multiple times. Avoids include-markdown plugin.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).parent.parent
OPENAPI_JSON = ROOT / "docs" / "_generated_openapi" / "openapi.json"
TARGET_MD = ROOT / "docs" / "reference" / "openapi.md"
BEGIN_MARK = "<!-- OPENAPI:BEGIN -->"
END_MARK = "<!-- OPENAPI:END -->"


def _load_spec() -> dict[str, Any]:
    if not OPENAPI_JSON.exists():  # pragma: no cover - runtime guard
        raise SystemExit("OpenAPI JSON not found. Run export-openapi first.")
    return cast("dict[str, Any]", json.loads(OPENAPI_JSON.read_text("utf-8")))


def _summarize(spec: dict[str, Any]) -> str:
    paths = spec.get("paths", {})
    method_counter: Counter[str] = Counter()
    for path_item in paths.values():
        for method in path_item:
            method_counter[method.upper()] += 1
    total_paths = len(paths)
    components = spec.get("components", {})
    schemas = components.get("schemas", {}) if isinstance(components, dict) else {}
    lines = ["#### Summary", "", f"Total paths: **{total_paths}**", ""]
    if method_counter:
        lines.append("Endpoint operations by method:")
        lines.append("")
        lines.append("| Method | Count |")
        lines.append("|--------|-------|")
        lines.extend([f"| {m} | {method_counter[m]} |" for m in sorted(method_counter)])
        lines.append("")
    lines.append(f"Component schemas: **{len(schemas)}**")
    return "\n".join(lines)


def _inject(content: str, replacement: str) -> str:
    if BEGIN_MARK not in content or END_MARK not in content:
        raise RuntimeError("openapi.md missing required BEGIN/END markers")
    pattern = re.compile(rf"{re.escape(BEGIN_MARK)}.*?{re.escape(END_MARK)}", re.DOTALL)
    return pattern.sub(f"{BEGIN_MARK}\n{replacement}\n{END_MARK}", content)


def _per_path_blocks(spec: dict[str, Any]) -> str:
    """
    Render each path and its operations inside a collapsible block.

    Keeps the page scannable while still exposing structured JSON for each endpoint.
    """
    paths = spec.get("paths", {})
    blocks: list[str] = []
    for route, operations in sorted(paths.items()):
        # operations is a dict like {"get": {...}, "post": {...}}
        op_lines: list[str] = []
        for method, op_spec in sorted(operations.items()):
            snippet = json.dumps(op_spec, indent=2, ensure_ascii=False)
            op_lines.append("    " + f"#### {method.upper()}\n")
            op_lines.append("    ```json")
            op_lines.extend(["    " + line for line in snippet.splitlines()])
            op_lines.append("    ```\n")
        blocks.append("\n".join([f'??? details "{route}"', *op_lines]))
    return "\n\n".join(blocks)


def main() -> None:  # pragma: no cover - thin wrapper
    spec = _load_spec()
    summary = _summarize(spec)
    full_json = json.dumps(spec, indent=2, ensure_ascii=False)
    per_path = _per_path_blocks(spec)
    generated = (
        "Generated OpenAPI documentation. Do not edit within markers; run scripts/update_openapi_markdown.py instead.\n\n"
        f"{summary}\n\n"
        "#### Full Specification\n\n"
        '???+ note "Complete OpenAPI JSON"\n'
        "    ```json\n" + "\n".join([f"    {line}" for line in full_json.splitlines()]) + "\n    ```\n\n"
        "#### Endpoints\n\n"
        f"{per_path}\n"
    )
    original = TARGET_MD.read_text("utf-8")
    updated = _inject(original, generated)
    if updated != original:
        TARGET_MD.write_text(updated, "utf-8")


if __name__ == "__main__":  # pragma: no cover
    main()
