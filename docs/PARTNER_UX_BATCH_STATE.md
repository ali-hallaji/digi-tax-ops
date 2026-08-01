# PARTNER UX — state after the 2026-08-01 (evening) session

_Money rule ANSWERED by the founder and recorded below. Item 2 SHIPPED.
Item 1 audited (backend already complete — UI remains). Item 3 NOT started._

## ✅ The money rule (final — no longer truncated)

> At checkout the partner discount is a **visible line «تخفیف همکار»** (percent +
> amount) reducing the payable total. **COMMISSION IS COMPUTED ON THE NET
> AMOUNT ACTUALLY PAID** (after discount), never on the pre-discount price. The
> activation snapshot records **both** the discount% and the commission basis
> amount. Pin with a test proving discount+commission cannot be gamed (max
> discount + commission still ≤ the expected net-based figure).

## ✅ SHIPPED this session — item 2 (the two codes)

**What they actually are** (audited, both `HAM-XXXX`, both on the same settings
card — that shape-collision was the whole confusion):

| Field | Where | What it really does |
|---|---|---|
| «کد همکار» | `PartnerAccessCard` (`src/components/digitax/partner/partner-access-card.tsx`) | **Grants an accountant partner ACCESS** to this business's books. Instant (no accept step), revocable by the owner any time. |
| «کد معرف» | referral form in `_app.app.settings.tsx` | **Records who referred the business.** One-time, NO access, drives partner commission. Guarded by `settings.referred_by_partner` — once set, the form is replaced by a confirmation. |

Neither is dead ⇒ **no removal proposed**. Fix shipped (frontend `ff53a76`):
labels now state the CONSEQUENCE («کد همکار — دسترسی حسابدار به دفترها» /
«کد معرف — فقط ثبت معرفی، بدون دسترسی»), one-line helper each, card hint
contrasts them first. Behaviour when **both** filled: independent, both apply
(access + referral are unrelated records). **Neither**: nothing happens; the
merchant keeps full use of their own books.

## 🟡 Item 1 — backend is ALREADY DONE; only the admin UI is missing

Audited `app/modules/partners/`:

- `partner_profiles.commission_percent` + `.tier2_commission_percent` +
  `.commission_effective_from` — per-partner two-tier rates already exist.
- `PUT` admin endpoint → `admin_set_commission_percent`
  (`application/commission.py:275`): validates 0–100 with Persian errors,
  writes an audit row (`partner_commission_set`) carrying
  `tier1_before/after` + `tier2_before/after` + actor + timestamp — i.e. the
  **who/when/old→new history the founder asked for already exists** in
  `admin_audit_log`.
- Resolution order (`application/accruals.py:17`): tier1 = profile → global →
  `DEFAULT_COMMISSION_PERCENT` (15); tier2 = recruiter profile → global → 0.
- Docstring is explicit: **«Existing accruals are NEVER recomputed»** ⇒
  future-only already holds.

**Remaining work (UI only):** surface the two percents on the admin partner
create AND edit forms (`_admin.admin.partners.*`), show the effective rate on
the partner detail page, and render the existing audit rows as a «تاریخچهٔ
نرخ» list. Plus the mandated test: change a rate → assert an OLD accrual's
snapshot is untouched and a NEW activation uses the new rate.

## ⬜ Item 3 — partner discounts (NOT started; build with the rule above)

1. **Admin bounds** — new params (floor/ceiling) with history. Mirror
   `module_prices` + `module_price_history`, or extend `tax_parameters` with a
   `partner_discount_floor` / `partner_discount_ceiling` pair (units: percent);
   admin screen next to «قیمت ماژول‌ها».
2. **Partner panel** — a partner sets their discount % (all SKUs or per module),
   clamped to the admin bounds on BOTH API and UI; friendly Persian when out of
   bounds.
3. **Checkout** (`app/modules/billing/application/checkout.py`) — apply the
   discount as its own visible «تخفیف همکار» line; payable total = price −
   discount; write the order snapshot with `discount_percent` +
   `commission_basis_amount` (= net paid).
4. **Commission** (`partners/application/accruals.py`) — accrue on the NET
   basis from the snapshot, never the list price.
5. **Tests**: (a) net-based commission ≤ expected; (b) max-discount gaming
   attempt still yields the net-based figure; (c) bounds enforced server-side
   even if the UI is bypassed.
6. **Journey proof**: admin sets bounds → partner sets discount → merchant
   enters code at checkout → discounted line visible → commission ledger shows
   the net-based number. Partner + admin guides in the SAME commit.

## Machine notes

Unchanged from `PAYROLL_1405_BATCH_STATE.md` § Machine notes (docker proxy
flags, `sg docker`, repo-local git identity).
