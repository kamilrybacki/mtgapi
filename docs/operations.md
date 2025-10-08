# Operations

Operational guidance for deploying and running the MTG API service.

## Runtime Footprint

- Stateless application process; all state is external (DB) or ephemeral (in‑memory cache).
- Single Uvicorn worker by default; scale horizontally for throughput.

## Health & Readiness

- Container `HEALTHCHECK` probes `/docs` (can switch to a lighter `/health` endpoint later for lower payload and privacy).
- Consider adding a dedicated `/healthz` (no auth, minimal body) for production probes.

## Configuration Delivery

Configuration is environment driven (env vars). For container orchestration:

- Use a config map / secret store for database URL.
- Keep non-sensitive defaults baked; override sensitive values only.

## Logging

- Structured logging can be enabled by adjusting log format in `APIConfiguration` (currently simple text).
- Recommendation: redirect stdout/stderr to a centralized aggregator (e.g. Loki, ELK).

## Metrics (Future)

Potential libraries: `prometheus-client` or `opentelemetry-instrumentation-fastapi`.

- Latency histogram (per endpoint)
- Cache hit ratio
- Upstream call success/failure counters

## Tracing (Future)

OpenTelemetry instrumentation could correlate:

- Incoming request spans
- Outbound HTTP calls (MTGIO)
- DB queries

## Deployment Checklist

1. Build image (CI) with pinned Python base.
2. Run security scan (Bandit now; add container scanner later).
3. Push to registry (GHCR).
4. Deploy orchestrator manifest (compose, k8s, Nomad, etc.).
5. Verify health probe passes.
6. Run smoke test: GET `/card/{known_id}`.

## Scaling

- Horizontal scaling limited by shared cache coherence (current cache is per process). Introduce Redis to consolidate.
- CPU bound? Add workers (`--workers` via Gunicorn + Uvicorn workers) or optimize hot paths.

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Upstream MTGIO outage | 5xx from /card | Retry policy / circuit breaker (future) |
| DB unavailable | 500 on DB-backed endpoints | Connection pool backoff, readiness gating |
| Cache bloat | Memory growth | Introduce size cap + metrics |
| High latency | Slow responses | Profile; add async timeouts & fallback |

## Backups & Data

Currently no persistent data layer aside from Postgres (if used). Rely on standard DB backup tooling (snapshots / PITR) if persistence matters.

> Keep operational concerns decoupled: adding metrics or tracing should not require touching domain logic—use instrumentation wrappers.
