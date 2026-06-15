# Business Scope Freeze — Digi Invoice v1

Last updated: 2026-06-16

This is the **canonical product scope document** for the DigiTax / Digi Invoice workspace.
All three repos (`digi-tax-backend`, `digi-tax-frontend`, `digi-tax-ops`) must follow this scope.
No feature work should contradict the Release 1A / 1B / 1C definitions below.

---

## Product Thesis

**Digi Invoice** is a simple, cloud-based, lower-cost, smart accounting and tax-readiness SaaS
for Iranian merchants, guild businesses, B2B sellers, small/medium legal entities, and accountants.

It is NOT:
- A Moadian-only tool or Tax Organization submission pipeline
- A heavy ERP clone (no double-entry ledger, no chart of accounts, no journal entries for MVP)
- A bank/guild/ministry-driven product (those are GTM channels, not design drivers)
- An AI system that guesses official tax or accounting results
- A mobile-first-only product (mobile-safe web first; native mobile only if validated later)

**Competitive position:** Dramatically simpler, cheaper, and smarter than Holoo/Sepidar.
The primary revenue is subscriptions. Moadian is a required edge capability, not the revenue core.

---

## Target Users

| Persona | Description | Priority |
|---|---|---|
| `merchant` / `business_owner` | اصناف, guild sellers, B2B vendors, service providers — need invoices, basic bookkeeping, tax readiness | P0 |
| `small_company` | SMEs, legal taxpayers, simple corporate bookkeeping | P0 |
| `accountant_partner` | Freelance accountants, accounting firms managing multiple clients | P1 |
| `sales_agent` | Referral/channel partners, guild associations | P2 |
| `internal_admin` | DigiTax operations, support, and system administration | P0 (internal) |

**What we are NOT designing for:**
- Banks, guild organizations, investors, or institutions as product users. They are optional GTM channels.
- Enterprise/government procurement.
- Existing self-TSP customers as the center of strategy (useful for testing/migration, not the core).

---

## Core User Journey

```
signup (purpose selector) →
business setup (name, type) →
add customers + products →
create invoice / pre-invoice / internal record →
track payment →
simple reports (P/L, VAT summary) →
Moadian connection (when ready) →
submit tax-reportable invoices →
accountant access (optional)
```

---

## Activation Ladder

| Stage | Condition | What becomes available |
|---|---|---|
| STAGE 0 | No business | Dashboard, assistant, business creation only |
| STAGE 1 | Business created, profile draft/missing | Profile setup, customers, products |
| STAGE 2 | Business profile submitted, awaiting approval | Same as STAGE 1 |
| STAGE 3 | Business profile approved | Invoices, print/PDF, reports, balances |
| STAGE 4 | Moadian connection approved | Tax-reportable invoices, Moadian dashboard |
| STAGE 5 | Accounting module activated (future) | Payroll, accounting, advanced reports |

---

## Record Separation (non-negotiable)

Records move lawfully and only by explicit user action:

```
internal_private → tax_reportable → submitted (official)
```

- **internal / private record**: the business's own books. No Tax Organization involvement.
- **tax-reportable record**: explicitly promoted to the official path by the user. Readiness-gated.
- **submitted / official record**: actually sent to the Tax Organization with a real `referenceNumber` from the API response (future R1B).

**Prohibited at all times:** fake `taxid`, fake `referenceNumber`, fake `sent`/`accepted`/`submitted` status.

---

## Subscription / Paywall / Entitlement Model

A subscription model is required before the product can be sold.

**Design direction:**
- Plans: `free_trial`, `starter`, `professional`, `accountant` (exact tiers TBD)
- Entitlement enforcement: `useFeatureAccess()` hook (frontend) + plan check in bearer-token middleware (backend)
- Feature gates by plan: invoice count, report access, Moadian connection, accountant seats
- Paywall CTA: Persian-friendly upgrade prompt inside locked feature screens

**Current state:** Zero — no `plans` table, no `subscriptions` table, no plan enforcement anywhere.
**Priority:** P0 for Release 1A. No launch without at least a basic plan model.

---

## Release 1A — Merchant Journey and Sellable Core

**Goal:** A paying merchant can set up a business, create invoices, see real reports, and be charged.

| Area | Status | Priority |
|---|---|---|
| Low-friction onboarding wizard (P1.5) | ❌ Missing | P0 |
| Purpose selector at signup | ❌ Missing | P0 |
| Subscription / paywall / entitlement foundation | ❌ Missing | P0 |
| Business setup (name, type, profile) | ✅ Done (partial — no wizard) | — |
| Customers / parties CRUD | ✅ Done | — |
| Products / services CRUD | ✅ Done | — |
| Pre-invoice / internal / tax-ready invoice draft | ✅ Done | — |
| Print (official A4/landscape, receipt 80mm) | ✅ Done | — |
| PDF (WeasyPrint, official layouts) | ✅ Done | — |
| Purchases / expenses baseline | ❌ Missing | P0 |
| Vendor / supplier CRUD | ❌ Missing | P1 |
| Customer / supplier balances | ❌ Missing | P1 |
| Simple real profit / loss report | ❌ Missing | P0 |
| VAT summary report | ❌ Missing | P1 |
| Dashboard backed by real data | ❌ Missing (stubs) | P0 |
| OTP production storage (Redis) | ❌ In-memory only | P0 (launch blocker) |
| Mock pages hidden, locked, or wired | ❌ Partial (feature gates done for payroll/accounting) | P0 |
| CORS restricted for production | ❌ Wildcard staging | P0 (launch blocker) |

---

## Release 1B — Moadian Real Core

**Goal:** Moadian submission truly works. No fakes. `referenceNumber` from the official API only.

Foundation is strong (P3.0B–P3.5 done). Blocker: 4 crypto methods not confirmed from spec.

| Area | Status | Priority |
|---|---|---|
| Moadian tenant onboarding (key, FM, approval) | ✅ Done | — |
| Dry-run / validate / standard-payload | ✅ Done | — |
| Transport foundation (nonce, submit, inquiry methods) | ✅ Done (crypto stubs raise ProtocolNotConfirmedError) | — |
| Crypto methods (build_auth_jwt, sign_payload_jws, encrypt_jwe, get_server_information) | ❌ Blocked — RC_TICS.IS_v1.6 §7 alg not confirmed | P0 |
| Real submit → official referenceNumber | ❌ Blocked on crypto | P0 |
| Real inquiry / status | ❌ Blocked on crypto | P0 |
| Correction / cancellation / return-from-sale | ❌ Needs irtaxid from real submission | P1 |
| Bulk reliability / retry / idempotency | ❌ Not built | P1 |
| Full Persian error taxonomy | ❌ Partial | P1 |
| Admin tax-item catalog CRUD | ❌ Seed-only | P1 |

---

## Release 1C — Accountant-Ready Reports and Retention

**Goal:** Reports that accountants and merchants find useful; partner/referral foundation.

| Area | Status | Priority |
|---|---|---|
| Excel / CSV import (customers, products) | ❌ Missing | P0 |
| OCR / photo-to-draft gateway | ❌ Missing | P1 |
| VAT draft | ❌ Missing | P0 |
| Detailed sales / purchase / expense reports | ❌ Missing | P0 |
| Accountant limited access (P1.7) | ❌ Missing | P0 |
| SMS / email / in-app reminders | ❌ Missing | P1 |
| Partner / referral / commission foundation | ❌ Missing | P1 |

---

## Release 2 — Advanced Accounting and AI

- Legal books / formal ledger outputs
- Payroll and salary tax
- Performance tax declaration draft
- Tax defense packet
- Advanced accounting automation
- AI assistant over reports and drafts (real AI, rule-based calculations only — see AI section)
- Native mobile app (only if validated by user research)

---

## Moadian Positioning

Moadian is a **required edge capability**, not the revenue core.

- Revenue = subscriptions from merchants using everyday accounting, invoicing, and reports
- Moadian = an important feature that unlocks the tax-reportable path and keeps us legally compliant
- Priority: Moadian must work reliably after R1A core is sellable. It should not delay R1A.
- Frontend submit button must remain a disabled placeholder until backend crypto is confirmed.

---

## AI / Smart Automation Definition

**What "AI" or "smart" means in this product:**
- Rule-based, deterministic calculations (VAT, payroll tax formulas) — always in backend, always auditable
- AI-assisted OCR: photo → draft extraction (field extraction only; user reviews before saving)
- AI-assisted explanations: "this invoice field means..." (non-authoritative guidance only)
- AI-drafted reports: summary text generation from real calculated numbers
- Smart line resolver: fuzzy product matching from typed text (already implemented)

**What AI must NOT do:**
- Generate or assert official tax amounts
- Produce official VAT rates without backend rule confirmation
- Fake or estimate `taxid`, `referenceNumber`, or any official identifier
- Make accounting decisions without explicit user confirmation

---

## Accountant / Partner Role

| Role | What they can do |
|---|---|
| `accountant_partner` | Access assigned clients' data inside admin/operations; view invoices, reports, balances; limited edits with client approval |
| `sales_agent` | Refer clients; track commissions; no access to client data |
| `internal_operator` | DigiTax operations; limited admin actions |
| `internal_admin` | Full system admin; taxpayer review; user management |

**Commission model:** Recurring 5–30% of client subscription payments, configurable by tier/contract.

**Current state:** Zero — no role model, no partner module, no commission tracking.

---

## Build Now / Validate / Later / Hide Table

| Feature | Decision | Reason |
|---|---|---|
| Invoice lifecycle (internal → tax-ready → submitted) | **Build now** | Core record model, legally required |
| Print / PDF (official layouts, WeasyPrint) | **Done** | Merchant value, legally required |
| Subscription / plan model | **Build now** | Required to monetize |
| Purchases / expenses baseline | **Build now** | Required for real P&L |
| Simple P&L / VAT summary | **Build now** | Revenue-critical reports |
| Moadian crypto / real submit | **Build now (R1B)** | Legally required, foundation done |
| Onboarding wizard (P1.5) | **Build now** | Blocks conversion |
| Accountant role (P1.7) | **Validate R1C** | Growth channel, spec first |
| OCR / photo-to-draft | **Later (R1C)** | Nice-to-have for early adopters |
| AI assistant over reports | **Later (R2)** | Needs real data first |
| Payroll / salary tax | **Later (R2)** | R2 scope; gate behind accounting module |
| Native mobile app | **Later / validate** | Web-first, mobile-safe; native only if demand confirmed |
| Double-entry ledger | **Later (R2)** | Not needed for MVP; merchants don't need it |
| Vue/Quasar frontend | **Hide / archived** | Replaced by React/TanStack; never use for new work |
| Lovable sync | **Hide / archived** | Manual-emergency only; never use for new work |

---

## Repo Audit Implications

| Finding | Action |
|---|---|
| 12 frontend routes still use mock data | Hide or show "coming soon" locked screen until backend APIs exist |
| No subscription/plan/paywall anywhere | R1A priority zero — must exist before launch |
| Moadian foundation strong but crypto blocked | R1B priority zero — confirm alg from spec, implement 4 crypto methods |
| OTP is in-memory (dev-only) | Launch blocker — move to Redis before any real user |
| Dashboard KPIs are stubs | R1A — back with real invoice/transaction data |
| lovable_sync.md says "Codex-driven" | Replace with "Claude Code-driven" throughout active docs |
| Vue/Quasar in archive files | OK to leave archived; never reference as current direction |
| No purchases/expenses backend | R1A — design API contract first, then implement |
| No real P&L backend | R1A — highest revenue-value item |
| Ops current_phase.md stale (2026-05-31) | Updated in this sync pass |

---

## Launch Blockers (Release 1A)

These must be resolved before the product is sold to real users:

1. **No subscription / paywall / entitlement** — cannot charge users
2. **OTP in in-memory storage** — lost on container restart
3. **No purchases / expenses backend** — P&L is entirely mock
4. **No real P&L backend** — revenue-critical reports are fake
5. **No real VAT draft backend** — tax outputs are fake
6. **No real Moadian submit / inquiry** — legal requirement (R1B)
7. **Mock pages visible to users** — first impressions will be negative
8. **Ops migration-state smoke missing** — staging deploys can silently miss migrations
9. **CORS is wildcard** — must be restricted before production
10. **Onboarding wizard missing** — conversion will be very low

---

*This document was created 2026-06-16 based on the Business Scope Freeze session.*
*Update this file when major scope decisions change. Cross-repo phase roadmaps must not contradict it.*
