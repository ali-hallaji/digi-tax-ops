# Part 5 — Monetization Assessment (برآورد درآمدزایی)

_Read-only research doc for the founder. 2026-07-22. No code was changed._
_Sources: `digi-tax-backend/app/core/plan.py`, `app/cli/seed_realistic_world.py` (MODULE_PRICE_SEED, lines 703–714), `app/modules/billing/application/pricing.py`, `app/modules/entitlements/`, `app/modules/moadian/normalizer/__init__.py`, `digi-tax-ops/docs/product_master_blueprint_v4_2.md` §9.13, `docs/business_scope_freeze_v1.md`, `docs/progress.md` (PC / monetization-D / base-plan entries)._

---

## 1. Current state — the seeded price list (exact, as in code)

Prices come from `MODULE_PRICE_SEED` in
`digi-tax-backend/app/cli/seed_realistic_world.py` (comment in code: «founder-set,
ریال»). All prices are **monthly** (`ModulePrice.monthly_price`), emitted as
whole-rial decimal strings by `rial()` in `billing/application/checkout.py`.
Trial defaults (from `entitlements/monetization.py`, per progress.md):
`BASE_TRIAL_DAYS=14` **AND** `BASE_TRIAL_DOCUMENT_CAP=30` — whichever hits first.
Partner default commission: `DEFAULT_COMMISSION_PERCENT = 15.00` (`app/core/plan.py`).

| Module key | Seeded price (ریال/ماه) | ≈ تومان/ماه | Sellable? | What it gates |
|---|---|---|---|---|
| `base_plan` | **5,000,000** | ۵۰۰٬۰۰۰ | ✅ active | «پلن پایه» — per-business subscription; without it (post-trial) invoice/customer/product/purchase/expense create returns 402 `BASE_PLAN_REQUIRED`. Existing tenants grandfathered. |
| `inventory_lite` | **3,000,000** | ۳۰۰٬۰۰۰ | ✅ active | انبار ساده — quantity-only stock, movements, low-stock card |
| `accountant_view` | **2,500,000** | ۲۵۰٬۰۰۰ | ✅ active | نمای حسابدار — journal/ledger/trial-balance pages + partner grants |
| `expense_breakdown_report` | **2,000,000** | ۲۰۰٬۰۰۰ | ✅ active | 5th reports tab «هزینه‌ها به تفکیک» |
| `tax_lens` | **2,000,000** | ۲۰۰٬۰۰۰ | ✅ active | «مالیات من از دو نگاه» — two-lens yearly tax estimate |
| `moadian_submission` | **1,500,000** | ۱۵۰٬۰۰۰ | ❌ `active=False` («به‌زودی») | Moadian submission flow (on top of taxpayer-approval gate). Also sold **standalone**: base-expired + moadian-active keeps customers/products/official invoices/submit/inquiry usable («فقط ارسال مودیان — بدون نیاز به پلن پایه»). |
| `team_members` | **1,000,000** | ۱۰۰٬۰۰۰ | ✅ active | >2 active members per tenant |
| `multi_business` | **0** («رایگان») | ۰ | ✅ active | Capability to create >1 business is free — but each business needs its own `base_plan` |

Notes kept honest:
- These are the only price numbers anywhere in code/docs. The blueprint §9.13 sketches
  Free-Trial / Starter / Professional / Accountant tiers **without any numbers** — the
  modular per-feature list above superseded that sketch.
- A `NULL` price renders as «استعلام قیمت»; exactly `0` renders as «رایگان» (pricing.py).
- No recurring-billing engine exists — `base_plan` is an entitlement with a monthly
  `expires_at`, renewed through the same checkout.
- Checkout is live but the gateway is **simulated** (`PAYMENT_GATEWAY=sim`); real
  Zarinpal is a go-live switch, not a build item.

### What exists today, feature-wise (for anchoring)
- **Moadian**: submission per business (mock/sandbox path built; real submit pending),
  status inquiry (استعلام وضعیت, MD-2), patterns implemented: نوع اول/الگوی اول + نوع
  دوم/الگوی اول only — all other patterns (ارز، طلا، پیمانکاری، قبوض، صادرات، …)
  raise «unsupported» (normalizer registry).
- **استعلام مودی (buyer taxpayer inquiry)**: customer records store last-inquiry
  freshness (MOADIAN B.5) — the plumbing exists; it is not a priced SKU.
- **Excel import**: invoice drafts (`invoice_drafts/application/excel_import.py`) +
  accounting xlsx export — shipped, not separately priced.
- **Accountant/partner layer**: partner panel, credit-activation («تسویه با همکار»),
  15% default commission ledger — shipped. Partner *access* to a client is free; the
  client pays for `accountant_view`.
- **Payroll (حقوق و دستمزد + بیمه)**: does **NOT** exist. It appears in the blueprint
  only as a future capability list («حقوق و دستمزد، مالیات حقوق، بیمه» — §accounting
  future phase and the Pro-tier sketch). No models, no routes, no UI.

---

## 2. Candidate assessment

### 2a. حقوق و دستمزد + بیمه (Payroll + insurance) — NEW SKU ⭐ recommended new revenue line

**Who needs it:** any merchant with even 1–2 employees — the same
سوپرمارکت/کافه/بازرگانی personas already seeded. Payroll tax + بیمه تأمین اجتماعی
filing is a monthly, deadline-driven pain with real penalty risk; today those
merchants pay a bookkeeper for exactly this. It is the classic "second product"
for SMB accounting SaaS: recurring, sticky, and it deepens the ledger data the
accountant layer and tax_lens already consume.

**What it would take (high level):**
- Employee registry (per business) + contract basics (پایه حقوق، مزایا).
- Deterministic monthly calc: payroll tax brackets (ماده ۸۵/۸۶) + بیمه سهم کارگر/کارفرما
  — rule-based tables, admin-editable like the tax_lens coefficients (the scope freeze
  explicitly endorses rule-based payroll formulas: business_scope_freeze_v1.md line 195).
- Payslip PDF (فیش حقوقی) + a monthly summary the merchant hands to their accountant;
  journal integration later (journal-engine semantics go to the accountant first, per
  the standing rule).
- Explicitly **out of v1**: direct لیست بیمه/salary.tax.gov.ir file upload — start with
  "compute + export", not "submit".

**Suggested price:** **3,000,000 ریال/ماه** — same shelf as `inventory_lite`, below
`base_plan`. Rationale: it is a full workflow (like inventory), clearly worth more than
a report tab (2M), but must not rival the base plan (5M). If per-employee pressure
appears later, keep the flat 3M up to ~5 employees and add a tier — don't start with
per-seat complexity. Attach rate even at 30% of paying businesses makes this the
largest add-on line.

**Cons/risks:** insurance rule tables change yearly and vary by decree — needs the same
admin-managed-coefficient posture as tax_lens (honest-empty when no rate row); getting a
calc wrong damages trust more than a missing feature. Ship behind the accountant-review
rule.

**Verdict: BUILD** (next major SKU after Moadian real-submit stabilizes).

### 2b. Pattern packs (الگوهای بیشتر مودیان: طلا، پیمانکاری، صادرات، …)

Today only الگوی اول (types 1&2) is implemented; the other ~11 patterns raise
«unsupported». Merchants in gold, contracting, export **cannot use Moadian submission
at all** without their pattern — so a pattern is not a luxury add-on, it is the
compliance floor for that vertical.

- **Pros:** each pattern is a well-scoped normalizer mapper + tests; verticals like طلا
  (الگوی سوم) are lucrative niches with few competitors; willingness to pay is high.
- **Cons / the real risk:** charging separately for *compliance itself* reads as
  hostage-pricing («برای قانونی‌بودن فاکتورت باید بخری») — exactly the scary-tax-terms
  tone the product forbids. Also each pattern carries ongoing maintenance as RC_IITP
  revs.
- **Recommendation:** do **not** sell patterns as separate SKUs. Instead price them
  *inside* `moadian_submission` as vertical tiers: keep الگوی اول in the base
  1,500,000 ریال/ماه Moadian SKU, and offer a «مودیان تخصصی» tier at
  **2,500,000 ریال/ماه** covering the merchant's specialty pattern (gold/contractor/
  export). Subscription, not one-time — patterns need maintenance, and one-time sales
  fight the subscription revenue model frozen in business_scope_freeze_v1. Build
  patterns **on demand** (first paying vertical customer), not speculatively.

**Verdict: LATER, as a Moadian tier — never a per-pattern paywall on basic compliance.**

### 2c. استعلام‌ها (inquiry features) — recommend **FREE**

Covers: استعلام وضعیت ارسال (submission status — already part of the Moadian flow) and
استعلام مودی for buyers (customer-record inquiry freshness, MOADIAN B.5 plumbing).

**Argument for free:**
- **Trust:** an inquiry is the moment the product proves it tells the truth about the
  tax organization. Metering that moment breaks the «no scary tax» tone and invites
  users to verify elsewhere.
- **Activation:** free استعلام مودی on customer create is a wow-moment in the ungated
  zone (§8.1 customers are always free) — it pulls fresh users toward the paid Moadian
  and official-invoice features.
- **Data quality feeding paid features:** every free inquiry validates buyer identities,
  which is precisely what makes paid `moadian_submission` succeed on first submit (fewer
  rejections → fewer support tickets → the paid feature *feels* reliable). Charging for
  inquiries would starve the paid feature of clean data.
- Marginal cost is near zero; the tax API is not metered per-call at meaningful cost.
  If abuse appears, rate-limit — don't price.

**Verdict: FREE, permanently; market it as a differentiator («استعلام رایگان و
نامحدود»).**

### 2d. Other plausible candidates (from docs/code)

**Extra businesses (multi_business):** currently the *capability* is free (seeded `0`)
and each business pays its own `base_plan` at 5,000,000 — this is already the correct
per-business monetization and the strongest existing line. Recommendation: keep exactly
as is; consider a bundle later (e.g. 2nd business's base_plan at 4M) only if churn data
demands it. **Skip (already solved).**

**Accountant/partner seats:** partner access is free today; the client pays
`accountant_view` (2.5M) and the partner earns 15% commission. That is deliberately a
*distribution channel*, not a revenue line — charging partners would shrink the channel
that sells everything else. Possible later: a paid «پنل همکار پرو» (bulk tools, white
label) once >20 active partners exist. **Later; do not price seats now.**

**SMS packs:** notification core is SMS-ready (SMS_ALLOWLIST, provider switch, «آخرین
پیامک‌ها»), and SMS has real per-message cost. But reminders/OTP SMS is table-stakes;
metering it punishes engagement. Recommendation: include a fair monthly quota inside
`base_plan`; sell a top-up pack (e.g. 500 پیامک / 1,000,000 ریال, one-time) only for
bulk customer-facing campaigns if that use ever emerges. **Later / cost-recovery only.**

**API access:** nothing in code or docs today; only worth it once accountants/ERPs ask.
**Skip for now** — note it as a future «اتصال نرم‌افزارها» SKU around the
accountant_view price point (2,500,000 ریال/ماه) when demand is proven.

---

## 3. One-page summary

| Candidate | Recommendation | Suggested price (ریال/ماه, monthly like the current list) | Expected effect |
|---|---|---|---|
| **حقوق و دستمزد + بیمه** (new SKU) | **BUILD** — next revenue line | **3,000,000** flat (per business, up to ~5 employees) | Largest new add-on line; deepens stickiness + ledger data; rides existing checkout/entitlement rails |
| **Pattern packs** (طلا/پیمانکاری/صادرات) | **LATER** — as a Moadian tier, on first paying vertical | «مودیان تخصصی» **2,500,000** (base Moadian stays 1,500,000) | Opens locked-out verticals; avoids "pay for compliance" backlash; build per demand |
| **استعلام‌ها** | **FREE forever** | 0 («رایگان») | Trust + activation driver; clean buyer data lowers Moadian rejections, making the paid SKU look reliable |
| Extra businesses | **SKIP** (already monetized) | keep: capability 0 + base_plan 5,000,000 each | Existing per-business engine keeps compounding |
| Partner seats | **LATER** (>20 active partners) | free now; future «پنل همکار پرو» TBD | Protects the distribution channel; 15% commission already aligns incentives |
| SMS packs | **LATER** (cost-recovery only) | quota in base_plan; top-up ~1,000,000 / 500 پیامک one-time | Neutralizes SMS cost without punishing engagement |
| API access | **SKIP** until demand | future ~2,500,000 | Optionality noted; zero build cost today |

**Honesty note:** the only real, seeded prices are the 8 rows in §1 (rial, monthly).
No price exists anywhere for payroll, patterns, SMS, or API — every number in §2/§3
for those is a **proposal** anchored to the existing shelf (1M–5M ریال/ماه), not a
found value. The blueprint's Free/Starter/Professional tier sketch contains no numbers.
