# Digi Invoice / DigiTax — Product Strategy & Phase Roadmap (v3)

Last updated: 2026-06-16

This is the ops-repo copy of the product strategy reference.
**Canonical scope document:** `docs/business_scope_freeze_v1.md` (this repo) — defines Release 1A/1B/1C, launch blockers, build-now table.
**Canonical frontend version:** `../digi-tax-frontend/docs/product_strategy_and_phase_roadmap_v3.md`

Read `docs/business_scope_freeze_v1.md` for the definitive scope and release structure.
This file is a concise product thesis summary for ops sessions.

---

## Product Thesis

Digi Invoice is a **simple, AI-assisted cloud accounting and tax-operations product** for Iranian
merchants, SMEs, companies, accountants, and internal DigiTax operations. It is **not** primarily
a Tax Organization (Moadian) submission tool. Tax submission must work, but the revenue core is
easier accounting, faster data entry, reports, tax outputs, and accountant-enabled growth.

## Revenue Thesis

Compete with Holoo/Sepidar by being dramatically simpler, cheaper, mobile-first, and smarter.
Partner/accountant referrals earn a **recurring commission** on client subscription payments
(5%–30% based on tier/contract).

## Legal and Privacy Boundary

Use lawful language only:
- **internal / private record** — the business's own books.
- **tax-reportable record** — explicitly promoted to the official path by the user.
- **submitted / official record** — actually submitted to the Tax Organization (future P6).

**Do not design or market the product as a tax-evasion tool.**
Fake submission, fake tracking numbers, and legal-bypass language are prohibited.

## Roles

- `business_owner` / `taxpayer` / `merchant`
- `company` / legal taxpayer
- `accountant_partner`
- `sales_agent`
- `internal_operator`
- `internal_admin`
- `support_operator`

## Moadian Submission Boundary (Ops Impact)

Both paths must eventually work:
1. **Legacy / self-TSP / simple path** — default low-friction path.
2. **CSR / certificate / RequestsManager v2 path** — advanced users.

P6 requires: fiscal memory; certificate/CSR; nonce; JWT/JWS/JWE; server information; invoice
submit; referenceNumber; inquiry; retry queue; error mapping; audit logs; admin visibility.

**Until P6 is built:** The submit button is a disabled frontend placeholder. No backend
submission endpoint exists. Ops must not provision fake submission infrastructure.

## Current Priorities (ops-relevant)

1. Add migration-state check to `smoke_test.sh` (`alembic current` vs `alembic heads`).
2. Keep deploy scripts aligned with new Moadian migrations (e5f9a2c1d7b3, f3a8b2c1d5e7,
   moadian_tenant_profiles) — see `docs/phase_roadmap.md` deploy checklist.
3. Maintain API contract snapshots in `api-contracts/` when backend OpenAPI changes (R1A will add
   purchases, expenses, reports, subscription endpoints).
4. Wire Nginx for production TLS termination (currently a placeholder only).
5. Ensure staging `.env` stays aligned with `.env.example` after each phase.
6. Move OTP storage to Redis before any real users.

## Resolved Questions

- **PDF engine provisioning (resolved 2026-06-11):** WeasyPrint system packages now installed in
  backend `Dockerfile`. `api` image must be rebuilt for any P2.7+ deploy. See `docs/phase_roadmap.md`
  WeasyPrint build note.

## Open Questions (ops-relevant)

- Legacy submission smoke path (P2.8): what backend endpoint + what ops smoke script change?
  (After R1B crypto is confirmed.)
- Staging CORS: currently wildcard; must be restricted before production go-live.
- Nginx production configuration: TLS termination, rate-limiting, reverse-proxy for api + frontend.
