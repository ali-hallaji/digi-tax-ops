# Server Deploy Runbook

> ⛔ **COMPOSE v2 ONLY.** Every command here is `docker compose` (space, v2). The server
> has ONLY the v2 plugin; the `docker-compose` (v1, hyphen) binary is retired and shadowed
> by a STOP wrapper at `/usr/local/bin/docker-compose`.
> **If `docker-compose` (v1) is ever invoked on the server — by a script, a habit, or a
> `command not found` fallback — STOP immediately and report.** Mixing v1 and v2 once
> deployed the OLD image while "building" the new one (v1 names images `project_service`,
> v2 names them `project-service`). **Always verify a deploy with the version guard below
> (§ Deploy-Verification), never by trusting the build log.**

## Purpose And Scope

This runbook covers staging/server deployment for DigiTax using the three
separate canonical repositories. The workspace root is not a git repository;
each project is updated and deployed independently.

`digi-tax-ops` coordinates deployment through Docker Compose, Nginx/reverse
proxy configuration, environment examples, and validation scripts. Do not use
`digi-tax-Front-source` for deployment; it is historical Lovable/design
reference only.

## Required Directory Layout

```txt
workspace/
  digi-tax-backend/
  digi-tax-frontend/
  digi-tax-ops/
```

Run deployment commands from `digi-tax-ops` unless a command explicitly uses
`git -C` for a sibling repository.

## Connection Vars (`$DIGI_TEST_SSH` / `$DIGI_TEST_PATH`)

The test server is referenced **only** via these env vars — never hardcode the
IP/SSH in git (ops CLAUDE.md hard rule).

- **Where they live:** `digi-tax-ops/.deploy.env` — a **gitignored** store (same
  treatment as `.env`; `git check-ignore` confirms it). It holds the two
  `export` lines and is the single source of truth. **Never commit it.**
- **Auto-load:** `~/.zshenv` sources `.deploy.env` if present. `~/.zshenv` is read
  by *every* zsh invocation — interactive terminals **and** non-interactive shells
  (Claude Code's Bash tool) — so every session has the vars with no manual
  `export`. If the store is ever missing, recreate it with the two lines
  (`DIGI_TEST_SSH`, `DIGI_TEST_PATH`); their values are known to the founder.
- **Usage — mind the shell (the value carries an `ssh` port flag, i.e. spaces):**
  - **bash** (this runbook's scripts, `bash -c`, `bash -s` heredocs): plain
    `ssh $DIGI_TEST_SSH …` word-splits correctly.
  - **zsh** (the Bash tool's default shell, the founder's terminal): zsh does
    **not** word-split unquoted expansions — use `ssh ${=DIGI_TEST_SSH} …`, or
    wrap the call in `bash -c '…'`. Plain `$DIGI_TEST_SSH` in zsh fails with
    "hostname contains invalid characters".

## Pre-Deploy Safety Checks

### GATE 0 — the experience harness (MANDATORY, PH rule)

**No deploy while the harness is red.** Before ANY push/deploy, run the Playwright
experience harness green against local, and after deploying, run it green against dev:

```bash
cd ../digi-tax-frontend
pnpm harness                                        # local (default base URL)
pnpm harness --base-url https://dev.digiinvoice.ir  # after deploy, against dev
```

One journey spec per seed persona; logins go through the REAL login page (dev-OTP,
Altcha PoW solved by the real widget — never disable captcha for the harness).
Artifacts land in `qa-screens/harness-<ts>/`. A red spec blocks the deploy — fix
first, never "deploy anyway".

### Repo cleanliness

Check all three repos before pulling or deploying:

```bash
git -C ../digi-tax-backend status --short
git -C ../digi-tax-frontend status --short
git -C ../digi-tax-ops status --short
```

Dirty files must be understood before pulling. Do not overwrite local server
changes, ignored deployment env files, or emergency hotfixes without deciding
whether they should be committed, backed up, or discarded.

## Server Update Quick Path

Use this path for the normal staging/server update with three separate repos.
The order is: pull backend, pull frontend, pull ops, validate Compose,
build/recreate `api` if backend changed, run the migration, build/recreate
`frontend` if frontend changed or `VITE_API_BASE_URL` changed, then run
preflight and smoke checks.

Full staging update:

```bash
cd /usr/local/digi-tax-ops

git -C ../digi-tax-backend pull
git -C ../digi-tax-frontend pull
git -C . pull

docker compose config

# DISK PREFLIGHT (added 2026-07-14 after a DiskFull incident): a `--no-cache`
# build writes a fresh full image; repeated builds pile up dangling images and
# once filled the 38G root to 100%, which broke a migration mid-deploy. Reclaim
# unused IMAGES + build cache BEFORE building. NEVER prune volumes (the DB volume
# must survive). A weekly cron (/etc/cron.weekly/docker-image-prune) also does this.
df -h /                              # confirm headroom first
docker image prune -af               # unused images only — NOT volumes
docker builder prune -af             # build cache only — NOT volumes
df -h /                              # verify reclaimed space before building

# Bake the git SHA of EACH repo into its image (the stale-image guard reads it back).
export BACKEND_SHA="$(git -C ../digi-tax-backend rev-parse HEAD)"
export FRONTEND_SHA="$(git -C ../digi-tax-frontend rev-parse HEAD)"

docker compose build api
docker compose up -d postgres redis api
docker compose exec api python -m alembic upgrade head

docker compose build --no-cache frontend
docker compose up -d --force-recreate frontend

bash scripts/preflight.sh
bash scripts/smoke_test.sh          # includes the Deploy-Verification guard (below)
```

> **Never `docker system prune --volumes`** on this server. The postgres data
> lives in a named volume; `--volumes` would delete the database. Prune only
> `image` and `builder` (both safe). See CLAUDE gotcha #14 lineage.

Backend-only update:

```bash
docker compose build api
docker compose up -d api
docker compose exec api python -m alembic upgrade head
```

Use this when backend source, backend dependencies, backend Dockerfile inputs,
or migrations changed.

Frontend-only update:

```bash
docker compose build --no-cache frontend
docker compose up -d --force-recreate frontend
```

Use this when frontend source changes or `VITE_API_BASE_URL` changes. The
frontend must be rebuilt because the Vite/TanStack build bakes
`VITE_API_BASE_URL` into the frontend bundle. Restarting the existing frontend
container is not enough after frontend source or frontend env changes. If the
browser still calls an old API URL after deployment, rebuild the frontend image
and hard-refresh the browser cache.

## Pull And Update Sequence

Pull each repository independently. Use the deployment branch or tag chosen for
that environment; do not assume the same branch name everywhere.

```bash
git -C ../digi-tax-backend fetch --all --tags
git -C ../digi-tax-backend checkout <backend-branch-or-tag>
git -C ../digi-tax-backend pull --ff-only

git -C ../digi-tax-frontend fetch --all --tags
git -C ../digi-tax-frontend checkout <frontend-branch-or-tag>
git -C ../digi-tax-frontend pull --ff-only

git -C ../digi-tax-ops fetch --all --tags
git -C ../digi-tax-ops checkout <ops-branch-or-tag>
git -C ../digi-tax-ops pull --ff-only
```

Recommended update order is backend, frontend, then ops. If deploying tags or
detached commits, replace `pull --ff-only` with the environment's approved
checkout procedure.

## Environment Checks

The server must have a deployment `.env` in `digi-tax-ops`. Keep real secrets
out of git and out of documentation.

Check at least these values before building or restarting:

- `DATABASE_URL`
- `POSTGRES_DB`
- `VITE_API_BASE_URL`
- `FRONTEND_PORT`
- any other runtime-only secrets required by the deployment

`VITE_API_BASE_URL` is build-time frontend configuration baked into the SSR
frontend bundle. Changing it requires rebuilding the `frontend` image. For
same-origin deployments behind the ops reverse proxy, `/api/v1` is usually the
right value. For direct-access staging, set the environment-specific public API
base URL in the server's ignored `.env`.

Restarting the existing `frontend` container is not enough after frontend source
changes or frontend build-time env changes.

Runtime-only secrets must remain runtime environment values. Do not pass them as Docker build args.

### STUFFID catalog drop-folder (`data/stuffid/`)

The `api` service bind-mounts `./data/stuffid` → `/data/stuffid` (read-write;
declared in `docker-compose.yml`). On every api startup a background thread
scans it for the newest `stuffid_catalog_YYYYMMDD.tar.zst` (Jalali date in the
name) and imports it into `tax_stuff_ids` **without blocking startup**; an
already-imported archive (sha256 recorded in `catalog_imports`) is skipped
silently, so restarts stay fast. Full convention + packing steps:
`data/stuffid/README.md` (committed; archives themselves are gitignored).

Operator one-liner to place/refresh the catalog on any server:

```bash
scp stuffid_catalog_<جلالیYYYYMMDD>.tar.zst ${=DIGI_TEST_SSH}:$DIGI_TEST_PATH/digi-tax-ops/data/stuffid/ \
  && ssh ${=DIGI_TEST_SSH} "cd $DIGI_TEST_PATH/digi-tax-ops && docker compose restart api"
```

(Alternatively upload through the admin page «شناسه‌های کالا و خدمت» — same
pipeline, no restart needed.) Verify after deploy: admin system-health shows
«کاتالوگ شناسه‌ها: به‌روز — نسخهٔ … · ~۴M ردیف», or
`GET /api/v1/admin/stuff-catalog/status` → `state: "ready"`. Budget ~6–7 min
import time and ~2.5 GB of Postgres volume growth on first import.

### Rate-limiter client IP behind the proxy (P7a)

The auth rate limiter keys on the real client IP, not the proxy peer, so a single
client's burst can't lock out the whole site. It trusts `X-Forwarded-For` ONLY
when the request's TCP peer is a trusted proxy (`TRUSTED_PROXIES`, comma-separated
IPs/CIDRs; default = localhost + the private ranges the docker/compose network and
nginx live in), then takes the right-most untrusted hop; a spoofed XFF from an
untrusted peer is ignored and the peer IP is used.

- **nginx requirement (already satisfied):** the site config must forward the
  client IP with `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`.
  Verified present in `/etc/nginx/sites-available/dev.digiinvoice.ir` (and
  `/etc/nginx/proxy_params`). No nginx change was needed for P7a.
- To tighten keying in production, set `TRUSTED_PROXIES` to the exact nginx +
  compose subnet instead of the broad private-range default.
- **Live proof:** two simulated client IPs via XFF through the real nginx — one
  bursts to `429`, the other stays `200` (see the smoke section).

### Moadian Iran-egress (MOADIAN_PROXY_*)

`tp.tax.gov.ir` is **Iran-access-only**. A server (or laptop) OUTSIDE Iran cannot
reach it directly — a connection test / real submission never leaves (null
`server_time`, no HTTP response; this is NOT a crypto/auth rejection). Two ways to
give the api an Iran egress:

- an **in-Iran SOCKS/HTTP proxy** the api routes Moadian traffic through, or
- an **Iran-hosted egress** for the api itself.

`MOADIAN_PROXY_*` (opt-in, default OFF) wires an egress proxy into the **Moadian
client only** — never the global httpx client or SMS:

```
MOADIAN_PROXY_ENABLED=true
MOADIAN_PROXY_URL=socks5h://127.0.0.1:2080   # socks5h = DNS resolved THROUGH the
                                             # proxy (REQUIRED when the domain
                                             # doesn't resolve outside Iran)
MOADIAN_PROXY_USERNAME=                       # optional
MOADIAN_PROXY_PASSWORD=                       # optional
```

- If `ENABLED=true` and `URL` is empty/invalid, the api **fails to start** with a
  clear error (no silent misconfiguration).
- When OFF, the Moadian client connects DIRECTLY (byte-identical to before).
- The connection-test response carries `transport: {proxy, target}` and precise
  error codes (`proxy_unreachable` / `dns_failed` / `connect_timeout` / `tls_error`
  / `http_error` / `auth_rejected`) instead of one generic failure; every attempt
  is logged to `moadian_api_log` with `used_proxy` (never the URL or credentials).
- **Currently for local/testing only.** Production egress topology is a founder
  decision — see backlog «توپولوژی خروجی ایران برای مودیان در پروداکشن». TLS to
  the Tax Org stays end-to-end; the proxy only forwards bytes.

## Compose Config Validation

Validate Compose before building or restarting services:

```bash
cd ../digi-tax-ops
docker compose config
```

Fix config errors before continuing. Do not deploy from an invalid Compose
configuration.

## Build Decision Matrix

Use targeted rebuilds. Do not rebuild every image by default.

| Change type | Rebuild needed |
|-------------|----------------|
| Backend code, backend dependencies, backend Dockerfile, or migrations changed | Rebuild `api` and backend worker images if those services are present |
| Frontend code, frontend Dockerfile, frontend dependencies, or `VITE_API_BASE_URL` changed | Rebuild `frontend` |
| Only ops docs changed | No image rebuild required |
| `docker-compose.yml`, Nginx, or env changed | Validate config, then recreate only affected services |

## Example Build Commands

Build frontend only:

```bash
docker compose build --no-cache frontend
docker compose up -d --force-recreate frontend
```

Build API/backend only:

```bash
docker compose build api
```

Build API and frontend:

```bash
docker compose build api frontend
```

Recreate changed services after a targeted build:

```bash
docker compose up -d --no-deps --force-recreate <service-name>
```

Start or refresh the default app services:

```bash
docker compose up -d postgres redis api frontend
```

If worker services are added to this Compose project later, rebuild and recreate
only the changed worker services when backend worker code or worker image inputs
change.

## Bootstrap And Migrations

Run the migration after backend changes, migration changes, first server setup,
or when the database may not have the expected schema:

```bash
docker compose exec api python -m alembic upgrade head
```

Run migrations inside the `api` container after `postgres`, `redis`, and `api`
are up. Run them before smoke tests.

Run preflight after services are up:

```bash
bash scripts/preflight.sh
```

Preflight validates Compose, required env, database consistency, container
readiness, and API database env visibility.

## Start And Restart Sequence

Use this order for a normal deployment:

```bash
docker compose up -d postgres redis
docker compose up -d api
docker compose up -d frontend
```

If an Nginx/reverse proxy service is present in the Compose project, start or
recreate it after API and frontend are healthy:

```bash
docker compose up -d nginx
```

Do not force a backend rebuild unless backend code, backend dependencies,
Dockerfile inputs, migrations, or related service configuration changed.

## Deploy-Verification (stale-image guard) — MANDATORY

This is the check that would have caught the P3-image-on-new-schema regression: the
build "succeeded" but the OLD image was running. After `up` + migrate, assert that the
image actually SERVING is the commit you just deployed, and that the DB schema matches
the image's migration graph. Any mismatch **FAILS the deploy loudly** — never ship past it.

`scripts/smoke_test.sh` runs this automatically; to run it standalone:

```bash
cd /usr/local/digi-tax-ops
BACKEND_SHA="$(git -C ../digi-tax-backend rev-parse HEAD)"
FRONTEND_SHA="$(git -C ../digi-tax-frontend rev-parse HEAD)"

VER="$(curl -fsS localhost:8000/health/version)"                 # {git_sha, alembic_head}
SERVED_SHA="$(printf '%s' "$VER" | python3 -c 'import sys,json;print(json.load(sys.stdin)["git_sha"])')"
CODE_HEAD="$(printf '%s' "$VER" | python3 -c 'import sys,json;print(json.load(sys.stdin)["alembic_head"])')"
DB_HEAD="$(docker compose exec -T api alembic current 2>/dev/null | grep -oE '[a-z0-9]{12}\b' | head -1)"
FE_SHA="$(curl -fsS localhost:3000/version.json | python3 -c 'import sys,json;print(json.load(sys.stdin)["sha"])')"

[ "$SERVED_SHA" = "$BACKEND_SHA" ] || { echo "DEPLOY FAIL: api serves $SERVED_SHA, deployed $BACKEND_SHA (STALE IMAGE)"; exit 1; }
[ "$CODE_HEAD" = "$DB_HEAD" ]       || { echo "DEPLOY FAIL: image alembic head $CODE_HEAD != DB head $DB_HEAD (MIGRATIONS OUT OF SYNC)"; exit 1; }
[ "$FE_SHA" = "$FRONTEND_SHA" ]     || { echo "DEPLOY FAIL: frontend serves $FE_SHA, deployed $FRONTEND_SHA (STALE FRONTEND)"; exit 1; }
echo "OK deploy-verification: api=$SERVED_SHA frontend=$FE_SHA alembic=$CODE_HEAD"
```

`GET /health/version` returns the git SHA baked into the api image + that image's alembic
head. `GET /version.json` (frontend) returns the frontend build SHA. If either SHA differs
from the just-deployed HEAD, or the image's migration graph doesn't match the DB, a stale
image is serving — STOP and investigate (usually a v1/v2 image-name split; see §13 gotcha 14).

## Validation After Deploy

Before next deploy verification — server test-artifact cleanup (one-time,
logged 2026-07-10): delete the Phase-2 test user `d5deploystaff` and the two
«استقرار» test invoice drafts in the demo tenant **via the app/API path (not
raw psql)** so linked payments and derived paid state recompute correctly;
then verify the demo-tenant dashboard numbers match expectations.

Run automated checks:

```bash
bash scripts/preflight.sh
bash scripts/smoke_test.sh
```

Manual checks:

- Frontend `/login` should load.
- Frontend `/app` should not return 404 or crash.
- Deep route `/app/tax/invoices` should refresh without breaking routing and
  should either render correctly or route through the expected login guard.
- Backend `/docs` should load when enabled for the environment.
- Backend health endpoint should return a healthy response.
- Smoke checks should not expose obvious hardcoded backend IPs in frontend HTML
  or bundle responses.

**Final report — always include the persona-login guide path:** every deploy
report ends with a pointer to `docs/persona_logins.md` (the guided per-persona
«چه چیزی را ببین» review checklist, generated from `world_fixtures.py`). If the
seed changed this deploy, regenerate it first:

```bash
docker compose exec -T api python -m app.cli.world_fixtures > docs/persona_fixtures.json
docker compose exec -T api python -m app.cli.world_fixtures --markdown > docs/persona_logins.md
```

## Reset the verification world (dev) — SEED-12

The persona world (`app.cli.seed_realistic_world`) is the canonical QA data.
Locally the founder runs `make reset-world` (or `bash scripts/reset_world.sh`). On
dev/staging, use the SAME script — it now **snapshots automatically before the wipe**
and **guards real Moadian keys** (see below), so the old hand-rolled snapshot line is
no longer needed:

```bash
# Point the auto-snapshot at /root, then run the guarded reset.
RESET_WORLD_SNAPSHOT_DIR=/root bash scripts/reset_world.sh
```

What the script does, in order (the seed never stores a Moadian key, so any
`encrypted_private_key_blob` is real, runtime-created material it cannot recreate):
(0a) **دیباتک (`09120000000`) is PROTECTED** — its key is captured to a holding schema
before the wipe and restored onto the freshly-seeded tenant afterward («🔒 … PRESERVED»),
so the founder's registered key survives every reseed with no `--force`;
(0b) a real key on ANY OTHER tenant **blocks** the wipe — it lists the businesses and
exits 1; only `--force` overrides (and `--force` wipes EVERYTHING, including دیباتک's key);
(1) `pg_dump | gzip` snapshot to `$RESET_WORLD_SNAPSHOT_DIR` (default `./.reseed-snapshots/`),
path printed; (2) wipe → `alembic upgrade head` → seed → regenerate `persona_logins.md` +
`persona_fixtures.json` + the README table.

- **Dev has no real keys** (MODE=mock, personas only), so the reset proceeds without
  `--force`. If it reports an OTHER-tenant key, STOP — a real merchant connected on that
  box; do not `--force` without confirming the key is disposable (it is destroyed and only
  the snapshot recovers it). دیباتک's key, if present, is always auto-preserved.
- The per-persona login guide is `docs/persona_logins.md` (regenerated). Surface it in
  the deploy report so the founder's taste-review is guided.

## Notifications / SMS go-live switch (Kavenegar) — STAGED, allowlist first

SMS is provider-agnostic and OFF (console) by default — dev keeps returning `dev_otp`.
Turning on real SMS needs **no code change**. Do it in THREE stages, never in one
jump: the dev database holds real-looking mobiles, and a single careless
`SMS_PROVIDER=kavenegar` on a box with seeded/real numbers texts strangers.

**The safety valve: `SMS_ALLOWLIST`** (PC-T5). Comma-separated mobiles. While it is
NON-EMPTY, only those numbers can receive a real SMS; every other recipient is
logged to the console instead and audited `status=suppressed` (the admin
«آخرین پیامک‌ها» panel shows suppressed rows distinctly, and still records which
provider it WOULD have used). Honored by BOTH providers. Empty = no restriction.

```bash
# ── Stage 1 — console (today, and the permanent default for local/dev) ────────
SMS_PROVIDER=console
SMS_ALLOWLIST=                      # irrelevant while console; nothing is sent

# ── Stage 2 — real provider, blast radius = the founder's own handset ─────────
SMS_PROVIDER=kavenegar
KAVENEGAR_API_KEY=<the key>
KAVENEGAR_OTP_TEMPLATE=digiotp      # must match the template name in the Kavenegar panel
SMS_ALLOWLIST=09XXXXXXXXX           # the founder's mobile ONLY
docker compose up -d --no-deps --force-recreate api
#   Verify BOTH halves before going further:
#   a) request an OTP for the ALLOWLISTED handset → SMS arrives; «آخرین پیامک‌ها»
#      shows status=sent + a provider_ref.
#   b) request an OTP for any OTHER number → NO SMS arrives; the row reads
#      status=suppressed, provider=kavenegar. This is the proof the valve works.
#      SELECT status, provider FROM notification_log ORDER BY created_at DESC LIMIT 5;

# ── Stage 3 — full send (only after stage 2 is proven on this host) ───────────
SMS_ALLOWLIST=                      # empty ⇒ everyone
docker compose up -d --no-deps --force-recreate api
```

Rollback at any stage: `SMS_PROVIDER=console` (or re-populate `SMS_ALLOWLIST`) and
restart api. Reminders-by-SMS is still «به‌زودی» — only the OTP path is wired
through the core today.

## Payments / checkout go-live switch (Zarinpal)

Checkout ships on a SIMULATED gateway shaped exactly like Zarinpal
(`request → redirect → callback → verify`), so going live is config, not a
refactor. The sim page is badged «درگاه آزمایشی» and moves no money.

```bash
# Default everywhere until real keys exist:
PAYMENT_GATEWAY=sim

# Go-live:
PAYMENT_GATEWAY=zarinpal
ZARINPAL_MERCHANT_ID=<merchant id>
ZARINPAL_BASE_URL=https://api.zarinpal.com
docker compose up -d --no-deps --force-recreate api
```

**`PAYMENT_FRONTEND_BASE_URL` is required wherever the frontend is not
same-origin with the API.** The gateway callback 302s the merchant to
`{PAYMENT_FRONTEND_BASE_URL}/app/plans/orders/{id}`; if it is unset, the redirect
is derived from the request and — on a split-origin setup like local dev (Vite
:8080 vs API :8000) — lands on the API origin and 404s AFTER a successful
payment. Set it explicitly:

```bash
# local dev
PAYMENT_FRONTEND_BASE_URL=http://localhost:8080
# dev server (same-origin behind nginx — set it anyway, don't rely on derivation)
PAYMENT_FRONTEND_BASE_URL=https://dev.digiinvoice.ir
```

Prices are admin-managed at `/admin/plans` («قیمت ماژول‌ها»), NOT in env. A module
with no published price shows «استعلام قیمت» to the merchant and cannot be bought
online — that is the honest default, not a bug.

## Rollback Notes

Keep rollback simple:

```bash
git -C ../digi-tax-backend checkout <previous-backend-commit-or-tag>
git -C ../digi-tax-frontend checkout <previous-frontend-commit-or-tag>
git -C ../digi-tax-ops checkout <previous-ops-commit-or-tag>
```

Then rebuild only affected images, recreate affected services, and rerun:

```bash
bash scripts/preflight.sh
bash scripts/smoke_test.sh
```

Do not invent a release system in an incident. Use the previous known-good git
commits or tags for the repositories that changed.

## Proxy And Restricted Network Notes

Some server networks require proxy values for Docker builds.

Rules:

- Do not commit proxy values.
- Do not write real proxy settings into Dockerfiles, Compose, app code, package
  files, docs, or lock files.
- Supply proxy values from the operator shell or ignored deployment env only.
- Remove temporary shell proxy values after the build if they are not meant to
  remain in the server session.

## Troubleshooting

Postgres container stopped:

Run `docker compose ps`, start `postgres`, then rerun `bash scripts/preflight.sh`.

Frontend still on old image:

Run `docker compose build --no-cache frontend`, then run
`docker compose up -d --force-recreate frontend`. Recheck `/login`, `/app`, and
a deep route.

`VITE_API_BASE_URL` changed but frontend was not rebuilt:

Run `docker compose build --no-cache frontend`, then run
`docker compose up -d --force-recreate frontend`. The value is baked into
frontend bundles at build time.

Problem: frontend still calls `http://localhost:8000/api/v1/...` on a remote
server.

Cause: the frontend image was built with an old `VITE_API_BASE_URL`, or browser
cache is serving old JavaScript.

Fix:

- Set the correct `VITE_API_BASE_URL` in `.env`.
- Run:

```bash
docker compose build --no-cache frontend
docker compose up -d --force-recreate frontend
```

- Hard refresh the browser or test in an incognito window.
- If needed, verify the baked value by grepping frontend files inside the
  container:

```bash
docker compose exec frontend sh -lc 'grep -R "localhost:8000" -n /app 2>/dev/null | head'
```

Problem: customers/products return 403.

Cause: the authenticated token may not have an active or authorized business
selected. Do not describe every 403 as a backend bug.

Fix:

- Logout and login again.
- Select a business from the sidebar.
- Or test the flow in Swagger:
  `GET /api/v1/businesses`,
  `POST /api/v1/businesses/select`,
  `GET /api/v1/products`.

Build fails due registry or network access:

Confirm the server can reach required registries. If a proxy is required, supply
it from shell or ignored env only and rerun the targeted build.

Smoke fails on `/app`:

Check frontend logs, confirm the SSR container listens on `PORT=3000`, confirm
the host `FRONTEND_PORT` mapping, and verify reverse proxy routing if Nginx is
in use.

API upstream wrong port:

The API service listens on port `8000` in Compose. Nginx/reverse proxy upstreams
should target `api:8000`, not frontend or database ports.

Dirty repo prevents safe pull:

Stop and inspect the dirty files. Commit, stash, back up, or intentionally
discard them only after confirming they are not deployment secrets or emergency
server changes.

## Nginx + Let's Encrypt (dev.digiinvoice.ir, set up 2026-07-08)

The test server (reachable via `$DIGI_TEST_SSH`; see § Connection Vars) runs nginx
1.24 (Ubuntu apt package) as a reverse proxy in front of the Compose stack, with a
Let's Encrypt cert via certbot's nginx plugin.

- Config: `/etc/nginx/sites-available/dev.digiinvoice.ir` (symlinked into
  `sites-enabled/`). Routes: `/health/` and `/api/` → `127.0.0.1:8000` (api),
  everything else → `127.0.0.1:3000` (frontend SSR). `client_max_body_size 16m`
  for future uploads (logo, etc.).
- Cert: `certbot --nginx -d dev.digiinvoice.ir --agree-tos --redirect`. Renews
  automatically via certbot's systemd timer; `certbot renew --dry-run` verified
  working. Certbot rewrites the site file in place (adds the 443 `server{}`
  block + the 80→443 redirect) — re-run `nginx -t` after any manual edit to
  that file, since certbot's markers are easy to disturb.
- `VITE_API_BASE_URL` and `BACKEND_CORS_ORIGINS` in `.env` must point at the
  final public HTTPS origin (`https://dev.digiinvoice.ir`), never the raw
  server IP — Altcha (captcha) requires a secure context and silently fails
  with "Secure context (HTTPS) required" over plain `http://ip:port`.
  `VITE_API_BASE_URL` is baked in at frontend **build** time — changing it
  requires `docker compose build --no-cache frontend`, a restart alone does
  nothing.
- No HSTS header is set yet (optional hardening, deferred — hard to safely
  reverse once browsers cache it, so it wasn't added without an explicit
  decision to keep it permanently).

### docker compose v1.29.2 `KeyError: 'ContainerConfig'` on recreate

This server's `docker compose` is v1.29.2 (via apt/pip), which has a known
incompatibility with newer Docker Engine image metadata: **any** `docker compose
up -d` that needs to *recreate* an existing container (image changed, or even
an unrelated `up` that touches a dependency) can throw
`KeyError: 'ContainerConfig'` inside `get_container_data_volumes` and abort,
potentially mid-way through recreating multiple services.

- It fails in the **recreate** path specifically — inspecting the *old*
  container's image config to merge volumes. A **fresh create** (no old
  container by that name) does not hit this code path.
- Symptom seen live: `docker compose up -d api frontend` (even with
  `--no-deps`) tried to recreate `postgres` too, hit the bug, and left the old
  postgres container *renamed* (e.g. `f5d2cdb3d5a2_digi-tax-postgres`) and
  stopped rather than removed — Compose's rename-out-of-the-way step ran
  before the failing create step. Data was intact throughout (named volume
  `digi-tax-ops_postgres_data`, independent of container identity); the
  container's compose-assigned network alias (`postgres`) survives a rename,
  so restarting the exact same (renamed) container with `docker start
  <name>` restores service with zero data risk and zero reconfiguration.
- **Safe recovery pattern**, in order of preference:
  1. If the affected container is stateful (postgres/redis) and only
     stopped/renamed (not removed): `docker start <renamed-name>` — do
     **not** let compose try to recreate it again until this is fixed
     properly (upgrade compose, or migrate to the `docker compose` v2 plugin).
  2. If the affected container is stateless (api/frontend, no volumes):
     `docker stop <name> && docker rm <name>`, then `docker compose up -d
     --no-deps <service>` — a **fresh create** succeeds because there's no old
     container to inspect.
  3. Never `docker compose down` as a "fix" for this — it removes containers
     network-wide in one step and increases blast radius for no benefit.
- Root-cause fix (not yet done, flagged for a future session): upgrade to the
  `docker compose` v2 plugin (`docker compose-plugin` apt package, invoked as
  `docker compose ...` not `docker compose ...`), which doesn't have this bug.
  Until then, expect this failure mode on *any* server-side rebuild that
  touches a long-running container and follow the recovery pattern above.

### Known residual items on this server (as of 2026-07-08, not yet resolved)

- **`SECRET_KEY` is unset in `.env`**, so the API falls back to the
  hardcoded placeholder in `app/core/config.py`
  (`"your-secret-key-here"`) — a value visible in the public repo. This means
  JWTs on this server are forgeable by anyone who reads the source. Needs an
  explicit decision before rotating (rotating invalidates all current
  sessions for every user on the server).
- **Orphan `digi_tax` (underscore) database** exists alongside the canonical
  `digitax` — confirmed empty (0 rows), a dead leftover from early setup, not
  a data risk, but exactly the "two-database disaster" pattern the workspace
  `CLAUDE.md` documents. `preflight.sh` was evidently never run against this
  server. Left untouched pending explicit confirmation to drop it.
- **`digi-tax-postgres` container runs under a temporary renamed identity**
  (see the compose bug above) instead of its compose `container_name`. Fully
  functional (network alias `postgres` still resolves), but the next person
  running `docker compose ps`/`docker ps` should not be alarmed by the odd
  name. Fixing this cosmetically requires another risky recreate of the live
  DB container — deferred until the compose v1→v2 upgrade above is done.
- **Frontend never surfaces `must_change_password`** on the user's *own*
  login (only the admin panel's user-management view reads that field, for
  managing *other* users). A seed/admin-created account with
  `must_change_password: true` logs straight into the app with no forced
  change prompt. This is a pre-existing frontend gap, not specific to this
  server.
- **D4 (split-scope settings: «حساب من» / «تنظیمات کسب‌وکار») is not deployed
  to this server** — those commits exist only on the founder's laptop
  (`digi-tax-backend` `1963a4f`/`7ea52cd`, `digi-tax-frontend` `4d362bb`/
  `d4b4eaa`) and were never pushed to `origin/main` nor pulled here. `/app/
  settings` on this server still shows the pre-D4 fake-save stub (only the
  display-currency card is real; everything else is an honest non-persisting
  preview). Push + pull + rebuild is a separate follow-up.
