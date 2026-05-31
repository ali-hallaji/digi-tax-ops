# Current Phase - Ops

Last updated: 2026-05-31

## Active Focus
Phase 0.2 local/staging orchestration hardening: bootstrap, preflight, smoke checks, and API contract snapshots.

## Current State
- `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, integration docs, and environment examples.
- Compose builds backend from `../digi-tax-backend`.
- Compose builds frontend from `../digi-tax-frontend`.
- The canonical frontend is React/TanStack/Vite.
- Bootstrap, preflight, and smoke-test scripts exist for repeatable validation.

## Current Task Boundary
- Keep orchestration and integration docs aligned with canonical sibling repos.
- Validate service wiring without changing backend/frontend application logic.
- Keep optional infrastructure out of the default stack.
- Use Compose/shell checks for validation and rebuild images only when needed.

## Do Not
- Do not edit backend or frontend app logic from this repo.
- Do not add Kubernetes by default.
- Do not add Prometheus, Grafana, MinIO, or other observability/storage stacks by default.
- Do not commit secrets.
- Do not commit proxy settings or network workarounds.

## Required Reading For New Codex Sessions
1. `AGENTS.md`
2. `docs/current_phase.md`
3. `docs/progress.md`
4. `docs/architecture_decisions.md` when touching architecture or boundaries.
