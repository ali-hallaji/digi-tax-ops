# Current State - Phase 0.2 Bootstrap/Preflight/Smoke Workflow In Progress

## Services Status

| Service | Status | Ports | Description |
|---------|--------|-------|-------------|
| postgres | ✅ Running | 5432 | PostgreSQL 16 database |
| redis | ✅ Running | 6379 | Redis 7 cache/store |
| api | ✅ Running | 8000 | Backend API server |
| frontend | ✅ Running | 9000 | Quasar/Vue frontend |

## Implementation Details

### Docker Compose Configuration
- All services run in a shared network: `digi-tax-network`
- postgres uses a persistent volume: `postgres_data`
- Services properly depend on each other for startup order
- Frontend build uses `network: host` and HTTP proxy build args

### Environment Variables
- PostgreSQL configured with user `digitax` and database `digi_tax`
- Redis configured with default settings
- Backend API configured with proper database and Redis connections
- Frontend configured with API base URL `http://localhost:8000/api/v1`
- Frontend build proxy configured for restricted networks

### Build Contexts
- Backend builds from `../digi-tax-backend`
- Frontend builds from `../digi-tax-frontend` (with HTTP proxy)

## Validation Status

| Check | Status | Notes |
|-------|--------|-------|
| docker-compose config | ✅ Pass | Configuration valid |
| Frontend build | ✅ Pass | Built successfully with proxy |
| Backend API health | ✅ Pass | `curl -s http://localhost:8000/health/check` returns `{"status":"ok"}` |
| Backend DB health | ✅ Pass | `curl -s http://localhost:8000/health/db` returns `{"status":"ok","database":"connected"}` |
| Frontend availability | ✅ Pass | `curl -I http://localhost:9000` returns HTTP 200 |

## Phase 0.2 Ops Workflow

- Added `scripts/bootstrap.sh` for safe DB creation and Alembic bootstrap inside Docker.
- Added `scripts/preflight.sh` for compose/env/readiness validation before or after deploy.
- Added `scripts/smoke_test.sh` for backend health, CORS, auth, dashboard, and frontend checks.
- Scripts are intended for repeatable local/staging deploy verification without host Python, Node, Bun, or Poetry.
- Current preflight explicitly checks that `DATABASE_URL` and `POSTGRES_DB` point to the same database name.

## Proxy Configuration

For restricted networks, the frontend build requires HTTP proxy settings in `.env`:

```bash
FRONTEND_BUILD_HTTP_PROXY=http://127.0.0.1:2080
FRONTEND_BUILD_HTTPS_PROXY=http://127.0.0.1:2080
FRONTEND_BUILD_ALL_PROXY=http://127.0.0.1:2080
```

## Next Steps

1. Validate the new bootstrap/preflight/smoke workflow against the real staging `.env`
2. Add worker services (worker-submission, worker-inquiry, worker-default, scheduler)
3. Implement nginx reverse proxy for production-like setup
4. Add monitoring with Prometheus and Grafana as optional profiles
5. Add CI/CD integration for automated deployments
