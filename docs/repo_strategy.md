# Repository Strategy

## Repository Model
Keep three active canonical repositories plus one historical frontend reference:

```txt
digi-tax-backend       # canonical backend
digi-tax-frontend      # canonical frontend
digi-tax-ops           # canonical ops
digi-tax-Front-source  # historical Lovable/design reference
```

`digi-tax-frontend` is canonical for future Claude Code-driven frontend development. `digi-tax-Front-source` is historical Lovable/design reference only. Lovable sync is deprecated and manual-emergency-only.
digi-tax-frontend is canonical for future Claude Code-driven frontend development.
digi-tax-Front-source is historical Lovable/design reference only.

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
- Canonical React/TanStack frontend implementation.
- Product UI, app shell, routes, forms, and frontend API integration.
- Frontend validation UX that follows backend-owned contracts and `VITE_API_BASE_URL`.

Does not own:
- Backend API contracts.

### digi-tax-Front-source
Owns:
- Historical Lovable/design reference only.

Does not own:
- Future product frontend implementation.
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
  digi-tax-frontend/
  digi-tax-ops/
  digi-tax-Front-source/   # historical Lovable/design reference
```

`digi-tax-ops/docker-compose.yml` references canonical sibling repos:

```yaml
services:
  api:
    build: ../digi-tax-backend
  frontend:
    build: ../digi-tax-frontend
```

Frontend product changes normally happen directly in `digi-tax-frontend`.

## Codex Workflow
- Work in one canonical repo at a time.
- Start from `AGENTS.md`, `docs/current_phase.md`, and `docs/progress.md`.
- Keep changes inside the repo that owns the requested behavior.
- Do not add Kubernetes or optional observability/storage stacks by default.
