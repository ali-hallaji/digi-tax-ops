# Tax numbers in the product — 1404 (value → source → where shown)

Every tax number the product shows, where it lives, and the citation stored with
it. Source of truth for all of them: `docs/tax_research_1404.md`.

The rule this table enforces: **a tax number with no stated source does not
ship.** Anything still unsourced stays flagged «برآوردی» in the UI.

_Applied 2026-07-28 by `app.cli.seed_tax_research_1404`._

---

## Confirmed and live

| # | Value | Stored as | Citation (in `source_note`) | Shown |
|---|-------|-----------|------------------------------|-------|
| 1 | **ماده ۱۳۱ مشاغل** — تا ۵۰۰٬۰۰۰٬۰۰۰ ﷼ ۱۵٪ · تا ۱٬۰۰۰٬۰۰۰٬۰۰۰ ﷼ ۲۰٪ · مازاد ۲۵٪ | `tax_tables(year=1404, kind=article_131)` | پلکان درآمد مشاغل، عملکرد ۱۴۰۴ — research «سؤال ۲», اطمینان بالا | «مالیات من از دو نگاه» — both lenses, per-bracket breakdown |
| 2 | **ماده ۱۰۱ معافیت مشاغل** — ۲٬۰۰۰٬۰۰۰٬۰۰۰ ﷼ | `tax_parameters(article_101_exemption)` | بند (ث) تبصره ۱ قانون بودجه ۱۴۰۴ — research «سؤال ۳» | Deducted before the brackets; shown as «معافیت مشاغل (۱۰۱)» |
| 3 | **ماده ۸۴ معافیت حقوق** — ۲٬۸۸۰٬۰۰۰٬۰۰۰ ﷼ | `tax_parameters(article_84_exemption)` | جزء ۱ بند «ز» تبصره ۱ بودجه ۱۴۰۴ — research «سؤال ۳» | Display/disambiguation only — **never** an input to the مشاغل estimate |
| 4 | **تبصره ۱۰۰ سقف فروش** — ۷۲۰٬۰۰۰٬۰۰۰٬۰۰۰ ﷼ | `tax_parameters(note_100_sales_ceiling)` | research «سؤال ۵», اطمینان بالا برای خودِ رقم | Headroom state ok / near ≥۸۰٪ / over |
| 5 | **نرخ عمومی VAT** — ۱۰٪ (`0.10`) | `tax_parameters(vat_rate_general)` | بند (خ) تبصره ۱ بودجه ۱۴۰۴ — research «سؤال ۱» | Gold pattern's اجرت/حق‌العمل/سود rate |

All five are stored with `is_estimated = false` (تأییدشده). None is a code constant.

### What changed, and why it mattered

The stored ماده ۱۳۱ steps were **wrong by 4×** — caps of ۲ و ۴ میلیارد ریال,
sourced from `ravihesab.com` (unofficial) and flagged `is_estimated=true`.

Worked example, حقیقی with ۳٬۰۰۰٬۰۰۰٬۰۰۰ ﷼ profit:

| | Old (wrong caps, no exemption) | New (researched caps + ماده ۱۰۱) |
|---|---|---|
| Taxable base | ۳٬۰۰۰٬۰۰۰٬۰۰۰ | ۱٬۰۰۰٬۰۰۰٬۰۰۰ |
| Estimated tax | — | **۱۷۵٬۰۰۰٬۰۰۰** |
| Same caps, no exemption | ۶۷۵٬۰۰۰٬۰۰۰ | — |

A حقوقی taxpayer is unaffected (ماده ۱۰۵ flat ۲۵٪, `exemption_applied = 0`) —
ماده ۱۰۱ is a مشاغل exemption and applying it to a legal person would understate
their tax.

### The confusion this design makes impossible

`article_101_exemption` and `article_84_exemption` are **separate keys with
separate Persian labels**, and `resolve_business_exemption()` reads only the
ماده ۱۰۱ key. The research doc flags twice that Persian tax sites publish
۲٬۸۸۰٬۰۰۰٬۰۰۰ as if it were the ماده ۱۰۱ figure; in this schema that substitution
cannot happen silently.

---

## ⚠️ Open — flagged, not resolved

**The تبصره ۱۰۰ derivation contradicts itself in the source.** The research
describes the ceiling as «۱۵۰ برابر معافیت ماده ۸۴» while also stating ماده ۸۴ =
۲٬۸۸۰٬۰۰۰٬۰۰۰ ﷼. Those cannot both hold:

```
150 × 2,880,000,000  = 432,000,000,000   ← the stated multiple
                       720,000,000,000   ← the stated ceiling
```

(The doc's own parenthetical uses ۴٬۸۰۰م ﷼ as the ماده ۸۴ base in that sentence,
which is a third number again.)

**Decision:** the ceiling is stored as the **absolute figure ۷۲۰ میلیارد ریال** —
the one the doc calls «رقم قطعی و پرتکرار» — and the ۱۵۰× relationship is
**deliberately not implemented as a formula**, because computing it would produce
a different, confidently-wrong number. Founder confirmation wanted on which base
the multiple refers to.

**Not yet parameterised (deliberate):**
- **مشارکت ceiling** ۱٬۴۴۰ میلیارد ریال and the «حداکثر دو معافیت» partnership
  rules are recorded as info copy only. They need a partner/share model the
  product does not have; inventing one to hold a number would be worse than the
  gap. Research «سؤال ۳/۵».
- **تبصره ماده ۱۳۱ transparency discount** (۱ واحد per ۱۰٪ growth, max ۵, only
  above ۴۰٪ growth, conditional on prior-year settlement) — needs prior-year
  declared income, which we do not hold.
- **۱۴۰۵ figures** — not legislated yet. The ۱۲٪ VAT rate is a bill, not law. The
  loader is exact-year and will NOT silently reuse 1404 values for 1405.

---

## Activity coefficients (نسبت سود فعالیت)

Unchanged by this batch and still admin-managed per (اینتاکد, year). The
research's contribution is a **source pointer**, now in the admin help: the
official tables are published as PDFs on **intamedia.ir**, split by
خدمات / بازرگانی / تولید, public since ۲۳/۰۳/۱۴۰۱.

Any coefficient without a stored source stays **«برآوردی»**. The research is
explicit that popular figures («سود ۱۵–۳۰٪ سوپرمارکت») are experiential and must
not replace the اینتاکد table — so they are not seeded.

---

## How next year happens

1. Founder supplies the 1405 numbers (budget act).
2. Either edit them in the admin screen, or copy
   `app/cli/seed_tax_research_1404.py` → `..._1405.py` with new values + citations.
3. Nothing in code changes. The loader is exact-year: until a 1405 row exists,
   the year has **no** exemption applied and the UI says so, rather than quietly
   reusing 1404.
