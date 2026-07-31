# PAYROLL-1405 batch — state + resume plan

_Updated 2026-07-31 (second session). Step 0-APEX SHIPPED; Part 3 engine + a
latent voucher bug landed; Part 3 persistence/UI + Part 4 remain._

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

## Part 4 — ⬜ STILL NOT STARTED (97% rule, second stop) — spec unchanged below.


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
