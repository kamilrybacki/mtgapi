# Services Layer

The services layer orchestrates side‑effects: HTTP requests, caching, database access, retries, and composition logic. Each service adheres to a small surface area and can be swapped or extended with minimal ripple.

## Principles

- **Explicit boundaries**: Every external system interaction (network, DB, cache) is mediated by a focused service.
- **Retry with intent**: Transient network failures use `tenacity` policies; logic errors are surfaced immediately.
- **Dependency injection**: Construction is centralized (see wiring) so tests can override concrete implementations.
- **Async first**: All I/O services expose async APIs; CPU work stays lean to preserve event‑loop responsiveness.

## Key Services

### HTTP Base

Provides a thin wrapper around `httpx.AsyncClient` adding:

- Standard timeouts
- Optional request / response logging
- Central place for future auth headers or instrumentation

### MTGIOAPIService

Encapsulates calls to the upstream MTGIO API. Responsibilities:

- Build request URLs / parameters
- Apply retry policy for transient errors
- Deserialize upstream JSON into `MTGIOCard`

### Cache Service

Abstracts in‑memory (or future distributed) caching of `MTGCard` objects. Current implementation is a simple dict protected by per‑event loop usage; future extension paths:

- TTL / eviction policy
- Redis or Memcached backend
- Negative caching for known miss patterns

### Database Service

Wraps SQLAlchemy async engine/session creation. Even if lightly used now, isolating this logic enables:

- Connection pooling configuration
- Migration integration later (Alembic) without leaking concerns into domain code
- Easier testcontainers overrides

### Proxy / Aggregation

The proxy service (if present) orchestrates multiple upstream sources (pricing, alternative info) and merges results into a single domain view. Currently minimal—acts as an extension seam.

## Wiring & Lifespan

During FastAPI lifespan startup the dependency injection container is built (`wire_services`) and resources are initialized (HTTP clients, DB connections). On shutdown, resources are closed gracefully to avoid dangling sockets.

## Extending a Service

1. Add interface / abstract method in the target service module or create a new service file.
2. Implement concrete class.
3. Register it in the wiring function / container.
4. Write integration tests with the new service, plus functional tests using a mock or fake.
5. Update documentation (this page + any API usage examples).

> Keep heavy transformation logic in domain or helper modules—services should orchestrate, not deeply compute.
