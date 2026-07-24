# LAUNCH_ROADMAP.md — DigiTax pre-launch tracker (founder-ordered, permanent)

Standing pre-launch roadmap. **Launch is THIS WEEK** (created 2026-07-24). This doc is
the single tracker for everything between now and public launch. **Every future batch
updates this doc in the SAME commit** — mark items ✅ done / 🔄 in-progress / ⬜ not
started, and add new items as they surface. It never goes stale.

> Rule of the road (workspace CLAUDE.md §2 + invoice_flow_matrix.md HARD LAW): proof =
> real UI journeys on dev. Small commits per part. Guarded dev deploy at the end
> (compose v2, `--no-cache`, alembic, psql-verify). Harness 10/10 local + dev.

---

## 🚦 Launch blockers (must clear before public launch)
- ⬜ **Real OTP** (Kavenegar template + API key) — the single hardest launch blocker;
  without real SMS, no real user can sign up. Founder's parallel queue.
- 🔄 **Real payment gateway** creds (Zarinpal/Zibal merchant approval) — checkout is
  simulated until then. Adapter ships launch-ready (Batch 1 Part 3); creds are env-only.
- ⬜ **Iran datacenter / egress** decision (Moadian tp.tax.gov.ir is Iran-only; prod
  egress topology + hosting). Founder decision.
- ⬜ **Accountant answers** (below) that gate correct Moadian packets & tax numbers.

---

## Launch Batch 1 — accountant correctness + sellable pricing + payments + profile (DEPLOYED to dev 2026-07-25)
- ✅ **Part 0** — this LAUNCH_ROADMAP.md.
- ✅ **Part 1 — Cheque ↔ bank-account law.** `account_id` REQUIRED at create for both
  directions (the FK + وصول/پاس money-movement already existed — the gap was optional-at-
  create + received never collecting it). Free-text bank name replaced by a required
  «حساب بانکی» select on the «افزودن چک» dialog AND the settlement dialog; empty-state →
  add bank account. Legacy NULL-account cheques get a «نیاز به انتخاب حساب» badge + a
  same-step account pick at وصول/پاس (no invented accounts, NO migration — column stays
  nullable). Tests + contract doc. (SHAs backend `e8d9770` · frontend `2efc308`.)
- ✅ **Part 2 — Hybrid pricing + metering (core).** Monthly «سند» metering (finalized
  invoices + purchases + returns, current Jalali month) vs an included volume
  (`BASE_PLAN_INCLUDED_DOCS_PER_MONTH`=200 env default, per-business admin override via
  tenant_plan_limits). merchant plan payload gains `document_allowance`; DocumentUsageCard
  «X از Y سند» on the plans page with ok/near(≥80%)/over(≥100%) states + upgrade CTA; reads
  never lock. Hard cap `require_document_capacity` at invoice finalize is FLAG-GATED
  (`DOCUMENT_CAP_ENFORCED`, default OFF — measure-first). (backend `64a36ba`.) **Follow-ups
  (below):** overage-pack consumable purchase; admin price effective-from + history; full
  ui-ux-pro-max plans redesign; dashboard usage card.
- ✅ **Part 3 — Multi-gateway adapter.** ZibalGateway added behind the existing
  PaymentGateway Protocol + get_gateway() factory (sim default · Zarinpal · Zibal);
  `PAYMENT_GATEWAY=zibal` + `ZIBAL_MERCHANT_ID`, no call-site change. Callback route
  normalizes BOTH Zarinpal/sim (`Authority`+`Status`) and Zibal (`trackId`+`success`)
  return shapes. Unit-tested vs recorded Zibal bodies. (backend `51b1081`.)
- ✅ **Part 4 — Moadian profile enrichment.** Cockpit «پروفایل مؤدی» card surfaces org
  economicCode/nationalId READ-ONLY + last-refresh, an amber divergence note vs the local
  copy, and the HONEST line that the org returns no اینتاکد/coefficient (exhaustive PDF
  audit — coefficients stay admin-managed). nameTrade stays suppressed. (backend
  `b52663a` · frontend `b52663a`.)

## Launch Batch 2 — landing page + SEO ⬜
Public marketing site / landing page + SEO foundation.

## Launch Batch 3 — partner panel v2 ⬜
- Per-partner **admin-set commission %** (currently a single global/implicit rate).
- **Two-tier referral commission** (referrer of a referrer earns).
- **Revenue-stream dashboard** for monthly partner payout (what each partner is owed).

## Launch Batch 4 — global UI consistency sweep ⬜
- Header **two-line owner name** (long names wrap correctly).
- **Mobile sidebar** must NOT auto-close on navigation.
- **Flaky mobile top bar** (intermittent layout/scroll issues).
- App-wide consistency pass (tokens, RTL, dialog footers, empty states).

---

## Founder's parallel queue (not code — founder-owned)
- ⬜ **Gateway signups** — Zarinpal and/or Zibal merchant approval → creds (Batch 1 Part 3
  ships the adapters; only env lines remain).
- ⬜ **Kavenegar** template + API key — **CRITICAL launch blocker** (real OTP).
- ⬜ **Accountant answers** (the questions blocking correct Moadian/tax behavior):
  - **Referring-subject blank fields** — a نوع دوم اصلاحیه registers but the org returns a
    non-blocking تذکر that inp/inty are «خارج از الگو» (14007/14004). We blank only the
    buyer today; confirm the exact field set to blank on referring subjects (ins 2/3/4)
    before we change the packet. *(see moadian_f_corrective memory / invoice_flow_matrix
    follow-ups.)*
  - **Gold pattern (طلا/جواهر) questions** — الگوی سوم semantics.
  - **Activity coefficients** (ضرایب فعالیت) — values/source for tax-lens.
  - **RC_UMGS.ST** — the official unit-of-measure catalog file (unit catalog ships empty
    until provided).
  - **پیمانکاری crn** — a registered contract number in the کارپوشه to org-prove الگوی ۴.
- ⬜ **Iran datacenter** — hosting/egress decision for prod Moadian.

---

## Post-launch backlog (explicitly NOT pre-launch)
- **Batch 1 Part 2 follow-ups:** overage-pack consumable SKU «بستهٔ افزایش سند» (needs a
  quota/credit model — the entitlement model is boolean, so a consumable pack doesn't fit
  yet; the over-cap prompt currently points to «ارتقا»); admin per-SKU price effective-from
  + price-history table (admin already edits every price with a shallow audit); full
  ui-ux-pro-max plans-page tiering redesign; dashboard usage card; turning
  `DOCUMENT_CAP_ENFORCED` on once pricing is finalized.
- **Batch 1 Part 3 follow-up:** live sandbox rehearsal of Zarinpal/Zibal once merchant
  creds arrive; renewal-reminder deep-link polish.
- **Payroll + insurance SKU** (حقوق و دستمزد + بیمه) — new module.
- **Gold pattern** (الگوی سوم — طلا، جواهر و پلاتین) issuance.
- **300-customer migration** — bulk import path for a real onboarding.
- **Issuance UX overhaul** — the invoice-builder experience redesign.
- **Matrix rows E5–E7** — full UI walks of corrective-on-cancelled, second-open-corrective,
  and the «لغو سند» cancel-draft path (guard+test proven; UI walks deferred).

---

_Last updated: 2026-07-24 (created — Launch Batch 1 in progress)._
