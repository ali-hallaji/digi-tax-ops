# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Skills and Subagents

Use these at session start and before commit. Skills live in `.claude/skills/`; subagents in `.claude/agents/`.

| When | Command / Agent |
|---|---|
| Session start | `/start-digi-session` — orient, surface blockers, confirm phase |
| Deploying the stack | `/deploy-digi-test` — controlled deploy sequence with migration step |
| After any deploy | `/smoke-check-digi` — health, auth, CORS, frontend availability |
| Before commit | `/review-ops-diff` — Compose, env, scripts, boundary check |
| Blocker found or resolved | `/update-blockers` — update `docs/progress.md` immediately |
| Full deploy config audit | Agent: `ops-deploy-auditor` |
| Blocker surface before deploy | Agent: `blocker-ledger-auditor` |

**Rule:** Read `docs/progress.md` Known Risks before any deploy or config change. Never edit backend or frontend application code from this repo.

## Orientation

Read `AGENTS.md`, `docs/current_phase.md`, and `docs/progress.md` before planning any task. Use `docs/architecture_decisions.md` when making structural decisions.

This is `digi-tax-ops`: the canonical operations repo for DigiTax. It owns Docker Compose, Nginx, scripts, API contract snapshots, environment templates, and local/staging orchestration only. It does not own backend or frontend application logic.

Sibling repos live at the same directory level:
```
../digi-tax-backend   # FastAPI async API, Alembic migrations, domain logic
../digi-tax-frontend  # React/TanStack/Vite, production SSR Node container
```

The workspace root is not a git repo. Each repo is updated and deployed independently.

## Common Commands

```bash
# Validate Compose config before any build or restart
docker-compose config

# Start all services
docker-compose up -d

# Start services individually (preferred order)
docker-compose up -d postgres redis
docker-compose up -d api
docker-compose up -d frontend

# View logs
docker-compose logs -f [service]

# Check service status and health
docker-compose ps

# Run database migrations (always inside the api container)
docker-compose exec api python -m alembic upgrade head

# Preflight checks (Compose validity, env, DB consistency, container readiness)
bash scripts/preflight.sh

# Smoke tests (API health, CORS, OTP auth flow, bearer-auth endpoints, frontend routes)
bash scripts/smoke_test.sh

# Bootstrap (creates DB if missing, runs migrations)
bash scripts/bootstrap.sh
```

## Build Rules

Rebuild only for dependency, Dockerfile, base image, or build-time env changes — not for every code change.

```bash
# Backend changed (code, deps, Dockerfile, or migrations)
docker-compose build api
docker-compose up -d api
docker-compose exec api python -m alembic upgrade head

# Frontend changed (source, deps, Dockerfile, or VITE_API_BASE_URL)
docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend
```

`VITE_API_BASE_URL` is **build-time** configuration baked into the frontend bundle by Vite/TanStack. Restarting the existing frontend container is not enough after frontend source or this env var changes — the image must be rebuilt. Use `/api/v1` for reverse-proxy same-origin deployments.

## Architecture

Four canonical repos:
- `digi-tax-backend` — owns backend logic, OpenAPI contracts, migrations
- `digi-tax-frontend` — owns product UI, routes, frontend API integration
- `digi-tax-ops` (this repo) — owns Compose, Nginx, scripts, env templates
- `digi-tax-Front-source` — historical Lovable/design reference only; not used for deployment

The frontend image runs a **production SSR Node server** (`node server.mjs`) on container port 3000. It is not a Vite dev server and is not static files served from Nginx.

`docker-compose.yml` builds both application images from sibling repo paths:
```yaml
api:     build: ../digi-tax-backend
frontend: build: ../digi-tax-frontend
```

Services and ports: `postgres` 5432, `redis` 6379, `api` 8000, `frontend` 3000 (host port controlled by `FRONTEND_PORT`).

## Hard Constraints

- Do not edit backend or frontend application logic from this repo.
- Do not add Kubernetes, Prometheus, Grafana, MinIO, or other optional stacks by default.
- Do not commit secrets, proxy URLs, credentials, or network workarounds.
- All backend/ops validation must go through Docker/Compose — no host-level Python or Poetry.
- `api-contracts/` stores exported OpenAPI snapshots; frontend consumes backend contracts, it does not invent routes.

## Environment Setup

```bash
cp .env.example .env
# Edit .env with actual values; DATABASE_URL db name must match POSTGRES_DB
```

Required: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `REDIS_URL`, `VITE_API_BASE_URL`, `FRONTEND_PORT`.

Proxy values for restricted-network builds belong in the shell environment or an ignored local env file only — never committed.
