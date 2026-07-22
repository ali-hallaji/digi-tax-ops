# Backlog — queued items (founder-gated; do NOT start until explicitly queued)

## طراحی معماری داده برای مقیاس‌پذیری آینده (P8 slot, after P6) — DONE (2026-07-13, backend `622a506`+`6994c87`, LOCAL/unpushed)

Measure-first audit delivered in `db-audit.md` (workspace root). Shipped migration
`m6n7o8p9q0r1`: 8 evidence-based indexes (CONCURRENTLY); 3 candidates rejected as
over-indexing. Key finding: `random_page_cost` must be `1.1` on SSD for the composites
to be adopted. Backlogged with measurements (below): read-path N+1s (journal export,
purchase/return line loads), journal-engine `ensure_detail` N+1 + per-entry flush,
trial-balance `entry_date`-on-`journal_lines` denormalization, `journal_lines`
fiscal-year partitioning, and PITR/WAL archiving. Tests 775 pass / 7 baseline fail
(zero new); reconciliation invariant holds. Pending founder GO + guarded deploy.

**Original goal:** evidence-based database design review before user/data volume grows.

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

## P7b — admin shell: session-expired renders «در حال بررسی» forever — DONE (2026-07-13, frontend `525d7b5`, LOCAL/unpushed)

`_admin.admin.tsx` rendered the same «در حال بررسی دسترسی ادمین» card for BOTH
`isCheckingAdminAccess` and `isSessionExpired` (401 from /admin/me) — an expired
admin session looked like an infinite loading state instead of a re-login prompt.
Fixed: 401 → a «نشست شما منقضی شده» card + «ورود دوباره» button (clears the dead
local session, no server logout, preserves the intended route). The partner shell
(`_partner.partner.tsx`) had the identical trap — fixed the same way.

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

## PB — تورهای per-صفحه (per-section mini-tours) — DONE (2026-07-13, frontend `b229f20`+`0da4d6c`+`eda923b`, LOCAL/unpushed)

Extended the P6 onboarding-tour engine with 7 per-page mini-tours (invoice-create,
settlement dialog, cheques, reports, accountant/journal, partner-console, reminders),
each 3–4 steps, auto-firing once on first visit and replayable from a «؟ راهنمای این
صفحه» button (helpTourId on the shared PageHeader). Reuses the P6 anchors/step model;
per-tour «completed» key + an app-wide "one auto-fired tour per session" slot so it
doesn't nag. Guide S8-16 + settings toggle copy + a merchant what's-new entry (no-drift).

## توپولوژی خروجی ایران برای مودیان در پروداکشن (Moadian Iran-egress topology) — QUEUED (founder decision)

tp.tax.gov.ir is Iran-access-only. Our servers (and the founder's laptop) are OUTSIDE
Iran, so a connection test / real submission from them never reaches the destination
(null `server_time`, no HTTP response — NOT a crypto/auth failure). MD-1 shipped an
opt-in `MOADIAN_PROXY_*` (SOCKS5/socks5h) wired into the Moadian client only, which
unblocks LOCAL/TESTING via the founder's in-Iran SOCKS proxy (port 2080).

**Prod topology is a founder decision — options:**
1. **Iran VPS for the api** — run the whole api inside Iran (simplest egress; but moves
   the DB/app hosting decision).
2. **Iran-hosted egress relay** — keep the api abroad, route ONLY Moadian traffic through
   a small in-Iran relay/proxy (the `MOADIAN_PROXY_*` model, hardened for prod: stable
   host, auth, monitoring).
3. **Iran-egress proxy service** — a managed in-Iran SOCKS/HTTP egress.

Trade-offs: latency, reliability of the egress, where per-tenant keys live, and whether
the proxy host is trusted with TLS-terminated traffic (it is NOT — the Moadian TLS is
end-to-end to tp.tax.gov.ir; the proxy only forwards). Decide before MD-2 real submission
goes live. `MOADIAN_PROXY_*` is currently for local/testing only.

**Pre-production checklist additions (MOADIAN D STEP B, 2026-07-22):**
- **systemd unit for the SOCKS tunnel** — the dev-host `autossh -D 172.18.0.1:2080`
  tunnel is launched manually today and does NOT survive a reboot. Whatever prod
  topology is chosen, the egress path must be supervised (systemd unit with
  `Restart=always`, or equivalent), not a hand-run process.
- **Egress-host DNS pins** — the egress host needs BOTH `/etc/hosts` pins
  (`tp.tax.gov.ir` live + `sandboxrc.tax.gov.ir` sandbox); its resolver SERVFAILs
  on these names. Procedure (no IPs in git): runbook § Egress-host DNS pins.

## Moadian private-key durability discipline (prod) — DOCUMENTED (2026-07-17)

A wipe-first reseed (`reset_world.sh`) once destroyed a real, runtime-created Moadian
private key — the seed never stores one, so any `moadian_tenant_profiles.encrypted_private_key_blob`
is genuine merchant key material. Now guarded LOCAL/dev: reset-world snapshots before the
wipe and refuses to proceed if a real key exists (lists them; `--force` overrides).

For **production** the concern is different — reseeds never run there — but key durability
still needs discipline, to document before real submission (MD-2) goes live:
- Backups must include `moadian_tenant_profiles` (the encrypted blobs) AND the Fernet
  `MOADIAN_CRED_KEY`; a blob without its key is unrecoverable. Rotating `MOADIAN_CRED_KEY`
  (or falling back to `SECRET_KEY`) orphans every stored key — treat it as key-custody, not
  ordinary config.
- No prod migration/maintenance path may `DROP`/truncate `moadian_tenant_profiles`. Any
  destructive op there needs a pre-op snapshot + explicit sign-off, mirroring the reseed guard.
- Consider a "re-import your key" self-serve recovery in the cockpit for the case where a
  key is lost but the public key is still registered in the merchant's کارپوشه.
