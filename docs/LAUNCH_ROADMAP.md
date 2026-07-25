# LAUNCH_ROADMAP.md — DigiTax pre-launch tracker (founder-ordered, permanent)

Standing pre-launch roadmap. **Launch is THIS WEEK** (created 2026-07-24). This doc is
the single tracker for everything between now and public launch. **Every future batch
updates this doc in the SAME commit** — mark items ✅ done / 🔄 in-progress / ⬜ not
started, and add new items as they surface. It never goes stale.

> Rule of the road (workspace CLAUDE.md §2 + invoice_flow_matrix.md HARD LAW): proof =
> real UI journeys on dev. Small commits per part. Guarded dev deploy at the end
> (compose v2, `--no-cache`, alembic, psql-verify). Harness green local + dev
> (12 spec files / 13 tests as of Batch 2 Part 4).

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

## Launch Batch 2 — landing + overflow + corrective-empirical + Excel + CoA templates + re-mine (DEPLOYED to dev 2026-07-25)
Combined batch. **New standing laws** added to workspace CLAUDE.md §2: EMPIRICAL-TEST LAW
(sandbox answers beat doc citations) + GRILL-ME LAW (hostile-test before DONE).
- ✅ **Part 1 — text-overflow sweep.** Fixed the reported bug (a long stuffid name shattered
  the items step): `min-w-0` on the items-step 1fr grid column. Also clamped the print-view
  line cell, the header owner name (two-line + title), the Moadian org message + interpreted
  chip (org-verbatim), and products/vendors table name cells. (frontend `e1f2dcf`.)
- ✅ **Part 2 — corrective items EMPIRICAL verdict (headline).** Sandbox on نیک‌تجارت:
  **ADD-line ACCEPTED** (taxid …916817), **REPLACE-sstid REJECTED** (taxid …916829); REMOVE +
  qty/price already ACCEPTED (MOADIAN F). So the corrective wizard now shows the add-line form
  (the old «نمی‌توان ردیف افزود» lock was a doc-guess the org disproved); existing-line sstid
  stays locked with the org's behaviour as the stated reason. `docs/moadian/
  corrective_experiments_2026-07.md` + `scripts/corrective_experiment.py`. (frontend `e1f2dcf`
  · ops `7493780`.)
- ✅ **Part 3 — Excel import sync.** Audit found the importer already handles نوع/الگوی‌پیمانکاری+crn/
  unit/sstid and the samples are in sync; added «اصلی-only» to the import dialog + fixed the stale
  «not implemented» contract line + documented the A–L schema. (frontend + backend-doc.)
- ✅ **Part 6 — public landing + SEO.** `/` is now a public SSR marketing page (four merchant
  questions + Moadian, outcome blocks, «شروع رایگان ۱۴ روزه» teaser, FAQ, footer + اینماد slot);
  logged-in → «ورود به پنل»; deep capabilities hidden. SEO: per-route head + JSON-LD (Org+Software+
  FAQ), robots.txt, sitemap.xml, webmanifest, theme-color; killed the __root duplicate-description
  + Lovable placeholder OG. /app guard intact. Landing smoke spec. (frontend `87fef12`.)
- ✅ **Part 4 — chart-of-accounts default templates** (accountant suggestion). «افزودن حساب‌های
  پیش‌فرض» on the accountant-view chart page: picker (خدماتی/بازرگانی/تولیدی/پیمانکاری) →
  PREVIEW («این حساب‌ها اضافه می‌شوند: …», writes nothing) → apply. **Additive only** — never
  deletes/renames/re-codes; idempotency key is (parent, exact title) so a re-apply is a true
  no-op and an archived template account is NOT resurrected; codes continue the existing scheme
  (کل `15`/`16`/`54` under گروه, معین `1501`…). Audited via the new append-only
  `chart_template_events` (migration **`coatpl00012`**), `TaxConfigEvent` discipline. Template
  accounts are `is_system=false`, and `chart_admin` now lets a NON-system کل be renamed/archived,
  so an additive template stays reversible (the seeded skeleton is frozen by `is_system`, not by
  level). **GRILL found + fixed a real 500:** a double-tap fired two applies that allocated the
  same codes → `uq_chart_accounts_tenant_code` violation as a raw 500 (gotcha #4/#13); fixed with
  a per-tenant `pg_advisory_xact_lock` + an `IntegrityError`→friendly-409 guard, with a real
  two-connection race test. Drafted trees for the founder's accountant:
  `docs/accounting/coa_templates_for_accountant_review.md` — **still pending their blessing**, so
  the picker shows «پیشنهادی — قابل ویرایش». Guide gains **S9-11**; S9-06 links it.
- ✅ **Part 5 — PDF re-mine, all findings FINAL.** `scripts/remine_wire_probe.py` (read-only)
  answered #3/#4/#6 on the نیک‌تجارت sandbox per the EMPIRICAL-TEST LAW:
  **#3 حد مجاز فروش → CLOSED**, `GET_FISCAL_INFORMATION` returns exactly four keys and no
  sales-limit field; **#6 article6Status → CLOSED**, absent from all 61 recorded inquiry
  responses AND a fresh live inquiry; **#4 taxpayerStatus → WIRED** — our map already covered
  every documented value, but the org answers an unknown economic code with an EMPTY body, which
  we rendered as «نامشخص»; the response now carries `found` and the UI says «در سامانهٔ مودیان
  یافت نشد». Nothing speculative wired. Table + verbatim wire evidence:
  `docs/moadian/pdf_remine_2026-07.md`.
- ✅ **Part 7 — real OG share image.** `public/og-image.png` (1200×630, brand teal + logo +
  Vazirmatn, says only what the public landing says); absolute `og:image`/`twitter:image` +
  width/height/alt on «/» and as a site-wide default in `__root.tsx`. Landing harness spec now
  hard-asserts the tags AND that the asset really returns 200 `image/png`. Closes the last SEO
  to-do from Part 6.

## Launch Batch 3 — partner panel v2 ⬜
- Per-partner **admin-set commission %** (currently a single global/implicit rate).
- **Two-tier referral commission** (referrer of a referrer earns).

## Launch Batch 3 — partner panel v2 ⬜
- Per-partner **admin-set commission %** (currently a single global/implicit rate).
- **Two-tier referral commission** (referrer of a referrer earns).
- **Revenue-stream dashboard** for monthly partner payout (what each partner is owed).

## Launch Batch 4 — global UI consistency sweep ⬜
- Header **two-line owner name** (long names wrap correctly).
- **Mobile sidebar** must NOT auto-close on navigation.
- **Flaky mobile top bar** — **now precisely diagnosed (Batch 2 Part 4 grill).** The header's
  right cluster `src/routes/_app.tsx:244` (`flex items-center gap-1.5`) measures **437px inside a
  390px viewport**, so EVERY `/app/*` page scrolls sideways by **99px** with no dialog open —
  measured on `/app/customers` and `/app/accounting/chart`. It is not dialog-related (dialogs sit
  correctly at x=0, w=390). Likely fix: `min-w-0` on that container + let the business-switcher
  label truncate. NOTE the local measurement includes the dev-only «نسخه آزمایشی» badge
  (`import.meta.env.MODE !== "production"`), so re-measure on a production build before sizing
  the fix.
- App-wide consistency pass (tokens, RTL, dialog footers, empty states).

---

## Founder's parallel queue (not code — founder-owned)
- ⬜ **Gateway signups** — Zarinpal and/or Zibal merchant approval → creds (Batch 1 Part 3
  ships the adapters; only env lines remain).
- ⬜ **Kavenegar** template + API key — **CRITICAL launch blocker** (real OTP).
- ⬜ **Accountant answers** (the questions blocking correct Moadian/tax behavior):
  - **Chart-of-accounts default trees** (Batch 2 Part 4) — bless or correct the four drafted
    trees in `docs/accounting/coa_templates_for_accountant_review.md` (five specific questions
    are listed at the top of that doc). The feature is LIVE and safe either way; until they are
    blessed the picker carries «پیشنهادی — قابل ویرایش», and removing that note is the only
    code change their answer triggers.
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
- **Data-migration importer from Holoo / Sepidar / Chortkeh** — an Excel importer that maps
  the common Iranian SME accounting exports (Holoo هلو, Sepidar سپیدار, Chortkeh چرتکه) into
  DigiInvoice customers/products/opening balances, so a switching business brings its history.
- **Issuance UX overhaul** — the invoice-builder experience redesign.
- **Matrix rows E5–E7** — full UI walks of corrective-on-cancelled, second-open-corrective,
  and the «لغو سند» cancel-draft path (guard+test proven; UI walks deferred).

---

_Last updated: 2026-07-25 (Launch Batch 2 Parts 4/5/7 landed — CoA templates, PDF re-mine finalised, OG image)._
