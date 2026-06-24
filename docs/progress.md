# Ops Progress

Last updated: 2026-06-24

## Current Phase
Phase 0.2 local/staging orchestration hardening.

## Completed

- **2026-06-20 — DB name single source of truth (`digitax`):** Root cause: two Postgres databases existed on the same server — `digitax` (canonical, 20+ tables at head `e1f2a3b4c5d6`) and `digi_tax` (orphan, 8 tables at stale rev `8b7a7fdc2f8d`). All defaults and examples now use `digitax`. Files changed: `digi-tax-backend/app/core/config.py` (default DATABASE_URL), `digi-tax-backend/alembic.ini` (sqlalchemy.url), `digi-tax-ops/.env.example` (POSTGRES_DB + DATABASE_URL), `digi-tax-ops/docker-compose.yml` (pg_isready default), `digi-tax-ops/scripts/bootstrap.sh` (POSTGRES_DB default). Guardrail: preflight.sh already checks DATABASE_URL db name matches POSTGRES_DB; canonical name `digitax` documented in AGENTS.md. Orphan `digi_tax` database left in place (safe to `DROP DATABASE digi_tax` after founder confirms no data there).

- Added v3 product strategy alignment: `docs/phase_roadmap.md` created with product-level phase status table, mandatory migration deploy checklist (migrations `a1c4e7f20b91`, `b2d5f8e30c14`, `c4e8b2d5f9a3`), and important corrections (Taxpayer Profile/Admin Review are `partial`, onboarding wizard/admin console/partner role are `future` high-priority, Moadian no-fake rule). `docs/product_strategy_and_phase_roadmap_v3.md` created as ops-repo concise copy/reference of the product strategy. CLAUDE.md mandatory reading updated to include `phase_roadmap.md` and `product_strategy_and_phase_roadmap_v3.md`. Commit message rule added. Ops coordination role clarified (not an app source repo; every deploy includes `alembic upgrade head`).
- Added Claude Code skills and subagents foundation: 5 project skills (`start-digi-session`, `deploy-digi-test`, `smoke-check-digi`, `review-ops-diff`, `update-blockers`) and 2 subagents (`ops-deploy-auditor`, `blocker-ledger-auditor`) under `.claude/`; CLAUDE.md updated with Skills and Subagents section.
- Docker Compose local stack for Postgres, Redis, backend API, and frontend.
- Backend build context points to `../digi-tax-backend`.
- Frontend build context points to `../digi-tax-frontend`.
- Environment example includes backend/frontend runtime wiring and restricted-network frontend build proxy variables.
- `scripts/bootstrap.sh` for DB creation and Alembic bootstrap inside Docker.
- `scripts/preflight.sh` for compose/env/readiness checks.
- `scripts/smoke_test.sh` for backend health, CORS, auth, dashboard, and frontend availability.
- README includes local/staging deploy workflow.
- Frontend orchestration updated for the production SSR Node container on port `3000` with build-time `VITE_API_BASE_URL`.
- Added a server deployment runbook for separate repo updates, targeted rebuilds, migrations, restarts, and validation.
- Cleaned up deployment documentation around the current `docker-compose` workflow, single Alembic migration command, targeted backend/frontend updates, and frontend rebuild requirements for `VITE_API_BASE_URL`.
- ~~Fixed `.env.example` DATABASE_URL db name to match `POSTGRES_DB=digi_tax` (was `digitax`).~~ **REVERTED** — this was wrong; canonical name is `digitax` (no underscore). All defaults and examples now use `digitax`. See 2026-06-20 entry below.
- Updated README project structure to reflect actual directory layout.
- Updated `phase_checklists.md` to reflect completed Phase 0 and Phase 0.2 state.
- Expanded `api-contracts/README.md` with OpenAPI snapshot export instructions.
- Updated `docs/current_state.md` to include nginx service.

- **P2.7 WeasyPrint migration (2026-06-11):** Backend `Dockerfile` now installs 7 WeasyPrint system packages (`libpango-1.0-0`, `libpangoft2-1.0-0`, `libharfbuzz0b`, `libfontconfig1`, `libcairo2`, `libgdk-pixbuf-2.0-0`, `shared-mime-info`) in a dedicated `apt-get` RUN layer before `COPY requirements.txt`. The `api` image **must be rebuilt** (`docker-compose build api`) before deploying this version. `fpdf2` and `uharfbuzz` removed from requirements.txt; `weasyprint>=62.3` added. No Compose, Nginx, or script changes required.

- **P3.0B–P3.5 Moadian foundation (2026-06-12/13):** Backend Moadian module complete with
  moadian_submissions table (`e5f9a2c1d7b3`), packet_uid column (`f3a8b2c1d5e7`), and
  moadian_tenant_profiles table. **All three migrations must be applied before any deploy.**
  Frontend: /app/moadian onboarding page, /admin/moadian-profiles admin approval page.
  Real submission blocked: 4 crypto methods raise `ProtocolNotConfirmedError` (pending
  RC_TICS.IS_v1.6 §7 algorithm confirmation). No fake taxid/referenceNumber at any point.

- **P3.5.8.x feature gating (2026-06-16):** Frontend-only changes (no deploy action, no
  new migrations). `useFeatureAccess` hook, `FeatureLockScreen`, `AccessLoadingCard`,
  RouteAccessGate (P3.5.8.1), in-component self-gates on payroll/employees/payslips/accounting,
  progressive sidebar by stage (P3.5.8.2). Redeploy frontend to activate on staging.

- **Docs sync pass (2026-06-16):** `docs/business_scope_freeze_v1.md` created as canonical
  scope document. `docs/phase_roadmap.md` updated with P2.7 done, P3.0B–P3.5 done, full
  migration checklist, and Release 1A/1B/1C structure. `docs/current_phase.md` updated
  to reflect June 2026 actual state. `docs/product_strategy_and_phase_roadmap_v3.md` open
  questions updated (WeasyPrint provisioning is done). Stale "Codex-driven" wording replaced
  with "Claude Code-driven" in active docs.

- **R1A-P0 Production hardening (2026-06-17):** OTP → Redis (`RedisOTPService`; OTPs survive
  api restarts; `fakeredis` used in tests; `DevOTPService` kept for test injection);
  CORS origins env-driven via `BACKEND_CORS_ORIGINS` (comma-separated for staging/prod, `*`
  only in dev); dead routes removed from OpenAPI (`/identity/login`, `/identity/me`,
  `/tenants/*`, `/taxpayers/*` (410), `/fiscal-memories/{id}` stub → 404); `smoke_test.sh`
  extended with `SMOKE_TEST_RESTART_OTP=1` OTP-across-restart verification.
  `fakeredis==2.26.2` added to requirements.txt (test dependency only). 459 tests pass;
  ruff clean; black clean. No new Alembic migrations (OTP in Redis needs no DB schema change).

- **R1A-P0.5 Docs cleanup (2026-06-17):** Three canonical docs added to ops:
  `product_master_blueprint_v4_2.md`, `engineering_execution_blueprint_v1.md`,
  `reality_audit.md`. Seven stale v1.3-era archive files removed. `token_saving_workflow.md`
  deleted. `product_strategy_and_phase_roadmap_v3.md` moved to `docs/archive/`.
  `api_contract_rules.md` (stale v1.3 copy) replaced with pointer. v3 references in
  required-reading sections updated to v4.2. CORS prod risk (env default=`*`) flagged
  as OPEN BLOCKER in `progress.md`.

- **R1A-P0.6 Tooling alignment (2026-06-17):** CORS note in `smoke-check-digi` skill
  fixed to reflect env-driven origins. `docs/tooling_inventory.md` added cataloguing
  all active skills, agents, and their phase alignment.

- **R1A-P0.7 Tooling clarity (2026-06-17):** All three CLAUDE.md files updated —
  skills framed as Claude-Code-invoked (not terminal commands); "What runs where"
  note added per repo; `up_local_test.sh` confirmed in `scripts/` and listed in ops
  CLAUDE.md Services section. Docs only; no app code changed.

- **R1A-P1 — Onboarding wizard + activation dashboard + E2E close-out (2026-06-18–19):**
  Backend commit `906d01d` (R1A-P1 in digi-tax-backend); migration `a2b3c4d5e6f7`
  (`add_onboarding_fields_to_tenants`) must be applied. Frontend: auth stabilization (SSR
  hydration blank-page, auth-clear on login, login token-exchange, OTP double-submit guard),
  activation dashboard, identity-field validation skill, UX fixes. Browser QA PASS locally.
  Playwright 7-spec E2E harness: headless 7/7 green (12 s); spec 07 full journey confirmed
  2.2 min in watch mode (stage_0 → wizard S1–S6 → customer → product → invoice finalize →
  stage_2). Watch-mode pacing: 2 s nav pauses, 7 s content pauses, 0.5 s field settle,
  1 s pre-submit beat, 600 s per-test timeout.
  Identity-validation audit: skill IS wired into taxpayer-profile via Zod refine; customer
  and product identity fields correctly optional per R1A-P1 scope.
  **Deploy action: `alembic upgrade head` in api container + rebuild api image.**

  **R1A-P2 — Taxpayer Profile full implementation (2026-06-19):**
  Backend: `taxpayer_type` enum column + Alembic migration `d7e8f9a0b1c2` (head after
  P1's `a2b3c4d5e6f7`); `app/core/identity_validation.py` with algorithmic checksums for
  کد ملی (10-digit control-digit), شناسه ملی شرکت (11-digit weights), کد اقتصادی (exactly
  12 ASCII digits); Persian digit normalization via existing `normalize_identifier`; Persian
  error messages on validation failure; invoice-readiness gate (`taxpayer_profile_approved`
  param in `evaluate_invoice_readiness` — only tax_reportable invoices blocked, draft/proforma
  free); 22 unit tests (all pass); ruff + black clean. Bug fixed: `taxpayer_type=None` on PUT
  now defers national_id validation to submit time (uses `elif` branch, not catch-all else).
  Frontend: `taxpayer_type` selector (first field), dynamic national_id label (کد ملی /
  شناسه ملی شرکت), `mode: "onBlur"` Zod `superRefine`, `identityValidation.ts` mirroring
  backend algorithms, 5 honest states (no-profile/draft/submitted/approved/rejected),
  confirmation dialog before submit, form locked for submitted/approved. E2E harness:
  `scripts/e2e-taxpayer-profile.sh` + `e2e/specs/08-taxpayer-profile.spec.ts` (4 flows).
  `api_contracts_v2_2.md` updated: stale field names corrected (id/name/economic_id replacing
  old taxpayer_id/legal_name/economic_code), `taxpayer_type` + `TaxpayerType` added.
  **Deploy action: `alembic upgrade head` in api container + rebuild api image.**
  22 identity tests pass; 487 total pass (3 pre-existing auth-route failures unchanged).

  **R1A-P2 gate correction (2026-06-19 — DECISION 2):**
  The tax_reportable conversion gate was incorrectly tied to Moadian profile (R1B concept).
  Fixed: `POST /invoice-drafts` with `invoice_type=tax_reportable` and `POST /{id}/convert-to-tax-reportable`
  now require an approved **taxpayer profile** (not Moadian profile). Error code changed from
  `moadian_profile_not_approved` → `taxpayer_profile_not_approved`. Frontend updated: new-invoice
  page and invoice detail page now key off taxpayer profile status; approved profile status card
  shows "قابلیت جدید باز شد" message. Moadian profile gate remains exclusively on the real-submit
  path (R1B). Basic bookkeeping unchanged and ungated. 3 new backend tests added (134 total
  pass). E2E gate flow updated with corrected assertions. No schema migration (logic change only).
  Blueprint DECISION 2 and product master §8.6 updated with 3-layer clarification.

  **R1A-P2.5 — Navigation & User-Journey Integration (2026-06-19):**
  Fixed the "system feels confusing" problem — pages existed but were unreachable
  except by typing URLs manually.
  Sidebar (`app-sidebar.tsx`) fully restructured:
  - Pre-approval state (stage_1/2): adds صدور فاکتور, فاکتورها و اسناد, پروفایل مالیاتی to راه‌اندازی
    group. All approval-gated destinations (تراکنش‌ها, خرید, گزارش‌ها, اتصال مودیان) now shown
    with soft-lock (lock icon + reduced opacity) instead of hidden. Coming-soon items
    (حسابداری) visible with "به زودی" badge.
  - Soft-lock click opens a Dialog (not a dead end): Persian explanation + CTA button to
    the unlock path (/app/taxpayer-profile). Coming-soon items show "به زودی" title, no CTA.
  - Post-approval state: صدور فاکتور added to "فروش و درآمد" group. Accounting module
    shown as "به زودی" locked item.
  No backend changes. No gate logic changed.
  E2E: `09-nav-journey.spec.ts` — 3 flows (A+B+C+D sidebar+locks, E mobile 390px, F wizard
  handoff). 15/15 full suite green (1 skipped idempotent).
  Blueprint PART 4 §4.6: soft-lock + wizard-handoff standard documented.
  **Deploy action: frontend image rebuild only.**

  **R1A-P2.5 — Navigation & User-Journey Integration — see entry above.**

  **UI Redesign Phase 1 — Design System + Rebrand (2026-06-24, pushed):**
  Unified design tokens (`tokens.css`), dark mode, teal rebrand (`--primary: oklch(0.508 0.097 184.5)`),
  Vazirmatn font wired, `--radius: 0.875rem`, status token system (`--success/warning/danger/info/locked`).
  RTL login fix. No backend changes. Frontend only.

  **UI Redesign Phase 2 — Wizard + Dashboard + Sidebars (2026-06-24, pushed):**
  Onboarding wizard polish, activation dashboard, operational dashboard skeleton.
  App-sidebar fully restructured: pre/post-approval states, soft-lock dialog with CTA,
  "به زودی" badges, 409 conflict errors inline on customer form. Frontend only.

  **UI Redesign Phase 3 — Customers + Products + Invoice Builder + Validation (2026-06-24, pushed):**
  Customer and product CRUD forms hardened. Invoice builder (new invoice route) updated.
  `useIdentityField` hook wired across all forms as single source of truth for
  کد ملی / شناسه ملی / کد اقتصادی / موبایل validation (blur-triggered, count hint while typing,
  Persian friendly errors). `identityValidation.ts` updated: improved mod-11 logic,
  operator-prefix whitelist for mobile. 409 conflict handling: inline Persian error (never raw JSON).
  Moadian page: placeholder UI with "در دست توسعه" state (real submission blocked — R1B).
  Frontend only.

  **UI Redesign Phase 4 — Taxpayer Profile 5-States + Admin Panel Polish (2026-06-24, pushed):**
  Taxpayer profile route: full 5-state flow (empty → draft → pending → approved → rejected/expired)
  with per-state Persian messaging, confirmation dialog before submit, form locked after submit/approval,
  soft-locked gated features revealed on approval.
  Admin taxpayer review: detailed profile view, approve/reject actions, rejection-reason form.
  Admin profiles index: pending badge, status filter tabs, full list.
  Admin sidebar cleanup. Admin API module extended. Frontend only.

  **UI Redesign Phase 5 — Purchases/Expenses Full Polish + Operational Dashboard (2026-06-24):**
  Complete rewrite of `_app.app.purchases.tsx`:
  - **JalaliDateField**: replaced native `<input type="date">` on all forms with the Shamsi picker
    (Gregorian shown as sub-hint, never as primary). CLAUDE.md updated with canonical rule.
  - **Amount inputs**: on-blur formatting via `formatDecimalForInputDisplay` (thousands separator +
    Persian digits); on-focus strips to raw; on-submit `normalizeDecimalInput` → ASCII decimal.
    Placeholders show separator-formatted examples (مثال: ۲,۵۰۰,۰۰۰).
  - **StatusPill**: design-token CSS vars (`--success/warning/danger`-tint).
  - **Edit dialogs**: EditPurchaseDialog (payment status, paid amount, note); EditExpenseDialog
    (all fields); both pre-populated and wired to PATCH endpoints.
  - **Delete confirm**: shared `DeleteConfirmDialog` with friendly Persian description; purchase
    delete triggers vendor-balance recompute (backend already handles this).
  - **Line-item mode**: toggle "افزودن اقلام خرید" reveals line entry with product smart-search
    (filters tenant product list); free-text description allowed when product not found; qty ×
    unit_price totals displayed; backend `purchase_lines` table already existed.
  - **Vendor picker**: select existing OR type new name with clear button.
  - **Operational dashboard**: removed all fake hash-seeded KPI sections; "P6" internal code
    removed from user-visible text; replaced with calm Persian honest placeholder.
  - **Admin pages**: audited — no changes needed (design tokens correct, approve/reject flow solid).
  - **Gate check verified**: unapproved user (09120000099) can create purchases and expenses.
  - **Backend CRUD verified via curl**: PATCH (payment update + outstanding recompute), DELETE
    (vendor balance recompute), line-item create (total = sum of lines), expenses PATCH/DELETE.
  - **Backend tests**: 513 pass, 6 pre-existing failures (3 auth-route, 3 moadian-profile) —
    unchanged from before this phase. Ruff + black clean.
  - Frontend commit: see git log. No backend code changes. No new migrations.

## Active Next (R1A — Phase 6 / Receipts+Payments)

- **Phase 6: Real financial data + Receipts/Payments**
  - Operational dashboard: wire real customers/products/invoice counts from backend (replace placeholder)
  - Receipts and payments module (P4 from original roadmap)
  - Real P&L and cashflow from actual transactions
- Add migration-state verification to `smoke_test.sh` (check no pending migrations on `alembic
  current` vs `alembic heads`).
- Wire Nginx for production TLS termination when ready (currently `nginx/placeholder.conf`).

## Known Risks

- **Migration-state smoke missing** — staging deploys can silently miss migrations. Must add
  `alembic current` check to `smoke_test.sh`.
- **Nginx is a placeholder** — `nginx/nginx.conf` is `placeholder.conf`, not in compose.
  Production TLS/proxy not wired.
- **CORS production risk (OPEN BLOCKER — config only, no code change needed):** `.env.example`
  defaults `BACKEND_CORS_ORIGINS=*` (wildcard). The backend code correctly reads the env var;
  no code forces `*`. Any staging/prod `.env` **must** set this to comma-separated real origins
  (e.g. `https://app.example.com`). Dev wildcard is acceptable; staging/prod must not use `*`.
  No automated enforcement exists — this is a deploy-time checklist item.
- Staging `.env` can drift from `.env.example` — review before each release.
- Optional services should remain out of the default Compose stack.
- Ops changes can accidentally cross repo boundaries if not kept scoped.

## Validation Policy
Use Docker Compose and shell syntax checks. Do not edit backend/frontend app logic from this repo.
