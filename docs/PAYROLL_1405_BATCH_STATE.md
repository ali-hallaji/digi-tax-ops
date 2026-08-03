# PAYROLL-1405 batch — state + resume plan

_Updated 2026-08-04. **The batch is complete**: overtime-from-hours, مأموریت,
وام و مساعده, and the two-column تسویه‌حساب have all shipped. Nothing is banked._

## PAYROLL v2.1 (2026-08-03) — what shipped

| Piece | Commits | State |
|---|---|---|
| اضافه‌کار from HOURS (ماده ۵۹) + per-business «مبنای ساعت ماهانه» | backend `b3c5213` · frontend `4ad99a7` | DONE — migration **`pay1405a004`** |
| ردیف مأموریت, outside insurance AND tax (two admin toggles) | same | DONE — معین **5323** «فوق‌العادهٔ مأموریت» |
| Eval data on 09120000000 (مرداد paid w/ hours+mission, شهریور editable draft) | ops `c141e3f` | DONE — `scripts/enrich_dibatak_payroll.py` |

**Deploy steps for this migration:** `alembic upgrade head` (pay1405a004) THEN
`python -m app.cli.seed_payroll_params_1405` — without `overtime_multiplier`
اضافه‌کار computes as ZERO (deliberate: an unsourced wage number does not ship).

**The formula, once, so it is never re-derived:**
اضافه‌کار = (حقوق پایه + پایهٔ سنوات) ÷ D × ضریب × ساعت, ROUND_DOWN.
· ضریب = `overtime_multiplier` tax parameter (1.4, sourced to ماده ۵۹). Unseeded ⇒ ZERO.
· D = `tenants.payroll_monthly_hours_basis`. NULL ⇒ 219.9 flagged `is_estimated`
  («رویهٔ رایج — پیشنهاد حسابدار»); UI offers 219.9 / 220 / 192 / custom.
· A typed AMOUNT still works but sets `overtime_is_override` and renders as
  «اضافه‌کار دستی» — the payslip never lets a hand-typed figure look derived.
· اضافه‌کار stays INSIDE both bases; مأموریت stays OUTSIDE both (pinned).
· DSKWOR `DSW_MASH` is the stored `insurance_base`, so the بیمه file and the
  payslip cannot drift: overtime in, mission out (pinned in `test_payroll_pg`).

**Accountant questions raised (both shipped as `is_estimated=True` toggles):**
`mission_insurance_free` (ماده ۳۰ ق.ت.ا؟) and `mission_tax_free` (بند ۳ ماده ۹۱
ق.م.م؟) — the research doc quotes neither article's text, so both are visible
admin switches rather than buried defaults.

## PAYROLL v2.1 — items 4 + 5 SHIPPED (2026-08-04)

| Piece | Commits | State |
|---|---|---|
| وام و مساعده as a REAL receivable (grant voucher, installments, early settle, void) | backend `04e831f`+`5358d7c` · frontend `f13a966` | DONE — migration **`pay1405a005`** |
| تسویه‌حساب v2, the accountant's two columns | same | DONE — engine EXTENDED, not rebuilt |
| Eval data: two loans running, one settlement closing a balance | ops `3d57958` | DONE |

**The accounting, once:**
```
grant        بدهکار 1202/<کارمند>        بستانکار خزانه
قسط (payslip) بدهکار — (withheld)        بستانکار 1202/<کارمند>
early settle  بدهکار خزانه               بستانکار 1202/<کارمند>
settlement    … افزودنی‌ها …             بستانکار 1202/<کارمند> (مانده) + 2104 + 2105
                                          + 2101 (سایر کسورات) + 2103/<کارمند> (خالص)
```
معین **1202 «وام و مساعدهٔ کارکنان»** is in `_SKELETON`, so `ensure_chart`
creates it for EXISTING tenants too — the settlement lesson, applied.

**Guards that carry it (all pinned in `test_loans_pg.py`):**
· repayment rows are UNIQUE per (loan, run) — a run recomputes on every edit
· the installment clamps twice: never > the installment, never > what is owed
· a repaid loan deducts NOTHING (no negative receivable)
· deleting a run returns its installment to the balance
· the installment credits the RECEIVABLE, never the payable leaf
· voiding a settlement re-opens the loan it closed
· an employee with a live loan cannot be deleted (friendly 409, not an FK 500)

**Bug found and fixed mid-batch (`5358d7c`):** `active_loans_for_employee`
filtered on `status == "active"`. An early settlement flipped the loan to
«settled», the open draft then recomputed, found no active loan and DELETED the
installment it had already withheld — the employee paid the lot and still owed
one installment. **Status is a derived LABEL; the balance is the truth.** Pinned.

**Known divergence, documented in the merchant guide:** «مانده» on the employee
card counts the installment reserved by an OPEN DRAFT; the دفاتر only count
confirmed documents. Confirming the run makes them agree. Not a bug — a draft
is a working copy — but it is visible, so it is written down.

**Accountant question raised:** the settlement's «سایر کسورات» free rows credit
**2101 حساب‌های پرداختنی** (withheld and owed onward). Crediting the employee's
own leaf would leave it non-zero after the payment closes only the net, which
breaks the zero-leaf identity. Where each free row really belongs is per-case —
worth confirming.

**Deploy:** `alembic upgrade head` (pay1405a005). No new seed step.

## PAYROLL v2.1 — the DEFERRED list, now closed

3. **وام و مساعده registry** — ✅ SHIPPED 2026-08-04 (see above). Original note: Today's workaround is
   «سایر کسورات» with a «بابت» note (the row editor's placeholder literally says
   «مثلاً قسط وام»), which deducts correctly but tracks no balance.
   Accounting note for whoever builds it: the installment's CREDIT leg belongs
   on a «وام و مساعده کارکنان» receivable, which means the GRANT has to be
   booked too — otherwise the asset goes negative. That is the part that makes
   this bigger than a deduction field.
4. **Settlement v2 two-column** — ✅ SHIPPED 2026-08-04 (see above).

## Earlier state (kept for reference)

## NEW since the first cut

| Piece | Commits | State |
|---|---|---|
| Apex landing bundle + 4 real footer pages (قوانین/حریم/تماس/راهنما) | frontend `bc5fdba` · ops `f756a90` | DONE — dev serves all 4 + txt (curl-proven); zip `dist/landing_apex_2026-07-31.zip` + `docs/apex_landing_deploy_note.md`; contact values are placeholders → founder fills `digi-tax-frontend/src/lib/landing-pages.json` keys `contact.phone/email/postalAddress` (lines 3–5) |
| Voucher bug: حق مسکن/پایهٔ سنوات missing from PAYROLL_COMPONENTS → unbalanced سند on confirm | backend `8624822` | FIXED (5318/5319), pg-pinned |
| Settlement ENGINE (pure calc + 8 worked-example tests) | backend `84eb13e` | DONE — `app/modules/payroll/application/settlement.py` |

## Part 3 — REMAINING (build in this order)

1. Migration `pay1405a003` — `employee_settlements` exactly per the banked design
   below (unchanged).
2. Service: quote (GET preview from engine + `resolve_wage_decree` +
   `load_active_tax_table_meta(kind="article_84")`; hourly basis = 90-day avg
   from payroll_items) → create(draft) → pay(treasury account; like
   set_run_status "paid") → void (standard). employee.is_active=False on pay.
3. Journal: mirror the payroll block in
   `app/modules/accounting/application/journal.py` (~line 780) for settlements:
   debit new components سنوات پایان کار/عیدی/بازخرید مرخصی (add to
   PAYROLL_COMPONENTS: e.g. 5320/5321/5322), credit 2103/<کارمند> net + 2105
   tax; pay leg closes 2103 from the treasury account. Balanced-voucher pg test
   like `test_voucher_balances_with_housing_and_seniority`.
4. PDF: variant of `payslip.py` renderer titled «تسویه‌حساب».
5. Routes + contract entries (PAY-1405 section).
6. UI wizard (employee row action در تب پرسنل): date+reason → leave days +
   breakdown → account → paid; PDF button; guide walkthrough SAME commit.
7. Harness settlement spec (persona p2's employee — after spec 17 they have
   insurance numbers; end assert: employee inactive + zero balance).

## Part 3 — ✅ SHIPPED (2026-08-01 session)

Backend `bfca97b`+`e78106c`+`fb8d6c5`, frontend (wizard+spec18): migration
pay1405a003 · engine+service+routes+journal (5320/5321/5322; leaf==0 pg-proven)
· برگهٔ تسویه PDF (ASCII filename — Persian in Content-Disposition 500s) ·
wizard 3 steps + guide · harness spec 18 (self-resetting via void). UI walk
green local (رضا کارگر: سنوات 772,853,698 + عیدی 42,360,990 + بازخرید
155,380,624 − مالیات 0 = خالص 970,595,312 ریال; leaf zero; inactive).
Grill catches: chart sync for settlement-only tenants; wizard تومان/ریال
label; PDF header unicode. Accountant Qs unchanged (3 toggles + عیدی-excess).

## Part 4 — ✅ SHIPPED (2026-08-01) — THE BATCH IS COMPLETE

Backend `65ea1c7` · frontend `1e3780d`: payroll_economy/growth/advanced in the
STANDARD machinery (FEATURES + module_prices + history + partner credit +
trial — zero new systems). `payroll_tier_enforced` flag DEFAULT OFF (mirror of
document_cap_enforced; production flip = founder). Flag ON gates: headcount
۵/۲۰/نامحدود · insurance-export رشد+ · تسویه‌حساب پیشرفته; non-purchasers keep
basic payroll at economy limits (founder-tunable reading, recorded here).
`seed_payroll_sku` seeds monthly-rial equivalents of the banked ANNUAL anchors
(1.8M/3.6M/6.5M toman → 1,500,000/3,000,000/5,416,666 ﷼/ماه ROUND_DOWN),
notes «پیشنهاد اولیه — تأیید نهایی مؤسس pending» + research §5-2 citation —
run it on deploy. Marketplace cards + admin editor render from the registry;
spec 18 asserts flag-OFF access + the three cards on sale.


## Part 3 — تسویه‌حساب (NOT started; design decisions BANKED — build these)

- **Table** `employee_settlements` (migration `pay1405a003`): tenant_id,
  employee_id, termination_date, reason (resignation|dismissal|contract_end),
  computed rial columns (severance, eydi, leave_days, leave_buyback, tax,
  net_payable), `params_snapshot` JSONB (rules + تأییدنشده flags), status
  draft|paid|voided, paid_from_account_id/paid_at, journal linkage like payroll.
- **Engine** (pure, like calculator.py): سنوات = آخرین حقوق پایهٔ ماهانه ×
  (سال‌های کامل + روزهای ناقص/365)؛ مبنای ساعتی/موقت = میانگین ۹۰ روز آخر (از
  payroll_items). عیدی سالانه = min(2×حقوق خود شخص، eydi_cap_multiplier×
  min_wage_monthly) × (روزهای کارکرد سال/365) — قانون ۱۳۷۰ («۶۰ روز آخرین مزد،
  سقف ۹۰ روز حداقل») همین است؛ در snapshot ثبت شود. بازخرید مرخصی = روزهای
  واردشدهٔ ویزارد (سقف annual_leave_days + 9×سال‌ها، با hint ماده ۶۶) ×
  (جمع دریافتی ماهانه ÷ ۳۰). مالیات: سنوات/بازخرید per toggles (تأییدنشده)؛
  عیدی معاف تا exemption/12، مازاد progressive از صفر روی جدول ماده ۸۵ —
  **این تفسیر ماست، در snapshot + doc ثبت و برای حسابدار پرسش شود.**
  بیمهٔ اقلام تسویه: صفر per toggle. همه ROUND_DOWN.
- **Flow**: employee page → «تسویه‌حساب» wizard (date+reason → leave days +
  breakdown review → payment account) → settlement payslip PDF (merchant
  Persian «تسویه‌حساب», reuse payslip renderer) → balanced voucher via the SAME
  path payroll-run confirm uses (read services voucher code first!) → treasury
  payment → employee is_active=false → **prove rial-for-rial zero balance in a
  real UI walk on a persona employee**. Reversible ONLY via standard void.
- Params already seeded (Part 1): eydi_min/cap, annual_leave_days,
  leave_carryover_cap_days, 3 toggles — the wizard READS, never hardcodes.
- Harness: one settlement spec (mandated).

## Part 4 — SKU gating (NOT started; seeds specified)

«حقوق و دستمزد کامل» in the existing module marketplace/entitlements machinery
(same as other SKUs; `module_prices` + history + partner credit + admin trial
policy). Tiers اقتصادی/رشد/پیشرفته, INITIAL annual prices (source_note:
«پیشنهاد اولیه — تأیید نهایی مؤسس pending») = 1,800,000 / 3,600,000 / 6,500,000
toman; limits = تا ۵ پرسنل / تا ۲۰ + insurance-export / نامحدود + تسویه‌حساب +
دیسکت مالیات. Enforcement flag **default OFF on dev** (mirror DOCUMENT_CAP
policy); production gating = founder flip. Payroll stays fully active for all
existing personas.

## Machine notes (new desktop)

- Docker builds need `--network=host` + `--build-arg HTTP(S)_PROXY=
  http://127.0.0.1:2080`: nekobox listens on 127.0.0.1 ONLY, so the
  `~/.docker/config.json` proxy (172.17.0.1:2080) is dead for builds. Fix
  permanently: enable «Allow LAN» in nekobox, or run builds with the flags.
- `sg docker -c "…"` needed until the founder re-logs-in (docker group).
- `~/.zshenv` restored to autoload `.deploy.env` (was missing post-migration).
- Repo-local git identity set in each repo (matches history); global unset.
