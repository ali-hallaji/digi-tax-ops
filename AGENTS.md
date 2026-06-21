# AGENTS.md - DigiTax Ops

You are working only inside `digi-tax-ops`, the canonical operations repository.

## Start Here
- Read `AGENTS.md`, `docs/current_phase.md`, and `docs/progress.md` before planning.
- Use `docs/architecture_decisions.md` for immutable decisions.
- Work on one task per session unless the user explicitly broadens scope.
- List planned files and wait for approval unless the user explicitly says to proceed.
- Keep edits scoped to ops/docs/scripts and update `docs/progress.md` after changes.
- After editing, run relevant validation or clearly state why it was skipped.

## Scope
This repo owns Docker Compose, Nginx, scripts, API contract snapshots, integration docs, environment examples, and local/staging orchestration.

Sibling canonical repos:
```txt
../digi-tax-backend
../digi-tax-frontend
```

The frontend is React/TanStack/Vite.

## Canonical Database Name

**One name. No exceptions. `digitax` (no underscore).**

The Postgres database name is `digitax`. Every file that references a database name must use `digitax`:
- `POSTGRES_DB=digitax` in `.env` and `.env.example`
- `DATABASE_URL=postgresql+asyncpg://digitax:digitax@postgres:5432/digitax` in `.env`
- `pg_isready -d ${POSTGRES_DB:-digitax}` in `docker-compose.yml`
- `sqlalchemy.url = ...@postgres:5432/digitax` in `alembic.ini`
- Default in `app/core/config.py`

**Guardrail:** `scripts/preflight.sh` asserts (1) the database name in `DATABASE_URL` matches `POSTGRES_DB`, and (2) no unexpected databases exist on the server beyond the system DBs and the canonical `digitax`. If either check fails, preflight exits non-zero. Run it before every deploy.

**Orphan (resolved 2026-06-21):** A stale database `digi_tax` (8 tables) from an earlier misconfiguration has been permanently dropped. The preflight orphan-DB check now prevents any similar database from silently persisting.

## Do Not
- Do not edit backend or frontend application logic from this repo.
- Do not add Kubernetes by default.
- Do not add Prometheus, Grafana, MinIO, or other observability/storage stacks by default.
- Do not put secrets in git.
- Do not use Python, Poetry, or Python package installation on the host for backend/ops validation.
- Run backend/ops validation through Docker/Compose unless explicitly approved otherwise.
- Do not rebuild Docker images for every small change when existing containers or volume mounts are enough.
- Rebuild only for dependency, Dockerfile, base image, or environment/build config changes.
- Do not embed proxy URLs, ports, credentials, tokens, or network workarounds in source, docs, Dockerfiles, Compose, or package files.
- **Do not introduce a second database name.** `digitax` is the one canonical name — any new reference that differs is a bug.
