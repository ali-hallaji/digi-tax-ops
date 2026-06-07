---
description: Review the current ops diff for Compose correctness, env safety, script correctness, and cross-repo boundary compliance before commit.
---

# review-ops-diff

Run before every commit in digi-tax-ops.

## Context Injection

```
!`git diff --stat HEAD`
!`git diff --name-only HEAD`
!`git status --short`
```

## Review Checklist

### 1. Active Blockers (check first)
- Read `docs/progress.md` Active Blockers.
- Flag any blocker touched or depended on by this diff.

### 2. Cross-Repo Boundary
- No backend or frontend application code edited from this repo.
- `docker-compose.yml` build contexts remain `../digi-tax-backend` and `../digi-tax-frontend`.
- No Kubernetes, Prometheus, Grafana, or MinIO added to default Compose stack.

### 3. Compose / Docker Safety
- `docker-compose config` would pass for any `docker-compose.yml` change.
- Port mappings are consistent with documented ports: postgres 5432, redis 6379, api 8000, frontend 3000 (FRONTEND_PORT).
- No hardcoded credentials in `docker-compose.yml` — values come from `.env`.
- `VITE_API_BASE_URL` is set as a build arg, not a runtime env var only.

### 4. Environment Safety
- No secrets, proxy URLs, or credentials in `.env.example` or committed files.
- `DATABASE_URL` db name matches `POSTGRES_DB` in `.env.example`.
- All required env vars documented in `.env.example`.

### 5. Script Correctness
- Shell scripts pass `bash -n <script>` syntax check.
- Scripts reference services by their Compose service name, not hardcoded IPs.
- Migration step (`alembic upgrade head`) is included in any deploy-related script change.

### 6. API Contract Snapshots
- Any update to `api-contracts/` is a real backend OpenAPI export, not a manually edited file.
- Snapshot version matches backend current phase.

## Output

```
## Ops Diff Review — digi-tax-ops

**Blockers touched:** <list or "None">
**Cross-repo boundary:** OK | VIOLATION — describe
**Compose validity:** OK | FAIL
**Env safety:** OK | issues listed
**Script syntax:** OK | FAIL
**Contract snapshot:** OK | N/A | needs re-export

**Result:** PASS | NEEDS FIXES
```
