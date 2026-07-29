# حقوق و دستمزد v1 — design doc

_Written 2026-07-29, BEFORE any code, from the founder's own سپیدار reference files.
This doc is the contract; the implementation follows it. Where it says OPEN, the
number or rule is **not** invented in code — it stays admin-parametric and flagged
«برآوردی» until the accountant confirms it._

Reference files (in-repo):
- `docs/import-samples/حقوق دستمزد سپيدار.xls` — a REAL payroll تراز export
- `docs/reference/سرفصل هاي سپيدار.xls` — the سپیدار chart skeleton
- `docs/reference/عملیات مالی حسابداری.JPG` — the سپیدار accounting menu

---

## 0. Why this module, and what v1 is NOT

The founder's repositioning (LAUNCH_ROADMAP § Positioning) made small/medium
**companies** a first-class audience, and حقوق و دستمزد is the single most-asked
capability from that shape of customer — the thing that makes us
replaceable-by-Sepidar without it.

**v1 is a payroll *document*, not a payroll *engine*.** It computes what an
Iranian monthly payslip computes, books it correctly, and prints it. It does
**not** do: مرخصی/کارکرد accrual, عیدی/سنوات/پایان خدمت provisioning, لیست بیمه
(DSKWEB) or لیست مالیات حقوق file generation, شیفت/نوبت‌کاری coefficients, وام
و مساعده ledgers, or multi-contract employees. Those are named here so their
absence is a decision, not an oversight.

---

## 1. What the real سپیدار export actually says (empirical, not assumed)

The founder's `حقوق دستمزد سپيدار.xls` is a one-sided (debit-only) تراز of the
سپیدار **611xxx** cost class:

| سپیدار code | عنوان | ریال |
|---|---|---|
| 611001 | حقوق پايه | ۳۷۰٬۶۸۵٬۴۱۴ |
| 611003 | بن كارگري و خواروبار و مسكن | ۱۰۴٬۰۰۰٬۰۰۰ |
| 611005 | حق تاهل | ۱۰٬۰۰۰٬۰۰۰ |
| 611008 | حق اولاد | ۳۳٬۲۵۰٬۰۰۰ |
| 611016 | بيمه بيكاري | ۱۴٬۵۴۰٬۵۶۲ |
| 611017 | بيمه سهم كارفرما | ۹۶٬۹۳۷٬۰۸۲ |
| | **جمع** | **۶۲۹٬۴۱۳٬۰۵۸** |

### 1.1 The insurance base, derived from the file itself

The two insurance rows are not decoration — they pin down the employer base
exactly. Solving for the base that produces both figures:

```
base + بن + حق تأهل = 370,685,414 + 104,000,000 + 10,000,000 = 484,685,414

484,685,414 × 0.20 = 96,937,082.80  → floor → 96,937,082  == file ✓
484,685,414 × 0.03 = 14,540,562.42  → floor → 14,540,562  == file ✓
```

Including حق اولاد gives ۱۰۳٬۵۸۷٬۰۸۲ / ۱۵٬۵۳۸٬۰۶۲ — **not** the file's numbers.
The جمع row reconciles to the ریال.

**Three rules fall out of this, and v1 implements exactly these:**

1. **حق اولاد is OUTSIDE the insurance base.** بن and حق تأهل are INSIDE.
   (This is also the standard تأمین اجتماعی treatment; the file confirms it
   rather than us asserting it.)
2. **Employer share = ۲۰٪ + ۳٪ بیمه بیکاری**, booked as **two separate cost
   accounts**, exactly as سپیدار does — not one merged ۲۳٪ line.
3. **Truncation, not rounding.** Both figures are `floor`, and a ۱-ریال
   half-up difference would have shown. Same discipline the Moadian packet
   builder already uses (`moadian_rial_truncation`).

### 1.2 What the export does NOT carry

No employee ۷٪ row, no مالیات حقوق row, no net-payable row — the export is
filtered to the 611xxx **cost** class, and the deduction/credit side lives in
the 2xxx liabilities. This is why `ledger_import` already had to invent the
balancing leg on **2103 حقوق و دستمزد پرداختنی** (see
`app/modules/ledger_import/application/service.py`). v1 produces that credit
side properly, from real data, instead of guessing it.

---

## 2. Chart of accounts

### 2.1 Cost side — under `53 هزینه‌ها` (the class the founder named)

The سپیدار 611xxx class maps onto our existing `53` هزینه‌ها کل. `5302 حقوق`
**already exists** as a default expense-category معین and is REUSED for حقوق پایه
— no second «حقوق» account appears in anyone's tree.

| our code | عنوان | سپیدار equivalent |
|---|---|---|
| `5302` | حقوق (existing معین — reused) | 611001 حقوق پايه |
| `5311` | بن کارگری، خواروبار و مسکن | 611003 |
| `5312` | حق تأهل | 611005 |
| `5313` | حق اولاد | 611008 |
| `5314` | اضافه‌کاری | — (manual in v1) |
| `5315` | سایر مزایا | — |
| `5316` | بیمه سهم کارفرما | 611017 |
| `5317` | بیمه بیکاری | 611016 |

**Collision safety (this is load-bearing).** Custom expense categories are
allocated sequentially from `5307` (`chart.category_code`), so a tenant with
five or more custom categories would already own `5311`. Therefore:

- payroll معین are allocated by `ensure_payroll_account()` with a **preferred
  code + next-free fallback**, keyed on `(entity_type='payroll_component',
  component)` — never on the code. An existing tenant whose `5313` is «قبوض»
  gets its اضافه‌کاری at the next free code and nothing is aliased.
- `category_code()` for NEW custom categories skips the reserved `5311–5317`
  block, so the collision cannot grow going forward.

The alternative — a brand-new `54` کل — was rejected: the founder named the
`5302/5314` class explicitly, and a second cost کل would split «هزینه‌ها» in
every report that already sums `53`.

### 2.2 Credit side — under `21 حساب‌های پرداختنی`

| our code | عنوان | role |
|---|---|---|
| `2103` | حقوق و دستمزد پرداختنی (existing) | **parent معین**; one تفصیلی per employee = the per-person ledger |
| `2104` | بیمه تأمین اجتماعی پرداختنی | employee ۷٪ + employer ۲۳٪, owed to the org |
| `2105` | مالیات حقوق پرداختنی | withheld ماده ۸۶ tax, owed to the org |

`2103` already exists (added for `ledger_import`) and is currently a flat معین.
v1 gives it تفصیلی children — `ensure_detail(parent_code='2103',
entity_type='employee', entity_id=<employee id>)` — which is what makes
«گردش این کارمند» answerable. `2104`/`2105` are new معین under the existing
`21` کل, so no new کل and no renumbering.

> **Deliberate v1 limit:** `2104` and `2105` accumulate and are settled by an
> ordinary هزینه/پرداخت document to سازمان تأمین اجتماعی / اداره مالیات. v1 does
> not model that settlement as its own document — the merchant records it the
> way they already record any other payment. Named here so the growing balance
> reads as intentional, and surfaced in the payroll report as «بدهی به سازمان‌ها».

---

## 3. The numbers — every one admin-parametric, none a code constant

The house rule stands: **a tax number with no stated source does not ship**
(`tax_numbers_applied_1404.md`). Payroll adds no exception.

### 3.1 مالیات حقوق — ماده ۸۴/۸۶, its OWN table

Stored in the existing `tax_tables` table under a **new `kind = "article_84"`**,
one row per Jalali year, same `{cap, rate}` bracket JSON, same `is_estimated`
flag, same admin screen. The ماده ۸۴ **exemption** is the already-existing
`tax_parameters` key `article_84_exemption` (۲٬۸۸۰٬۰۰۰٬۰۰۰ ﷼/سال for 1404,
confirmed, `is_estimated=false`).

**THE RULE THIS ENFORCES — the one the codebase already exists to protect:**

```
ماده ۱۰۱  = معافیت مشاغل   → article_101_exemption → the BUSINESS estimate
ماده ۸۴   = معافیت حقوق     → article_84_exemption  → the PAYROLL calc
```

They are different systems with different numbers, and `tax_parameters.py`
already refuses to substitute one for the other (`resolve_business_exemption`
reads only the ۱۰۱ key). The payroll calculator gets a **mirror-image**
`resolve_salary_exemption()` that reads only the ۸۴ key and likewise refuses the
۱۰۱ figure. `load_active_tax_table_meta(..., kind="article_84")` already takes
`kind` as a parameter — no change to that loader.

The calculation is **monthly**: `monthly_exemption = article_84_exemption / 12`,
`monthly_bracket_caps = yearly_caps / 12`, matching how a Iranian payslip is
actually produced. Taxable = مشمول مالیات earnings − monthly exemption, then the
brackets. Truncated to the ریال.

**⚠️ OPEN — the 1404 ماده ۸۵ brackets are NOT in `docs/tax_research_1404.md`.**
The research covers ۱۳۱/۱۰۱/۱۰۰/VAT and the ۸۴ *exemption*, but not the salary
*steps*. v1 therefore seeds the 1404 `article_84` table with the widely-published
figures **flagged `is_estimated=true`** and a `source_note` naming that it needs
confirmation. Everywhere the number surfaces, the UI says «برآوردی». Confirming
it is one admin screen and zero code — exactly like the ۱۳۱ table before it was
researched. **This is an accountant question, added to the open-questions list.**

### 3.2 بیمه — two new `tax_parameters` keys

| key | 1404 seed | label |
|---|---|---|
| `insurance_employee_rate` | `0.07` | سهم بیمهٔ کارگر (۷٪) |
| `insurance_employer_rate` | `0.20` | سهم بیمهٔ کارفرما (۲۰٪) |
| `insurance_unemployment_rate` | `0.03` | بیمهٔ بیکاری (۳٪) |

Three keys, not one ۲۳٪ key, because the سپیدار export books ۲۰٪ and ۳٪ to two
different accounts and a merged rate could not reproduce it. Each carries its own
`source_note` and `is_estimated` flag, editable in the same admin screen that
already edits ماده ۱۰۱/۸۴/تبصره ۱۰۰/VAT. `PARAMETER_UNITS` = `fraction` for all
three, so the existing `validate_parameter` rejects anything > 1.

### 3.3 The insurance base (from §1.1)

```
insurance_base = حقوق پایه + بن/خواروبار/مسکن + حق تأهل + اضافه‌کاری + سایر مزایا
                 (حق اولاد EXCLUDED)
employee_share  = floor(insurance_base × insurance_employee_rate)
employer_share  = floor(insurance_base × insurance_employer_rate)
unemployment    = floor(insurance_base × insurance_unemployment_rate)
```

اضافه‌کاری and سایر مزایا are in the base because they are مزایای مستمر نقدی;
the سپیدار file had neither, so this is the standard rule rather than a
file-derived one — **flagged in the open questions.** حق اولاد's exclusion IS
file-derived and is stated as such in the UI hint.

> **بیمه ceiling (سقف دستمزد بیمه):** NOT implemented in v1. A ceiling exists in
> law and would need the yearly حداقل/حداکثر دستمزد figures, which we do not
> hold and will not invent. Open question; until answered the base is uncapped
> and the payslip says so in the accountant detail.

---

## 4. Data model

Three tables, `app/modules/payroll/`:

### `employees` — پرسنل
```
id, tenant_id
full_name                 required
national_id               required, 10-digit کد ملی, mod-11 — the CENTRAL validator
                          (app/common/identity.py / useIdentityField), never a local regex
insurance_number          optional, free digits
job_title                 optional
hire_date                 optional (Jalali in UI, ISO on the wire)
base_salary               Numeric(20,4) — monthly, ریال
allowance_bon             Numeric(20,4) default 0   ← fixed monthly, prefills the doc
allowance_marriage        Numeric(20,4) default 0
allowance_child           Numeric(20,4) default 0
allowance_other           Numeric(20,4) default 0
is_active                 bool default true
created_at / updated_at
UNIQUE (tenant_id, national_id) WHERE national_id IS NOT NULL
```
The four `allowance_*` columns are **defaults that prefill a monthly document**,
not the amounts themselves — raising someone's بن next month must not silently
rewrite last month's payslip.

### `payroll_runs` — سند حقوق ماهانه
```
id, tenant_id
jalali_year               String(4)   e.g. "1404"
jalali_month              int 1..12
period_start / period_end date — the Gregorian window the Jalali month maps to;
                          period_end is the document date for FY-lock and journal ordering
status                    'draft' | 'confirmed' | 'paid'
paid_from_account_id      FK treasury_accounts, NULL until paid
paid_at                   date, NULL until paid
tax_table_year            String(4) — WHICH ماده ۸۴ table produced these numbers
tax_is_estimated          bool      — snapshot of that table's «برآوردی» flag
note                      optional
UNIQUE (tenant_id, jalali_year, jalali_month)
```
`tax_table_year` + `tax_is_estimated` are **snapshotted at confirm**, not read
live: a payslip already handed to an employee must not silently change its tax
figure when the admin later edits the table. Same reasoning as the partner
commission accruals (Batch 3 Part 1).

### `payroll_items` — one row per person per run
```
id, tenant_id, run_id FK→payroll_runs ON DELETE CASCADE, employee_id FK→employees
employee_name_snapshot    denormalized (the payslip must reprint identically)
employee_national_id_snapshot
base_salary, allowance_bon, allowance_marriage, allowance_child,
  allowance_other, overtime                     ← earnings, all Numeric(20,4)
insurance_base                                  ← stored, not re-derived on read
insurance_employee, insurance_employer, insurance_unemployment
taxable_income, income_tax
other_deductions          Numeric(20,4) default 0, + `other_deductions_note`
gross_earnings, total_deductions, net_pay       ← stored
rates_snapshot            JSONB {employee, employer, unemployment, exemption_monthly,
                                 brackets:[...]} — the payslip's own audit trail
```

**Every computed figure is STORED, never recomputed on read.** A payslip is a
document handed to a person; recomputation on read is how a printed number and a
screen number drift apart. (The stale-`vat_amount` lesson from the income module,
inverted: there the fix was to always recompute *on write*, and that is exactly
what happens here — the run recomputes on every edit and stores the result.)

---

## 5. The voucher — ONE per person, the interim pattern

Generated by `generate_tenant_journal` like every other document (deterministic
replay, `source_type='payroll'`, priority slot after `income`), **one سند per
`payroll_item`** — per the founder's spec, and because a merged monthly voucher
would make «چقدر به این کارمند دادیم» unanswerable.

```
سند حقوق — <نام کارمند> — <ماه> <سال>

بدهکار                                    بستانکار
──────────────────────────────────────────────────────────────────────
5302  حقوق                    base        2104  بیمه پرداختنی    emp7% + er20% + un3%
5311  بن/خواروبار/مسکن        bon         2105  مالیات حقوق پرداختنی   income_tax
5312  حق تأهل                 marriage    2103/<employee>  خالص پرداختنی    net_pay
5313  حق اولاد                child       2103/<employee>  سایر کسورات      other_deductions
5314  اضافه‌کاری               overtime
5315  سایر مزایا              other
5316  بیمه سهم کارفرما        employer20
5317  بیمه بیکاری             unemployment
```

Balance proof:
```
Σ debit  = gross_earnings + employer20 + unemployment
Σ credit = (emp7 + employer20 + unemployment) + tax + net + other_deductions
         = employer20 + unemployment + emp7 + tax + other_deductions
           + (gross − emp7 − tax − other_deductions)
         = gross_earnings + employer20 + unemployment          ✓
```

Both `2103/<employee>` legs carry `party_type='employee'` + `party_id`, so the
employee's تفصیلی shows real **گردش** and its **مانده = what is still owed** —
the same «party ledger گردش» goal the expense/income interim legs serve, except
here the balance is *meant* to survive until payment (an employee genuinely is
owed money between confirm and pay). Zero-amount legs are omitted, so a merchant
with no اضافه‌کاری never sees an empty line.

**Mark-paid** emits a second, separate سند (`source_type='payroll_payment'`):
```
بدهکار  2103/<employee>   net_pay
بستانکار  <treasury تفصیلی>  net_pay
```
…which closes the employee's مانده to zero and drains the treasury account.

### 5.1 Money-movement wiring (the "silently lies" checklist)

`treasury.compute_account_balances()` is THE balance formula and its header says
any document that moves money and is missing from it is a balance that lies. A
paid payroll run therefore MUST be added to:

- `compute_account_balances()` — outflow of Σ`net_pay` per `paid_from_account_id`
- `reports.cash_flow()` — both the pre-window `start` seed AND the in-window
  movement rows (the درآمد bug taught that missing the seed makes every running
  balance below it wrong by the same amount)
- `reports.profit_loss()` — payroll cost is an **expense**: gross_earnings +
  employer23%. It is NOT in the `expenses` table, so the P/L must add it as its
  own addend. Per the «سایر درآمدها» defect (Batch 5), the addend also needs its
  own **wire field** on `ProfitLossResponse` and its own **export row**, with a
  test pinning every addend to the wire — a figure inside `profit` but absent
  from the visible rows is the exact bug that shipped last time.

---

## 6. Payslip PDF — فیش حقوقی

Rendered by the **existing** WeasyPrint path, not a new one. `pdf_service.py`
already embeds NotoNaskhArabic/DejaVu as data URIs and is the only place that
knows how to make Persian render inside the slim container; v1 extracts that
`_pdf_extra_css()` into a shared helper and reuses it verbatim.

- Persian, RTL, Jalali dates via `to_jalali` (the Batch 5 print fix — printed
  Gregorian dates were a shipped defect), brand «دیجی اینویس».
- Header: business name, «فیش حقوقی», ماه/سال Jalali, employee name + کد ملی +
  شمارهٔ بیمه.
- Two columns: **مزایا** (base, بن, تأهل, اولاد, اضافه‌کاری, سایر) and
  **کسورات** (بیمهٔ سهم کارگر ۷٪, مالیات حقوق, سایر کسورات).
- Footer: جمع مزایا / جمع کسورات / **خالص پرداختی** + عدد به حروف.
- «برآوردی» strip when `tax_is_estimated` — the payslip never presents an
  unconfirmed tax figure as settled.
- Employer share is shown in the **accountant detail only**, never on the
  employee's own فیش (it is not their money and printing it confuses people).

---

## 7. Report — گزارش حقوق ماهانه

One page, one month: per-person rows (نام، حقوق پایه، مزایا، بیمه، مالیات،
خالص) + a totals row, plus **بدهی به سازمان‌ها** (Σ2104, Σ2105 for the period).
XLSX export through the existing `export_xlsx` helper with `money_cols`.
Merchant reads نام/خالص/جمع; the bracket-by-bracket tax breakdown and the
employer-share columns sit behind the **accountant view** toggle, per the
standing «merchant Persian, accountant detail behind the accountant view» rule.

---

## 8. Gating

**v1 ships UNGATED**, alongside customers/products/purchases/expenses/incomes.

`LAUNCH_ROADMAP.md` lists «Payroll + insurance SKU» under **post-launch backlog**
— i.e. the *SKU* is post-launch while the *module* is building-now. Shipping a
paywall now would mean pricing, checkout wiring, module-request admin flow and a
`LockedFeatureCard` for a module whose price nobody has set. Adding `payroll` to
`core/plan.py FEATURES` later is a small, additive change.
**Founder decision wanted; ungated is the reversible default.**

---

## 9. Rules inherited (not re-litigated)

- **FY lock** — `assert_date_in_window(window, period_end, doc_label="تاریخ سند حقوق")`
  on create/edit/confirm, exactly like every other dated document.
- **Decimal-as-string** on the wire; never a float.
- **Persian→ASCII** digit normalization before validate/persist.
- **Jalali everywhere** in the UI; `JalaliDateField` for date inputs; native
  `<input type="date">` is a bug.
- **Live separators** on every amount input (raw while typing → format on blur →
  `normalizeDecimalInput` on submit).
- **Tenant isolation** on every query; delete paths guarded with rollback + a
  friendly Persian 409 rather than an FK 500 (gotcha 13 — the `FakeDBSession`
  harness bypasses these, so delete-with-children gets an *integration* test).
- **No success toast without a persisted call.**

---

## 10. ⚠️ OPEN — accountant questions (v1 ships honest, not guessed)

1. **جدول مالیات حقوق ۱۴۰۴ (ماده ۸۵)** — the exact steps. Ships seeded but
   `is_estimated=true` and labelled «برآوردی» until confirmed. §3.1
2. **سقف دستمزد بیمه** — is there a ceiling on the insurance base, and what is
   the ۱۴۰۴ figure? Uncapped in v1, stated in the accountant detail. §3.3
3. **اضافه‌کاری و سایر مزایا in the insurance base** — file-underived; standard
   rule applied. حق اولاد's exclusion IS file-proven. §3.3
4. **مزایای غیرنقدی / non-cash benefits** — out of v1 entirely.
5. **حق بیمهٔ سهم کارفرمای معاف** (کارگاه‌های مشمول معافیت) — not modelled.
6. **Payroll SKU** — ungated or paid? §8

Every one of these is a **stored parameter or an absent feature**, never a
hardcoded guess. That is the point.

---

## 11. Build order

1. design doc (this file) — committed before code ✅
2. backend: models + migration + chart accounts + params/table + calculator
3. backend: journal wiring + treasury/cashflow/P-L wiring + payslip PDF
4. backend: routes + pg tests (incl. delete-with-children)
5. frontend: personnel → monthly doc → payslip → mark-paid → report
6. guide + school touch
7. real-UI proof: one employee, one month, end-to-end
