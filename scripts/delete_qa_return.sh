#!/usr/bin/env bash
# Delete ONE return document and its lines, with a full before/after audit.
#
# Written for the founder's decision to remove the single pre-VAT-fix QA artifact
# on dev: RET-2026-000006, a FULL return of a ۲,۴۰۰,۰۰۰ + ۱۰٪ purchase that was
# recorded with vat_amount = 0 because it predates the برگشت-از-خرید VAT fix
# (backend 04e5f28). Left in place it would keep overstating اعتبار in the VAT
# report and understating the vendor balance — a wrong number in a tax figure.
#
# Deliberately NOT a bulk cleanup and NOT idempotent-by-guessing: it takes ONE
# explicit id, refuses anything it does not recognise, prints the state before
# and after, and does the delete in a single transaction. A script that could
# delete "returns that look like QA" is a script that will one day delete a real
# document.
#
# Usage (from digi-tax-ops, against the LOCAL stack):
#   bash scripts/delete_qa_return.sh <return_id>
#   bash scripts/delete_qa_return.sh <return_id> --apply    # actually delete
#
# Against dev, run it THROUGH ssh so the id is never guessed remotely:
#   ssh $DIGI_TEST_SSH "cd \$DIGI_TEST_PATH && bash scripts/delete_qa_return.sh <id> --apply"
set -euo pipefail

RETURN_ID="${1:-}"
APPLY="${2:-}"

if [[ -z "$RETURN_ID" ]]; then
  echo "usage: $0 <return_id> [--apply]" >&2
  exit 2
fi
if ! [[ "$RETURN_ID" =~ ^[0-9a-fA-F-]{36}$ ]]; then
  echo "ERROR: '<return_id>' must be a UUID — refusing to run on a pattern." >&2
  exit 2
fi

PSQL=(docker compose exec -T postgres psql -U digitax -d digitax)

echo "═══ BEFORE ═══"
"${PSQL[@]}" -c "
SELECT r.document_number, r.direction, r.return_date,
       r.subtotal_amount, r.vat_amount, r.total_amount, r.refunded,
       t.name AS business, r.party_name
FROM return_documents r JOIN tenants t ON t.id = r.tenant_id
WHERE r.id = '${RETURN_ID}';"

FOUND=$("${PSQL[@]}" -tAc "SELECT count(*) FROM return_documents WHERE id='${RETURN_ID}';" | tr -d '[:space:]')
if [[ "$FOUND" != "1" ]]; then
  echo "ERROR: no return document with that id — nothing to do." >&2
  exit 1
fi

# A refunded return has a payment hanging off it; deleting one would orphan real
# money movement. Refuse rather than cascade into the treasury.
REFUNDED=$("${PSQL[@]}" -tAc "SELECT refunded FROM return_documents WHERE id='${RETURN_ID}';" | tr -d '[:space:]')
if [[ "$REFUNDED" == "t" ]]; then
  echo "ERROR: this return is marked refunded (a payment is attached)." >&2
  echo "       Deleting it would orphan a real money movement. Aborting." >&2
  exit 1
fi

TENANT=$("${PSQL[@]}" -tAc "SELECT tenant_id FROM return_documents WHERE id='${RETURN_ID}';" | tr -d '[:space:]')

echo
echo "── lines ──"
"${PSQL[@]}" -c "
SELECT title, returned_quantity, unit_price, line_subtotal, line_vat_amount, line_total
FROM return_lines WHERE return_id = '${RETURN_ID}';"

echo
echo "── this tenant's return totals BEFORE ──"
"${PSQL[@]}" -c "
SELECT direction, count(*) AS docs,
       sum(subtotal_amount) AS subtotal, sum(vat_amount) AS vat, sum(total_amount) AS total
FROM return_documents WHERE tenant_id = '${TENANT}' GROUP BY direction ORDER BY direction;"

if [[ "$APPLY" != "--apply" ]]; then
  echo
  echo "DRY RUN — nothing deleted. Re-run with --apply to delete."
  exit 0
fi

echo
echo "═══ DELETING ═══"
# One transaction: children then parent. The FK would enforce the order anyway,
# but doing it explicitly means a failure leaves nothing half-removed.
"${PSQL[@]}" -v ON_ERROR_STOP=1 -c "
BEGIN;
DELETE FROM return_lines WHERE return_id = '${RETURN_ID}';
DELETE FROM return_documents WHERE id = '${RETURN_ID}';
COMMIT;"

echo
echo "═══ AFTER ═══"
"${PSQL[@]}" -c "
SELECT count(*) AS still_present FROM return_documents WHERE id = '${RETURN_ID}';"
"${PSQL[@]}" -c "
SELECT direction, count(*) AS docs,
       sum(subtotal_amount) AS subtotal, sum(vat_amount) AS vat, sum(total_amount) AS total
FROM return_documents WHERE tenant_id = '${TENANT}' GROUP BY direction ORDER BY direction;"

echo
echo "The journal is DERIVED (generate_tenant_journal replays current rows), so"
echo "the سند for this return disappears on the next regeneration — no manual"
echo "journal surgery is needed or wanted."
echo "Verify the P/L and the VAT report for this tenant now."
