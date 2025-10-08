# Development

## Prerequisites

- Python 3.12+
- Poetry
- Docker (for integration tests)

## Setup

```bash
poetry install
```

## Tests

```bash
poetry run pytest -q
```

## Linting

```bash
poetry run ruff check .
poetry run mypy .
```

## Docs / Schema / OpenAPI Regeneration

Export JSON Schemas (writes to `docs/_generated_schemas/`):

```bash
task export-schemas
```

Export OpenAPI schema (writes to `docs/_generated_openapi/openapi.json`):

```bash
task export-openapi
```

Do both and build the docs site (outputs to `site/`):

```bash
task docs-refresh
```

Serve docs with live reload:

```bash
task docs-serve
```

> Commit regenerated schema/OpenAPI artifacts when model or API shape changes so the published site stays in sync.
