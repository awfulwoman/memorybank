# Ralph Agent Instructions — MemoryBank

You are an autonomous coding agent building MemoryBank, a self-hosted shared expense splitting app.

## Tech Stack

- **Backend:** Django + Django REST Framework, SQLite
- **Frontend:** Vue 3 (Composition API), Vue Router, Pinia
- **Deployment:** Docker Compose (backend, frontend, db volumes)

## Your Task

1. Read `prd.json` in this directory
2. Read `progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, create it from main.
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (typecheck, lint, test as applicable)
7. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
8. Update `prd.json` to set `passes: true` for the completed story
9. Append your progress to `progress.txt`

## Progress Report Format

APPEND to progress.txt (never replace, always append):
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

## Consolidate Patterns

If you discover a **reusable pattern**, add it to `## Codebase Patterns` at the TOP of progress.txt (create if missing). Only general, reusable patterns — not story-specific details.

## Update CLAUDE.md Files

Before committing, check if edited directories have learnings worth preserving in nearby CLAUDE.md files:
- API patterns or conventions specific to that module
- Gotchas or non-obvious requirements
- Dependencies between files
- Testing approaches

Do NOT add story-specific details, debugging notes, or info already in progress.txt.

## Quality Requirements

- ALL commits must pass quality checks (typecheck, lint, test)
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

## Browser Testing (Frontend Stories)

For any story that changes UI, verify in browser if browser tools are available:
1. Navigate to the relevant page
2. Verify UI changes work as expected
3. Note in progress if manual verification needed

## Stop Condition

After completing a story, check if ALL stories have `passes: true`.

If ALL complete: reply with `<promise>COMPLETE</promise>`

If stories remain with `passes: false`: end normally (next iteration picks up).

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read Codebase Patterns in progress.txt before starting
