# OpenAPI Specification

The OpenAPI specification is generated from the live FastAPI application.

Generation pipeline:

1. `scripts/export_openapi.py` writes `docs/_generated_openapi/openapi.json`.
2. `scripts/update_openapi_markdown.py` embeds a summary and the full spec below.

Regenerate locally:

```bash
task export-openapi && python scripts/update_openapi_markdown.py
```

<!-- OPENAPI:BEGIN -->
<!-- (content injected by update_openapi_markdown.py) -->
<!-- OPENAPI:END -->
