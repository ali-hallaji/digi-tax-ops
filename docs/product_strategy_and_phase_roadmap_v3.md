# Digi Invoice / DigiTax — Product Strategy & Phase Roadmap (v3)

Last updated: 2026-06-09

This is the ops-repo copy of the product strategy reference.
**Canonical source:** `../digi-tax-frontend/docs/product_strategy_and_phase_roadmap_v3.md`

Read the canonical frontend version for the full product thesis, revenue model, personas,
onboarding/admin/partner model, record separation, shared-catalog privacy, and Moadian boundary.
This file is a concise summary for ops sessions.

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

1. Keep deploy scripts aligned with backend migration requirements.
2. Maintain API contract snapshots in `api-contracts/` when backend OpenAPI changes.
3. Provision PDF renderer (WeasyPrint system packages) when P2.7 is approved.
4. Prepare smoke-test scripts for legacy submission path (P2.8) before P6 full submission.
5. Ensure staging `.env` stays aligned with `.env.example` after each phase.

## Open Questions (ops-relevant)

- PDF engine provisioning: WeasyPrint requires `libpango`, `libcairo`, `libgdk-pixbuf2.0` on
  Debian/Ubuntu. Needs explicit ops approval before adding to Dockerfile.
- Legacy submission smoke path (P2.8): what backend endpoint + what ops smoke script change?
- Staging CORS: currently wildcard; must be restricted before production go-live.
