#!/usr/bin/env bash
# SEED-12 — the founder's one-command verification-world reset (LOCAL).
#
#   Full wipe (drop schema → alembic head) → seed the persona world →
#   regenerate persona_logins.md + persona_fixtures.json + README → print the table.
#
# Run from anywhere; it cd's to the digi-tax-ops root. Requires the local compose
# stack to be up (postgres + api). Deterministic + idempotent (wipes first).
#
# DATA-LOSS GUARD (added after a reseed destroyed a founder's real Moadian key):
#   • A pg_dump snapshot is ALWAYS taken before the wipe — the path is printed.
#   • The seed NEVER stores a Moadian private key, so ANY moadian_tenant_profiles
#     row with an encrypted_private_key_blob is REAL, runtime-created key material
#     the seed cannot recreate. If any exist, reset-world REFUSES to wipe and lists
#     them; pass --force to proceed anyway (the snapshot is then your only recovery).
#
# DEV/STAGING: the "Reset the verification world" step in docs/server_deploy_runbook.md
# wraps this; it points RESET_WORLD_SNAPSHOT_DIR at /root and passes --force only on
# a disposable DB with no real keys.
set -euo pipefail

cd "$(dirname "$0")/.."  # digi-tax-ops root

FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    *) echo "unknown argument: $arg (only --force is accepted)" >&2; exit 2 ;;
  esac
done

echo "▶ reset-world: preparing to wipe and reseed the persona verification world…"

# 0. Data-loss guard — real Moadian keys the seed cannot recreate.
#    On a fresh/unmigrated DB the table is absent → the query fails → count 0 → proceed.
KEY_COUNT=$(docker compose exec -T postgres psql -U digitax -d digitax -tAc \
  "SELECT count(*) FROM moadian_tenant_profiles WHERE encrypted_private_key_blob IS NOT NULL;" \
  2>/dev/null | tr -d '[:space:]')
KEY_COUNT=${KEY_COUNT:-0}

if [ "$KEY_COUNT" -gt 0 ]; then
  echo
  echo "╔══════════════════════════════════════════════════════════════════════╗"
  echo "║  ⛔  STOP — this reseed will DESTROY real Moadian private keys.        ║"
  echo "╚══════════════════════════════════════════════════════════════════════╝"
  echo "The seed never stores a key, so these $KEY_COUNT profile(s) hold REAL, encrypted"
  echo "private keys that a wipe deletes permanently (the seed cannot recreate them):"
  echo
  docker compose exec -T postgres psql -U digitax -d digitax -P pager=off -c \
    "SELECT t.name AS business,
            (SELECT u.mobile FROM tenant_members m JOIN users u ON u.id = m.user_id
             WHERE m.tenant_id = p.tenant_id AND m.role = 'owner' LIMIT 1) AS owner_mobile,
            p.fiscal_memory_id,
            length(p.encrypted_private_key_blob) AS key_bytes
     FROM moadian_tenant_profiles p JOIN tenants t ON t.id = p.tenant_id
     WHERE p.encrypted_private_key_blob IS NOT NULL
     ORDER BY t.name;"
  echo
  if [ "$FORCE" -ne 1 ]; then
    echo "reset-world will NOT proceed. To KEEP a key, re-import its PEM via the"
    echo "cockpit before reseeding, or restore it later from the snapshot below."
    echo "If you are sure, re-run with:  bash scripts/reset_world.sh --force"
    exit 1
  fi
  echo "⚠  --force given: proceeding despite real keys — the pre-wipe snapshot is your"
  echo "   ONLY recovery path."
fi

# 1. Snapshot BEFORE wiping (always) — recoverable even under --force.
SNAP_DIR="${RESET_WORLD_SNAPSHOT_DIR:-./.reseed-snapshots}"
mkdir -p "$SNAP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
SNAP_PATH="$SNAP_DIR/digitax-pre-reseed-$STAMP.sql.gz"
echo "▶ snapshotting current DB before wipe…"
docker compose exec -T postgres pg_dump -U digitax digitax | gzip > "$SNAP_PATH"
SNAP_ABS="$(cd "$(dirname "$SNAP_PATH")" && pwd)/$(basename "$SNAP_PATH")"
echo "  ✓ snapshot: $SNAP_ABS  ($(du -h "$SNAP_PATH" | cut -f1))"

echo "▶ wiping schema and reseeding…"

# 2. Full wipe → migrate to head.
docker compose exec -T postgres psql -U digitax -d digitax \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec -T api alembic upgrade head

# 3. Seed the canonical world.
docker compose exec -T api python -m app.cli.seed_realistic_world

# 4. Regenerate the single-source persona artifacts (docs read by humans + harness).
docker compose exec -T api python -m app.cli.world_fixtures > docs/persona_fixtures.json
docker compose exec -T api python -m app.cli.world_fixtures --markdown > docs/persona_logins.md
# Refresh the README «🔑 ورود به دنیای دمو» login table in place (mount the repo so
# the container can rewrite README.md between its PERSONA-LOGINS markers).
docker compose run --rm -v "$(pwd)":/ops -T api \
    python -m app.cli.world_fixtures --readme /ops/README.md || \
    echo "  (README refresh skipped — run world_fixtures --readme README.md manually)"

# 5. Print the login table.
echo
echo "════════════════════════════════════════════════════════════════════════"
cat docs/persona_logins.md
echo "════════════════════════════════════════════════════════════════════════"
echo "✓ reset-world complete — login guide: digi-tax-ops/docs/persona_logins.md"
echo "  pre-wipe snapshot: $SNAP_ABS"
