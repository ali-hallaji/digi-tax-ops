# Ops Phase Checklists

## Phase 0
- [x] docker-compose.yml exists.
- [x] .env.example exists.
- [x] postgres service.
- [x] redis service.
- [x] api service built from sibling backend.
- [x] frontend service built from sibling frontend.
- [x] nginx placeholder.
- [x] no secrets.
- [x] no Kubernetes.

## Phase 0.2
- [x] scripts/bootstrap.sh — DB creation and Alembic bootstrap inside Docker.
- [x] scripts/preflight.sh — compose/env/readiness/DB-name consistency checks.
- [x] scripts/smoke_test.sh — health, CORS, OTP auth, bearer-auth, dashboard, frontend routes.
- [x] Server deployment runbook (docs/server_deploy_runbook.md).
- [x] Frontend orchestration updated for production SSR Node container.
- [ ] API contract snapshots exported and committed to api-contracts/.
- [ ] Phase 0.2 scripts validated against current staging .env.
