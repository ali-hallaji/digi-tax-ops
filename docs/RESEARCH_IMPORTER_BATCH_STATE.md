# RESEARCH-APPLICATION + IMPORTER BATCH — state (2026-07-28)

Honest resume point. **Landed** and **not started** are both listed; nothing
below is half-built and left dangling.

---

## LANDED

### Part 2.1 — the tax numbers (headline) ✅
Full table with citations: **`docs/tax_numbers_applied_1404.md`**.

- ماده ۱۳۱ مشاغل 1404 was **wrong by 4×** (2B/4B caps from an unofficial site,
  flagged برآوردی). Now ۵۰۰م / ۱٬۰۰۰م at 15/20/25%, cited, **تأییدشده**.
- New `tax_parameters` table for the scalar yearly numbers:
  ماده ۱۰۱ = ۲٬۰۰۰٬۰۰۰٬۰۰۰ · ماده ۸۴ = ۲٬۸۸۰٬۰۰۰٬۰۰۰ · تبصره ۱۰۰ =
  ۷۲۰٬۰۰۰٬۰۰۰٬۰۰۰ · VAT = ۰٫۱۰. Separate keys + labels for 101 vs 84 so the
  commonest Persian-web confusion is unrepresentable.
- Estimator deducts ماده ۱۰۱ before the brackets, **individuals only**.
  Verified: ۳ میلیارد profit → 675,000,000 without vs **175,000,000** with;
  حقوقی unchanged at 750,000,000, `exemption_applied=0`.
- تبصره ۱۰۰ headroom state (ok / near ≥۸۰٪ / over / **unknown**).
- Loader is **exact-year**: no silent fallback to last year's exemption.
- Seed: `app.cli.seed_tax_research_1404`. Backend `2676d73`.

### Part 2.6 — GOLD الگوی سوم, engine ✅ (UI + sandbox NOT done — see below)
`map_type1_pattern3` + 9 passing tests, backend `51a2aea`.
- tcpbs/vam/adis/tsstam per the research formulas; VAT charged on the
  workmanship trio only — the raw-gold value never enters the base.
- The rate is a **parameter** (`vat_rate_general`), not the doc's literal `10`;
  a missing parameter **blocks** the submission instead of guessing.
- `crn` popped for gold; DB columns `gold_consfee/bros/spro` added (tcpbs is
  computed, never stored).
- Specs updated in-batch; gold moved out of the "coming soon" list.

### Part 2.2 — coefficients source pointer ✅
Admin screen now names **intamedia.ir**, the اینتاکد mechanism, and warns that
popular «سود ۱۵–۳۰٪» figures are experiential. Frontend `1c29ded`.

### Part 2.4 — CoA trees ✅
پیمانکاری gains «حساب پیمان» + «کار گواهی‌شده (صورت‌وضعیت تأییدشده)» +
«کارفرما – حساب پیمان». تولیدی **already had** مواد اولیه / در جریان ساخت /
ساخته‌شده — verified, not duplicated.

### Part 2.5 — referring-invoice discrepancy ✅ (doc only, no code change)
`docs/moadian/corrective_inp_inty_experiment_2026-07.md` now records that the
research reads «must MATCH inty/inp» while our sandbox experiment proved
«must OMIT them». Both are true — the org takes them FROM the reference, which is
why repeating them is «خارج از الگو» (error ۱۴۰۰۴, named in the research itself).
Empirical verdict stands; note exists so nobody "corrects" it back.

### Part 1 — pricing, schema + procedure ✅ (checkout/UI NOT done)
- `module_price_history` (append-only) + `module_prices.effective_from`,
  **back-filled from current prices** so the log is not born empty.
- `module_prices.pack_units` + `document_quota_packs` — the overage SKU modelled
  as a **consumable**, deliberately not an entitlement (a second purchase of an
  entitlement is rejected as «از قبل فعال است», which is wrong for something
  that depletes).
- **`docs/document_cap_flip_procedure.md`** — the `DOCUMENT_CAP_ENFORCED` flip,
  including the fact that packs only deplete once the flag is ON.

---

## NOT DONE — resume here

### Part 1 remainder
1. `document_pack` **SKU row + price** (nothing is purchasable yet).
2. Checkout support: `_price_the_basket` currently rejects an already-entitled
   feature — a consumable must bypass that, and `_activate_paid_order` must
   create a `DocumentQuotaPack` instead of flipping an entitlement.
3. Usage card must add purchased headroom (`document_usage` → `included` +
   remaining pack units).
4. Admin price-history UI (table exists and is populated; no screen reads it).
5. Plans page polish.

### Part 2.3 — party interim-account voucher (NOT STARTED)
Research «سؤال ۷»: named payments should route through an interim payable
(تفصیلی طرف) — expense credits it, payment debits it — generated as ONE combined
voucher, so the party ledger shows **گردش** with a **net-zero مانده**. Also needs
گردش alongside مانده in the party-balances report. This is the largest remaining
accounting change and was not begun.

### Part 2.6 remainder — gold UI + sandbox proof
The engine is done and tested; a merchant still cannot enter gold values.
Needs: line-form fields shown only when الگوی ۳ is selected (ui-ux-pro-max, calm
goldsmith copy), validation mirroring the org rules, per-pattern Excel sample,
then **one accepted sandbox gold invoice on a fresh reference**.
Per the batch instruction: if the org rejects our formula reading, report the
exact response and STOP that leg — no formula guessing beyond the sourced one.

### Part 3 — IMPORTER (NOT STARTED)
Real-sample findings are already banked and **correct two points in the spec**:

| Spec said | Reality (verified by magic bytes) |
|---|---|
| Tadbir = real BIFF `.xls` | **OOXML/xlsx** (`50 4B 03 04`, `xl/workbook.xml`) with a `.xls` extension |
| Sepidar = SpreadsheetML | ✅ confirmed (`EF BB BF` + `<?xml`, `urn:schemas-microsoft-com:office:spreadsheet`) |

So sniffing must be by **content**, and the set is SpreadsheetML + OOXML + BIFF +
CSV. Other banked facts:
- **Tadbir sales**: 23 columns, 62 data rows, **no trailing totals row**. Dates
  `1405/02/09`. Customer hints live in شرح with **no separator** —
  `09125984941اقای سجادی - شماره پیش فاکتور :10482`; many rows have no customer
  at all. Column V «شماره منحصر به فرد مالیاتی» is empty throughout.
- **Sepidar payroll**: 6 columns (کد/عنوان/گردش بدهکار/گردش بستانکار/مانده…),
  6 data rows, **row 8 is a totals row** (blank کد+عنوان, amounts present,
  sum 629,413,058 — exactly the six rows).
- ⚠️ **The payroll file is ONE-SIDED**: all debit, credit = 0. A journal voucher
  must balance, so a naive import produces an unbalanced voucher. The honest
  design — and it ties straight into Part 2.3 — is to ask the user for the
  balancing payable («حقوق و دستمزد پرداختنی») and generate a balanced voucher.
- ⚠️ **Headers use Arabic ك/ي** («كد», «بدهكار»), not Persian ک/ی. Header
  matching MUST normalize Arabic↔Persian or it matches nothing.

### Part 4 — cleanup (NOT STARTED)
Still open from `PRIORITY_BATCH_STATE.md`: prod_smoke false-green (`otp_hint`
not matched + probes the one hint-protected mobile), 1.7 GB untracked DB dumps
in the ops worktree on the server, `smoke_test.sh` stale vs captcha, matrix rows
citing pre-rotation taxids.

---

## Open questions for the founder

1. **تبصره ۱۰۰ base** — the research says «۱۵۰ برابر ماده ۸۴» AND ماده ۸۴ =
   ۲٬۸۸۰٬۰۰۰٬۰۰۰, but 150 × 2.88B = 432B ≠ the 720B it reports. Stored the
   absolute 720B; the multiple is deliberately not a formula. Which base is right?
2. **Gold rounding** — we round half-up (489,541) where the ترازسامانه example
   truncates (489,540). Confirm on the sandbox before anyone "fixes" it.
3. **Partnership rules** (max two ماده ۱۰۱ exemptions, ۱٬۴۴۰ میلیارد مشارکت
   ceiling) need a partner/share model we do not have — info copy for now.
