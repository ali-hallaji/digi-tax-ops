# RESUME NOTE — Phase-1 Closure Batch (tester-unblock window)

_Written 2026-07-21. Read this + workspace CLAUDE.md §2/§4.6 before continuing._

## What is DONE + COMMITTED-LOCAL (this window) — NOT deployed
- **Prior batches DEPLOYED to dev** first (founder GO): Tax-Lens v2 + Accountant-Pack v2.
  Verified: api `cae9657` + frontend `a52a6b7`, alembic `tlv2est00007`, `is_estimated`
  columns present, new routes on live OpenAPI, **harness 9/9 dev** + Playwright view-only
  pass (shots `digi-tax-frontend/qa-screens/harness-tlv2verify/`).
- **Part 1 — DEV login OTP hint** (backend `6909e5d`, frontend `f775e52`). New
  `DEV_LOGIN_OTP_HINT` env flag (default off, dev-only, NEVER prod), independent of
  `debug`. `OTPRequestResponse.otp_hint` set ONLY when the flag is on AND the account
  passes the HARD GUARD in `identity/application/services.py::dev_login_otp_hint_for`
  (never `09120000000`, never any `is_system_admin`, only persisted accounts). Login page
  renders «کد ورود (محیط آزمایشی): …» (--info token). 5 guard tests green; suite baseline
  unchanged (3 known FakeDBSession auto-tenant fails only).
- **Part 3 — dashboard discovery card + plans** (frontend `34bda84`). Dismissible
  «امکانات بیشتر می‌خواهید؟» → /app/plans, hidden once all entitlements enabled
  (`usePlan`, no new endpoint); standalone-Moadian badge on plans page. Existing
  module copy was already good.
- **Part 4 — guides** (frontend `f6113d9`). Walkthrough sweep + new «پلن‌ها و ماژول‌های
  پولی» section at `/app/guide/plans`. no-drift 42/42, typecheck 0, build green.

Frontend combined typecheck 0 + build green across all three tracks.

## WIP ON DISK (uncommitted) — Parts 2 + 7 seed, code-done, NOT verified/committed
`digi-tax-backend/app/cli/seed_realistic_world.py` carries:
- **Part 2 (single admin):** `seed()` sets `ADMIN_MOBILE` (09120000001) `is_system_admin=False`
  (demoted); founder دیباتک (`build_dibatak`) stays the SOLE system_admin. Comments +
  summary-print updated.
- **Part 7 (demo user):** `build_demo(db, admin)` (+ helpers `_demo_sales`/`_demo_drafts`)
  appended after `build_dibatak`, wired into `seed()` after دیباتک, with a manual opening
  entry + summary print line + docstring row. Persona `09120009000` «کاربر نمونه» /
  «دیجی‌تکس نمونه» (legal), ALL modules granted (base/accountant/expense_breakdown_report/
  inventory_lite/team_members/moadian_submission/tax_lens; perpetual), taxpayer APPROVED,
  Moadian profile `environment=sandbox` with **NO key material**. Rich data over FY1404+1405:
  12 customers, 12 products, 20 finalized invoices (8×1404 / 12×1405) + 3 drafts, 4 purchases,
  4 cheques (lifecycle), 2 returns, 8 expenses, 22 payments, 3 treasury accounts. ruff/black/
  parse green. (1404 data is دی–اسفند only — `_d()` maps to Greg-2026; widen with raw
  `date(2025,…)` if a fuller 1404 curve is wanted.)

## REMAINING to finish Parts 2 + 7 and deploy the window
0. **KEY FINDING:** world_fixtures.py ALREADY has a `dibatak` persona (`09120000000`,
   «علی حلاجی», role "system_admin + partner + merchant") at line ~411 whose `see` says it
   lands on `/admin` via admin-precedence. So the harness admin fix = **point spec 05 at
   `PERSONAS.dibatak`**, not a rewrite of the `admin` entry.
1. **world_fixtures.py** — the harness/docs single source:
   - **`admin` persona (09120000001, line ~60):** demote it — role → e.g. "partner + regular"
     (no longer system_admin), businesses stay []. MOVE its `expected.dashboard_counts` +
     `tax_calendar_override` to the `dibatak` persona (they describe the ADMIN view, and دیباتک
     is now the sole admin). Update its `explore`/`see` (partner HAM-ADMIN only; no admin panel).
   - **`dibatak` persona (line ~411):** add `expected.dashboard_counts` (**users 18→19,
     tenants 13→14** — demo +1/+1; pending reviews stay 2, partners_active 5, partners_pending 1,
     module_requests_pending 1, credit_activations_pending 1) + the `tax_calendar_override` block.
   - Add a `demo` persona entry (`09120009000`, «کاربر نمونه» / «دیجی‌تکس نمونه») with a
     modest `see`/`expected` (don't over-assert). Add its `PERSON_TYPE` row (حقوقی, line ~28).
2. **harness spec 05** (`tests/e2e-harness/specs/05-p5-admin.spec.ts`) — **BLOCKER (founder-
   ack'd):** its T1b block asserts «شما مدیر سیستم هستید» + «می‌خواهم کسب‌وکار شخصی بسازم»
   on `/app`. دیباتک is admin **+ merchant**, so `/app` shows the merchant dashboard.
   **Rewrite:** `const ADMIN = PERSONAS.dibatak`; keep /admin-landing + counts(19) + tax-calendar
   + password-reset(P3) + module-activation(P1); **DROP the bare-admin `/app` role-card block
   with a comment** noting that code path is now persona-untested (single-admin rule wins —
   founder decision). Confirm دیباتک lands on /admin on a cold context (admin precedence).
3. **Regenerate** `docs/persona_fixtures.json` + `docs/persona_logins.md` + README «🔑 ورود
   به دنیای دمو» from world_fixtures (do NOT hand-edit) — see world_fixtures.py header. Add
   the founder-approved persona-table amendments (single-admin demotion note + demo login).
4. **RESEED verification (destructive — care):** local reseed is BLOCKED (نیک‌تجارت real key
   locally). On dev, only دیباتک holds a real key (auto-preserved by reset_world.sh); VERIFY
   no other tenant has a real key BEFORE wiping (`--force` would destroy keys — do NOT use it).
   Take the pre-reseed snapshot. Reseed → verify_world → `python -m app.cli.world_fixtures`
   regen → psql spot-check counts (19 users / 14 tenants; demo entitlements present).
5. **Gates + deploy (ONE guarded window, founder GO):** pytest isolated (run_tests.sh) +
   ruff+black; pnpm typecheck+build; guide no-drift. Push all repos. Deploy compose v2,
   `--no-cache` api+frontend, reseed dev, **set `DEV_LOGIN_OTP_HINT=true` on dev only**
   (env in ops `.env`/compose — dev, never prod). Deploy-verification (SHAs + heads).
   **harness 9/9 dev** + the **mobile build-up journey** (390px: login-with-OTP-hint →
   dashboard guide card → plans → activate a module via sim-checkout → feature unlocks →
   guide section; screenshots each step). Print the demo phone `09120009000` + what to tell
   accountants.

## Then: Parts 5 + 6 (admin + partner panel deep polish) — the NEXT window (Opus-level UI).
