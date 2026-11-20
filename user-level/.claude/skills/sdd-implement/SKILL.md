---
name: sdd-implement
description: SDD step 4 - implement an approved task list one task at a time through the implement-feature pipeline (tests first, code, review, fix loop), tick each task in tasks.md, then run a spec-conformance audit. Refuses to run if tasks are not approved. Argument is the feature slug (optionally a task id like T3).
allowed-tools: Agent, Skill, AskUserQuestion, Read, Glob, Grep, Bash, Write, Edit
---

# SDD step 4: Implement

Arguments: `$ARGUMENTS` (slug, optional task id). Sub-agents cannot spawn sub-agents: you orchestrate everything from this conversation. Project rules (CLAUDE.md, ref/file restrictions) win and must be repeated in each sub-agent prompt. Never guess; never commit or push unless the user asks.

## Procedure
1. **Gate check**: spec, plan and tasks in `specs/<slug>/` must all be `status: approved`. Otherwise stop and name the step to run.
2. Read all three files. Pick the task: the one given, else the first unchecked (`[ ]`) task whose dependencies are done. Tell the user which one.
3. Invoke the `implement-feature` skill (Skill tool) in **pre-approved plan mode**, passing: the spec path, the plan path, the task id/text, and the spec's Out of scope section. It runs tests first (`feature-test-writer`), code (`feature-coder`), review (`feature-reviewer`) and the bounded fix loop, without re-planning.
4. When it reports success (tests green, review approved or remaining findings listed), tick the task `[x]` in tasks.md and summarize: files changed, tests, verification results, remaining findings.
5. Gate (AskUserQuestion): "Next task" / "Run all remaining tasks (still stop on any failure)" / "Stop here". Never start the next task without this answer.
6. After the last task: run the `sdd-conformance-checker` agent with spec, plan, tasks, `git status`/`git diff` scope and the plan's commands. Show the conformance matrix and deviations. If `DEVIATIONS`, ask the user how to handle each (fix via another implement-feature round, amend the spec through `/sdd-spec`, or accept).
7. Final reply: tasks done, verdict, open issues. Do not commit.
