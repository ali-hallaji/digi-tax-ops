# Digi Invoice — Canonical Onboarding Brief

Last updated: 2026-07-04 · **This file supersedes every older status claim.**
Read this FIRST in any new session, before older briefs/status tables. When any other doc
disagrees with this file about *status*, this file wins (rules still live in workspace
`CLAUDE.md`; product scope still lives in `business_scope_freeze_v1.md` — but that doc's
*status columns* are dated 2026-06-16 and are stale).

## What the product is

**Digi Invoice**: simple, cloud, Persian-RTL, mobile-first accounting + tax-readiness SaaS for
Iranian merchants — dramatically simpler than Holoo/Sepidar. #1 principle: **a merchant with no
accountant must never see accounting complexity** (journal/debit/credit live behind the scenes,
for a future accountant layer). Revenue = subscriptions; Moadian is a required edge capability,
never faked.

## TRUE current state (verified in code, 2026-07-04 audit)

**Stale-brief warning:** any older brief saying "P0/P1 not closed — do not start
invoices/accounting" is WRONG. Reality:

### Built and real (backend + frontend, tested)
- Auth/OTP (dev-OTP behind flag), businesses/tenants, members with owner/admin/staff/viewer +
  owner-admin server guard, admin panel (taxpayer review, users, moadian profiles).
- Customers (identity-validated, `total_receivable` live recompute incl. invoice
  finalize/cancel hooks) · Vendors (thin: name/phone/email, `total_unpaid` recompute) ·
  Products/services (catalog + tax codes; **no inventory**).
- **Invoice core** (`invoice_drafts`): proforma / سند داخلی / فاکتور رسمی; draft→finalize→
  cancel/archive lifecycle; readiness gating; smart-line resolver; print/PDF (A4, landscape,
  80mm; renders «ریال»).
- Purchases (lump-sum + line items) + expenses, delete-path integrity fixed.
- **Payments module** (`/payments`): aggregate receipts/payments per party, cash|card|transfer,
  balances recompute. **No invoice linkage yet — that is this phase.**
- Per-business **display currency** rial|toman (display-only; canonical unit is ریال).
- Taxpayer profile 5-state workflow; identity validation centralized both sides
  (کد ملی mod-11 · شناسه ملی length-only · کد اقتصادی 12 · mobile prefixes).
- Moadian: onboarding/keys/validate/dry-run real; **live submit gated** (crypto unconfirmed,
  R1B) — submit button is a disabled placeholder; never fake referenceNumber/taxid/status.

### NOT built (the current phase exists to close most of this)
- Treasury depth: **no cheque, no bank-account/صندوق entities, no POS mapping, no transfers,
  no installments, no prepayment UX**.
- **No invoice↔payment linkage** (settlement is aggregate-only), no combined settlement window.
- **No returns** (برگشت از فروش/خرید). No inventory (deferred, phase 2).
- **No real reports; dashboard KPIs are seeded placeholders** (`app/modules/dashboard/` fakes).
- No journal/ledger (deliberate — merchant never sees it; accountant layer = phase 2).
- No subscriptions/paywall (post-launch phase 2). Excel import / AI persistence: later phases.
- Frontend duplicate to remove: `/app/payments` + `/app/transactions` (same API, two pages);
  dead mock `/app/tax/*` tree + orphan mock components await deletion (approved).

## The active phase — "Phase 1: real accounting core" (approved 2026-07-04)

Canonical docs (read both before ANY phase-1 task):
1. `docs/phase1_accounting_plan_v1.md` — audit, gap table vs Holoo/Sepidar, scope, build Steps 0–6.
2. `docs/phase1_user_scenarios_v1.md` — **55 scenarios, locked Persian terminology, 16 locked
   decisions, journey map, shared-screen matrix.** The decisions table there is the single
   decision log; do not re-debate closed decisions.

Build order (each step ships a complete merchant story):
```
Step 0  de-dup cleanup (merge payments+transactions → «دریافت و پرداخت»; delete dead /app/tax + orphans)
Step 1  حساب‌های من (bank accounts + صندوق + transfers + opening balances; POS mapping)
Step 2  invoice↔payment linkage (+ migrate purchases' self-entered paid_amount into payment rows)
Step 3  combined settlement window «دریافت وجه»/«پرداخت وجه» — PROGRESSIVE default face (decision 16)
Step 4  cheque lifecycle (دریافتی/پرداختی: در جریان→واگذار→وصول/برگشتی) — minimal, no صیاد
Step 5  returns (برگشت از فروش/خرید, financial-only)
Step 6  real dashboard + 4 merchant reports; then phase close (E2E refresh, reseed, docs, push ritual)
```

## Non-negotiables for every phase-1 session
- Merchant screens: task language only — never debit/credit/سند; hide accounting concepts per
  the catalog's "accounting-literacy flags" table.
- One concept = one surface (shared-screen matrix in the catalog); the settlement dialog is ONE
  component with modes — never fork it.
- Money: canonical ریال strings; display via `useMoney()`; Jalali dates via `JalaliDateField`;
  identity via `useIdentityField`. All the workspace CLAUDE.md golden rules apply.
- Cheques become money ONLY at وصول. Never fake Moadian anything. No new DB without instruction.
- Model: Fable 5 for phase-1 build prompts (per founder). Captcha state reported every message.

## Session ritual pointer
Workspace `CLAUDE.md` §0 (Serena single-active, per-repo CLAUDE.md, skills) → then THIS file →
then the two phase-1 docs → then repo `docs/progress.md` for the latest per-repo entries
(`digi-tax-backend/docs/progress.md` and `digi-tax-frontend/docs/progress.md` are the
ground truth for what landed most recently).
