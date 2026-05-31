# Ops Current State

Last updated: 2026-05-31

## Services

| Service | Status | Port | Description |
|---------|--------|------|-------------|
| postgres | Configured/runnable | 5432 | PostgreSQL 16 database |
| redis | Configured/runnable | 6379 | Redis 7 cache/store |
| api | Configured/runnable | 8000 | Backend API from `../digi-tax-backend` |
| frontend | Configured/runnable | 9000 | React/TanStack frontend from `../digi-tax-frontend` |

## Ownership
- `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, integration docs, and environment examples.
- Backend logic belongs in `../digi-tax-backend`.
- Frontend logic belongs in `../digi-tax-frontend`.
- The frontend stack is React/TanStack/Vite.

## Phase 0.2 Workflow
- `scripts/bootstrap.sh` creates the configured database if needed and runs Alembic inside Docker.
- `scripts/preflight.sh` validates compose/env/readiness and database-name consistency.
- `scripts/smoke_test.sh` checks backend health, CORS, auth, dashboard, and frontend availability.

## Current Boundaries
- Do not edit backend or frontend app logic from this repo.
- Do not add Kubernetes by default.
- Do not add Prometheus, Grafana, MinIO, or other optional stacks by default.
- Do not commit secrets.

## Active Next
- Validate the Phase 0.2 scripts against the current staging `.env`.
- Keep API contract snapshots aligned with backend OpenAPI.
- Add Nginx routing only when explicitly requested.
