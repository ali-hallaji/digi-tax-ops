# Digi Invoice — Operational Phase Roadmap (v3)

Last updated: 2026-06-09

This is the **product-level** roadmap — the true status of each phase from a user/business
standpoint. For the full product thesis, revenue model, personas, onboarding/admin/partner model,
and Moadian boundary, read `docs/product_strategy_and_phase_roadmap_v3.md` (this repo) or the
canonical version in `../digi-tax-frontend/docs/product_strategy_and_phase_roadmap_v3.md`.

**Product framing (v3):** Digi Invoice is a simple, AI-assisted **cloud accounting &
tax-operations** product for Iranian merchants/companies/accountant-partners — competing with
Holoo/Sepidar on simplicity, price, mobile-first, and smarts. Moadian submission is a required
edge capability, **not** the revenue core.

**Ops scope:** `digi-tax-ops` owns Docker Compose, Nginx, scripts, API contract snapshots, and
orchestration only. It does **not** own backend or frontend application logic. Deploy changes
always include `alembic upgrade head` inside the API container.

**Governance rule:** Do not mark a phase done just because skeleton endpoints exist. Skeletons
are `partial`.

---

| Phase | Name | Status | Deploy impact |
|---|---|---|---|
| P0 | Auth / Business / Session | done/mostly | No new migrations |
| P1 | Customers / Products | done/mostly | `tax_items` migration must run |
| P1-A | Taxpayer Profile Skeleton | partial | Existing migrations |
| P1-B | Admin Review Skeleton | partial | Existing migrations |
| P1-C | Merchant Onboarding Wizard | future_high | New migrations when built |
| P1-D | Admin Operations Console | future_high | New migrations when built |
| P1-E | Accountant/Sales Partner Role | future_high | New migrations when built |
| P2 | Invoice Draft MVP | done | `a1c4e7f20b91` must be applied |
| P2.5 | Lifecycle / Readiness | done | `b2d5f8e30c14` must be applied |
| P2.6 | Print View / PDF placeholder | done_partial | No new migrations (PDF 501) |
| P2.6.1–2 | Jalali / Multi-template print | done | No new migrations |
| P2.6.3 | Official Spec Digest | next/docs | No deploy impact |
| P2.7 | Real PDF | future | PDF engine system packages needed |
| P2.8 | Legacy Submission Smoke | future_high | Ops smoke scripts update needed |
| P3 | Simple Reports | future_revenue | New migrations when built |
| P4 | Data-entry Channels | future_revenue | New migrations when built |
| P5 | AI Assistant | future | TBD |
| P6 | Real Moadian Submission | future_major | Fiscal memory / crypto / queue |
| P7 | Accounting / Tax Docs | future | TBD |
| P8 | Market Launch | future | TBD |

## Important Corrections (v3)

- Taxpayer Profile and Admin Review are **partial** skeletons — not product-complete.
- Merchant onboarding wizard is **missing** — high priority before market.
- Admin operations console is **missing** — high priority.
- Moadian submission (P6) must **truly work** — no fake submission or fake tracking numbers.
- PDF (P2.7) is dependency-gated; the `/pdf` endpoint returns 501 until a server renderer is provisioned.

## Deploy Checklist — Current Mandatory Migrations

Before any production deploy, confirm these Alembic migrations are applied:

| Migration | Phase | What it adds |
|---|---|---|
| `a1c4e7f20b91` | P2 Invoice Draft | `invoice_drafts` + `invoice_draft_lines` tables |
| `b2d5f8e30c14` | P2.5 Lifecycle | `document_number`, `archived_at`, `converted_to_tax_reportable_at`, line snapshot columns |
| `c4e8b2d5f9a3` | P2.5.1 Tax Items | `tax_items` table (required for tax-item search) |

Always run: `docker-compose exec api python -m alembic upgrade head`
