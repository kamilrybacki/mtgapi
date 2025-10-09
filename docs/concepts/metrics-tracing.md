# Metrics & Tracing (Planned)

This page outlines the roadmap for adding metrics collection and distributed tracing to the MTG API. The current API includes placeholder endpoints:

- `GET /metrics` – returns HTTP 501 until Prometheus style metrics are exposed.
- `GET /_trace/test` – returns HTTP 501; will emit a simple trace span once tracing is wired.

## Objectives

1. Provide basic service-level telemetry (request rate, latency, error ratio).
2. Enable insight into upstream dependency latency (external MTG IO API, database, cache).
3. Make local developer enablement effortless (zero-config defaults; env-based opt-in for exporters).
4. Avoid vendor lock-in via OpenTelemetry (OTel) instrumentation.

## Metrics Plan

| Category | Metric | Type | Labels (Dimensions) | Notes |
|----------|--------|------|---------------------|-------|
| HTTP | `http_requests_total` | Counter | method, route, status | Total requests processed. |
| HTTP | `http_request_duration_seconds` | Histogram | method, route, status | Request latency buckets. |
| External | `mtgio_latency_seconds` | Histogram | operation | MTG IO API call durations. |
| Cache | `cache_hits_total` | Counter | cache_name | Successful cache reads. |
| Cache | `cache_misses_total` | Counter | cache_name | Misses (driving upstream fetches). |
| Errors | `exceptions_total` | Counter | exception_type | Unhandled / surfaced exceptions. |

Implementation sketch:

- Use `prometheus_client` for initial exposition (WSGI/ASGI middleware or custom registry scrape).
- Encapsulate metrics registration in a `telemetry/metrics.py` module to avoid polluting business code.
- Provide a `TELEMETRY_ENABLED` (bool) and `TELEMETRY_METRICS_BACKEND` (enum: `prometheus`, later `otlp`) in config.
- Expose `/metrics` only when enabled; otherwise keep 404 or 501 (current placeholder).

## Tracing Plan

| Concern | Approach |
|---------|---------|
| API Incoming Requests | FastAPI middleware generating a root span per request. |
| External HTTP Calls | Instrument `httpx` client with OTel instrumentation. |
| Database (async) | Add SQLAlchemy OTel instrumentation (optional gating). |
| Cache | Manual spans around cache get/set to surface latency vs upstream calls. |
| Propagation | W3C Trace Context headers (`traceparent`, `tracestate`). |
| Export | OTLP over HTTP / gRPC (configurable), fallback to console exporter for local debug. |

Implementation sketch:

```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

resource = Resource.create({
    "service.name": "mtgapi",
    "service.version": VERSION,
})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
```

Middleware hook (pseudo-code):

```python
@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    with tracer.start_as_current_span(f"HTTP {request.method} {request.url.path}"):
        response = await call_next(request)
        return response
```

## Configuration Roadmap

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `TELEMETRY_ENABLED` | bool | false | Master toggle for metrics + tracing. |
| `TELEMETRY_EXPORTER` | enum | `console` | `console`, `otlp`, `prometheus` (metrics only). |
| `OTLP_ENDPOINT` | str | empty | Collector endpoint if exporter = otlp. |
| `METRICS_PORT` | int | 8000 | Future dedicated metrics port (optional). |

## Phased Delivery

1. Phase 0 (Now): Placeholder endpoints (in place).
2. Phase 1: Basic request metrics + cache hit/miss counters; real `/metrics` output.
3. Phase 2: OTel tracing provider, HTTP + MTG IO spans.
4. Phase 3: Database + cache spans; error and exception metrics.
5. Phase 4: Optional dedicated metrics port & OTLP exporter configuration.

## Testing Strategy

- Unit: Ensure middleware respects disabled telemetry (no spans, no metrics registry growth).
- Integration: Hit `/card/{id}` and assert metrics counters progress.
- E2E (future): Verify `traceparent` propagation to downstream calls (mock).

## Open Questions

- Do we need high-cardinality labels for card identifiers? (Likely no — avoid.)
- Should metrics include success vs user-error (4xx) separation? (Probably via status grouping.)

## Next Steps

1. Introduce config toggles.
2. Add metrics registry & swap placeholder `/metrics` implementation.
3. Add tracing provider bootstrap in lifespan.
4. Instrument external service calls.

> See also: Feature Flags concept and Operations guide.
