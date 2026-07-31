# استقرار لندینگ ایستا روی سرور apex (digiinvoice.ir) — سه قدم

_Bundle: `digi-tax-ops/dist/landing_apex_2026-07-31.zip` (~450KB، کاملاً
خودکفا: HTML + CSS + فونت وزیرمتن؛ بدون JS، بدون بک‌اند، بدون CDN). ساخته‌شده
با `digi-tax-frontend/scripts/build-apex-landing.mjs` از همان متن‌هایی که صفحات
اصلی رندر می‌کنند (`src/lib/landing-pages.json`)._

## قدم ۱ — آپلود

```bash
# روی سرور apex (وب‌روت را با مسیر واقعی عوض کنید):
unzip landing_apex_2026-07-31.zip -d /var/www/digiinvoice
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
```

بعد از سبز شدن هر شش خط، در پنل اینماد «تایید بارگذاری» را بزنید.

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
