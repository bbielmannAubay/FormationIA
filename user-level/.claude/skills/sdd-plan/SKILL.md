---
name: sdd-plan
description: SDD step 2 - from an approved spec, produce the technical plan (architecture, stack, contracts between components, rule-to-component mapping) in specs/<slug>/plan.md and get the user's approval. Refuses to run if the spec is not approved. Argument is the feature slug.
allowed-tools: Agent, AskUserQuestion, Read, Glob, Grep, Write, Edit
---

# SDD step 2: Plan

Arguments: `$ARGUMENTS` (slug). If missing and only one folder exists under `specs/`, propose it; otherwise ask.

Never guess: open questions go to the user with a recommended default.

## Procedure
1. **Gate check**: read `specs/<slug>/spec.md`. If missing or its frontmatter is not `status: approved`, stop and tell the user to run `/sdd-spec <slug>` first.
2. Run the `sdd-planner` agent with the full spec text and relevant project rules (CLAUDE.md, restrictions on files/refs to read).
3. If the result has "Open questions" other than None: ask the user (AskUserQuestion, recommended default first), then re-run the planner with the answers.
4. Write the result to `specs/<slug>/plan.md` with frontmatter `status: draft`. Show it condensed (architecture, contracts, R -> component mapping, files, commands).
5. Gate (AskUserQuestion): "Approve" / "Request changes" (collect the changes, re-run the planner with the previous plan and the requested changes, loop) / "Stop".
6. On approval set `status: approved` and `approved: <today's date>`. If the spec was edited after approval, warn that the plan may be stale. Tell the user the next step is `/sdd-tasks <slug>`. Do not start it.
