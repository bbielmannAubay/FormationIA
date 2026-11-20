---
name: sdd
description: Spec-driven development orchestrator. Runs the 4 gated steps - specification, plan, tasks, implement - for a feature, resuming from the first step not yet approved. Use when the user wants to build a feature spec-first or says "SDD". Argument is the feature slug (optionally a spec file path).
allowed-tools: Skill, AskUserQuestion, Read, Glob, Bash
---

# Spec-Driven Development

Arguments: `$ARGUMENTS`. If no slug, list `specs/*/` folders and ask which feature (or a new slug).

Process: **1 spec -> 2 plan -> 3 tasks -> 4 implement**. Each step must be approved by the user before the next one starts. The spec comes from the user.

## Procedure
1. Determine state in `specs/<slug>/` from the frontmatter `status:` of `spec.md`, `plan.md`, `tasks.md` (missing = not started; `draft` = not approved).
   If there is no spec yet and the user only has a rough idea/ticket, suggest `/sdd-write-spec <slug>` first.
2. Show a one-line state, e.g. `spec approved | plan draft | tasks -`.
3. Invoke (Skill tool) the skill of the **first non-approved step**, forwarding the slug and spec path if any: `sdd-spec`, `sdd-plan`, `sdd-tasks` or `sdd-implement` (the latter until every task is `[x]` and the conformance audit is done).
4. When that step ends approved, ask (AskUserQuestion) whether to continue to the next step or stop; if continue, go back to 1. Never chain two steps without this answer. Never bypass a step's own gate.
5. If the user wants to change an earlier artifact, note that downstream files may become stale and offer to re-run those steps.
