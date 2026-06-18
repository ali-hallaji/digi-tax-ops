# Digi Invoice — Operational Phase Roadmap

Last updated: 2026-06-17

This is the **product-level** roadmap — the true status of each phase from a user/business
standpoint. For the full product thesis, revenue model, personas, onboarding/admin/partner model,
and Moadian boundary, read `docs/business_scope_freeze_v1.md` (canonical) and
`docs/product_master_blueprint_v4_2.md` (product intent v4.2).

**Product framing (v4.2):** Digi Invoice is a simple, cloud-based accounting & tax-readiness SaaS
for Iranian merchants/companies/accountant-partners — competing with Holoo/Sepidar on simplicity,
price, mobile-first, and smarts. Revenue = subscriptions. Moadian = required edge capability,
**not** the revenue core.

**Ops scope:** `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, and
orchestration only. It does **not** own backend or frontend application logic. Deploy changes
always include `alembic upgrade head` inside the API container.

**Governance rule:** Do not mark a phase done just because skeleton endpoints exist. Skeletons
are `partial`.

---

## Release Structure

| Release | Goal | Backend status | Frontend status |
|---|---|---|---|
| **Release 1A** | Merchant journey + sellable core | ❌ Missing: purchases, real P/L, subscription, onboarding | ❌ Missing: wizard, subscription UI, mock pages hidden |
| **Release 1B** | Moadian real submit + inquiry | ❌ Blocked: crypto methods (ProtocolNotConfirmedError) | ❌ Blocked on backend |
| **Release 1C** | Accountant-ready reports + retention | ❌ Future | ❌ Future |
| **Release 2** | Advanced accounting, AI assistant, mobile | ❌ Future | ❌ Future |

---

## Phase Status Table

| Phase | Name | Status | Deploy impact |
|---|---|---|---|
| P0 | Auth / Business / Session | done | No new migrations |
| P1 | Customers / Products | done | `c4e8b2d5f9a3` (tax_items) must run |
| P1-A | Taxpayer Profile Skeleton | partial | Existing migrations |
| P1-B | Admin Review Skeleton | partial | Existing migrations |
| P1-C / R1A-P1 | Merchant Onboarding Wizard + Activation Dashboard | **done** (2026-06-18) | `a2b3c4d5e6f7` must be applied |
| P1-D | Admin Operations Console | future_high | New migrations when built |
| P1-E | Accountant/Sales Partner Role | future (R1C) | New migrations when built |
| P2 | Invoice Draft MVP | done | `a1c4e7f20b91` must be applied |
| P2.5 | Lifecycle / Readiness | done | `b2d5f8e30c14` must be applied |
| P2.6 | Print View / PDF placeholder | done | No new migrations |
| P2.6.1–4 | Jalali / Multi-template / Spec digest / Compliance | done | No new migrations |
| P2.7 | Real PDF (WeasyPrint) | **done** (2026-06-11) | ⚠️ `api` image MUST be rebuilt (WeasyPrint system packages) |
| P2.8 | Legacy Submission Smoke | future | Ops smoke scripts update needed |
| P3.0B | Moadian Dry-run Foundation | **done** (2026-06-12) | `e5f9a2c1d7b3` (moadian_submissions) must be applied |
| P3.1 | Moadian Strict Readiness Validation | **done** (2026-06-12) | No new migrations |
| P3.2 | Moadian Converter + Validation Engine | **done** (2026-06-12) | No new migrations |
| P3.3 | Moadian Transport Foundation (nonce/submit/inquiry) | **done** (2026-06-12) | `f3a8b2c1d5e7` (packet_uid) must be applied |
| P3.4 | Moadian Tenant Profile + Feature Gate | **done** (2026-06-12) | moadian_tenant_profiles migration must be applied |
| P3.4.1–3 | Moadian UX + Hardening | **done** (2026-06-12) | No new migrations |
| P3.5 | Moadian real tax-item / stuff-id workflow | **done** (2026-06-13) | No new migrations |
| P3.5.8 | Frontend feature access gates (`useFeatureAccess`) | **done** | No deploy impact |
| P3.5.8.1 | Route-level access gate (`RouteAccessGate`) | **done** (staging deployment not confirmed) | No deploy impact; redeploy frontend if not live |
| P3.5.8.2 | In-component self-gates + progressive sidebar | **done** (2026-06-16) | No deploy impact |
| P4 (R1A) | Purchases / Expenses / Balances | future_revenue | New migrations when built |
| P4.5 (R1A) | Simple Real Reports (P/L, VAT) | future_revenue | New migrations when built |
| P4.6 (R1A) | Subscription / Plan / Entitlement | future_revenue | New migrations when built |
| P5 | Excel Import / OCR / AI Data Channels | future (R1C) | New migrations when built |
| P6 | Real Moadian Submission (crypto + send) | future (R1B) | Fiscal memory / crypto / queue |
| P7 | Accounting / Tax Docs / Payroll | future (R2) | TBD |
| P8 | Market Launch Packaging | future | TBD |

---

## Important Corrections (v3, updated 2026-06-16)

- Taxpayer Profile and Admin Review are **partial** skeletons — not product-complete.
- ~~Merchant onboarding wizard is **missing**~~ — **DONE (R1A-P1, 2026-06-18):** Activation dashboard + business create wizard live; migration `a2b3c4d5e6f7` required on deploy.
- **Bug B fixed (2026-06-18):** `ensure_default_tenant_membership` auto-created a business for every new login — removed from `get_or_create_auth_user`. New users now correctly land on wizard (stage_0). ⚠️ Requires `docker-compose build --no-cache api` + `alembic upgrade head` + re-seed on any running instance.
- **E2E harness shipped, stabilized + spec 07 full journey (2026-06-18–19):** Playwright 7-spec harness in `digi-tax-frontend/e2e/`. `pnpm e2e` (headless) · `pnpm e2e:watch` (interactive picker → headed, 1 worker, slowMo 3500 ms, Persian caption cards 7 s, `pauseForWatch` live toasts at every checkpoint) · `pnpm e2e:headed` (headed all workers). 7/7 green, 1 skipped (spec 03 idempotent). White-screen flash fixed: stage_0 redirect in `beforeLoad`. Spec 07: full journey stage_0 → wizard S1–S6 → activation dashboard → customer + product (UI) → invoice finalize (API) → stage_2 invite banner in one continuous test.
- Admin operations console is **partial** (Tier-1 and Tier-2 done; console not complete).
- Subscription / paywall / entitlement is **missing** — launch blocker.
- Purchases, expenses, real P&L, and balances are **missing** — launch blockers.
- Moadian submission (P6) must **truly work** — no fake. Foundation done (P3.0B–P3.5).
- P2.7 real PDF via **WeasyPrint** — done 2026-06-11. `fpdf2`/`uharfbuzz` removed. Dockerfile changed.
- Frontend has 12+ routes that still use mock data — must be hidden or wired before user demos.
- ~~OTP is in-memory~~ — **DONE (R1A-P0):** Redis-backed (`RedisOTPService`); OTPs survive API restarts; `dev_otp` debug field intentional in `DEBUG=True` mode only — never in production.

---

## Deploy Checklist — All Mandatory Migrations

Before any staging or production deploy, confirm **all** of these Alembic migrations are applied:

| Migration | Phase | What it adds |
|---|---|---|
| `a2b3c4d5e6f7` | R1A-P1 Onboarding | `onboarding` fields on `tenants` table |
| `a1c4e7f20b91` | P2 Invoice Draft | `invoice_drafts` + `invoice_draft_lines` tables |
| `b2d5f8e30c14` | P2.5 Lifecycle | `document_number`, `archived_at`, `converted_to_tax_reportable_at`, line snapshot columns |
| `c4e8b2d5f9a3` | P2.5.1 Tax Items | `tax_items` table (required for tax-item search) |
| `e5f9a2c1d7b3` | P3.0B Moadian | `moadian_submissions` table |
| `f3a8b2c1d5e7` | P3.3 Transport | `packet_uid` column on `moadian_submissions` |
| (moadian_tenant_profiles) | P3.4 | `moadian_tenant_profiles` table |

Always run: `docker-compose exec api python -m alembic upgrade head`

The smoke test should verify that no pending migrations exist. TODO: add migration-state check to `smoke_test.sh`.

---

## WeasyPrint Build Note (P2.7+)

The backend `Dockerfile` now includes 7 system packages for WeasyPrint:
`libpango-1.0-0`, `libpangoft2-1.0-0`, `libharfbuzz0b`, `libfontconfig1`,
`libcairo2`, `libgdk-pixbuf-2.0-0`, `shared-mime-info`.

**Any deploy of the P2.7+ backend requires:**
```bash
docker-compose build api
docker-compose up -d api
docker-compose exec api python -m alembic upgrade head
```

---

## Frontend Deploy Note (P3.5.8.1+)

P3.5.8.1 (`RouteAccessGate`) and P3.5.8.2 (in-component gates + progressive sidebar) are
frontend-only changes. They require a frontend image rebuild to take effect on staging:

```bash
docker-compose build --no-cache frontend
docker-compose up -d --force-recreate frontend
```

Verify the feature gate is live by checking that `/app/accounting` redirects unapproved users
to the locked-feature screen rather than showing mock data.
