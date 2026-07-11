# پنل همکار (پارتنرشیپ) — Partner Panel Design Plan

**Design-only deliverable for founder approval. No code, no migrations, no pushes.**
Cross-repo (backend + frontend + ops). Release slot per roadmap: R1C "Accountant & Retention" (module #15, currently NONE built). Moadian Stage D out of scope; D14 stays open — nothing below depends on it.

> **RESOLVED + BUILT (2026-07-11):** the founder approved **all nine open decisions as
> the recommended A options** (OD-1..OD-9 = A), with one addition baked into B4/F4:
> every journal-entry description visible to a partner carries the source document's
> human reference (invoice number, cheque number, expense category) so a سند is
> auditable without leaving the accountant layer. The batch shipped as B1–B7
> (backend), F1–F7 (frontend), O1 (ops) — commit hashes in `progress.md`
> («پنل همکار» entry). The cash-flow residual was closed pre-push (B8 backend
> `GET /partner/businesses/{id}/treasury-accounts` + F8 cash-flow tab);
> duplicate-partner UX and commission mechanics stay deferred as designed.

---

## Context

Partners are accountants/consultants who **supervise many businesses** — review, export, guide — and **bring clients** to Digi Invoice. The product docs already commit to this direction:

- `product_master_blueprint_v4_2.md` §4.1.3: «حسابدار دشمن محصول نیست. حسابدار کانال رشد محصول است.» — accountant supervises/corrects/advises, gets a recurring share of subscriptions.
- `business_scope_freeze_v1.md` defines two archetypes: **`accountant_partner`** (access to assigned clients' data; view invoices/reports/balances; limited edits *with client approval*) and **`sales_agent`** (refer + commission, **no client data**). This plan builds the accountant_partner v1 with the referral hook; sales_agent and commission mechanics are explicitly deferred (commission needs the Subscription module, R1A-P6, not built).
- Founder hard rule (HANDOFF.md): «پارتنرشیپ نمی‌شود با ادمینِ ستادی قاطی شود» — completely separate module from staff admin.
- Today's stopgap is S9-05 (CSV export «بدون واگذاری کامل دسترسی») — the partner panel is the real solution.

Everything below reuses proven in-repo patterns: the **admin shell** (`/admin/*` two-file layout, `/admin/me` preflight, 403-without-logout state machine), the **member invite** machinery (S8-01..04: soft-revoke, server-side 403, reactivate-same-row), the **Batch B accounting layer** (tenant_id-parameterized read services in `app/modules/accounting/application/reports.py` — directly reusable), and the **`require_system_admin`** DB-live authority pattern (`app/modules/identity/application/auth.py:132`).

**Locked terminology to add to the scenarios table** (no term exists yet — coining now prevents synonym drift): «همکار» (partner) · «پنل همکار» (the shell) · «حسابدار همکار» (the persona) · «کد همکار» (partner code) · «دسترسی همکار» (the grant). Avoid: شریک، نماینده، پارتنر (raw transliteration) in UI copy.

---

## 1. Data model

### 1a. Partner identity — reuse `users` + new `partner_profiles` (1:1)
A partner is an L2 user (unique per mobile, same OTP login — the pyramid model) — no parallel identity system. Partner-ness is a **profile**, not a boolean on users, because it carries workflow state (approval, code, firm name) — richer than `is_system_admin`:

```
partner_profiles
  id UUID pk
  user_id UUID FK users, UNIQUE          -- 1:1; one partnerhood per person
  status String(20)                       -- pending | approved | suspended | rejected
  partner_type String(20) default 'accountant'   -- future-proofs sales_agent; single value in v1
  partner_code String(12) UNIQUE          -- human-shareable, e.g. "HAM-4X7K"; server-generated on approval
  firm_name String nullable               -- display only in v1 (see OD-5)
  city / province nullable
  review_note Text nullable               -- admin's Persian rejection reason
  approved_at / approved_by_user_id nullable
  created_at / updated_at
```

### 1b. Grants — new `partner_business_grants` (+ append-only event log)
**NOT `tenant_members` rows.** A grant is a different relationship (cross-tenant supervision, no role in the role matrix); putting partners into tenant_members would pollute member lists, `seesAllTenantData`, and the D5 scope system. Mirrors tenant_members conventions (unique pair, reactivate-same-row):

```
partner_business_grants
  id UUID pk
  partner_profile_id UUID FK partner_profiles
  tenant_id UUID FK tenants
  status String(20)                       -- invited | active | declined | revoked
  invited_by_user_id UUID FK users        -- the owner/admin who invited
  responded_at / revoked_at nullable
  revoked_by_user_id nullable             -- owner-side or partner-side exit
  created_at / updated_at
  UNIQUE (partner_profile_id, tenant_id)  -- one row per pair; transitions reactivate

partner_grant_events                      -- audit trail (explicitly required)
  id UUID pk
  grant_id UUID FK partner_business_grants
  event String(30)                        -- invited | accepted | declined | revoked_by_owner |
                                          --   revoked_by_partner | reinvited
  actor_user_id UUID FK users
  created_at
```
Append-only events (no update/delete path) because status columns alone lose history on re-invite after revoke. No generic audit infra exists to reuse (`/admin/audit-logs` is a stub).

### 1c. Referral attribution — `tenants.referred_by_partner_id`
Nullable FK `partner_profiles.id` on tenants. Captured **once at business creation** via an optional «کد همکار» field in the wizard (invalid/unknown code ⇒ inline field error, never a hard block). Immutable afterwards in v1 (no admin re-attribution yet). Commission/billing mechanics: **explicitly deferred** — this column is the minimum that makes future commission computable.

**Migrations (3, continuing the chain from head `a4b5c6d7e8f9`):** M1 `partner_profiles` → M2 `partner_business_grants` + `partner_grant_events` → M3 `tenants.referred_by_partner_id`. All reversible; naming follows the existing sequential-suffix convention.

---

## 2. AuthZ — how grants compose with the existing system

**Core principle: partners never enter the membership/scope system, and all partner gates are DB-live per request** (like `require_system_admin`), so **revoke cuts access on the very next request** — no token invalidation needed, and nothing partner-related goes into the token.

- **`require_approved_partner`** (new dependency, mirror of `require_system_admin`): load user by `auth.user_id` → require `is_active` + `partner_profiles.status == "approved"` → return profile; 403 friendly Persian otherwise.
- **`resolve_partner_business_access(profile, business_id, db)`**: require an `active` grant for `(profile, business_id)`. **Ungranted/unknown business ⇒ 404** (not 403) to prevent tenant enumeration (OD-8).
- **Partner endpoints carry `business_id` explicitly in the path** (`/partner/businesses/{id}/…`), like `/admin/businesses/{id}`. The `active_business_id` token mechanism is untouched — partners hop across businesses without re-minting tokens, and blueprint rule 8 (tenant isolation) is honored as a *deliberate, grant-scoped* cross-tenant read, never a bypass of merchant namespaces.
- **Zero change to merchant namespaces.** A partner hitting `/customers`, `/accounting/*`, etc. has no membership ⇒ existing resolution already 403s. The Batch B accounting read layer (`chart_tree`, `journal_page`, `ledger`, `trial_balance`, `entry_for`, CSV) is already `tenant_id`-parameterized pure reads ⇒ the partner router wraps the **same functions** behind the partner gate. No business-logic duplication.

### Gate matrix (per endpoint family)

| Surface | Owner/Admin member | Staff/Viewer member | Partner w/ active grant | Partner w/o grant / revoked | SysAdmin |
|---|---|---|---|---|---|
| `/accounting/*` (merchant ns) | ✓ if toggle ON, else 403 | 403 | — (no membership ⇒ 403, unchanged) | — | unchanged |
| `/partner/me` | state=`none`* | state=`none`* | 200 approved | 200 approved (empty portfolio) | state=`none` unless also a partner |
| `/partner/businesses` (portfolio) | — | — | 200 (own grants only) | 200 (invites/empty) | — |
| `/partner/businesses/{id}/accounting/*` + `/reports/*` | — | — | ✓ (toggle per OD-3) | **404** | — |
| Grant mgmt, merchant side (`/businesses/{id}/partners/*`) | ✓ | 403 | — | — | ✓ (existing `_require_owner_or_admin` short-circuit) |
| `/admin/partners/*` | 403 | 403 | 403 | 403 | ✓ |
| All other merchant ops endpoints | unchanged | unchanged | 403/404 (no membership — unchanged) | same | unchanged |

\* `/partner/me` returns a **status discriminator** (`none | pending | approved | suspended | rejected`) rather than a bare 403 — the shell uses it to render the application form / under-review card (§4). Data-access endpoints stay hard-gated on `approved` + active grant.

**Toggle interaction — recommendation (OD-3):** an **active grant implies partner accounting access, independent of the merchant's own «نمای حسابدار» toggle**. The grant *is* the owner's explicit consent — stronger than the toggle, which D13 established as the *merchant's own* view preference, not a data switch. To satisfy D1 (reads never auto-regenerate), **grant activation triggers `generate_tenant_journal`** exactly like toggle-ON does, and the partner journal page gets the same «به‌روزرسانی اسناد» button. Merchant surfaces stay pixel-identical for businesses with no partner (structural, like D10).

---

## 3. Partner shell — `/partner/*`

Two-file TanStack pattern copied from admin: `_partner.tsx` (pass-through `<Outlet/>`) + `_partner.partner.tsx` (shell at `/partner`). Preflight = React Query `GET /partner/me` with the admin shell's exact state machine (checking / denied / session-expired / ready); **403/denial shows a calm card without logout** (AGENTS.md: 403 is a state, never auto-logout). Whitelist `/partner*` in `login.tsx`'s `isAllowedRedirectPath`. Entry point: merchant-sidebar footer link «پنل همکار» shown only when `/partner/me` returns `approved` (mirror of the «ورود به پنل ادمین» link).

**Shell states by `/partner/me` status:** `none` → application form (§4) · `pending` → «درخواست شما در حال بررسی است» card · `rejected` → reason + re-apply · `suspended` → contact-support card · `approved` → the real shell.

**Branding:** sidebar `side="right" collapsible="icon"`, its own header tile distinct from merchant (`bg-primary`) and admin (`bg-foreground`) — e.g. the `--info` family — label «پنل همکار» / «دیجی اینویس — همراه حسابداران». Same `ThemeToggle`, `SidebarProvider`, `Toaster`, Vazirmatn, Calm Bazaar tokens, RTL, 390px-first. **Partner copy may use accounting vocabulary** — the merchant jargon ban does not apply in this shell.

**Routes:**
| Route | Page |
|---|---|
| `/partner` | Portfolio dashboard: «دعوت‌نامه‌های در انتظار» banner (accept/decline) + granted-business cards + referred-business section (per OD-6) |
| `/partner/businesses/$businessId` | Drill-in; index redirects to journal (same pattern as `/app/accounting` index) |
| `…/journal` `…/ledger` `…/trial-balance` `…/chart` | The 4 accountant pages, partner-gated API; extract shared presentational table components from the Batch B pages so both shells render identically, each behind its own gate |
| `…/reports` | Read-only report tabs (register / balances / cash-flow / P&L / expense breakdown) via `/partner/businesses/{id}/reports/*` |
| `/partner/profile` | «کد همکار شما» + copy/share, firm name, status |
| `/partner/guide` | Partner-scoped guide (mirror of the admin-guide pattern) |

**Portfolio card contents (aggregates only — data minimization; details live behind drill-in):** business name + activity type + city · grant date · آخرین فعالیت (latest journal-entry date) · تعداد اسناد · تراز متعادل/نامتعادل flag · نزدیک‌سررسیدها count (server-computed cheques-due-in-7-days count — a number, never cheque rows). One purpose-built `GET /partner/businesses` portfolio endpoint serves all cards.

**Notifications-worthy events (list only — NO notification infra this phase):**
1. Owner invited a partner (→ partner) · 2. Partner accepted/declined (→ owner) · 3. Owner revoked access (→ partner) · 4. Partner left a business (→ owner) · 5. Application approved/rejected (→ applicant) · 6. Referred business signed up / activated (→ partner) · 7. Cheque due-soon in a granted business (→ partner, digest) · 8. Month-end «دفترها آمادهٔ مرور است» (→ partner, digest).

---

## 4. Onboarding + referral

**Becoming a partner (OD-4, recommendation): self-serve application + admin approval.** Any authenticated user visits `/partner` → status `none` → application form (name / firm / city + short «چرا همکار می‌شوید؟») → `POST /partner/apply` creates `partner_profiles(status=pending)` → admin reviews in `/admin/partners` (approve → code generated; reject → mandatory Persian reason). Mirrors the taxpayer-profile review workflow the admin shell already implements. Admin can also create+approve directly (superset). **No business required to apply** — an accountant is never forced to create a fake business (the `/partner` shell is reachable business-less).

**Referral (the minimum attributable "brings clients" hook):** partner shares their «کد همکار»; the business-creation wizard gains one optional field «کد همکار (اختیاری)» → `tenants.referred_by_partner_id`. Portfolio shows referred businesses per OD-6 (recommendation: name + activation state only — §4.1.4's sales-partner scope, no financial data). **Commission/billing deferred** (needs Subscriptions R1A-P6); this schema is sufficient for it later.

---

## 5. Admin additions (`/admin/partners`)

- **List** with status filter + pending-count badge in the admin sidebar (same live-badge pattern as taxpayer-profiles, `refetchInterval: 60_000`).
- **Detail**: profile fields, partner code, grants table (business / status / dates), referred businesses, grant-event log.
- **Actions**: approve (generates code) · reject with mandatory Persian reason · suspend/unsuspend (suspend hard-gates all `/partner/*` data access on the next request). Admin does **not** create/revoke grants on behalf of owners in v1 (merchant-in-control); grants are read-only in admin.
- Backend: `/admin/partners` router with `require_system_admin`, following `app/modules/admin` conventions.

---

## 6. Guide + school

- **Merchant scenario S9-07 «دادن دسترسی به حسابدار همکار»** in the existing `accounting` guide group (the upgrade of S9-05's CSV stopgap): settings → invite by کد همکار → partner reviews from their own panel → revoke anytime. Group description updated. Rides in the SAME commit as the merchant grant UI (no-drift rule).
- **Partner-scoped guide** (`partner-content.ts`, mirroring `admin-content.ts`): درخواست همکاری و کد همکار · پذیرش دعوت کسب‌وکار · مرور دفترها و تراز مشتری · خروجی CSV · خروج از یک کسب‌وکار.
- **School L22 — extend, don't duplicate:** one added concept beat + one example beat — instead of only sending CSVs, آقای توکلی invites his accountant as a «همکار» who reviews the books live from their own panel, and the owner can cut access anytime. Practice block gains the S9-07 scenario id.
- **Catalog** (`phase1_user_scenarios_v1.md`): S9-07 row, new actor «Partner (همکار)», terminology additions, count 70→71.

---

## 7. Contracts, migrations, tests

**Contracts FIRST** — every entry lands in `docs/api_contracts_v2_2.md` before its code commit: `PartnerMeResponse` (status discriminator) · `PartnerApplyRequest` · `PartnerPortfolioResponse` (aggregate card fields) · grant DTOs + merchant-side `POST /businesses/{id}/partners/invite` (by code) / `GET …/partners` / `DELETE …/partners/{grantId}` · partner-side `POST /partner/invites/{grantId}/accept|decline` · `/partner/businesses/{id}/accounting/*` + `/reports/*` (same response DTOs as the merchant namespaces, new paths) · `/admin/partners*` · wizard `partner_code` optional field + tenant `referred_by_partner_id`. **Adjacent fix:** the existing member-management endpoints have NO contract entries (gap found in exploration) — backfill in the same docs commit.

**Test plan (rides with each backend commit; + a pg-integration module like Batch B's invariant tests):**
- Grant lifecycle: invite → accept → active → revoke → **immediate 403/404 on the next request** (DB-live gate); re-invite reactivates the same row; decline; partner-side leave.
- Isolation: partner A never sees partner B's businesses; ungranted business ⇒ 404; partner token on merchant namespaces ⇒ unchanged 403s; member lists exclude partners; `seesAllTenantData`/D5 scope untouched (regression asserts).
- Toggle interaction per OD-3; journal generated on grant activation; partner-side regenerate works.
- Referral: valid code attributes; invalid code ⇒ inline field error; attribution immutable via API.
- Admin: approve generates a unique code; reject requires a reason; suspend gates instantly.
- Frontend: typecheck+build per commit; founder browser QA per protocol (no Playwright mid-task); merchant surfaces for partner-less businesses unchanged by construction.

---

## 8. OPEN DECISIONS (the key deliverable — founder resolves before build)

**OD-1 · Invite direction** — affects grant flow, merchant UI, partner portfolio
- **A (recommended): owner invites by «کد همکار»; partner must accept.** Merchant-in-control from the first second; the two-sided handshake prevents both spam-attaching businesses to a partner's portfolio and partners holding access they never agreed to service. Mirrors S8-01 mechanics.
- B: partner requests using a code the merchant reads out; owner approves. Same handshake, reversed initiative — more friction on the merchant (an approval queue they must notice).
- C: both directions. Most flexible; ~1.5× the flow/UI/test surface — defer B until demand appears.

**OD-2 · What a partner sees inside a granted business** — affects backend surface and phase size
- **A (recommended): accountant layer + read-only reports only** (journal/ledger/trial-balance/chart/CSV + the 5 report tabs). Matches "supervise, review, export, guide"; smallest safe surface; ships fast.
- B: A + read-only merchant operational pages (invoices/purchases/expenses lists + details). Better review context («این سند از کدام فاکتور است؟») but every module needs a partner-gated read path — roughly doubles backend scope. Natural R1C follow-up.
- C: limited edits with client approval (scope-freeze mentions it) — explicitly later; needs its own approval-workflow design.

**OD-3 · Grant vs the merchant's «نمای حسابدار» toggle** — affects gate logic + D1 generation triggers
- **A (recommended): active grant ⇒ partner access regardless of the merchant's toggle; grant activation triggers journal generation.** The grant is the owner's explicit consent; the toggle stays what D13 made it — the merchant's own view preference. Avoids «دسترسی دادم ولی حسابدارم چیزی نمی‌بیند».
- B: require the toggle ON too. One master switch, conceptually simpler — but couples two different consents and breaks the owner's mental model.
- C: granting auto-turns the toggle ON — rejected: silently changes what the *merchant* sees; violates merchant-in-control/pixel-parity.

**OD-4 · Partner onboarding path** — affects admin workload + the growth funnel
- **A (recommended): self-serve application + admin approval** (taxpayer-review pattern; scales with the channel ambition; admin-create stays available as a superset).
- B: admin-created only. Simplest/safest v1; every partner requires founder action — throttles the channel.
- C: auto-approve — rejected (partners get real client-data access).

**OD-5 · Partner FIRM (multi-user) now or later** — affects schema + grant semantics
- **A (recommended): individual partners only in v1; firm later as an aggregation layer.** Grants stay per-person **permanently** (professional auditability — you always know *which human* saw the books). A future `partner_orgs` table + nullable `org_id` on profiles adds firm-level portfolio/commission aggregation without ever migrating grants. `firm_name` free-text covers display today.
- B: model the firm entity now. Pays complexity today for a persona we haven't met yet.

**OD-6 · Referred-but-ungranted businesses in the portfolio** — privacy posture
- **A (recommended): name + activation status only** (exactly §4.1.4's scope: «لیست مشتریان معرفی‌شده، وضعیت فعال‌سازی» — no financial data).
- B: aggregate count only («۴ کسب‌وکار معرفی‌شده»). Max privacy; weakens the referral feedback loop.
- C: nothing until commission ships. Kills "brings clients" visibility entirely.

**OD-7 · Invite key: «کد همکار» vs mobile** — minor
- **A (recommended): partner code.** Deliberate, typo-safe, doesn't leak whether a mobile belongs to a partner, and doubles as the referral code — one artifact to share.
- B: mobile (like member invite). Familiar, but enables probing («این شماره حسابدار است؟») and conflates member/partner mental models.

**OD-8 · Ungranted business ⇒ 404 vs 403** — minor, security posture
- **A (recommended): 404** — prevents business-id enumeration by approved partners. (Members keep their existing 403 semantics; this applies only to the partner namespace.)

**OD-9 · Where the merchant manages partner access** — minor, UX
- **A (recommended): a settings card «دسترسی حسابدار همکار» directly under the «نمای حسابدار» card** (one thematic "accountant" cluster; settings is already owner territory).
- B: a section in `/app/members`. Risks conflating partners with members — the exact confusion the separate table avoids.

---

## Estimated commits: **15** (7 backend · 7 frontend · 1 ops)

Each backend commit: Docker rebuild `--no-cache` → migrate → pytest green vs baseline. Each frontend commit: typecheck+build clean. Guide no-drift rides with its UI commit. Local only — no push until founder GO.

| # | Repo | Commit |
|---|---|---|
| 1 | backend | **B1** docs: full partner contract entries in `api_contracts_v2_2.md` + member-mgmt contract backfill + terminology |
| 2 | backend | **B2** M1 `partner_profiles` + partner module skeleton: `GET /partner/me` (status discriminator), `POST /partner/apply`, `require_approved_partner` + tests |
| 3 | backend | **B3** M2 grants + events; merchant grant endpoints (invite-by-code / list / revoke) + partner invite endpoints (accept / decline / leave) + lifecycle & isolation tests |
| 4 | backend | **B4** portfolio endpoint (aggregate cards) + `/partner/businesses/{id}/accounting/*` reads + CSV (reusing accounting application fns) + journal-on-grant-activation + tests |
| 5 | backend | **B5** `/partner/businesses/{id}/reports/*` reads (reusing report services) + tests |
| 6 | backend | **B6** M3 `tenants.referred_by_partner_id` + wizard `partner_code` capture + referred list + tests |
| 7 | backend | **B7** `/admin/partners` list/detail/approve/reject/suspend + tests |
| 8 | frontend | **F1** shell: `_partner.tsx` + `_partner.partner.tsx` (5-state preflight), PartnerSidebar, `/partner*` login whitelist, merchant footer link |
| 9 | frontend | **F2** application form (`none/pending/rejected` states) + `/partner/profile` (code display/share) |
| 10 | frontend | **F3** portfolio dashboard + invite accept/decline |
| 11 | frontend | **F4** drill-in: 4 accountant pages + reports tab (partner API module; shared presentational components with the Batch B pages) |
| 12 | frontend | **F5** merchant settings card «دسترسی حسابدار همکار» + wizard «کد همکار» field + **S9-07 walkthrough (same commit)** |
| 13 | frontend | **F6** admin partners UI (list/detail/approve/reject + pending badge) |
| 14 | frontend | **F7** partner-scoped guide + school L22 extension |
| 15 | ops | **O1** catalog (S9-07, actor row, terminology, count 70→71) + progress.md + decisions log |

**Dependencies:** B2→B3→(B4∥B5) · B6/B7 independent after B2 · F1 after B2 · F3 after B3 · F4 after B4+B5 · F5 after B3+B6 · F6 after B7 · F2/F7 flexible.

## Verification (end of batch)
- Backend suite green vs the 747/7 baseline + new partner tests + pg-integration grant-lifecycle module (skips without DB, like Batch B).
- curl proofs with three tokens (owner / partner-with-grant / partner-after-revoke): grant lifecycle end-to-end; revoke-immediacy; 404 on ungranted; merchant-ns 403s unchanged.
- Frontend typecheck+build at every commit; founder browser QA (incognito · 390px+desktop · light+dark): partner shell all 5 states, portfolio, drill-in, merchant grant card, admin review flow.
- Merchant pixel parity for partner-less businesses is structural (no merchant surface changes except the additive settings card + optional wizard field).
