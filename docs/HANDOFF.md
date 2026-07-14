# Digi Invoice — Session Handoff (2026-07)

---

## ⛔ RESUME NOTE — PX-B interrupted mid-pack (2026-07-14, founder shutdown)

**Trigger phrase: «resume PX-B». Read this block, then continue exactly here.**

### Task state
- **T1 (expense VAT) — DONE end-to-end.** Backend `48af67b` (migration
  `n7o8p9q0r1s2`, inclusive extraction, vat_paid, journal 2402 line, tests) +
  frontend `7eda5d0` (shared VatRateSelector default ۰٪ in ثبت/ویرایش هزینه,
  «شامل … ارزش افزوده» hint, API types, guide S4-06 + school L13 + whats-new
  «ارزش افزوده روی هزینه‌ها» — no-drift done).
- **T2 (admin tax calendar) — backend DONE (`ebddc07`), frontend NOT STARTED.**
  tax_deadlines table (migration `o8p9q0r1s2t3`), softened reminder copy
  «مهلت طبق آخرین اطلاع…», apply_deadline_overrides pure overlay,
  GET/PUT/DELETE `/admin/tax-deadlines[/{kind}/{period_key}]`, tests, contract
  entry. Live-verified via curl (override set → merchant reminder changed →
  override deleted; local DB has NO leftover overrides).
- **T3 (yearly tax tables) — backend DONE (`cd7e3fb`), frontend NOT STARTED.**
  tax_tables table (migration `p9q0r1s2t3u4`, **seeds 1404** from بخشنامه
  ۲۰۰/۱۴۰۱/۴۱; 1405 intentionally unseeded → placeholder derives true),
  estimate_basis in tax-estimates payload, GET/PUT/DELETE `/admin/tax-tables`,
  bracket validation, math-parity tests, contract entry. Live-verified
  (basis=year_1404_table, placeholder=true).

### Precise next step on resume
Frontend admin page for T2+T3 (they share one surface):
1. NEW route `digi-tax-frontend/src/routes/_admin.admin.tax-calendar.tsx` —
   «تقویم مالیاتی»: list from GET /admin/tax-deadlines (kind_label, period_key,
   effective date Jalali, badge «طبق قانون» vs «تمدید شده», note), inline edit
   dialog (JalaliDateField + note «تمدید رسمی تا …» + save via PUT; «حذف تمدید»
   via DELETE when overridden). Pattern: copy
   `_admin.admin.module-requests.tsx` (list+dialog) + AdminPlanCard's
   PlanLimitsEditor. Sibling card «جدول‌های مالیاتی» on the same page: per-year
   bracket editor (rows سقف/نرخ٪ — note API rate is a FRACTION string "0.15",
   UI shows ٪ — add/remove rows, last row بدون سقف, source_note field, sample-
   calc preview computed client-side with the same progressive math, save via
   PUT /admin/tax-tables/{year}).
2. Add sidebar item «تقویم مالیاتی» to `admin-sidebar.tsx` systemItems
   («وضعیت سیستم» group, e.g. CalendarClock icon) — NOT a `soon` stub.
3. API module: add getAdminTaxDeadlines/putAdminTaxDeadline/deleteAdminTaxDeadline
   + getAdminTaxTables/putAdminTaxTable/deleteAdminTaxTable to
   `src/lib/api/admin.ts` (types per backend contract PX-B section in
   `digi-tax-backend/docs/api_contracts_v2_2.md`).
4. Dashboard estimate basis line: `tax-estimate-cards.tsx` (lines ~199-203
   currently render the brackets_placeholder quiet line) — extend to also show
   the basis quietly when `estimate_basis` is `year_{y}_table` for a NON-current
   year (e.g. «بر اساس جدول سال ۱۴۰۴»); types: add `estimate_basis` to
   `TaxEstimatesResponse` in `src/lib/api/types.ts`.
5. No-drift IN THE SAME COMMITS: admin guide (`src/lib/guide/admin-content.ts`)
   gains the tax-calendar job walkthrough (scenario in the system group); admin
   whats-new entry in `src/lib/whats-new.ts`.
6. Then the PX-B wrap: typecheck+build, viewing-only sweep (expense VAT selector
   0/custom, softened reminder copy + override note, admin calendar list+edit,
   bracket editor+preview, dashboard basis line; 390+desktop, light+dark,
   three-questions verdicts), frontend+backend progress.md updates, guarded
   deploy (Step-0 SHA export → build --no-cache → up -d → alembic upgrade head
   (3 new migrations n7o8…/o8p9…/p9q0…) → verify-smoke SHA+head match + live
   smoke: VAT expense on demo tenant → vat_paid moves + journal 2402 line;
   deadline override → reminder date changes), report + captcha/rate-limit state.

### Migrations / tests / state
- 3 new migrations, ALL APPLIED LOCALLY (compose DB head = `p9q0r1s2t3u4`), all
  verified up/down/up. NOT on dev server (dev head = `m6n7o8p9q0r1`).
- Backend suite: 799 pass / 7 known FakeDBSession baseline / 42 skip — zero
  new failures; PG integration (expenses+reminders+reports, 80 tests) green in
  compose. Nothing pending except the frontend work above.
- **NOTHING PUSHED this session** (backend ahead 3: 48af67b/ebddc07/cd7e3fb ·
  frontend ahead 1: 7eda5d0 · ops ahead 2: 70d5745 (PX-A docs) + this note).
  No deploy, no dev migrations.
- Temporary state: captcha toggled OFF twice for dev-OTP curls and RESTORED ON
  + empirically re-verified (OTP request → «تأیید امنیتی ناموفق…»). Local
  compose stack (postgres/redis/api) LEFT RUNNING; frontend dev server NOT
  running. Scratch tokens deleted. Local-only test data: PX-A scratch users
  09355550101/02 (harmless); no leftover tax_deadlines overrides; tax_tables
  contains only the migration-seeded 1404 row. PX-A (previous pack) is fully
  deployed on dev and unaffected.

این سند کاملِ سفر از ابتدای این چت (تصحیح ادمین + معماری مالتی‌تننت) تا اکنون (Part 3 ادمین) را ثبت می‌کند. هدف: هر Claude جدیدی (چه claude.ai چه Claude Code) بتواند بدون از دست دادن context ادامه دهد.

---

## وضعیت جاری — پایان سشن PX-A (2026-07-14) — DEPLOYED روی dev زیر گاردِ version-guard

**PX-A — Onboarding bug + UX surgery pack** (فرانت‌اند، ۶ تسک + داکس) کامل شد،
push و روی `dev.digiinvoice.ir` **دیپلوی guarded** شد. جزئیات کامل:
`digi-tax-frontend/docs/progress.md` (بخش PX-A). خلاصه:

- **T1 (بلاکر):** باگ «چک‌لیست تمام شد ولی داشبورد راه‌اندازی می‌ماند» — ریشه:
  mutation‌های تکمیل‌کننده (`مشتری/کالا/نهایی‌سازی فاکتور`) کوئری `["onboarding"]`
  را invalidate نمی‌کردند. حل + «فعلاً رد شو» per-business + بنر ادامهٔ راه‌اندازی.
  مسیر کامل با کاربر تازه از طریق curl تأیید شد (stage_2 بلافاصله).
- **T2:** «افزودن کسب‌وکار» همیشه visible؛ در سقف پلن → دیالوگ آرام honest-lock
  (الگوی کارت پلن، mailto، بدون دکمهٔ پرداخت قلابی) در سه مسیر (سایدبار، کارت
  /app/businesses، گاردِ /app/onboarding).
- **T3:** ردیف آرام «ورود همکاران» / «ورود مدیران سیستم» در لاگین → همان کانال
  sanitized `?redirect=`؛ تقدم: intent صریح > lastPanel > /app؛ ۸ تست واحد
  (`pnpm test:unit`، runner داخلی Node — dependency جدید صفر).
- **T4:** تنظیمات به ۴ گروه: «حساب من» / «کسب‌وکار» / «حسابداری و همکار» / «پلن»؛
  هیچ کارتی حذف نشد؛ anchor id بخش‌ها اضافه شد؛ ۱۲ ارجاع راهنما در همان کامیت
  به‌روز شد (no-drift).
- **T5:** موتور تور سخت شد: locate با retry → `scrollIntoView(center)` →
  double-rAF settle → measure؛ ResizeObserver + scroll/resize زنده؛ anchorِ
  غایب/مخفی → SKIP در جهت حرکت (هرگز 0,0). زندهٔ اسپات‌لایت بعد از اسکرول تأیید شد.
- **T6:** فوتر سایدبار (مرچنت + ادمین + همکار) → یک ردیف فشرده + DropdownMenu
  (سوییچر رادیویی، افزودن کسب‌وکار با قفل T2، راهنما، تنظیمات، خروجِ جدا).
  اثبات 390px با نمای حسابدار ON: آیتم آخر 770px < فوتر 777px — بدون همپوشانی.

**دیپلوی guarded (اولین اجرای کامل زیر گارد، این سشن):** SHAها:
backend `73fb0fd` (بدون تغییر این سشن؛ همان head پوش‌شدهٔ P8) · frontend
`bedad23` · ops `a82971a`. توالی: Step-0 export SHA → `build --no-cache` →
`up -d --no-deps` → `alembic upgrade head` → **verify:** `/health/version` ==
BACKEND_SHA و image head == DB head `m6n7o8p9q0r1` (psql هم جدول‌های
`reminders`/`partner_module_requests` را تأیید کرد) · `pg_index NOT indisvalid`
= **0** · `random_page_cost=1.1` اعمال و reload شد · `/version.json` ==
FRONTEND_SHA. همه `docker compose` v2. Captcha لوکال موقتاً برای dev-OTP خاموش
و **دوباره ON + verify** شد؛ روی dev طبق کانفیگ سرور ON.

Sweep viewing-only: ‏۱۷ اسکرین‌شات در `qa-screens/pxa-20260714/` — سه‌سوال PASS؛
فلوهای تایپی (لاگین OTP، ویزارد، فرم‌ها) برای QA دستی founder.

**یافته‌های دیپلوی (follow-up):**
- `scripts/smoke_test.sh` روی سرور در چک CORS **fail می‌شود چون Origin را
  `http://127.0.0.1:8080` هاردکد کرده** — روی dev فقط `https://dev.digiinvoice.ir`
  در allowlist است (رفتار درست backend). دستی با Origin واقعی verify شد (200 +
  `access-control-allow-origin`). فیکس اسکریپت: Origin را از env بگیرد. بخش
  OTP اسکریپت هم روی dev با captcha ON ذاتاً قابل عبور نیست — smoke کامل فقط
  لوکال سبز می‌شود؛ روی سرور از گارد deploy-verification (standalone) استفاده شد.
- timing گزارش سنگین روی dev ثبت نشد — dev دادهٔ prod-shape ندارد؛ اندازه‌گیری‌های
  P8 در `db-audit.md` (لوکال، ۲.۴M ردیف) معتبرند. `random_page_cost=1.1` روی
  postgres سرور ALTER SYSTEM + reload و verify شد (`SHOW` → 1.1).
- `.env` سرور `DEBUG=true` دارد (pre-existing، برای dev-OTP در پاسخ API) —
  قبل از prod باید خاموش شود (در چک‌لیست pre-prod موجود).

---

## وضعیت قبلی — پایان سشن (2026-07-13) — COMMITTED + PUSHED به origin/main · deploy روی dev هنوز انجام نشده

همهٔ کارهای زیر کامل، commit و به `origin/main` **push** شده‌اند. اما **هنوز روی
`dev.digiinvoice.ir` دیپلوی نشده‌اند** — dev کد قدیمی را اجرا می‌کند (`/health/version`
روی dev هنوز `404` می‌دهد، یعنی version-guard هم هنوز live نیست). پس alembic head روی
dev هنوز `m6n7o8p9q0r1` نیست و این سشن نتوانست آن را از بیرون تأیید کند؛ دیپلوی گام
بعدیِ founder است.

- **PA — Revenue Dashboard Pack** و **PB — Partner Workspace v2** (پرتفوی همکار،
  حلقهٔ درخواست فعال‌سازی ماژول + کمیسیون، usage metering، earnings) — DONE.
- **گاردهای زیرساخت:** (۱) **v1-kill** — docker-compose v1 بازنشسته + shadow با STOP
  wrapper؛ قانون «فقط `docker compose` v2». (۲) **version-guard** — `GET /health/version`
  (git SHA + alembic head) در بک‌اند + بیک SHA در `/version.json` فرانت، برای
  verify-smoke دیپلوی (served SHA == deployed SHA و image alembic head == DB head).
- **P7b** — نشست منقضیِ ادمین/همکار دیگر اسپینر بی‌پایان «در حال بررسی» نشان نمی‌دهد؛
  کارت «نشست منقضی شده» + دکمهٔ «ورود دوباره» (frontend `525d7b5`).
- **تورهای per-صفحه** — ۷ تور کوتاهِ متنی (فاکتور، تسویه، چک، گزارش، نمای حسابدار،
  کنسول همکار، یادآورها) + دکمهٔ «؟ راهنمای این صفحه»، یک auto-fire در هر سشن
  (frontend `b229f20`/`0da4d6c`/`eda923b`).
- **P8 — ممیزی مقیاس‌پذیری DB (measure-first)** — گزارش کامل `db-audit.md` (ریشهٔ
  workspace). ۸ ایندکسِ evidence-based (migration `m6n7o8p9q0r1`، همه CONCURRENTLY)؛
  ۳ کاندید با measurement رد شد (over-indexing)؛ یافتهٔ کلیدی: `random_page_cost`
  باید روی SSD `1.1` باشد وگرنه planner ایندکس‌ها را adopt نمی‌کند. Before/after روی
  tenantِ ۱۵۰هزار فاکتور: sales-register **16.6ms→0.34ms**، purchases-register
  **13.6ms→0.15ms**، cash-flow **20ms→4ms**. تست `775 pass / 7 baseline fail`
  (صفر جدید)؛ invariantِ تراز سبز؛ migration بالا/پایین/بالا تمیز، ۰ ایندکس invalid.
  seeder prod-shape به‌عنوان dev tool commit شد (`scripts/seed_prod_shape*.sql`).

**گام بعدیِ founder — دیپلوی guarded روی dev (اولین اجرا زیر گارد جدید):** Step 0
export‌ِ `BACKEND_SHA`/`FRONTEND_SHA` → `build --no-cache` → `up -d --no-deps` →
`alembic upgrade head` (۸ ایندکس CONCURRENTLY) → verify-smoke (served SHA == deployed
SHA و image head == DB head) + چک `SELECT count(*) FROM pg_index WHERE NOT indisvalid`
باید `0` باشد + **اعمال `random_page_cost=1.1`** (بدون آن ایندکس‌ها adopt نمی‌شوند) →
یک گزارش سنگین روی dev دوباره اجرا و timing ثبت شود. **`docker compose` v2 فقط.**
captcha/rate-limit روی dev طبق config سرور ON است (این سشن دیپلوی نکرد، پس دوباره
verify نشد).

---

## آخرین وضعیت — Batch B «لایهٔ طلایی» (۲۰ تیر ۱۴۰۵ / 2026-07-10) — LOCAL, NOT PUSHED

لایهٔ اختیاریِ «نمای حسابدار» ساخته شد: موتور دوطرفهٔ سند (درخت حساب‌ها + دفتر روزنامه)
که سند را از همان رویدادهای کاملِ فاز ۱ به‌صورت **replay قطعی و idempotent** می‌سازد —
بدونِ ذره‌ای کوپلینگ با مسیرهای نوشتنِ کاسب. کلیدِ per-business (`accountant_view_enabled`،
پیش‌فرض **خاموش**)؛ **با کلیدِ خاموش هر صفحهٔ کاسب دقیقاً مثل قبل است** (pixel parity
ساختاری است، نه با اسکرین‌شات — D10).

- گزارشِ کامل: **`batchB-review.md`** (ریشهٔ workspace) · تصمیم‌ها D1–D12 در
  `DECISIONS-batchB.md` · کاتالوگ Group 9 (S9-01..06) در `phase1_user_scenarios_v1.md`.
- کامیت‌ها: backend ۶، frontend ۴، ops ۱ (+docs) — **هیچ‌کدام push نشده**. Alembic head
  `a4b5c6d7e8f9`.
- تست‌ها: backend `747 pass / 7 fail (baseline، صفر جدید)`؛ invariantها روی Postgres واقعی
  سبز؛ backfill CLI `۷ tenant، ۶۱ سند، ۰ gap`.
- **Mission 3 (deploy) بلاک است — درست:** گیتِ pixel-parity به اسکرین‌شاتِ founder نیاز دارد
  (قانونِ «Claude مرورگر را نمی‌راند»). وقتی GO: rebuild api `--no-cache` → up -d →
  `alembic upgrade head` → `python -m app.cli.backfill_journals` → smokeِ toggle-ON → خاموش.
- Captcha: دست‌نخورده — لوکال ON، dev ON.

---

## ۱. جهت‌گیریِ کلی محصول

**محصول:** Digi Invoice (دیجی اینویس) — ابری، RTL فارسی، mobile-first، حسابداری/فاکتور برای کاسبانِ ایرانی. rebrand از DigiTax. **همان ریپوها ادامه پیدا می‌کنند، نه پروژه‌ی نو.**

**اصلِ شماره ۱ (غیرقابل تغییر):** کاسبِ بدونِ حسابدار. کاسب فقط ببیند: «فروختم، پول گرفتم، طلبِ من چقدر است، سود ماه چیست؟» تمامِ پیچیدگیِ حسابداری (سند، بدهکار/بستانکار، تراز، معین/تفصیلی) پشتِ صحنه، برای «لایه‌ی حسابدار» فاز ۲. اگر صفحه‌ای در `/app/*` نیاز به دانش حسابداری داشته باشد، غلط است.

**رقبا برای غلبه:** هلو، سپیدار (دسکتاپ، اصطلاح‌محور، سخت) + حسابفا، چرتکه (ابری، ولی اصطلاح‌محور یا محدود). **تمایزِ ما:** ابری + موبایل‌محور + بدون اصطلاح + راهنمای سناریومحور + مودیانِ native.

**اصولِ حاکم:** RTL، mobile-first، یک قدمِ روشنِ بعدی، progressive disclosure، هرگز عددِ قلابی/دکمه‌ی fake save، خطای فارسیِ دوستانه (هرگز 500 خام)، همه‌ی محاسبات با ذخیره‌ی ریال (تومان فقط نمایش)، Vazirmatn سلف‌هاست.

---

## ۲. ریپوها (workspace: /home/hitman47/Public/projects/digitax-workspace)

- **digi-tax-backend** — FastAPI, PostgreSQL, Alembic, Redis. Docker-first برای تست.
- **digi-tax-frontend** — React + TanStack Router + TypeScript + Tailwind v4 (RTL)، pnpm. Dev روی localhost:8080. Base URL شامل `/api/v1` است — پس API کالِ فرانت بدون `/api/v1` (مثلاً `/customers`).
- **digi-tax-ops** — docker-compose، docs canonical، scripts.
- (فقط رفرنس تاریخی: `digi-tax-Front-source` — نه dev source.)

**سرور تست:** `https://dev.digiinvoice.ir` روی `65.109.213.75` (SSH `root@65.109.213.75 -p 6543`). nginx + Let's Encrypt از قبل ست شده. `.env` روی سرور با DEBUG=false، captcha ON، rate-limit ON.

---

## ۳. اسناد canonical (منبع حقیقت — همیشه اول این‌ها را بخوان، به ترتیب)

1. `digi-tax-ops/docs/project_onboarding_brief.md` — brief بروزشده. **متن کهنه‌ی «Do not start invoices…» STALE است، نادیده بگیر.**
2. `digi-tax-ops/docs/phase1_accounting_plan_v1.md` — پلن حسابداری Phase 1 (Steps 0-6).
3. `digi-tax-ops/docs/phase1_user_scenarios_v1.md` — ۶۰ سناریوی کاسب + terminology قفل شده + جدول تصمیمات.
4. `digi-tax-ops/docs/admin_scenarios_v1.md` (جدید در Part 3) — ۷ سناریوی پنل ادمین.
5. `digi-tax-backend/docs/progress.md` + `digi-tax-frontend/docs/progress.md` — وضعیتِ زنده.
6. AGENTS.md + CLAUDE.md در هر ریپو — قوانینِ ریپو.

---

## ۴. وضعیتِ فعلی (2026-07)

**تمام شده و به origin/main push شده — Phase 1 حسابداری (Steps 0-6):**
- **Step 0:** ادغام داپلیکیت‌ها (`/app/transactions` رفت زیر `/app/payments`)، حذف mock tree.
- **Step 1:** حساب‌های خزانه (بانک/صندوق، شبا ISO-13616، مانده اولیه، انتقال، POS mapping، صندوق پیش‌فرض خودکار).
- **Step 2:** لینک فاکتور↔پرداخت (invoice_id/purchase_id/account_id روی payments، paid_amount/payment_status/remaining derived، FIFO allocator، block-cancel 409).
- **Step 3:** پنجره‌ی تسویه‌ی progressive (`POST /payments/settle`، split نقد/کارت/انتقال + مانده نسیه، یک dialog برای همه‌جا، ردیف چک reserved-disabled).
- **Step 4:** چرخه‌ی کامل چک (دریافتی: در جریان→واگذار→وصول/برگشتی؛ پرداختی: در جریان→پاس/برگشت؛ پول فقط در وصول/پاس حرکت می‌کند؛ نوار سررسید ۷ روز).
- **Step 5:** برگشت از فروش/خرید (financial-only، refund toggle default OFF، «برگشت‌خورده» متمایز از «باطل‌شده»، برگشتِ جزئی).
- **Step 6:** داشبورد واقعی (اعدادِ واقعی، صفرِ قلابی) + ۴ گزارش کاسب (P/L، دفتر فروش/خرید، مانده طرف حساب‌ها، جریان نقدی) + shared list foundation (سرچ+صفحه‌بندی همه‌ی لیست‌ها) + read-only invoice view.

**تمام شده — Phase 2 پایه (D1-D6 تا Part 3):**
- **D1:** فیکس باگ ماه‌ها که آزار می‌داد — پسورد `Admin@12345` روی هر دو `09120000000` و `09120000001` کار می‌کند. `upsert_user()` هرگز `hash_password` صدا نمی‌زد — الان می‌زند. `must_change_password=True` برای اولین لاگین.
- **D2:** مدیریت کاربران توسط ادمین ستادی (`/admin/users` list + detail + reset-password + enable/disable). Password reset تولید temp، `must_change_password=True` می‌شود، هرگز ذخیره نمی‌شود.
- **D3:** بازسازی shell ادمین + داشبورد staff + صفحه‌ی businesses. اعدادِ واقعی از psql. تایل‌های سلامت زنده.
- **D4:** تنظیمات واقعی — تفکیک «حساب من» (per-user، تم، تغییر پسورد، اعلان‌ها) از «تنظیمات کسب‌وکار» (per-business، نام، هویت، پیشوند فاکتور، سالِ مالی، ارز نمایش، اتصال مودیان). صفرِ fake save.
- **D5:** محدوده‌ی داده مالتی‌تننت. `staff`/`viewer` فقط رکوردهای خودشان (فاکتور، پرداخت، چک، برگشت، خرید). Catalog data (مشتری، کالا، تأمین‌کننده) shared در tenant. Reports/dashboard = owner/admin only. `created_by_user_id` روی جداول رکوردی. سایدبار آیتم‌های owner/admin-only برای staff/viewer مخفی می‌شود.
- **D6:** سالِ مالی + تاریخچه. جدول `fiscal_year_changes` فقط تغییرات را ثبت می‌کند. تابع `get_fiscal_year_range(business, date)` برای هر تاریخ (چه گذشته چه آینده) مرزهای درست را برمی‌گرداند. تغییر شروع سال روی گزارش‌های سال‌های قبل تأثیر نمی‌گذارد (خواسته صریح founder).
- **Part 3 (بازسازی ادمین + راهنما):** سایدبار ادمین با الگوی مرچنت (RTL درست، grouping)، موبایل‌های کامل برای ادمین، تگ‌های صادقانه، `/admin/guide` با ۷ سناریو دو-سطحی، کاتالوگ `admin_scenarios_v1.md`.

**مانده — Phase 2 نهایی:**
- **Part 4** (بعدی): افزودن walkthroughهای تنظیمات به راهنمای مرچنت `/app/guide` — تغییر رمز، تم، ارز، سالِ مالی، پیشوند فاکتور، اطلاعات کسب‌وکار، اتصال مودیان.
- **Deploy Phase-2 → سرور تست** (بعد از Part 4، در یک تسک ops).

**در صف — بعد از Phase 2:**
- **پنل پارتنرشیپ** (partnership/accountant panel) — حسابداران معرف و مدیریتِ آن‌ها. ماژول بزرگ جدا.
- **مدیریت تننت پیشرفته** — تعلیق/فعال‌سازی کسب‌وکار، متریک‌های مالی هر tenant.
- **Stage D — مودیانِ کامل** (R1B: crypto/signing، sandbox، bulk، tracking). Opus. **مستنداتِ رسمی PDF + API از سازمان مالیاتی را founder دارد، هنگامِ شروع Stage D بگیر.**
- **گزارش‌های Gold-tier** (نمودار، تفکیک ماه/سال مالی، سود سالانه). سال مالی جاری vs قبل.
- **ری‌برند کامل** DigiTax → Digi Invoice + لوگو (founder سه لوگو دارد: تایپو، شرکتی، محصول).
- **لایه‌ی حسابدار** (سند خودکار پشت صحنه + تراز/دفتر export).
- **انبار + بهای تمام‌شده.**
- **اکسل bulk import.**
- **حقوق و دستمزد.**
- **Subscription/paywall.**
- **سخت‌سازی pre-prod** (env:prod checklist).

---

## ۵. قوانینِ مهندسی ثابت (این‌ها را هر پرامپت رعایت کن)

### مدل و اقتصادِ توکن
- **Fable 5** برای همه‌ی کارِ روتین (CRUD، UI polish، backend/frontend استاندارد).
- **Opus 4.8** فقط برای مسائلِ سنگین: UI/UX heavy redesign، معماریِ cross-repo، security-sensitive (مودیان R1B).
- **Sonnet 5** برای کارِ ops (deploy، config، diagnosis).
- سشن روی مدل غلط شروع شد → `/model` عوض کن قبل از build.

### Docker-first backend
- بعد از هر تغییرِ backend: `docker-compose build --no-cache api` قبل از تست (چون Dockerfile قبل COPY می‌کند، بدون --no-cache لایه‌ی stale می‌ماند — این نصفی از هدر رفتنِ سشن‌های قبلی بود).
- بعد: `docker-compose up -d`، `alembic upgrade head`.
- تست‌ها: `pytest`، `ruff`، `black` در container.

### Frontend
- pnpm فقط.
- `pnpm run typecheck` + `pnpm run build` قبلِ هر commit.
- Base URL شاملِ `/api/v1` — پس کالِ نسبی (`/customers`)، هرگز `/api/v1/customers`.

### UI/UX (اجباری در هر پرامپتِ UI)
- Skillهای vendored: `digi-tax-frontend:ui-ux-pro-max` + `:design-system` + `:ui-styling` — واقعاً query کن نه فقط load.
- توکن‌های Calm Bazaar. Acceptance = صفحه‌ی مشتریان (تأیید شده).
- RTL checklist: کنترل چک‌باکس/رادیو راستِ label، صفر نشتِ LTR در 390px، Vazirmatn سلف‌هاست (هرگز Google/CDN).
- **Label↔input binding** با name/value واقعی چک شود، نه از روی جای بصری (سواپِ نام/نام‌خانوادگی موقع تایپ دیده می‌شود).
- شمسی فقط (JalaliDateField). هرگز caption میلادی زیر فیلد شمسی نچین.
- Money inputs: Decimal string، جداکنندهٔ سه‌رقمی روی blur، برچسبِ واحد کنارِ عدد، upper-bound.
- خطای فارسی inline دوستانه، هرگز 500 خام یا JSON.

### validators متمرکز
- موبایل: 09 + prefix عملیاتی واقعی
- کد ملی فرد: ۱۰ رقم + mod-11 checksum
- شناسه ملی حقوقی: ۱۱ رقم (length-only، بدون checksum)
- کد اقتصادی: ۱۲ رقم
- شبا: ISO-13616 mod-97
- Display می‌تواند فارسی نشان دهد، ذخیره ASCII only.

### Testing rhythm
- Playwright فقط viewing (هرگز input فرمی React را automatically پر نکن).
- Headless ترجیح داده می‌شود.
- Live proof با dev-OTP curl.

### Screenshots
- قبل از هر commit یا push، QA screenshots جمع‌شده را delete/gitignore کن.
- در پایانِ هر turn که screenshot گرفت، مسیرهای مطلقِ کامل را چاپ کن و از founder بخواه پیست کند.

### قانونِ ۹۷٪ context
- در ~۹۷٪ pause کن در commit امن، resume note در progress.md بنویس، از founder yes/no بپرس. هرگز کار در هوا معلق نگذار.

### Captcha state
- در پایانِ هر پیام گزارش کن ON/OFF. اگر برای dev-OTP curl خاموش کردی، حتماً برگردان و re-verify کن قبل از تمام کردن.

### Commits
- Small separate commits. هرگز bulk-apply.
- **No push تا founder GO.**

### مغایرت گزارش کن
- اگر code/docs/scenarios متفاوت‌اند، mismatch را گزارش کن قبل از انتخاب — هرگز صامت یکی را انتخاب نکن.

### راهنما و اپ — no drift rule
- هر تغییرِ در label/screen/tab/dialog مرچنت، در همان commit راهنمای مربوطه را بروز کن.

---

## ۶. آدرس‌ها و حساب‌های تست

- **Local dev:** `http://localhost:8080` (frontend)، `http://localhost:8000` (api)
- **Test server:** `https://dev.digiinvoice.ir`
- **حساب‌های seed:**
  - `09120000000` — کاربر کاملِ seed (owner ۴ کسب‌وکار)، OTP، حالا پسورد `Admin@12345` هم دارد (D1).
  - `09120000099` — کاربر stage-1، OTP.
  - `09120000001` — سیستم ادمین، پسورد `Admin@12345`، `must_change_password=true`.
- OTP در حالت dev در جواب API برمی‌گردد (DEBUG=true only).
- Reseed تازه: `python -m app.cli.seed_dev_data` داخل api container.

---

## ۷. اشاره‌های خیلی مهم که Founder گفت (و باید همیشه رعایت شود)

- **رابطه‌ی هرمی:** L1 staff admin (Digi Invoice) → L2 user (unique per mobile، در چند tenant عضو) → L3 business (tenant، isolated). این معماری Slack/Notion — استاندارد صنعت.
- **اشتراکی vs اختصاصی per tenant:**
  - اشتراکی (کاربر): پروفایل، تم، اعلان.
  - اختصاصی (کسب‌وکار): مودیان، شماره فاکتور، ارز نمایش، سال مالی، کاربران، حساب‌های خزانه.
- **پارتنرشیپ نمی‌شود** با ادمینِ ستادی قاطی شود. ادمینِ ستادی = کارکنانِ Digi Invoice. پارتنرشیپ = حسابداران معرف. دو ماژول کاملاً جدا.
- **تاریخچه‌ی سالِ مالی باید حفظ شود** — تغییرِ سال جاری نباید گزارش‌های قدیم را دستکاری کند. حل شده در D6.
- **Font Vazirmatn سلف‌هاست**، هرگز Google Fonts (CDN بی‌ثبات، رنگ فارسی خراب می‌شود).
- **حبابِ `D.D`/`D.A` initial avatar را برنگردان** — از قدیم حذف شد.

---

## ۸. نقشه‌ی بلافصلِ راه (بعد از این handoff)

1. **الان (چت جدید):** چکِ چشمی Part 3 → GO Part 4 (walkthroughs راهنما برای تنظیمات مرچنت).
2. **بعدِ Part 4:** deploy همه‌ی Phase-2 (D5+D6+Part 3+Part 4) به `dev.digiinvoice.ir`.
3. **بعدِ deploy:** پنل پارتنرشیپ + مدیریت تننت پیشرفته (ماژول جدا).
4. **Stage D:** مودیانِ کامل با مستنداتِ رسمیِ founder (Opus).
5. **گزارش‌های Gold-tier + ری‌برند + سخت‌سازی pre-prod.**

---

## ۹. پرامپت فوری برای چت جدید

بعد از این‌که Part 3 چشمی تأیید شد، این را در چت جدید بده:

```
GO Part 4: افزودن walkthroughهای تنظیمات به راهنمای مرچنت `/app/guide`. Fable 5.

اول این‌ها را بخوان: `digi-tax-ops/docs/project_onboarding_brief.md`،
`phase1_accounting_plan_v1.md`، `phase1_user_scenarios_v1.md`،
`admin_scenarios_v1.md`، و resume note بالای `digi-tax-backend/docs/progress.md`.
Phase 1 (Steps 0-6) و Phase 2 D1-D6 + Part 3 (ادمین + راهنما) DONE هستند.
هرگز بازسازی نکن.

هدف: صفحه‌ی تنظیمات D4 هیچ walkthrough راهنما ندارد. این سناریوها را در
`/app/guide` به گروه «کاربران و تنظیمات» اضافه کن (دو سطح مبتدی/پیشرفته،
همان ساختار موجود، terminology قفل شده):

- «تغییر رمز عبور»
- «تغییر پوسته برنامه (روشن/تاریک)»
- «تغییر واحد نمایش مبالغ ریال ↔ تومان»
- «تنظیم شروع سال مالی کسب‌وکار» (اشاره کن تغییر روی گزارش‌های قبل تأثیر ندارد)
- «تنظیم پیشوند شماره فاکتور و سیاست بازنشانی»
- «ویرایش اطلاعات کسب‌وکار (نام، نوع شخص، کد ملی/شناسه/اقتصادی، نشانی)»
- «اتصال به سامانه مودیان — این کار برای هر کسب‌وکار جداگانه انجام می‌شود»

هرکدام نامِ دقیقِ سایدبار + برچسبِ دکمه‌های فعلیِ اپ را بگو. در حین
نوشتن با dev-OTP session تازه verify کن. اگر label mismatch بود،
راهنما را فیکس کن (هرگز اپ را) — قانونِ no-drift.

Standing: Docker-first، pnpm typecheck+build، ui-ux-pro-max query،
Calm Bazaar tokens، RTL check، screenshots absolute paths در انتها،
delete accumulated QA screenshots قبل از commit، 97% rule، captcha
ON/OFF در انتها، small separate commits، NO push. STOP در پایان Part 4
برای بازبینیِ founder.
```

---

## ۱۰. یک نکته‌ی روانی

این پروژه در یک ماه از یک اسکلت به یک محصولِ حسابداریِ کامل تبدیل شد که رقیبِ هلو/سپیدار است (روی سرور، با HTTPS، فارسی، بی‌جارگون، sceneario-driven). Founder فشار زیاد داشته و انتظار حرفه‌ای دارد. کم‌گوی و صادق باش. اگر چیزی جواب نمی‌دهد، همان اول گزارش کن. `progress.md` را همیشه بروز نگه‌دار. کاسبِ بدونِ حسابدار — این تمامِ فلسفه‌ی محصول است.
