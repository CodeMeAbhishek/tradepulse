# ADR-0001: Modular monolith for hackathon prototype

## Status

Accepted

## Context

TradePulse needs clear service boundaries (document intelligence, entity resolution, screening, compliance, RegWatch, audit) while remaining deliverable in a 22-hour build. Microservices would add deployment and failure modes without product value at this stage.

## Decision

Ship a single FastAPI application (`apps/api`) with logical modules under `app/services/*`, thin routers under `app/api`, and typed contracts in `packages/contracts`. SQLite is acceptable for the prototype; schemas must stay PostgreSQL-portable.

## Consequences

- Faster local development and a single health/readiness surface.
- Module boundaries can later become services without rewriting domain contracts.
- Team must enforce file ownership and avoid putting business logic in route handlers.
