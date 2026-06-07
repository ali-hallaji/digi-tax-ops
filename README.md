# digi-tax-ops

Local/staging orchestration and cross-repo coordination for DigiTax.

## Overview

This repository owns operational setup for DigiTax, including:

- Docker Compose configuration for local development
- Nginx and integration documentation
- Scripts for bootstrap, preflight, and smoke validation
- API contract snapshots
- Environment variable templates

## Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.0+
- Git
- 4GB+ RAM available for Docker

## Quick Start

### 1. Clone sibling repositories

```bash
# Go to parent directory of digi-tax-ops
cd ..
git clone <digi-tax-backend-repo>
git clone <digi-tax-frontend-repo>
```

### 2. Set up environment

```bash
cd digi-tax-ops
cp .env.example .env
# Edit .env with your actual values if needed
# For restricted networks, provide proxy values from your shell or ignored local env only.
# Do not commit real proxy URLs, ports, credentials, or tokens.
```

### 3. Run services

```bash
# Start all services
docker-compose up -d

# Or start services individually
# docker-compose up -d postgres redis
# docker-compose up -d api
# docker-compose up -d frontend

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Local Services

| Service | Description | Port |
|---------|-------------|------|
| postgres | PostgreSQL 16 database | 5432 (local dev only) |
| redis | Redis 7 cache/store | 6379 (local dev only) |
| api | Backend API server | 8000 |
| frontend | React/TanStack SSR frontend | 3000 |

## Project Structure

```
digi-tax-ops/
├── docker-compose.yml          # Main compose configuration
├── .env.example                # Environment template
├── README.md                   # This file
├── AGENTS.md                   # Project rules and scope
├── CLAUDE.md                   # Claude Code guidance
├── nginx/
│   └── placeholder.conf        # Nginx reverse proxy configuration
├── scripts/
│   ├── bootstrap.sh            # DB creation and Alembic bootstrap
│   ├── preflight.sh            # Compose/env/readiness checks
│   └── smoke_test.sh           # API health, auth, frontend validation
├── api-contracts/
│   └── README.md               # OpenAPI snapshot export instructions
└── docs/
    ├── current_phase.md        # Active phase and task boundary
    ├── current_state.md        # Service and ownership state
    ├── progress.md             # Implementation progress log
    ├── architecture_decisions.md
    ├── api_contract_rules.md
    ├── ops_deployment_guide.md
    ├── phase_checklists.md
    ├── repo_strategy.md
    ├── server_deploy_runbook.md
    ├── token_saving_workflow.md
    └── shared/
        ├── glossary_bilingual.md
        └── transport_strategy.md
```

## Development

### Health checks

All services have built-in health checks:

```bash
docker-compose ps
```

### Rebuild services

```bash
# Rebuild backend services
docker-compose build api

# Rebuild frontend after dependency/build-config changes or VITE_API_BASE_URL changes
docker-compose build --no-cache frontend
```

## Server update quick path

For server deployments, use the full runbook in
[`docs/server_deploy_runbook.md`](docs/server_deploy_runbook.md).

Normal update order uses the three separate repos: pull backend, pull frontend,
pull ops, validate Compose, build/recreate `api` if backend changed, run the
single documented migration command, build/recreate `frontend` if frontend
changed or `VITE_API_BASE_URL` changed, then run preflight and smoke checks.

Full staging update:

```bash
cd /usr/local/digi-tax-ops

git -C ../digi-tax-backend pull
git -C ../digi-tax-frontend pull
git -C . pull

docker-compose config

docker-compose build api
docker-compose up -d postgres redis api
docker-compose exec api python -m alembic upgrade head

docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend

bash scripts/preflight.sh
bash scripts/smoke_test.sh
```

Backend-only update:

```bash
docker-compose build api
docker-compose up -d api
docker-compose exec api python -m alembic upgrade head
```

Frontend-only update:

```bash
docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend
```

Notes:
- `scripts/preflight.sh` checks compose validity, required services, `.env` requirements, DB-name consistency, Postgres readiness, and `DATABASE_URL` visibility in `api`.
- `scripts/smoke_test.sh` checks backend health, CORS preflight, dev OTP auth flow, bearer-auth endpoints, dashboard endpoints, frontend availability, `/login`, `/app`, and obvious hardcoded backend IPs in frontend responses when `frontend` is enabled.
- Ensure `.env` has a `DATABASE_URL` whose database name matches `POSTGRES_DB`.
- The frontend image is a production SSR Node container that runs `node server.mjs` from `../digi-tax-frontend` and listens on container port `3000`.
- `VITE_API_BASE_URL` is build-time frontend configuration. Use `/api/v1` behind the ops Nginx reverse proxy, or provide an environment-specific public API URL from ignored local/staging env before rebuilding the frontend image.
- Use the frontend-only update when frontend source changes or `VITE_API_BASE_URL` changes. Vite/TanStack bakes `VITE_API_BASE_URL` into the frontend bundle, so restarting the existing frontend container is not enough after frontend source or frontend env changes.
- If the browser still calls an old API URL, rebuild the frontend image and hard-refresh the browser cache.
- Runtime frontend secrets, such as `LOVABLE_API_KEY` if needed, must be passed only at runtime through ignored environment configuration.

## Environment Variables

Required env vars (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `APP_NAME` - Application name
- `DEBUG` - Enable debug mode
- `VITE_API_BASE_URL` - Build-time public frontend API base URL
- `VITE_API_TIMEOUT_MS` - Frontend API timeout in milliseconds
- `FRONTEND_PORT` - Host port mapped to frontend container port `3000`

## Next Steps

- **Current** - Local/staging orchestration hardening and cross-repo coordination
- **Next** - Worker service wiring when backend worker contracts are ready
- **Deferred** - Kubernetes, observability, and optional storage stacks only when explicitly requested
- **Future** - Production-ready configs

## License

Internal use only.
