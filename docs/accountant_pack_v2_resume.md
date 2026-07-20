# Accountant-Pack v2 — RESUME NOTE (PART 3 + PART 4)

Written 2026-07-21 at a committed boundary. PART 1, 2, and all of PART 5 are done,
committed locally (NOT pushed/deployed), gates green (backend 1093/7/4, frontend
typecheck+build). This note lets the next session execute the two remaining
headline parts without re-researching. **Nothing is pushed** — the whole batch
ships in ONE guarded deploy at the end (founder GO required per turn).

## State recap (commits, all LOCAL)
- FE: `7ed7192` (P1 switcher) · `da97851` (P5.1) · `0a8df07` (P5.3) · `28ef4a9` (P5.4
  docstring) · `a31bb82` (P5.5) · `651f08c` (P5.2) · `325bc00` (P2)
- BE: `ee36dd3` (P1b window) · `6984b60` (P5.4 tests) · `10ef2cc` (P5.5) · `3dbfd3c` (P2)
- ops: progress.md updated (this batch), uncommitted+committed locally.

---

## PART 3 — Persian-RTL PDF engine + Excel export sweep

### KEY: the engines already exist — EXTEND, don't build
- **PDF = WeasyPrint** (`weasyprint>=62.3`, already a dep). `invoice_drafts/application/
  pdf_service.py` → `render_invoice_pdf(ctx, layout)` renders HTML→PDF (real HarfBuzz RTL
  shaping + bidi — no reshaper/reportlab needed). HTML source = `print_service.render_print_view`.
  Layouts `official_a4`/`official_landscape`; `@page` A4 already set (`print_service.py:327`).
  Fonts embedded as base64 `@font-face` data URIs via `_BUNDLED_FONTS` (`pdf_service.py:59`) —
  currently NotoNaskhArabic + DejaVuSans TTFs in `invoice_drafts/application/assets/fonts/`.
- **XLSX = openpyxl** via `xlsx_response(report, sheet_title, headers, rows, money_cols)`
  (`accounting/application/xlsx.py:21`) — already RTL sheet, bold frozen header, `#,##0`
  money format, Jalali filename. Module-agnostic; `partners` already imports it cross-module.

### Vazirmatn TTF for the PDF engine (the one real gap)
No Vazirmatn `.ttf`/`.otf` in either repo (frontend has only woff2). The backend image HAS
`fonttools 4.63` + `brotli` (verified) → decompress the woff2 to TTF:
```
# inside the backend image / a one-shot:
python -c "from fontTools.ttLib.woff2 import decompress; decompress('Vazirmatn-Regular.woff2','Vazirmatn-Regular.ttf')"
```
Source woff2: `digi-tax-frontend/public/fonts/Vazirmatn-{Regular,Bold}.woff2`. Drop the TTFs
in `invoice_drafts/application/assets/fonts/` (or a new shared `app/common/pdf/assets/`) and
register in `_BUNDLED_FONTS` the same way as Noto. `print_service.py:261` already lists
`'Vazirmatn'` in its CSS font stack as a fallback — nothing embeds it yet.

### Build a shared report renderer (base template + table renderer)
The dispatch wants ONE engine reusable for reports/accountant + later invoices. Suggested:
`app/common/pdf/report_pdf.py` — a base A4 HTML template (letterhead: business name + logo
placeholder, Jalali date, ریال/تومان per business display pref) + a generic table renderer
`render_report_pdf(*, title, business, columns, rows, money_cols, meta)` → WeasyPrint bytes,
reusing `pdf_service`'s font CSS. Then a `pdf_response(...)` helper mirroring `xlsx_response`.

### Wire PDF + XLSX — coverage matrix (what exists today)
Only 4 handlers emit xlsx today (all reuse `xlsx_response`): accounting **ledger**
(`accounting/api/routes.py:225` `?format=xlsx`), **trial-balance** (`:303`), **journal.xlsx**
(`:393`), partner **earnings** (`partners/api/routes.py:234`). Reports emit **CSV only**
(`reports/api/routes.py` `format=="csv"` branches at `:135,176,231,285,339`). Everything else
(customers, products, payments, cheques, purchases, expenses, returns, invoices-list) has NO
export.

Do (in value order):
1. **PDF on the 4 merchant reports** (register/party-balances/cash-flow/profit-loss,
   `reports/api/routes.py`) + accountant **trial-balance** & **ledger** — add a `format==pdf`
   branch calling the new `render_report_pdf`. These already have the aggregated rows.
2. **XLSX sweep**: add a dedicated export handler per list surface (customers, products,
   payments, cheques, purchases, expenses, returns, invoices) that calls the SERVICE layer
   **unpaginated** (`page_size=100000`, the journal pattern) — do NOT `format=` the capped
   list route (`app/utils/listing.py MAX_PAGE_SIZE=100`, no `?all=`). Reuse `xlsx_response`.
   Add xlsx to the 4 reports too (currently CSV-only).
3. Every export must accept + honor the fiscal window — reuse the `fiscal_year_window`
   dependency (`app/common/fiscal_window.py`) already built in PART 1b.

### Frontend: ONE shared export component
No shared export button exists — there are 4 near-identical blob helpers: `downloadAccountingCsv`
(`lib/api/accounting.ts:230`), `downloadReportCsv` (`reports.ts:171`), `downloadPartnerCsv`
(`partners.ts:184`), `downloadInvoicePdf` (`invoice-drafts.ts:253` — the richest: parses
Content-Disposition, Persian errors). **Collapse into one `downloadBlob(path,{params,filename,
format})` util + one `<ExportButton>`** (shadcn Button + `Download` icon, busy state, Persian
toast). HARNESS matches the exact string «خروجی Excel» (`tests/e2e-harness/specs/02:61`) — keep
xlsx buttons labelled «خروجی اکسل»/«خروجی Excel». Add the button to every list page pointing at
its new xlsx endpoint; pass the global FY window (`useActiveFiscalYear().range`).

---

## PART 4 — Accountant trial-balance drill-down (~80% present)

Chain: trial-balance row → account turnover (= the LEDGER) → source document (read-only).
- **Trial balance**: `GET /accounting/trial-balance` (`accounting/api/routes.py:264`, service
  `R.trial_balance` `reports.py:243`). Rows have `code,title,level,debit,credit`. Frontend
  `trial-balance-view.tsx` + `_app.app.accounting.trial-balance.tsx`. Make rows clickable →
  navigate to the ledger for that account (`?account_id=`).
- **Turnover = ledger**: `GET /accounting/ledger?account_id=` (`routes.py:187`, `R.ledger`
  `reports.py:132`). Row shape `entry_no,entry_date,description,debit,credit,running_balance`
  (`schemas.py:55`). **GAP**: rows don't carry `entry_id`/`source_type`/`source_id` and aren't
  clickable. FIX: extend `R.ledger` (`reports.py:170-181`) to also SELECT `JournalEntry.id`
  (+ `source_type`,`source_id`); add to `LedgerRowResponse` (`schemas.py:55`) + TS `LedgerRow`
  (`lib/api/accounting.ts:70`); make `ledger-view.tsx:157` rows link to the سند page.
- **Source doc**: `JournalEntry.source_type`+`source_id` (`accounting/infrastructure/models.py:124`);
  reverse lookup `GET /accounting/entry-for` (`routes.py:170`); `sourceDocPath(entry)`
  (`entry-view.tsx:30`). Lowest-friction drill target = the سند page
  `/app/accounting/entries/{entryId}` (`_app.app.accounting.entries.$entryId.tsx`, read-only
  voucher + onward «اصلاح تراکنش مبدأ» to the real doc). Only invoices have a per-ID read-only
  route (`_app.app.invoices.$invoiceId_.view.tsx`); purchase/payment/cheque resolve to list
  pages — route via the سند page to sidestep.
- **Gating**: `_gate` (`accounting/api/routes.py:54`) = `require_feature(...accountant_view...)`
  + `tenant.accountant_view_enabled`. New endpoints must go through the same `_gate`.
- **PDF/Excel on drill-down**: ledger + trial-balance already have xlsx/csv; PDF is net-new
  (use the PART 3 renderer). Add the shared `<ExportButton>`.

---

## VERIFY / SHIP (deferred to the end of the batch)
- Playwright view-only on dev: switcher changes a list; out-of-year friendly error; one PDF +
  one Excel downloaded; drill-down two levels; bulk draft delete; password eye toggle.
- Gates: `bash ../digi-tax-backend/scripts/run_tests.sh` (expect 11xx pass / 7 baseline / 4
  skip), ruff+black; `pnpm typecheck && pnpm build`; `pnpm harness` 9/9 local + dev.
- Rebuild API `--no-cache` (backend changed), alembic if any migration (none so far), psql-verify.
- Guarded dev deploy compose v2 `--no-cache` (frontend + api). Founder GO required.
- Immediate PART 2 follow-up: pass the FY window from the purchase/expense CREATE forms (backend
  lock already wired) so their out-of-year lock is active too.
