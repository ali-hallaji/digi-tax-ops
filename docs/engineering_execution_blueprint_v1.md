# Digi Invoice / DigiTax — Engineering Execution Blueprint

**Version:** 1.6 (engineering companion to Product Master Blueprint v4.2)
**Changelog (1.6):** Taxpayer Profile added as R1A-P2 (new dedicated phase);
subscription moved to R1A-P6 (value-first principle); every phase P2–P7 now
paired with its own admin slice; demand-engine framing updated (UX/journey +
AI background jobs + modular pricing); UX/journey gate strengthened as first-
class recurring requirement; causal order locked in PART 5 rationale.
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

### 1.8 Where phases run (workspace-root, not per-repo)
**Open Claude Code from the workspace root, not from inside one repo.** Most phases
are cross-repo (a single phase touches backend + frontend + ops). Launch from root
so all repos are reachable; use `--add-dir` for read-only cross-repo context.
Pattern: **one phase = one Claude Code session from workspace root**, which builds
backend first, then frontend, then ops verifies — not three separate sessions.
This keeps shared context (cheaper tokens) and keeps the repos converging.

### 1.9 Commit automatically, push AFTER the founder's manual check
At phase end, Claude Code **commits** each changed repo (one commit per repo, short
message; migration noted in body). It does **not push immediately**. Push happens
**only after the founder has manually verified the feature** (see 1.10) — because a
push finalizes changes on GitHub and the project snapshot. Sequence: Claude builds →
audits → tests on server → commits → **founder checks** → then push (Claude or
founder). Pushing before the manual check is not allowed.

### 1.10 Founder manual check after every feature (not just sprint end)
A phase is not "done" on green tests alone. After Claude Code delivers a feature,
**the founder manually verifies it on the test server** (pull → build → compose up
→ migrate if needed → open and use it) before moving to the next feature. The DoD
"PASS" is only final after this manual check, and **push happens only after this
check passes**. This is a hard gate, every feature.

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
| 13 | Subscriptions / Billing / Paywall | NONE | backend, frontend | 1A-P6 |
| 14 | Admin Operations | PARTIAL (review real; ops console incomplete) | backend, frontend | per-phase: profile review (P2), tenant volume (P3), balance view (P4), system KPIs (P5), plan mgmt (P6), final console (P7) |
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

### 4.6 Soft-lock + wizard-handoff standard (R1A-P2.5)

Established in P2.5 as a **mandatory pattern** for all nav items and action screens:

**Soft-lock rule:**
Every destination is VISIBLE in the sidebar regardless of gate status. A locked
destination is shown with a lock icon and reduced opacity — it is NEVER hidden.
Clicking a locked destination opens a friendly Persian dialog that:
1. States WHY it's locked in one plain sentence (no jargon).
2. Offers ONE direct CTA button to the unlock path (e.g. "تکمیل پروفایل مالیاتی").
3. For "coming soon" features: shows "به زودی" title with no CTA — just dismiss.

**Sidebar gate layers:**
- `activeBusiness` items: always a real link (کالا، مشتریان، فاکتورها، صدور فاکتور، پروفایل مالیاتی).
- `businessApproved` items: shown with soft-lock in pre-approval state; CTA → /app/taxpayer-profile.
- `accountingApproved` items: always "coming soon" locked (module is R2 future).

**Wizard-handoff rule:**
After every key action that advances the user's state, ONE forward CTA must be
visible with no dead ends:
- Wizard submit → `/app` → ActivationDashboard with active-step CTA button.
- ActivationDashboard stage_2 → "تکمیل پروفایل مؤدی" banner → `/app/taxpayer-profile`.
- Taxpayer profile approved → "قابلیت جدید باز شد" banner.
- صدور فاکتور always reachable from the sidebar (stage_1 through post-approval).

**Validation gate:** `frontend-ux-auditor` + `browser-qa-auditor` verify these
properties at the end of every frontend phase. E2E spec 09 (`09-nav-journey.spec.ts`)
asserts: sidebar links, soft-lock dialog content, CTA routing, mobile 390px drawer,
and wizard handoff CTA presence.
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

**Key principles (locked):**
- **Admin paired per phase (P2–P7):** every merchant feature closes its own admin
  slice in the same phase. No deferred "admin phase" — that would force re-learning
  each feature's logic 6 phases later.
- **Causal order:** profit/dashboard/reports come only *after* purchases+expenses+
  payments (v4.2 §13.3). This is non-negotiable.
- **Demand engine:** the product sells on simplicity+beauty+journey, AI background
  automation, and modular cloud pricing — not on Moadian submission alone.

---

#### R1A-P0 — Production hardening & skeleton cleanup ✓ DONE
**Why:** Audit found 3 launch blockers + skeletons polluting OpenAPI.
**Status:** Completed 2026-06-17. OTP → Redis (`RedisOTPService`), CORS env-driven
(`BACKEND_CORS_ORIGINS`), dead routes removed from OpenAPI (`/identity/login`,
`/identity/me`, `/tenants/*`, `/taxpayers/*`, `/fiscal-memories/{id}` stub).
459 tests pass; ruff + black clean. See progress.md for detail.

---

#### R1A-P1 — Onboarding wizard + activation dashboard ✓ DONE
**Why:** Audit: onboarding PARTIAL, no real wizard. The welcoming first impression
— the journey that wins the user (v4.2 §8, §9.3).
**Status:** Completed 2026-06-18/19. Short create-business flow, activation
dashboard, identity-field validation skill wired, E2E Playwright harness 7-spec
green (12 s headless; 2.2 min full journey in watch mode). Migration
`a2b3c4d5e6f7` (`add_onboarding_fields_to_tenants`) applied. See progress.md.

---

#### R1A-P2 — Taxpayer Profile + invoice-readiness gate + admin review
**Why:** The taxpayer profile exists as a partial skeleton (Stage 3/4 in the
user journey) but has never had a dedicated implementation phase. This is a real
gap: the profile cannot be completed correctly without a person-type selector,
algorithmic identity validation is missing, and the invoice-readiness gate (an
approved profile unlocks tax-reportable invoices) is the link that makes the
whole official path meaningful. The admin review queue must close in this same
phase — not later. Deferred admin means re-learning the whole profile logic in a
future phase.
**Scope (in):**
- `taxpayer_type` selector (حقیقی / حقوقی) in the profile form.
- Algorithmic identity validation (not just length checks):
  - individual `national_id` (کد ملی): exactly 10 digits + control-digit checksum
  - legal `national_id` (شناسه ملی): exactly 11 digits + checksum
  - `economic_id` (کد اقتصادی): exactly 12 digits — enforce symmetrically on
    backend (currently only `max_length=20`, no digit-count check) and frontend
- Persian/Arabic digit normalization → ASCII before persist (validate-identity-
  fields skill; wire into profile form).
- State machine: draft → submitted → approved | rejected (with Persian reason).
  Full profile form UI, inline Persian validation errors, welcoming flow.
- Invoice-readiness gate: `POST /invoice-drafts` with `type=tax_reportable`
  must require `approved` taxpayer profile. **Basic bookkeeping (customers,
  products, internal/draft invoices) is never blocked by profile state** — PART 2
  rule 5 is absolute.
- **Admin slice (closes in this phase):**
  - Full profile review queue with correct pagination (`total` = all matching
    rows, not just current page — audit §7.7: fix this bug now).
  - Detail view, approve/reject with Persian reason, audit log, pending badge.
**Scope (out):** Moadian profile (separate module), subscription (P6), purchases (P3).
**DECISION 2 — Three-layer split (tax-reportable gate):**
The gate for `tax_reportable` documents has three distinct layers that must never be merged:
- Layer 1 — **Approved taxpayer profile** (this phase): national_id/economic_id/address admin-reviewed. Approval unlocks `tax_reportable` conversion AND is the accounting/documentation foundation. This is implemented in R1A-P2.
- Layer 2 — **Karpoosheh keys** (private/public key pair): optional, only needed to actually sign and send to Moadian via the legacy path. NOT a prerequisite for conversion. Belongs to R1B.
- Layer 3 — **Real Moadian submission** (legacy / CSR middleware): R1B. Untouched in R1A.
Rule: approved taxpayer profile → may convert to `tax_reportable`. Karpoosheh keys / Moadian profile → only gate real submission (R1B). Basic bookkeeping always ungated.
- **Backend:** add `taxpayer_type` field + Alembic migration if schema change
  needed; enforce identity validation algorithmically (Pydantic validator);
  fix admin profile-list pagination bug. Contract first. Builder
  **Sonnet/medium**; Auditor `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** person-type selector → switch Zod refine rules by type; wire
  validate-identity-fields skill checksum logic; profile state machine UI
  (draft/submitted/approved/rejected with clear Persian copy); admin review
  queue (approve/reject, correct pagination, pending badge). Builder
  **Sonnet/medium**; Auditors `frontend-ux-auditor` **Sonnet/low** +
  `browser-qa-auditor` **Sonnet/medium**.
**DoD:** profile form has person_type selector; national_id and economic_id
validated algorithmically (not just length); digit normalization active; state
machine transitions work (draft→submit→approve/reject); admin review queue shows
real data with correct pagination totals; approved profile unlocks tax-reportable
invoices; internal/draft invoices never blocked; RTL+mobile verified; friendly
Persian errors; typecheck+build+pytest+ruff+black pass.
**Contract table:**
| Backend provides | Frontend consumes |
|---|---|
| `PUT/PATCH /taxpayer-profile` with `taxpayer_type` + validated ids | person-type selector + Zod refine per type |
| Fixed `GET /admin/taxpayer-profiles` (correct total count) | Pagination + pending badge |
| `POST /admin/taxpayer-profiles/{id}/approve` | Approve CTA |
| `POST /admin/taxpayer-profiles/{id}/reject` (with Persian reason) | Reject form + reason display |

---

#### R1A-P3 — Purchases & Expenses baseline (+admin)
**Why:** Real profit = sales − purchases − expenses. Audit: both NONE; mock
pages exist. v4.2 §10.1 requires these for a sellable core. Keep simple (no
inventory). Admin slice: tenant transaction volume — operational visibility for
the admin without building a full reporting engine yet.
**Scope (in):** simple purchase (supplier, lines|lump-sum, total, payment status,
date, simple purchase VAT); simple expense (category, amount, payment method,
date); effects on supplier balance + reports + real profit. Internal by default,
never readiness-blocked. **Admin slice:** operational view of tenant transaction
volume (purchase/expense counts + totals per tenant in admin tenant detail).
**Scope (out):** multi-warehouse, formal inventory, landed cost, OCR, recurring.
- **Backend:** `purchases`/`purchase_lines` + `expenses` tables (tenant_id FK +
  index); CRUD mirroring proven `invoice_drafts` patterns; balances via service;
  admin tenant detail endpoint updated with purchase/expense summary. Migration.
  Contract first. Builder **Sonnet/medium**; Auditor `backend-contract-auditor`
  **Sonnet/low**.
- **Frontend:** replace `mock/purchases.ts` + expense mocks with real API
  modules; inline supplier quick-create; category picker (no accounting jargon);
  progressive tax-field disclosure; admin tenant detail updated. Builder
  **Sonnet/medium**; Auditors `frontend-ux-auditor` **Sonnet/low** +
  `browser-qa-auditor` **Sonnet/medium**.
- **Ops:** run migration on test server; smoke covers purchases+expenses.
  **Sonnet/low**.
**DoD:** no mock on live path; tenant-safe; Decimal everywhere; supplier balance
correct in seeded test; RTL+mobile flow verified; friendly Persian errors; admin
can see tenant transaction volume (real numbers); typecheck+build+pytest+ruff+black pass.

---

#### R1A-P4 — Receipts & Payments baseline (+admin)
**Why:** v4.2 §9.9 — money is separate from the document; a sale may be paid
later. Needed for accurate balances & cash flow. Audit: NONE. Admin slice:
balance + data-health view per tenant — confirms data integrity before dashboard.
**Scope (in):** record receipt (from customer) / payment (to supplier/expense),
full or partial; link to invoice/purchase; update balances; simple cash flow.
**Admin slice:** balance + data-health view per tenant in admin (outstanding
receivables, outstanding payables, cash-in/out total — real DB numbers, no fakes).
**Scope (out):** bank integration, reconciliation, POS.
- **Backend:** `receipts`/`payments` (or unified `cash_movements`) tenant-scoped;
  partial settlement logic; balance updates via service; admin balance endpoints
  per tenant. Migration. Contract first. Builder **Sonnet/medium**; Auditor
  `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** record receipt/payment from a document with balance; partial
  amounts; clear "who still owes" view. Replace `transactions` mock. Admin view:
  balance + data-health panel. Builder **Sonnet/medium**; Auditors
  `frontend-ux-auditor` **Sonnet/low** + `browser-qa-auditor` **Sonnet/medium**.
**DoD:** partial payment reduces balance correctly (seeded test); cash-flow view
real (no fakes); admin sees real tenant balances; RTL+mobile verified; friendly
Persian errors.

---

#### R1A-P5 — Real Dashboard & Reports (+admin)
**Why:** Audit: dashboard returns hash-seeded **fake** numbers while the frontend
shows them as real — a trust risk. Reports module NONE. Only now (after
purchases/expenses/payments are wired) can profit be real (v4.2 §13.3). Admin
slice: real system-wide dashboard replaces any remaining fake/hash-seeded admin
KPIs.
**Scope (in):** replace fake dashboard service with live DB aggregates; reports —
sales today/month, purchase month, expense month, simple real profit, customer/
supplier debts, unpaid invoices. **Admin slice:** real system-wide dashboard
(active businesses count, profile completion rate, system health KPIs — no fake
numbers, ever). **Scope (out):** P&L deep, VAT draft (1C), legal ledgers (R2).
- **Backend:** real aggregation queries (Decimal); replace `build_dashboard_
  summary` stubs (hash-seeded → real); reports endpoints; system-wide admin
  aggregates (no fakes). Contract first. Builder **Sonnet/medium**; Auditor
  `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** wire dashboard + reports to real data; replace `reports`/
  `summary`/`tasks`/`activity` mocks; `toPersianDigits` on all figures; wire
  admin dashboard to real system counts. Builder **Sonnet/medium**; Auditors
  `frontend-ux-auditor` **Sonnet/low** + `browser-qa-auditor` **Sonnet/medium**.
**DoD:** **no fake numbers anywhere**; dashboard ties to real records; profit =
sales − purchases − expenses on seeded data; admin dashboard shows real system
KPIs (not hash-seeded); figures in Persian digits.

---

#### R1A-P6 — Subscription & Paywall — modular/dynamic (+admin)
**Why:** v4.2 §9.13 + §11.3: product must have plan/paywall before launch. Audit:
NONE. Subscription moves here — not P2 as previously planned — because a paywall
on a product that doesn't yet show real profit is meaningless. Value first, then
paywall. This phase merges foundation + enforcement + paywall UX into one
complete subscription implementation. Admin slice: plan/subscription management
per tenant.
**Scope (in):**
- Plan model (Free Trial, Starter, Professional, Accountant/Partner),
  tenant→plan link, feature-gate read API, friendly paywall data (value, what
  unlocks).
- Plan enforcement: enforce limits (invoice count, customers/products caps,
  feature access) at the API layer; structured `402/403`-style payloads the
  frontend translates to friendly Persian prompts.
- Paywall UX: plan comparison, trial limits visible, upgrade flow (payment may
  be manual/placeholder if no gateway yet — never fake "paid" status). Non-
  annoying; explains value + which plan + what's lost.
- **Subscription structure is modular:** monthly / 3-month / 12-month / per-
  module, optional bundles. The data model must support this from the start.
- **Admin slice:** plan/subscription management per tenant — which plan, trial
  status, upgrade history, manual plan assignment by admin.
**Scope (out):** automated payment gateway (1C if needed), commission engine (1C).
- **Backend:** plans + subscription tables (migration); `GET /subscription`,
  feature-gate resolver, enforcement middleware/guards; admin plan-management
  endpoints. Decimal for prices. Contract first. Builder **Sonnet/medium**;
  Auditor `backend-contract-auditor` **Sonnet/low**.
- **Frontend:** paywall component, upgrade CTA, limit-error→paywall translation,
  plan comparison; admin subscription management panel. Builder **Sonnet/medium**;
  Auditors `frontend-ux-auditor` **Sonnet/low** + `browser-qa-auditor`
  **Sonnet/medium**.
**DoD:** plans seeded; feature-gate read works; enforcement server-side (not
bypassable); paywall explains value clearly in Persian; no payment claims that
aren't real; admin can manage tenant plans; trial limits clear; modular pricing
structure supported in the data model.

---

#### R1A-P7 — Hide/lock mock pages + final admin console + launch gate
**Why:** v4.2 DoD: no mock page ships as a real feature. Audit lists ~15 mock
pages. The final admin console consolidates all remaining placeholder admin pages
into honest locked states. This is the launch gate.
**Scope (in):**
- Verify `RouteAccessGate` hides/locks every not-yet-real page (sales-as-mock,
  vendors, receipt-inbox, assistant, accounting, payroll, employees, payslips,
  tax sub-routes); honest "coming soon"/locked states.
- **Final admin console:** consolidate all admin placeholder pages — replace or
  honestly lock: `/admin/invoices`, `/admin/submissions`, `/admin/failed-
  submissions`, `/admin/retry-queue`, `/admin/support-tickets`,
  `/admin/announcements`, `/admin/audit-logs`. Pages with real backends (from
  P2–P6) are live; the rest show honest "coming in 1B/1C" states.
- Launch gate: final E2E check, all DoDs across all 1A phases verified.
- **Frontend:** gate audit + lock states + final admin cleanup. Builder
  **Sonnet/medium**; Auditor `browser-qa-auditor` **Sonnet/medium** (walk every
  route, confirm no fake feature reachable).
**DoD:** every route is REAL or clearly locked; no mock data visible to a user;
verified route-by-route in browser; all launch blockers from Known Risks closed
or documented with an explicit decision.

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
| 1A-P0 ✓ | Redis OTP, env CORS, clean OpenAPI | (no UI change) | Redis verified, smoke | ops-deploy-auditor |
| 1A-P1 ✓ | onboarding-state read | wizard + activation UI | migration `a2b3c4d5e6f7` | api-contract-guardian + browser-qa |
| 1A-P2 | taxpayer_type + algo id validation + fixed admin pagination | person-type selector, checksum validation, profile state machine, admin review queue | migration if schema change | api-contract-guardian + browser-qa |
| 1A-P3 | `/purchases`, `/expenses`, admin tenant summary | replace mocks, inline supplier create, admin tenant view | migration | api-contract-guardian + browser-qa |
| 1A-P4 | `/receipts`, `/payments`, admin balance view | record + balances UI, admin balance panel | migration | api-contract-guardian + browser-qa |
| 1A-P5 | real aggregates + reports + admin system KPIs (no fakes) | real dashboard/reports + admin dashboard | — | api-contract-guardian + browser-qa |
| 1A-P6 | plans + enforcement + sub-status + admin plan mgmt | paywall, upgrade journey, admin subscription panel | migration | api-contract-guardian + frontend-ux-auditor |
| 1A-P7 | (none) | gate/lock all mocks + final admin cleanup | — | browser-qa-auditor |

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

### 8.1.1 Phase Closing Ritual (mandatory — never skip)
A phase is NOT closed, and push is NOT allowed, until BOTH status files reflect it.
This is a hard, repeatable ritual so live-project state is never left stale:

1. **State update FIRST, before push.** In every changed repo, update:
   - `docs/progress.md` — mark this phase done; move it out of "active"; record any
     new open blocker discovered.
   - `docs/phase_roadmap.md` — set this phase's true status (done/partial); never
     mark a skeleton as done.
2. **Self-check question (Claude Code asks the founder, out loud):** before any
   push, Claude Code must state: *"Closing phase <ID — name>. progress.md and
   phase_roadmap.md updated in <repos>. Confirm this is the phase being closed and
   that it's ready to push?"* — and wait for the founder's yes.
3. **Founder confirms phase ID + name.** The founder restates the phase being
   closed (catches mismatches).
4. **Then push.** Push only after status files are updated AND the founder
   confirmed in step 2/3.

If the founder pushed manually (not via Claude Code), the same rule still applies:
the status files must already be updated. If they aren't, that's a gap to fix
before starting the next phase — see the kickoff check in 8.4.

### 8.2 Frontend journey DoD (the soul — extra gate)
Beyond functional correctness, `browser-qa-auditor` explicitly verifies:
- [ ] RTL correct, mobile-first responsive at narrow width.
- [ ] One clear next action per screen; progressive disclosure works.
- [ ] Welcoming, beautiful, calm — does it feel *simple and smart to explore?*
- [ ] No raw error leakage; all copy Persian and friendly.
- [ ] Persian digits on all user-facing numbers.

**Mandatory UX/journey report (every frontend phase):** at the end of a frontend
phase, Claude Code outputs a short **UX & Flow report** to the founder — not just
PASS/FAIL. It states, in plain language: does the journey feel welcoming and
simple? Is the next action always obvious? Any friction, ugliness, confusing
copy, or broken flow? Screens/states checked. This is the qualitative read the
founder uses to decide the feature is genuinely good, not merely functional.

**Seed/sample data is required for browser QA.** Testing a journey on empty
screens is meaningless. Always run with real sample data before QA:
- Backend: `python -m app.cli.seed_dev_data` (in the api container).
- Frontend run locally on the laptop via `pnpm`: use the project's sample/seed
  scripts to populate data first. browser-qa walks the flow on populated state,
  at mobile width, with Persian sample content.

**UX/journey gate is a first-class recurring gate (not optional, not one-time):**
Every merchant-facing frontend phase requires a full UX & flow evaluation,
repeated per phase as a standing requirement:
- **Journey questions (all must pass):** Is this journey welcoming? Is there one
  clear next action per screen? Are all states honest and not scary? Are Persian
  errors friendly and inline? Does the user feel progress after each action?
- **E2E harness requirements:**
  - Must run with an **interactive flow menu** so the founder can trigger
    individual flows by name without running the full suite.
  - **Inter-action delays are mandatory:** ≥0.5 s field settle, ≥2 s navigation
    pauses, ≥7 s content settle on heavy pages (so the founder sees what a real
    user sees, not a blur of transitions).
  - Must output a **Persian UX report** to the founder: flow quality, any
    friction / confusing copy / broken state / visual ugliness, screens checked,
    verdict (PASS / NEEDS FIXES).
- "Tests pass" and "typecheck clean" are necessary but not sufficient — the
  qualitative journey read is mandatory before the phase is closed. This gate
  is evaluated after every merchant-facing frontend phase, every time.

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
> "Phase <ID> from the engineering blueprint. **First, confirm the previous phase
> is fully closed: check that `progress.md` + `phase_roadmap.md` reflect it as done
> and list any open blockers.** Then read blueprint PART 2 + PART 5 entry for <ID>
> + reality_audit. Confirm scope, contract, and file list before coding. Builder
> Sonnet/<effort>. Then run the named auditor. Test on the test server with seeded
> data. Close with the Phase Closing Ritual (8.1.1)."

This kickoff check is the safety net: even if a prior phase's status update was
missed (e.g. a manual push), the next phase catches and fixes it before building.

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
