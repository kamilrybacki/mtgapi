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
