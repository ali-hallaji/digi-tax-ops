# Ops Progress

Last updated: 2026-06-05

## Current Phase
Phase 0.2 local/staging orchestration hardening.

## Completed
- Added Claude Code skills and subagents foundation: 5 project skills (`start-digi-session`, `deploy-digi-test`, `smoke-check-digi`, `review-ops-diff`, `update-blockers`) and 2 subagents (`ops-deploy-auditor`, `blocker-ledger-auditor`) under `.claude/`; CLAUDE.md updated with Skills and Subagents section.
- Docker Compose local stack for Postgres, Redis, backend API, and frontend.
- Backend build context points to `../digi-tax-backend`.
- Frontend build context points to `../digi-tax-frontend`.
- Environment example includes backend/frontend runtime wiring and restricted-network frontend build proxy variables.
- `scripts/bootstrap.sh` for DB creation and Alembic bootstrap inside Docker.
- `scripts/preflight.sh` for compose/env/readiness checks.
- `scripts/smoke_test.sh` for backend health, CORS, auth, dashboard, and frontend availability.
- README includes local/staging deploy workflow.
- Frontend orchestration updated for the production SSR Node container on port `3000` with build-time `VITE_API_BASE_URL`.
- Added a server deployment runbook for separate repo updates, targeted rebuilds, migrations, restarts, and validation.
- Cleaned up deployment documentation around the current `docker-compose` workflow, single Alembic migration command, targeted backend/frontend updates, and frontend rebuild requirements for `VITE_API_BASE_URL`.
- Fixed `.env.example` DATABASE_URL db name to match `POSTGRES_DB=digi_tax` (was `digitax`).
- Updated README project structure to reflect actual directory layout.
- Updated `phase_checklists.md` to reflect completed Phase 0 and Phase 0.2 state.
- Expanded `api-contracts/README.md` with OpenAPI snapshot export instructions.
- Updated `docs/current_state.md` to include nginx service.

## Active Next
- Re-validate Phase 0.2 scripts against the current staging `.env`.
- Keep API contract snapshots aligned with backend OpenAPI.
- Keep Nginx reverse proxy routing aligned with API and frontend SSR service ports when requested.

## Known Risks
- Staging `.env` can drift from `.env.example`.
- Optional services should remain out of the default Compose stack.
- Ops changes can accidentally cross repo boundaries if not kept scoped.

## Validation Policy
Use Docker Compose and shell syntax checks. Do not edit backend/frontend app logic from this repo.
