# Invoice Flow Integrity Matrix — the permanent QA contract

_Created: 2026-07-24 (INVOICE FLOW INTEGRITY batch). This document is the canonical
scenario matrix for the ENTIRE issuance journey. **HARD LAW: a scenario counts as
PROVEN only when walked through the REAL UI journey (create → … → org response).
Engine-level calls (curl, pytest, container scripts) are supporting evidence, never
the proof.** Any change to issuance behavior must update this matrix in the same
commit; any red row blocks the batch that produced it._

## Canonical rules the matrix encodes (founder-locked)

1. **Internal invoices (پیش‌فاکتور `proforma` / فاکتور داخلی `internal_private`) never
   require a customer** and carry **zero Moadian friction** — no نوع, no validate/submit
   UI, no buyer-identity demands, anywhere.
2. **Tax-reportable + نوع اول (type 1)** is the ONLY scenario where a customer with
   full identity is required: name + (کد ملی for حقیقی | شناسه اقتصادی for حقوقی).
   Postal/address are recommendations (warnings), never blockers.
3. **Tax-reportable + نوع دوم (type 2)**: buyer is OPTIONAL and never blocking.
   «بدون مشخصات خریدار» is ONE tap with ZERO required fields and proceeds straight to
   finalize. An attached customer with missing/partial ids never blocks. A legacy
   12-digit economic code is ACCEPTED with an amber (never red) nudge; the packet
   builder substitutes the 11-digit شناسه ملی for `tinb` automatically.
4. **Type switch 1↔2 on an existing draft re-evaluates requirements LIVE** — stale
   rules must never trap the user.
5. **The finalize/submit button always explains what's missing** — never silently dead.
6. **Single source of (effective buyer, نوع):** backend
   `converter.resolve_effective_buyer_and_type` — `moadian_type_override` wins (1|2);
   otherwise buyer presence derives the نوع (buyer→1, walk-in→2). The draft readiness
   gate, the Moadian validator, the preview, and the UI must all obey the SAME resolver.
7. **ZERO-TOTAL law**: real (non-sandbox) test submissions are zero-total only
   (100% discount, نوع دوم walk-in). Non-zero proofs go to the نیک‌تجارت sandbox.

Persona map for proofs: **نیک‌تجارت** `09120001002` (sandbox, non-zero allowed) ·
**دیباتک** `09120000000` (live, zero-total smoke only) · demo «کاربر نمونه»
`09120009000` (sandbox, drafts).

## A — Issuance core: kind × نوع × buyer × amount

Legend: kind `INT` = internal (proforma/internal_private), `TAX` = tax_reportable.
Proof = real-UI Playwright journey on dev unless noted. Viewport: rows marked 📱 are
proven at 390px; the rest desktop.

| # | Kind | نوع | Buyer | Amount | Expected behavior | Proof | Status |
|---|------|-----|-------|--------|-------------------|-------|--------|
| A1 📱 | TAX | 2 (one-tap walk-in) | none | real | Step 2 «بدون مشخصات خریدار» = one tap, zero fields → finalize enabled → validate OK → sandbox submit → org ACCEPTED | UI journey, نیک‌تجارت sandbox | pending |
| A2 📱 | TAX | 2 | customer, no ids | real | Customer attaches fine; identity NEVER blocks finalize/validate/submit; org ACCEPTED | UI journey, sandbox | pending |
| A3 | TAX | 2 | customer, partial (name only) | real | Same as A2 — warnings only (postal/address «توصیه می‌شود»), never a blocker | UI journey, sandbox | pending |
| A4 | TAX | 2 | customer, full ids | real | Accepted; packet carries buyer snapshot with inty=2 | UI journey, sandbox | pending |
| A5 📱 | TAX | 1 | customer, full ids | real | The strict path: finalize OK, validate OK, submit → org ACCEPTED | UI journey, sandbox | pending |
| A6 | TAX | 1 | customer, missing id | real | BLOCKED with the named missing field (e.g. «کد/شناسه ملی برای اشخاص حقیقی لازم است») shown inline AND on the finalize button explainer; one-tap escape to نوع دوم offered | UI journey, sandbox | pending |
| A7 | TAX | 1 | none | real | BLOCKED with «برای صورتحساب نوع اول، اطلاعات خریدار لازم است» + visible path (select customer OR switch to نوع دوم); button explains, never silently dead | UI journey | pending |
| A8 | TAX | 1 | customer, legacy 12-digit eco code | real | ACCEPTED with amber nudge «کد اقتصادی جدید همان شناسه ملی (۱۱ رقمی) است»; packet `tinb` = the 11-digit شناسه ملی | UI journey, sandbox | pending |
| A9 | TAX | 1↔2 switch on existing draft | any | real | Switching type re-evaluates requirements LIVE both directions; no stale blockers; readiness + validate + button text all follow | UI journey | pending |
| A10 📱 | INT | — | none | real | No customer demanded at ANY step; no Moadian UI anywhere; finalize + print/PDF work | UI journey | pending |
| A11 | INT | — | customer | real | Customer optional-attach works; still zero Moadian friction | UI journey | pending |
| A12 | TAX | 2 | none | **zero-total** (100% discount) | THE live smoke on دیباتک: finalize → validate → LIVE submit → org ACCEPTED «ثبت شده»; ZERO-TOTAL law honored | UI journey, دیباتک LIVE | pending |

## B — Draft lifecycle

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| B1 📱 | Create draft → add lines (product + free-title) | Lines add/edit/remove; totals recompute; Shamsi date; money formatting per §7.3 | UI journey | pending |
| B2 | Edit draft header + lines | Only `draft` status editable; edits persist (reload-proof) | UI journey | pending |
| B3 | Delete line / archive draft | Friendly Persian confirm; totals recompute; archived leaves list | UI journey | pending |
| B4 | Finalize | Document number assigned per business numbering config; editing locks; receivable recomputes when customer attached | UI journey | pending |
| B5 | Finalize with zero lines | BLOCKED «برای نهایی‌سازی، حداقل یک ردیف لازم است» — explained, not dead | UI journey | pending |
| B6 | Convert internal → tax_reportable | Allowed only when tax requirements satisfied (override-aware); gated on approved taxpayer profile | UI journey | pending |
| B7 | Settle — cash receipt | Payment records; `payment_status` transitions unpaid→partial→paid | UI journey | pending |
| B8 | Settle — cheque | Cheque received against invoice; lifecycle (در جریان/وصول) reflects on invoice paid state | UI journey | pending |
| B9 | Print view + PDF | Both kinds render Persian RTL, Vazirmatn, correct totals; walk-in shows «مصرف‌کنندهٔ نهایی», never an empty buyer error | UI journey | pending |
| B10 | Fiscal-year lock | Out-of-window issue date blocked with the FY message; in-window passes | UI journey | pending |

## C — Moadian journey (tax_reportable only)

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| C1 📱 | Validate (پیش‌بررسی) | Interpreted issues; نوع-aware (same resolver); zero raw JSON | UI journey | pending |
| C2 📱 | Submit → org result | Sandbox: real submit → interpreted org response; taxid + reference rendered copyable | UI journey, sandbox | pending |
| C3 | Inquiry / refresh status | «به‌روزرسانی وضعیت» updates from org; «آخرین استعلام» timestamp | UI journey | pending |
| C4 📱 | Status lock after registration | Panel permanently shows persisted state (no re-validate CTA); lifecycle actions offered | UI journey | pending |
| C5 | اصلاحیه (amendment) | New packet ins=2 carrying accepted original's taxid; org ACCEPTED | UI journey, sandbox | pending |
| C6 | ابطال (cancellation) | ins=3 carrying original taxid; org ACCEPTED; amend-after-cancel blocked friendly | UI journey, sandbox | pending |
| C7 | برگشت از فروش — full | Return document → packet sold-minus-returned; org ACCEPTED | UI journey, sandbox | pending |
| C8 | برگشت از فروش — partial | Partial quantities; org ACCEPTED | UI journey, sandbox | pending |
| C9 | Bulk submit | Multi-select → submit-bulk (≤1000); per-invoice interpreted results | UI journey, sandbox | pending |
| C10 | Excel import — نوع اول rows | Sample downloads; import creates drafts; per-type columns honored | UI journey | pending |
| C11 | Excel import — نوع دوم rows | Walk-in rows import with NO buyer columns required | UI journey | pending |
| C12 | Entitlement-gated business | No `moadian_submission` → honest «FEATURE_NOT_ENABLED» Persian module-state message, NEVER a generic access-denied; internal invoicing untouched | UI journey | pending |
| C13 | Duplicate اصلی re-submit | Friendly rejection steering to اصلاحیه/ابطال (E PART 2 guard) | UI journey | pending |
| C14 | 1300501 تذکر rendering | Serial-continuity notice renders as calm non-blocking تذکر, never red/error | UI journey | pending |
| C15 | پیمانکاری (الگوی ۴) | Pattern selector فروش/پیمانکاری (نوع اول only); crn required (numeric ≤12) when پیمانکاری; Excel crn column | UI journey; org proof founder-blocked on کارپوشه crn | pending |

## D — Internal-invoice purity sweep

| # | Scenario | Expected behavior | Proof | Status |
|---|----------|-------------------|-------|--------|
| D1 | Internal create/edit/finalize/print | Zero Moadian UI (no نوع line, no validate/submit, no buyer-identity text) at every step | UI sweep | pending |
| D2 | Internal invoice list + detail | No Moadian status column/filter leakage for internal docs | UI sweep | pending |

## Proof artifacts

Screenshots land in `digi-tax-frontend/qa-screens/matrix-<ts>/<row>-*.png`, one per
row minimum, referenced from the Status column when green (✅ + shot name). The
Playwright journeys live in the experience-harness tree so they stay runnable.
