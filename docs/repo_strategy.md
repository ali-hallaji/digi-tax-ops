# Repository Strategy

## Canonical Repositories
Keep exactly three canonical repositories:

```txt
digi-tax-backend
digi-tax-Front-source
digi-tax-frontend
digi-tax-ops
```

`digi-tax-Front-source` is the canonical React/TanStack/Lovable frontend source repo. `digi-tax-frontend` is the synced deploy/build frontend repo generated from it.

## Ownership

### digi-tax-backend
Owns:
- FastAPI async API.
- Database models and Alembic migrations.
- Backend API/OpenAPI contracts.
- Domain modules and backend tests.
- Compliance, invoice, submission, transport, worker, import, reporting, accounting/payroll boundary code.

Does not own:
- Frontend UI implementation.
- Docker Compose root orchestration.
- Nginx configuration, except API path assumptions.

### digi-tax-frontend
Owns:
- Synced deploy/build frontend output.
- Docker/static build and deployment-facing frontend files.
- Routine sync from `../digi-tax-Front-source` through `scripts/sync_lovable.sh`.

Does not own:
- Canonical product UI source.
- Backend API contracts.

### digi-tax-Front-source
Owns:
- Canonical React/TanStack/Lovable frontend source.
- UI/UX design and React source generation.
- Frontend API integration code that follows backend-owned contracts and `VITE_API_BASE_URL`.

Does not own:
- Official tax calculations.
- Tax ID generation.
- Signing/encryption.
- Database schema.
- Backend API contracts.

### digi-tax-ops
Owns:
- Docker Compose.
- Nginx.
- Scripts.
- API contract snapshots.
- Environment examples.
- Integration and local/staging run instructions.

Does not own:
- Backend application logic.
- Frontend application logic.
- Migrations except orchestration commands.

## Workspace Layout

```txt
workspace/
  digi-tax-backend/
  digi-tax-Front-source/   # canonical React/TanStack/Lovable source
  digi-tax-frontend/
  digi-tax-ops/
```

`digi-tax-ops/docker-compose.yml` references canonical sibling repos:

```yaml
services:
  api:
    build: ../digi-tax-backend
  frontend:
    build: ../digi-tax-frontend
```

Frontend product changes normally happen in `digi-tax-Front-source`, then sync into `digi-tax-frontend`.

## Codex Workflow
- Work in one canonical repo at a time.
- Start from `AGENTS.md`, `docs/current_phase.md`, and `docs/progress.md`.
- Keep changes inside the repo that owns the requested behavior.
- Do not add Kubernetes or optional observability/storage stacks by default.
