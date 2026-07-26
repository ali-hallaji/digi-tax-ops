#!/usr/bin/env bash
# Restore a backup into a SCRATCH database and report row counts (FINISH-LINE
# Part 4).
#
# A backup nobody has restored is a hope, not a backup. This restores into a
# throwaway database by default so the procedure can be REHEARSED on a live
# server without touching anything real.
#
#   bash scripts/restore_db.sh backups/digitax-daily-20260726_210000.sql.gz
#   bash scripts/restore_db.sh <dump> digitax_restore_check   # explicit target
#
# Restoring OVER the live database is deliberately NOT a flag on this script:
# that is a decision that deserves its own deliberate commands, documented in
# docs/server_deploy_runbook.md § Restore.
set -euo pipefail

cd "$(dirname "$0")/.."

# Multi-stack aware — see scripts/backup_db.sh.
DC=(docker compose)
[ -n "${PROJECT:-}" ] && DC+=(-p "$PROJECT")
[ -n "${STACK_ENV_FILE:-}" ] && DC+=(--env-file "$STACK_ENV_FILE")

DUMP="${1:?usage: restore_db.sh <dump.sql.gz> [target_db]}"
TARGET="${2:-digitax_restore_check}"
DB_USER="${POSTGRES_USER:-digitax}"

if [ ! -f "$DUMP" ]; then
  echo "✗ no such dump: $DUMP" >&2
  exit 1
fi

case "$TARGET" in
  digitax|postgres)
    echo "✗ refusing to restore over «$TARGET» — use a scratch name." >&2
    echo "  Restoring over live is a deliberate manual procedure (see runbook)." >&2
    exit 1
    ;;
esac

echo "▶ recreating scratch database «${TARGET}»"
"${DC[@]}" exec -T postgres psql -U "$DB_USER" -d postgres \
  -c "DROP DATABASE IF EXISTS ${TARGET};" >/dev/null
"${DC[@]}" exec -T postgres psql -U "$DB_USER" -d postgres \
  -c "CREATE DATABASE ${TARGET} OWNER ${DB_USER};" >/dev/null

echo "▶ restoring $(basename "$DUMP")…"
gunzip -c "$DUMP" | "${DC[@]}" exec -T postgres psql -U "$DB_USER" -d "$TARGET" \
  >/dev/null 2>/tmp/restore_err.log || {
    echo "✗ restore failed — last lines:" >&2
    tail -20 /tmp/restore_err.log >&2
    exit 1
  }

echo "▶ row counts in the restored copy:"
"${DC[@]}" exec -T postgres psql -U "$DB_USER" -d "$TARGET" -c "
SELECT 'tenants' AS table, count(*) FROM tenants
UNION ALL SELECT 'users', count(*) FROM users
UNION ALL SELECT 'customers', count(*) FROM customers
UNION ALL SELECT 'products', count(*) FROM products
UNION ALL SELECT 'invoice_drafts', count(*) FROM invoice_drafts
UNION ALL SELECT 'journal_entries', count(*) FROM journal_entries
UNION ALL SELECT 'partner_commission_accruals', count(*) FROM partner_commission_accruals
ORDER BY 1;"

echo
echo "✓ restore rehearsal OK. Drop the scratch copy when done:"
echo "  "${DC[@]}" exec -T postgres psql -U ${DB_USER} -d postgres -c 'DROP DATABASE ${TARGET};'"
