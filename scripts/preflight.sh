#!/usr/bin/env bash

set -u

pass() {
  printf 'PASS: %s\n' "$1"
}

info() {
  printf 'INFO: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

load_env() {
  if [ ! -f ".env" ]; then
    fail ".env is required for preflight checks"
  fi

  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
  pass "Loaded environment from .env"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

service_exists() {
  printf '%s\n' "$SERVICES" | grep -Fx "$1" >/dev/null 2>&1
}

extract_db_name() {
  local url="$1"
  local remainder db_name

  remainder="${url##*/}"
  db_name="${remainder%%\?*}"
  printf '%s\n' "$db_name"
}

container_running() {
  local service="$1"
  local container_id

  container_id="$(docker compose ps -q "$service" 2>/dev/null)"
  [ -n "$container_id" ] || return 1
  [ "$(docker inspect -f '{{.State.Running}}' "$container_id" 2>/dev/null)" = "true" ]
}

frontend_config() {
  printf '%s\n' "$COMPOSE_CONFIG" | awk '
    /^  frontend:/ { in_frontend=1; print; next }
    /^  [A-Za-z0-9_-]+:/ { in_frontend=0 }
    in_frontend { print }
  '
}

require_command docker
require_command docker

if COMPOSE_CONFIG="$(docker compose config 2>/dev/null)"; then
  pass "docker compose config is valid"
else
  fail "docker compose config is invalid"
fi

SERVICES="$(docker compose config --services)"

for service in postgres redis api; do
  if service_exists "$service"; then
    pass "Compose service '$service' exists"
  else
    fail "Compose service '$service' is missing"
  fi
done

if service_exists frontend; then
  pass "Compose service 'frontend' exists"

  FRONTEND_CONFIG="$(frontend_config)"

  if printf '%s\n' "$FRONTEND_CONFIG" | grep -E 'context: .*/digi-tax-frontend$|context: ../digi-tax-frontend$' >/dev/null 2>&1; then
    pass "Frontend build context points to ../digi-tax-frontend"
  else
    fail "Frontend build context does not point to ../digi-tax-frontend"
  fi

  if printf '%s\n' "$FRONTEND_CONFIG" | grep -Ei 'pnpm.*dev|vite[[:space:]]+dev|--port[[:space:]]+9000|target:[[:space:]]+9000' >/dev/null 2>&1; then
    fail "Frontend service still appears to use a Vite dev server or port 9000"
  else
    pass "Frontend service does not use a Vite dev server override"
  fi

  if printf '%s\n' "$FRONTEND_CONFIG" | grep -E 'target:[[:space:]]+3000' >/dev/null 2>&1; then
    pass "Frontend service publishes container port 3000"
  else
    fail "Frontend service does not publish container port 3000"
  fi

  if printf '%s\n' "$FRONTEND_CONFIG" | grep -E 'VITE_API_BASE_URL:' >/dev/null 2>&1; then
    pass "Frontend build config includes VITE_API_BASE_URL"
  else
    fail "Frontend build config is missing VITE_API_BASE_URL"
  fi
else
  info "Compose service 'frontend' is not defined"
fi

load_env

for var_name in POSTGRES_USER POSTGRES_DB POSTGRES_PASSWORD POSTGRES_HOST POSTGRES_PORT; do
  if [ -n "${!var_name:-}" ]; then
    pass ".env contains $var_name"
  else
    fail ".env is missing required variable $var_name"
  fi
done

if service_exists frontend; then
  if [ -n "${VITE_API_BASE_URL:-}" ]; then
    pass ".env contains VITE_API_BASE_URL for frontend builds"
  else
    fail ".env is missing VITE_API_BASE_URL for frontend builds"
  fi
fi

if [ -n "${DATABASE_URL:-}" ]; then
  database_url_db_name="$(extract_db_name "$DATABASE_URL")"
  if [ "$database_url_db_name" = "$POSTGRES_DB" ]; then
    pass "DATABASE_URL database name matches POSTGRES_DB"
  else
    fail "DATABASE_URL database name '$database_url_db_name' does not match POSTGRES_DB '$POSTGRES_DB'"
  fi
else
  info "DATABASE_URL is not set in .env; skipping DB-name consistency check"
fi

if container_running postgres; then
  pass "Postgres container is running"
else
  fail "Postgres container is not running"
fi

if docker compose exec -T postgres env PGPASSWORD="$POSTGRES_PASSWORD" \
  pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; then
  pass "Postgres responds to pg_isready"
else
  fail "Postgres did not respond to pg_isready"
fi

# Canonical DB is "digitax" (no underscore). Detect any lingering orphan — in
# particular "digi_tax" — that would indicate a prior misconfiguration survived.
# "${POSTGRES_DB}_test" is the sanctioned isolated pytest DB (BATCH 0.5), not an
# orphan: the backend test suite refuses to run against any non-*_test database.
orphan_dbs="$(docker compose exec -T postgres \
  env PGPASSWORD="$POSTGRES_PASSWORD" \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc \
  "SELECT datname FROM pg_database
   WHERE datname NOT IN ('postgres','template0','template1',
                         '$POSTGRES_DB','${POSTGRES_DB}_test');" 2>/dev/null)"
if [ -z "$orphan_dbs" ]; then
  pass "No orphan databases found (canonical DB is '$POSTGRES_DB')"
else
  fail "Orphan database(s) detected: $orphan_dbs — drop them before deploying (canonical DB is 'digitax')"
fi

if container_running api; then
  pass "API container is running"
else
  fail "API container is not running"
fi

if docker compose exec -T api sh -lc 'test -n "${DATABASE_URL:-}"' >/dev/null 2>&1; then
  pass "API container can see DATABASE_URL"
else
  fail "API container cannot see DATABASE_URL"
fi
