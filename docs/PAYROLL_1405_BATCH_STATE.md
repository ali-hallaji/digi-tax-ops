# PAYROLL-1405 batch — state + resume plan

_Cut 2026-07-31 on the new desktop. Steps 0/1/2 SHIPPED (committed, gates green);
Parts 3/4 NOT STARTED — this doc is the resume contract so the next session
starts building, not re-deriving._

## Shipped (safe committed baseline)

| Piece | Commits | Proof |
|---|---|---|
| Enamad file at web root + landing audit | frontend `b4a71af` (deployed to dev) | `curl https://dev.digiinvoice.ir/15027996.txt` → 200 · text/plain · 0B |
| 1405 parameter engine (wage decree, ceiling formula, sourced ماده ۸۵, admin page) | backend `b2452e3` · frontend `805fa67` | 22 payroll tests; psql-verified columns; live OpenAPI shows `/admin/tax-parameters` |
| Insurance export DSKKAR00/DSKWOR00 | backend `bb3b1fb` · frontend `eb2ec79` | DBF round-trip tests; harness spec 17 (fail-path + real zip bytes) |

Migrations applied locally: `pay1405a001`, `pay1405a002` (psql-verified, not
just alembic). Seeds run locally: `seed_payroll_params_1405` (idempotent — MUST
be re-run on dev after deploy). Layout doc: `tamin_dbf_layout.md` (most fields
«تأییدنشده» pending the official لیست دیسک viewer check — that check GATES the
first real upload).

## ⛔ Founder-owned blockers surfaced by this batch

1. **Enamad apex**: digiinvoice.ir → 185.46.217.162 («Central Core Front»,
   cert only for central.digiinvoice.ir, no access from this workspace). The
   Enamad checker cannot succeed until the apex serves our stack.
2. **Landing Enamad prerequisites**: dead `#` footer links (قوانین/حریم
   خصوصی/تماس با ما/راهنما) and NO phone/email/address on the landing.
3. **Tamin field catalog**: obtain «دفترچهٔ راهنمای تهیهٔ لیست حق بیمه» (new
   ساختار آذر ۱۴۰۳) from samt.tamin.ir — flips the layout doc's تأییدنشده rows.

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
