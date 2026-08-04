# استقرار لندینگ ایستا روی سرور apex (digiinvoice.ir) — سه قدم

> ## ⚠️ این باندل یک «لندینگ دوم» نیست — و هرگز نباید بشود
>
> **قانون دائمی (۱۴۰۵-۰۵-۱۳ / 2026-08-04).** این باندل ایستا فقط یک **خروجی
> موقت از همان لندینگ اصلی** است: `scripts/build-apex-landing.mjs` آن را از
> همان `src/lib/landing-pages.json` می‌سازد که خودِ اپ React رندر می‌کند. یک
> منبع متن، دو خروجی — نه دو پروژه.
>
> - **هیچ‌وقت لندینگ دوم ساخته نمی‌شود.** هر تغییر متن/طراحی در
>   `landing-pages.json` (یا کامپوننت‌های لندینگ) انجام می‌شود و باندل دوباره
>   ساخته می‌شود؛ ویرایش دستی HTML داخل باندل = دو نسخه‌ای شدن محتوا و همان
>   دام «drift» است.
> - **موقتی است.** به‌محض این‌که `digiinvoice.ir` به استک خودمان اشاره کند
>   (nginx → کانتینر frontend)، این باندل و این سند **بازنشسته** می‌شوند و
>   لندینگ React تنها سطح زنده می‌ماند.
> - تا آن روز، هر بازسازی باندل باید بلافاصله بعد از تغییر لندینگ انجام شود تا
>   apex و اپ یک متن را نشان دهند.

_Bundle: `digi-tax-ops/dist/landing_apex_2026-08-03.zip` (~450KB، کاملاً
خودکفا: HTML + CSS + فونت وزیرمتن؛ بدون JS، بدون بک‌اند، بدون CDN). ساخته‌شده
با `digi-tax-frontend/scripts/build-apex-landing.mjs` از همان متن‌هایی که صفحات
اصلی رندر می‌کنند (`src/lib/landing-pages.json`)._

> **۱۴۰۵-۰۵-۱۲ (2026-08-03):** «نماد اعتماد الکترونیکی» دیگر placeholder نیست —
> مارک‌آپ رسمی اینماد (id=7118850) در فوتر هر پنج صفحهٔ این باندل و در فوتر
> لندینگ React نشسته است. تصویر نماد **عمداً** روی `trustseal.enamad.ir` میزبانی
> می‌ماند (تنها درخواست بیرونیِ این باندل)؛ اگر آن را روی سرور خودمان کپی کنیم،
> بررسی اینماد رد می‌شود. جعبهٔ ۹۶×۱۰۰ پیکسلی برایش رزرو شده تا نماد کُند یا
> در دسترس‌نبودن، فوتر را جابه‌جا نکند (CLS اندازه‌گیری‌شده: صفر سهم از نماد).

## قدم ۱ — آپلود

```bash
# روی سرور apex (وب‌روت را با مسیر واقعی عوض کنید):
unzip landing_apex_2026-08-03.zip -d /var/www/digiinvoice
```

## قدم ۲ — nginx

```nginx
server {
    server_name digiinvoice.ir www.digiinvoice.ir;
    root /var/www/digiinvoice;
    index index.html;

    # صفحات ایستا + فایل تأیید اینماد
    location / { try_files $uri $uri/ =404; }
    types { text/plain txt; }           # ← 15027996.txt باید text/plain برگردد

    # TLS: گواهی فعلی فقط برای central.digiinvoice.ir است — برای apex صادر کنید:
    #   certbot --nginx -d digiinvoice.ir -d www.digiinvoice.ir --redirect
}
```

⚠️ بدون گواهی معتبر برای خود `digiinvoice.ir`، چک اینماد و مرورگرها خطای TLS
می‌گیرند — قدم certbot اجباری است.

## قدم ۳ — راستی‌آزمایی

```bash
curl -i https://digiinvoice.ir/15027996.txt      # → 200 · text/plain · بدنهٔ خالی
curl -o /dev/null -sw '%{http_code}\n' https://digiinvoice.ir/           # 200
curl -o /dev/null -sw '%{http_code}\n' https://digiinvoice.ir/terms/     # 200
curl -o /dev/null -sw '%{http_code}\n' https://digiinvoice.ir/privacy/   # 200
curl -o /dev/null -sw '%{http_code}\n' https://digiinvoice.ir/contact/   # 200
curl -o /dev/null -sw '%{http_code}\n' https://digiinvoice.ir/guide/     # 200
# نماد در فوتر هر پنج صفحه (باید ۵ بشود):
grep -rl "trustseal.enamad.ir" /var/www/digiinvoice | wc -l
```

بعد از سبز شدن هر شش خط، در پنل اینماد «تایید بارگذاری» را بزنید.

> **نکتهٔ نماد:** `logo.aspx` از هر مبدأ دلخواهی سرو نمی‌شود — از این ماشین
> (خارج از دامنهٔ ثبت‌شده) با ۴۰۳ پاسخ می‌دهد. یعنی تصویر نماد فقط وقتی واقعاً
> رندر می‌شود که از خودِ `https://digiinvoice.ir` با TLS معتبر باز شود. تا آن
> لحظه جعبهٔ رزروشده خالی می‌ماند (بدون آیکون شکسته، چون `alt=''`) و چیزی
> نمی‌شکند — ولی «نماد دیده نمی‌شود» قبل از قدم certbot یک باگ نیست.

## تلفن/ایمیل/آدرس (الان placeholder است)

مقدارها را در `digi-tax-frontend/src/lib/landing-pages.json` کلیدهای
`contact.phone` / `contact.email` / `contact.postalAddress` (خط‌های ۳–۵) وارد
کنید، سپس:

```bash
cd digi-tax-frontend && node scripts/build-apex-landing.mjs
# دوباره zip و آپلود؛ صفحات dev هم با دیپلوی بعدی خودشان به‌روز می‌شوند.
```

(راه سریع بدون rebuild: همان مقدارها را مستقیم در `contact/index.html` داخل
وب‌روت ویرایش کنید — ولی منبع اصلی JSON بماند تا dev و apex یکی باشند.)

نکته: CTAها و «ورود» عمداً به `https://dev.digiinvoice.ir` می‌روند تا داور
اینماد به اپ واقعیِ در حال کار برسد؛ وقتی production بالا آمد، `APP` را در
`build-apex-landing.mjs` عوض کنید و دوباره بسازید.
