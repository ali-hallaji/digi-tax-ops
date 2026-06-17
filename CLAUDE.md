# CLAUDE.md — digi-tax-ops

Guidance for Claude Code in this repository. This is the **coordination & deploy
repo only** — it does not own backend or frontend application code, and is the
**home of canonical docs**.

## Canonical sources (read order)
1. `CLAUDE.md` (this file) + `AGENTS.md`
2. **`docs/engineering_execution_blueprint_v1.md`** — execution plan (operating
   model, PART 2 canonical rules, PART 5 phases, PART 6 three-repo matrix,
   PART 7 docs cleanup, PART 8 DoD). Cross-chat memory. **Lives here.**
3. `docs/product_master_blueprint_v4_2.md` — product intent (v4.2). **Lives here.**
   *(Supersedes the old v3 strategy doc — v3 is archived, do not read it.)*
4. `docs/reality_audit.md` — true code state. **Lives here.**
5. `docs/current_phase.md`, `docs/progress.md` (Known Risks before any deploy).
6. `docs/phase_roadmap.md`, `docs/architecture_decisions.md`.

**Shared canonical rules are defined once in blueprint PART 2. Ops never edits
backend/frontend logic; it deploys and coordinates.**

## Skills / subagents
Session start `/start-digi-session` · deploy `/deploy-digi-test` · post-deploy
`/smoke-check-digi` · pre-commit `/review-ops-diff` · blockers `/update-blockers`.
Audit agents `ops-deploy-auditor`, `blocker-ledger-auditor`. Default model
Sonnet/low (blueprint PART 8.3).

## Repos & roles
```
../digi-tax-backend   # FastAPI, Alembic, domain logic — owns contracts
../digi-tax-frontend  # React/TanStack, production SSR Node container
../digi-tax-ops       # this repo: Compose, Nginx, scripts, env, doc home
../digi-tax-Front-source  # historical Lovable reference only — not deployed
```
Workspace root is not a git repo; each repo updates/deploys independently.

## Deploy rhythm (test server — never hardcode its IP/SSH in git)
Refer to the server via shell/env only (`$DIGI_TEST_SSH`, `$DIGI_TEST_PATH`).
Owner's proven sequence:
```bash
git pull
docker-compose config                  # validate first
docker-compose build api               # if backend changed
docker-compose build --no-cache frontend   # if frontend changed
docker-compose up -d                   # postgres+redis → api → frontend
docker-compose exec api python -m alembic upgrade head   # if schema changed
bash scripts/smoke_test.sh
```
`VITE_API_BASE_URL` is **build-time** — frontend image must be rebuilt when it or
frontend source changes; restart alone is not enough. Migrations always run inside
the api container.

## Services & scripts
`postgres` 5432, `redis` 6379, `api` 8000, `frontend` 3000 (`FRONTEND_PORT`).
Compose builds app images from sibling repo paths. Scripts: `bootstrap.sh`
(DB+migrations), `preflight.sh` (compose/env/DB/readiness), `smoke_test.sh`
(health/CORS/OTP/bearer/frontend).

## Hard constraints
- Do not edit backend/frontend application logic from this repo.
- Do not add Kubernetes/Prometheus/Grafana/MinIO by default.
- Do not commit secrets, proxy URLs, server IP/SSH, or credentials.
- All validation via Docker/Compose — no host-level Python/Poetry.
- `api-contracts/` stores exported OpenAPI snapshots; keep them current.

## Commit messages
Short one-line; body only for migrations/security/API-breaking/major decisions.

## Environment
`cp .env.example .env`; `DATABASE_URL` db name must match `POSTGRES_DB`. Required:
`DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`, `VITE_API_BASE_URL`, `FRONTEND_PORT`.
Proxy values belong in shell/ignored local env only — never committed.
