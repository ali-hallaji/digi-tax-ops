# Repository Strategy v1.3

## Final repo count
Create exactly three repos:

```txt
digi-tax-backend
digi-tax-frontend
digi-tax-ops
```

Do not create one giant root repo containing backend and frontend. Do not create many small service repos. Three repos gives clean IDE context and keeps deployment manageable.

## Why not one repo?
A single repo makes Zed/Ollama context noisy. The frontend agent may read backend tax code. The backend agent may modify UI files. Long prompts become expensive. Search context becomes polluted.

## Why not many repos?
More than three repos creates orchestration overhead before the product is stable. This is not yet the time for microservices.

## Ownership

### digi-tax-backend
Owns:
- FastAPI async API
- Database models and Alembic migrations
- Domain modules
- Compliance engine
- Invoice engine
- Submission engine
- Tax organization transports
- Workers
- Import processing
- Accounting/payroll boundaries
- Backend tests

Does not own:
- Vue components
- Docker Compose root orchestration
- Production Nginx config, except API path assumptions

### digi-tax-frontend
Owns:
- Quasar/Vue app
- App shell and layouts
- Taxpayer panel
- Central admin panel
- API client wrappers
- Form validation UX
- Bulk import UI
- Status polling/SSE UI

Does not own:
- Business tax calculations
- taxid generation
- signing/encryption
- database schema

### digi-tax-ops
Owns:
- docker-compose.yml
- Nginx config
- .env.example for local orchestration
- local volumes and service names
- shared docs
- API contract snapshots
- integration/run instructions
- future Kubernetes migration notes

Does not own:
- Domain logic
- UI components
- migrations except orchestration commands

## Workspace layout

```txt
~/work/digitax/
  digi-tax-backend/
  digi-tax-frontend/
  digi-tax-ops/
```

`digi-tax-ops/docker-compose.yml` references sibling repos by relative path:

```yaml
services:
  api:
    build: ../digi-tax-backend
  frontend:
    build: ../digi-tax-frontend
```

## Zed opening order
1. Open `digi-tax-ops` first and create orchestration.
2. Open `digi-tax-backend` and create backend skeleton.
3. Open `digi-tax-frontend` only after backend health/API skeleton exists.

## Agent concurrency rule
Start with one build agent and one review agent. Do not run backend and frontend generation simultaneously until Phase 0 is stable.
