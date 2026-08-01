# دیباتک — the books, and the state of the demo world

_2026-08-02. Covers (a) the ۱۵۵٬۰۰۰٬۰۰۱-ریال gap the founder asked to repair, and
(b) what the 09120000000 tenant now contains, module by module._

---

## 1. The «۱۵۵٬۰۰۰٬۰۰۱ gap» — the books were never broken

The batch was written on the premise that دیباتک carried **14 legacy short journal
rows** that needed balancing correcting entries. **That premise was false, and no
correcting entries were injected.** Injecting them would have permanently damaged
a correct set of books.

What the DB actually said:

- Zero unbalanced journal entries — every voucher's debits equal its credits.
- Every account-group net summed to exactly `0` across the whole ledger.

The gap was **a classification bug in the ratios report**, not in the ledger. Two
causes, both in `app/modules/accounting/application/ratios.py`:

1. **Equity used the PERIOD's profit, not cumulative retained earnings.** A
   business older than one fiscal period therefore appeared to be missing every
   ریال it had ever earned before the reporting window.
2. **Group «۹» (حساب‌های انتظامی/معلق) was excluded from current assets**, so
   assets under-counted by exactly that group's balance.

Fixed in backend `59efeec`, pinned by
`tests/modules/accounting/test_financial_ratios.py::test_equity_uses_cumulative_retained_earnings_not_just_the_period`.
Live verification on the founder's own tenant:

```
GET /accounting/financial-ratios
  balance_check.balanced = true
  balance_check.difference = "0"
```

The «تراز برقرار نیست» banner is gone because the arithmetic is right, not
because anything was papered over.

**Standing lesson:** when a report disagrees with the ledger, suspect the report
first. A "repair the data" instruction is worth one SQL check before it is worth
one correcting entry.

## 2. The accountant's equity definition (locked)

Per the accountant's voice note, and now enforced in code:

```
حقوق صاحبان سهام = سرمایه + اندوختهٔ قانونی + سود (زیان) انباشته
```

**جاری شرکا is EXCLUDED** — it is a liability of the business toward its
partners, not part of what the owners have in it. It is counted in
`current_liabilities` instead. The نسبت مالکانه card's drill-down shows all three
components plus the total, so the number can be audited from the screen (this
closes سؤال ۶ in `financial_ratios_mapping.md`).

## 3. Rule-of-thumb bands are ADMIN PARAMETERS, never constants

`ownership_ratio_low` / `ownership_ratio_high` (unit: percent, defaults 15 / 20)
live in `tax_parameters` with the source note «پیشنهاد حسابدار — قاعدهٔ
سرانگشتی، قابل‌تنظیم», editable at «پارامترهای مالیاتی» → «بندهای نسبت مالکانه».
Red below the low bound, amber between, green at or above the high bound.

دیباتک currently reads **۸۷٫۵٪ (green)**.

## 4. What the demo world now contains (09120000000 · ترازپیشه دیبا)

Enriched by `scripts/enrich_dibatak_world.py` — the real HTTP API through a real
password login, **idempotent** (a second run creates nothing), and it performs
**no Moadian call of any kind**.

| Module | Before | After |
|---|---|---|
| مشتریان | 8 | 8 |
| کالا و خدمات | 6 | 7 (incl. one **dual-unit** جعبه ↔ مترمربع) |
| تأمین‌کنندگان | 3 | 4 |
| خریدها | 2 | 5 (paid · نسیه · partial) |
| هزینه‌ها | 3 | 10 (spread across the year) |
| درآمدهای غیرعملیاتی | **0** | 5 |
| فاکتورها | 15 | 15 |
| چک‌ها | 2 | 5 — states: `in_progress`, `deposited`, `cleared`, `bounced` |
| دریافت/پرداخت | 13 | 16 |
| برگشت‌ها | 1 (از فروش) | 2 (از فروش **و** از خرید) |
| حساب‌های خزانه | 3 | 3 — بانک ملت now **POS-connected** |
| انتقال بین حساب‌ها | **0** | 1 (صندوق ← بانک) |
| حقوق و دستمزد | 4 کارمند · 2 run | unchanged (deliberately preserved) |

Notes on the choices:

- **The dual-unit product** is «کفپوش آنتی‌استاتیک اتاق سرور»: stocked by the
  جعبه, quoted by the مترمربع, ۱ جعبه = ۲٫۵ m². It is inventory-tracked with a
  low-stock threshold, so the انبار ساده screens have something real to show.
- **Every income and expense names a طرف حساب** because the API refuses an
  anonymous one — correctly: «سود سپرده» with no counterparty is an unauditable
  row. The bank is recorded as a vendor («بانک ملت — شعبهٔ ونک»), which is how an
  Iranian accountant would carry it as a حساب تفصیلی.
- **Cheque states were reached through real transitions** (`deposit`, `bounce`),
  never a status write, so the treasury side effects are genuine.
- Everything this script owns is tagged `[enrich-world]` in its note, so
  enrichment is distinguishable from seed at a glance.

## 5. Known drift found while verifying (NOT fixed here)

`09120001004` (زهرا محمدی, HAM-TEST1) is listed in the generated persona table
with the fixed password `Admin@12345`, but the **restored** database has no
password for her — a live password login returns 401. The frozen contract says
she was granted the password in the FINISH-LINE batch, so this database simply
predates that grant. **Not repaired here**: this DB is the laptop mirror holding
live Moadian credentials, and reseeding is forbidden. Either reseed on a machine
where that is safe, or set her password through the admin panel.

Partner-panel verification was therefore done with **09120000000** instead, who
is an approved partner (HAM-DIBA) *and* has a password.
