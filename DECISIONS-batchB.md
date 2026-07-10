# Batch B «لایهٔ طلایی» — Decisions Log (autonomous overnight run, 2026-07-10)

Model: **Opus 4.8 (1M context)** — confirmed, correct for this batch.

Decisions taken beyond the locked prompt (conservative-by-default, per the
"unlocked decision" rule). Newest first within each area.

## Architecture

### D1 — Journal generation is DERIVE-ON-DEMAND (replay), not write-hooked
The prompt anticipates optional in-transaction generation ("generate inside the
same transaction where cheap"). I chose the **conservative** path: journal is a
pure, deterministic, idempotent **replay of existing rows** — never coupled to
merchant write paths.
- Triggered by: (a) toggle turning ON, (b) the backfill migration, (c) an
  explicit `POST /accounting/regenerate` (owner + toggle gated).
- Read endpoints serve the persisted journal; they do NOT auto-regenerate
  (predictable, cheap reads). The accountant refreshes via regenerate.
- **Why:** (1) generation is already deterministic+idempotent from existing rows
  (Part-E design), so on-demand full regen is identical to incremental; (2) it
  touches ZERO merchant services → the 747-test baseline and the pixel-parity
  requirement are structurally safe; (3) "no merchant flow may fail because of
  journal generation" is trivially true — merchant flows never call it.
- **Trade-off:** with the toggle ON the journal reflects state as of the last
  regenerate, not live. Mitigation: regenerate on toggle-ON and expose an
  explicit refresh. A live dirty-flag refresh is a documented future
  enhancement. At current data sizes a full regen is sub-millisecond.

### D2 — `entry_no` is deterministic → idempotency holds
Per-tenant sequential integer assigned in a fixed event order:
`(event_date ASC, source_type priority ASC, source_id ASC)`. Same inputs →
identical entry_no every regen. `UNIQUE(tenant_id, source_type, source_id)`
guards against duplicates within a generation.

## Chart of accounts (D3 — structure + codes)

4 levels: گروه(1) → کل(2) → معین(3) → تفصیلی(4). Codes: group 1 digit, کل
group+1, معین کل+2, تفصیلی معین+4 (sequential per parent). Seeded group/کل/معین
are `is_system=true`; تفصیلی is auto-created (`is_system=false`, entity-linked
via `entity_type`+`entity_id`).

```
1 دارایی‌ها (asset)
  11 موجودی نقد و بانک
     1101 صندوق        → تفصیلی per cash_box treasury account
     1102 بانک         → تفصیلی per bank treasury account
     1103 تنخواه       → تفصیلی per petty_cash treasury account
  12 حساب‌های دریافتنی
     1201 حساب‌های دریافتنی → تفصیلی per customer
  13 اسناد دریافتنی
     1301 اسناد دریافتنی  (معین; lines carry customer party ref, no تفصیلی)
  14 پیش‌پرداخت‌ها
     1401 پیش‌پرداخت‌ها   → تفصیلی per vendor
2 بدهی‌ها (liability)
  21 حساب‌های پرداختنی
     2101 حساب‌های پرداختنی → تفصیلی per vendor
  22 اسناد پرداختنی
     2201 اسناد پرداختنی  (معین; lines carry vendor party ref)
  23 پیش‌دریافت‌ها
     2301 پیش‌دریافت‌ها   → تفصیلی per customer
  24 مالیات ارزش افزوده
     2401 مالیات ارزش افزوده دریافتی
     2402 مالیات ارزش افزوده پرداختی   (naturally carries a debit balance)
3 سرمایه (equity)
  31 سرمایه
     3101 سرمایهٔ اولیه   (opening balances balance here)
4 درآمد (income)
  41 فروش
     4101 فروش
  42 برگشت از فروش (contra-income; carries debit)
     4201 برگشت از فروش
5 هزینه (expense)
  51 خرید
     5101 خرید
  52 برگشت از خرید (contra-expense; carries credit)
     5201 برگشت از خرید
  53 هزینه‌ها
     53NN معین per expense category (auto-created; default slugs seeded,
          custom categories added lazily)
9 حساب‌های موقت (kind=equity, neutral)
  91 موقت
     9101 در انتظار بررسی (suspense — unmappable events land here + journal_gaps)
```

### D4 — Opening balances for parties are journaled (required by reconciliation)
The prompt's opening-balance mapping names only treasury accounts, but the
reconciliation invariant needs customer/vendor opening balances in the ledger.
Conservative, symmetric mapping:
- Customer opening (they owe us): بدهکار حساب‌های دریافتنی مشتری / بستانکار سرمایهٔ اولیه.
- Vendor opening (we owe them): بدهکار سرمایهٔ اولیه / بستانکار حساب‌های پرداختنی تأمین‌کننده.

### D5 — Cheque-derived payments are journaled via the CHEQUE event, not the payment
Clearing (وصول/پاس) and خرج چک each create Payment rows carrying `cheque_id`.
Those rows are SKIPPED in the payment-settlement journaling loop and journaled by
the cheque event instead — avoids double-counting. Treasury `current_balance`
counts the clearing payment (account_id set), and the cheque-وصول سند posts the
same بدهکار بانک amount → موجودی نقد ledger == treasury balance.

### D6 — Party refs on journal_lines enable per-party reconciliation
اسناد دریافتنی/پرداختنی are معین-level (not per-party accounts), but their lines
carry `party_type`+`party_id`, so reconciliation sums lines per party across
{حساب‌های دریافتنی, اسناد دریافتنی} == merchant طلب (and mirrored for vendors).
This matches the merchant model where a received cheque does NOT reduce طلب until
وصول (registration moves حساب‌های دریافتنی → اسناد دریافتنی, sum unchanged).

_(more decisions appended as the batch proceeds)_

### D7 — Returns are VAT-split in the journal (more correct than A15's report)
ReturnDocument carries `vat_amount`, so the return سند reverses the VAT
(بدهکار/بستانکار مالیات …) alongside برگشت از فروش/خرید, keeping the VAT accounts
accurate. This is stricter than the A15 P/L report (which kept returns
VAT-inclusive) but does not contradict it — the نیک‌تجارت returns are VAT-free.

### D8 — نیک‌تجارت invariant fixture inserts canonical rows directly
The prompt says "replayed via API"; I insert canonical financial rows directly
(matching the shapes the merchant services produce) rather than driving the full
HTTP API. Rationale: the invariant under test is the JOURNAL ENGINE's correctness
given the data — direct inserts isolate it, are far more robust, and avoid
coupling the test to service-request internals. Runs against real Postgres;
skips cleanly when no DB (keeps the standard `docker run` suite at 747/7).

### D9 — Backfill is a CLI, not an async-in-alembic migration
`python -m app.cli.backfill_journals` (idempotent) regenerates every tenant's
journal, run as an explicit deploy step after `alembic upgrade head`. Reason:
running async generation inside a sync alembic migration (which already holds a
live transaction) risks deadlock/uncommitted-read from a second engine. Also,
since toggle-ON already generates per-tenant lazily and read endpoints require
the toggle, no mass backfill is strictly needed for correctness — the CLI exists
for completeness + the deploy verification counts.

## Frontend

### D10 — Pixel-parity proof is STRUCTURAL, not screenshot-driven (browser rule wins)
The B-7 spec asks for a headless screenshot sweep as pixel-parity proof. Both the
workspace and frontend CLAUDE.md carry a hard rule: **Claude Code must NOT drive the
browser** (no Playwright-MCP click/login/screenshot) — verification is the founder's job.
Conservative resolution: I do NOT drive the browser. Instead, pixel-parity with the toggle
OFF is guaranteed **by construction** and stated as such:
- `ViewEntryLink` returns `null` when `useAccountantView()` is false → zero DOM on every
  merchant surface (invoice/payment/cheque/expense) with the toggle off.
- The sidebar «نمای حسابدار» group is only appended when `accountantView && seesAll`.
- The settings `AccountantViewCard` is purely **additive** (a new card), changing no
  existing card.
- Backend read endpoints 403 when the toggle is off; nothing renders.
- The toggle defaults OFF; a fresh/unchanged business is byte-identical to pre-Batch-B.
**Consequence for Mission 3 gate:** the "pixel-parity screenshots" gate cannot be
self-certified by me. Mission 3 (deploy) therefore stays BLOCKED pending the founder's
manual screenshot verification (incognito · 390px + desktop · light + dark · toggle OFF
then ON). Everything Mission-2 is committed locally; nothing is pushed.

### D11 — Accountant sidebar/label vocabulary aligned to page titles + school
The sidebar journal item was initially «اسناد حسابداری» but the page title and school
lesson L20 both teach «دفتر روزنامه». Renamed the sidebar item to «دفتر روزنامه» so the
guide (which names exact labels), the page, and the school all agree. Ledger stays
«دفتر حساب‌ها» (sidebar/section) with page title «دفتر حساب» (a single account's ledger) —
an acceptable section-vs-page distinction; the guide references the sidebar label.

### D12 — «دیدن سند» opens a dialog, not a deep-link into the paged journal
The entry-for endpoint returns one entry_id. Rather than deep-linking into the paginated
دفتر روزنامه (which would need scroll-to-entry + auto-expand plumbing), «دیدن سند» fetches
the entry and shows its بدهکار/بستانکار lines in a small read-only dialog. The merchant
never loses their place, and the feature has zero coupling to journal pagination.
