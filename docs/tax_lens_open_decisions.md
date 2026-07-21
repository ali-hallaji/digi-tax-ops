# Tax-Lens — OPEN accountant decisions (built as structure, values «برآوردی»)

Per the standing rule (real accounting-/tax-semantics decisions go to the founder's
accountant, not engineering judgment), Tax-Lens v2 builds the **structure** and keeps
every number **«برآوردی»-flagged** (`is_estimated=True`) until confirmed. These are the
open questions the accountant's voice note should resolve. **No number below is presented
to a merchant as fact — each is either sourced (admin, `is_estimated=False` + `source_note`)
or shown as «برآوردی».**

## 1. View B — «نگاه سازمان» exact computation (OPEN)
v1 computes lens B as `coefficient × ALL net_sales` (the presumptive/ضرایب / علی‌الراس view).
The founder's framing — «اگر همهٔ فاکتورها به مودیان ارسال شود، تصویر سازمان به این عدد نزدیک
می‌شود» — implies the org's picture is driven by the **submitted-to-Moadian** sales, not all
sales. **v2 keeps v1's computation** (coefficient × all net_sales) as the presumptive figure,
and **separately surfaces the FACTUAL submitted-vs-unsent ratio** (real counts, not a tax
number) in the «چرا دو نگاه فرق دارند؟» explainer + the soft-guidance line. The exact formula
for "the tax the organization would assess from only the submitted data" is **NOT implemented**
— it needs the accountant's method (does the org apply ضرایب to submitted sales only? to the
full assessed turnover? how do non-reportable records net out?).

## 2. «طلب معوق» / receivable aging (OPEN — not computed)
There is **no due-date / aging model** on receivables (`Customer.total_receivable` is a live
denormalized balance; finalized invoices carry `issue_date` + `payment_status` but no due
date / payment term). So an "overdue طلب" figure **cannot be computed truthfully** and is NOT
shown. The dashboard cash+receivables lens surfaces only **real** signals: due-soon **cheques**
(which have real `due_date`s) + the total outstanding receivable. Real receivable aging needs
an invoice/customer payment-term + due-date model — a founder+accountant decision + new
modelling, logged as a follow-up.

## 3. ماده-۱۰۱ annual exemption (OPEN — unchanged from v1)
Not applied by the engine; representable as a leading 0%-rate bracket row in the admin-managed
`tax_tables` — a data decision, not code.

## 4. «برآوردی» → «تأییدشده» flip (structure shipped in v2)
Every seeded coefficient (`tax_activity_coefficients`) and every Article-131 table (`tax_tables`)
ships `is_estimated=True`. The admin flips a row to **«تأییدشده»** (`is_estimated=False`) only
when they enter an officially-sourced value together with a `source_note` citation. The merchant
two-view screen shows a calm «برآوردی» chip while `is_estimated=True`, and the source citation
once confirmed.
