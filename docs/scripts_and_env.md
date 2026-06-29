# Scripts & Env — What to Run When

_Last updated: 2026-06-29. Canonical single source for every runnable operation._

---

## The manager (start here)

```bash
python3 digi-tax-ops/scripts/digi-invoice-manager.py --help
```

Run from anywhere in the workspace; paths are resolved from the script's location.
It prints what it will run before running it, checks prerequisites, and exits with the
correct exit code.

---

## Quick reference

| When you want to… | Command |
|---|---|
| Check the stack is healthy | `setup:preflight` |
| First-time / fresh-clone setup | `setup:bootstrap` |
| Start the stack | `setup:up` |
| Load test accounts | `seed:dev` |
| Seed realistic demo data | `seed:demo` |
| Run all Alembic migrations | `db:upgrade` |
| Confirm tables actually exist (not just alembic head) | `db:status` |
| Start the frontend dev server | `front:dev` |
| Validate before commit | `front:typecheck` + `front:build` |
| Run backend pytest | `test:backend` |
| Run E2E (phase end only) | `test:e2e` (see below) |
| Smoke-test running stack | `maintenance:smoke` |
| Rebuild api image after backend code change | `maintenance:rebuild-api` |
| Diff env vars against code | `env:check` |
| Prepare for production | `env:prod` |

---

## All scripts (discovered)

| Script | Purpose | Category | Repo |
|---|---|---|---|
| `scripts/bootstrap.sh` | First-time DB init + Alembic migrations (idempotent) | setup | ops |
| `scripts/preflight.sh` | Docker + env + DB name + service readiness checks | setup | ops |
| `scripts/up_local_test.sh` | `docker-compose up -d` shortcut with wait | setup | ops |
| `scripts/smoke_test.sh` | Health / CORS / OTP / bearer / frontend smoke | maintenance | ops |
| `scripts/seed_demo_business.py` | Realistic demo business data via API | seed | ops |
| `app/cli/seed_dev_data.py` | Fixed test accounts 09120000000/099/001 | seed | backend |
| `app/cli/seed_qa_invoice.py` | QA invoice scenario data | seed | backend |
| `alembic upgrade head` | Apply all pending schema migrations | db | backend (via ops) |
| `alembic current` | Show applied migration head | db | backend (via ops) |
| `pnpm run dev` | Vite dev server (localhost:8080) | frontend | frontend |
| `pnpm run build` | Production build | frontend | frontend |
| `pnpm run typecheck` | TypeScript check (must be zero errors) | frontend | frontend |
| `pnpm e2e` | Playwright E2E suite (headless) | test | frontend |
| `pnpm e2e:watch` | E2E interactive watched run | test | frontend |
| `pnpm e2e:report` | Open last E2E HTML report | test | frontend |

---

## E2E: disable captcha + rate-limit first

E2E tests hit the real `/auth/otp/request` endpoint. With auth hardening on, this
returns 400 (captcha required) and the suite fails before the first step.

Before any E2E run, set in `digi-tax-ops/.env`:
```
AUTH_CAPTCHA_ENABLED=false
AUTH_RATE_LIMIT_ENABLED=false
```

Restore to `true` immediately after. The manager's `test:e2e` command prints this reminder.

---

## Env vars — canonical list

`digi-tax-ops/.env` is the **canonical** runtime env for the backend (injected by
docker-compose). The frontend reads its own `VITE_*` vars from `.env.local` (dev) or
the Docker build arg `VITE_API_BASE_URL` (Docker).

Run `env:check` to diff the code-defined list against your `.env` and refresh `.env.example`:

```bash
python3 digi-tax-ops/scripts/digi-invoice-manager.py env:check
```

### Authoritative env var list (from config.py + frontend source)

**Backend (pydantic Settings — env var = uppercase field name):**

| Env var | Default | Notes |
|---|---|---|
| `APP_NAME` | DigiTax Backend | |
| `DEBUG` | false | `true` exposes `dev_otp` in API responses |
| `LOG_LEVEL` | INFO | |
| `ENVIRONMENT` | development | |
| `SWAGGER_AUTO_AUTH_ENABLED` | false | set true in dev only |
| `HOST` / `PORT` | 0.0.0.0 / 8000 | managed by docker-compose uvicorn cmd |
| `BACKEND_CORS_ORIGINS` | * | lock down to domain in prod |
| `DATABASE_URL` | postgresql+asyncpg://… | must match POSTGRES_DB=digitax |
| `REDIS_URL` | redis://localhost:6379/0 | |
| `SECRET_KEY` | (insecure default) | **[SECRET] rotate before every deploy** |
| `ALGORITHM` | HS256 | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | |
| `AUTH_RATE_LIMIT_ENABLED` | true | false for E2E env only |
| `AUTH_RATE_LIMIT_MAX_ATTEMPTS` | 5 | |
| `AUTH_RATE_LIMIT_WINDOW_SECONDS` | 60 | |
| `AUTH_RATE_LIMIT_BLOCK_SECONDS` | 300 | |
| `AUTH_CAPTCHA_ENABLED` | true | false for E2E env only |
| `AUTH_CAPTCHA_MAX_NUMBER` | 100000 | PoW search space |
| `AUTH_CAPTCHA_TTL_SECONDS` | 300 | challenge validity |
| `MOADIAN_LEGACY_ENABLED` | false | keep false until R1B |
| `MOADIAN_*` | (empty) | per-tenant keys live in DB |

**Frontend (VITE_* — baked into bundle at build time):**

| Env var | Dev value | Prod value |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | `/api/v1` (same-origin) |
| `VITE_API_TIMEOUT_MS` | 30000 | 30000 |

---

## Production deploy checklist

```bash
python3 digi-tax-ops/scripts/digi-invoice-manager.py env:prod
```

Key changes required before any prod/staging deploy:
- `SECRET_KEY` → strong random value (`python3 -c "import secrets; print(secrets.token_hex(32))"`)
- `DEBUG=false`, `ENVIRONMENT=production`
- `BACKEND_CORS_ORIGINS=https://yourdomain.com`
- `SWAGGER_AUTO_AUTH_ENABLED=false`
- `VITE_API_BASE_URL=/api/v1` (relative — for nginx same-origin)
- `AUTH_CAPTCHA_ENABLED=true`, `AUTH_RATE_LIMIT_ENABLED=true` (already default)
