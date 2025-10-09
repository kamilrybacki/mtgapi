# Domain Models

The domain layer is the heart of the service. It transforms raw upstream API payloads into **typed, cohesive objects** that the rest of the codebase can reason about.

## Design Goals

- **Clarity over completeness**: Only persist and expose fields that the application actually needs.
- **Forward compatibility**: Model construction is tolerant to unknown / additional upstream fields.
- **Pure transformations**: Domain objects should avoid side effects; enrichment (e.g. caching, HTTP calls) happens in services.
- **Serialization boundary**: Pydantic models (e.g. `MTGIOCard`) accept the raw JSON shape; high-level models (e.g. `MTGCard`) normalize to stable internal names and types.

## Key Models

### MTGIOCard
Represents the _direct_ shape returned by the external MTGIO API. This model is intentionally close to the source so that upstream schema drift is easy to detect.

### MTGCard

The canonical internal representation used by endpoints and caching. It:

- Normalizes optional / missing fields.
- Provides convenience constructors (e.g. `from_mtgio_card`).
- Implements basic validation & derived properties (e.g. computed mana value if needed).

### ManaValue

A tiny semantic wrapper describing a card's converted mana cost / total pip value. Encapsulating it:

- Gives a future hook for formatting and comparison logic.
- Centralizes potential validation (e.g. non-negative enforcement).

## Schema Export

Run:

```bash
task export-schemas
```
This writes JSON Schema documents into `docs/_generated_schemas/` which are then included in the rendered documentation.

## Evolution Strategy

When adding or modifying fields:

1. Update upstream (raw) model first if the source API changed.
2. Adjust internal `MTGCard` with a migration function or fallback logic so older cache entries (if any) remain readable.
3. Regenerate schemas (`task export-schemas`) and OpenAPI (`task export-openapi`).
4. Add tests demonstrating the new or changed field.

> Keep business rules out of the models—push them into service layer objects for testability and separation of concerns.
