# MTG Card Info API

Fast, typed, container-ready MTG card data microservice built with FastAPI.

[![Tests](https://img.shields.io/github/actions/workflow/status/kamilrybacki/mtgcobuilder-api/pytest.yml?label=tests&logo=pytest)](./.github/workflows/pytest.yml)
[![Lint](https://img.shields.io/github/actions/workflow/status/kamilrybacki/mtgcobuilder-api/lint.yml?label=lint&logo=ruff)](./.github/workflows/lint.yml)
[![Docker Publish](https://img.shields.io/github/actions/workflow/status/kamilrybacki/mtgcobuilder-api/docker-publish.yml?label=docker&logo=docker)](./.github/workflows/docker-publish.yml)
![Python Version](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Type Checked](https://img.shields.io/badge/typing-mypy-blue.svg)
![Code Style](https://img.shields.io/badge/style-ruff-informational)
![Coverage](./badges/coverage.svg)
[![Docs](https://img.shields.io/github/actions/workflow/status/kamilrybacki/mtgcobuilder-api/docs.yml?label=docs&logo=mdbook)](./.github/workflows/docs.yml)

> Docs will be published to GitHub Pages after the next push to `main` (via `mkdocs gh-deploy`). Once live, update this note with the URL (e.g. `https://kamilrybacki.github.io/mtgcobuilder-api/`).

---

This service retrieves Magic: The Gathering card information, with caching, domain modeling, and integration-friendly abstractions. It focuses on:

- Async HTTP integrations (MTGIO + future providers)
- Typed domain models for card data
- Extensible service layer (API, cache, DB, proxy)
- Local & container-based development parity

It is intentionally not a full deck-building product.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Quick Start (Development)](#quick-start-development)
4. [API Docs](#api-docs)
5. [Configuration](#configuration)
6. [Taskfile Commands](#taskfile-developer-tasks)
7. [Testing](#testing)
8. [Docker & Container Image](#docker--container-image)
9. [Examples](#examples)
10. [Migration Notes](#migration-notes)
11. [Roadmap](#roadmap)
12. [Contributing](#contributing)
13. [License](#license)

## Features

- 🚀 FastAPI async service with lifespan wiring
- ♻️ In-memory / pluggable caching layer
- 🧩 Dependency Injector based wiring (`wire_services`)
- 🗃️ Async Postgres integration (SQLAlchemy + asyncpg)
- 🔄 External MTGIO API client with retry (tenacity)
- 🧪 Layered test suites (unit, functional, integration)
- 🐳 Container-first workflow (Dockerfile + compose)
- 🛡️ Supply chain & dependency export integrity in CI (hash + non-empty check)
- 🔧 Strict linting (Ruff) & typing (mypy)

## Architecture

```text
┌────────────────────┐
│ FastAPI (entrypoint)│
└───────────┬────────┘

           │ lifespan wires
     ┌──────▼───────┐         ┌──────────────────┐
     │ Services DI  │────────▶│ External APIs     │ (MTGIO)
     └──────┬───────┘         └──────────────────┘
           │
     ┌──────▼────────┐   ┌──────────────────┐
     │ Cache Layer   │   │ Postgres (async) │
     └──────┬────────┘   └──────────────────┘
           │
     ┌──────▼────────┐
     │ Domain Models │ (MTGCard, conversions)
     └───────────────┘
```

Key modules:

- `mtgapi.entrypoint`: FastAPI app & lifespan
- `mtgapi.config.settings`: Configuration objects & defaults
- `mtgapi.services`: API clients, proxy orchestration, database, cache
- `mtgapi.domain`: Card model + conversion helpers

## Quick Start (Development)

## Key packages and layout

- Python 3.12
- FastAPI for the HTTP layer (in `src/mtgapi`)
- Modular services under `src/mtgapi/services` (http clients, proxy, cache, database)
- Domain models under `src/mtgapi/domain` (card, conversions)
- Config and wiring in `src/mtgapi/config`

1. Install dependencies:

```bash
poetry install
```

1. Run tests:

```bash
poetry run pytest -q
```

1. Start the API (module run):

```bash
poetry run python -m mtgapi.entrypoint
```

Or with Uvicorn directly:

```bash
poetry run uvicorn mtgapi.entrypoint:API --reload
```

## API Docs

When running locally:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Configuration

Environment variables (examples):

| Variable | Purpose | Example |
|----------|---------|---------|
| `MTGAPI_MTGIO__BASE_URL` | Upstream MTGIO API base | `https://api.magicthegathering.io` |
| `MTGAPI_DATABASE__CONNECTION_STRING` | Async DB URI | `postgresql+asyncpg://user:pass@host:5432/db` |

See `mtgapi/config/settings/*` for structured settings.

## Testing

Test layers:

- Unit & functional: fast feedback
- Integration: external API & Postgres via Testcontainers

Common commands:

```bash
task test          # full suite
task test-offline  # offline subset
task test-chosen   # marked tests
```

## Docker & Container Image

Build locally:

```bash
task build-image
```

Run with compose:

```bash
task start-api
```

Manual Docker:

```bash
docker build -f deploy/Dockerfile -t ghcr.io/kamilrybacki/mtgapi:local .
docker run -p 8000:8000 ghcr.io/kamilrybacki/mtgapi:local
```

### Taskfile (Developer Tasks)

```bash
task install-dev    # dev deps + venv + config
task install-prod   # prod-only deps
task init-project   # bootstrap project
task lint           # ruff + mypy
task test           # full tests
task start-api      # docker compose up api + db
```

## Examples

Fetch a card JSON (assuming numeric ID):

```bash
curl -s http://localhost:8000/card/597 | jq
```

Fetch a card image:

```bash
curl -o card.webp http://localhost:8000/card/597/image
```

Python usage:

```python
from mtgapi.services.apis.mtgio import MTGIOAPIService
import anyio

async def main():
          service = MTGIOAPIService()
          card = await service.get_card(597)
          print(card.name, card.set_code)

anyio.run(main)
```

## Migration Notes

See [`MIGRATION.md`](./MIGRATION.md) for details on the package rename and image changes.

## Roadmap

- Additional data providers (pricing, format legality)
- Pluggable cache backends (Redis)
- Pagination & search endpoints
- Dependency diff attestation in CI
- OpenTelemetry tracing hooks

## Contributing

Contributions welcome! To contribute:

1. Fork & branch
2. `task install-dev`
3. Add tests for changes
4. (Optional) Enable git hooks: `task enable-pre-commit`
5. Run `task lint && task test`
6. Open PR

Issues / feature requests encouraged.

### Security Scan

Run a local Bandit scan:

```bash
task security-scan
```

### Dependency Audit

Run vulnerability scan (pip-audit):

```bash
task dependency-audit
```

CI runs a scheduled dependency audit (and on pushes/PRs) with a configurable failure threshold.

Lock consistency is enforced by a separate workflow (`lock-consistency.yml`) which runs `poetry lock --check` and fails if the lock would change (indicating drift or an uncommitted lock refresh). Run it locally with:

```bash
poetry lock --check   # exits non-zero if lock needs regeneration
poetry lock           # (only if above command fails, then commit the updated poetry.lock)
```

Badge (generated on the nightly schedule or manual dispatch) will appear once `badges/dependency_audit.json` is committed. Example (after first schedule run):

```markdown
![Dependency Audit](./badges/dependency_audit.svg)
```

Interpretation (status → meaning):

| Status Example | Meaning |
|----------------|---------|
| `passing` | No vulnerabilities at or above the configured threshold. |
| `fail (3)` | Job failed due to 3 vulnerabilities meeting/exceeding the threshold. |
| `passing` + yellow color | High/Critical vulns exist but below chosen failure threshold (e.g. threshold set to `critical` and only `HIGH` found). |

Failure Threshold Logic:

- Default threshold: `high` (fails on HIGH or CRITICAL)
- Manual override: trigger the workflow via Actions → dependency-audit → Run workflow and set `fail-on-severity` input to one of:
      - `none` (never fail)
      - `low` (fail on LOW+)
      - `medium` (fail on MEDIUM+)
      - `high` (fail on HIGH+ — default)
      - `critical` (fail only on CRITICAL)

The GitHub Step Summary shows a table of all vulnerabilities plus aggregated counts.

Local equivalence (no threshold gate, just raw report):

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry run pip-audit -r requirements.txt -f json > audit.json || true
cat audit.json | jq '.[] | {name: .name, vulns: (.vulnerabilities | length)}'
```

To experiment with thresholds locally, you can emulate gating quickly:

```bash
python scripts/quick_fail_on_severity.py --report audit.json --fail-on high
```

(`scripts/quick_fail_on_severity.py` can be added later if you want a local mirror of CI logic.)

### Pre-commit Hooks

Install and run hooks locally (Ruff lint/format, mypy, Bandit, whitespace hygiene):

```bash
task enable-pre-commit      # one-time setup
task pre-commit-run-all     # run hooks against entire repo
```

Hooks run automatically on staged changes after installation.

Additional manual hooks (not run automatically):

```bash
pre-commit run ruff-fix -a         # apply auto-fixes (stages: manual)
pre-commit run poetry-lock-check   # verify lock is current (no regeneration needed)
```

These are marked with `stages: [manual]` to avoid slowing normal commits; invoke them explicitly when needed.

### Schema Export

Generate JSON Schemas for domain models (output in `docs/_generated_schemas/`):

```bash
task export-schemas
```

## License

MIT
