# Feature Flags (Planned)

The API includes a placeholder endpoint `GET /feature-flags` returning HTTP 501 until real flagging is enabled.

## Goals

1. Allow progressive rollout of non-breaking enhancements (instrumentation, performance tweaks).
2. Provide safe-guarded experiments (A/B style) without redeploying core logic.
3. Keep operational surface minimal for now (config-file / env-driven) before considering a SaaS provider.

## Initial Scope

| Flag | Purpose | Phase |
|------|---------|-------|
| `telemetry.metrics` | Enable metrics collection & `/metrics` endpoint. | Telemetry Phase 1 |
| `telemetry.tracing` | Enable tracing provider & spans. | Telemetry Phase 2 |
| `api.experimental-endpoints` | Expose any experimental routes under `/_exp`. | As needed |

## Implementation Outline

Short-term (Phase A):

- Simple Pydantic settings model: `FEATURE_FLAGS: list[str]` or structured `FeatureFlags` model.
- Helper: `is_flag_enabled(name: str) -> bool` that checks (1) in-memory cache of flags, (2) environment, (3) fallback file.
- `GET /feature-flags` returns dictionary of known flags + boolean state.

Mid-term (Phase B):

- Add cache invalidation endpoint (auth-protected) or TTL reload.
- Support hierarchical flags (`telemetry.*`).

Long-term (Phase C):

- Optional integration with LaunchDarkly / Unleash / Flagsmith via provider adapter.
- Percentage rollouts.
- Context-aware evaluations (e.g., request headers, user tokens if auth added later).

## Data Model Sketch

```python
from pydantic import BaseModel

class FeatureFlags(BaseModel):
    telemetry_metrics: bool = False
    telemetry_tracing: bool = False
    api_experimental_endpoints: bool = False
```

Runtime accessor:

```python
def is_flag_enabled(flag: str) -> bool:
    flags = FeatureFlags()  # real impl: singleton or DI provided
    return getattr(flags, flag.replace('.', '_'), False)
```

## Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FEATURE_FLAGS` | CSV / str | empty | Global on/off list of flags, overrides config defaults. |
| `FEATURE_FLAGS_FILE` | path | empty | Optional JSON/YAML file with structured flag states. |

## Endpoint Contract (planned)

`GET /feature-flags`

```json
{
  "flags": {
    "telemetry.metrics": false,
    "telemetry.tracing": false,
    "api.experimental-endpoints": false
  },
  "detail": "feature flags not implemented"
}
```

## Testing Strategy

- Unit: `is_flag_enabled` path coverage (env override, file fallback, default).
- Integration: Hitting `/feature-flags` returns list of known flags (even if false).
- Future: Simulate enabling metrics flag and assert `/metrics` becomes live.

## Rollout Principles

1. Default safe (all off) until stable.
2. Flags removed once feature is permanently on for 2+ releases.
3. Avoid deep flag nesting — prefer flat names with dot separators.

## Next Steps

1. Add settings + model scaffolding.
2. Implement endpoint real logic & remove placeholder 501.
3. Connect flags to telemetry bootstrap.
4. Add tests & docs updates.

See also: Metrics & Tracing concept and Operations guide.
