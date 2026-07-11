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

## P7a — rate-limiter must trust X-Forwarded-For from the local proxy (before P8)

Today the auth rate limiter keys "per-IP" on the connection peer, which behind the
reverse proxy is always the server's own IP — **all external users share one bucket**.
A benign burst (or one abuser) blocks OTP/login for the whole site for
`block_seconds`. Fix: read the client IP from `X-Forwarded-For` (first hop) but ONLY
when the peer is the trusted local proxy; keep peer-IP behaviour otherwise. Small,
medium-priority. (Observed live 2026-07-11 during the P2 deploy smoke: an 8-request
429 test blocked the whole dev site's OTP bucket for 300s.)

## P7b — admin shell: session-expired renders «در حال بررسی» forever

`_admin.admin.tsx` renders the same «در حال بررسی دسترسی ادمین» card for BOTH
`isCheckingAdminAccess` and `isSessionExpired` (401 from /admin/me) — an expired
admin session looks like an infinite loading state instead of a re-login prompt.
Split the two states: 401 → a clear «نشست شما منقضی شده» card with a login button
(no logout side-effects). Small.
