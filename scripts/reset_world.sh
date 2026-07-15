#!/usr/bin/env bash
# SEED-12 — the founder's one-command verification-world reset (LOCAL).
#
#   Full wipe (drop schema → alembic head) → seed the 12-persona world →
#   regenerate persona_logins.md + persona_fixtures.json → print the login table.
#
# Run from anywhere; it cd's to the digi-tax-ops root. Requires the local compose
# stack to be up (postgres + api). Deterministic + idempotent (wipes first).
#
# DEV/STAGING: do NOT run this blindly — use the "Reset the verification world"
# step in docs/server_deploy_runbook.md, which snapshots the DB FIRST, always.
set -euo pipefail

cd "$(dirname "$0")/.."  # digi-tax-ops root

echo "▶ reset-world: wiping schema and reseeding the 12-persona verification world…"

# 1. Full wipe → migrate to head.
docker compose exec -T postgres psql -U digitax -d digitax \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec -T api alembic upgrade head

# 2. Seed the canonical world.
docker compose exec -T api python -m app.cli.seed_realistic_world

# 3. Regenerate the single-source persona artifacts (docs read by humans + harness).
docker compose exec -T api python -m app.cli.world_fixtures > docs/persona_fixtures.json
docker compose exec -T api python -m app.cli.world_fixtures --markdown > docs/persona_logins.md

# 4. Print the login table.
echo
echo "════════════════════════════════════════════════════════════════════════"
cat docs/persona_logins.md
echo "════════════════════════════════════════════════════════════════════════"
echo "✓ reset-world complete — login guide: digi-tax-ops/docs/persona_logins.md"
