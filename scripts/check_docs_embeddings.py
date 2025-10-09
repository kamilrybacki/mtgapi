"""
Check that embedded schema and OpenAPI markdown sections are up to date.

Process:
1. Run export tasks (schemas + openapi) to generate fresh JSON artifacts.
2. Run embedding scripts to update markdown in-place.
3. Use git to detect working tree changes. If any tracked docs/reference/*.md changed, exit 1.

Intended usage: CI guard / local pre-commit sanity.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_REF = ROOT / "docs" / "reference"
TARGET_FILES = [DOCS_REF / "schemas.md", DOCS_REF / "openapi.md"]


def _run(cmd: list[str]) -> None:
    """
    Run a command, raising on failure.

    Commands here are internal (no user input), so Bandit warning S603 is a
    false positive for this controlled context.
    """
    subprocess.run(cmd, check=True)  # noqa: S603


def main() -> int:
    # Step 1/2: regenerate artifacts + embeddings
    _run([sys.executable, "scripts/export_schemas.py"])
    _run([sys.executable, "scripts/export_openapi.py"])
    _run([sys.executable, "scripts/update_schemas_markdown.py"])
    _run([sys.executable, "scripts/update_openapi_markdown.py"])

    # Step 3: git diff --quiet on target files; if diff present -> failure
    changed = False
    git_exe = shutil.which("git") or "git"
    for path in TARGET_FILES:
        result = subprocess.run(  # noqa: S603
            [git_exe, "diff", "--name-only", str(path)], capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            changed = True
    if changed:
        sys.stderr.write("Embedded documentation is stale. Regenerated content differs.\n")
        return 1
    sys.stderr.write("Embedded documentation is current.\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
