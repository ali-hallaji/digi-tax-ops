# لیست بیمهٔ تأمین اجتماعی — ساختار DSKKAR00.DBF / DSKWOR00.DBF

_Compiled 2026-07-31 for the payroll insurance-export (backend
`app/modules/payroll/application/insurance_export.py`). This doc is the single
place that says which part of the layout is SOURCED and which is «تأییدنشده»._

## Source situation — read this first

The official field catalog is published by سازمان تأمین اجتماعی in the
«دفترچهٔ راهنمای تهیهٔ لیست حق بیمه» distributed with the لیست دیسک software
(and updated for the NEW structure in آذر ۱۴۰۳). **That PDF was not reachable
from the dev machine's network** (US-routed search cannot open the Iranian
mirrors). What IS sourced:

| Fact | Source |
|---|---|
| Two files: `DSKKAR00.DBF` = ONE aggregate workshop record («فقط یک سطر سرجمع»), `DSKWOR00.DBF` = one row per worker («برای تک تک پرسنل یک سطر جدا») | [nosa.com support forum](https://accsupport.nosa.com/tabid/63/aft/2591/Default.aspx) |
| DBF (dBASE III) format, DOS bytes, **کدپیج ایران‌سیستم** for Persian text, ANSI not Unicode | [tavafi.ir/post/dsk](https://tavafi.ir/post/dsk/) · research doc §۱-۳ |
| New structure since آذر ۱۴۰۳ adds حق تأهل + پایهٔ سنوات fields | [tavafi.ir/post/dsk](https://tavafi.ir/post/dsk/) (DSKEditor changelog) · [timanet.com](https://timanet.com/tamin-list-disk/) |
| Field names `DSK_TKOSO` (سهم کارفرما), `DSK_TMASH` (جمع مشمول), `DSK_BIC` (بیکاری = ۳٪ × DSK_TMASH) exist with these roles | [tavafi.ir/post/dsk](https://tavafi.ir/post/dsk/) changelog v2.3.1.4 |
| Upload target: samt.tamin.ir → کارفرمایان → ارسال لیست حق بیمه | research doc §۱-۳ |

**Everything else below — every field name, length, and semantic mapping not in
the table above — is reproduced from widely-replicated Iranian payroll
integrations and is «تأییدنشده».** The 1403+ additions (حق تأهل/پایهٔ سنوات
field names) are NOT yet in our export at all.

## ⛔ Gate before the first real upload (empirical law)

1. Founder/accountant downloads one month's zip from the payroll page.
2. Opens both files in the official **لیست دیسک** software (or DBF viewer).
3. Checks: files load without error · worker names legible (Iran System
   encoding correct) · figures match the payroll report rial-for-rial.
4. Only then upload to samt.tamin.ir — and file any mismatch as a bug with the
   viewer screenshot; each fixed field flips to تأییدشده here.

## DSKKAR00.DBF — one record per month

| Field | Type | Meaning (assumed) | Our mapping | Status |
|---|---|---|---|---|
| DSK_ID | C10 | کد کارگاه | tenants.insurance_workshop_code | نام/طول تأییدنشده — نقش مسلم |
| DSK_NAME | C100 | نام کارگاه | tenant.name | تأییدنشده |
| DSK_FARM | C100 | نام کارفرما | tenant.name | تأییدنشده |
| DSK_ADRS | C100 | آدرس کارگاه | tenant.address | تأییدنشده |
| DSK_KIND | N1 | نوع لیست (اصلی=۰) | 0 | تأییدنشده |
| DSK_YY | N2 | سال (دو رقم) | run.jalali_year % 100 | تأییدنشده |
| DSK_MM | N2 | ماه | run.jalali_month | تأییدنشده |
| DSK_LISTNO | C12 | شمارهٔ لیست | خالی | تأییدنشده |
| DSK_DISC | C100 | شرح | خالی | تأییدنشده |
| DSK_NUM | N5 | تعداد بیمه‌شدگان | count(items) | تأییدنشده |
| DSK_TDD | N6 | جمع روزهای کارکرد | Σ DSW_DD | تأییدنشده |
| DSK_TROOZ | N12 | جمع دستمزد روزانه | Σ DSW_ROOZ | تأییدنشده |
| DSK_TMAH | N12 | جمع دستمزد ماهانه | Σ DSW_MAH | تأییدنشده |
| DSK_TMAZ | N12 | جمع مزایای مشمول | Σ DSW_MAZ | تأییدنشده |
| DSK_TMASH | N12 | جمع کل مشمول بیمه | Σ insurance_base (capped) | **نام+نقش تأییدشده** (tavafi) — mapping ours |
| DSK_TTOTL | N12 | جمع کل | = DSK_TMASH | تأییدنشده |
| DSK_TBIME | N12 | جمع سهم کارگر (۷٪) | Σ insurance_employee | تأییدنشده |
| DSK_TKOSO | N12 | جمع سهم کارفرما (۲۰٪) | Σ insurance_employer | **نام+نقش تأییدشده** (tavafi) — mapping ours |
| DSK_BIC | N12 | بیمهٔ بیکاری (۳٪) | Σ insurance_unemployment | **نام+نقش+فرمول تأییدشده** (tavafi: ۳٪ × TMASH) |
| DSK_RATE | N5 | نرخ (۲۰) | 20 | تأییدنشده |
| DSK_PRATE | N2 | نرخ مشاغل سخت | 0 | تأییدنشده |
| MON_PYM | C3 | ماه/نوع پیمان | خالی | تأییدنشده |

## DSKWOR00.DBF — one record per worker

| Field | Type | Meaning (assumed) | Our mapping | Status |
|---|---|---|---|---|
| DSW_ID | C10 | شمارهٔ بیمه | employee.insurance_number (snapshot→live fallback) | تأییدنشده |
| DSW_YY/MM | N2 | سال/ماه | run | تأییدنشده |
| DSW_LISTNO | C12 | شمارهٔ لیست | خالی | تأییدنشده |
| DSW_ID1 | C10 | (احتمالاً کد ملی/شناسه) | national_id snapshot | تأییدنشده — دو فیلد کدملی‌نما (DSW_ID1 و PER_NATCOD) |
| DSW_FNAME | C100 | نام | token اول full_name | تأییدنشده + **گپ داده**: نام/نام‌خانوادگی جدا ذخیره نمی‌شود |
| DSW_LNAME | C100 | نام خانوادگی | بقیهٔ full_name | تأییدنشده |
| DSW_DNAME | C100 | نام پدر | خالی — نگه نمی‌داریم | تأییدنشده + گپ داده |
| DSW_IDNO / IDPLC / IDATE / BDATE / SEX / NAT / OCP / JOB / SDATE / EDATE | — | شناسنامه/تولد/جنسیت/ملیت/شغل/شروع/ترک | خالی — نگه نمی‌داریم | تأییدنشده + گپ داده |
| DSW_DD | N2 | روزهای کارکرد | روزهای ماه (کارکرد per-item هنوز نداریم) | تأییدنشده + **گپ مدل**: فرض تمام‌وقت |
| DSW_ROOZ | N12 | دستمزد روزانه | base_salary/30 (ROUND_DOWN) | تأییدنشده |
| DSW_MAH | N12 | دستمزد ماهانه | base_salary | تأییدنشده |
| DSW_MAZ | N12 | مزایای مشمول | insurance_base − base_salary | تأییدنشده |
| DSW_MASH | N12 | جمع مشمول | insurance_base (سقف‌خورده) | تأییدنشده |
| DSW_TOTL | N12 | جمع کل | = DSW_MASH | تأییدنشده |
| DSW_BIME | N12 | حق بیمهٔ سهم کارگر | insurance_employee | تأییدنشده |
| DSW_PRATE | N2 | نرخ مشاغل سخت | 0 | تأییدنشده |
| PER_NATCOD | C10 | کد ملی | national_id snapshot | تأییدنشده |

## Iran System encoding — status

`dbf.py:iransystem_encode` implements digits + contextual letter forms +
visual (RTL-reversed) storage from public references, NOT from an org spec.
**Status: تأییدنشده until one real month renders legible names in the official
viewer.** Numeric/date/ID fields are pure ASCII and carry the legal substance;
a mis-mapped letter is visible (falls back to `?`), never silent.

## Known model gaps surfaced by this export (future work, reported not hidden)

- نام/نام‌خانوادگی/نام پدر/شناسنامه/تولد/جنسیت/ملیت/شغل as separate employee
  fields (today: one full_name + job_title).
- روزهای کارکرد per payroll item (today: full-month assumed).
- شمارهٔ لیست / نوع لیست selection UI.
- فیلدهای ساختار جدید ۱۴۰۳ برای حق تأهل/پایهٔ سنوات — names unknown until the
  official دفترچه is obtained; totals currently fold into DSW_MAZ.
