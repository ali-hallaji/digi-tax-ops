Review the current git diff only.

Read:
1. AGENTS.md
2. docs/current_phase.md
3. docs/progress.md
4. docs/architecture_decisions.md

Check for:
- Compose/Nginx/script correctness
- env hygiene and no secrets
- accidental backend/frontend app logic edits
- incorrect frontend stack references
- unnecessary Kubernetes or observability additions
- service dependency risks

Return only critical issues, missing env vars, service dependency risks, and minimal patch recommendations.
