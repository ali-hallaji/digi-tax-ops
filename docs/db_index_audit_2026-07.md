# DB Index Audit — BATCH 0.5 (2026-07-20)

One-time performance audit of the local seeded world (supermarket persona
`سوپرمارکت محله`, 500 finalized invoices; stuffid catalog 3,984,695 rows) plus the
permanent index migration it justified: backend `d0e1f2a3b4c5_perf_indexes_batch05`.
Method: full index inventory (`pg_indexes`), hot-query map from actual
routers/services code, `EXPLAIN (ANALYZE, BUFFERS)` before/after on the live local
compose stack.

## 1. Inventory summary

188 indexes across 54 tables. The schema is already well-covered: every merchant
list table has a `(tenant_id, …)` composite for its primary filter, reports run on
`(tenant_id, issue/purchase/expense_date)` composites, the entitlement gate is fully
served by `uq_tenant_entitlements_pair (tenant_id, feature)`, trial balance by
`ix_journal_lines_party` (leading `tenant_id`), and the partner tables by their
grant composites. The audit found **six** real gaps (below) and confirmed the rest.

## 2. Migration contents (each index → the query it serves)

| Index | Query served |
|---|---|
| `ix_payments_tenant_payment_date (tenant_id, payment_date, created_at)` | payments list: `WHERE tenant_id ORDER BY payment_date DESC, created_at DESC` — previously a top-N heapsort per page (only `(tenant_id, created_at)` existed) |
| `ix_cheques_tenant_due (tenant_id, due_date, created_at)` | cheques list default sort `due_date ASC, created_at ASC` + dashboard-tasks / reminders due-window (`due_date <= cutoff`), run on every dashboard load |
| `ix_return_documents_tenant_created (tenant_id, created_at)` | returns list `ORDER BY created_at DESC` — table only had single-column `tenant_id` |
| `ix_tax_coefficient_requests_tenant_status (tenant_id, status)` | tax-lens merchant summary pending-count `WHERE tenant_id AND status='pending'` — no tenant index existed at all |
| `ix_invoice_draft_lines_product (product_id) WHERE product_id IS NOT NULL` | `recompute_stock` `_sales_qty`/`_sale_return_qty`: `WHERE product_id = X` per tracked product on **every invoice finalize/return** — unindexed FK ⇒ per-write seq scan, O(total lines) |
| `ix_purchase_lines_product (product_id) WHERE product_id IS NOT NULL` | `recompute_stock` `_purchase_qty`/`_purchase_return_qty` — same per-write shape; only `purchase_id` was indexed |

## 3. Before/after (local, supermarket persona, warm)

| Query | Before | After | Plan change |
|---|---|---|---|
| payments list (410 rows, page 20) | 1.93 ms — Seq Scan + top-N heapsort | **0.21 ms** — Index Scan Backward on new index, Sort gone | ✅ real flip |
| recompute `_sales_qty` (13 lines of 803) | 1.71 ms — Seq Scan on invoice_draft_lines | 1.70 ms — Bitmap Index Scan on new index (line side; drafts side still seq at 500 rows) | ✅ line-side flip |
| cheques list (30 rows) | 0.32 ms seq+sort | 0.26 ms seq+sort (planner ignores index at 30 rows; forced plan uses `ix_cheques_tenant_due` correctly) | structural |
| cheques due-window count | 0.09 ms seq | 0.11 ms seq (forced plan uses index) | structural |
| returns list (0 rows this tenant) | 0.16 ms | 0.05 ms (forced plan: Index Scan Backward on new index) | structural |
| tax_coefficient_requests pending count | 0.18 ms | 0.03 ms (forced plan: Index **Only** Scan on new index) | structural |
| invoice list (baseline, no change) | 0.52 ms | 0.27 ms — already on `ix_invoice_drafts_tenant_created` | — |
| trial balance (2,216 lines) | 19.5 ms | 19.0 ms — covered by existing `ix_journal_lines_party` | — |
| entitlement gate | 0.16 ms | 0.02 ms — covered by existing `uq_tenant_entitlements_pair` | — |

**Honesty note:** at current local sizes (≤800 rows on every merchant table) only the
payments sort elimination and the recompute line-side flip are *measurable*; the other
four indexes were verified usable via forced plans (`enable_seqscan=off`) and are
justified by query shape on tables that grow with usage — the planner adopts them as
soon as row counts outgrow a few heap pages. None were dropped because "didn't help at
30 rows" is true of any index on a 30-row table; each cites a real production query.

## 4. stuff_catalog typeahead (4M rows) — verified, deliberately NOT changed

- **Code-prefix path** (`code >= :lo AND code < :hi ORDER BY code`): PK range scan,
  0.39 ms cold. Collation-safe by construction (range, not LIKE) — correct as-is.
- **Exact code lookup**: PK, 0.04 ms.
- **Selective title terms** (e.g. «خدمات حمل», ~1k matches): Bitmap scan on the
  existing trigram GIN, 26 ms cold. Correct as-is.
- **Broad title terms** (e.g. «برنج», ~78K matches): the planner picks
  seq-scan-until-400-candidates: **601 ms cold / 37 ms warm**. Forcing the GIN path
  measures **50 ms warm** — i.e. the planner's seq choice is *right* when warm and the
  slow case is cold-cache only (first broad search after a restart/import). This is
  the dev "146 ms" — a partially-warm broad term. **No index can improve this**: the
  GIN already exists and loses warm; the fix, if ever needed, is a query-side nudge
  (e.g. `SET LOCAL enable_seqscan=off` for the broad-term branch), which is a
  behavior change out of scope for this batch → logged as an optional follow-up.

## 5. Deliberately NOT indexed (and why)

- **Merchant ILIKE search boxes** (customers/products/vendors/payments/cheques/
  invoices `%term%` search): always tenant-scoped; the residual filter runs over one
  tenant's rows after the tenant index. Global pg_trgm GINs on these columns would
  tax every insert for no gain at per-tenant cardinality (hundreds–thousands).
- **customers/products `created_at` sort**: `(tenant_id, is_active)` composites exist;
  per-tenant cardinality low; revisit if a tenant exceeds thousands of rows.
- **cheques `customer_id`/`vendor_id`/`account_id` FKs**: only touched by rare
  delete-guard existence checks on a small table.
- **`*_by_user_id` audit FKs** (22 columns): never queried by that column.
- **vendors `name` sort**: per-tenant vendor counts are tiny.
- **journal ledger**: `ix_journal_lines_account` + PK join to entries is optimal for
  the per-account query shape.

## 6. Lock/deploy safety

Plain `CREATE INDEX` inside alembic's transaction (SHARE lock per table during
build). Largest affected table on dev: payments (~650 rows) / invoice_draft_lines
(~800 rows) — each build <10 ms, total write-block well under 1 s. The 4M-row
`tax_stuff_ids` table is untouched by the migration.

## 7. Test-DB isolation guard (shipped in the same batch)

`tests/conftest.py` now refuses to start unless the `DATABASE_URL` database name ends
with `_test` (escape hatch `DIGITAX_TESTS_DB_ALLOW=<dbname>`). Proof: pytest against
live `digitax` exits 2 with zero tests run; full suite via
`digi-tax-backend/scripts/run_tests.sh` (creates + migrates `digitax_test`) is green
at 1046 pass / 7 known-baseline fail / 4 skip, and live `module_prices` stayed at its
canonical 8 rows while `digitax_test.module_prices` absorbed `test_checkout_pg`'s
wipe — the incident is now impossible by construction. `preflight.sh` whitelists
`digitax_test` (not an orphan).
