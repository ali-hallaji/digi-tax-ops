# Backlog — queued items (founder-gated; do NOT start until explicitly queued)

## طراحی معماری داده برای مقیاس‌پذیری آینده (P8 slot, after P6)

**Goal:** evidence-based database design review before user/data volume grows.

**Deliverables:**
- (a) **Schema audit** — missing indexes on hot FKs and query-filter columns;
  over-indexed tables; nullable-should-be-not-null; N+1 patterns, especially in
  settlement recompute, journal regenerate, dashboard aggregates, and the admin
  overview strip.
- (b) **Partitioning candidates** — `journal_lines`, `payments`, `invoice_drafts`
  (by `tenant_id` or date).
- (c) **Archival strategy** for old journal entries (the journal is regenerable —
  archival is simpler than for source documents).
- (d) **Query-plan review** of the top-10 highest-frequency queries
  (`EXPLAIN ANALYZE` against seeded prod-shape data).
- (e) **Migration/backup posture under load** — PITR, replica readiness,
  snapshot cadence.
- (f) **Tenant isolation stress** under concurrent load.

**Model:** Opus. **Mode:** no code execution in the audit; measurement + a
prioritized plan. **Gate:** do not start until the founder queues it.
