# Architecture (Moved)

Moved to `concepts/architecture.md`.

See new Concepts section.

```text
FastAPI (entrypoint) -> Services (DI) -> { Cache | Postgres | External APIs }
                                  -> Domain Models (MTGCard)
```

## Layers

- **Entry Point**: Manages lifespan and wiring.
- **Services**: External API clients, caching, database access, proxies.
- **Domain**: Typed models and transformations.
- **Config**: Structured settings & dependency injection.

## Future Enhancements

- Redis cache backend
- Additional data sources (pricing, legality)
- Observability (OpenTelemetry)
- Enhanced caching strategies (see [Caching](caching.md) for current approach and roadmap)
