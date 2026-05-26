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

  container_id="$(docker-compose ps -q "$service" 2>/dev/null)"
  [ -n "$container_id" ] || return 1
  [ "$(docker inspect -f '{{.State.Running}}' "$container_id" 2>/dev/null)" = "true" ]
}

require_command docker-compose
require_command docker

if docker-compose config >/dev/null 2>&1; then
  pass "docker-compose config is valid"
else
  fail "docker-compose config is invalid"
fi

SERVICES="$(docker-compose config --services)"

for service in postgres redis api; do
  if service_exists "$service"; then
    pass "Compose service '$service' exists"
  else
    fail "Compose service '$service' is missing"
  fi
done

if service_exists frontend; then
  pass "Compose service 'frontend' exists"
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

if docker-compose exec -T postgres env PGPASSWORD="$POSTGRES_PASSWORD" \
  pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; then
  pass "Postgres responds to pg_isready"
else
  fail "Postgres did not respond to pg_isready"
fi

if container_running api; then
  pass "API container is running"
else
  fail "API container is not running"
fi

if docker-compose exec -T api sh -lc 'test -n "${DATABASE_URL:-}"' >/dev/null 2>&1; then
  pass "API container can see DATABASE_URL"
else
  fail "API container cannot see DATABASE_URL"
fi

