# CONTINUATION 2 (2026-07-28) — read this first

## Part A — GOLD: **SOLVED**, and it was a one-ریال rounding bug

The org REGISTERED our gold invoice. Everything about الگوی سوم — the shape, the
formulas, the taxid, the signing, the transport — was already right; the packet
was refused over **one ریال**. The org re-derives every computed amount with
integer arithmetic and **TRUNCATES**; we rounded half-up.

**The rule, settled empirically:**

```
Es  = ⌊am × fee⌋
Is  = Es + TAs − Gs                     (adis)
Ks  = ⌊ TAs×goldRate/100 + Es×J/100 ⌋   sum the two terms, THEN truncate
Os  = Ks + Is                           (tsstam)
```
One line per article; the gold quartet (`consfee`/`bros`/`spro`/`tcpbs`) is
**mandatory on EVERY line** — a "fee on its own line" split is rejected outright.

**This was never gold-specific.** The same rule governs الگوی اول, so any
ordinary invoice whose VAT or line amount landed on half a Rial was being
rejected (`0204501` / `0204101`). Round demo numbers hid it. Fixed at the root:
`converter._rial` now truncates.

Thirteen sandbox submissions, one variable at a time, full table + both accepted
payloads verbatim: **`docs/moadian/gold_pattern3_sandbox_2026-07-28.md`**.

### Four more real defects fell out of walking the gold journey in the UI

The packet was right while the product around it was not. All four are fixed:

1. **The printed invoice charged VAT on the exempt gold** and left اجرت/سود out of
   the total the customer owes. `invoice_drafts.compute_line_amounts` now applies
   the gold formulas with the same rate the packet reads.
2. **A line's شناسهٔ کالا never resolved against the org catalog.** `tax_items` is
   the tenant shortlist and is empty on most businesses; the search box reads
   `tax_stuff_ids` (~۴M codes). So every code a merchant picked was filed as a
   *manual* code carrying no registered rate.
3. **The form's echoed VAT rate beat the catalog's.** The org validates the rate
   against the stuffid (`0303301`), so a differing value is a guaranteed
   rejection, not an override. The catalog is now authoritative.
4. **Our own validator blocked a correct gold invoice**, recomputing every amount
   with the plain-sale formula. It is pattern-aware now.

Net effect, verified on dev through the real UI: a gold invoice built by a
merchant produces a packet **byte-for-value identical** to the one the org
registered (`A2HP31050B5006AF9168F4`).

Still open (founder's call, logged not done): the invoice document keeps 4-decimal
precision internally (`_q4`) while the org record is whole-Rial, so a non-gold PDF
can still print ۱ ریال more VAT than the tax record holds. Changing it touches
accounting/journals/reports.

## Part B — party interim voucher: **DONE**

New معین `2102` «حساب واسط طرف حساب», تفصیلی per party, built lazily. A هزینه with
a NAMED party now emits ONE voucher:

```
هزینه / مالیات   بدهکار        حساب واسط طرف   بدهکار
  حساب واسط طرف        بستانکار      خزانه            بستانکار
```

The interim legs cancel, so مانده is untouched and the party's ledger finally
shows گردش. Party-balances (screen + export) gained **گردش بدهکار/بستانکار**, read
from the journal lines carrying the party. An expense with no party keeps its
plain two-line سند. Proven live on dev (سند ۷۴, تولیدی سرماساز).

Also added `2103` «حقوق و دستمزد پرداختنی» — the balancing leg the payroll import
needs.

## Part C — importer: **DONE**, both real files end-to-end

`app/modules/ledger_import/` — analyze (writes nothing) → the accountant sees the
detected source, every mapped column and every parsed row → commit, tagged with a
batch that one «برگرداندن» undoes. Screen at `/app/accounting/import`.

Every trap in the founder's real exports is now a test, because each one silently
produces a WRONG import rather than an error:

| Trap | What it would have done |
|---|---|
| both files named `.xls`, neither is BIFF (one xlsx, one SpreadsheetML) | valid file rejected as unreadable |
| Sepidar headers use ARABIC ك/ي | header matching finds nothing at all |
| labelless «جمع» row with real numbers | doubles every figure in the voucher |
| payroll sheet is one-sided (۶۲۹٬۴۱۳٬۰۵۸ debit, 0 credit) | unbalanced voucher |
| «هزینه» stolen by «مرکز هزینه»; «طرف حساب» by «- کد حساب» | wrong column read as the amount |
| mobile glued to the name with no separator | no customer, or the wrong one |
| row 50 is a CREDIT NOTE (negative total) | a return imported as a sale |

**Verified on dev through the real UI:** تدبیر → 61 of 62 invoices + 8 customers,
stored total ۲۶٬۰۵۶٬۰۸۴٬۷۷۱ == the file's own, the credit note named and refused;
سپیدار → one balanced 7-line voucher, ۶۲۹٬۴۱۳٬۰۵۸ each side, «جمع» row dropped
with a visible warning and the balancing leg shown before committing.

Imported sales are **internal** documents, never tax-reportable — the org already
received them from the merchant's previous software.

Re-runnable proof: `scripts/ledger_import_proof.py` (run inside the api container).

## Part D — pricing wires + cleanup: NOT STARTED

Unchanged from the previous state doc, and still the right resume point:

1. `document_pack` SKU row + price (nothing is purchasable yet).
2. Checkout: `_price_the_basket` rejects an already-entitled feature — a
   consumable must bypass that; `_activate_paid_order` must create a
   `DocumentQuotaPack` rather than flip an entitlement.
3. Usage card must add purchased headroom.
4. Admin price-history UI (the table exists and is populated; no screen reads it).
5. Plans page polish.
6. Cleanup: `prod_smoke` false-green (`otp_hint` unmatched + probes the one
   hint-protected mobile); 1.7 GB untracked DB dumps in the ops worktree on the
   server; `smoke_test.sh` stale vs captcha; matrix rows citing pre-rotation
   taxids.

## Open questions for the founder

1. **Sub-Rial money in the document** (above). The org is whole-Rial and
   truncating; our ledger keeps 4 decimals. Align them, and if so, in the same
   direction?
2. **Gold submit is entitlement-gated** on نیک‌تجارت, so the final «ارسال» click
   could not be exercised in the UI. The packet it would send was built and
   compared instead — identical to the accepted one.
3. **Payroll account mapping** defaults by title words (بیمه → بیمه, else حقوق)
   and the accountant can change every row before committing. Worth a saved
   per-source mapping so the second import needs no clicks?
