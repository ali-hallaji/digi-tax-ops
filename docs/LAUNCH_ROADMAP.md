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

_As of the PRE-PRODUCTION batch (2026-07-26) every remaining item on this list is
**founder-owned** — there is no engineering work left holding launch. Code-side
readiness is proven: the production bring-up has been rehearsed end-to-end on
throwaway infrastructure and reduced to two commands (§ runbook v3)._

- 🔄 **Real OTP** — Kavenegar provider, API key and `digiotp` template are WIRED and
  configured on dev (Batch 5.6). `SMS_ALLOWLIST=09120000000` still restricts delivery
  to the founder's number. Remaining: founder confirms receipt of a real SMS, then
  empties the allowlist for production. No code work left.
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

## Launch Batch 4 — app shell + consistency + auto-inquiry (pulled forward, DEPLOYED to dev 2026-07-25)
- ✅ **Part 1 — the mobile app shell (headline).** **The Batch-2 diagnosis was re-measured on a
  production build and CORRECTED:** the 99px sideways scroll on every `/app` page was the
  **dev-only «نسخهٔ آزمایشی» badge** (98px). In production the document did NOT overflow — but the
  right cluster still occupied **338px of a 390px viewport**, i.e. one element away from breaking,
  and the owner name was `line-clamp-2` (wrapping to two lines inside a 56px bar). Rebuilt the
  header as ONE row that cannot overflow: a fixed-width start group + a `min-w-0 flex-1` end group
  whose only elastic item (the name) truncates; the name+role render on ONE line («علی حلاجی ·
  مالک») with the full text in `title`; theme, fiscal-year, the quiet logout and the dev badge
  leave the mobile bar for `<AccountMenu>` (`sm:hidden` rows); the sidebar trigger is a real
  44×44 touch target. **Real production overflows the sweep DID find and fix:** `/app/invoices`
  (17px — a three-button action row that did not wrap) and `/app` at 320px (58px — two KPI columns
  whose ریال amounts have no break opportunity). **Mobile drawer auto-closes on navigation**
  (`useCloseMobileSidebarOnNavigate`, wired into all three shells: /app, /admin, /partner); ESC and
  the backdrop already worked. Two silent CSS-cascade bugs found by the grill: the fiscal-year
  switcher's `hidden sm:inline` prefix was overridden by `SelectTrigger`'s `[&>span]:line-clamp-1`
  (145px instead of ~60px at 390px), and `.pill` sets an UNLAYERED `display:inline-flex` that beats
  Tailwind's layered `hidden`. (frontend `d416250`.)
- ✅ **Part 2 — consistency sweep (partial, see the follow-up).** ONE mobile dialog baseline in
  `ui/dialog.tsx` for all 32 dialogs (16px gutter instead of an edge-to-edge slab, rounded at
  EVERY width — it was `sm:rounded-lg`, so phones got square corners — and a `max-h`+scroll cap so
  a tall dialog can never push its footer below the fold); the two deliberately full-screen mobile
  forms (customers/products) keep that intent explicitly. RTL logical properties in
  `ui/dropdown-menu.tsx` (`ps-8`/`start-2`/`ms-auto`) so the check/radio indicator sits on the
  LEADING edge next to its label instead of the far side. ONE `<MoadianEnvTag>` replacing six
  copy-pasted «آزمایشی»/«زنده» chips. **Grill find + fix:** the onboarding tour card positioned
  itself by TOP with a hardcoded 180px height guess and no bottom clamp — on a 390×844 phone
  «بعدی» landed at y=852 and «فهمیدم، دیگر نشان نده» at y=881, both below the fold, so a
  first-time merchant could neither advance nor dismiss the tour. Now clamped against the card's
  measured height. (frontend `d49a648`.)
- ✅ **Part 3 — auto-inquiry after every submission.** The server now polls the org's استعلام by
  itself (backoff `5,15,45`s, own db session, survives closing the page) until a FINAL status
  lands — single, bulk rows, lifecycle docs, returns and correctives all funnel through
  `submit_invoices`, so one hook covers every path. State is PERSISTED
  (migration **`autoinq00013`**: `auto_inquiry_state` + `auto_inquiry_attempts`, additive, no
  backfill) so «در حال دریافت وضعیت از سامانه…» → the final interpreted state survives a reload,
  and a poll interrupted by an api restart reads as `exhausted` instead of spinning forever. On
  exhaustion the panel shows the calm «وضعیت هنوز از سامانه دریافت نشده» and the manual
  «به‌روزرسانی وضعیت» button stays as the founder-explicit fallback. No double-polling (in-process
  guard + a DB re-check before each org call); idempotent with the manual button (a final status
  closes the auto state, and the next tick makes NO org call). Bulk follows every row with ONE
  business-scoped read every 4s, never one request per row. (backend `a21b77c` · frontend
  `904c924`.)
- ⬜ **Part 2 follow-up (explicitly not done today):** card-padding rhythm is still drifted —
  `rounded-2xl border bg-card` appears with `p-4` (35×), `p-5` (78×), `p-6` (54×). Normalising 167
  call sites is a mass edit with real regression risk and reads as a redesign, so it is a
  standalone task with its own screenshot pass. Same for table→card at 390px (tables scroll
  correctly inside `overflow-x-auto` but carry no visible «swipe» affordance) and the ~28
  hand-rolled empty states that bypass `<EmptyState>`.

## Launch Batch 5 — official units + OTP bypass safety + live separators (DEPLOYED to dev 2026-07-26)
- ✅ **Part 1 — OFFICIAL UNITS (RC_UMGS.ST_V1.18).** All **102** rows transcribed from the
  founder's PDF into `digi-tax-backend/data/moadian/rc_umgs_st_v1_18_units.csv` and imported
  via the existing `python -m app.cli.import_tax_units` on local + dev. Cross-checked: 102
  data rows, 102 unique codes, no non-numeric codes, no empty titles, and all five founder
  spot-values match (عدد=1627 · کیلوگرم=164 · متر=165 · ساعت=16103 · نفر-ماه=16134). The
  product form auto-upgrades to the official picker as designed — and since 102 options in a
  plain `<Select>` is unusable, it is now a SEARCHABLE combobox (matches the Persian title OR
  the numeric code, Persian digits normalised: «۱۶۱۰۳» finds ساعت). The dormant
  «نیاز به انتخاب واحد رسمی» soft-flag activates by itself now that the catalog is non-empty
  (`_validate_units` skips on an empty set). The three Excel samples left column J empty in
  every row; they now carry real official codes (1627/164/16103), verified against the CSV,
  regenerated by the committed `scripts/fill_sample_unit_codes.py`.
  (backend `8567b92` · frontend `adf125e`.)
- ✅ **Part 2 — OTP BYPASS SAFETY (the launch-blocker's safe half).** The Kavenegar API KEY is
  genuinely absent — see the one-line ask in the report and in «Founder's parallel queue»
  below. The PROVIDER was already fully wired from earlier work (Verify/Lookup, `digiotp`
  template, notification_log audit, failure never breaks the caller), so what this batch adds
  is the thing that must exist BEFORE a key is ever pasted in: a per-user
  `otp_delivery_bypass` flag (migration **`otpbypass00014`**, backfilled true for every
  existing account because real OTP has never been on, so all of them are test accounts).
  Internal accounts are FORCED to the console provider whatever `SMS_PROVIDER` says —
  short-circuited before `get_provider()` so no kavenegar client is ever constructed for a
  seeded number — and are the only accounts allowed an on-screen OTP hint; the env flag alone
  is no longer sufficient. Both seeders now flag every account they touch. Admin toggle
  («حساب داخلی») on the user detail, audited in Persian. **Fixed a pre-existing bug found on
  the way:** `/admin/users/$userId` was unreachable — `_admin.admin.users.tsx` acted as a
  layout with no `<Outlet/>`, so the whole user-detail page never rendered; converted to
  `.index.tsx` like `businesses`/`my-clients` already are.
  (backend `16633eb` · frontend `eb482fd`.)
- ✅ **Part 3.3 — LIVE THOUSAND SEPARATORS.** The shared `DecimalInput` formatted only on
  blur, so a merchant typing ۲۵۰۰۰۰۰۰ saw an undifferentiated digit run until they clicked
  away — exactly when a zero too many goes unnoticed. It now regroups on every keystroke with
  a CARET-SAFE algorithm (the caret is re-placed after the same number of DIGITS it preceded,
  so mid-number edits do not jump to the end). Storage is unchanged: it still emits a clean
  ASCII decimal string. (frontend `fbbab7b`.)
- ⬜ **Part 3.1 — party linkage on money flows: NOT STARTED.** Needs a migration plus changes
  across expenses/payments and the party-balances report; it is a data-model change to money
  records and must not be half-shipped.
- ⬜ **Part 3.2 — manual journal vouchers: NOT STARTED.** Needs its own migration, balanced
  debit/credit validation, the locked-auto-voucher rule, numbering alongside auto vouchers and
  export coverage. Note also the standing rule that journal-engine SEMANTICS go to the
  accountant before implementation — the founder has now had a second accountant review, so
  this is unblocked, but it is a full part, not a slice.
- ⬜ **Part 3.3 remainder — migrate the ~45 hand-rolled money inputs.** `DecimalInput` is used
  by only the 7 invoice-line fields; purchases, payments, accounts, customers, vendors,
  cheques, returns and four admin pages each hand-roll the blur-only pattern (52
  `formatDecimalForInputDisplay` call sites). Mechanical but touches every money form, so each
  needs its own browser pass.
- ⬜ **Part 4 — anti-confusion navigation pass: NOT STARTED.**

## Launch Batch 5.5 — Kavenegar prep + founder tweaks (DEPLOYED to dev 2026-07-26)
**Founder decisions recorded (permanent):**
- **Moadian SKU stays SELLABLE on dev** — dev is the founder/accountant test bed and
  they must be able to walk the real purchase. The «به‌زودی» state is a **PRODUCTION
  policy**, driven by `module_prices.moadian_submission.active` (admin panel or a seed
  flag), NOT by code. Harness spec 08 no longer hard-codes either state: it asserts the
  Moadian card is in a coherent state that the environment actually declares, so the
  same spec is honest-green on dev and in production.
- **Auto-inquiry first poll is NOT immediate** — a random 3–7s wait
  (`MOADIAN_AUTO_INQUIRY_FIRST_POLL_MIN/MAX_SECONDS`), then the existing backoff. The
  org needs a moment to process a fresh packet, and the jitter stops a bulk send from
  hitting inquiry in lockstep. The backoff still measures FROM THE SEND (asserted:
  4s jitter → +1 → +10 → +30 for a 5/15/45 schedule).
- **Header shows the NAME ONLY** — the role line («مالک» …) is gone; the role stays in
  the account menu. Re-proved at 390px: one line, 0px overflow on 3 core pages.

- 🔄 **Part 0 — Kavenegar activation: BLOCKED on the key itself.** No key exists in any
  env (local, backend, ops, `.deploy.env`, the dev server) and none was supplied — the
  batch instruction carried the literal placeholder `<provided>`. Everything that does
  NOT need the secret landed:
  - **`.gitignore` gap CLOSED** — `digi-tax-frontend/.gitignore` had only `.env`, so
    `.env.production` was committable. Now `.env.*` + `!.env.example`; verified with
    `git check-ignore` and confirmed no env file is tracked in any repo.
  - **The non-allowlisted behaviour was VERIFIED and FIXED.** It is a *silent* no-send:
    `SMS_ALLOWLIST` suppresses the send, the API still answers `otp_sent`, and a real
    non-allowlisted person sees «کد ارسال شد» and waits forever for an SMS that is never
    coming. The OTP response now carries `delivery_notice` when nothing was delivered,
    and the login page shows the calm «ارسال پیامک در حال حاضر محدود است — لطفاً کمی
    بعد دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.» instead of a false success. The
    message deliberately never explains WHY (the allowlist is internal).
  - Env lines + the allowlist-open one-liner are in the batch report.
- ✅ **Part 1 — party linkage: DONE in Batch 5.6.**
- ✅ **Part 2 — manual journal vouchers: DONE in Batch 5.6.**
- ✅ **Part 3 — separator rollout: DONE in Batch 5.6.**
- ✅ **Part 4 — anti-confusion navigation: DONE in Batch 5.6.** The
  «ورود اطلاعات از نرم‌افزار قبلی» entry ships as a calm Settings placeholder; the real
  importer stays BLOCKED on the accountant's sample export files (هلو / سپیدار /
  حسابان) — a dedicated batch maps customers/products/opening balances from the REAL
  formats. **No guessed mappings.**

## Launch Batch 5.6 — party linkage · manual vouchers · separators · navigation (2026-07-26)
The four parts deferred from 5.5, plus the Kavenegar key finally landing.

- ✅ **Part 1 — PARTY LINKAGE ON MONEY RECORDS (headline).** «طرف حساب» on an expense
  was FREE TEXT, so a salary paid to a real person was invisible to the party reports.
  Migration **`expparty00015`** (additive, NOT backfilled) adds `party_type` +
  `customer_id`/`vendor_id` with FKs, partial indexes and a CHECK that exactly one side
  is set; `party_name` survives as the DISPLAY copy, denormalized from the party on write
  and **no longer accepted from the client**, so the label can never disagree with the
  link. The party is REQUIRED on a new expense (Persian 422 `PARTY_REQUIRED`) and resolves
  ONLY inside the caller's tenant (the id is client-supplied — covered by a test).
  Legacy rows keep their historic text with NULL FKs under a calm «نیاز به انتخاب طرف»
  badge and reopen with the picker EMPTY, so editing one never blesses the old text.
  ONE shared `<PartyPicker>` (searchable, SERVER-side search, inline «افزودن … جدید»)
  serves both the expense dialog and the manual-payment dialog — which required a party
  but offered no way to create one, i.e. an empty vendor list was a dead end mid-form.
  **Accounting decision, stated:** the party-balances report gains `settled_total` +
  `expense_total` as FLOWS beside the balance and deliberately NOT folded into it — an
  expense carries a mandatory treasury account, so it is incurred AND paid in one act and
  adding it to the payable would invent a debt that was never owed. Whether an expense
  should ever move a party's مانده is an accountant decision, logged OPEN.
  (backend `c794723` · frontend `79f8f12`, `1a4dc43`.)
- ✅ **Part 2 — MANUAL JOURNAL VOUCHERS hardened.** The T4 سند دستی already existed
  (create/edit/delete, balance validation, live Σ diff, «دستی» pill, regenerate-safe), so
  this part closed the four gaps a grill found. **A real 500:** `entry_no` was
  `max(entry_no)+1` under UNIQUE (tenant_id, entry_no), so a double-tapped «ثبت سند» or
  two tabs raced and the loser's INSERT surfaced raw — the same class as the Batch 2
  chart-template race. Now a per-tenant `pg_advisory_xact_lock` with an
  IntegrityError→409 retry behind it, proven by a two-connection race test. **Audit**
  (migration **`manaudit00016`**): create/edit/delete append a `manual_entry_events` row
  with a full snapshot; `entry_id` carries NO FK so the trail outlives the سند, and the
  row is written inside the caller's transaction so a rejected سند leaves no phantom
  trail (asserted). **FY lock** on POST/PATCH. **Exports:** journal.csv/.xlsx gain the
  «نوع» column — دستی vs خودکار had existed only as a UI pill. **Locked auto vouchers**
  now say so: «این سند از [مبدأ] ساخته شده — برای تغییر، مبدأ را ویرایش کنید» + link.
  (backend `99cf65c` · frontend `9457d90`.)
- ✅ **Part 3 — SEPARATOR ROLLOUT COMPLETE.** All remaining hand-rolled blur-only money
  inputs moved onto the live caret-safe `DecimalInput`: purchases/expenses (7), payments
  (2), accounts (2), cheques, customers, vendors, products, settlement splits, return lump
  sum, the سند دستی debit/credit cells, and four admin surfaces. The local
  `formatAmountBlur`/`stripAmountFocus` pair is retired. Storage is unchanged — the
  component still emits a clean ASCII decimal string, so every payload is byte-identical.
  (frontend `87fef12`… see `87d0b80`, `1a4dc43`.)
- ✅ **Part 4 — ANTI-CONFUSION NAVIGATION.** The findability walk found four real
  problems: the FIRST sidebar group was «راه‌اندازی» (setup) yet held the daily selling
  and buying work; «هزینه» had no menu entry at all (it hid in the second tab of «خرید و
  هزینه»); «سند دستی» sat two levels deep; and nothing told a merchant which of the four
  documents they wanted. Groups are now the questions being asked — خانه · فروش · خرید و
  هزینه · پول و گزارش · نمای حسابدار · تنظیمات — with nothing removed and the two missing
  entries added. `<NewDocumentMenu>` is ONE «سند جدید» button (sidebar + dashboard) asking
  «چه اتفاقی افتاده؟» over فروش / خرید / هزینه / سند دستی حسابداری, each with the
  plain-language tell that separates them; «سند دستی» appears only when the accountant
  view is on. `/app/expenses` is a real deep-link (`?tab=expenses`, URL-driven so Back and
  sharing work) and each tab states the خرید-vs-هزینه difference out loud. Guide gains
  **S4-00** «سند فروش، خرید و هزینه — تفاوت و جای هرکدام» (starter #1). Settings gains the
  calm «ورود اطلاعات از نرم‌افزار قبلی (هلو، سپیدار، حسابان…)» placeholder.
  (frontend `84b546a`.)
- ✅ **Part 5 — the grill's own findings, fixed** (`0762673`): the party picker asked for
  `page_size=200` against a `MAX_PAGE_SIZE=100` server and 422'd on every open — fixed by
  moving the search SERVER-side rather than shrinking the page; «خریدها» stayed highlighted
  while «هزینه‌ها» was open (two entries, one path → the active state now reads the tab),
  which then produced a duplicate React key; and the legacy badge wrapped to three lines at
  390px.
- **Test hygiene found on the way:** two SMS tests read ambient env and went red the moment
  a real `KAVENEGAR_API_KEY` landed in `.env` — both now pin what they assert. One stale
  payments assertion expected 204 from a route that has always returned 200 + {status,id}.

## FINISH-LINE batch — sandbox verdict · the school · thread sweep · production prep (DEPLOYED to dev 2026-07-26)

- ✅ **Part 1 — 14007/14004 CLOSED, empirically.** First, the Batch-3 claim that
  «MOADIAN_BASE_URL is empty on dev» was CORRECTED: it only affects the LIVE leg;
  sandbox routing is per-tenant with its own default. The نیک‌تجارت cockpit
  connection test passes from dev (`ok: true`, `fiscal_status: ACTIVE`, via the
  SOCKS egress; both org hostnames answer through the tunnel). Then the deferred
  experiment: two otherwise-identical correctives differing ONLY in inp/inty —
  present → `"warning": [14007, 14004]`, omitted → `"warning": []`. Adopted:
  referring subjects (ins 2/3/4) now drop both from the EMITTED header while the
  mapper still uses them to choose the pattern (an unsupported combination is
  still refused — asserted). Write-up:
  `docs/moadian/corrective_inp_inty_experiment_2026-07.md`; matrix follow-up
  closed. (backend `2a3184b`.)
- ✅ **Part 2 — «مدرسه — از صفر تا صد» (headline).** A DOING school, distinct in
  kind from the existing conceptual one: twelve lessons that take the merchant's
  own business from empty to a full picture. Each lesson is exactly three blocks —
  چرا (two plain lines) · «حالا این را انجام بدهید» (ONE deep-linked action with
  the control named) · «حالا اینجا را ببینید» (where the effect landed). Progress
  is per-BUSINESS and persisted. Content-accuracy law honoured: all 24 links
  loaded in the running app, lessons 1 and 9 followed literally.
  (frontend `2180fd6`.)
- ✅ **Part 3 — thread sweep (4 of 6 done, 2 deferred with reasons).**
  ✓ raw `utilities` → «قبوض» (label map fixes existing rows with no migration).
  ✓ زهرا محمدی (09120001004) seeded the fixed password (founder-approved) and
    CLAUDE.md §4.6 corrected — three other personas remain dev-OTP-only and are
    now named rather than misdescribed.
  ✓ accrual backfill documented as a one-time-per-environment runbook step.
  ✓ inventory-lite end-to-end re-verified: 0 → buy 10 → sell 3 → return 1 → **8**.
  ⬜ **E5–E7 matrix rows NOT walked** — deferred, see progress.md.
  ⬜ **Issued-cheque پاس** — deferred, see progress.md.
- ✅ **Part 4 — production readiness (everything not needing the datacenter).**
  Nightly `backup_db.sh` (7 daily + 4 weekly, dumps from inside the container to
  the host, a <10 KB dump is renamed `.SUSPECT` rather than counted) installed as
  a systemd timer on dev and PROVEN by a real triggered run. `restore_db.sh`
  restores into a SCRATCH database and prints row counts — REHEARSED, not assumed
  (123 MB dump → tenants 14 · users 19 · customers 327 · products 170 ·
  invoice_drafts 842 · journal_entries 1633 · accruals 4). `env.production.template`
  with the reason each var matters plus an explicit «must NOT appear» list. Deploy
  runbook v2: an 8-step production bring-up checklist with the DNS/TLS/egress
  steps marked ⏸ pending the datacenter decision. (ops `6df6458`.)

## PRE-PRODUCTION batch — rehearsed migration · E5–E7 · cheque پاس (2026-07-26)

**Part 1 — fresh-reference sandbox chain + cheque.** Registered a FRESH اصلی on
نیک‌تجارت (INV-2026-000037, ins=1 accepted, taxid `A2HP…876`) and walked the whole
lifecycle on it, because sandbox records rotate. **E6**: a second «صدور اصلاحیه»
while a draft is open → 409, no second draft, friendly «یک پیش‌نویس اصلاحیه برای این
صورتحساب باز است — همان را تکمیل یا لغو کنید.» **E7**: deleting the corrective draft
left the original نهایی‌شده/ثبت‌شده AND re-correctable (a new draft was created after).
**E5**: ابطال accepted (ins=3, taxid `A2HP…882`, both legs `accepted` with NO error
code — the referring-subject inp/inty drop holding), after which «صدور اصلاحیه» is
disabled with «این صورتحساب باطل شده — صدور اصلاحیه مجاز نیست.» Matrix E5/E6/E7 now ✅
and a standing **SANDBOX ROTATION LAW** was added as canonical rule 8: every lifecycle
experiment registers its own fresh اصلی; a `0300601` on an old reference is expected
rotation, not a regression. **B8b**: issued cheque #PASS-E8-001 (۲۵٬۰۰۰٬۰۰۰ on بانک
ملت) moved NO money while «در جریان», then پاس شد → balance ۱٬۰۴۱٬۰۰۲٬۰۰۰ →
۱٬۰۱۶٬۰۰۲٬۰۰۰, exactly −۲۵٬۰۰۰٬۰۰۰. Grill fix: the lifecycle block reasons lived only
in tooltips, unreachable on touch — now also rendered as inline text (§8.4).

**Part 2 — production migration REHEARSED (the headline).** Stood up a throwaway
prod-shaped stack on the dev host (own project, env, ports, network, volume; dev's
resolved compose config proven byte-identical and its containers never restarted),
ran the runbook end-to-end, tore it down, and ran it again from nothing. **Eight
findings, all fixed** — hardcoded `container_name` / `env_file` / ports (a second
stack would have silently written to the FIRST stack's database), a **missing
create_admin CLI**, an import command whose documented path does not exist, an
unexported `BACKEND_SHA`, an **admin-before-backfill ordering bug that only the
second clean run exposed**, and backup/restore scripts that always targeted the
default project. Steps 2–7 are now one script (`prod_bring_up.sh`); verification is
`prod_smoke.sh` + exactly one prod-safe harness spec. The final clean run completed
with **zero improvisation** (exit 0) and 8/8 smoke green. Documented honestly: on a
`DEBUG=false` stack no automated spec can log in, so one manual founder login with a
real OTP is a mandatory, non-automatable gate. Runbook is now **v3 (REHEARSED)**.
Teardown verified complete; dev preflight green afterwards.

**Part 3 — closers.** The three password-less personas (…1005/1006/1007) now carry the
fixed `Admin@12345` (founder-approved, credentials-only — identities and counts
untouched); `world_fixtures.py`, `persona_logins.md`, `persona_fixtures.json` and the
README table regenerated from the single source, and کامران سعیدی's login proven
through the REAL login page (Altcha solved by the real widget). Roadmap hygiene: every
remaining launch blocker is now founder-owned.

## Launch Batch 3 — partner panel v2 (DEPLOYED to dev 2026-07-26)
- ✅ **Part 1 — COMMISSION MODEL, admin-controlled (headline).** Commission used to be
  DERIVED ON READ (`amount × the partner's CURRENT percent`), so the first rate change
  would silently rewrite every figure a partner had ever been shown and «چقدر تیر بهش
  بدهکار بودیم؟» became unanswerable. Migration **`partner2t00017`** replaces it with
  real **snapshot accruals**: `partner_commission_accruals`, one row per (revenue event,
  earning partner, tier), carrying the rate AS IT WAS. UNIQUE on that triple ⇒ replaying
  revenue can never double-pay; written in the SAME transaction as the revenue event
  (an accrual outliving a rolled-back payment would be money we never earned); a refund
  **reverses** (status + reason), never deletes.
  **TWO TIERS, exactly.** `parent_partner_profile_id` is the recruiter. The sub-partner
  is NOT docked — tier 2 is paid by us on top. The «exactly two levels» rule is
  ENFORCED: a partner who already has a recruiter cannot become one, and a partner with
  children cannot be given a parent (both would open a third level).
  **RATES:** global defaults in `partner_commission_settings` — append-only and
  effective-dated, so a change is a new row and the old rate stays readable. Per partner,
  `commission_percent` / `tier2_commission_percent` override from
  `commission_effective_from` onward, so raising a rate mid-month does not retroactively
  repay the first half. Every admin change lands in the ONE unified `admin_audit_log`.
  (backend `60705a9`.)
- ✅ **Part 2 — REVENUE DASHBOARDS (the «سر ماه پولش را بگیرد» promise).** Partner side:
  the two tiers in the partner's own words («سطح ۱ — معرفی‌های خودتان» / «سطح ۲ —
  معرفی‌های زیرمجموعه‌های شما») with the honest line «از سهم آن‌ها کم نمی‌شود»; a partner
  who recruited nobody never sees the second card. «در انتظار تسویه» is a headline
  number, months carry their tier-2 portion and can read «تسویهٔ ناقص», and per-client
  rows carry a سطح ۲ tag so a tier-2 figure is always explainable. Admin side: a new
  **/admin/settlements** — one page per Jalali month, per-partner tier-split totals,
  exact pending vs settled, month stepper (URL-driven), «ثبت تسویه» with the owed amount
  pre-filled, and an Excel export for the bank run. `admin_add_payout` now STAMPS the
  accruals it covers with its `payout_id`, which is what makes pending-vs-settled EXACT
  instead of inferred from a payout period overlapping a month.
  (frontend `f587587`, `2631cd4`.)
- ✅ **Part 3 — demo world + real-UI proof.** `seed_commission_world` (also called by the
  full seeder) wires آرش رستمی (HAM-TEST2) as a sub-partner of خانم محمدی (HAM-TEST1),
  gives her a 5% tier-2 rate, and runs the REAL accrual engine over every seeded revenue
  event — the demo numbers come from the same code path production uses. Shipped as a
  standalone CLI because a full reseed requires a wipe, and the wipe guard correctly
  refuses while نیک‌تجارت holds a real Moadian key.
- 🔄 **Part 4 — corrective referring-fields experiment: NOT RUN.** The sandbox
  (tp.tax.gov.ir) is Iran-only and only reachable from the dev egress; it needs a
  dedicated run on dev. The inp/inty «خارج از الگو» (14007/14004) nag therefore remains
  on the accountant question list, unchanged.

---

## Founder's parallel queue (not code — founder-owned)
- ⬜ **Gateway signups** — Zarinpal and/or Zibal merchant approval → creds (Batch 1 Part 3
  ships the adapters; only env lines remain).
- ⬜ **Kavenegar API KEY** — **CRITICAL launch blocker** (real OTP). The TEMPLATE is settled
  (`digiotp`, already the config default and visible in the admin «آخرین پیامک‌ها» rows); the
  provider, the audit trail and the bypass safety net all ship as of Batch 5. **The only thing
  missing is the API key itself** — paste it into the dev/prod `.env` as `KAVENEGAR_API_KEY`
  and flip `SMS_PROVIDER=kavenegar`; no code change.
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

_Last updated: 2026-07-26 (FINISH-LINE — 14007/14004 closed empirically, «مدرسه — از صفر تا صد», thread sweep, production prep; Launch Batch 3 — partner panel v2: two-tier snapshot commission, settlement run; Batch 5.6 — party linkage, manual-voucher hardening, separator rollout complete, anti-confusion navigation; Batch 5.5 — Kavenegar prep, founder tweaks; Batch 5 — official units, OTP bypass safety, live separators; Batch 4 pulled forward — mobile app shell, consistency pass,
server-side Moadian auto-inquiry; harness now 13 spec files / 14 tests)._
