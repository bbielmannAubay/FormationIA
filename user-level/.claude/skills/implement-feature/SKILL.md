---
name: implement-feature
description: Implement a new feature on any project through a pipeline of specialised sub-agents - plan, tests first, code, verification, then an independent review (architecture, quality, security) with a bounded fix loop. Use when asked to implement, add, build or develop a feature or enhancement, even if the user doesn't name the workflow. Argument is the feature description.
allowed-tools: Agent, AskUserQuestion, Read, Glob, Grep, Bash, Write
---

# Implement a feature

Feature: `$ARGUMENTS`. If empty or too vague to plan, ask the user before anything else.

Never guess: missing information becomes a question to the user (or a proposal with a recommendation). Sub-agents cannot spawn sub-agents, so you (the main conversation) orchestrate every step below, sequentially. Each sub-agent only knows what you put in its prompt: pass the full plan and any needed context, not a reference to it.

Project rules always win (CLAUDE.md, restrictions on which refs/files may be read, etc.): repeat relevant ones in each sub-agent prompt.

## 1. Plan: `feature-planner` (opus, read-only)
Prompt: the feature description, target area if known, relevant project rules. If the result has "Open questions", ask the user (AskUserQuestion, recommended default first), then re-run the planner with the answers.

## 2. Gate
Show the user the plan (condensed: requirements, files, test strategy, commands). Wait for approval or edits. Do not continue without it. Fold edits into the plan text.

## 3. Tests: `feature-test-writer` (red phase)
Prompt: the approved plan. Check the report: tests exist and fail for the right reason. If it returns questions, resolve them with the user.

## 4. Code: `feature-coder`
Prompt: the approved plan + test files list. Check: tests green, lint/typecheck/format run. If it reports a test believed wrong, decide with the user, then send it back to `feature-test-writer` rather than letting the coder edit tests.

## 5. Review: `feature-reviewer` (opus, high effort, read-only + can run the project)
Prompt: the plan, the changed files (`git status` / `git diff`), the commands to run. Do not pass your own opinion of the code quality, to keep the review independent.

## 6. Fix loop (max 2 rounds)
While the verdict is `CHANGES_REQUESTED` and rounds < 2:
- Send BLOCKER and MAJOR findings (verbatim) to `feature-coder`; test gaps go to `feature-test-writer` first.
- Re-run `feature-reviewer` with the previous findings to re-check.
After 2 rounds, stop and report what remains. MINOR findings are only listed.

## 7. Reply
Short summary: feature, files changed, tests added, verification results (from the reviewer's last run), remaining findings, and open questions. Do not commit or push unless the user asks.
