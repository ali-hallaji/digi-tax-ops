# PARTNER UX batch (Part 3 of the EVAL batch) — BANKED, not started

_2026-08-01. Banked under the batch's own 97% rule («PART 3 is the one to
bank»). Parts 1 shipped, Part 2 skipped (gate file absent — see the report)._

## ⚠️ The instruction arrived TRUNCATED

The founder's Part-3 spec cut off mid-sentence at:
«Checkout applies the …». Item 3's checkout/commission interaction semantics
(does the discount reduce the commission base? who absorbs it? floor/ceiling
defaults?) are MONEY RULES and were NOT guessed. **Ask the founder to re-send
the end of the Part-3 paragraph before building item 3.**

## What Part 3 asks (as received)

1. **Admin per-partner commission rates** on partner create/edit for the
   existing two-tier snapshot model: validation, who/when/old→new history,
   visible on the partner detail page. AUDIT FIRST — per-partner
   `commission_percent` already exists at least as a nullable column
   (DEFAULT_COMMISSION_PERCENT=15 in app/core/plan.py, partner_profiles
   table, partner_commission_settings table exists); surface/clarify rather
   than duplicate. Changed rates affect FUTURE activations only; historical
   snapshots untouched — pin with a test.
2. **Referral-code clarity**: locate the TWO code fields in merchant settings,
   document what each does today, distinct labels + helper lines, both/neither
   behavior; a dead one → propose removal (founder GO required).
3. **Partner discounts** tied to the partner code, per module/SKU or all,
   bounded by NEW admin params (floor/ceiling, with history), enforced API+UI.
   Checkout application semantics = the truncated part. DO NOT build until the
   founder completes the spec.

## Audit starting points (verified to exist, unread)

- Tables: partner_profiles · partner_commission_settings ·
  partner_commission_accruals · partner_credit_activations ·
  partner_grant_events · referred_revenue_events · partner_payouts.
- Code: app/core/plan.py (DEFAULT_COMMISSION_PERCENT) · partners module ·
  billing/checkout.py (where a discount would apply) · admin partners screens
  (frontend `_admin.admin.partners.*`).
- Merchant settings referral fields: search `کد معرف` in
  digi-tax-frontend/src/routes/_app.app.settings.tsx + the wizard.
- Docs: partner_panel_design_v1.md · LAUNCH_ROADMAP «Launch Batch 3 — partner
  panel v2».

Laws unchanged (rate history like module_price_history; snapshots immutable;
guides in-commit; harness gate).
