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
- [x] WeasyPrint system packages in backend Dockerfile (api image must be rebuilt).
- [ ] API contract snapshots exported and committed to api-contracts/.
- [ ] Phase 0.2 scripts validated against current staging .env.
- [ ] Migration-state check added to smoke_test.sh (alembic current vs alembic heads).
- [ ] Nginx configured for production TLS termination (currently placeholder.conf only).
- [ ] OTP moved to Redis production storage.
- [ ] All Moadian migrations applied on staging: e5f9a2c1d7b3, f3a8b2c1d5e7, moadian_tenant_profiles.
