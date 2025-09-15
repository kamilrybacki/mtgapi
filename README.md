# MTG Card Info API

This repository provides a small FastAPI-based service for retrieving Magic: The Gathering card information and related utilities used in tests and integrations.

The codebase focuses on backend HTTP services, domain models for MTG cards, and service integrations (external APIs, cache, and database adapters). It is not a full user-facing deck-building product.

## Key packages and layout

- Python 3.12
- FastAPI for the HTTP layer (in `src/mtgapi`)
- Modular services under `src/mtgapi/services` (http clients, proxy, cache, database)
- Domain models under `src/mtgapi/domain` (card, conversions)
- Config and wiring in `src/mtgapi/config`

## Quick start (development)

1. Install dependencies with Poetry:

```bash
poetry install
```

1. Run the test suite (recommended before running):

```bash
poetry run pytest -q
```

1. Start the app (module path depends on how you run the package). A common pattern in this repo is to run the entrypoint module:

```bash
poetry run python -m mtgapi.entrypoint
```

If you prefer Uvicorn directly, point it at the ASGI app module used in `entrypoint.py`.

## API docs

When the server is running locally, the FastAPI interactive docs are typically available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Testing and Docker

- Tests are in the `tests/` folder and include unit, integration, and functional suites. Use `pytest` to run them.
- A Dockerfile and docker-compose are included under `deploy/` for containerized runs and in-repo integration testing. See `deploy/docker-compose.yaml` and `deploy/Dockerfile`.

### Taskfile (developer tasks)

This project includes a `Taskfile.yaml` with convenient developer tasks. Common commands (run from the repository root):

- Install development dependencies (creates/uses the in-project virtualenv configured by the Taskfile):

```bash
task install-dev
```

- Install production dependencies only:

```bash
task install-prod
```

- Initialize the project (venv + install + pre-commit):

```bash
task init-project
```

- Run linters and type checks (ruff + mypy):

```bash
task lint
```

- Run the full test suite:

```bash
task test
```

- Start the API with docker-compose (uses `deploy/docker-compose.yaml`):

```bash
task start-api
```

## Notes and caveats

- The project contains utilities and fixtures used by the test suite (see `tests/conftest.py` and `tests/globals.py`).
- This README intentionally stays focused on running and testing the service; see inline docs and module docstrings for implementation details.

## Contributing

If you'd like to contribute, open issues or pull requests. Keep tests green and follow repository linting rules (Taskfile contains developer commands such as `task lint`).

## License

MIT
