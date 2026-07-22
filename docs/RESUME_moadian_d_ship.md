# RESUME — MOADIAN D ship sequence (stopped mid-deploy 2026-07-22 ~11:00)

Founder stopped the turn mid-ship. Everything is committed; the dev deploy is
HALF-PREPARED (safe state — old code still serving). Pick up at «Remaining» below.

## What is DONE and PUSHED (all three repos, origin/main)

- **backend `c358002`** (3 commits: `61f7596` serial fix · `74e3235` excel caps ·
  `c358002` fiscal-status + bulk refresh):
  - `_next_inno` seeds NEW fiscal memories at epoch-seconds (org 0100504 fix);
    migration **`mdser00009`** (NEW HEAD) bumps counters < 1e9, idempotent;
    `_guard_serial` pre-submit block on `^[a-fA-F0-9]{10}$`; `_buyer_tinb`
    11-digit resolution (legacy 12-digit → buyer's شناسه ملی) + validator warning
    `buyer_economic_id_legacy_12`; buyer snapshot overrides now resolved BEFORE
    the packet buyer dict (they previously never reached bid/tinb).
  - Excel: `MAX_EXCEL_IMPORT_ROWS`/`MAX_EXCEL_IMPORT_MB` env caps + Persian cap
    errors + `GET /invoice-drafts/import-excel/limits`.
  - `GET /moadian/profile/fiscal-status` (read-only cockpit card) +
    `POST /admin/moadian/submissions/refresh-pending` (bulk استعلام, newest 50).
  - Tests: **1167 pass / 7 known baseline / 4 skip** on isolated digitax_test;
    ruff+black clean. Contract entries added (MOADIAN B Excel updated + new
    MOADIAN D section).
- **frontend `ac998f6`** (3 commits: `0850f60` amber economic hint · `99548b8`
  import dialog caps/per-type samples/XHR progress · `ac998f6` cockpit fiscal
  card + bulk-refresh button). typecheck 0, build green, unit **fail 0**
  (notice tests added). Per-type samples versioned in `public/samples/`
  (`…-type1.xlsx` / `…-type2.xlsx`; combined kept). Guide copy updated in-commit.
- **ops `1f2e3a6`** (3 commits incl. PART 0 proof doc, egress-pin/tunnel runbook
  §, org services map + honest boundary, pattern assessment (build-0),
  monetization assessment). CLAUDE.md §7.5 updated (workspace root, not a repo).

## Local machine state (verified green before the stop)

- Local world RESEEDED (fixtures-true again). دیباتک's Moadian key preserved by
  the script; نیک‌تجارت's local key (A11111 — local test identity) manually
  preserved via a holding schema and restored — both keys verified present.
  Pre-reseed snapshot: `digi-tax-ops/.reseed-snapshots/digitax-pre-reseed-14050431-135729.sql.gz`.
- Local migration applied (head `mdser00009`); local counters unchanged (both epoch).
- **Local harness 9/9.** Playwright QA PASSED: customer-form amber hint
  (desktop+390), buyer-card amber hint (پارس legacy code, desktop+390), import
  dialog caps line «حداکثر ۲۰۰۰ ردیف و ۵ مگابایت» + per-type sample switch +
  all three samples 200. Shots: `qa-screens/md-d/*.png` (workspace root).
- Local api container rebuilt and running the new code. A leftover QA draft
  invoice «آزمایش کارت خریدار…» + customer «شرکت آزمایش امبر» exist on
  ترازپیشه دیبا/نیک‌تجارت locally (harmless; reseed clears).

## DEV state (samad) — deploy HALF-PREPARED, old code still serving

- Snapshot taken: `backups/digitax-pre-md-d-20260722-1053.sql.gz` (128 MB).
- All three repos PULLED to the SHAs above; `docker compose config` OK.
- **api image BUILT (`--no-cache`) but container NOT recreated** — still running
  the pre-D image. Frontend NOT built. Migration NOT applied (dev head still
  `acraud00008`).
- **PRE-migration counter proof captured** (for the دیباتک-untouched check):
  `A2HP31|1784709096` · `A41XRD|1784564819` — both ≥1e9, so mdser00009 must be
  a no-op on BOTH; verify byte-identical after upgrade.
- PART 0 state still live on dev: sandbox pin on the egress host, نیک‌تجارت
  sandbox connection approved, 6 sandbox submissions (1 rejected + 5 accepted).
  Tunnel: manual autossh (not reboot-persistent).

## REMAINING ship sequence (in order, next window)

1. `docker compose up -d api` (recreates onto the already-built image) →
   `docker compose build --no-cache frontend && docker compose up -d frontend`.
2. `docker compose exec api alembic upgrade head` → expect `mdser00009 (head)`.
3. **POST-migration psql proof**: counters byte-identical to the PRE values above.
4. Verify live OpenAPI shows the new routes (`/moadian/profile/fiscal-status`,
   `/admin/moadian/submissions/refresh-pending`, `/invoice-drafts/import-excel/limits`).
5. Dev harness: `pnpm harness --base-url https://dev.digiinvoice.ir` → 9/9.
6. **STEP A.4 sandbox re-proof**: one fresh اصلی on نیک‌تجارت through the
   DEPLOYED code — accepted, serial 10-digit, and the submission's tinb resolved
   to 11-digit (create a fresh tax_reportable invoice; the two PART 0 chain
   invoices are already consumed by lifecycle rules).
7. Captcha/rate-limit state check (must stay ON) + Playwright spot-check of the
   import dialog + amber hint on dev.
8. Final progress.md entry (this batch has NO progress entry yet — only PART 0's)
   + phase_roadmap touch + founder report (headline: serial fix proven, amber
   shots, excel demo, services table, pattern/monetization doc paths, SHAs).

## Notes / observations for the next session

- Pre-existing (NOT from this batch): admin-token users hitting `/app/moadian`
  get 422 retries on `/admin/moadian/submissions` (require_moadian_read_access
  returns None for system_admin) — SubmissionsCard hides; merchant tokens fine.
  Candidate small fix later.
- The local reseed proved fixtures users=19 matches; reseed output prints «۱۸
  کاربر» for the admin dashboard while fixture says 19 — harness passed, so the
  fixture is the truth; ignore the seed's console phrasing.
- `tax_units` is empty everywhere (unit check advisory-skip) — unchanged.
