# HISTORICAL

Archived on 2026-05-31. This file is old model/editor workflow guidance and is not active. Use `docs/token_saving_workflow.md` for the current Codex workflow.

# Token-Saving Workflow for Zed/Ollama Agents

## Golden rules
1. Keep backend, frontend, and ops in separate repos.
2. Open only the repo you are working on.
3. Put rules in files; do not paste the whole architecture every time.
4. Use short phase prompts that reference files by path.
5. Ask the agent to list planned files before editing.
6. Tell the agent to modify only the current phase.
7. Use a reviewer prompt with `git diff`, not the whole repo.
8. Commit after each small milestone.
9. Never ask: "build the whole project".
10. Never let agents change architecture silently.

## Standard task loop

### Step A — planning prompt
```txt
Read AGENTS.md and docs/<phase-doc>.md.
We are implementing only Phase X / Task Y.
Summarize the task in 10 lines max.
List files you plan to create/modify.
Do not edit files yet.
```

### Step B — approval
Review its plan. If acceptable, say:

```txt
Proceed with the listed files only.
Implement the task.
Write/update tests.
Run lint/tests if available.
Update docs/progress.md.
Return changed files, commands run, test results, and remaining risks.
```

### Step C — review prompt
```txt
Review the current git diff only.
Check against AGENTS.md, docs/<phase-doc>.md, and docs/phase_checklists.md.
Do not rewrite everything.
Return only: critical issues, minor issues, missing tests, and recommended patch.
```

### Step D — fix prompt
```txt
Apply only the minimal patch for the review issues.
Do not refactor unrelated code.
Run tests again.
```

## Context packing rule
When the agent gets confused, do not paste more docs. Instead ask:

```txt
Stop. Re-read AGENTS.md and docs/current_phase.md. State the exact boundary of this task. Then continue only within that boundary.
```

## Daily workflow
At the end of each day, ask the agent to update:

```txt
docs/progress.md
```

Format:

```txt
Completed:
- ...

Changed files:
- ...

Tests:
- ...

Known issues:
- ...

Next task:
- ...
```
