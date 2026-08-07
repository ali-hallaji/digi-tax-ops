#!/usr/bin/env bash
# Production bring-up, executable (PRE-PRODUCTION rehearsal deliverable).
#
# The runbook's checklist was prose; rehearsing it end-to-end turned up SEVEN
# places where a human would have had to improvise on migration morning — a
# missing create_admin CLI, an import command whose CSV path was undocumented
# (and wrong in the module docstring), an unexported BACKEND_SHA, hardcoded
# container names / ports / env_file, and an admin-before-backfill ordering
# dependency that only a second CLEAN run exposes. This script is that checklist
# with every gap closed, so migration morning is fill-and-go.
#
#   ADMIN_MOBILE=09xxxxxxxxx ADMIN_FIRST_NAME=… ADMIN_LAST_NAME=… \
#   ADMIN_PASSWORD='…' STACK_ENV_FILE=.env bash scripts/prod_bring_up.sh
#
#   PROJECT=digitax-rehearsal STACK_ENV_FILE=.env.rehearsal bash scripts/prod_bring_up.sh
#
# Idempotent: safe to re-run against a stack that is already partly up.
# It never seeds the demo/persona world — production has no personas.
set -euo pipefail

cd "$(dirname "$0")/.."

ENV_FILE="${STACK_ENV_FILE:-.env}"
PROJECT="${PROJECT:-}"

if [ ! -f "$ENV_FILE" ]; then
  echo "✗ env file «$ENV_FILE» not found. Start from env.production.template:" >&2
  echo "    cp env.production.template .env && chmod 600 .env" >&2
  exit 1
fi

if grep -q 'CHANGE-ME' "$ENV_FILE"; then
  echo "✗ «$ENV_FILE» still contains CHANGE-ME placeholders:" >&2
  grep -n 'CHANGE-ME' "$ENV_FILE" | sed 's/^/    /' >&2
  exit 1
fi

DC=(docker compose)
[ -n "$PROJECT" ] && DC+=(-p "$PROJECT")
DC+=(--env-file "$ENV_FILE")

# The SHAs are BUILD ARGS. They must be exported in the SAME shell as the build
# or the images bake «unknown» and deploy-verification by SHA becomes impossible
# — for the API as much as the frontend. (The runbook named only FRONTEND_SHA;
# the rehearsal's prod smoke caught the missing BACKEND_SHA.)
export BACKEND_SHA="$(git -C ../digi-tax-backend rev-parse HEAD 2>/dev/null || echo unknown)"
export FRONTEND_SHA="$(git -C ../digi-tax-frontend rev-parse HEAD 2>/dev/null || echo unknown)"
echo "▶ BACKEND_SHA=$BACKEND_SHA"
echo "▶ FRONTEND_SHA=$FRONTEND_SHA"

echo
echo "── 1. validate compose ─────────────────────────────────────────"
"${DC[@]}" config -q
echo "  ✓ compose config valid"

echo
echo "── 2. data layer ───────────────────────────────────────────────"
"${DC[@]}" up -d postgres redis
for i in $(seq 1 30); do
  up=$("${DC[@]}" ps --format '{{.Status}}' postgres 2>/dev/null | grep -c healthy || true)
  [ "$up" -ge 1 ] && break
  sleep 3
done
"${DC[@]}" ps --format '  {{.Name}}  {{.Status}}' postgres redis

echo
echo "── 3. api image + migrations ───────────────────────────────────"
"${DC[@]}" build api
"${DC[@]}" up -d api
for i in $(seq 1 30); do
  up=$("${DC[@]}" ps --format '{{.Status}}' api 2>/dev/null | grep -c healthy || true)
  [ "$up" -ge 1 ] && break
  sleep 3
done
"${DC[@]}" exec -T api python -m alembic upgrade head

# gotcha 3: `alembic current` is NOT proof the tables exist. Count them.
DB_USER="$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | cut -d= -f2-)"
DB_NAME="$(grep -E '^POSTGRES_DB=' "$ENV_FILE" | cut -d= -f2-)"
tables=$("${DC[@]}" exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT count(*) FROM pg_tables WHERE schemaname='public';")
echo "  ✓ psql sees ${tables} tables in ${DB_NAME}"
[ "$tables" -lt 40 ] && { echo "  ✗ far too few tables — migration did not land" >&2; exit 1; }

echo
echo "── 4. reference data (production has NO personas) ──────────────"
"${DC[@]}" exec -T api python -m app.cli.import_tax_units \
  data/moadian/rc_umgs_st_v1_18_units.csv
units=$("${DC[@]}" exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT count(*) FROM tax_units;")
echo "  ✓ tax_units: ${units}"

echo
echo "── 5. first system-admin ───────────────────────────────────────"
# ORDERING IS LOAD-BEARING — found by the rehearsal's SECOND clean run.
# `seed_commission_world` attributes its settings row to a system admin and
# aborts with «no system admin found» on a virgin database. The first rehearsal
# run only survived because an admin had been created by hand beforehand; the
# runbook's prose order hid the dependency. Admin BEFORE backfills, always.
admins=$("${DC[@]}" exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT count(*) FROM users WHERE is_system_admin;")
if [ "${admins:-0}" -gt 0 ]; then
  echo "  ✓ a system admin already exists (${admins}) — leaving it alone"
else
  : "${ADMIN_MOBILE:?set ADMIN_MOBILE (09xxxxxxxxx) — the first system admin}"
  : "${ADMIN_FIRST_NAME:?set ADMIN_FIRST_NAME}"
  : "${ADMIN_LAST_NAME:?set ADMIN_LAST_NAME}"
  : "${ADMIN_PASSWORD:?set ADMIN_PASSWORD (>=10 chars; forced to change at first login)}"
  "${DC[@]}" exec -T -e ADMIN_PASSWORD api python -m app.cli.create_admin \
    --mobile "$ADMIN_MOBILE" \
    --first-name "$ADMIN_FIRST_NAME" \
    --last-name "$ADMIN_LAST_NAME"
fi

echo
echo "── 6. one-time backfills ───────────────────────────────────────"
# No-op on a fresh DB; required the moment referred revenue predates the engine.
"${DC[@]}" exec -T api python -m app.cli.seed_commission_world

echo
echo "── 7. frontend ─────────────────────────────────────────────────"
"${DC[@]}" build frontend
"${DC[@]}" up -d frontend

echo
echo "── 8. state ────────────────────────────────────────────────────"
"${DC[@]}" ps --format '  {{.Name}}  {{.Status}}'

cat <<EOF

✓ bring-up complete.

NEXT — not done by this script, deliberately:
  1. bash scripts/prod_smoke.sh          (API=… WEB=… for a non-default stack)
  2. pnpm harness --base-url <prod> tests/e2e-harness/specs/11-landing.spec.ts
  3. ONE manual founder login with a real OTP — the only proof that auth,
     SMS delivery and the session actually work end-to-end. Not automatable
     on a DEBUG=false stack; see scripts/prod_smoke.sh header.
  4. Install the nightly backup timer (docs/server_deploy_runbook.md).
  5. The admin created above must change its bootstrap password at first login.
EOF

# ── Disk hygiene ────────────────────────────────────────────────────────────
# A --no-cache build leaves the previous image dangling. Repeated deploys filled
# a 38G dev disk to 100% and put postgres into a checkpoint crash-loop
# (runbook § فضای دیسک). Volumes are never touched — only unused images older
# than 6h, which can no longer be anything this deploy needs.
echo "→ pruning unused images (volumes untouched)"
docker image prune -af --filter 'until=6h' >/dev/null 2>&1 || true
df -h / | tail -1
