#!/usr/bin/env bash
# One-shot Moadian credential migration: LOCAL stack → DEV server.
#
# Decrypts the source tenant's private key INSIDE the local api container
# (source key), streams the bundle through an SSH pipe straight into the dev
# api container's stdin, where it is re-encrypted with the DEV key and
# upserted. The secret never touches a file on either side; helper scripts
# (which carry no secrets) are copied in and removed afterwards. The source
# database is strictly read-only.
#
# Usage (from digi-tax-ops, with $DIGI_TEST_SSH / $DIGI_TEST_PATH set):
#   bash scripts/migrate_moadian_creds.sh <src_tenant_id> <dst_tenant_id>
set -euo pipefail

SRC_TENANT="${1:?src_tenant_id required}"
DST_TENANT="${2:?dst_tenant_id required}"
: "${DIGI_TEST_SSH:?DIGI_TEST_SSH not set}"
: "${DIGI_TEST_PATH:?DIGI_TEST_PATH not set}"

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."

cleanup() {
  docker compose exec -T api rm -f /tmp/_mx.py 2>/dev/null || true
  # shellcheck disable=SC2086
  ssh $DIGI_TEST_SSH "cd $DIGI_TEST_PATH && docker compose exec -T api rm -f /tmp/_mi.py; rm -f /tmp/_mi.py" 2>/dev/null || true
}
trap cleanup EXIT

docker compose cp scripts/moadian_cred_export.py api:/tmp/_mx.py
# shellcheck disable=SC2086
ssh $DIGI_TEST_SSH "cat > /tmp/_mi.py" < scripts/moadian_cred_import.py
# shellcheck disable=SC2086
ssh $DIGI_TEST_SSH "cd $DIGI_TEST_PATH && docker compose cp /tmp/_mi.py api:/tmp/_mi.py && rm -f /tmp/_mi.py"

# The pipe: decrypt(source key) → ssh → re-encrypt(dev key) → upsert.
# shellcheck disable=SC2086
docker compose exec -T api python /tmp/_mx.py "$SRC_TENANT" \
  | ssh $DIGI_TEST_SSH "cd $DIGI_TEST_PATH && docker compose exec -T api python /tmp/_mi.py '$DST_TENANT'"

echo "migration pipe completed (see stderr lines above for both sides)"
