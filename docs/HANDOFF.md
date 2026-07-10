# Digi Invoice — Session Handoff (2026-07)

این سند کاملِ سفر از ابتدای این چت (تصحیح ادمین + معماری مالتی‌تننت) تا اکنون (Part 3 ادمین) را ثبت می‌کند. هدف: هر Claude جدیدی (چه claude.ai چه Claude Code) بتواند بدون از دست دادن context ادامه دهد.

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
