# Testing Strategy

A layered test approach balances speed, confidence, and maintainability.

## Layers

| Layer | Scope | Speed | Purpose |
|-------|-------|-------|---------|
| Unit | Pure functions / small methods | Fastest | Logic correctness & edge cases |
| Functional | Service + domain interactions (no external network) | Fast | Contract behavior |
| Integration | External APIs, DB (Testcontainers) | Moderate | Real I/O correctness |
| End-to-end (future) | Full API flow with container orchestration | Slowest | Deployment realism |

## Guiding Principles

- **Fail fast**: Unit/functional tests catch regressions before slower integration layers run.
- **Isolate side effects**: Use dependency injection to swap real services for fakes/mocks in functional tests.
- **Determinism**: External variability (network, time) is minimized or controlled.
- **Readable fixtures**: Prefer factory helpers in `tests/common` over deep parameterization.

## Asynchronous Testing

`pytest-asyncio` powers async tests. Keep event loop scope at `session` for expensive resources (e.g. DB container) but isolate state via fixtures.

## Testcontainers Usage

Integration tests spin Postgres (and potentially future services) in ephemeral containers:

- Ensures parity with production driver (asyncpg + SQLAlchemy)
- Avoids mocking SQL behavior

## Adding a New Test

1. Pick the narrowest appropriate layer.
2. If hitting external HTTP, prefer recorded sample or a mock unless the purpose is real upstream contract verification.
3. Add assertions for both expected data and absence/presence of side effects (e.g. cache entry created).
4. Run `task test` (or a narrower marker) before committing.

## Future Enhancements

- Contract tests for upstream API schema drift.
- Performance smoke test measuring 95th percentile response time.
- Coverage thresholds enforced in CI.

> Keep tests expressive—naming clarity and focused assertions beat overly DRY abstractions.
