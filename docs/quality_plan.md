# Quality Plan — post-freeze quality & completeness batch

_Planning only. Nothing here is implemented by this document; it scopes the HANDOFF
debt registry (`HANDOFF.md` §«بدهی‌های بَچ نهایی کیفیت») plus the founder's extended
list, so no item silently drops. Author: this session (2026-07-17). Do not execute any
line item without the founder scheduling it as its own batch._

## How to read this

Each item carries: **Scope** (what the effort actually is), **Acceptance** (the
observable done-gate), **Effort** (S ≤1 session · M 2–4 · L 5+ · XL multi-week),
**Founder input** (what only the founder can supply — blocks the item until provided),
and **Depends on** (other items/facts). Items are grouped by track and the ordering
column reflects **(impact × effort)** — high-impact/low-effort first.

Guiding constraints (inherited, non-negotiable): backend owns the contract; no invented
endpoints/fields/status; Decimal-as-string; no fake success toasts; soft-lock never
hard-hide; Persian errors; harness green before any deploy; **never guess a tax
identifier or a protocol — ASK the founder** (Moadian Stage D, ستید, buyer ids).

---

## Ordering summary (do in this order unless the founder re-prioritises)

| # | Item | Track | Effort | Founder-input gate |
|---|------|-------|--------|--------------------|
| 1 | Pre-prod checklist | Ops/Launch | S | none (I draft; he signs off) |
| 2 | VAT/عوارض split | Moadian/Reporting | M | rate table confirmation |
| 3 | Kavenegar SMS live | Notifications | S | API key + approved template |
| 4 | Zarinpal live | Billing | M | live merchant id + callback domain |
| 5 | Unified «پروندهٔ مشتری» admin view | Admin | M | none |
| 6 | Admin panel coherence overhaul | Admin | M | taste review |
| 7 | Quarterly VAT return view (اظهارنامهٔ فصلی) | Moadian/Reporting | L | official form fields |
| 8 | Full guide rewrite | Docs/UX | L | feature freeze must land first |
| 9 | Per-seat team | Platform | L | seat/role policy |
| 10 | Self-hosting | Platform/Ops | L | target customer + boundary |
| 11 | هلو/سپیدار migration | Import | XL | sample export files + field map |
| 12 | Payroll module (مالیات حقوق) | Reporting | XL | yearly tax tables + rules |
| 13 | Tax-school (آموزش) | Content | XL | curriculum + author |
| — | Moadian Stage D core | Moadian | XL | **official protocol docs (ASK)** |

Rationale: launch-enablers (1–4) unblock real revenue/compliance at low cost;
admin (5–6) pays down the most-touched internal surface; reporting (7,12) and the big
platform/content bets (9–13) are large and mostly founder-input-gated, so they queue
behind the freeze. Stage D sits outside the ranking — it cannot start until the founder
hands over the official docs.

---

## Track A — Launch enablers (unblock going live)

### A1. Pre-production checklist  ·  Effort S  ·  order 1
- **Scope.** A single `docs/pre_prod_checklist.md` covering everything that must be true
  before a paying customer touches prod: dev-OTP disabled behind the non-prod flag;
  Altcha/captcha enforced; rate limits on; secrets rotated out of any committed history;
  `MOADIAN_MODE` per-environment; DB backup + restore rehearsed; prune cron present;
  compose v2-only guard; migration/rollback runbook; smoke + harness green gate; error
  monitoring; TLS/domain; legal/privacy copy.
- **Acceptance.** Every line has an owner and a verified/❌ state; a dry run against a
  staging target passes each gate; the founder signs the bottom.
- **Founder input.** Final sign-off only; I can draft the whole thing.
- **Depends on.** Nothing blocking; references A3/A4 states when they land.

### A2. VAT / عوارض split (مالیات vs عوارض breakdown)  ·  Effort M  ·  order 2
- **Scope.** Official invoices and VAT reports must show مالیات and عوارض as separate
  components, not a merged «مالیات بر ارزش افزوده». Backend: carry both on the invoice
  line/summary and in the Moadian payload per the org's field split; frontend: show the
  breakdown in the invoice view, PDF, and the VAT report. Single source of truth for the
  rate/split.
- **Acceptance.** A reportable invoice renders مالیات and عوارض separately and their sum
  equals the total tax; the Moadian payload carries the split; VAT report columns
  reconcile; unit tests on the split math; guide + harness assertion updated.
- **Founder input.** Confirm the current statutory split (e.g. the standard rate and how
  عوارض is derived) so the math is authoritative — do not hard-code a guessed rate.
- **Depends on.** Touches the Moadian payload; sequence before the quarterly view (A/​C7).

### A3. Kavenegar SMS live  ·  Effort S  ·  order 3
- **Scope.** The provider-agnostic notification core already has `KavenegarProvider`
  (Verify/Lookup REST) wired OFF behind `KAVENEGAR_API_KEY`. Turn it on for real OTP +
  transactional sends: register the approved template, switch the OTP path from
  dev-response to real SMS in non-dev, keep the dev-OTP fallback strictly behind the
  non-prod flag.
- **Acceptance.** A real OTP arrives on a real handset in staging; dev-OTP still works
  in dev and is provably off in prod; failure falls back gracefully with a Persian
  message; no key in git.
- **Founder input.** The Kavenegar API key + the approved OTP/template text (sender line
  approval is Kavenegar-side).
- **Depends on.** A1 (prod flag discipline).

### A4. Zarinpal live billing  ·  Effort M  ·  order 4
- **Scope.** Move subscription/credit purchase from placeholder to real Zarinpal:
  request → redirect → verify callback → settle the plan/credit, idempotent on the
  callback, Persian receipts. Keep the gate rules (soft-lock) intact.
- **Acceptance.** A real low-value payment in staging completes end-to-end and settles
  the entitlement exactly once (verified against double-callback); refund/failed paths
  show honest Persian states; no fake success toast anywhere in the flow.
- **Founder input.** Live merchant id + the authorised callback domain.
- **Depends on.** A1; per-seat (B/​9) may change what a «plan» grants — coordinate.

---

## Track B — Admin

### B5. Unified «پروندهٔ مشتری» view in admin  ·  Effort M  ·  order 5  ·  **DELIVERED (Coherence Batch 1 · T2, 2026-07-18)** — `/admin/users/$userId`, existing endpoints only; partner-relationship lookup omitted (no mobile/user_id partner search endpoint — noted in-file); taste review pending.
- **Scope.** One screen per customer that stitches: user → businesses → taxpayer status
  → plan/modules/entitlements → partner relationship → usage/activity. Read-first;
  actions (approve profile, adjust plan) link out to the existing flows, not
  reimplemented.
- **Acceptance.** From one route an admin sees the whole customer without hopping between
  five pages; every datum traces to a real endpoint (no invented aggregation fields —
  compose from existing contracts or add one approved read endpoint); RTL/390px/dark all
  pass the three-questions test.
- **Founder input.** None to start; taste review at the end.
- **Depends on.** Pairs naturally with B6.

### B6. Admin panel coherence overhaul  ·  Effort M  ·  order 6  ·  **LARGELY DELIVERED (Coherence Batch 1 · T1, 2026-07-18)** — sidebar regroup, dead-stub nav retirement, one list/row-action/approve-reject grammar, admin page-tours; remaining: taste sign-off + the deferred S3 polish list in `digi-tax-frontend/docs/flow_audit.md`.
- **Scope.** Menus, grouping, naming, dead-stub removal, and visual consistency across
  the whole `/admin/*` shell. No new features — polish and coherence so the admin world
  reads as one product.
- **Acceptance.** Every admin route reachable from a coherent menu; no dead/placeholder
  stubs; consistent headers/empty-states/toasts; the paired-view rule (every merchant
  feature has its admin counterpart) verified; harness admin journey green.
- **Founder input.** Taste sign-off.
- **Depends on.** Best done with/after B5 so the unified view slots into the new IA.

---

## Track C — Reporting & Moadian

### C7. Quarterly VAT return view (اظهارنامهٔ فصلی / معاملات فصلی)  ·  Effort L  ·  order 7
- **Scope.** A preparation view that aggregates the quarter's sales/purchases into the
  official return shape (ماده ۱۶۹ / اظهارنامهٔ ارزش افزوده fields), ready to file. Gated
  behind an approved taxpayer profile per the locked gate rules.
- **Acceptance.** Numbers reconcile against the underlying invoices/purchases for a
  seeded quarter; the view maps 1:1 to the official form's fields; export/print; unit
  tests on the aggregation; guide + harness updated.
- **Founder input.** The exact official form fields/format for the target period — do not
  reverse-engineer from memory.
- **Depends on.** A2 (VAT/عوارض split must exist first so the components are separable).

### C-D. Moadian Stage D core  ·  Effort XL  ·  order — (gated)
- **Scope.** Invoice patterns beyond نوع اول, bulk send, and the ابطال/اصلاحی/برگشتی
  lifecycles, signing, and sandbox validation. This is the large compliance core after
  SMS.
- **Acceptance.** Each lifecycle round-trips against the org and the کارپوشه reflects the
  correct state; single-source status buckets extended to cover the new subjects; no
  ابطال/اصلاحی path fires without explicit founder authorisation semantics.
- **Founder input.** **The official protocol docs — ASK, never guess the protocol or a
  subject code.** This is the gate; the item cannot start without them.
- **Depends on.** MD-2 transport (done); A2 for the tax split.

### C-serial. Moadian invoice serial (`inno`) alignment  ·  Effort M  ·  order (after go-live smoke)
- **Scope.** The org returns a **non-blocking** warning `1300501` («سریال صورتحساب با
  اطلاعات سامانه منطبق نیست») on every submission. Root cause (verified live): our
  `_next_inno` uses **epoch-seconds** as the fiscal-memory internal serial, but the
  taxid spec (§7-1) defines `inno` as the fiscal memory's **sequential internal
  counter** («سریال صورتحساب داخلی حافظه مالیاتی»), which the org expects to increment
  monotonically. Epoch-seconds are unique+monotonic (so invoices are ACCEPTED) but never
  match the org's expected next-serial, hence the warning.
- **Acceptance.** A gap-free, per-fiscal-memory sequential `inno` whose values match the
  org's expected sequence; the `1300501` warning disappears on a live submission.
- **Founder input.** Confirm the expected starting point / semantics — دیباتک has already
  registered invoices with epoch-seconds serials, so the org's "last serial" is now a
  large number; the counter must resume correctly from there (do not guess — validate
  against the org's inquiry state before switching).
- **Depends on.** Non-blocking today; schedule before high-volume real use. Logged from
  the MD-3 نوع دوم live test.

### C-abtal. ابطالی/اصلاحی lifecycle packet is over-populated  ·  Effort M  ·  order (Stage D)
- **Scope.** First live ابطال (cancellation, ins=3) of two نوع دوم invoices **succeeded**
  (org SUCCESS/accepted) — but the org returned ~20 **non-blocking** warnings
  (`14004/14007/14022–14059`) reporting that essentially every line, total, and
  type/pattern field is «خارج از الگو» for an ابطالی. Root cause: `submit_lifecycle`
  reuses the full `submit_invoices` build and re-sends the entire invoice body+totals
  with `ins=3`, but an ابطالی صورتحساب's pattern expects a **minimal packet** keyed on the
  reference taxid (`irtaxid`), not a full re-statement of the original. Verified live.
- **Acceptance.** ابطالی/اصلاحی packets carry only the fields their pattern defines (per
  RC_IITP §5 + جدول ۸); a live cancellation returns with no «خارج از الگو» warnings.
- **Founder input.** Confirm the exact ابطالی/اصلاحی/برگشتی field sets from the official
  doc before trimming (never guess which fields to drop).
- **Depends on.** Part of Moadian Stage D (lifecycles). Non-blocking today.

### C12. Payroll module (مالیات حقوق)  ·  Effort XL  ·  order 12
- **Scope.** A standalone payroll-tax module using the yearly `tax_tables` pattern:
  employees, monthly payroll, bracket-based withholding, and the list/return output.
- **Acceptance.** Withholding matches the official brackets for a worked example; yearly
  tables are data-driven (no hard-coded rates); output matches the filing format.
- **Founder input.** The current-year tax tables + the payroll rules (exemptions,
  brackets, rounding).
- **Depends on.** Independent; large — schedule as its own phase.

---

## Track D — Platform & content bets

### D9. Per-seat team (multi-user per business)  ·  Effort L  ·  order 9
- **Scope.** Multiple users under one business with roles/permissions; invitations; seat
  counting tied to the plan.
- **Acceptance.** A second user can be invited, scoped, and billed as a seat; role gates
  enforce on both API and UI; audit of who-did-what.
- **Founder input.** The seat/role policy — which roles exist, what each can do, how
  seats price.
- **Depends on.** Coordinates with A4 (billing) — a seat is a billable unit.

### D10. Self-hosting  ·  Effort L  ·  order 10
- **Scope.** Package the stack so a customer can run it on their own infrastructure
  (compose bundle, env template, migration/seed runbook, upgrade path, license/telemetry
  boundary).
- **Acceptance.** A clean box brings the whole stack up from the bundle and passes smoke
  + a login journey; secrets are operator-supplied; documented upgrade path.
- **Founder input.** The target customer and the product boundary (what a self-host build
  may/may not include — e.g. Moadian keys, partner world).
- **Depends on.** A1 (prod discipline) informs the bundle.

### D11. هلو / سپیدار migration (import)  ·  Effort XL  ·  order 11
- **Scope.** Import customers/products/opening balances/invoices from هلو and سپیدار
  exports into the DigiTax model — the classic switching-cost remover.
- **Acceptance.** A real sample export imports with a mapping report and a
  reconciliation (counts + totals match the source); dry-run/preview before commit;
  idempotent re-import.
- **Founder input.** Sample export files from both systems + the field-mapping decisions
  (their schema → ours).
- **Depends on.** Nothing technical; entirely gated on real sample files.

### D13. Tax-school (آموزش / محتوا)  ·  Effort XL  ·  order 13
- **Scope.** In-product educational content — a structured «مدرسهٔ مالیات» that teaches
  merchants the concepts behind each feature.
- **Acceptance.** A content model + at least one full track published and reachable;
  reads on-brand (warm, no scary jargon) per the tone rules.
- **Founder input.** The curriculum and who authors it (content, not code, is the long
  pole).
- **Depends on.** D8 (guide rewrite) shares a content pipeline — build once.

---

## Track E — Docs

### D8. Full guide rewrite (merchant + admin + partner)  ·  Effort L  ·  order 8
- **Scope.** Rewrite all three guides top-to-bottom against the **frozen** product — not
  incremental patches. Concrete «open page X → see Y» steps; the login-world/persona
  tables stay generated from `world_fixtures.py`, never hand-edited.
- **Acceptance.** Each guide walks the real current UI with no drift; no-drift check
  passes; the founder can hand a guide to an accountant and it matches the screen.
- **Founder input.** None beyond the freeze itself.
- **Depends on.** **Hard dependency: the feature freeze must land first** (HANDOFF §4 —
  post-SMS). Writing before freeze guarantees re-drift.

---

## Cross-cutting notes

- **Freeze is the pivot.** D8 and much of Track D assume the product stops moving. Track A
  (launch enablers) and Track B (admin) can proceed before freeze because they harden
  what exists rather than describe it.
- **Every reporting/Moadian item is founder-input-gated on a real statutory artifact**
  (rate table, official form, protocol doc). None may be built from memory — that is the
  same rule that stopped Part 4's real invoice on the ستید.
- **Each item ships with tests + guide-no-drift + a harness assertion** — the standing
  DoD, not optional.
