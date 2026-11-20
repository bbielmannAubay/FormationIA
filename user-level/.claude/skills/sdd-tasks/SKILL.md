---
name: sdd-tasks
description: SDD step 3 - break an approved spec and plan into small, ordered, testable tasks traced to the rules (R#) in specs/<slug>/tasks.md and get the user's approval. Refuses to run if the plan is not approved. Argument is the feature slug.
allowed-tools: Agent, AskUserQuestion, Read, Glob, Grep, Write, Edit
---

# SDD step 3: Break down into tasks

Arguments: `$ARGUMENTS` (slug). If missing and only one folder exists under `specs/`, propose it; otherwise ask.

## Procedure
1. **Gate check**: `specs/<slug>/spec.md` and `specs/<slug>/plan.md` must both exist with `status: approved`. Otherwise stop and name the step to run (`/sdd-spec` or `/sdd-plan`).
2. Run the `sdd-task-breaker` agent with the full spec and full plan texts and relevant project rules.
3. Resolve its open questions with the user (AskUserQuestion, recommended default first), re-run if needed.
4. Check yourself that the coverage matrix includes every R# of the spec and no task lacks an R#. If not, re-run the agent with the gap.
5. Write `specs/<slug>/tasks.md` with frontmatter `status: draft`. Show the task list and coverage matrix condensed.
6. Gate (AskUserQuestion): "Approve" / "Request changes" (re-run with the changes) / "Stop".
7. On approval set `status: approved` and `approved: <today's date>`. Tell the user the next step is `/sdd-implement <slug>`. Do not start it.
