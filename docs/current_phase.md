# Current Phase - Ops

Last updated: 2026-06-17

## Active Focus

Phase 0.2 orchestration is complete. Current focus: keep deploy docs, migration checklists, and
service wiring aligned with the backend's Release 1A / 1B / 1C priorities.

## Current State

- `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, environment examples.
- Compose builds backend from `../digi-tax-backend`.
- Compose builds frontend from `../digi-tax-frontend`.
- The canonical frontend is React/TanStack/Vite (SSR production container on port 3000).
- Bootstrap, preflight, and smoke-test scripts exist for repeatable validation.
- WeasyPrint PDF migration complete (2026-06-11): backend Dockerfile installs 7 system packages;
  `api` image **must be rebuilt** for any deploy of P2.7+ backend.
- Moadian foundation phases P3.0B–P3.5 complete: new migrations `e5f9a2c1d7b3`, `f3a8b2c1d5e7`,
  and the Moadian tenant-profile migration must be applied on every staging/production deploy.
- Feature gating (P3.5.8.x): frontend-only changes; no deploy action required.

## Release Structure (canonical in `docs/business_scope_freeze_v1.md`)

- **Release 1A** — merchant journey + sellable core (purchases, real P/L, subscription, onboarding)
- **Release 1B** — Moadian real submit + inquiry (crypto blocked pending spec confirmation)
- **Release 1C** — accountant-ready reports, Excel import, partner role

## Current Task Boundary

- Keep orchestration and integration docs aligned with canonical sibling repos.
- Validate service wiring without changing backend/frontend application logic.
- Keep optional infrastructure out of the default stack.
- Use Compose/shell checks for validation; rebuild images only when needed.
- Track all new Alembic migrations in `docs/phase_roadmap.md` deploy checklist.

## Launch Blockers (ops-relevant)

- ~~OTP in-memory~~ — **DONE (R1A-P0):** `RedisOTPService` replaces `DevOTPService`; OTPs survive api restart. `SMOKE_TEST_RESTART_OTP=1` verifies.
- ~~CORS wildcard~~ — **DONE (R1A-P0):** CORS origins now env-driven (`BACKEND_CORS_ORIGINS`); set comma-separated list for staging/prod.
- Ops migration-state smoke test does not verify Alembic migration state — must be added to `smoke_test.sh`
- Nginx is a placeholder (`nginx/placeholder.conf`); not in `docker-compose.yml` — must be wired for production TLS
- Staging `.env` can drift from `.env.example` — manual review before each release

## Do Not

- Do not edit backend or frontend app logic from this repo.
- Do not add Kubernetes by default.
- Do not add Prometheus, Grafana, MinIO, or other observability/storage stacks by default.
- Do not commit secrets.
- Do not commit proxy settings or network workarounds.

## Required Reading For New Ops Sessions

1. `CLAUDE.md`
2. `AGENTS.md`
3. `docs/current_phase.md` (this file)
4. `docs/progress.md`
5. `docs/phase_roadmap.md` — product-level true phase status and mandatory migration checklist
6. `docs/business_scope_freeze_v1.md` — canonical scope: Release 1A/1B/1C, launch blockers, build-now table
7. `docs/product_master_blueprint_v4_2.md` — product intent v4.2 (supersedes v3 strategy doc)
8. `docs/architecture_decisions.md` when touching architecture or boundaries

> **Product framing (v4.2):** Digi Invoice is a simple, cloud-based accounting & tax-readiness SaaS.
> Revenue = subscriptions. Moadian = required edge capability, not revenue core.
> Taxpayer Profile and Admin Review are **partial skeletons**. See `docs/phase_roadmap.md` for migration checklist.
