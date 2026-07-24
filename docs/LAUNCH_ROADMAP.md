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

## Launch Batch 1 — accountant correctness + sellable pricing + payments + profile (IN PROGRESS 2026-07-24)
- 🔄 **Part 0** — this LAUNCH_ROADMAP.md (founder-ordered permanent tracker).
- ⬜ **Part 1 — Cheque ↔ bank-account law** (accountant-mandated). Cheques get a REQUIRED
  `account_id` FK to treasury accounts; وصول credits the linked account, پاس debits it,
  برگشتی moves nothing (money moves ONLY at وصول/پاس — the locked lifecycle). Legacy
  NULL-account cheques get a soft «نیاز به انتخاب حساب» state (never invent an account).
  Form «حساب بانکی» becomes a required select (empty-state → one-tap add bank account →
  return with state). Journal entries reflect the account. **Headline proof:** create
  bank account → received cheque → وصول → balance visibly up on حساب‌های من + report;
  issued پاس → down.
- ⬜ **Part 2 — Hybrid pricing + admin price control.** Current module prices = BASE
  ECONOMY tier; usage ceiling on top. Admin edits EVERY SKU price (effective-from +
  audit; no retroactive change to paid terms). Monthly «اسناد» metering per business
  (finalized invoices + purchases + returns = trial-cap definition); per-plan included
  volume (`BASE_PLAN_INCLUDED_DOCS_PER_MONTH`, `MOADIAN_INCLUDED_SUBMISSIONS_PER_MONTH`,
  env+admin-editable). Calm over-cap: 80% heads-up, 100% «ارتقا یا بستهٔ افزایشی» prompt on
  NEW-doc creation (reads/reports never lock); overage packs via checkout. Per-business
  admin overrides (audited). Plans page = professional tiering («تا X سند در ماه»). Usage
  card «X از Y سند». ui-ux-pro-max consulted.
- ⬜ **Part 3 — Multi-gateway adapter** (env-switched). `GatewayAdapter` interface behind
  the current checkout; adapters: simulated (default), Zarinpal, Zibal. Idempotent
  server-side verify; failed/cancelled → friendly plans state; entitlement activates ONLY
  after verify. Renewal reminders deep-link to checkout. Ships complete + unit-tested
  against recorded response shapes; prints the exact env lines the founder sets on creds.
  *(97%: may resume with notes.)*
- ⬜ **Part 4 — Moadian profile enrichment.** Fetch/refresh org-sourced profile fields in
  cockpit «پروفایل مؤدی» (read-only org values + timestamp) alongside local overridable
  copies (amber «فقط در دیجی‌اینویس اعمال می‌شود» note; never silently overwrite; show diff
  on divergence). اینتاکد/coefficient: surface ONLY if a documented org service returns it;
  otherwise state honestly. *(97%: may resume with notes.)*

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
- **Payroll + insurance SKU** (حقوق و دستمزد + بیمه) — new module.
- **Gold pattern** (الگوی سوم — طلا، جواهر و پلاتین) issuance.
- **300-customer migration** — bulk import path for a real onboarding.
- **Issuance UX overhaul** — the invoice-builder experience redesign.
- **Matrix rows E5–E7** — full UI walks of corrective-on-cancelled, second-open-corrective,
  and the «لغو سند» cancel-draft path (guard+test proven; UI walks deferred).

---

_Last updated: 2026-07-24 (created — Launch Batch 1 in progress)._
