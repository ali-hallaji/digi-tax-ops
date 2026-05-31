# Codex-First Workflow

## Golden Rules
1. Keep backend, frontend, and ops in separate repos.
2. Start each Codex session by reading `AGENTS.md`, `docs/current_phase.md`, and `docs/progress.md`.
3. Read `docs/architecture_decisions.md` only when the task touches architecture or boundaries.
4. Work on one task per session unless the user explicitly broadens scope.
5. Read the smallest relevant docs/code slice; do not scan the whole repo by default.
6. Ask Codex to list planned files before editing unless the task already approved implementation.
7. Review `git diff`, not the whole repo.
8. Update `docs/progress.md` after meaningful changes.
9. Keep active docs concise; do not add long architecture dumps.

## Standard Task Loop

### Plan
```txt
Read AGENTS.md, docs/current_phase.md, and docs/progress.md.
We are implementing only <task>.
Summarize the task in 10 lines max.
List files you plan to create or modify.
Do not edit files until approved.
```

### Implement
```txt
Proceed with the approved files only.
Keep the patch minimal.
Run relevant Docker Compose or shell checks if configured.
Update docs/progress.md.
Return changed files, validation, and risks.
```

## Validation And Network Rules
- Use Docker/Compose for backend and ops validation unless explicitly approved otherwise.
- Do not use Python, Poetry, or Python package installation on the host.
- Do not rebuild Docker images for every small change when existing containers or volume mounts are enough.
- Rebuild only for dependency, Dockerfile, base image, or environment/build config changes.
- Do not embed proxy URLs, ports, credentials, tokens, or network workarounds.
- Proxy values may come only from the developer shell, ignored local env files, or explicit one-off user-provided build args.

### Review
```txt
Review the current git diff only.
Check AGENTS.md, docs/current_phase.md, docs/progress.md, and docs/architecture_decisions.md.
Return critical issues, env/secrets risks, service dependency risks, and minimal patch recommendations.
```

## Reset Prompt
```txt
Stop. Re-read AGENTS.md, docs/current_phase.md, and docs/progress.md.
State the exact task boundary.
Continue only within that boundary.
```
