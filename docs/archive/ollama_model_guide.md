# HISTORICAL

Archived on 2026-05-31. This file is old model/editor workflow guidance and is not active. Use `AGENTS.md`, `docs/current_phase.md`, `docs/progress.md`, and `docs/architecture_decisions.md` for the current Codex workflow.

# Ollama Cloud Model Guide for Zed v1.3

Use Zed primarily with Ollama Cloud to keep costs predictable. Use ChatGPT Pro for architecture review, final decisions, and complex debugging summaries.

## Recommended model roles

### Backend Builder
Use:
```txt
qwen3-coder:480b-cloud
```
Best for FastAPI, SQLAlchemy, workers, tests, database design, tax transport code, and repo-scale edits. It has strong coding-agent behavior and long context.

Fallback if slower/costly:
```txt
qwen3-coder-next:cloud
```
Use for smaller backend tasks, refactors, test writing, and simpler endpoints.

### Frontend Builder
Use:
```txt
qwen3-coder-next:cloud
```
Best speed/cost balance for Vue/Quasar components, pages, stores, forms, and API clients.

Use `qwen3-coder:480b-cloud` when the frontend task is complex, such as invoice wizard state machines, dynamic validation UI, or central admin dashboards.

### Reviewer
Use:
```txt
qwen3-coder:480b-cloud
```
Ask it to review only changed files and compare them against AGENTS.md and the current phase checklist.

### Fast small edits
Use:
```txt
qwen3-coder-next:cloud
```
For small bug fixes, renames, lint errors, and simple component changes.

### Reasoning / product / architecture
Use ChatGPT Pro outside Zed. Do not use IDE agents for major architecture changes.

## Practical model routing

```txt
Ops repo:
  qwen3-coder-next:cloud for Docker/Nginx skeleton.
  qwen3-coder:480b-cloud for review.

Backend repo:
  qwen3-coder:480b-cloud for phase implementation.
  qwen3-coder-next:cloud for small fixes.

Frontend repo:
  qwen3-coder-next:cloud for normal UI work.
  qwen3-coder:480b-cloud for complex UX/state flows.
```

## Zed settings behavior
Keep context small. Open only the repo you are editing. Do not open the whole workspace containing all three repos unless doing manual inspection.

## Prompt rule
Always tell the model:

```txt
Read AGENTS.md first. Then read only the specific docs for this phase. Do not scan the whole repo unless necessary.
```

## Cost control
Use the large model for planning and first implementation pass. Use the faster model for lint fixes. Do not ask the large model to repeatedly re-read large docs.
