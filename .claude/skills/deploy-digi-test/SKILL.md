---
description: Run a controlled local/staging deploy sequence: validate config, run preflight, apply migrations, start services.
---

# deploy-digi-test

Use when deploying or re-deploying the local/staging stack. Follows the documented deploy order.

## Pre-Deploy Checks (mandatory)

1. Read `docs/progress.md` Active Blockers — stop if any `[DEPLOY]` or `[INFRA]` blocker is unresolved.

2. Confirm `.env` exists and is not `.env.example`:
   ```
   !`ls -1 .env 2>/dev/null || echo "MISSING"`
   ```

3. Validate Compose config:
   ```bash
   docker-compose config
   ```
   Stop if this fails — do not proceed with broken config.

## Deploy Sequence

Run steps in order. Do not skip steps.

### Step 1: Start infrastructure
```bash
docker-compose up -d postgres redis
```

### Step 2: Start API
```bash
docker-compose up -d api
```

### Step 3: Apply migrations
```bash
docker-compose exec api python -m alembic upgrade head
```
Required after every backend deploy. Confirm it exits 0.

### Step 4: Start frontend
```bash
docker-compose up -d frontend
```

### Step 5: Check service status
```bash
docker-compose ps
```

### Step 6: Run preflight
```bash
bash scripts/preflight.sh
```

## Build Rules

Rebuild only when necessary (not for every deploy):

- Backend code/deps/Dockerfile changed:
  ```bash
  docker-compose build api && docker-compose up -d api
  ```
- Frontend source/deps/Dockerfile/`VITE_API_BASE_URL` changed:
  ```bash
  docker-compose build --no-cache frontend && docker-compose up -d --force-recreate frontend
  ```
  **Note:** `VITE_API_BASE_URL` is build-time — restarting without rebuild does not apply changes.

## Output

```
## Deploy — digi-tax-ops

**Blocker check:** <None | list>
**Compose config:** VALID | INVALID — stopped
**Migration result:** OK (exit 0) | FAILED — stopped
**Services up:** <docker-compose ps summary>
**Preflight:** PASS | FAIL

**Result:** PASS | NEEDS FIXES
```
