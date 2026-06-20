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
  if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
    info "Loaded environment from .env"
  else
    info ".env not found, using current shell environment and script defaults"
  fi
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

get_container_id() {
  docker-compose ps -q "$1" 2>/dev/null
}

assert_service_running() {
  local service="$1"
  local container_id

  container_id="$(get_container_id "$service")"
  [ -n "$container_id" ] || fail "Service '$service' has no container. Start the stack first."

  if [ "$(docker inspect -f '{{.State.Running}}' "$container_id" 2>/dev/null)" != "true" ]; then
    fail "Service '$service' container is not running."
  fi

  pass "Service '$service' container is running"
}

load_env
require_command docker-compose
require_command docker

POSTGRES_USER="${POSTGRES_USER:-digitax}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-digitax}"
POSTGRES_DB="${POSTGRES_DB:-digitax}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

assert_service_running postgres
assert_service_running api

if docker-compose exec -T postgres env PGPASSWORD="$POSTGRES_PASSWORD" \
  pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; then
  pass "PostgreSQL is accepting connections"
else
  fail "PostgreSQL is not ready for connections"
fi

db_exists="$(
  docker-compose exec -T postgres env PGPASSWORD="$POSTGRES_PASSWORD" \
    psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB';" 2>/dev/null | tr -d '[:space:]'
)"

if [ "$db_exists" = "1" ]; then
  pass "Database '$POSTGRES_DB' already exists"
else
  info "Database '$POSTGRES_DB' is missing, creating it now"
  docker-compose exec -T postgres env PGPASSWORD="$POSTGRES_PASSWORD" \
    createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB" \
    >/dev/null || fail "Failed to create database '$POSTGRES_DB'"
  pass "Database '$POSTGRES_DB' created"
fi

docker-compose exec -T api alembic upgrade head >/dev/null || fail "Alembic upgrade head failed inside api container"
pass "Alembic upgrade head completed successfully"

