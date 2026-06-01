# Server Deploy Runbook

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

## Pre-Deploy Safety Checks

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

docker-compose config

docker-compose build api
docker-compose up -d postgres redis api
docker-compose exec api python -m alembic upgrade head

docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend

bash scripts/preflight.sh
bash scripts/smoke_test.sh
```

Backend-only update:

```bash
docker-compose build api
docker-compose up -d api
docker-compose exec api python -m alembic upgrade head
```

Use this when backend source, backend dependencies, backend Dockerfile inputs,
or migrations changed.

Frontend-only update:

```bash
docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend
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
- runtime-only secrets such as `LOVABLE_API_KEY`, if required

`VITE_API_BASE_URL` is build-time frontend configuration baked into the SSR
frontend bundle. Changing it requires rebuilding the `frontend` image. For
same-origin deployments behind the ops reverse proxy, `/api/v1` is usually the
right value. For direct-access staging, set the environment-specific public API
base URL in the server's ignored `.env`.

Restarting the existing `frontend` container is not enough after frontend source
changes or frontend build-time env changes.

Runtime-only secrets, including `LOVABLE_API_KEY`, must remain runtime
environment values. Do not pass them as Docker build args.

## Compose Config Validation

Validate Compose before building or restarting services:

```bash
cd ../digi-tax-ops
docker-compose config
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
docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend
```

Build API/backend only:

```bash
docker-compose build api
```

Build API and frontend:

```bash
docker-compose build api frontend
```

Recreate changed services after a targeted build:

```bash
docker-compose up -d --no-deps --force-recreate <service-name>
```

Start or refresh the default app services:

```bash
docker-compose up -d postgres redis api frontend
```

If worker services are added to this Compose project later, rebuild and recreate
only the changed worker services when backend worker code or worker image inputs
change.

## Bootstrap And Migrations

Run the migration after backend changes, migration changes, first server setup,
or when the database may not have the expected schema:

```bash
docker-compose exec api python -m alembic upgrade head
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
docker-compose up -d postgres redis
docker-compose up -d api
docker-compose up -d frontend
```

If an Nginx/reverse proxy service is present in the Compose project, start or
recreate it after API and frontend are healthy:

```bash
docker-compose up -d nginx
```

Do not force a backend rebuild unless backend code, backend dependencies,
Dockerfile inputs, migrations, or related service configuration changed.

## Validation After Deploy

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

Run `docker-compose ps`, start `postgres`, then rerun `bash scripts/preflight.sh`.

Frontend still on old image:

Run `docker-compose build --no-cache frontend`, then run
`docker-compose up -d --force-recreate frontend`. Recheck `/login`, `/app`, and
a deep route.

`VITE_API_BASE_URL` changed but frontend was not rebuilt:

Run `docker-compose build --no-cache frontend`, then run
`docker-compose up -d --force-recreate frontend`. The value is baked into
frontend bundles at build time.

Problem: frontend still calls `http://localhost:8000/api/v1/...` on a remote
server.

Cause: the frontend image was built with an old `VITE_API_BASE_URL`, or browser
cache is serving old JavaScript.

Fix:

- Set the correct `VITE_API_BASE_URL` in `.env`.
- Run:

```bash
docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend
```

- Hard refresh the browser or test in an incognito window.
- If needed, verify the baked value by grepping frontend files inside the
  container:

```bash
docker-compose exec frontend sh -lc 'grep -R "localhost:8000" -n /app 2>/dev/null | head'
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
