# Corrective (اصلاحیه, ins=2) — EMPIRICAL item-edit verdicts

_Batch 2 Part 2. Recorded per the EMPIRICAL-TEST LAW (workspace CLAUDE.md §2): when the
sandbox can answer a question about org behaviour, we submit the experiment and let the
org's real response decide the product — not a doc citation._

**Environment:** نیک‌تجارت sandbox (tenant `7085fcf2…`), self-tsp, live sandbox
(`sandboxrc.tax.gov.ir`). Script: `digi-tax-ops/scripts/corrective_experiment.py`
(creates the corrective draft via the engine, applies the mutation the UI forbids,
finalizes, submits, inquires the org verdict).

## Verdict table

| # | Corrective operation on an accepted original | Org verdict | Evidence (sandbox taxid) | Product action |
|---|---|---|---|---|
| a | **ADD a brand-new line** | **✅ ACCEPTED** («ثبت شده») | `A2HP31050B2006AF916817` (corrective of INV-2026-000022, 2026-07) | **UNLOCK** — the add-line form is now available in the corrective wizard (a new line sets its own شناسهٔ کالا). |
| b | **REMOVE a line entirely** | ✅ ACCEPTED («ثبت شد») | MOADIAN F: INV-2026-000027 deleted line 3 and registered | Already allowed (the «حذف» button). |
| c | **REPLACE an existing line's شناسهٔ کالا (sstid)** | **❌ REJECTED** («رد شد») | `A2HP31050B2006AF916829` (corrective of INV-2026-000023; 2800002692993→2001666836426, both @10%) | **KEEP LOCKED** on existing lines — reason stated to the user is the org's own behaviour: «سامانهٔ مودیان تغییر شناسهٔ کالای یک ردیف را در اصلاحیه نمی‌پذیرد.» |
| d | **Change تعداد + مبلغ + تخفیف** | ✅ ACCEPTED | MOADIAN F: INV-2026-000027 changed qty 2→5 + price 2M→2.5M and registered | Already allowed. |

## What the product does now (corrective wizard, `_app.app.invoices.$invoiceId.tsx`)

- **تعداد / مبلغ / تخفیف** on existing lines — editable (as before).
- **حذف ردیف** — allowed (as before).
- **افزودن ردیف جدید** — NOW ALLOWED (the add-line form is shown in a corrective; `lockTaxProfile` is per-line = `isCorrective && line.tax_item_id` so a copied line's sstid is locked but a new line can pick its own).
- **شناسهٔ کالای ردیف‌های موجود** — LOCKED, with the org's behaviour as the stated reason (not a doc guess).
- نوع/الگو/خریدار/نرخ مالیات — frozen (unchanged).

## Correction to the earlier assumption

The MOADIAN F spec (`md_f_corrective_spec.md`) cited RC_IITP §5-2 نکته ۲ to LOCK adding a
line. **The sandbox disproves that reading** — the org accepts an added line. The doc
citation was over-strict; the empirical verdict wins. The sstid-replace lock, by
contrast, is confirmed by the org's rejection, so it stays — but its stated reason is now
the org's behaviour, not our interpretation of the دستورالعمل.

_Last updated: 2026-07-25 (Batch 2 Part 2)._
