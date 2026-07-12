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

## PB — Self-Hosting سازمانی (enterprise on-prem)

Enterprise on-premise deployment of the existing Docker Compose stack for orgs
that require data to stay inside their own network. Open questions to resolve when
the first enterprise lead appears: licensing/activation model (offline license key
vs phone-home), the update channel (pinned image tags vs a managed pull), support
SLA tiers, and data-migration in/out (import an existing cloud tenant → on-prem,
and the reverse). No near-term bridge; this is a distinct future phase. Gate: real
enterprise demand.

## PB — حقوق و دستمزد v1 (Iranian payroll)

Full Iranian payroll as its own future phase: بیمهٔ تأمین اجتماعی, مالیات پلکانی
حقوق (salary-specific brackets, distinct from the Article-131 business brackets in
PA-T1), عیدی/سنوات, پایهٔ حقوق و مزایا, and monthly لیست بیمه/مالیات output.
**Near-term bridge already available (no new build):** the «حقوق» expense category
records payroll spend today, and the PA-T2 reminders already surface the standing
tax/insurance deadlines — merchants aren't blind to payroll obligations before v1
ships. Gate: after the core accounting + partner loop matures.

## PB — تورهای per-صفحه (per-section mini-tours)

Extend the P6 onboarding-tour engine with per-section mini-tours triggered from a
small «؟» affordance on a page/section (not just the one-time global tour). Reuses
the existing tour anchors + step model; adds a per-section trigger + a «seen» key
per mini-tour so it doesn't nag. Low-risk, incremental. Gate: after the current
guide/school content stabilizes.
