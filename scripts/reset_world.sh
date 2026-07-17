#!/usr/bin/env bash
# SEED — the founder's one-command verification-world reset (LOCAL).
#
#   Full wipe (drop schema → alembic head) → seed the persona world →
#   regenerate persona_logins.md + persona_fixtures.json + README → print the table.
#
# Run from anywhere; it cd's to the digi-tax-ops root. Requires the local compose
# stack to be up (postgres + api). Deterministic (wipes first — the seed is NOT
# idempotent; it assumes a clean schema).
#
# MOADIAN KEY SAFETY (the seed NEVER stores a key, so ANY encrypted_private_key_blob
# is REAL, runtime-created merchant material a wipe would destroy):
#   • A pg_dump snapshot is ALWAYS taken before the wipe — the path is printed.
#   • دیباتک (09120000000), the founder's PROTECTED tenant, is special: its key is
#     CAPTURED before the wipe and RESTORED onto the freshly-seeded tenant afterward,
#     so the founder's registered key survives every reseed with NO --force. (True
#     full-subgraph "untouched" preservation isn't possible — the DROP is mandatory
#     because the seed isn't idempotent — so we preserve the irreplaceable KEY and
#     re-seed the deterministic test data.)
#   • A real key on ANY OTHER tenant BLOCKS the wipe (lists them); --force overrides
#     and wipes EVERYTHING, including دیباتک's key (a deliberate clean-slate escape).
#
# DEV/STAGING: the "Reset the verification world" step in docs/server_deploy_runbook.md
# wraps this; it points RESET_WORLD_SNAPSHOT_DIR at /root.
set -euo pipefail

cd "$(dirname "$0")/.."  # digi-tax-ops root

FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    *) echo "unknown argument: $arg (only --force is accepted)" >&2; exit 2 ;;
  esac
done

DIBATAK_OWNER="09120000000"
PSQL() { docker compose exec -T postgres psql -U digitax -d digitax "$@"; }

echo "▶ reset-world: preparing to wipe and reseed the persona verification world…"

# 0. Classify real Moadian keys. On a fresh/unmigrated DB the tables are absent → the
#    queries fail → counts default to 0 → proceed. دیباتک's key is preserved; a key on
#    any other tenant blocks the wipe unless --force.
_owned_key_count() {  # $1 = "=" (دیباتک) or "<>" (others)
  PSQL -tAc "
    SELECT count(*) FROM moadian_tenant_profiles p
    WHERE p.encrypted_private_key_blob IS NOT NULL
      AND EXISTS (SELECT 1 FROM tenant_members m JOIN users u ON u.id = m.user_id
                  WHERE m.tenant_id = p.tenant_id AND m.role = 'owner'
                    AND u.mobile $1 '$DIBATAK_OWNER');" 2>/dev/null | tr -d '[:space:]'
}
DIBATAK_KEYS=$(_owned_key_count "=");  DIBATAK_KEYS=${DIBATAK_KEYS:-0}
OTHER_KEYS=$(_owned_key_count "<>");   OTHER_KEYS=${OTHER_KEYS:-0}

# Guard: a real key on a NON-protected tenant blocks the wipe unless --force.
if [ "$OTHER_KEYS" -gt 0 ] && [ "$FORCE" -ne 1 ]; then
  echo
  echo "╔══════════════════════════════════════════════════════════════════════╗"
  echo "║  ⛔  STOP — this reseed will DESTROY real Moadian keys.                ║"
  echo "╚══════════════════════════════════════════════════════════════════════╝"
  echo "These $OTHER_KEYS profile(s) hold a REAL key on a NON-protected tenant (only"
  echo "دیباتک is auto-preserved). A wipe deletes them permanently:"
  echo
  PSQL -P pager=off -c \
    "SELECT t.name AS business,
            (SELECT u.mobile FROM tenant_members m JOIN users u ON u.id = m.user_id
             WHERE m.tenant_id = p.tenant_id AND m.role = 'owner' LIMIT 1) AS owner_mobile,
            length(p.encrypted_private_key_blob) AS key_bytes
     FROM moadian_tenant_profiles p JOIN tenants t ON t.id = p.tenant_id
     WHERE p.encrypted_private_key_blob IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM tenant_members m JOIN users u ON u.id = m.user_id
                       WHERE m.tenant_id = p.tenant_id AND m.role = 'owner'
                         AND u.mobile = '$DIBATAK_OWNER')
     ORDER BY t.name;"
  echo
  echo "reset-world will NOT proceed. Re-import the key(s) elsewhere first, or restore"
  echo "later from the snapshot. If you are sure, re-run with:  bash scripts/reset_world.sh --force"
  echo "(--force wipes EVERYTHING, including دیباتک's key.)"
  exit 1
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

# 2. Protected-tenant CAPTURE — stash دیباتک's Moadian key material in a holding schema
#    that DROP SCHEMA public does not touch. Skipped under --force (clean-slate wipe).
PROTECTED=0
if [ "$DIBATAK_KEYS" -gt 0 ] && [ "$FORCE" -ne 1 ]; then
  PROTECTED=1
  echo "🔒 دیباتک has a real Moadian key — capturing it to preserve across the reseed…"
  PSQL -c "
    DROP SCHEMA IF EXISTS preserve CASCADE;
    CREATE SCHEMA preserve;
    CREATE TABLE preserve.dibatak_moadian AS
      SELECT p.status, p.fiscal_memory_id, p.seller_economic_id, p.seller_national_id,
             p.public_key_pem, p.public_key_fingerprint, p.private_key_storage_mode,
             p.encrypted_private_key_blob, p.private_key_uploaded_at,
             p.signing_cert_der_b64, p.cert_subject_cn, p.cert_not_after
      FROM moadian_tenant_profiles p
      WHERE p.encrypted_private_key_blob IS NOT NULL
        AND EXISTS (SELECT 1 FROM tenant_members m JOIN users u ON u.id = m.user_id
                    WHERE m.tenant_id = p.tenant_id AND m.role = 'owner'
                      AND u.mobile = '$DIBATAK_OWNER');" >/dev/null
fi

echo "▶ wiping schema and reseeding…"

# 3. Full wipe → migrate → seed.
PSQL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec -T api alembic upgrade head
docker compose exec -T api python -m app.cli.seed_realistic_world

# 4. Protected-tenant RESTORE — re-attach the preserved key onto the freshly-seeded دیباتک.
if [ "$PROTECTED" -eq 1 ]; then
  echo "🔒 restoring دیباتک's preserved Moadian key…"
  PSQL -c "
    WITH d AS (
      SELECT m.tenant_id AS tid FROM tenant_members m JOIN users u ON u.id = m.user_id
      WHERE u.mobile = '$DIBATAK_OWNER' AND m.role = 'owner' LIMIT 1)
    DELETE FROM moadian_tenant_profiles WHERE tenant_id = (SELECT tid FROM d);
    INSERT INTO moadian_tenant_profiles
      (id, tenant_id, status, fiscal_memory_id, seller_economic_id, seller_national_id,
       public_key_pem, public_key_fingerprint, private_key_storage_mode,
       encrypted_private_key_blob, private_key_uploaded_at, signing_cert_der_b64,
       cert_subject_cn, cert_not_after, created_at, updated_at)
    SELECT gen_random_uuid(),
           (SELECT m.tenant_id FROM tenant_members m JOIN users u ON u.id = m.user_id
            WHERE u.mobile = '$DIBATAK_OWNER' AND m.role = 'owner' LIMIT 1),
           h.status, h.fiscal_memory_id, h.seller_economic_id, h.seller_national_id,
           h.public_key_pem, h.public_key_fingerprint, h.private_key_storage_mode,
           h.encrypted_private_key_blob, h.private_key_uploaded_at, h.signing_cert_der_b64,
           h.cert_subject_cn, h.cert_not_after, now(), now()
    FROM preserve.dibatak_moadian h;
    DROP SCHEMA preserve CASCADE;" >/dev/null
  echo "  🔒 دیباتک Moadian key PRESERVED across the reseed."
fi

# 5. Regenerate the single-source persona artifacts (docs read by humans + harness).
docker compose exec -T api python -m app.cli.world_fixtures > docs/persona_fixtures.json
docker compose exec -T api python -m app.cli.world_fixtures --markdown > docs/persona_logins.md
# Refresh the README «🔑 ورود به دنیای دمو» login table in place (mount the repo so
# the container can rewrite README.md between its PERSONA-LOGINS markers).
docker compose run --rm -v "$(pwd)":/ops -T api \
    python -m app.cli.world_fixtures --readme /ops/README.md || \
    echo "  (README refresh skipped — run world_fixtures --readme README.md manually)"

# 6. Print the login table.
echo
echo "════════════════════════════════════════════════════════════════════════"
cat docs/persona_logins.md
echo "════════════════════════════════════════════════════════════════════════"
echo "✓ reset-world complete — login guide: digi-tax-ops/docs/persona_logins.md"
echo "  pre-wipe snapshot: $SNAP_ABS"
[ "$PROTECTED" -eq 1 ] && echo "  🔒 دیباتک Moadian key was preserved across the reseed."
