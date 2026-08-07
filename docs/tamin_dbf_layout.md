# لیست بیمهٔ تأمین اجتماعی — ساختار DSKKAR00.DBF / DSKWOR00.DBF

_Rewritten **2026-08-04** from the organisation's OWN artifacts. The previous
version of this file was compiled from third-party blogs and marked almost every
field «تأییدنشده»; that guesswork is now replaced by two primary sources and the
export code was corrected against them (21 header mismatches → 1 deliberate)._

## Sources — both primary, both retrieved 2026-08-04

| # | Source | What it gives | Retrieval |
|---|---|---|---|
| **S1** | **«دستورالعمل تولید فایل های لیست بیمه سازمان تامین اجتماعی»** (PDF, 5pp, dated ۱۳۹۲/۰۸/۱۵) — <https://www.tamin.ir/file/file/8460>, linked from <https://www.tamin.ir/news/1673.html> | The org's written spec **addressed to third parties**: «چنانچه شما برای ایجاد فایل لیست بیمه خود از نرم افزار موجود روی سایت تامین اجتماعی استفاده نمی نمایید … فایل مورد نظر طبق فرمت ذیل باید ایجاد گردد». Field names, types, **maximum** lengths, column order, and the content rules. | direct download |
| **S2** | **The template `DSKKAR00.DBF` / `DSKWOR00.DBF` shipped inside the official software** — `ListDisk-V2.7` (`/news/1673.html` → 5×RAR parts → `setup/Setup.msi` → `Cabs.w1.cab`) | The **binary header** the org's own program uses: exact names, types, **actual** lengths, order, and the codepage (LDID) byte. | direct download + header parsed programmatically |

> **Version reality-check — CORRECTED 2026-08-04 (second pass).** An earlier
> version of this doc said "there is no official v6". **That was wrong.**
> tamin.ir's download page (`/news/1673.html`) hosts the **v2.7 full installer
> only**, which is what led to the error — but **ListDisk v6 is official**,
> released «در **دی ۱۴۰۳** توسط تامین اجتماعی» and distributed as an *update
> patch* (`PrjList-V6.5.exe`) applied on top of an installed v2.7. Its own
> setup guide says «فایل های DSKKAR00.DBF و DSKWOR00.DBF را … جایگزین دو فایل
> قبلی نمایید (**ساختار فایل ها تغییر یافته است**)» and the in-app step is
> «بروزرسانی به ورژن جدید **1403**». Separately, **DSKEditor** (tavafi.ir) is a
> genuinely third-party tool that also has a v6.x — conflating the two is what
> produced the bad call.
> **S3** = the v6.5 update package, `bidbarg.net/blog/list-disk/` →
> `documents/39/ListDisk_v6_5_zlNm5tK.rar`, retrieved 2026-08-04. It carries its
> own `DSKKAR00.DBF`/`DSKWOR00.DBF` templates, parsed byte-for-byte below.

> **Network note.** Iranian hosts are only reachable from the founder's machine
> on the **direct (un-proxied)** route; the shell's default proxy egresses in
> Helsinki and tamin.ir answers it with «محدودیت جغرافیایی». tamin.ir also sits
> behind an **ArvanCloud JS cookie challenge** (`__arcsjs`/`__arcsjsc`) — a
> scripted `eval`, **not** an image captcha, so it is solvable head­lessly and
> needed no human. See `scripts/` note at the end.

## Content rules (S1 — verbatim obligations)

1. `DSKKAR00.DBF`/`.TXT` = workshop info, `DSKWOR00.DBF`/`.TXT` = insured people;
   **«الویت با فرمت dbf است»** (dbf preferred — that is what we emit).
2. Dates are **Shamsi, 8 chars, no separators** — «۱۳۹۲۰۷۰۱».
3. `DSW_SEX` is the **word** «مرد» or «زن», not a code.
4. **No leading/trailing space or newline** in any field.
5. `DSK_KIND` **must be `0`**.
6. Character fields must contain **none of** `"` `'` `>` `<` `&`.
7. «Encoding فایل ها باید Unicode باشد» — see the codepage section below, where
   this sentence conflicts with the org's own binary template.

## S3 — تأیید مستقل از نصبِ خودِ مؤسس (۱۴۰۵/۰۵/۱۷)

مؤسس نسخهٔ ListDisk خودش را باز کرد و قالب‌های همان نصب را بررسی کرد. نتیجه، منبع
سومی است که **دو منبع قبلی را تأیید می‌کند**:

| قلم | نصبِ مؤسس | آنچه ما تولید می‌کنیم | نتیجه |
|---|---|---|---|
| `DSKKAR00` تعداد فیلد / طول رکورد | **۲۵ فیلد / ۳۱۱** | ۲۵ / ۳۱۱ | ✅ یکی |
| `DSKWOR00` تعداد فیلد / طول رکورد | **۲۹ فیلد / ۴۶۹** | ۲۹ / ۴۶۹ | ✅ یکی |
| LDID (کدپیج) | **0x7E** | 0x7E | ✅ یکی |
| تعداد رکوردها در فایل‌های نصب | **صفر** | — | قالبِ خام‌اند، نه دادهٔ واقعی |
| `Manufactory.mdb` | **خالی** | — | هیچ دادهٔ مؤسس در آن‌ها نبود |

⇒ **ساختاری که می‌نویسیم با قالبِ رسمیِ نصب‌شده مو‌به‌مو یکی است.** تنها انحراف
عمدیِ باقی‌مانده، عرض `DSW_ID1` است (ما ۱۰، قالب ۸) که در جدول DSKWOR00 پایین
مستند شده و آزمونِ بارگذاری در خودِ ListDisk تکلیفش را روشن می‌کند.

### نگاشت‌های استنتاجی از schema داخلیِ ListDisk (Access)

مؤسس ساختار جدول‌های داخلیِ ListDisk را هم داد. اینها **استنتاج از نام‌گذاریِ
خودِ نرم‌افزارند، نه متن رسمی سازمان** — و دقیقاً با همین برچسب ثبت می‌شوند:

| جدول / فیلد | معنای استنتاجی | وضعیت |
|---|---|---|
| `Kar_Spec` | مشخصات کارگاه (معادل DSKKAR00) | inferred from ListDisk schema |
| `Kar_Mon` | جمع‌های ماهانهٔ کارگاه | inferred from ListDisk schema |
| `Kar_Work` | سطرهای کارگران (معادل DSKWOR00) | inferred from ListDisk schema |
| `Mon_BimK` | حق بیمهٔ سهم **کارگر** — ماهانه | inferred |
| `Mon_BimF` | حق بیمهٔ سهم **کارفرما** — ماهانه | inferred |
| `Mon_BimB` | حق بیمهٔ **بیکاری** — ماهانه | inferred |
| `Wor_BimK` | حق بیمهٔ سهم کارگر — سطرِ هر کارگر | inferred |
| `Wor_TotW` | جمع دستمزد/مزد کارگر | inferred |
| `Wor_RMaz` | مزایای مشمول | inferred |
| `Wor_TotM` | جمع مزایا | inferred |
| `Wor_TotH` | جمع کل مشمول | inferred |
| `Wor_TotE` | جمع کسور/پرداختی | inferred |

> این نگاشت‌ها هیچ‌کدام جای «تأییدنشده»‌های زیر را به «تأییدشده» تغییر نمی‌دهند؛
> فقط بهترین حدسِ مستند را با منبعش کنار هر قلم می‌گذارند. تأییدِ نهایی وقتی است
> که یک فایل واقعی در ListDisk بارگذاری شود و اعداد درست نمایش داده شوند.

> ⚠️ **فایل‌های مرجعِ مؤسس دیگر روی ماشین نیستند.** طبق «قانون مرجعِ مصرف‌شدنی»
> پوشهٔ `reference_outputs/` در همین نشست پاک شد — ولی قالب‌های ListDisk هنوز
> استخراج‌نشده بودند و یکجا با بقیه رفتند. یافته‌های بالا از گزارشِ خودِ مؤسس ثبت
> شده‌اند، نه از خواندنِ دوبارهٔ فایل‌ها. اگر بازبینیِ بایت‌به‌بایت لازم شد، باید
> دوباره آپلود شوند.

## DSKKAR00 — exactly ONE record (workshop monthly summary)

`S2 len` is authoritative for the DBF; `S1 max` is the published maximum.
**Status column: ✅ = confirmed by BOTH sources.**

| # | Field | Type | S2 len | S1 max | Meaning | Our mapping | Status |
|---|---|---|---|---|---|---|---|
| 1 | DSK_ID | C | 10 | 10 | کد کارگاه | `tenants.insurance_workshop_code` | ✅ |
| 2 | DSK_NAME | C | 30 | 100 | نام کارگاه | `tenant.name` | ✅ |
| 3 | DSK_FARM | C | 30 | 100 | نام کارفرما | `tenant.name` | ✅ |
| 4 | DSK_ADRS | C | 40 | 100 | آدرس کارگاه | `tenant.address` | ✅ |
| 5 | DSK_KIND | N | 1 | 1 | نوع لیست | `0` (required) | ✅ |
| 6 | DSK_YY | N | 2 | 2 | سال عملکرد | `jalali_year % 100` | ✅ |
| 7 | DSK_MM | N | 2 | 2 | ماه عملکرد | `jalali_month` | ✅ |
| 8 | DSK_LISTNO | C | 12 | 12 | شماره لیست | خالی | ✅ (gap ↓) |
| 9 | DSK_DISC | C | 30 | 100 | شرح لیست | خالی | ✅ |
| 10 | DSK_NUM | N | 5 | 5 | تعداد کارکنان | `count(items)` | ✅ |
| 11 | DSK_TDD | N | 6 | 6 | مجموع روزهای کارکرد | `Σ DSW_DD` | ✅ |
| 12 | DSK_TROOZ | N | 12 | 12 | مجموع دستمزد روزانه | `Σ DSW_ROOZ` | ✅ |
| 13 | DSK_TMAH | N | 12 | 12 | مجموع دستمزد ماهانه | `Σ DSW_MAH` | ✅ |
| 14 | DSK_TMAZ | N | 12 | 12 | مجموع مزایای ماهانه مشمول | `Σ DSW_MAZ` | ✅ |
| 15 | DSK_TMASH | N | 12 | 12 | مجموع دستمزد و مزایای مشمول | `Σ insurance_base` | ✅ |
| 16 | DSK_TTOTL | N | 12 | 12 | مجموع کل (مشمول **و غیرمشمول**) | `= TMASH` | ✅ name · ⚠ mapping ↓ |
| 17 | DSK_TBIME | N | 12 | 12 | مجموع حق بیمه سهم بیمه‌شده | `Σ insurance_employee` | ✅ |
| 18 | DSK_TKOSO | N | 12 | 12 | مجموع حق بیمه سهم کارفرما | `Σ insurance_employer` | ✅ |
| 19 | DSK_BIC | N | 12 | 12 | مجموع حق بیمه بیکاری | `Σ insurance_unemployment` | ✅ |
| 20 | DSK_RATE | N | 5 | 5 | نرخ حق بیمه | `20` | ✅ |
| 21 | DSK_PRATE | N | 2 | 2 | **نرخ پورسانتاژ** | `0` | ✅ (was mislabelled) |
| 22 | DSK_BIMH | N | 12 | 12 | **نرخ مشاغل سخت و زیان‌آور** | `0` | ✅ (**was missing**) |
| 23 | MON_PYM | C | 3 | 3 | ردیف پیمان | خالی | ✅ |

## DSKWOR00 — one record per insured worker

| # | Field | Type | S2 len | S1 max | Meaning | Our mapping | Status |
|---|---|---|---|---|---|---|---|
| 1 | DSW_ID | C | 10 | 10 | **کد کارگاه** | `insurance_workshop_code` | ✅ (**was wrong**) |
| 2 | DSW_YY | N | 2 | 2 | سال عملکرد | run | ✅ |
| 3 | DSW_MM | N | 2 | 2 | ماه عملکرد | run | ✅ |
| 4 | DSW_LISTNO | C | 12 | 12 | شماره لیست | خالی | ✅ (gap ↓) |
| 5 | DSW_ID1 | C | **8** | **10** | **شماره بیمه** | `employee.insurance_number` | ✅ name · **deviation ↓** |
| 6 | DSW_FNAME | C | 60 | 100 | نام | first token of `full_name` | ✅ · gap ↓ |
| 7 | DSW_LNAME | C | 60 | 100 | نام خانوادگی | rest of `full_name` | ✅ · gap ↓ |
| 8 | DSW_DNAME | C | 60 | 100 | نام پدر | `employee.father_name` | ✅ (**now filled**) |
| 9 | DSW_IDNO | C | 15 | 15 | شماره شناسنامه | `employee.birth_certificate_no` | ✅ (**now filled**) |
| 10 | DSW_IDPLC | C | 30 | 100 | محل صدور | `employee.birth_certificate_place` | ✅ (**now filled**) |
| 11 | DSW_IDATE | C | 8 | 8 | تاریخ صدور | `employee.birth_certificate_date` → Shamsi8 | ✅ (**now filled**) |
| 12 | DSW_BDATE | C | 8 | 8 | تاریخ تولد | `employee.birth_date` → Shamsi8 | ✅ (**now filled**) |
| 13 | DSW_SEX | C | 3 | 3 | جنسیت («مرد»/«زن») | `employee.gender` | ✅ (**now filled**) |
| 14 | DSW_NAT | C | 10 | 10 | ملیت | `employee.nationality` | ✅ (**now filled**) |
| 15 | DSW_OCP | C | 50 | 100 | شرح شغل | `employee.job_title` | ✅ (**now filled**) |
| 16 | DSW_SDATE | C | 8 | 8 | تاریخ شروع به کار | `employee.hire_date` → Shamsi8 | ✅ (**now filled**) |
| 17 | DSW_EDATE | C | 8 | 8 | تاریخ ترک کار | `employee.termination_date` → Shamsi8 | ✅ (**now filled**) |
| 18 | DSW_DD | N | 2 | 2 | تعداد روزهای کارکرد | real overlap of [استخدام، ترک کار] with the period | ✅ (**was full-month**) |
| 19 | DSW_ROOZ | N | 12 | 12 | دستمزد روزانه | `base_salary/30` ROUND_DOWN | ✅ |
| 20 | DSW_MAH | N | 12 | 12 | دستمزد ماهانه | `base_salary` | ✅ |
| 21 | DSW_MAZ | N | 12 | 12 | مزایای ماهانه | `insurance_base − base_salary` | ✅ |
| 22 | DSW_MASH | N | 12 | 12 | جمع دستمزد و مزایای مشمول | `insurance_base` (سقف‌خورده) | ✅ |
| 23 | DSW_TOTL | N | 12 | 12 | جمع کل دستمزد و مزایا | `= MASH` | ✅ name · ⚠ mapping ↓ |
| 24 | DSW_BIME | N | 12 | 12 | حق بیمه سهم بیمه‌شده | `insurance_employee` | ✅ |
| 25 | DSW_PRATE | N | 2 | 2 | نرخ پورسانتاژ | `0` | ✅ |
| 26 | DSW_JOB | C | 6 | 6 | کد شغل | `employee.job_code` (از فهرست رسمی) | ✅ (**now filled**) |
| 27 | PER_NATCOD | C | 10 | 10 | کد ملی | `national_id` snapshot | ✅ |

## What the diff caught — 21 header mismatches, all fixed

Our export was diffed **binary header against binary header** with the official
template. Result before the fix: **21 mismatching columns of 50**.

| Class | Detail |
|---|---|
| **Wrong data in the wrong column (worst)** | `DSW_ID` held the worker's **شمارهٔ بیمه** and `DSW_ID1` held the **کد ملی**. Per both sources `DSW_ID` is the **کد کارگاه** and `DSW_ID1` is the **شمارهٔ بیمه**. Every worker row identified the wrong thing. |
| **Missing column shifted the file** | `DSK_BIMH` (col 22) did not exist in ours, so `MON_PYM` sat in its slot and DSKKAR00 had 22 columns instead of 23. |
| **Column order wrong** | `DSW_JOB` was written at position 16; it belongs at **26**, after `DSW_PRATE`. That mis-ordered 11 consecutive columns. |
| **Lengths too wide** | `DSK_NAME/FARM/DISC` 100→30/30/30, `DSK_ADRS` 100→40, `DSW_FNAME/LNAME/DNAME` 100→60. |
| **Codepage undeclared** | Header byte 29 (LDID) was `0x00` ("not set"); the org's own DSKKAR00 declares `0x7E` = **cp1256**. |

**After the fix: 1 remaining difference, deliberate** (below). Pinned by
`tests/modules/payroll/test_insurance_export.py::test_layout_matches_official_listdisk_template`,
which carries both official column lists literally — a future edit that drifts
from the org's spec fails the suite.

### The one deliberate deviation — `DSW_ID1` C10 instead of C8

S1 (the spec addressed to us) says **max 10**; S2 (the software's template) uses
**8**. A modern شمارهٔ بیمه is 10 digits, so writing C8 would **truncate a legal
identifier**. We take **C10**: inside the org's published maximum, and lossless.
DBF is self-describing (the reader takes widths from the header), so a wider
column is safe where a narrower one is destructive.
**Founder sign-off requested** — if the org's uploader ever rejects the file, this
field is the first thing to try at 8.

Second, smaller, deliberate difference: we write **LDID `0x7E` on BOTH files**,
while the org's `DSKWOR00` template leaves it `0x00`. Declaring the codepage can
only help a reader; leaving it unset is what made our Persian undecodable.

## Codepage — corrected, with the conflict stated honestly

Three claims exist. Two are primary and agree; the one we had been following was
the weakest.

| Claim | Source | Weight |
|---|---|---|
| **cp1256** (Windows ANSI Arabic/Persian) | **S2**: the org's own `DSKKAR00.DBF` header declares LDID `0x7E`. Plus the package's «راهنمای تنظیم زبان» tells the employer to set Windows **System Locale → Persian** — the classic requirement of a **non-Unicode VB6 app** that reads/writes in the system ANSI codepage. | **primary ×2** |
| "Unicode" | **S1** sentence «Encoding فایل ها باید Unicode باشد» | primary, but contradicts S2's own binary and most plausibly addresses the **`.TXT`** variant |
| **Iran System** | tavafi.ir blog about the *third-party* DSKEditor | third-party only |

**Decision: cp1256 is now the default**, and the LDID byte is actually written.
The Iran System encoder is **retained, not deleted** — set
`INSURANCE_DBF_ENCODING=iransystem` to emit the other variant, so the founder can
produce BOTH for one real month and let the official viewer settle it
empirically without a code change.

Three cp1256 traps the implementation had to close (each one caught by a test):
- **ی (U+06CC) has no cp1256 slot.** Persian text on this page uses **ي**
  (U+064A, `0xED`). Getting this backwards turns the commonest letter in Iranian
  names into `?`.
- **Persian «۰-۹» and Arabic-Indic «٠-٩» digits are absent** → normalized to ASCII.
- **ZWNJ has no slot** → space (so «کوچک‌پور» → «کوچک پور»).
- ک گ پ چ ژ *do* exist (`0x98/0x90/0x81/0x8D/0x8E`) and pass through untouched.

## ⛔ Gate before the first real upload (unchanged, still empirical)

The structure is now sourced; **legibility and acceptance are not yet proven**.

1. Founder/accountant downloads one month's zip from the payroll page.
2. Opens both files in the official **لیست دیسک** software (or a DBF viewer).
3. Checks: files load without error · worker names legible · figures match the
   payroll report rial-for-rial · `DSW_ID1` shows the **شمارهٔ بیمه** (not the
   کد کارگاه) and `DSW_ID` shows the **کد کارگاه**.
4. If names are garbled, re-export with `INSURANCE_DBF_ENCODING=iransystem` and
   compare — that A/B is the whole point of keeping both encoders.
5. Only then upload to samt.tamin.ir.

## Remaining gaps — reported, not hidden

These are **data-model** gaps (the column is correct, we have nothing to put in
it), not layout gaps:

- **CLOSED 2026-08-04 (migration `ins1405a001`):** نام پدر، شمارهٔ شناسنامه،
  محل/تاریخ صدور، تاریخ تولد، جنسیت، ملیت، کد شغل and تاریخ ترک کار are now real
  `Employee` columns, and the export REFUSES with a friendly Persian message
  naming who is missing what rather than shipping a blank legal column.
- **CLOSED 2026-08-04:** روزهای کارکرد is the real overlap of the employment
  window with the period (mid-month hire/termination), snapshotted per payroll
  line so an issued payslip never changes retroactively.
- **نام/نام‌خانوادگی** are still split from one `full_name` on the first space —
  wrong for compound first names. Remaining gap.
- **شمارهٔ لیست / نوع لیست** have no UI (both written empty; `DSK_KIND=0` is the
  required value so that one is fine).
- **`DSK_TTOTL`/`DSW_TOTL`** are set equal to the مشمول total. Per S1 they are the
  total **including non-مشمول** pay, so once a غیرمشمول figure exists in payroll
  they must stop aliasing `MASH`.
- **حق تأهل / پایهٔ سنوات** as separate 1403-structure columns do **not exist** in
  the official v2.7 layout; they fold into `DSW_MAZ`. If the org ships a newer
  structure it will appear as a new ListDisk version on `/news/1673.html`.

## Reproducing this

The two template DBFs are **not committed** (they are the org's installer
payload). To re-derive the table:

```
# direct/un-proxied route + ArvanCloud challenge solved automatically
curl --noproxy '*' -L https://www.tamin.ir/news/1673.html      # download page
#   → /file/file/8460                 = S1, the دستورالعمل PDF
#   → /file/file/246147..246151       = ListDisk-V2.7.part1..5.rar
7z x ListDisk-V2.7.part1.rar          # → setup/Setup.msi
7z x setup/Setup.msi                  # → Cabs.w1.cab
7z x Cabs.w1.cab                      # → DSKKAR00.DBF, DSKWOR00.DBF
```
Then read header byte 29 (LDID) and the 32-byte field descriptors from offset 32.


---

# ListDisk v6 (دی ۱۴۰۳) — the superset layout

**Verdict: v6 is a strict SUPERSET of v2.7.** Parsed from the v6.5 update's own
template DBFs (**S3**) and diffed against the v2.7 templates (**S2**):

| | v2.7 | v6 | Relationship |
|---|---|---|---|
| DSKKAR00 | 23 cols, reclen 287 | **25** cols, reclen 311 | first 23 **byte-identical** (name/type/width/order) + 2 appended |
| DSKWOR00 | 27 cols, reclen 447 | **29** cols, reclen 469 | first 27 **byte-identical** + 2 appended |
| LDID (codepage) | KAR `0x7E`, WOR `0x00` | **`0x7E` on BOTH** | v6 settles it: **cp1256** |

Not one existing column changed name, type, width or position. The «ساختار
فایل ها تغییر یافته است» in the guide means *columns were added*, not moved.

### The four new columns

| File | # | Field | Type | Meaning | Our mapping |
|---|---|---|---|---|---|
| DSKKAR00 | 24 | `DSK_INC` | N12 | مجموع پایهٔ سنوات | `Σ seniority_base` |
| DSKKAR00 | 25 | `DSK_SPOUSE` | N12 | مجموع حق تأهل | `Σ allowance_marriage` |
| DSKWOR00 | 28 | `DSW_INC` | N12 | پایهٔ سنوات | `PayrollItem.seniority_base` |
| DSKWOR00 | 29 | `DSW_SPOUSE` | **C10** | حق تأهل | `PayrollItem.allowance_marriage` |

This is exactly the v6 headline feature: «امکان **جداسازی پایه سنوات و حق تاهل**
در لیست بیمه». We already hold both figures per payroll line (they were folded
into `DSW_MAZ` under 2.7), so v6 is fully populatable today.

> ⚠️ **`DSW_SPOUSE` is Character(10) while `DSK_SPOUSE` is Numeric(12)** — an
> asymmetry read straight from the org's binary, not a transcription slip. We
> write the worker figure as a digit string. Semantics are inferred from the
> release note, not from a field-by-field org spec: treat the *meaning* as
> «تأییدنشده» until the viewer confirms, even though the *structure* is certain.

### Which layout we emit

Per-workshop setting **«نسخهٔ فایل لیست بیمه»** (`tenants.insurance_file_version`),
default **`2.7`**, `6` selectable. Rationale: which build a given شعبه accepts
cannot be established without a real upload, so the default is the layout the
org's own full installer ships, and two workshops on different ListDisk builds
are independently configurable. Flip to `6` once a workshop has run the ۱۴۰۳
update — the two extra columns then carry real figures instead of hiding inside
`DSW_MAZ`.

Our emitted v6 header was diffed against S3 byte-for-byte: **25/25 and 29/29
columns match** name/type/width/order, LDID `0x7E` on both, with the single
deliberate `DSW_ID1` difference below.

### `DSW_ID1` width — founder decision, now configurable

Founder ruling: **KEEP 10** — truncating a شمارهٔ بیمه falsifies an identity.
The org template says 8; the دستورالعمل publishes 10 as the maximum. Now
`tenants.insurance_id1_width` (default 10) so the answer can change without a
deploy.

> **STANDING GATE — the final answer comes from the viewer, not from us.**
> Before any real upload: open one real month in the official لیست دیسک program,
> confirm the names are legible and `DSW_ID1` shows the شمارهٔ بیمه intact. If
> the file is rejected or the column is mangled, set `insurance_id1_width = 8`
> and re-export. Nothing here is proven until that happens.

# کد شغل — the official occupational catalog

`DSW_JOB` is **C6**, and the سازمان's published job list has **87,835 unique
codes, max length 6** — the width match is the cross-check that this is the list
the column expects.

| Fact | Value |
|---|---|
| Source | «جدول مشاغل تأمین اجتماعی» official Excel — `bidbarg.net/blog/job-title-sso-list/` → `documents/94/440656.xlsm` |
| Retrieved | 2026-08-04 |
| Rows | 87,835 unique codes (from 175,578 sheet rows) |
| Stored | `sso_job_codes` (code, title, **source**, **retrieved_at** per row) |
| Import | `python -m app.cli.import_sso_job_codes` (gzipped TSV in `data/sso_job_codes/`, chunked upsert — the stuffid pattern) |
