# MOADIAN F Part 2 — pagination / search / filter sweep

_Audit + fixes. Shared foundation reused (not reinvented): FE `useListQuery` +
`ListShell` + `normalizeListResponse`; BE `app/utils/listing.py` (page/page_size
for CRUD) or the limit/offset dialect for admin/moadian feeds._

## Priority — /app/moadian (the founder's ask)

| Surface | Before | After |
|---|---|---|
| **Cockpit «ارسال‌های صورتحساب»** (`GET /admin/moadian/submissions` → `list_submissions`) | hard `.limit(50)`, no pager, no search | **server-paginated (limit/offset) + search (شمارهٔ سند / taxid / شماره ارجاع) + status & environment filters + calm count.** `list_submissions` returns `(rows, total)`; the per-invoice timeline call (invoice_id set) still returns ALL rows for that one invoice (bounded). FE `SubmissionsCard` rewritten onto `ListShell` + two filter selects. |
| **Cockpit «سوابق ارتباط»** (`GET /moadian/profile/api-log` → `list_api_log`) | hard `limit=20`, no pager | **server-paginated (limit/offset) + total + prev/next footer.** `list_api_log` returns `(rows, total)`. |

## Real unbounded query fixed

| Surface | Before | After |
|---|---|---|
| **Accounting ledger drill-down** (`GET .../ledger` → `reports.ledger()`) | `.order_by(entry_no)` over the whole window, **no limit** — the one truly unbounded query (a busy account × a long window streams thousands of rows) | **defensive cap `LEDGER_MAX_ROWS = 5000` + `{total_rows, truncated}` flags.** opening/closing computed INDEPENDENTLY (`opening + Σ(debit−credit)` over the full window) so a capped row list never corrupts the balance. Not a silent cap — `truncated` tells the UI to narrow the date range. (Proper running-balance cursor pagination = logged follow-up; FE `truncated` banner = logged follow-up.) |

## Verified PAGINATED-OK (no change)

Invoices, customers, products, vendors, purchases, cheques, payments, returns,
reports (register / party-balances / cash-flow), accounting journal, admin users,
admin businesses, admin taxpayers, admin moadian submissions-feed
(cross-tenant), admin audit-log «گزارش ممیزی», partners/module-requests/
credit-activations/module-offers, stuffid id-search — all already server-paginated
(page/page_size or limit/offset) through the shared foundation.

## Logged follow-ups (FE-driven gaps + reference caps — BE already paginated)

Small, bounded, not this batch (97% rule):
- **Notification/SMS log** (`_admin.admin.system-health.tsx` → `getAdminNotificationLog`): FE hardcodes `limit=20&offset=0`; BE (`get_admin_notifications`) is fully paginated — wire a pager.
- **Admin taxpayer-profiles review**: FE fetches `limit=100` then paginates client-side (breaks past 100/status); BE paginated — send offset.
- **Admin moadian profiles**: FE never sends `offset`, `ListShell` pinned `page=1`; BE paginated + searchable — send offset.
- **Expenses tab** (`_app.app.purchases.tsx`): FE `getExpenses()` with no params → fixed 50; BE (`list_expenses`) paginated — add a pager/search on that tab.
- **Stuffid imports history** (`catalog_imports`): route caps ≤100, no offset — add offset.
- **Stuffid tax-units** (`list_tax_units`): `.limit(200)` reference table — fine; add search+offset if it grows.
- **Ledger**: proper running-balance cursor pagination + FE `truncated` banner.
