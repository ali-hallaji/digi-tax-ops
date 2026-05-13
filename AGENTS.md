# AGENTS.md — DigiTax Ops

You are working only inside the `digi-tax-ops` repository.

## Scope
This repo owns local orchestration and shared operational docs. It references sibling repos:

```txt
../digi-tax-backend
../digi-tax-frontend
```

## Phase 0 services
Create Docker Compose for:
- postgres
- redis
- api built from `../digi-tax-backend`
- worker-submission built from backend
- worker-inquiry built from backend
- worker-default built from backend
- scheduler built from backend
- frontend built from `../digi-tax-frontend`
- nginx placeholder

Keep MinIO, Prometheus, Grafana as optional profiles only, not default.

## Do not
- Do not add Kubernetes in Phase 0.
- Do not add CI/CD unless requested.
- Do not change backend/frontend code from ops repo.
- Do not put secrets in git.

## Before editing
List planned files and wait for approval unless told otherwise.
