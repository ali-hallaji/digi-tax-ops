# Ops Progress

Last updated: 2026-06-17

## Current Phase
Phase 0.2 local/staging orchestration hardening.

## Completed
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
- Fixed `.env.example` DATABASE_URL db name to match `POSTGRES_DB=digi_tax` (was `digitax`).
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

## Active Next

- Add migration-state verification to `smoke_test.sh` (check no pending migrations on `alembic
  current` vs `alembic heads`).
- R1A-P2 subscription / plan foundation (next feature phase).
- Wire Nginx for production TLS termination when ready (currently `nginx/placeholder.conf`).

## Known Items — Deferred to Taxpayer-Profile Phase

Identified during R1A-P1 identity-validation audit. Not bugs in shipped code — deferred scope.
Must be addressed before taxpayer-profile form ships.

1. **No person_type selector in taxpayer profile** — `national_id` in `taxpayer-profile-form.tsx`
   always validates as 10 digits (individual کد ملی). Legal entities (حقوقی) need 11-digit
   شناسه ملی. Fix: add a person_type (حقیقی/حقوقی) selector to the form; switch the Zod
   refine rule based on selection.

2. **economic_id length alignment (backend vs frontend)** — Backend `TaxpayerProfileSchema`
   uses `max_length=20` with no digit-count constraint; the identity-validation skill and
   taxpayer-profile Zod schema enforce exactly 12 digits. Before taxpayer-profile ships,
   decide the canonical rule (12 digits for Iranian کد اقتصادی is correct) and enforce it
   symmetrically: add `@validator` or `@field_validator` on the backend schema.

3. **Algorithmic identity validation — dedicated task for taxpayer-profile phase**
   Length/shape checks are insufficient for real Iranian tax identifiers:
   - **کد ملی (10 digits):** must run the control-digit checksum algorithm — `1234567890`
     passes a length check but fails the official algorithm and would be rejected by
     the Tax Organization.
   - **شناسه ملی (11 digits):** has its own validation algorithm.
   - **Mobile:** operator-prefix check (`^09[0-9]{9}$`) is too broad — should validate
     against real IRANCELL/MCI/Rightel/etc. prefix lists.
   - Reference implementations: github.com/majidh1/regex-list and
     imrostami.github.io/regexha (do not import as runtime deps — extract and own the logic).
   - **Plan:** centralize checksum functions + exact regexes in the identity-validation
     skill (`.claude/skills/validate-identity-fields/SKILL.md`) so frontend AND backend
     share one canonical source of truth, applied everywhere these fields appear.

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
