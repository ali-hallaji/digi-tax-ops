# DigiTax Tooling Inventory

Last updated: 2026-06-17  
Scope: read-only report — no changes made.

---

## Summary

| Repo | Skills | Agents | Commands | AGENTS.md |
|---|---|---|---|---|
| digi-tax-backend | 5 | 3 | 0 | ✓ |
| digi-tax-frontend | 6 | 4 | 0 | ✓ |
| digi-tax-ops | 5 | 2 | 0 | ✓ |
| **Total** | **16** | **9** | **0** | **3** |

No slash-commands (`.claude/commands/`) were found in any repo. Skills are invoked via
`/skill-name`; agents are spawned by name.

### Top 5 Issues

1. **Stale v3 doc reference in 2 frontend skills** — `start-digi-session` and
   `implement-frontend-task` both direct the session to read
   `docs/product_strategy_and_phase_roadmap_v3.md`, which was archived in R1A-P0.5.
   The next frontend session will try to read a file that has moved.

2. **Browser QA MCP mismatch** — `browser-qa-digi` skill and `browser-qa-auditor` agent
   both reference `mcp__claude-in-chrome__*` tools. The only MCP configured in
   `digi-tax-frontend/.mcp.json` is **Playwright** (`@playwright/mcp@latest`). The
   claude-in-chrome MCP is not registered; browser QA as written cannot run.

3. **Stale resolved-blocker text in backend `blocker-ledger-auditor`** — The agent still
   lists "OTP in-memory storage (dev-only limitation)" and "PDF 501 blocker (WeasyPrint
   not yet approved)" as risks to flag. Both are resolved: OTP → Redis (R1A-P0);
   WeasyPrint PDF live (R1A-P2.7). The agent will generate false alarms.

4. **Stale CORS note in ops `smoke-check-digi`** — The skill says "CORS is currently
   temporary wildcard for dev/staging; confirm it is not restricted before running against
   production." After R1A-P0, CORS is env-driven (`BACKEND_CORS_ORIGINS`), not a
   permanent wildcard. The note is misleading and slightly inverted.

5. **`update-blockers` is near-identical across all 3 repos** — 95% shared logic; only
   the section header name and category list differ slightly. Merge candidate.

---

## Skills

| Name | Repo | Purpose | Stale refs | Alignment | Verdict |
|---|---|---|---|---|---|
| `start-digi-session` | backend | Orient session: read CLAUDE.md, AGENTS.md, current_phase, progress, api_contracts; inject git state; report blockers | None | ✓ Aligned | KEEP |
| `implement-backend-task` | backend | Pre-impl checklist (blockers, phase boundary, contract); enforce money/tenant/auth/module/migration rules; run review-digi-diff post | None | ✓ Aligned | KEEP |
| `check-openapi-contract` | backend | Verify implemented routes and schemas match api_contracts_v2_2.md; check OpenAPI declarations, Decimal, tenant safety | None | ✓ Aligned | KEEP |
| `review-digi-diff` | backend | Pre-commit review: contract compliance, Decimal safety, tenant isolation, auth, module boundaries, migrations, tests | None | ✓ Aligned | KEEP |
| `update-blockers` | backend | Add/update/close blocker entries in docs/progress.md Active Blockers | None | ✓ Aligned | MERGE — near-identical to frontend/ops versions; keep per-repo for now, future unification possible |
| `start-digi-session` | frontend | Orient session: reads CLAUDE.md, AGENTS.md, current_phase, progress, **v3 doc** (line: `docs/product_strategy_and_phase_roadmap_v3.md`), phase_roadmap, product_scope, api_contracts, execution plan | **STALE: reads archived v3 doc** | ✗ v3 ref must be updated to v4.2 path | UPDATE |
| `implement-frontend-task` | frontend | Pre-impl checklist including mandatory read of **v3 doc** and "Trust the v3 strategy doc"; enforces API/auth/UX/component/invoice rules; run review-digi-diff post | **STALE: reads archived v3 doc (step 0 x2)** | ✗ v3 refs must be updated | UPDATE |
| `check-api-contract` | frontend | Verify frontend API modules match backend contracts; check endpoint paths, request/response shapes, normalizeListResponse, Decimal types, tenant safety | None | ✓ Aligned | KEEP |
| `review-digi-diff` | frontend | Pre-commit review: contract alignment, auth/session, Persian RTL/UX, component structure, invoice lifecycle guard, commit message check | None | ✓ Aligned | KEEP |
| `browser-qa-digi` | frontend | Live browser QA using claude-in-chrome MCP: inspect RTL, console errors, network, print flow, Moadian placeholder, readiness UX | **MCP MISMATCH: references `mcp__claude-in-chrome__*` but Playwright is configured** | ✗ Wrong MCP tools | UPDATE — rewrite for Playwright, or register claude-in-chrome MCP |
| `update-blockers` | frontend | Add/update/close blocker entries in docs/progress.md Active Blockers | None | ✓ Aligned | MERGE — near-identical to backend/ops versions |
| `start-digi-session` | ops | Orient session: reads CLAUDE.md, AGENTS.md, current_phase, progress; inject git state; report blockers and hard constraints | None | ✓ Aligned | KEEP |
| `deploy-digi-test` | ops | Controlled deploy sequence: check blockers, validate Compose, start infra+api, run migrations, start frontend, preflight | None | ✓ Aligned | KEEP |
| `smoke-check-digi` | ops | Run smoke_test.sh after deploy; manual fallback checks; logs review | **STALE: "CORS is currently temporary wildcard" — inaccurate post-R1A-P0** | ✗ Misleading CORS note | UPDATE |
| `review-ops-diff` | ops | Pre-commit review: cross-repo boundary, Compose/Docker safety, env safety, script syntax, API contract snapshot freshness | None | ✓ Aligned | KEEP |
| `update-blockers` | ops | Add/update/close blocker entries in docs/progress.md Known Risks / Active Blockers | None | ✓ Aligned | MERGE — near-identical to backend/frontend versions |

---

## Subagents

| Name | Repo | Purpose | Stale refs | Alignment | Verdict |
|---|---|---|---|---|---|
| `backend-contract-auditor` | backend | Read-only: audit routes/schemas/migrations/tests for contract compliance, Decimal safety, tenant isolation, module boundaries, submission safety | None | ✓ Aligned; tools correctly restricted to Read+Bash | KEEP |
| `api-contract-guardian` | backend | Read-only: compare backend Pydantic response models vs api_contracts_v2_2.md; catch undocumented fields, envelope key issues, Decimal serialization issues | None | ✓ Aligned; tools Read+Bash | KEEP |
| `blocker-ledger-auditor` | backend | Read-only: classify blockers in docs/progress.md; flags OTP in-memory, CORS wildcard, PDF 501, crypto scope as specific risks | **STALE: OTP in-memory resolved (R1A-P0); PDF 501 resolved (R1A-P2.7); CORS wildcard note partially stale** | ✗ Will generate false alarms on resolved items | UPDATE |
| `api-contract-guardian` | frontend | Read-only: verify frontend API modules vs api_contracts_v2_2.md; invented endpoints, request/response fields, missing normalizations, Decimal types | None | ✓ Aligned; tools Read+Bash | KEEP |
| `blocker-ledger-auditor` | frontend | Read-only: classify blockers in docs/progress.md Active Blockers; report which block the planned task | None | ✓ Aligned; tools Read only | KEEP |
| `browser-qa-auditor` | frontend | Read-only/inspect-only browser QA: RTL, mobile, font, console/network, JSON leakage, disabled/enabled correctness, Moadian submission risk, print/PDF, readiness UX | **MCP MISMATCH: lists `mcp__claude-in-chrome__*` in tools frontmatter; Playwright is the configured MCP** | ✗ Agent declaration specifies wrong browser tools | UPDATE — rewrite tool list for Playwright, or register claude-in-chrome |
| `frontend-ux-auditor` | frontend | Read-only: audit changed files for Persian RTL, mobile layout, loading/empty/error states, font consistency, menu clarity, no raw backend errors | None | ✓ Aligned; tools Read+Bash | KEEP |
| `blocker-ledger-auditor` | ops | Read-only: classify blockers/risks in docs/progress.md; check runbook gaps (migration step, frontend rebuild, seed, smoke test); cross-repo migration dependencies; env drift | None | ✓ Aligned; tools Read only | KEEP |
| `ops-deploy-auditor` | ops | Read-only: audit docker-compose.yml, .env.example, migration steps, scripts, seed for deploy correctness and safety | None | ✓ Aligned; tools Read+Bash | KEEP |

---

## Commands

No `.claude/commands/` directories found in any repo. All skills are invoked via `/skill-name`
and all agents are spawned by name in prompts. **No commands to inventory.**

---

## MCP Status

| Repo | MCP Config | Servers Registered | Notes |
|---|---|---|---|
| digi-tax-backend | Not found | None | No browser or external MCP |
| digi-tax-frontend | `.mcp.json` ✓ | **Playwright** (`@playwright/mcp@latest`, stdio) | Only Playwright; no claude-in-chrome |
| digi-tax-ops | Not found | None | No MCP |

**Critical gap:** `browser-qa-digi` (skill) and `browser-qa-auditor` (agent) both reference
`mcp__claude-in-chrome__*` tools (tabs_context_mcp, tabs_create_mcp, navigate,
read_console_messages, read_network_requests, read_page, find, computer, get_page_text,
tabs_close_mcp). None of these are available — only Playwright is registered. Browser QA as
currently written **cannot execute** in this environment.

Resolution options (decision for founder):
- **Option A:** Rewrite `browser-qa-digi` and `browser-qa-auditor` to use Playwright MCP
  tools (`mcp__playwright__*`). Playwright is already registered.
- **Option B:** Register the claude-in-chrome MCP alongside Playwright. The skill and agent
  can then run as written.
- **Option C:** Keep browser QA as a manual-only step (human runs the browser, Claude Code
  reads network/console output from logs or pastes).

---

## Recommended Actions

Priority order — highest impact first:

### 1. UPDATE `digi-tax-frontend/.claude/skills/start-digi-session/SKILL.md` (HIGH)
**Reason:** Still instructs the session to read `docs/product_strategy_and_phase_roadmap_v3.md`,
which was archived in R1A-P0.5. The next frontend session will try to open a moved file.
**Fix:** Replace the v3 path with `../digi-tax-ops/docs/product_master_blueprint_v4_2.md`.

### 2. UPDATE `digi-tax-frontend/.claude/skills/implement-frontend-task/SKILL.md` (HIGH)
**Reason:** Step 0 (mandatory reading) references v3 doc twice, including the instruction
"Trust the v3 strategy doc." Both references are stale.
**Fix:** Replace v3 references with `../digi-tax-ops/docs/product_master_blueprint_v4_2.md`.

### 3. UPDATE `browser-qa-digi` skill + `browser-qa-auditor` agent to use Playwright (HIGH)
**Reason:** Both reference `mcp__claude-in-chrome__*` tools exclusively. The configured MCP
is Playwright. Browser QA is completely non-functional as written.
**Fix (Option A — recommended):** Rewrite tool calls to use `mcp__playwright__*` equivalents.
The Playwright MCP has page navigation, console, network, and screenshot capabilities.

### 4. UPDATE `digi-tax-backend/.claude/agents/blocker-ledger-auditor.md` (MEDIUM)
**Reason:** Specifically flags "OTP in-memory storage" and "PDF 501 blocker (WeasyPrint not
yet approved)" as risks — both resolved. Will generate noise in every backend session.
**Fix:** Remove those two items from the hard-coded risk list; keep the generic classification
logic and the crypto/submission scope guard (still relevant).

### 5. UPDATE `digi-tax-ops/.claude/skills/smoke-check-digi/SKILL.md` (MEDIUM)
**Reason:** "CORS is currently temporary wildcard for dev/staging; confirm it is not
restricted before running against production." Post R1A-P0, CORS is env-driven via
`BACKEND_CORS_ORIGINS`. The note implies wildcard is always in effect, which is wrong.
**Fix:** Replace with: "CORS is env-driven (`BACKEND_CORS_ORIGINS`). Confirm staging/prod
`.env` sets explicit origins — the default in `.env.example` is `*`."

### 6. MERGE `update-blockers` across repos (LOW)
**Reason:** Three near-identical copies (backend/frontend/ops) differ only in section header
names and category lists. Maintaining three copies risks drift.
**Fix (deferred):** Create a single shared skill in `digi-tax-ops/.claude/skills/` and have
per-repo wrappers override only the section name and categories. Low urgency — no functional
harm currently.

### 7. RETIRE browser-qa frequency concern (resolved — no action needed)
**Reason:** The founder flagged risk of browser QA running on every change. On review:
`review-digi-diff` (runs pre-commit) does NOT invoke `browser-qa-digi`. The browser QA
skill/agent is only triggered explicitly (`/browser-qa-digi` or named agent invocation).
The blueprint correctly scopes it to phase-end and explicit frontend phase DoD gates.
No change needed — the frequency concern does not apply to the current wiring.

---

No changes made — this is a report.
