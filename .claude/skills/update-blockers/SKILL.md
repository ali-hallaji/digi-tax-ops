---
description: Add, update, or close a blocker entry in docs/progress.md Active Blockers.
---

# update-blockers

Run when: a blocker is discovered, resolved, or its status changes.

## Steps

1. Read the current `docs/progress.md` Known Risks / Active Blockers section.

2. Determine action:
   - **Add:** new blocker discovered in this session.
   - **Update:** blocker description or severity changed.
   - **Close:** blocker confirmed resolved.

3. Blocker entry format:
   ```
   - **[CATEGORY]** <one-line description of the blocker and its impact>.
   ```
   Categories: `[DEPLOY]`, `[INFRA]`, `[BACKEND]`, `[FRONTEND]`, `[CONTRACT]`, `[FUTURE]`.

4. Edit `docs/progress.md`:
   - Add new blocker under `## Known Risks` (ops convention) or create `## Active Blockers` if needed.
   - Update `Last updated:` date.
   - Annotate resolved blockers with resolution note.

5. For cross-repo blockers (e.g. a backend migration required for ops deploy):
   - Record it here with the category matching the repo that must fix it.
   - Note the dependency chain.

6. Never silently drop a blocker — always explain resolution.

## Output

```
## Blocker Update — digi-tax-ops

**Action:** Add | Update | Close
**Blocker:** <category + description>
**Reason / resolution:** <why it was added, updated, or closed>

**Result:** PASS | NEEDS FIXES
```
