# Caching

Efficient caching minimizes upstream latency and reduces redundant external calls.

## Goals

- **Reduce latency** for frequently requested cards.
- **Protect upstream APIs** from burst traffic.
- **Provide predictable staleness window** while enabling eventual consistency.

## Current Implementation

An in‑memory dictionary keyed by string card identifiers:

- Stored value: fully materialized `MTGCard` instance.
- Lifetime: process lifetime (no TTL yet).
- Eviction: none (assumes moderate working set size).

## Cache Flow

1. Endpoint receives request for card id `X`.
2. Lookup in cache. If hit → return.
3. Miss → fetch from MTGIO via service.
4. Convert to `MTGCard`, store, return.

## Future Enhancements

| Feature | Benefit | Notes |
|---------|---------|-------|
| TTL / Expiration | Bound staleness | Consider adaptive TTL per rarity |
| Size-based Eviction | Avoid unbounded memory | LRU or LFU policies |
| Distributed Cache (Redis) | Horizontal scaling | Leverage key prefixing `card:{id}` |
| Negative Caching | Fewer repeat misses | Short TTL for known absent IDs |
| Compression | Memory reduction | Only if memory pressure emerges |

## Key Design Choices

- **No premature invalidation**: Until churn metrics warrant it, skip complexity.
- **Whole-object storage**: Avoid partial fragments; simplifies serialization.
- **Synchronous population**: First requester pays fetch cost—could later add background warmers.

## Operational Considerations

- Track hit ratio (future metrics hook).
- Provide cache clear / stats endpoint if administrative needs arise.

> Keep caching transparent to domain logic—swap implementation without changing core business code.
