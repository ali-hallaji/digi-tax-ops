# Current Phase - Ops

Last updated: 2026-07-18

> **NOTE:** this file lagged behind reality (previous update 2026-06-24). The LIVE phase
> tracker is `docs/progress.md` — trust it first. Since 2026-06-24 the workspace shipped:
> P3 entitlements+commission, PX-B accountant pack, SEED-12 + persona freeze, PC self-serve
> checkout, PH experience harness, MD-1/MD-2 Moadian crypto + SELF-TSP real submission,
> role-architecture correction, and (2026-07-18, local, awaiting GO) Coherence Batch 1 +
> the Tax-Lens module.

## Active Focus

**Coherence Batch 1 + Tax-Lens «مالیات من از دو نگاه» — complete locally, gates green,
awaiting founder review sitting + GO for the single dev deploy window. Details:
`docs/progress.md` Current Phase.**

Phases 1–5 of the UI redesign are complete. Phase 5 full scope delivered:
- JalaliDateField on all purchase/expense forms (Gregorian date picker was a BUG — now fixed)
- Amount input blur-formatting (thousands separator + Persian digits, ASCII on persist)
- Edit/delete row actions on purchases AND expenses with Persian confirm dialogs
- Purchase line-item mode: smart product search + free-title + qty×unit price total
- Vendor balance recompute verified on edit/delete
- Honest operational dashboard: fake KPI cards removed, "P6" internal string purged
- Admin approve/reject flow audited and confirmed correct
- Gate verified: unapproved user (09120000099) reaches purchases/expenses without any block
- Backend CRUD fully verified via curl (PATCH, DELETE, line-item create)
- pnpm typecheck → zero errors; pnpm build → clean
- CLAUDE.md updated with canonical UI rules (JalaliDateField, amount input pattern)
No backend code changes. No new migrations.

## Completed UI Redesign Phases (all frontend-only, no new migrations)

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Design system + rebrand (tokens, dark mode, Vazirmatn, teal brand) | ✓ pushed |
| Phase 2 | Wizard + Dashboard + Sidebars (soft-lock dialog, 409 inline errors) | ✓ pushed |
| Phase 3 | Customers + Products + Invoice builder + `useIdentityField` validation | ✓ pushed |
| Phase 4 | Taxpayer Profile 5-states + Admin Panel polish | ✓ pushed |
| Phase 5 | Purchases/Expenses RTL polish + honest operational dashboard | ✓ committed |

**Key cross-cutting features landed in Phases 1–4:**
- `useIdentityField` hook: single source of truth for کد ملی / شناسه ملی / کد اقتصادی / موبایل
  (blur-triggered, count hint, mod-11 / weighted checksums, operator-prefix whitelist, Persian errors)
- 409 conflict errors: inline Persian message, never raw JSON to user
- Moadian page: placeholder "در دست توسعه" UI — real submission blocked at R1B (no fake IDs)
- App sidebar: pre/post-approval states, soft-lock dialog with CTA, "به زودی" badges

## Current State

- `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, environment examples.
- Compose builds backend from `../digi-tax-backend`.
- Compose builds frontend from `../digi-tax-frontend`.
- The canonical frontend is React/TanStack/Vite (SSR production container on port 3000).
- Bootstrap, preflight, and smoke-test scripts exist for repeatable validation.
- WeasyPrint PDF migration complete (2026-06-11): backend Dockerfile installs 7 system packages;
  `api` image **must be rebuilt** for any deploy of P2.7+ backend.
- Moadian foundation phases P3.0B–P3.5 complete: migrations `e5f9a2c1d7b3`, `f3a8b2c1d5e7`,
  and the Moadian tenant-profile migration must be applied on every staging/production deploy.
- Feature gating (P3.5.8.x): frontend-only changes; no deploy action required.
- UI Redesign Phases 1–4: frontend-only; **no new Alembic migrations**; frontend image rebuild
  required to activate on staging.

## Release Structure (canonical in `docs/business_scope_freeze_v1.md`)

- **Release 1A** — merchant journey + sellable core (purchases, real P/L, subscription, onboarding)
- **Release 1B** — Moadian real submit + inquiry (crypto blocked pending spec confirmation)
- **Release 1C** — accountant-ready reports, Excel import, partner role

## Current Task Boundary (Phase 6 — Receipts + Real Dashboard)

- Receipts and payments module: record cash received / paid out against invoices and purchases.
- Operational dashboard: wire real backend metrics (replace P6 placeholder card with actual counts).
- Real P&L and cashflow derived from purchases + expenses + receipts.
- Keep orchestration and integration docs aligned with canonical sibling repos.
- Validate service wiring without changing backend/frontend application logic.
- Keep optional infrastructure out of the default stack.
- Use Compose/shell checks for validation; rebuild images only when needed.
- Track all new Alembic migrations in `docs/phase_roadmap.md` deploy checklist.

## Launch Blockers (ops-relevant)

- ~~OTP in-memory~~ — **DONE (R1A-P0):** `RedisOTPService` replaces `DevOTPService`; OTPs survive api restart. `SMOKE_TEST_RESTART_OTP=1` verifies.
- ~~CORS wildcard~~ — **DONE (R1A-P0):** CORS origins now env-driven (`BACKEND_CORS_ORIGINS`); set comma-separated list for staging/prod.
- Ops migration-state smoke test does not verify Alembic migration state — must be added to `smoke_test.sh`
- Nginx is a placeholder (`nginx/placeholder.conf`); not in `docker-compose.yml` — must be wired for production TLS
- Staging `.env` can drift from `.env.example` — manual review before each release

## Do Not

- Do not edit backend or frontend app logic from this repo.
- Do not add Kubernetes by default.
- Do not add Prometheus, Grafana, MinIO, or other observability/storage stacks by default.
- Do not commit secrets.
- Do not commit proxy settings or network workarounds.

## Required Reading For New Ops Sessions

1. `CLAUDE.md`
2. `AGENTS.md`
3. `docs/current_phase.md` (this file)
4. `docs/progress.md`
5. `docs/phase_roadmap.md` — product-level true phase status and mandatory migration checklist
6. `docs/business_scope_freeze_v1.md` — canonical scope: Release 1A/1B/1C, launch blockers, build-now table
7. `docs/product_master_blueprint_v4_2.md` — product intent v4.2 (supersedes v3 strategy doc)
8. `docs/architecture_decisions.md` when touching architecture or boundaries

> **Product framing (v4.2):** Digi Invoice is a simple, cloud-based accounting & tax-readiness SaaS.
> Revenue = subscriptions. Moadian = required edge capability, not revenue core.
> Taxpayer Profile and Admin Review are **partial skeletons**. See `docs/phase_roadmap.md` for migration checklist.
