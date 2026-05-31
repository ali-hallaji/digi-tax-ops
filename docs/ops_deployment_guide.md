# Ops Deployment Guide v1.3

## Local workspace layout

```txt
~/work/digitax/
  digi-tax-backend/
  digi-tax-frontend/
  digi-tax-ops/
```

Run Docker Compose from `digi-tax-ops`.

For staging/server deployment steps, use
[`docs/server_deploy_runbook.md`](server_deploy_runbook.md).

## Initial files
Create:
```txt
docker-compose.yml
.env.example
nginx/nginx.conf
README.md
docs/progress.md
```

## Service names
Use stable service names:
```txt
postgres
redis
api
worker-submission
worker-inquiry
worker-default
scheduler
frontend
nginx
```

## Build paths
```yaml
api:
  build: ../digi-tax-backend
frontend:
  build: ../digi-tax-frontend
```

## Initial ports
```txt
api: 8000 internal
frontend: 3000 SSR Node container
postgres: 5432 local optional
redis: 6379 local optional
nginx: 80/443 later
```

## Frontend SSR container

The canonical frontend image is built from `../digi-tax-frontend` and runs its
production SSR Node server with `node server.mjs`. It is not a Vite dev server
and is not served as static files from an Nginx image.

`VITE_API_BASE_URL` is build-time public frontend configuration. Prefer `/api/v1`
when traffic goes through the ops Nginx reverse proxy. For local or staging
direct access, provide the environment-specific public API URL from ignored env
configuration and rebuild the frontend image.

Runtime-only frontend secrets, such as `LOVABLE_API_KEY` if needed, stay in
runtime environment configuration and must not be passed as Docker build args.

## Phase 0 acceptance
- `docker compose config` passes.
- postgres and redis start.
- api service can be referenced even if backend skeleton is not built yet.
- no production secrets.
- no Kubernetes.
