# Digi Invoice / DigiTax — Engineering Execution Blueprint

**Version:** 1.2 (engineering companion to Product Master Blueprint v4.2)
**Language:** English skeleton · Persian UI/UX content
**Audience:** Founder (PO), Claude Code, backend / frontend / ops sessions
**Status:** Canonical execution plan. Sits *below* the product master doc (v4.2,
the "why"), and *above* per-repo execution plans (the "how/when").

---

## PART 0 — How to read this document

This blueprint is the bridge between **product intent** and **working code**.

- **Product intent** lives in `product_master_blueprint_v4_2.md` (the strategy,
  personas, journeys, scope philosophy). That answers *what and why*.
- **Real code state** lives in `reality_audit.md` (audited 2026-06-17). That is
  ground truth for *what exists today*.
- **This document** answers *how, in what order, with which model, and how we
  prove each step is done* — without repos diverging.

**Intent-vs-code rule:** When the master doc claims a feature state that the code
contradicts, the **code + OpenAPI win**, and this blueprint records the real
state. (Example: master doc implied dashboard was real; audit proved it returns
hash-seeded fake numbers. This doc treats dashboard as SKELETON.)

**Bilingual policy:** Engineering structure, field names, endpoints, and rules
are in English (so they match code and CLAUDE.md). All user-facing words, UI
copy, and error messages are Persian. The two never mix inside a sentence.

---

## PART 1 — Operating Model (how we actually work)

This is the discipline that protects your time and tokens. It is not optional —
every phase below assumes it.

### 1.1 Two surfaces, two jobs
- **claude.ai (Opus, this surface):** decisions only — architecture, cross-repo
  design, phase planning, contract design. Short, high-value conversations.
- **Claude Code (Sonnet, on your machine/server):** all execution — reading code,
  writing code, running audits, running tests. The heavy work lives here.

Never do bulk coding on claude.ai. Never make architecture decisions blindly
inside a Claude Code session without a phase plan from here.

### 1.2 One chat per phase (cross-chat memory = this document)
Claude has no live memory between chats, and a long chat gets expensive because
the whole history is reprocessed every turn. Therefore:
- **Each major phase gets a fresh claude.ai chat.** When a phase closes, close
  the chat.
- This blueprint (in the repo) is the memory that survives across chats. A new
  chat starts by reading the relevant phase here — nothing needs re-explaining.

### 1.3 Builder / Auditor cycle (the core loop)
Every implementation phase runs as:
1. **Plan** (claude.ai, Opus): confirm the phase, contract, file list.
2. **Build** (Claude Code, Sonnet): implement per the phase spec.
3. **Audit** (Claude Code, subagent): a *separate* pass verifies correctness
   against the DoD. Builder and Auditor are different runs so the auditor reviews
   with fresh eyes.
4. **Test** (Claude Code, on test server / browser MCP): prove it works with real
   seeded data.
5. **Close**: update `progress.md` + `phase_roadmap.md`, commit, open fresh chat.

### 1.4 Model & effort discipline (token control)
Each task in PART 5 carries an explicit **model** and **effort**. Defaults:
- **Sonnet** for almost everything: implementation, audits, reports, browser QA.
- **Opus** only for genuine cross-repo architecture or contract design — rare.
- **effort low/medium/high** signals how much reasoning depth to spend. Most
  audits are `low`. Most implementation is `medium`. `high` is exceptional.

If you ever find yourself about to run Opus for routine implementation — stop.
That is the single biggest source of token waste.

### 1.5 Skills, subagents, MCP (already built — make them mandatory)
You already have these across the repos. This blueprint makes them required gates,
not optional helpers:
- Session start: `/start-digi-session`
- Implement: `/implement-backend-task` · `/implement-frontend-task`
- Contract checks: `/check-openapi-contract` · `/check-api-contract`
- Pre-commit: `/review-digi-diff` · `/review-ops-diff`
- Subagents: `backend-contract-auditor`, `api-contract-guardian`,
  `frontend-ux-auditor`, `browser-qa-auditor`, `ops-deploy-auditor`,
  `blocker-ledger-auditor`
- Browser MCP: `/browser-qa-digi` (real browser — RTL, mobile, flow, console).

### 1.6 Test server & deploy rhythm
A test server hosts all three repos. **Never hardcode its address in git.** Refer
to it via shell/env only (e.g. `$DIGI_TEST_SSH`, `$DIGI_TEST_PATH`). Key-based
SSH, no password.

Standard deploy rhythm on the test server (the owner's proven sequence):
```
# from the repo(s) that changed:
git pull
# for each changed app repo, rebuild its image:
docker-compose build api          # if backend changed
docker-compose build --no-cache frontend   # if frontend changed
# bring the stack up:
docker-compose up -d
# if the DB schema changed:
docker-compose exec api python -m alembic upgrade head
# verify:
bash scripts/smoke_test.sh
```
Backend and frontend can both run on the test server. Frontend may alternatively
run locally on the laptop via `pnpm` for fast UI iteration. Migrations always run
inside the api container.

### 1.7 Security guardrails (always)
- Never commit the test server IP, SSH details, keys, proxy URLs, or secrets.
- Secrets never returned to frontend or printed in logs (redact in tickets/logs).
- These apply in every phase regardless of what the phase is about.

---

## PART 2 — Canonical Engineering Rules (single source)

These are the non-negotiables. The three repo `CLAUDE.md` files should **point
here** instead of repeating them, to cut token cost and prevent drift. Repo files
keep only repo-specific detail (commands, module layout, route patterns).

1. **Money = Decimal/string only. Never float.** Backend computes all money.
   `Numeric(20,4)` for amounts, `Numeric(7,4)` for rates. JSON decimals as
   strings unless a contract says otherwise. *(Audit confirmed: currently clean.)*
2. **Backend owns contracts.** Frontend never invents endpoints, fields, status
   values, or sends `tenant_id`/`business_id` unless the contract defines it.
3. **Frontend API base already includes `/api/v1`.** Call relative paths
   (`/customers`, not `/api/v1/customers`).
4. **No fake official statuses.** Never fabricate Moadian `referenceNumber`,
   `taxid`, `submitted`, `accepted`. Not really sent = not submitted.
   *(Audit confirmed: currently honored — real submit returns 503, no fakes.)*
5. **Internal records never blocked by tax readiness.** Customers, products,
   internal/draft records work without taxpayer approval. Readiness gates only
   the official path.
6. **Persian digit normalization:** UI may show Persian/Arabic digits;
   persistence is ASCII only. Normalize before saving.
7. **No raw backend/Pydantic/JSON errors in UI.** All errors human, Persian,
   inline, friendly.
8. **Tenant isolation mandatory.** Every tenant-scoped query filters by
   `active_business_id` from the token. No cross-business leakage.
   *(Audit confirmed: currently enforced.)*

### Identity field rules (exact)
- `taxpayer_type`: `individual` | `legal`
- individual `national_id`: exactly 10 digits
- legal `national_id`: exactly 11 digits
- `economic_id`: exactly 12 digits
- Draft: empty allowed; if provided, must be exact-valid.
- Submit: all required identity fields present.

### Status honesty rule
Do not mark a skeleton (exists but not product-complete) as `done`. Skeletons are
`partial`. `phase_roadmap.md` holds true status.
---

## PART 3 — Module Catalog (all 20 modules, real state from audit)

Nothing is dropped. State column is ground truth from `reality_audit.md`.
Owner = repo(s) that own the work. Release = when it becomes product-complete.

| # | Module | Real state (audit) | Owner | Release |
|---|--------|-------------------|-------|---------|
| 1 | Auth / Identity | REAL (OTP in-memory — needs Redis) | backend, frontend | 1A (Redis: 1A-P0) |
| 2 | Business / Tenant | REAL | backend, frontend | done |
| 3 | Onboarding | PARTIAL (no real wizard) | frontend (+be contract) | 1A-P1 |
| 4 | Customers / Parties | REAL | backend, frontend | done (extend: supplier in 1A-P4) |
| 5 | Products / Catalog | REAL | backend, frontend | done |
| 6 | Sales / Invoicing | REAL (full lifecycle, print, PDF) | backend, frontend | done (polish only) |
| 7 | Purchases | NONE | backend, frontend | 1A-P4 |
| 8 | Expenses | NONE | backend, frontend | 1A-P4 |
| 9 | Receipts / Payments | NONE | backend, frontend | 1A-P5 |
| 10 | Reports (sales/purchase/expense/profit) | NONE | backend, frontend | 1A-P6 |
| 11 | Tax Readiness | REAL (invoice readiness) | backend, frontend | done (extend per module) |
| 12 | Moadian / Submission | PARTIAL — real submit **BLOCKED** (crypto unconfirmed, returns 503; no fake status) | backend, frontend | 1B |
| 13 | Subscriptions / Billing / Paywall | NONE | backend, frontend | 1A-P7 |
| 14 | Admin Operations | PARTIAL (review real; ops console incomplete) | backend, frontend | 1A-P8 → 1B |
| 15 | Accountant / Partner | NONE | backend, frontend | 1C |
| 16 | Smart Input (Excel/OCR/Voice) | NONE | backend, frontend | 1C (Excel) → 2 |
| 17 | Accounting Automation | NONE (reports only in 1A) | backend | 2 |
| 18 | Payroll / Salary Tax | NONE (gated mock pages exist) | backend, frontend | 2 |
| 19 | Notifications / Tax Calendar | NONE | backend, frontend | 1C |
| 20 | Support / Tickets | NONE (placeholder admin pages) | backend, frontend | 1C |

**Skeletons to clean up (audit findings):** `/identity/login`, `/identity/me`
(placeholder tokens), `/tenants/*` (deprecated placeholders), `/taxpayers/*`
(410 but still registered), `/fiscal-memories/{id}` (hardcoded). These pollute
OpenAPI — removed/marked in 1A-P0.

**Mock frontend pages (audit):** sales, purchases, transactions, vendors,
reports, receipt-inbox, assistant, accounting, payroll, employees, payslips, most
`/app/tax/*`. Each is either replaced (when its phase lands) or locked/hidden
(1A-P9). No mock page ships as if it were real.

---

## PART 4 — Flows & User Journeys

The product's soul is the journey: **welcoming, simple, beautiful, smart.** A user
is won by how *effortless and pleasant* it feels — they should enjoy exploring
because it's so simple and intelligent. This is a measurable DoD criterion in
every frontend phase, not a vague wish.

### 4.1 Journey principles (apply to every screen)
- **One clear next action** per screen. Never present a wall of options.
- **Progressive disclosure:** hard tax fields appear only when the user chooses
  the official path. Bookkeeping stays light.
- **Welcoming tone:** Persian, friendly, never bureaucratic or scary. Avoid
  government/tax jargon for merchants (v4.2 §14.2 forbidden-words list).
- **Reward on progress:** completing a step visibly unlocks the next capability,
  and the user understands *why* (Progressive Activation, v4.2 §8).
- **Beauty + RTL + mobile-first** are baseline, not polish.

### 4.2 Internal state vs UI words (the vocabulary contract)
Backend uses internal states; UI shows Persian words. Never leak internal terms.

| Internal | UI (Persian) |
|----------|--------------|
| financial_event | رویداد مالی |
| internal_record | سند داخلی |
| proforma | پیش‌فاکتور |
| invoice | فاکتور |
| tax_reportable_invoice | سند آماده مالیات |
| submitted_invoice | سند ارسال‌شده رسمی |
| readiness / blocker / warning | آمادگی / مورد ضروری / هشدار |
| submitted / accepted / rejected | ارسال‌شده / پذیرفته‌شده / ردشده |
| referenceNumber | شماره پیگیری سامانه |
| fiscal memory | حافظه مالیاتی |
| tax item id (sstid) | شناسه کالا/خدمت |

### 4.3 Core journeys as state machines (per active module)

**Onboarding (1A-P1):**
`login (OTP) → no business → short create form (name, activity, person type,
city) → business created → Stage 1 dashboard → "add first customer/product" →
"record first sale" → see first output.` Each arrow shows one clear action.
Backend: businesses (REAL) + a lightweight onboarding-state read. Frontend: the
wizard + activation UI. *No heavy forms on day one.*

**Sale (REAL — polish only):**
`record sale → pick/quick-create customer → add product (smart line) → totals →
save as internal | proforma | (later) tax-reportable → PDF/print → effects on
sales report + customer balance.` Already implemented; this blueprint only
guards the journey quality.

**Purchase (1A-P4) — full state machine:**
States: `draft → saved_internal → (optional later) tax_reportable`.
```
[tap "ثبت خرید"]
  → pick supplier (existing) OR quick-create inline (name+mobile minimum)
  → add items: smart-line search of tenant products
       ├─ product found → add as line
       ├─ not found → free line (raw title) — allowed, no blocker
       └─ no item detail → lump-sum amount instead of lines
  → quantities, unit price, optional discount, optional simple purchase VAT
  → set payment status (paid / unpaid / partial)
  → [save] → saved_internal
       ├─ effect: supplier balance += unpaid amount
       ├─ effect: purchase report (month) updated
       └─ effect: real profit recomputed (sales − purchases − expenses)
```
Responsibility split — **backend:** persist purchase + lines (Decimal), recompute
supplier balance + totals in service, tenant-scoped. **frontend:** the form, smart
line, inline supplier create, payment-status control, friendly Persian validation.
Tax fields hidden by default (internal-only); shown only if user later chooses the
official path. Error cases (all human Persian, inline): empty supplier on a
balance-bearing purchase, non-numeric amount (after digit normalization), negative
total. Mirrors the proven sale flow's feel.

**Expense (1A-P4) — full state machine:**
States: `draft → saved`.
```
[tap "ثبت هزینه"]
  → pick simple category (اجاره، حقوق، حمل‌ونقل، تبلیغات، کارمزد، …) — NOT a
    chart-of-accounts; just friendly buckets (v4.2 §9.8)
  → amount + date
  → optional: payment method, related supplier/party, note, attachment (later)
  → [save] → saved
       ├─ effect: real profit recomputed
       └─ effect: expense report (by category, month) updated
```
Responsibility split — **backend:** persist expense (Decimal), category enum,
recompute profit aggregate, tenant-scoped. **frontend:** category picker (zero
accounting jargon), amount field with digit normalization, one clear action.
Error cases (Persian): missing category, missing/zero amount, future-dated beyond
allowed range. No accounting terms ever shown to the merchant.

**Receipt / Payment (1A-P5) — full state machine:**
Separates money from document (v4.2 §9.9). States per movement: `recorded`;
per linked document: `unpaid → partial → settled`.
```
[open invoice OR purchase that carries a balance]
  → [tap "ثبت دریافت" (from customer) | "ثبت پرداخت" (to supplier/expense)]
  → enter amount (full or partial) + method + date
  → [save] → movement recorded
       ├─ if amount < balance → document = partial, remaining shown
       ├─ if amount = balance → document = settled
       ├─ effect: party balance reduced by amount
       └─ effect: simple cash-flow (in/out today/month) updated
```
Responsibility split — **backend:** record movement (Decimal), apply to the
correct document, recompute party balance + cash-flow, tenant-scoped, partial
logic in service. **frontend:** record dialog from a document, partial amount
support, clear "who still owes / what's still due" view. Error cases (Persian):
amount exceeds remaining balance, amount ≤ 0, no linked document.

**Tax-reportable conversion (existing + per module):**
`user taps "آماده‌سازی مالیاتی" → readiness check → show blockers/warnings in
Persian → user completes missing fields → becomes tax-reportable → still NOT
submitted until real Moadian send (1B).` Never silent, always user-driven,
readiness-gated, no fake status.

**Moadian submission (1B):**
`tax-reportable doc → readiness hard-check → build payload → sign/encrypt →
real send → store real referenceNumber → schedule inquiry → show status.`Blocked today (crypto 503); unblocks in 1B with confirmed crypto.

### 4.4 Admin journey (operational brain, not just review)
`admin login (is_system_admin) → dashboard (real counts) → review queue →
approve/reject with Persian reason → audit log → (1B) submission health, retry →
(1C) partner/accountant management, tickets.` Admin must diagnose without seeing
secrets (redacted views).

### 4.5 Deferred journeys (intentionally not detailed yet)
Smart Input (Excel import, OCR photo→draft, Voice) and Accountant/Partner journeys
exist in the Master doc (§9.15–9.16) but belong to Release 1C / 2. Per our own
"detail-the-phase-when-we-open-it" rule, their full state machines are written at
the **start of 1C**, not now — writing them six phases early would only produce
detail that drifts before use. Principle locked: all channels (Excel/OCR/Voice)
feed a **staging** area; no AI/OCR output ever becomes an official document
without explicit user confirmation (Master §9.16).
---

## PART 5 — Phased Execution Roadmap

Order matters and is causal. Reports come *after* purchases/expenses (else profit
is fake — v4.2 §13.3). Each phase uses the standard template (rationale, scope,
per-repo work, model/effort, DoD, contract, exit). One phase = one chat.

> **Phase template legend:** every phase lists Builder/Auditor **model + effort**,
> a per-repo DoD checklist, and a cross-repo contract table. Open a fresh chat per
> phase; reference this blueprint.

---

### RELEASE 1A — Sellable Merchant Core

Goal: the first version you can actually sell to a merchant/small company. Real
profit needs sales + purchases + expenses. Keep purchases/expenses *simple*.

---

#### R1A-P0 — Production hardening & skeleton cleanup
**Why:** Audit found 3 launch blockers + skeletons polluting OpenAPI. Fix the
cheap, high-risk items before building features on top.
**Scope (in):** OTP → Redis (audit: in-memory, lost on restart); CORS lockdown
for staging/prod (audit: wildcard); remove/mark dead routes (`/identity/*`,
`/tenants/*`, `/taxpayers/*`, `/fiscal-memories/{id}` stub); confirm Alembic
applies cleanly on test server.
**Scope (out):** Nginx/TLS (separate ops task when domain is ready).
- **Backend:** Redis-backed OTP service replacing `DevOTPService`; env-driven CORS
  origins; delete/deprecate dead routers. Builder **Sonnet/medium**; Auditor
  `backend-contract-auditor` **Sonnet/low**.
- **Ops:** confirm Redis wired + used; smoke test covers OTP across restart.
  Builder **Sonnet/low**; Auditor `ops-deploy-auditor` **Sonnet/low**.
**DoD:** OTP survives api restart (Redis); CORS not wildcard in staging; dead
routes gone from OpenAPI; migrations clean on test server; smoke passes.

---

#### R1A-P1 — Onboarding wizard (contract + UI)
**Why:** Audit: onboarding PARTIAL, no real wizard. This is the welcoming first
impression — the journey that wins the user (v4.2 §8, §9.3).
**Scope (in):** short create-business flow (name, activity, person type, city);
post-create activation dashboard with "one clear next action"; progressive unlock
copy. **Scope (out):** heavy legal/tax fields (those are Stage 3 / taxpayer
profile, already PARTIAL).
- **Backend:** lightweight onboarding/activation-state read (derive from existing
  business + profile data; no fake numbers). Contract entry first. Builder
  **Sonnet/medium**; Auditor `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** the wizard + activation UI; welcoming, RTL, mobile-first, one
  action per step. Builder **Sonnet/medium**; Auditors `frontend-ux-auditor`
  **Sonnet/low** + `browser-qa-auditor` **Sonnet/medium**.
**DoD:** new user reaches "first business created" in < 1 min, < 1 screen of
fields; next action always obvious; RTL+mobile verified in browser; no fake data;
**journey feels welcoming/simple (browser-qa explicit check).**

---

#### R1A-P2 — Subscription / plan foundation (contract)
**Why:** v4.2 §9.13 + §11.3: product must have plan/paywall before launch. Audit:
NONE. Build the *foundation* (data + read), not full billing yet.
**Scope (in):** plan model (Free Trial, Starter, Professional, Accountant),
tenant→plan link, feature-gate read API, friendly paywall data (value, what
unlocks). **Scope (out):** real payment gateway, commission engine (1C).
- **Backend:** plans + subscription tables (migration); `GET /subscription`,
  feature-gate resolver. Decimal for prices. Contract first. Builder
  **Sonnet/medium**; Auditor `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** paywall component (non-annoying, explains value + which plan +
  what's lost), upgrade CTA. Builder **Sonnet/medium**; Auditor
  `frontend-ux-auditor` **Sonnet/low**.
**DoD:** plans seeded; feature-gate read works; paywall explains value clearly in
Persian; no payment claims that aren't real.

---

#### R1A-P3 — Plan enforcement (backend gates)
**Why:** A plan foundation without enforcement is decorative. Audit: none.
**Scope (in):** enforce limits (invoice count, customers/products caps, feature
access) at the API layer; return structured, translatable limit errors.
- **Backend:** enforcement middleware/guards; structured `402/403`-style payloads
  the frontend can translate. Builder **Sonnet/medium**; Auditor
  `api-contract-guardian` **Sonnet/low**.
- **Frontend:** map limit errors to friendly Persian paywall prompts. Builder
  **Sonnet/low**; Auditor `frontend-ux-auditor` **Sonnet/low**.
**DoD:** hitting a limit shows a clear Persian upgrade prompt, never a raw error;
enforcement is server-side (not bypassable from frontend).

---

#### R1A-P4 — Purchases & Expenses baseline
**Why:** Real profit = sales − purchases − expenses. Audit: both NONE; mock
pages exist. v4.2 §10.1 requires these for a sellable core. Keep simple (no
inventory).
**Scope (in):** simple purchase (supplier, lines|lump-sum, total, payment status,
date, simple purchase VAT); simple expense (category, amount, payment method,
date); effects on supplier balance + reports + real profit. Internal by default,
never readiness-blocked. **Scope (out):** multi-warehouse, formal inventory,
landed cost, OCR, recurring (later).
- **Backend:** `purchases`/`purchase_lines` + `expenses` tables (tenant_id FK +
  index); CRUD mirroring proven `invoice_drafts` patterns; balances via service.
  Migration. Contract first. Builder **Sonnet/medium**; Auditor
  `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** replace `mock/purchases.ts` + expense mocks with real API
  modules; inline supplier quick-create; category picker (no accounting jargon);
  progressive tax-field disclosure. Builder **Sonnet/medium**; Auditors
  `frontend-ux-auditor` **Sonnet/low** + `browser-qa-auditor` **Sonnet/medium**.
- **Ops:** run migration on test server; smoke covers purchases+expenses.
  **Sonnet/low**.
**DoD:** no mock on live path; tenant-safe; Decimal everywhere; supplier balance
correct in seeded test; RTL+mobile flow verified; friendly Persian errors;
typecheck+build+pytest+ruff+black pass.

---

#### R1A-P5 — Receipts & Payments baseline
**Why:** v4.2 §9.9 — money is separate from the document; a sale may be paid
later. Needed for accurate balances & cash flow. Audit: NONE.
**Scope (in):** record receipt (from customer) / payment (to supplier/expense),
full or partial; link to invoice/purchase; update balances; simple cash flow.
**Scope (out):** bank integration, reconciliation, POS.
- **Backend:** `receipts`/`payments` (or unified `cash_movements`) tenant-scoped;
  partial settlement logic; balance updates via service. Migration. Contract
  first. Builder **Sonnet/medium**; Auditor `backend-contract-auditor`
  **Sonnet/low**.
- **Frontend:** record receipt/payment from a document with balance; partial
  amounts; clear "who still owes" view. Replace `transactions` mock. Builder
  **Sonnet/medium**; Auditors `frontend-ux-auditor` **Sonnet/low** +
  `browser-qa-auditor` **Sonnet/medium**.
**DoD:** partial payment reduces balance correctly (seeded test); cash-flow view
real (no fakes); RTL+mobile verified; friendly errors.

---

#### R1A-P6 — Real dashboard & reports
**Why:** Audit: dashboard returns hash-seeded **fake** numbers while the frontend
shows them as if real — a trust risk. Reports module NONE. Only now (after
purchases/expenses/payments) can profit be real (v4.2 §13.3).
**Scope (in):** replace fake dashboard service with live DB aggregates; reports —
sales today/month, purchase month, expense month, simple real profit, customer/
supplier debts, unpaid invoices. **Scope (out):** P&L deep, VAT draft (1C),
legal ledgers (R2).
- **Backend:** real aggregation queries (Decimal); replace `build_dashboard_
  summary` stubs; reports endpoints. Contract first. Builder **Sonnet/medium**;
  Auditor `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** wire dashboard + reports to real data; replace `reports`/
  `summary`/`tasks`/`activity` mocks; `toPersianDigits` on all figures. Builder
  **Sonnet/medium**; Auditors `frontend-ux-auditor` **Sonnet/low** +
  `browser-qa-auditor` **Sonnet/medium**.
**DoD:** **no fake numbers anywhere**; dashboard ties to real records; profit =
sales − purchases − expenses on seeded data; figures in Persian digits.

---

#### R1A-P7 — Subscription paywall UX completion
**Why:** Tie P2/P3 together into the real upgrade journey before launch.
**Scope (in):** plan comparison, trial limits visible, upgrade flow UX (payment
may still be manual/placeholder if no gateway yet — but never fake "paid"
status). **Scope (out):** automated gateway (1C if needed).
- **Frontend:** plan/paywall journey, clear value framing. Builder
  **Sonnet/medium**; Auditor `frontend-ux-auditor` **Sonnet/low**.
- **Backend:** subscription status transitions (honest states only). Builder
  **Sonnet/low**; Auditor `backend-contract-auditor` **Sonnet/low**.
**DoD:** user understands what unlocks before paying; no fake paid status; trial
limits clear.

---

#### R1A-P8 — Admin operations minimum
**Why:** Audit: admin PARTIAL — many placeholder pages (invoices, submissions,
plans, tickets, audit logs). Bring the *minimum* real admin for launch.
**Scope (in):** real admin views for users, businesses/tenants, taxpayer profiles
(exists), plans/subscriptions (from P2), basic audit log read. Fix pagination bug
(audit §7.7: admin profile `total` counts page, not all rows). **Scope (out):**
submission health/retry (1B), partner mgmt, tickets (1C).
- **Backend:** real admin list endpoints + correct pagination totals; audit log
  read. Builder **Sonnet/medium**; Auditor `backend-contract-auditor`
  **Sonnet/low**.
- **Frontend:** replace placeholder admin pages with real ones (or lock the
  not-yet-real ones honestly). Builder **Sonnet/medium**; Auditor
  `frontend-ux-auditor` **Sonnet/low**.
**DoD:** admin can manage users/businesses/profiles/plans with real data;
pagination totals correct; placeholders either real or honestly locked.

---

#### R1A-P9 — Hide/lock mock pages & launch gate
**Why:** v4.2 DoD: no mock page ships as a real feature. Audit lists ~15 mock
pages. Ensure none are reachable as if real.
**Scope (in):** verify `RouteAccessGate` (P3.5.8.1) hides/locks every not-yet-real
page (sales-as-mock, vendors, receipt-inbox, assistant, accounting, payroll,
employees, payslips, tax sub-routes); honest "coming soon"/locked states.
- **Frontend:** gate audit + lock states. Builder **Sonnet/medium**; Auditor
  `browser-qa-auditor` **Sonnet/medium** (walk every route, confirm no fake
  feature reachable). 
**DoD:** every route is REAL or clearly locked; no mock data visible to a user;
verified route-by-route in browser.

---

### RELEASE 1B — Real Moadian & Compliance Core
(Phases summarized; each expands to full template in its own chat.)
- **1B-P1 Moadian crypto unblock:** confirm JWS/JWE/auth-JWT, real submit +
  inquiry (audit: currently 503). No fake status ever. Backend-heavy; the *only*
  place Opus may assist on crypto/protocol design. Builder **Sonnet/high** on
  impl, Opus only for protocol design review.
- **1B-P2 Submission health (admin):** failed/retry/inquiry views, redacted
  diagnostics. **Sonnet**.
- **1B-DoD:** real send works on confirmed path; secrets never exposed; errors
  human Persian; admin can retry; inquiry updates status.

### RELEASE 1C — Accountant & Retention
- Excel import (staging→validate→commit), VAT draft, accountant limited access,
  partner/commission, reminders/notifications, support tickets, shared catalog
  with consent. Mostly **Sonnet/medium**, audits **Sonnet/low**.

### RELEASE 2 — Advanced Accounting, Payroll, AI
- Proposed journal drafts, ledgers, declarations, payroll + salary tax, defense
  package, mature OCR/Voice, AI assistant over *audited* reports. AI never emits
  official documents directly; rule-based, backend-owned, traceable.
---

## PART 6 — Three-Repo Alignment Matrix

The guarantee that repos converge. For each active phase: what each repo provides/
consumes, and the contract gate that proves they match. Filled per phase as it
starts; the pattern:

| Phase | Backend provides | Frontend consumes | Ops | Gate |
|-------|-----------------|-------------------|-----|------|
| 1A-P0 | Redis OTP, env CORS, clean OpenAPI | (no UI change) | Redis verified, smoke | ops-deploy-auditor |
| 1A-P1 | onboarding-state read | wizard + activation UI | — | api-contract-guardian + browser-qa |
| 1A-P2 | plans + `GET /subscription` | paywall component | migration | api-contract-guardian |
| 1A-P3 | enforcement + limit errors | translate to paywall | — | api-contract-guardian |
| 1A-P4 | `/purchases`, `/expenses` | replace mocks, inline create | migration | api-contract-guardian + browser-qa |
| 1A-P5 | `/receipts`, `/payments` | record + balances UI | migration | api-contract-guardian + browser-qa |
| 1A-P6 | real aggregates + reports | real dashboard/reports | — | api-contract-guardian + browser-qa |
| 1A-P7 | honest sub-status | upgrade journey | — | frontend-ux-auditor |
| 1A-P8 | admin lists + audit log | real admin pages | — | backend-contract-auditor |
| 1A-P9 | (none) | gate/lock all mocks | — | browser-qa-auditor |

**Contract-first rule:** the backend contract entry (in
`docs/api_contracts_v2_2.md`) must be merged *before* frontend consumes it. The
`api-contract-guardian` subagent fails the phase if frontend invents anything.

---

## PART 7 — Docs Cleanup Plan

Audit found ~60 md files with heavy duplication. Target: a lean, canonical set.

### 7.1 Canonical layout (one home per fact)
- **Product intent:** `digi-tax-ops/docs/product_master_blueprint_v4_2.md`
  (this is the v4.2 master; ops is its home). Backend/frontend keep a 1-line
  **pointer**, not a copy.
- **Engineering plan:** *this* blueprint — also in ops, pointers elsewhere.
- **Code reality:** `digi-tax-ops/docs/reality_audit.md`.
- **Contracts:** `digi-tax-backend/docs/api_contracts_v2_2.md` is the source;
  frontend's contract doc becomes a consumption guide that points to it.
- **Shared (glossary, transport strategy):** one canonical copy in ops/shared;
  the other two repos point to it. (Audit: currently 3-way duplicated.)

### 7.2 Actions (from audit §5 verdicts)
- **DELETE-candidate:** all `archive/*` v1.3-era docs, `ollama_model_guide`,
  `token_saving_workflow*` duplicates, `ZED.md`, `lovable_sync.md`. (Confirm none
  referenced by a live CLAUDE.md first.)
- **MERGE:** 3-way `glossary_bilingual.md` and `transport_strategy.md` → single
  ops copy + pointers. `frontend_api_contract.md` → into the consumption guide.
- **REDUNDANT:** drop the second copy of `api_contract_rules.md`. **v3 strategy
  (`product_strategy_and_phase_roadmap_v3.md`) is SUPERSEDED by v4.2 — move it to
  `archive/` and repoint every CLAUDE.md reference from v3 → the v4.2 master.**
  This is a required, explicit action (NotebookLM audit confirmed v3 is stale).
- **KEEP:** all current_phase/progress/roadmap/contract/moadian/spec digests.

### 7.3 CLAUDE.md slimming (token saving)
Move the repeated blocks (Decimal, no-fake-status, contract ownership, product
framing, status rule) into PART 2 here, and replace them in each repo CLAUDE.md
with a single pointer line: *"Canonical rules: see ops/docs engineering
blueprint PART 2."* Keep only repo-specific content (commands, module layout,
route patterns) in each CLAUDE.md. Repoint the v3 → v4.2 reference everywhere.

> Docs cleanup is itself a phase: **R1A-P0.5 (docs)**, run with **Sonnet/low**,
> auditor `blocker-ledger-auditor` + a human glance. Run it **before R1A-P0** so
> the code phase orients on a clean, non-contradictory doc set (and burns fewer
> tokens reading duplicates).

---

## PART 8 — Definition of Done & Audit Gates

### 8.1 Universal DoD (every phase)
- [ ] Contract entry merged before frontend work (if API involved).
- [ ] Canonical rules (PART 2) all honored — Decimal, tenant isolation, no fake
      status, no invented endpoints, Persian errors, digit normalization.
- [ ] Builder pass complete; **separate** Auditor pass complete.
- [ ] Validation: backend `pytest`+`ruff`+`black` (Docker-first); frontend
      `typecheck`+`build`; `git diff --check`.
- [ ] Tested with **real seeded data** (test server and/or browser MCP).
- [ ] `progress.md` + `phase_roadmap.md` updated to true status (no skeleton
      marked done).
- [ ] One commit per repo; migration noted in commit body.
- [ ] Fresh chat opened for the next phase, referencing this blueprint.

### 8.2 Frontend journey DoD (the soul — extra gate)
Beyond functional correctness, `browser-qa-auditor` explicitly verifies:
- [ ] RTL correct, mobile-first responsive at narrow width.
- [ ] One clear next action per screen; progressive disclosure works.
- [ ] Welcoming, beautiful, calm — does it feel *simple and smart to explore?*
- [ ] No raw error leakage; all copy Persian and friendly.
- [ ] Persian digits on all user-facing numbers.

### 8.3 Which model audits what (token control)
| Audit type | Subagent | Model | Effort |
|-----------|----------|-------|--------|
| Backend contract/migration/tenant | backend-contract-auditor | Sonnet | low |
| Cross-repo shape match | api-contract-guardian | Sonnet | low |
| Frontend UX/RTL/errors | frontend-ux-auditor | Sonnet | low |
| Live browser flow (real data) | browser-qa-auditor | Sonnet | medium |
| Ops deploy/config | ops-deploy-auditor | Sonnet | low |
| Blocker ledger | blocker-ledger-auditor | Sonnet | low |
| Crypto/protocol design (1B only) | (manual + review) | Opus | high |

Opus appears once, in 1B crypto design review. Everything else is Sonnet. This is
the deliberate token-saving posture.

### 8.4 Per-phase chat kickoff (copy-paste starter)
When opening a fresh chat for any phase, start with:
> "Phase <ID> from the engineering blueprint. Read blueprint PART 2 + PART 5 entry
> for <ID> + reality_audit. Confirm scope, contract, and file list before coding.
> Builder Sonnet/<effort>. Then run the named auditor. Test on the test server
> with seeded data."

---

## Appendix A — Immediate next actions (this week)
1. Place v4.2 master + this blueprint + reality_audit in `digi-tax-ops/docs/`.
2. Repoint all three CLAUDE.md from v3 → v4.2; slim them per PART 7.3.
3. Archive `product_strategy_and_phase_roadmap_v3.md` to `archive/`.
4. Run **R1A-P0.5** docs cleanup FIRST — clean the ~60 md files, remove
   duplicates/contradictions, so the code phase orients on a clean doc set.
5. Run **R1A-P0** (Redis OTP, CORS, dead-route cleanup) — highest risk, cheapest.
6. Then **R1A-P1** onboarding wizard — the welcoming journey.

## Appendix B — What "done for launch" (1A) means
A merchant can: log in, create a business in <1 min, add customers/products,
record sales + purchases + expenses, take a PDF, see *real* profit, understand
what's missing for tax, and hit a paywall that makes sense — with every screen
feeling simple, beautiful, and welcoming, and zero fake numbers anywhere.
