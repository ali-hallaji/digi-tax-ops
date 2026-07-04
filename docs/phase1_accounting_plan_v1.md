# Phase-1 Accounting Plan — Digi Invoice (v1, pending founder approval)

Date: 2026-07-04 · Status: **APPROVED (2026-07-04) — no build code started.**
Companion: `phase1_user_scenarios_v1.md` (55 scenarios; all 9 open questions + 6 review
ambiguities resolved — its decisions table is the canonical decision log for this phase).
Authors: Claude (Fable 5) planning session · Sources: code audit of all three repos (2026-07-04),
`progress.md` (both repos), `api_contracts_v2_2.md`, `business_scope_freeze_v1.md`,
`product_scope_v2_2.md`, founder's Holoo/Sepidar gap analysis (5 pillars).

Governing principles (restated, judged against): (1) merchant-without-an-accountant — all
accounting complexity behind the scenes; (2) real ui-ux-pro-max quality per screen; (3)
user-ordered flow, correct Persian, zero duplicate concepts; (4) RTL, mobile-first,
rial-canonical money, centralized validators.

> Staleness note: `business_scope_freeze_v1.md`'s status table (2026-06-16) and the frontend
> `current_phase.md` mock/real table are outdated — vendors/purchases/expenses/payments are now
> REAL. This document's Part A is the current code-level truth.

---

## PART A — What exists today (read-only audit, by pillar)

### Pillar 1 — Counterparties (طرف حساب‌ها) — **BUILT, asymmetric**

| Capability | Status | Evidence |
|---|---|---|
| Customers CRUD + identity + `total_receivable` | BUILT | `app/modules/customers/` — table `customers`: `customer_type individual|legal`, `economic_id`/`national_id` (String(20) — stale vs the canonical 12/10-11 rule), `mobile`, `total_receivable Numeric(20,4)`. Endpoints `GET/POST /customers`, `GET/PATCH/DELETE /customers/{id}` |
| Vendors CRUD + `total_unpaid` | BUILT (thin) | `app/modules/vendors/` — table `vendors`: only `name/phone/email/note/total_unpaid`. **No identity fields** (needed later for معاملات فصلی). Endpoints mirror customers |
| Receivable recompute | BUILT | `customers/application/services.py:254` — `max(0, Σ finalized invoice totals − Σ payments)`; triggered by payment create/update/delete **and** (fixed 2026-07-02) invoice finalize/cancel |
| Payable recompute | BUILT | `vendors/application/services.py:203` — `max(0, Σ purchase outstanding − Σ payments)` |
| Frontend | REAL | `/app/customers`, `/app/vendors` — wired, validated (useIdentityField), polished |

Holoo/Sepidar treat customer+vendor as one "counterparty" concept. We have two thin-linked
models; a party can't be both without duplication. Acceptable for phase 1 (see gap table).

### Pillar 2 — Goods & inventory (کالا و انبار) — **catalog BUILT, inventory MISSING**

| Capability | Status | Evidence |
|---|---|---|
| Product/service catalog | BUILT | `app/modules/products/` — `product_type goods|service`, `sku`, `sstid/sstt` (tax codes), `unit_code/unit_name`, `default_unit_price`, `default_vat_rate`, `currency` | 
| Product tax profile | BUILT | `PATCH /products/{id}/tax-profile` + tax-items catalog search |
| Stock quantities / movements / warehouse | **MISSING** | Zero matches for stock/inventory/موجودی/انبار anywhere in backend. `qty` exists only on document lines |
| Frontend | REAL | `/app/products` wired + polished |

### Pillar 3 — Invoice types (انواع فاکتور) — **sale side BUILT, returns MISSING**

| Capability | Status | Evidence |
|---|---|---|
| Sale invoice: proforma / internal_private / tax_reportable | BUILT | `app/modules/invoice_drafts/` — statuses `draft/finalized/cancelled/archived`, `direction` fixed `"sale"`, full line model with snapshots, backend-authoritative Decimal totals |
| Lifecycle: finalize / cancel / archive / convert-to-tax-reportable / readiness | BUILT | endpoints + tests; finalize gated by readiness for tax_reportable |
| Print/PDF (A4, landscape, 80mm receipt) | BUILT | `print_service.py` + `pdf_service.py` (fpdf2); renders «ریال» (fixed 2026-07-04) |
| Purchase recording (lump-sum OR line-items) | BUILT | `app/modules/purchases/` — `payment_status paid|unpaid|partial`, `paid_amount` **entered on the purchase itself**, `purchase_lines` table |
| Expenses | BUILT | `app/modules/expenses/` — category, amount, method `cash|card|transfer` |
| **Return-from-sale (برگشت از فروش)** | **MISSING** | no concept anywhere |
| **Return-from-purchase (برگشت از خرید)** | **MISSING** | no concept anywhere |
| Service-invoice | BUILT implicitly | `product_type=service` + free lines cover it; no separate doc type needed |
| Frontend | REAL | `/app/invoices` list/new/detail (finalize, convert, PDF, readiness — the deepest real surface, ~1090 lines); `/app/purchases` (purchases+expenses tabs) |

### Pillar 4 — Treasury (خزانه‌داری) — **the big gap, matches founder's analysis exactly**

| Capability | Status | Evidence |
|---|---|---|
| Receipts/payments vs party aggregate | BUILT | `app/modules/payments/` — `party_type vendor|customer`, `amount`, `payment_date`, `payment_method cash|card|transfer`, note. Full CRUD `GET/POST /payments`, `GET/PATCH/DELETE /payments/{id}` |
| **Invoice↔payment linkage** | **MISSING** | Payment has **no `invoice_id`/`purchase_id`**; invoice_drafts has **no `paid_amount`/`payment_status`**. Settlement is aggregate-only. Backend progress explicitly logs this as the deliberately-deferred next task |
| **Combined settlement window on invoice** (نقد+کارت+چک+نسیه in one dialog) | **MISSING** | print_service comment: "No settlement method / credit / cash fields exist in the data model" |
| **Cheque lifecycle** (دریافت → واگذاری به بانک → وصول/برگشت → خرج) | **MISSING** | zero matches for cheque/چک in backend AND frontend |
| Bank accounts / cash box (صندوق) / POS terminal entities | **MISSING** | zero matches; `بانک` appears only as the «انتقال بانکی» method label |
| Installments (اقساط) / prepayment (پیش‌دریافت) / inter-account transfer | **MISSING** | zero matches |
| Frontend | REAL but **DUPLICATED** | `/app/payments` («دریافت و پرداخت», full CRUD) and `/app/transactions` («تراکنش‌ها», settlement cards + read-only history) — two sidebar entries, two pages, **one backend concept** (`listPayments`) |

### Pillar 5 — Accounting document & reports (سند و گزارش) — **MISSING**

| Capability | Status | Evidence |
|---|---|---|
| Journal / ledger / double-entry / سند حسابداری | MISSING | zero matches; scope-freeze explicitly excludes it for MVP |
| Reports (P/L, sales, VAT, معاملات فصلی) | MISSING | no reports module/router; contracts have a *planned* R1-P4 section only |
| Dashboard real aggregates | MISSING (placeholder) | `app/modules/dashboard/` docstring says "placeholder"; KPIs are **sha256-seeded fake numbers**, tasks/activity hard-coded |
| Frontend | honest STUB | `/app/reports` = honest «به‌زودی» empty state; dashboard readiness card real, KPI numbers stubs |

### Duplicate / mock surfaces a merchant can reach today (frontend)

| Surface | State | Action needed |
|---|---|---|
| `/app/payments` **vs** `/app/transactions` | Both REAL, same API, two names («دریافت و پرداخت» / «تراکنش‌ها») | **MERGE — the one true duplicate a merchant sees today** |
| `/app/sales`, `/app/accounting`, `/app/receipt-inbox`, `/app/payslips`, `/app/employees`, `/app/payroll` | Already neutralized → `beforeLoad` redirects | Keep; delete orphan components |
| Orphan mock components (zero refs): `sales/new-sale-sheet.tsx`, `payroll/payroll-run-sheet.tsx`, `dashboard/cashflow-sparkline.tsx`, `dashboard/tax-status-card.tsx` | Dead code importing `@/lib/mock/*` | Delete in cleanup step |
| `/app/tax/*` legacy tree (15 routes) + `src/features/tax/*` | ALL MOCK but **unreachable** (parent redirects to taxpayer-profile) | Delete or archive in cleanup (duplicate invoice concept) |
| `/app/assistant` | Real LLM chat, demo-only drafts (don't persist), hidden from sidebar | Leave hidden; out of phase |
| Moadian submit button | Disabled placeholder, no network call | Correct per R1B rule — unchanged |
| RBAC | owner/admin guard on member routes; **no role matrix on business data modules** (staff/viewer read-write like owner) | Flag — phase-1 candidate hardening (small) |

---

## PART B — Gap table vs Holoo/Sepidar

Effort: S ≤ 2 sessions · M ≈ 3–6 · L ≥ 7. "Merchant-facing?" = does the merchant see a screen
for it (vs behind-the-scenes).

| # | Capability | Holoo/Sepidar | We have today | Merchant-facing? | Effort | Phase 1? |
|---|---|---|---|---|---|---|
| 1 | Unified counterparty (one person = customer AND vendor) | Yes | Two separate models, balances each side | Yes (one «طرف حساب» list) | M | **OUT** — two lists are simpler for merchants; unify in accountant layer later |
| 2 | Vendor identity fields (کد ملی/اقتصادی) | Yes | Missing on vendors | Barely (optional fields) | S | **IN** (optional fields only — needed before معاملات فصلی) |
| 3 | Goods catalog + units + VAT | Yes | BUILT | Yes | — | Done |
| 4 | Inventory / stock / انبار | Yes (core) | MISSING | Yes | **L** | **OUT** — biggest scope; launch segment (services/small retail) survives without stock counts; phase 2 flagship |
| 5 | Sale invoice + proforma + internal | Yes | BUILT | Yes | — | Done |
| 6 | Purchase recording | Yes (purchase invoice) | BUILT (lump-sum + lines) | Yes | — | Done |
| 7 | **Return-from-sale (برگشت از فروش)** | Yes | MISSING | Yes | M | **IN** (financial-only; no stock effect since no inventory) |
| 8 | **Return-from-purchase (برگشت از خرید)** | Yes | MISSING | Yes | S–M | **IN** (same pattern, on purchases) |
| 9 | **Combined settlement window on invoice** (cash+card+cheque+credit in one step) | Yes (signature feature) | MISSING | Yes (THE selling moment) | M | **IN** — core of phase 1 |
| 10 | **Invoice↔payment linkage** (per-doc paid/status) | Yes | MISSING (aggregate only) | Yes (invoice shows «تسویه‌شده/نسیه») | M | **IN** — prerequisite of #9 |
| 11 | **Cheque lifecycle: receive → deposit → clear/bounce** | Yes (core) | MISSING (zero چک anywhere) | Yes («چک‌های من») | **L** (M backend + M frontend) | **IN** — founder's #1 competitor gap |
| 12 | Cheque endorsement (خرج چک به غیر) | Yes | MISSING | Yes | M | **OUT** — phase 2; needs stable cheque core first |
| 13 | Bank accounts + cash box (صندوق) entities | Yes | MISSING | Yes (simple «حساب‌های من») | M | **IN** (minimal: bank accounts + one auto cash box; POS = card→bank mapping) |
| 14 | Inter-account transfer (بانک↔صندوق) | Yes | MISSING | Yes | S | **IN** (trivial once #13 exists) |
| 15 | Installment schedule (اقساط) | Yes | MISSING (partial payments only) | Yes | M | **OUT** — phase 2; linkage (#10) already allows repeated partial settlements, which covers the merchant's real need |
| 16 | Prepayment (پیش‌دریافت/پیش‌پرداخت) | Yes | MISSING | Yes | S via design | **Half-IN** — design #10 so unallocated payments ARE prepayments (no extra UX in phase 1; explicit UX phase 2) |
| 17 | Auto accounting document (سند اتوماتیک) | Yes | MISSING (excluded by scope freeze) | **No** (accountant layer) | L | **OUT** — phase 2; phase 1 lays the event foundation (see split below) |
| 18 | Reports: simple P/L, sales, debtors/creditors, cheque due list | Yes | MISSING | Yes | M | **IN** (merchant set only) |
| 19 | Real dashboard KPIs | Yes | MISSING (seeded fakes) | Yes | S–M | **IN** — fake numbers are a credibility killer |
| 20 | VAT / معاملات فصلی reports | Yes | MISSING | Accountant-ish | M | **OUT** — needs Moadian/R1B context; phase 2 |
| 21 | Treasury surface de-duplication (payments vs transactions) | n/a | Duplicate | Yes | S | **IN** — step 0 |

---

## PART C — Phase-1 scope (bounded)

**Definition of phase 1:** after this phase, a merchant with no accountant can, alone: sell
(invoice), get paid the way Iranian trade actually works (cash + card + **cheque** + credit
remainder, in one window), track every cheque to vseen/bounced, record purchases/expenses,
see who owes them and whom they owe per document, and read honest simple reports — all in
calm Persian with zero accounting jargon.

### IN (in journey order — see Part D)
0. **De-dup & cleanup** — merge `/app/payments` + `/app/transactions` into one surface; delete orphan mocks + unreachable `/app/tax/*` mock tree. *(Reason: principle 3 — zero duplicates before adding features.)*
1. **حساب‌های من (treasury accounts)** — bank accounts + auto-created «صندوق» + transfer between them. *(Reason: cheque deposit and settlement need a "where did the money land".)*
2. **Invoice↔payment linkage** — `payment.invoice_id`/`purchase_id` (nullable = on-account/prepayment), derived `paid_amount`/`settlement_status` on invoices. *(Reason: prerequisite of everything; already queued in backend docs.)*
3. **Combined settlement window** — on finalize (and later, from invoice detail): split amount across نقد/کارت/انتقال/چک, remainder = نسیه automatically. *(Reason: the Holoo signature moment; #9.)*
4. **Cheque lifecycle** — received & issued cheques; states در جریان → واگذار به بانک → وصول‌شده / برگشتی; due-date surfacing. *(Reason: founder's #1 gap.)*
5. **Returns** — برگشت از فروش (against a finalized invoice), برگشت از خرید (against a purchase); financial effect only. *(Reason: #7/#8; no inventory yet so pure balance/report effect.)*
6. **Real dashboard + merchant reports** — replace seeded KPIs with real aggregates; reports page: سود و زیان ساده، فروش، بدهکاران/بستانکاران، چک‌های نزدیک سررسید. *(Reason: honesty + daily value.)*
7. **Small hardenings riding along:** vendor optional identity fields; migrate purchase `paid_amount` entry to linkage-based payments (single source of truth); role matrix (staff/viewer read-only) if cheap.

### OUT (deferred, one-line reasons)
- **Inventory/انبار** — L-effort flagship of phase 2; launch segment tolerates absence; adding it later doesn't break phase-1 data.
- **Auto سند حسابداری / journal / ledger / chart of accounts** — scope-freeze exclusion stands; phase 1's typed financial events (invoice, payment-with-allocation, cheque transitions, returns, transfers) ARE the journal source; a phase-2 generator replays them into proper double-entry for the accountant layer. Nothing merchant-visible ever shows debit/credit.
- **Cheque endorsement (خرج چک)** — phase 2 on top of stable cheque core.
- **Installment schedules (اقساط)** — phase 2; partial settlements already cover the need.
- **Explicit prepayment UX** — phase 2; model supports it from day 1 (unallocated payments).
- **Unified counterparty merge** — accountant-layer concern; two simple lists are more merchant-friendly today.
- **VAT/معاملات فصلی reports** — phase 2 with R1B context.
- **Moadian real submit (R1B)**, **Excel import (E)**, **subscriptions/paywall** — separate tracks, unchanged.

### Merchant / accountant layer split (recommendation)
- **Merchant layer (phase 1, everything above):** task language only — «فروختم / پول گرفتم / چک دادم / کی به من بدهکاره». No debit/credit, no ledger, no "سند".
- **Accountant layer (phase 2):** read-only journal generated from phase-1 events + Excel/CSV export + ledgers/trial balance. Gate: role `accountant` (new) or owner opt-in «نمای حسابدار». Phase 1's only obligation: **don't destroy information** — every money movement is a typed, immutable-after-finalize row with party, document link, treasury account, and timestamp. The audit confirms current models already satisfy this except where phase 1 adds the missing links.

---

## PART D — User-journey-ordered build sequence (phase 1)

Ordered by the merchant's natural day, so each step ships a complete story. Every step: Persian
labels locked here; ui-ux-pro-max pass = full skill pass (layout, states, motion, a11y, 390px,
dark) to the customers-page bar — not a token repaint.

**Step 0 — «یک مفهوم، یک صفحه» cleanup (S)**
- Merge `/app/transactions` into `/app/payments` under the single name **«دریافت و پرداخت»**, one sidebar entry in group «مالی»: open-settlement cards (from transactions) on top, history + CRUD (from payments) below. Redirect `/app/transactions` → `/app/payments`.
- Delete orphan mocks (`new-sale-sheet`, `payroll-run-sheet`, `cashflow-sparkline`, `tax-status-card`) and the unreachable `/app/tax/*` + `features/tax` mock tree (git history preserves it).
- **Duplicate-avoidance:** after this, treasury has exactly one surface; invoices already have exactly one.

**Step 1 — «حساب‌های من» (M)**
- New small screen (inside تنظیمات or مالی): add bank account (نام بانک، چهار رقم آخر — no IBAN validation burden in v1), auto «صندوق» created per business, optional POS→bank mapping. Transfer dialog «جابه‌جایی بین حساب‌ها».
- Persian: «حساب بانکی»، «صندوق»، «کارت‌خوان». UX: card list, one primary action, empty state explains why this helps («تا بدونید هر پولی کجا نشسته»).
- **Duplicate-avoidance:** payment_method stays the *how*; account is the *where*. One concept each.

**Step 2 — Invoice settlement core (M, backend-first)**
- Backend: `payments.invoice_id`/`purchase_id` (nullable), `payments.account_id`, derived invoice `paid_amount` + `settlement_status ∈ تسویه‌شده/تسویه جزئی/نسیه`; recomputes reuse existing functions. Migrate purchases' self-entered `paid_amount` to real payment rows (one-time data migration).
- Frontend: invoice detail + list show settlement chip; «ثبت دریافت برای این فاکتور» from the invoice itself.
- Locked rules (scenario review): cancel-finalized is BLOCKED while linked receipts/cheques exist (guided message, never auto-unlink); per-party receipts auto-allocate oldest-first (FIFO) — the per-invoice entry point IS the manual override; pre-existing payment rows backfill account=صندوق in this migration.
- **Duplicate-avoidance:** the aggregate «تسویه کامل» flow and the per-invoice flow both create the SAME payment rows — one model, two entry points.

**Step 3 — Combined settlement window (M)**
- On finalize (optional, skippable) and from invoice detail: one calm dialog «دریافت وجه» with split rows: نقد / کارت / انتقال / چک (+ حساب مقصد per row), live remainder line «باقی‌مانده به‌صورت نسیه: …». Mobile-first; each row optional; zero rows = pure نسیه.
- **PROGRESSIVE design constraint (locked, decision 16):** the default face is ONE question — «چقدر دریافت کردید؟» — with نقد preselected; کارت/انتقال/چک/split live behind «روش‌های بیشتر». The one-dialog architecture stays (anti-duplicate); only its default state must be as simple as a cash sale. ui-ux-pro-max owns this dialog's design. Walk-in (no-customer) mode hides the نسیه remainder entirely.
- Purchases get the mirrored «پرداخت وجه» window.
- Unit labels per Stage-A2 rules (display unit + always-visible label).

**Step 4 — Cheques (L)**
- Backend: `cheques` table (direction received/issued, party, amount, due_date صیادی serial optional, bank, status enum «در جریان / واگذار به بانک / وصول‌شده / برگشتی», linked payment row created on وصول). State transitions as explicit endpoints; bounce reverses settlement effect.
- Frontend: «چک‌ها» screen (sidebar, group مالی): two tabs دریافتی/پرداختی, cards sorted by سررسید, big status pills, actions per state («به بانک سپردم» → «وصول شد / برگشت خورد»). Cheque as a row type inside the Step-3 window.
- Dashboard strip: «چک‌های نزدیک سررسید».
- **Duplicate-avoidance:** a cheque is NOT a payment until cleared — the payment row is created by the وصول transition, so «دریافت و پرداخت» history never double-counts.

**Step 5 — Returns (M)**
- «برگشت از فروش» action on a finalized invoice (select lines/amounts → return doc, reduces receivable + reports); «برگشت از خرید» mirrored on purchases. New doc numbers, printable.
- Persian: «برگشت از فروش»، «برگشت از خرید» (the canonical trade terms). Financial-only note shown to no one — merchants don't care; accountant layer will.
- **Duplicate-avoidance:** returns live INSIDE the invoice/purchase detail as actions + a filter on the lists — no separate «returns» menu item.

**Step 6 — Real dashboard + reports (M)**
- Backend: real aggregation endpoints (replace seeded dashboard; new reports endpoints: P/L simple, sales by period/customer/product, debtors/creditors, cheque due list).
- Frontend: dashboard KPIs real («فروش این ماه»، «طلب شما»، «بدهی شما»، «موجودی حساب‌ها»); `/app/reports` becomes real with 4 simple cards, each one chart + one table max.
- **Duplicate-avoidance:** dashboard = glance, reports = depth; no number appears in both with different definitions (single backend source per figure).

**Step 7 — Phase close:** E2E specs for the new flows (incl. refreshing the 6 drifted specs), reseed test accounts, progress docs, founder live proof, push ritual.

Sequence rationale: 0 removes confusion before anything new; 1→2→3 follow the money in the
order the merchant meets it (where money lives → which invoice it settles → the one dialog that
does it); 4 extends the same dialog with Iran's dominant instrument; 5 handles the unhappy path
of the same documents; 6 shows the truth the merchant built up in 1–5.

---

## PART E — Open questions for the founder

> **All 9 answered (2026-07-04).** Decisions live in `phase1_user_scenarios_v1.md` → "Decisions
> locked" table (rows 1–16). Kept below for the historical record only.

1. **Inventory:** confirmed OUT of phase 1? (Biggest conscious divergence from Holoo/Sepidar parity; phase-2 flagship.)
2. **Cheque realism depth:** is bank-name + due date + optional صیادی serial enough for v1, or do you need صیاد-registration semantics day 1? (Recommend: minimal fields v1.)
3. **Purchases `paid_amount` migration:** OK to migrate purchase-entered paid amounts into real payment rows (single source of truth), with a one-time data migration on existing rows? (Recommend: yes.)
4. **Merged treasury name:** keep «دریافت و پرداخت» for the single merged surface? (Recommend: yes; «خزانه‌داری» stays out of merchant vocabulary.)
5. **Delete vs archive** the unreachable `/app/tax/*` mock tree and orphan mock components? (Recommend: delete; git history is the archive.)
6. **Accountant layer trigger:** phase 2 as a role (`accountant` member role) or as an owner-visible «نمای حسابدار» toggle? (Affects nothing in phase 1; sets direction.)
7. **Role matrix:** should staff/viewer become read-only on financial modules inside phase 1 (small), or defer with members work already done in Stage B? 
8. **Subscriptions/paywall:** scope-freeze marks it P0-before-launch but it's outside the 5 pillars — separate parallel track after phase-1 approval, or inserted into phase 1?
9. **Settlement window on finalize:** mandatory step or skippable (recommend skippable — «بعداً تسویه می‌کنم» keeps the نسیه path one tap)?

---

*Plan ends. Approved 2026-07-04 with the scenario catalog; all decisions closed. Next: Step-0
build prompt (de-dup cleanup) on founder go.*
