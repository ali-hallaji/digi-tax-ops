#!/usr/bin/env bash
# Nightly PostgreSQL backup with rotation (FINISH-LINE Part 4).
#
# Writes a gzipped pg_dump into backups/ and prunes on a two-tier schedule:
#   daily   keep the last 7
#   weekly  keep the last 4 (a Friday dump is promoted to weekly)
#
# Deliberately dumb and dependency-free: pg_dump runs INSIDE the postgres
# container (no host psql needed) and the file lands on the host, so a lost
# container never takes the backups with it.
#
# Install as a systemd timer — see docs/server_deploy_runbook.md § Automated
# backups. Safe to run by hand at any time.
set -euo pipefail

# The host may run a Persian locale, which makes `date` emit JALALI digits — the
# filenames would then be unsortable against anything else and confusing to read
# next to a Gregorian log. Pin the C locale for every date in this script.
export LC_ALL=C

cd "$(dirname "$0")/.."

# Multi-stack aware (PRE-PROD rehearsal finding): a bare `docker compose exec`
# always targets the DEFAULT project + .env, so on a host running two stacks
# this script would happily dump the WRONG database under the right filename.
# PROJECT / STACK_ENV_FILE select the stack; defaults reproduce old behaviour.
DC=(docker compose)
[ -n "${PROJECT:-}" ] && DC+=(-p "$PROJECT")
[ -n "${STACK_ENV_FILE:-}" ] && DC+=(--env-file "$STACK_ENV_FILE")

BACKUP_DIR="${BACKUP_DIR:-backups}"
DB_USER="${POSTGRES_USER:-digitax}"
DB_NAME="${POSTGRES_DB:-digitax}"
KEEP_DAILY="${KEEP_DAILY:-7}"
KEEP_WEEKLY="${KEEP_WEEKLY:-4}"

mkdir -p "$BACKUP_DIR"

# Friday (date +%u = 5) dumps are the weekly ones — a different prefix is all
# the rotation logic needs, and it keeps the filenames self-explaining.
if [ "$(date +%u)" = "5" ]; then
  TIER="weekly"
else
  TIER="daily"
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${BACKUP_DIR}/digitax-${TIER}-${STAMP}.sql.gz"

echo "▶ dumping ${DB_NAME} → ${OUT}"
# Fail the whole pipeline if pg_dump fails rather than writing a truncated .gz.
set -o pipefail
"${DC[@]}" exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$OUT"

# A dump that is suspiciously small is a failed dump wearing a filename.
SIZE=$(stat -c%s "$OUT")
if [ "$SIZE" -lt 10000 ]; then
  echo "✗ dump is only ${SIZE} bytes — refusing to treat this as a backup" >&2
  mv "$OUT" "${OUT}.SUSPECT"
  exit 1
fi
echo "✓ ${OUT} ($(numfmt --to=iec "$SIZE" 2>/dev/null || echo "${SIZE}B"))"

prune() {
  local tier="$1" keep="$2"
  # shellcheck disable=SC2012 — filenames are ours and contain no newlines.
  local files
  files=$(ls -1t "${BACKUP_DIR}"/digitax-"${tier}"-*.sql.gz 2>/dev/null || true)
  local n=0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    n=$((n + 1))
    if [ "$n" -gt "$keep" ]; then
      echo "  · pruning $(basename "$f")"
      rm -f "$f"
    fi
  done <<< "$files"
}

prune daily "$KEEP_DAILY"
prune weekly "$KEEP_WEEKLY"

echo "▶ current backups:"
ls -1t "${BACKUP_DIR}"/digitax-*.sql.gz 2>/dev/null | head -20 | sed 's/^/  /'
