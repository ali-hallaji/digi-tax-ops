# DigiTax / Digi Invoice — Reality Audit

**Audit date:** 2026-06-17  
**Auditor:** Claude Code (read-only, no files modified except this report)  
**Workspace root:** `/home/hitman47/Public/projects/digitax-workspace`

> **Needs re-audit (flagged 2026-06-19):** The following phases completed *after*
> this audit's capture date. Sections listed below are stale; the rest of this
> document reflects code state as of 2026-06-17 and remains authoritative until
> a fresh audit is run.
>
> - **R1A-P0 (2026-06-17):** OTP moved to Redis (`RedisOTPService`); CORS now
>   env-driven (`BACKEND_CORS_ORIGINS`); dead routes removed from OpenAPI
>   (`/identity/login`, `/identity/me`, `/tenants/*`, `/taxpayers/*` 410 kept
>   but unregistered, `/fiscal-memories/{id}` stub → 404). **Stale sections:**
>   §1 (OTP bullet), §2.1 `/identity/` and `/tenants/` rows, §2.6 (OTP storage),
>   §4.4 (key ops blockers table). These blockers are now resolved.
>
> - **R1A-P1 (2026-06-18/19):** Onboarding wizard implemented (short create-
>   business flow + activation dashboard); migration `a2b3c4d5e6f7`
>   (`add_onboarding_fields_to_tenants`) applied; identity-field validation skill
>   wired into taxpayer-profile; E2E Playwright harness (7 specs, 12 s headless).
>   **Stale sections:** §2.7 Onboarding row (was PARTIAL → now REAL), §3.1
>   `/app/taxpayer-profile` row (person_type deferred items noted in progress.md
>   Known Items — still PARTIAL pending R1A-P2 completion).
>
> These changes are confirmed by `docs/progress.md`. Exact code state for any
> section requires a fresh audit pass before asserting as fact.

---

## 1. Summary

- **OTP is in-memory only** (`DevOTPService` in `app/modules/identity/application/services.py`). It is a plain Python dict with no Redis integration. A server restart silently clears all pending OTPs. This is the single most critical production blocker.
- **All financial columns use `Numeric`/`Decimal` — no float found** in any model or service code for money, quantities, VAT rates, or totals. The Decimal rule is correctly enforced.
- **Invoice draft module is real and substantial**: full CRUD, line management, totals recalculation, lifecycle (finalize/archive/convert), readiness gate, print-view HTML (3 layouts), and PDF via WeasyPrint. This is the core product feature.
- **Dashboard KPI numbers are deterministic fake numbers** (`build_dashboard_summary` generates stable hashes, not live DB counts). The doc acknowledges this; the code confirms it.
- **Moadian real submission is blocked**: 4 crypto methods (`build_auth_jwt`, `sign_payload_jws`, `encrypt_jwe`, `get_server_information`) raise `ProtocolNotConfirmedError` at runtime. The routes exist but all real-submit calls return 503. No fake taxid/referenceNumber is returned anywhere.
- **Frontend has ~15 pages backed by mock data** (purchases, sales, transactions, vendors, reports, receipt-inbox, assistant, accounting, payroll, employees, payslips, most tax/ sub-routes). These files exist and are navigable; the sidebar is gated from P3.5.8.2 but prior deployments may still expose them.
- **Tenant isolation is correctly enforced** on all real CRUD modules via `resolve_active_tenant_id_for_auth_db` and `business_id` FK on every tenant-scoped table.
- **API base path**: `VITE_API_BASE_URL` defaults to `/api/v1` in ops. Frontend `apiRequest` prepends paths with no duplication. All frontend API modules use relative paths like `/customers`. This is correctly wired.
- **There are 15 Alembic migrations**; the most recent is `f3a8b2c1d5e7_add_packet_uid_to_moadian_submissions.py`. No migration covers the `reports` module (R1-P4, not yet implemented).
- **No purchases/expenses/reports/subscription backend** exists. These are documented as R1-P4/P4.5/P4.6 future work. Frontend pages for them use hardcoded mock data from `src/lib/mock/`.
- **CORS is wildcard in dev/staging** (`allow_origins=["*"]` when `backend_cors_origins == "*"`). Ops docs flag this as a launch blocker.
- **Nginx is not in `docker-compose.yml`**; there is only a placeholder config (`nginx/placeholder.conf`). No TLS termination in the current ops setup.

---

## 2. Backend State

### 2.1 Route Inventory

All routes are mounted under `/api/v1`.

#### Auth (`/auth/`, `/me/`, `/identity/`)

| Method | Path | Status | Notes |
|--------|------|---------|-------|
| POST | `/auth/otp/request` | REAL | In-memory OTP store; returns `dev_otp` in debug mode |
| POST | `/auth/otp/verify` | REAL | Validates OTP, creates/finds DB user, issues JWT |
| POST | `/auth/logout` | REAL (stateless) | Acknowledges logout; no server-side session to clear |
| GET | `/me` | REAL | Returns current user + active business context |
| POST | `/identity/login` | SKELETON | Hardcoded `placeholder-token`; legacy Phase 1A artifact |
| GET | `/identity/me` | SKELETON | Returns hardcoded placeholder user; legacy Phase 1A artifact |

#### Businesses / Tenants (`/businesses/`, `/tenants/`)

| Method | Path | Status | Notes |
|--------|------|---------|-------|
| GET | `/businesses` | REAL | Lists user's businesses from DB |
| POST | `/businesses` | REAL | Creates business, returns new scoped token |
| POST | `/businesses/select` | REAL | Selects active business, returns new scoped token |
| GET | `/tenants/{tenant_id}` | SKELETON (deprecated) | Returns placeholder; legacy |
| GET | `/tenants/` | SKELETON (deprecated) | Returns placeholder; legacy |

#### Customers (`/customers/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/customers` | REAL — tenant-scoped, paginated |
| POST | `/customers` | REAL — tenant-scoped, creates in DB |
| GET | `/customers/{id}` | REAL |
| PATCH | `/customers/{id}` | REAL |
| DELETE | `/customers/{id}` | REAL — soft-delete |

#### Products (`/products/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/products` | REAL — tenant-scoped |
| POST | `/products` | REAL |
| GET | `/products/{id}` | REAL |
| PATCH | `/products/{id}` | REAL |
| PATCH | `/products/{id}/tax-profile` | REAL — updates sstid/unit_code/vat_rate only |
| DELETE | `/products/{id}` | REAL — soft-delete |

#### Invoice Drafts (`/invoice-drafts/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/invoice-drafts` | REAL — tenant-scoped, filterable by status/type |
| POST | `/invoice-drafts` | REAL — blocks tax_reportable without approved Moadian profile |
| POST | `/invoice-drafts/smart-line/resolve` | REAL — matches raw title to tenant products |
| GET | `/invoice-drafts/{id}` | REAL |
| PATCH | `/invoice-drafts/{id}` | REAL — blocks type change via lifecycle code |
| DELETE | `/invoice-drafts/{id}` | REAL — soft-cancel (status→cancelled) |
| POST | `/invoice-drafts/{id}/lines` | REAL |
| PATCH | `/invoice-drafts/{id}/lines/{lid}` | REAL |
| DELETE | `/invoice-drafts/{id}/lines/{lid}` | REAL — hard-delete, recalculates totals |
| PATCH | `/invoice-drafts/{id}/lines/{lid}/tax-profile` | REAL |
| GET | `/invoice-drafts/{id}/readiness` | REAL — machine-readable gate |
| POST | `/invoice-drafts/{id}/finalize` | REAL — assigns INV-YYYY-NNNNNN, locks |
| POST | `/invoice-drafts/{id}/convert-to-tax-reportable` | REAL — readiness-gated |
| POST | `/invoice-drafts/{id}/archive` | REAL |
| GET | `/invoice-drafts/{id}/print-view` | REAL — HTML 3 layouts (official_a4/landscape/receipt_80mm) |
| GET | `/invoice-drafts/{id}/pdf` | REAL — WeasyPrint PDF; receipt_80mm returns 400 |

#### Taxpayer Profile (`/taxpayer-profile/`, `/taxpayers/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/taxpayer-profile` | REAL — returns envelope `{profile: …\|null}` |
| PUT | `/taxpayer-profile` | REAL — upsert draft |
| PATCH | `/taxpayer-profile` | REAL — partial update |
| POST | `/taxpayer-profile/submit` | REAL — transitions to submitted |
| GET | `/taxpayers/{id}` | DEPRECATED — returns 410 Gone |
| GET | `/taxpayers/` | DEPRECATED — returns 410 Gone |

#### Admin (`/admin/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/admin/me` | REAL — requires system admin |
| GET | `/admin/dashboard/summary` | REAL — reads live DB counts |
| GET | `/admin/system/health` | REAL — reads DB connectivity |
| GET | `/admin/users` | REAL — paginated, safe fields only |
| GET | `/admin/users/{id}` | REAL |
| POST | `/admin/users/{id}/activate` | REAL |
| POST | `/admin/users/{id}/deactivate` | REAL |
| GET | `/admin/taxpayers` | REAL — masked view |
| GET | `/admin/taxpayers/{id}` | REAL |
| GET | `/admin/taxpayer-profiles` | REAL — review queue, filterable by status |
| GET | `/admin/taxpayer-profiles/{id}` | REAL |
| POST | `/admin/taxpayer-profiles/{id}/approve` | REAL |
| POST | `/admin/taxpayer-profiles/{id}/reject` | REAL |

#### Moadian — Admin Submissions (`/admin/moadian/`)

| Method | Path | Status |
|--------|------|---------|
| POST | `/admin/moadian/invoices/{id}/legacy-dry-run` | REAL (dry-run only, never sends) |
| POST | `/admin/moadian/invoices/{id}/validate` | REAL |
| POST | `/admin/moadian/invoices/{id}/standard-payload` | REAL |
| POST | `/admin/moadian/submissions/{id}/legacy-prepare` | REAL |
| POST | `/admin/moadian/submissions/{id}/legacy-submit` | PARTIAL — returns 503 (crypto not confirmed) |
| POST | `/admin/moadian/submissions/{id}/inquiry` | PARTIAL — returns 503 (crypto not confirmed) |

#### Moadian — Tenant Profile (`/moadian/profile/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/moadian/profile` | REAL |
| POST | `/moadian/profile/generate-key-pair` | REAL — RSA-2048, Fernet-encrypted storage |
| POST | `/moadian/profile/import-public-key` | REAL |
| POST | `/moadian/profile/import-private-key` | REAL |
| POST | `/moadian/profile/mark-public-key-registered` | REAL |
| PATCH | `/moadian/profile/fiscal-memory` | REAL |
| PATCH | `/moadian/profile/seller-economic-id` | REAL |
| POST | `/moadian/profile/submit-for-approval` | REAL |

#### Moadian — Admin Profiles (`/admin/moadian/profiles/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/admin/moadian/profiles` | REAL — list with filter/search |
| GET | `/admin/moadian/profiles/{tenant_id}` | REAL |
| POST | `/admin/moadian/profiles/{tenant_id}/approve` | REAL |
| POST | `/admin/moadian/profiles/{tenant_id}/reject` | REAL |

#### Dashboard (`/dashboard/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/dashboard/summary` | SKELETON — deterministic fake numbers (hash-seeded) |
| GET | `/dashboard/tasks` | SKELETON — deterministic fake task list |
| GET | `/dashboard/activity` | SKELETON — deterministic fake activity feed |
| GET | `/dashboard/tax-status` | REAL-ish — derives from transport capability matrix, not live data |

#### Fiscal Memories (`/fiscal-memories/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/fiscal-memories/default-settings` | REAL — returns default constants |
| GET | `/fiscal-memories/{id}` | SKELETON — hardcoded placeholder response |

#### Transports (`/transports/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/transports/capabilities` | REAL — from capability matrix |
| GET | `/transports/modes` | REAL — returns LEGACY_SELF_TSP + REQUESTS_MANAGER_V2 |
| GET | `/transports/default` | REAL |

#### Tax Items (`/tax-items/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/tax-items/search` | REAL — DB-backed search |
| GET | `/tax-items/{id}` | REAL — by UUID or code |

#### Health (`/health/`)

| Method | Path | Status |
|--------|------|---------|
| GET | `/health/check` | REAL — used by Docker healthcheck |

### 2.2 Response Shapes

- **No global envelope** (`{ data, meta, error }`) is used. Responses are direct Pydantic models.
- List responses use per-module wrapper models (e.g., `CustomerListResponse { customers, total, limit, offset }`).
- Taxpayer profile `GET` returns `TaxpayerProfileEnvelopeResponse { profile: … | null }` — a special null-safe envelope.
- Error responses follow FastAPI default: `{ detail: string | object }`. Structured invoice lifecycle errors use `{ detail: { code, message, readiness } }`.

### 2.3 SQLAlchemy Models

| Table | Module | Tenant-scoped |
|-------|--------|---------------|
| `users` | identity | No (global) |
| `tenants` | tenants | — (is the tenant) |
| `tenant_members` | tenants | Via tenant_id FK |
| `customers` | customers | Yes — tenant_id FK + indexed |
| `products` | products | Yes — tenant_id FK + indexed |
| `taxpayers` | taxpayers | Yes — unique constraint on tenant_id |
| `taxpayer_branches` | taxpayers | Via taxpayer_id |
| `invoice_drafts` | invoice_drafts | Yes — tenant_id FK + indexed |
| `invoice_draft_lines` | invoice_drafts | Yes — tenant_id FK |
| `moadian_submissions` | moadian | Yes — tenant_id FK |
| `moadian_tenant_profiles` | moadian | Yes — unique on tenant_id |
| `fiscal_memories` (model) | fiscal_memories | Via taxpayer_id (model exists; routes are stubs) |
| `tax_items` | tax_items | No (global catalog) |

**Tenant isolation verdict:** Correctly enforced on all real modules via `resolve_active_tenant_id_for_auth_db` which reads `active_business_id` from the JWT. Every DB query for tenant-scoped data filters by `tenant_id`.

### 2.4 Alembic Migrations

15 migrations total. Chronological (by likely order):

| Revision | Description |
|----------|-------------|
| `df43309a954f` | Initial migration (Phase 1B-1) — users, tenants, tenant_members, taxpayers, fiscal_memories |
| `4d2f83b5c9a1` | Add customers and products |
| `8b7a7fdc2f8d` | Add mobile to users + membership uniqueness |
| `2f61b7c9d4a0` | Add is_system_admin flag to users |
| `9c3d2a1b8f6e` | Add taxpayer profile review workflow (status, rejection_reason, reviewed_by) |
| `a1c4e7f20b91` | Add invoice_drafts table |
| `b2d5f8e30c14` | Add invoice lifecycle fields (finalized_at, cancelled_at, archived_at, document_number) |
| `c4e8b2d5f9a3` | Add tax_items table |
| `b3c4d5e6f7a8` | Add moadian_tenant_profiles table |
| `e5f9a2c1d7b3` | Add moadian_submissions table |
| `f3a8b2c1d5e7` | Add packet_uid to moadian_submissions |

Latest revision: `f3a8b2c1d5e7`.

**Missing migrations (for future work):** No migrations for reports, purchases/expenses, subscriptions/plans.

### 2.5 Money Handling

No `Float` or `float` type found in any financial column in any model. All money, quantity, price, discount, VAT rate, and total columns use `Numeric(20, 4)` or `Numeric(7, 4)` (for rates). The `Decimal` rule from CLAUDE.md is correctly enforced in models. No float usage in financial service calculations was found.

### 2.6 OTP Storage

**In-memory only.** `DevOTPService` in `app/modules/identity/application/services.py` is a plain Python dict keyed by mobile. It is explicitly documented as "dev-only" and "not production safe." Redis is in docker-compose but is NOT used for OTP storage. This is a documented launch blocker.

### 2.7 Feature State Summary

| Feature | State |
|---------|-------|
| OTP Auth | REAL (in-memory store — dev-only; Redis required for production) |
| Business / Tenant CRUD | REAL |
| Customers CRUD | REAL |
| Products CRUD | REAL |
| Taxpayer Profile | PARTIAL (workflow exists; no wizard, no full validation) |
| Admin Review (taxpayer profiles) | PARTIAL (approve/reject flow real; admin console not product-complete) |
| Invoice Draft MVP | REAL (full lifecycle, lines, totals, finalize, print, PDF) |
| Moadian Onboarding | REAL (tenant profile, key pair, admin approval) |
| Moadian Submission | PARTIAL (dry-run/validate/payload real; actual submit blocked by crypto) |
| Dashboard KPIs | SKELETON (hash-seeded fake numbers) |
| Fiscal Memories | SKELETON (model exists; GET route is placeholder) |
| Purchases / Expenses | NONE |
| Reports / P&L | NONE |
| Subscriptions / Plans | NONE |
| Excel Import | NONE |
| AI Assistant | NONE |
| Accounting / Payroll | NONE |

---

## 3. Frontend State

### 3.1 Page Inventory

#### App Routes (`/app/*`)

| Route | Status | Evidence |
|-------|--------|---------|
| `/login` | REAL | OTP flow via `auth.ts`; calls `/auth/otp/request` + `/auth/otp/verify` |
| `/app` (dashboard) | PARTIAL | Calls real `/dashboard/*` endpoints; KPI numbers are backend stubs |
| `/app/businesses` | REAL | Calls `/businesses`, renders create/select flow |
| `/app/customers` | REAL | Full CRUD wired to `/customers/*`; validation helpers; delete confirm |
| `/app/products` | REAL | Full CRUD wired to `/products/*` |
| `/app/taxpayer-profile` | PARTIAL | Form wired to `/taxpayer-profile`; no wizard branching |
| `/app/invoices` (list) | REAL | Calls `/invoice-drafts`; filterable |
| `/app/invoices/new` | REAL | Creates draft via `/invoice-drafts` POST |
| `/app/invoices/$id` | REAL | 5-step wizard; lines, readiness, finalize, print, PDF |
| `/app/moadian` | REAL | Wired to `/moadian/profile/*`; step timeline |
| `/app/sales` | MOCK | Uses `src/lib/mock/sales.ts` |
| `/app/purchases` | MOCK | Uses `src/lib/mock/purchases.ts` |
| `/app/transactions` | MOCK | Uses `src/lib/mock/transactions.ts` |
| `/app/vendors` | MOCK | Uses `src/lib/mock/vendors.ts` |
| `/app/reports` | MOCK | Uses `src/lib/mock/` data |
| `/app/receipt-inbox` | MOCK | Upload UI only; no OCR backend |
| `/app/assistant` | MOCK | Local Zustand store only; no AI backend |
| `/app/accounting` | MOCK (gated) | Behind `accountingApproved` gate (P3.5.8.2) |
| `/app/payroll` | MOCK (gated) | Behind `accountingApproved` gate |
| `/app/employees` | MOCK (gated) | Behind `accountingApproved` gate |
| `/app/payslips` | MOCK (gated) | Behind `accountingApproved` gate |
| `/app/settings` | STATIC | No backend wiring; static placeholder |
| `/app/tax` | MOCK | Dashboard placeholder; most sub-routes are placeholders |
| `/app/tax/submissions` | PLACEHOLDER | No real Moadian submission backend yet |
| `/app/tax/notifications` | PLACEHOLDER | No backend |
| `/app/tax/reports` | PLACEHOLDER | No backend |
| `/app/tax/invoices` | MONITORING-ONLY | Amber banner; CTA to workbench; no CRUD |

#### Admin Routes (`/admin/*`)

| Route | Status | Evidence |
|-------|--------|---------|
| `/admin` | REAL | Calls `GET /admin/dashboard/summary` for live counts |
| `/admin/system-health` | REAL | Calls `GET /admin/system/health` |
| `/admin/taxpayers` | REAL | Calls `GET /admin/taxpayers` |
| `/admin/taxpayers/$id` | REAL | Calls `GET /admin/taxpayers/{id}` |
| `/admin/taxpayer-profiles` | REAL | Calls `GET /admin/taxpayer-profiles`; approve/reject |
| `/admin/taxpayer-profiles/$id` | REAL | Calls `GET /admin/taxpayer-profiles/{id}` |
| `/admin/users` | REAL | Calls `GET /admin/users`; activate/deactivate |
| `/admin/moadian-profiles` | REAL | Calls `GET /admin/moadian/profiles`; approve/reject |
| `/admin/invoices` | PLACEHOLDER | No backend route for admin invoice list |
| `/admin/submissions` | PLACEHOLDER | No admin submissions list API |
| `/admin/failed-submissions` | PLACEHOLDER | No backend |
| `/admin/retry-queue` | PLACEHOLDER | No backend |
| `/admin/plans` | PLACEHOLDER | No subscription backend |
| `/admin/support-tickets` | PLACEHOLDER | No backend |
| `/admin/announcements` | PLACEHOLDER | No backend |
| `/admin/audit-logs` | PLACEHOLDER | No backend |

### 3.2 API Layer

- **Base path:** `VITE_API_BASE_URL` (env var, defaults to `/api/v1` in ops). The client in `src/lib/api/client.ts` appends relative paths. No double-prefix found.
- **API modules:** `auth.ts`, `customers.ts`, `products.ts`, `invoice-drafts.ts`, `taxpayer-profile.ts`, `dashboard.ts`, `admin.ts`, `moadian.ts`, `tax-items.ts`.
- **Mock files** in `src/lib/mock/`: `activity.ts`, `customers.ts` (old, unused?), `dashboard.ts`, `employees.ts`, `expense-categories.ts`, `payroll.ts`, `products.ts` (old), `purchases.ts`, `receipt-inbox.ts`, `sales.ts`, `summary.ts`, `tasks.ts`, `tax-status.ts`, `transactions.ts`, `vendors.ts`.

### 3.3 Hardcoded / Fake Numbers

- **Dashboard KPI numbers:** Frontend calls real `/dashboard/summary`, but the backend service returns hash-seeded deterministic fakes (e.g., `38_000_000 + seed % 600_000`). The numbers are not random but are also not real accounting data.
- **`/app/sales`, `/app/purchases`, `/app/transactions`, `/app/vendors`:** Entirely from mock files. No API calls.
- **`/app/assistant`:** Uses a local Zustand store; no backend connection.

### 3.4 Persian RTL and Validation

- `lang="fa" dir="rtl"` set on the root HTML element in `__root.tsx`.
- `toPersianDigits` function in `src/lib/format.ts` applied to user-facing numbers per P2.7 rule.
- Validation helpers: `getApiFieldErrors`, `getFriendlyApiErrorMessage`, `getFirstApiFieldErrorMessage` in `src/lib/api/validation-errors.ts`.
- Customer and product forms include client-side validation (mobile regex, postal code length, national ID length).

---

## 4. Ops State

### 4.1 Docker Compose Services

| Service | Image / Build | Port |
|---------|--------------|------|
| `postgres` | `postgres:16-alpine` | 127.0.0.1:5432 |
| `redis` | `redis:7-alpine` | 127.0.0.1:6379 |
| `api` | Built from `../digi-tax-backend` | 8000 |
| `frontend` | Built from `../digi-tax-frontend` | `${FRONTEND_PORT:-3000}` |

- **Nginx:** Not in `docker-compose.yml`. A placeholder config exists at `nginx/placeholder.conf` but is not wired. No TLS in current compose.
- **Migrations:** Must be run manually via `docker-compose exec api python -m alembic upgrade head`. Not automated in compose.
- **CORS:** Wildcard (`allow_origins=["*"]`) when `backend_cors_origins == "*"` (dev/staging). No restriction in current setup.
- **`VITE_API_BASE_URL`:** Build-time arg, defaults to `/api/v1`. Requires frontend image rebuild on change.
- **Frontend runtime:** Production SSR Node server (`node server.mjs`) on container port 3000. Not a Vite dev server.
- **Redis:** Running in compose but **not used by any backend code for OTP or caching** as of this audit.

### 4.2 Scripts

- `scripts/bootstrap.sh` — creates DB, runs migrations.
- `scripts/preflight.sh` — validates compose config, env, DB consistency, container readiness.
- `scripts/smoke_test.sh` — tests API health, CORS, OTP auth flow, bearer-auth endpoints, frontend routes.

### 4.3 API Contract Snapshots

- `api-contracts/` directory exists with a `README.md` placeholder. No exported OpenAPI JSON snapshots found in the directory (UNKNOWN whether snapshots are kept current).

### 4.4 Key Ops Blockers (per docs, confirmed in code)

| Blocker | Confirmed in Code |
|---------|-------------------|
| OTP in-memory (not Redis) | YES — `DevOTPService` dict |
| CORS wildcard | YES — `allow_origins=["*"]` in main.py |
| Nginx not wired | YES — not in docker-compose.yml |
| Redis unused | YES — no Redis calls in any reviewed Python module |

---

## 5. Docs Inventory

### digi-tax-backend/docs/

| Path | ~Lines | Purpose | Verdict |
|------|--------|---------|---------|
| `api_contracts_v2_2.md` | 1546 | Definitive backend API contracts (source of truth) | KEEP |
| `api_contract_rules.md` | ~100 | Rules for contract ownership | KEEP |
| `architecture_decisions.md` | ~200 | Immutable ADRs | KEEP |
| `backend_execution_plan_v2_2.md` | ~200 | Active release execution plan | KEEP |
| `current_phase.md` | 207 | Active phase status (last updated 2026-06-16) | KEEP |
| `current_state.md` | ~100 | Snapshot of current state | KEEP (may duplicate current_phase) |
| `database_design.md` | ~150 | DB schema design decisions | KEEP |
| `phase_roadmap.md` | ~200 | Product-level roadmap with phase status | KEEP |
| `product_scope_v2_2.md` | ~200 | Scope constraints | KEEP |
| `progress.md` | ~300 | Done/blocked/active | KEEP |
| `moadian_legacy_v1_plan.md` | ~150 | Moadian Legacy V1 plan | KEEP |
| `moadian_onboarding_workflow.md` | ~100 | Tenant onboarding workflow | KEEP |
| `moadian_p3_3_transport_notes.md` | ~100 | Transport implementation notes | KEEP |
| `moadian_p3_scope.md` | ~100 | Moadian phase 3 scope | KEEP |
| `moadian_tax_item_workflow.md` | ~100 | Tax item / stuff-id workflow | KEEP |
| `moadian_technical_connection_digest.md` | ~200 | RC_TICS.IS_v1.6 digest | KEEP |
| `tax_org_invoice_spec_digest_v7_8.md` | ~300 | RC_IITP.IS_V7.8 field spec digest | KEEP |
| `print_pdf_compliance_gap_matrix.md` | ~150 | Print/PDF compliance gaps | KEEP |
| `accounting_payroll_future.md` | ~100 | Future scope placeholder | KEEP |
| `business_scope_freeze_pointer.md` | ~50 | Pointer to ops scope freeze doc | KEEP |
| `tax_core_spec.md` | ~100 | Tax core spec | KEEP |
| `shared/glossary_bilingual.md` | ~100 | FA/EN glossary | KEEP |
| `shared/transport_strategy.md` | ~100 | Transport strategy | MERGE (duplicate in frontend/ops) |
| `archive/backend_implementation_plan.md` | ~200 | Old v1 plan | DELETE-CANDIDATE (superseded by v2.2) |
| `archive/backend_phase_1c_plan.md` | ~100 | Old phase plan | DELETE-CANDIDATE |
| `archive/backend_phase_1d_plan.md` | ~100 | Old phase plan | DELETE-CANDIDATE |
| `archive/master_architecture_v1_3.md` | ~300 | v1.3 arch (superseded by v2.2) | OUTDATED |
| `archive/phase_checklists.md` | ~200 | Old checklists | OUTDATED |
| `archive/repo_strategy_v1_3.md` | ~100 | Old strategy | OUTDATED |
| `archive/transport_strategy.md` | ~100 | Old transport strategy | OUTDATED (see shared/) |
| `archive/ollama_model_guide.md` | ~50 | Ollama guide unrelated to product | DELETE-CANDIDATE |
| `archive/token_saving_workflow*.md` | ~50 each | LLM workflow notes | DELETE-CANDIDATE |
| `archive/ZED.md` | ~50 | Editor notes | DELETE-CANDIDATE |
| `prompts/` (7 files) | ~100 each | Historical phase prompts | KEEP (workflow context) |

### digi-tax-frontend/docs/

| Path | ~Lines | Purpose | Verdict |
|------|--------|---------|---------|
| `api_contracts_v2_2.md` | 972 | Frontend-side API contract consumption guide | KEEP |
| `api_consumption_rules.md` | ~100 | Rules for API consumption | KEEP |
| `architecture_decisions.md` | ~150 | Frontend ADRs | KEEP |
| `current_phase.md` | 161 | Active phase (last updated 2026-06-16) | KEEP |
| `current_state.md` | ~100 | State snapshot | KEEP (may duplicate current_phase) |
| `frontend_execution_plan_v2_2.md` | ~200 | Active execution plan | KEEP |
| `frontend_ux_spec.md` | ~200 | UX spec | KEEP |
| `phase_roadmap.md` | ~150 | Roadmap | KEEP |
| `product_scope_v2_2.md` | ~150 | Scope | KEEP |
| `product_strategy_and_phase_roadmap_v3.md` | ~400 | Authoritative product thesis (v3) | KEEP — most important strategic doc |
| `progress.md` | ~200 | Done/blocked | KEEP |
| `business_scope_freeze_pointer.md` | ~50 | Pointer to ops doc | KEEP |
| `frontend_api_contract.md` | ~100 | Earlier contract draft | MERGE into api_contracts_v2_2.md or DELETE |
| `lovable_sync.md` | ~50 | Lovable sync notes (deprecated workflow) | DELETE-CANDIDATE |
| `ui_rtl_design_guardrails.md` | ~100 | RTL design rules | KEEP |
| `shared/glossary_bilingual.md` | ~100 | FA/EN glossary | MERGE (same as backend) |
| `shared/transport_strategy.md` | ~100 | Transport strategy | MERGE (duplicate across 3 repos) |
| `archive/` (6 files) | various | Old v1 Vue/Quasar era docs | OUTDATED — DELETE-CANDIDATE |

### digi-tax-ops/docs/

| Path | ~Lines | Purpose | Verdict |
|------|--------|---------|---------|
| `api_contract_rules.md` | ~100 | Contract ownership rules | REDUNDANT (same as backend) |
| `architecture_decisions.md` | ~150 | Ops ADRs | KEEP |
| `business_scope_freeze_pointer.md` | ~50 | Pointer | KEEP |
| `business_scope_freeze_v1.md` | ~200 | Canonical scope: Release 1A/1B/1C | KEEP — authoritative |
| `current_phase.md` | 67 | Ops phase status | KEEP |
| `current_state.md` | ~100 | State snapshot | KEEP |
| `ops_deployment_guide.md` | ~200 | Deploy guide | KEEP |
| `phase_checklists.md` | ~150 | Phase deploy checklists | KEEP |
| `phase_roadmap.md` | ~150 | Roadmap | KEEP |
| `product_strategy_and_phase_roadmap_v3.md` | ~400 | v3 product strategy copy | REDUNDANT (same as frontend version) |
| `progress.md` | ~150 | Done/blocked | KEEP |
| `repo_strategy.md` | ~100 | Monorepo strategy | KEEP |
| `server_deploy_runbook.md` | ~100 | Server deploy steps | KEEP |
| `shared/glossary_bilingual.md` | ~100 | Glossary | MERGE (3-way duplicate) |
| `shared/transport_strategy.md` | ~100 | Transport strategy | MERGE (3-way duplicate) |
| `token_saving_workflow.md` | ~50 | LLM workflow notes | DELETE-CANDIDATE |
| `archive/` (6 files) | various | v1.3 era docs | OUTDATED — DELETE-CANDIDATE |

### Cross-repo Duplicates / Contradictions

- `shared/glossary_bilingual.md` appears in all 3 repos — likely identical; should be single canonical copy.
- `shared/transport_strategy.md` appears in all 3 repos — duplicate.
- `product_strategy_and_phase_roadmap_v3.md` appears in both `digi-tax-frontend/docs/` and `digi-tax-ops/docs/` — should have one canonical copy.
- `api_contract_rules.md` appears in both `digi-tax-backend/docs/` and `digi-tax-ops/docs/` — redundant.

---

## 6. Cross-Repo Contract Alignment

### Flow 1: Auth / OTP

| Step | Frontend call | Backend route | Shape match | Verdict |
|------|--------------|--------------|-------------|---------|
| Request OTP | `POST /auth/otp/request` body `{mobile}` | `POST /api/v1/auth/otp/request` | Frontend sends `{mobile: string}`. Backend expects `OTPRequestRequest.mobile`. Match. | ALIGNED |
| Verify OTP | `POST /auth/otp/verify` body `{mobile, otp}` | `POST /api/v1/auth/otp/verify` | Frontend sends `{mobile, otp}`. Backend expects same. Response: `{access_token, token_type, expires_in_seconds, user}`. Frontend reads `OTPVerifyResponse`. | ALIGNED |
| Logout | `POST /auth/logout` | `POST /api/v1/auth/logout` | Frontend calls, backend acknowledges. `{status: "logged_out"}`. | ALIGNED |
| Get current user | `GET /me` | `GET /api/v1/me` | Frontend `CurrentUserResponse`. Backend `{user, active_business_id, business_count}`. Frontend reads same shape. | ALIGNED |

### Flow 2: Business Select

| Step | Frontend call | Backend route | Shape match | Verdict |
|------|--------------|--------------|-------------|---------|
| List businesses | `GET /businesses` | `GET /api/v1/businesses` | Backend returns `{businesses: [...], active_business_id}`. Frontend normalizes via `normalizeBusinessesResponse`. | ALIGNED |
| Create business | `POST /businesses` body `{name}` | `POST /api/v1/businesses` | Backend returns `BusinessCreationResponse {status, access_token, token_type, expires_in_seconds, active_business}`. Frontend reads same. | ALIGNED |
| Select business | `POST /businesses/select` body `{business_id}` | `POST /api/v1/businesses/select` | Shape matches `BusinessSelectionResponse`. | ALIGNED |

### Flow 3: Customers CRUD

| Step | Frontend call | Backend route | Shape match | Verdict |
|------|--------------|--------------|-------------|---------|
| List | `GET /customers` | `GET /api/v1/customers` | Backend `CustomerListResponse { customers, total, limit, offset }`. Frontend normalizes via `normalizeListResponse`. | ALIGNED |
| Create | `POST /customers` body `CustomerCreateRequest` | `POST /api/v1/customers` | Fields: name, customer_type, economic_id, national_id, mobile, phone, postal_code, address. Match. | ALIGNED |
| Update | `PATCH /customers/{id}` | `PATCH /api/v1/customers/{id}` | Same shape with optional fields. | ALIGNED |
| Delete | `DELETE /customers/{id}` | `DELETE /api/v1/customers/{id}` | Backend returns `CustomerDeleteResponse {id}`. Frontend calls `apiRequest<void>`. Mild mismatch — frontend discards response body. | MINOR MISMATCH |

### Flow 4: Taxpayer Profile

| Step | Frontend call | Backend route | Shape match | Verdict |
|------|--------------|--------------|-------------|---------|
| Get | `GET /taxpayer-profile` | `GET /api/v1/taxpayer-profile` | Backend returns `{profile: TaxpayerProfileResponse \| null}`. Frontend unwraps the `profile` key via `normalizeNullableProfile`. | ALIGNED |
| Save (PUT) | `PUT /taxpayer-profile` | `PUT /api/v1/taxpayer-profile` | Backend returns `TaxpayerProfileResponse` (not envelope). Frontend treats as direct object. | ALIGNED |
| Patch | `PATCH /taxpayer-profile` | `PATCH /api/v1/taxpayer-profile` | Same as PUT response. | ALIGNED |
| Submit | `POST /taxpayer-profile/submit` | `POST /api/v1/taxpayer-profile/submit` | Backend returns `TaxpayerProfileResponse`. Frontend calls correctly. | ALIGNED |

### Flow 5: Invoice Draft Create + Lifecycle

| Step | Frontend call | Backend route | Shape match | Verdict |
|------|--------------|--------------|-------------|---------|
| Create draft | `POST /invoice-drafts` | `POST /api/v1/invoice-drafts` | `InvoiceDraftCreateRequest {invoice_type, ...}`. Backend blocks `tax_reportable` without approved profile. Frontend handles 409 `moadian_profile_not_approved`. | ALIGNED |
| List drafts | `GET /invoice-drafts` | `GET /api/v1/invoice-drafts` | Backend returns `{items, total, limit, offset}`. Frontend reads `items` array. | ALIGNED |
| Get detail | `GET /invoice-drafts/{id}` | `GET /api/v1/invoice-drafts/{id}` | `InvoiceDraftResponse`. | ALIGNED |
| Finalize | `POST /invoice-drafts/{id}/finalize` | `POST /api/v1/invoice-drafts/{id}/finalize` | Returns updated draft. Frontend calls correctly. | ALIGNED |
| PDF download | `GET /invoice-drafts/{id}/pdf?layout=` | `GET /api/v1/invoice-drafts/{id}/pdf` | Frontend uses direct `fetch` with Bearer header; correct layout params; handles 400/401/403/404. | ALIGNED |
| Readiness | `GET /invoice-drafts/{id}/readiness` | `GET /api/v1/invoice-drafts/{id}/readiness` | `InvoiceReadinessResponse`. | ALIGNED |

---

## 7. Doc-vs-Code Contradictions

1. **OTP described as "dev-only"**: `current_phase.md` and ops docs say OTP must move to Redis before production. The code class `DevOTPService` is indeed labelled "Dev-only in-memory OTP store. Not production safe." Docs and code agree on the gap, but docs do not show that any Redis migration has been done. **No contradiction — both say it's not ready for production.**

2. **Dashboard KPI endpoints described as "real" in current_phase.md**: The backend `current_phase.md` lists dashboard endpoints as implemented. However, `build_dashboard_summary()` in `app/modules/dashboard/application/services.py` explicitly generates hash-seeded placeholder numbers, not real DB aggregations. Frontend `current_phase.md` correctly calls these "stubs." **Contradiction: backend `current_phase.md` implies dashboard is real; backend code shows it is deterministic placeholder data.**

3. **Fiscal memories routes**: `current_phase.md` does not mention fiscal_memories routes as skeletons. The routes file shows `GET /fiscal-memories/{id}` returns a hardcoded placeholder response. `GET /fiscal-memories/default-settings` is real. **The fiscal_memories module is more skeleton than implied.**

4. **`/identity/login` and `/identity/me` as deprecated**: The routes exist and are registered, returning placeholder data. No doc explicitly calls them "deprecated/legacy" in a warning visible to API consumers; they appear in the OpenAPI schema without a clear "do not use" marker (though the route code has comments). These pollute the OpenAPI docs.

5. **`/taxpayers/{id}` and `/taxpayers/`**: These routes return 410 Gone, which is correct, but both are still registered in the router. Docs do not mention they were not fully removed.

6. **Redis in compose but unused**: Ops docs state Redis is "for cache/locks/rate limits." Backend code has no Redis client import or usage in any reviewed module. This is not a contradiction per se (Redis is there for future use) but it is potentially misleading for operators who may assume Redis is being used.

7. **`/admin/moadian/profiles` total count**: The admin profile list endpoint calculates `total=len(profiles)` after filtering, meaning the total is not an accurate count of all matching rows (it is the count of the current page). This is a pagination contract issue not reflected in any doc.

---

## 8. Open Questions / UNKNOWNs

1. **UNKNOWN: Alembic state on staging/production.** Cannot determine if all 15 migrations have been applied to any deployed database without running `alembic current` against a live DB.

2. **UNKNOWN: Whether `api-contracts/` OpenAPI snapshots are kept current.** The directory exists with only a `README.md`. No `.json` or `.yaml` files were found. The README may describe a process that is not being executed.

3. **UNKNOWN: Tax item seed data on staging.** The `seed_dev_data.py` CLI inserts 10 demo tax items. Whether these are in staging/production DB is unknown from code alone.

4. **UNKNOWN: Frontend `_app.app.tax.customer-profiles.tsx`, `_app.app.tax.fiscal-memories.tsx`, `_app.app.tax.item-profiles.tsx`, `_app.app.tax.taxpayers.tsx`, `_app.app.tax.rejected.tsx`, `_app.app.tax-readiness.tsx`** — these route files exist but were not audited in detail. Status (REAL/MOCK) is UNKNOWN.

5. **UNKNOWN: Whether `RouteAccessGate` (P3.5.8.1) is live on staging.** Frontend `current_phase.md` says "staging deployment not confirmed." This gate wraps the `_app.app.tsx` outlet and should hide mock pages from users. Without access to the deployed environment, this cannot be verified.

6. **UNKNOWN: `fiscal_memories` model** — the `FiscalMemory` SQLAlchemy model is referenced in the initial migration but only a placeholder GET route exists. The full fiscal memory management API (list, create, update, associate with taxpayer) has no implemented routes. The extent of the model's actual usage beyond the migration is unclear.

7. **UNKNOWN: WeasyPrint system dependencies** — the `current_phase.md` states "backend Dockerfile installs 7 system packages." The Dockerfile was not read in this audit. Whether the image needs to be rebuilt for current deployments is a deploy-state question.

8. **UNKNOWN: Tax Branch model** (`TaxpayerBranch`) — the model exists in `taxpayers/infrastructure/models.py` but no routes or services reference it. It appears unused.

9. **UNKNOWN: `/app/tax/*` sub-routes** in detail — most were not individually audited. They are described as placeholders in `current_phase.md` but exact mock-vs-empty-state behavior was not verified for each.

10. **UNKNOWN: Whether `normalizeListResponse` handles the `customers` key** — The backend `CustomerListResponse` uses key `customers` (not `items`). The `normalize.ts` helper does include `customers` in its key list. This appears aligned, but was not traced to a live test.
