---
description: Start a DigiTax ops session — orient, check blockers, confirm phase, report status.
---

# start-digi-session

Run at the beginning of every ops session before making any changes.

## Steps

1. Read orientation documents in order:
   - `CLAUDE.md` — ops constraints, hard rules, do-not lists
   - `AGENTS.md` — workflow rules
   - `docs/current_phase.md` — active phase and task boundary
   - `docs/progress.md` — completed items, **Active Blockers**, known risks

2. Inject live repo state:
   ```
   !`git status --short`
   !`git diff --name-only HEAD`
   ```

3. Report session context:

```
## Session Start — digi-tax-ops

**Current Phase:** <from docs/current_phase.md>
**Active Blockers:**
- <list each blocker from docs/progress.md, or "None">

**Uncommitted changes:**
<git status --short output>

**Ready to work on:** <confirm the task or ask for clarification>
```

4. If any blocker is relevant to the planned task, surface it explicitly before proceeding.

5. Do not begin changes until this report is complete.

## Hard Constraints (confirm before any session)

- Do not edit backend or frontend application code from this repo.
- Do not add Kubernetes, Prometheus, Grafana, MinIO, or other optional stacks by default.
- Do not commit secrets, proxy URLs, or credentials.
- All Python/backend validation runs through Docker/Compose — never host-level.

## Output

`PASS` — session context reported, blockers surfaced, ready to work.  
`NEEDS FIXES` — missing docs, unresolvable blocker, or ambiguous phase.
