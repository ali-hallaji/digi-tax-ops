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

## ✅ Item 1 — SHIPPED (2026-08-02)

Backend was already complete (rates, 0–100 validation, audit history,
future-only accruals). Shipped this session: «تاریخچهٔ تغییر نرخ» on the admin
commission card (reads the existing `partner_commission` audit rows via a new
additive `entity_id` filter on `/admin/audit-logs`), plus the missing half of
the future-only pin — `test_a_rate_change_applies_to_the_next_activation`.
Frontend `<commission-card>`, backend `087ac54`.

## (historical) Item 1 audit — backend was already done

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

## ✅ Item 3 — CLOSED (2026-08-02, ownership batch)

All four gaps from the earlier pass are now shut:

1. **Proof captured.** `tests/e2e-harness/specs/checkout-partner-discount.spec.ts`
   walks پخش آریا (09120001003, referred by HAM-TEST1) plans → checkout at BOTH
   390px and 1440px and asserts «تخفیف همکار (٪۱۵)» renders ABOVE «مبلغ قابل
   پرداخت» (bounding-box comparison, not just presence). Live numbers:
   ۲٬۰۰۰٬۰۰۰ − ۳۰۰٬۰۰۰ = ۱٬۷۰۰٬۰۰۰ ریال.
2. **Why it was flaky, and the real fix.** The first-visit tour auto-fired ~700ms
   after mount and its overlay covered «فعال‌سازی», so the click hit the overlay.
   `PURCHASE_PATHS` in `page-tour.tsx` now blocks AUTO-FIRE on `/app/plans/*`
   only; the «؟» replay still opens the tour there, and no other page changed.
   The tour is suppressed on money paths, not weakened.
3. **Partner panel UI shipped** — `PartnerDiscountCard` on «پروفایل و کد همکار»:
   percent + per-module scope, shows the admin floor/ceiling, and renders the
   SERVER-clamped value (with a warning toast when a clamp happened) rather than
   echoing what was typed. Current discount also shows on «مشتریان من».
4. **Guides shipped** in the same commit — partner scenario `partner-discount`
   and admin scenarios `partner-discount-bounds` + `partner-commission-rate`.

FOUNDER DECISION recorded in the UI: **no code box at checkout.** The referral
code stays a one-time settings entry, and the checkout line now says so —
«از طرف همکار معرف شما — بدون نیاز به وارد کردن کد.»

## (historical) Item 3 — SHIPPED backend + checkout line (2026-08-02); ONE proof gap

DONE: migration `pdisc001`; admin floor/ceiling as `tax_parameters`
(`partner_discount_floor`/`ceiling`, unit `percent`, audited history for free);
`GET/PUT /partner/discount` with SERVER-side clamp; checkout applies per item,
keeps list price for the receipt, pays the gateway the net; **commission
accrues on `net_amount`** (the money rule); order snapshots percent + basis;
merchant pricing view exposes the discount so the checkout screen shows the
«تخفیف همکار» line BEFORE paying. 12 anti-gaming tests (monotonicity, tamper,
rounding, scope). Backend `aedf72c`.

PROVEN LIVE (API): admin bounds 0–20 → partner set 15% → tamper 95% clamped to
20% → merchant pricing returns `{percent: 15.00}` for پخش آریا (referred by
HAM-TEST1).

REMAINING (small):
1. **Screenshot of the checkout discount line** — the temp spec kept timing out
   on the plans→checkout click (a first-visit guided tour overlays it; even
   after dismissing, the «فعال‌سازی» → continue path was flaky). The line is
   implemented + typechecked + built; it just is not photographed yet.
2. **Partner-panel UI** for setting the discount — only the API exists; the
   partner currently has no screen (admin can set it for them via DB/API).
3. **Guides** (partner + admin) for the discount — NOT yet written.
4. A note for the founder: the merchant does NOT «enter a code at checkout» —
   the referral code is entered once in settings and the discount follows the
   referring partner. If you want a code box AT checkout, that is a separate
   (small) change.

## (historical) Item 3 plan

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
