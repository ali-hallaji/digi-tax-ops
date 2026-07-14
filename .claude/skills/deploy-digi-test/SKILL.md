---
description: Run a controlled local/staging deploy sequence: validate config, run preflight, apply migrations, start services.
---

# deploy-digi-test

Use when deploying or re-deploying the local/staging stack. Follows the documented deploy order.

## Pre-Deploy Checks (mandatory)

0. **GATE 0 — the experience harness (PH rule): no deploy while the harness is red.**
   ```bash
   cd ../digi-tax-frontend && pnpm harness
   ```
   All persona journey specs must pass against local BEFORE any push/deploy. After
   the deploy, re-run against dev: `pnpm harness --base-url https://dev.digiinvoice.ir`.
   Captcha is never disabled for the harness (the login helper waits for the real
   Altcha widget to solve). A red spec blocks the deploy — fix first.

1. Read `docs/progress.md` Active Blockers — stop if any `[DEPLOY]` or `[INFRA]` blocker is unresolved.

2. Confirm `.env` exists and is not `.env.example`:
   ```
   !`ls -1 .env 2>/dev/null || echo "MISSING"`
   ```

3. Validate Compose config:
   ```bash
   docker compose config
   ```
   Stop if this fails — do not proceed with broken config.

## Deploy Sequence

Run steps in order. Do not skip steps.

### Step 0: Stamp the build SHAs (deploy-verification guard)
Export the exact commit being built **before** any `build`, so the SHA is baked
into the image (`GET /health/version`) and the frontend (`/version.json`). Step 7
asserts the running stack serves these SHAs — a stale image then fails loudly.
```bash
export BACKEND_SHA="$(git -C ../digi-tax-backend rev-parse HEAD)"
export FRONTEND_SHA="$(git -C ../digi-tax-frontend rev-parse HEAD)"
```

### Step 0.5: Disk preflight before a `--no-cache` build (added 2026-07-14)
A `--no-cache` build writes a fresh full image; repeated builds accumulate
dangling images and once filled the server root to 100%, breaking a migration
mid-deploy. Reclaim unused **images + build cache** first — **never volumes**
(the DB lives in a named volume). A weekly cron does this too.
```bash
df -h /                    # confirm headroom
docker image prune -af     # unused images only — NOT volumes
docker builder prune -af   # build cache only  — NOT volumes
df -h /                    # verify before building
```
**Never `docker system prune --volumes`** here — it would delete the database.

### Step 1: Start infrastructure
```bash
docker compose up -d postgres redis
```

### Step 2: Start API
```bash
docker compose up -d api
```

### Step 3: Apply migrations
```bash
docker compose exec api python -m alembic upgrade head
```
Required after every backend deploy. Confirm it exits 0.

### Step 4: Start frontend
```bash
docker compose up -d frontend
```

### Step 5: Check service status
```bash
docker compose ps
```

### Step 6: Run preflight
```bash
bash scripts/preflight.sh
```

### Step 7: Deploy-verification + smoke (MANDATORY)
Run smoke with the SHAs from Step 0 still exported — the guard block **fails the
deploy** if the served backend/frontend SHA ≠ the deployed SHA, or if the image's
alembic head ≠ the DB's current head (the P3-image-on-new-schema regression).
```bash
BACKEND_SHA="$BACKEND_SHA" FRONTEND_SHA="$FRONTEND_SHA" bash scripts/smoke_test.sh
```
A non-zero exit here means the running stack is **not** the code you just deployed —
do not report the deploy as successful; rebuild with `--no-cache` and re-run.

## Build Rules

Rebuild only when necessary (not for every deploy). **Run Step 0 first** — compose
reads `${BACKEND_SHA}` / `${FRONTEND_SHA}` as build args, so an un-exported SHA
bakes `unknown` and Step 7 can't verify the image.

- Backend code/deps/Dockerfile changed:
  ```bash
  docker compose build api && docker compose up -d api
  ```
- Frontend source/deps/Dockerfile/`VITE_API_BASE_URL` changed:
  ```bash
  docker compose build --no-cache frontend && docker compose up -d --force-recreate frontend
  ```
  **Note:** `VITE_API_BASE_URL` is build-time — restarting without rebuild does not apply changes.

## Output

```
## Deploy — digi-tax-ops

**Blocker check:** <None | list>
**Compose config:** VALID | INVALID — stopped
**Migration result:** OK (exit 0) | FAILED — stopped
**Services up:** <docker compose ps summary>
**Preflight:** PASS | FAIL

**Result:** PASS | NEEDS FIXES
```
