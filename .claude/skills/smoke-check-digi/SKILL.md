---
description: Run smoke checks against the local/staging stack to confirm API health, auth, CORS, and frontend availability.
---

# smoke-check-digi

Run after any deploy to confirm the stack is healthy. Use the documented smoke script.

## Steps

1. Read `docs/progress.md` Active Blockers — note any `[DEPLOY]` blockers that may affect expected results.

2. Confirm all services are up:
   ```bash
   docker compose ps
   ```

3. Run the smoke test script:
   ```bash
   bash scripts/smoke_test.sh
   ```
   The script covers:
   - Backend health endpoint
   - CORS headers
   - OTP auth flow (request + verify)
   - Bearer-auth protected endpoints
   - Frontend availability on configured port
   - **Deploy-verification (stale-image guard):** reads `GET /health/version`
     (served backend SHA + image alembic head) and `GET /version.json` (served
     frontend SHA). When run in a deploy context (`BACKEND_SHA` / `FRONTEND_SHA`
     exported before the build), it **fails loudly** if the served SHA ≠ the
     deployed SHA, or if the image's alembic head ≠ the DB's current head — the
     exact check that catches a stale image passing an otherwise-green smoke.
     Without those env vars (ad-hoc local smoke) it just reports the served SHAs.

4. If `smoke_test.sh` is not available or fails, run manual checks:

   ```bash
   # API health
   curl -s http://localhost:8000/health | python3 -m json.tool

   # CORS preflight
   curl -sI -X OPTIONS http://localhost:8000/api/v1/me \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET"

   # Frontend availability
   curl -sI http://localhost:${FRONTEND_PORT:-3000}/ | head -5
   ```

5. Check logs for errors:
   ```bash
   docker compose logs --tail=50 api
   docker compose logs --tail=20 frontend
   ```

## Known Blockers to Note

- If `tax_items` migration (`c4e8b2d5f9a3`) has not run, `GET /api/v1/tax-items/search` will fail — this is a known `[DEPLOY]` blocker in frontend `docs/progress.md`.
- CORS is env-driven via `BACKEND_CORS_ORIGINS`. The `.env.example` default is `*` (wildcard) — this is an OPEN BLOCKER for production. Confirm staging/prod `.env` sets `BACKEND_CORS_ORIGINS` to comma-separated explicit origins (e.g. `https://app.example.com`) before any production deploy. Dev wildcard is acceptable; staging/prod must not use `*`.

## Output

```
## Smoke Check — digi-tax-ops

**Services up:** <docker compose ps summary>
**API health:** OK | FAIL
**CORS:** OK | FAIL
**Auth flow:** OK | FAIL
**Frontend:** OK | FAIL
**Log errors:** <list notable errors or "None">

**Result:** PASS | NEEDS FIXES
```
