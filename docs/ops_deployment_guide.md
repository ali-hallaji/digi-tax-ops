# Ops Deployment Guide v1.3

## Local workspace layout

```txt
~/work/digitax/
  digi-tax-backend/
  digi-tax-frontend/
  digi-tax-ops/
```

Run Docker Compose from `digi-tax-ops`.

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
frontend: 8080 or nginx-served static
postgres: 5432 local optional
redis: 6379 local optional
nginx: 80/443 later
```

## Phase 0 acceptance
- `docker compose config` passes.
- postgres and redis start.
- api service can be referenced even if backend skeleton is not built yet.
- no production secrets.
- no Kubernetes.
