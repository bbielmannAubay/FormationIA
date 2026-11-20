---
name: sdd-spec
description: SDD step 1 - register and validate the user's specification (context & objective, numbered testable rules, out of scope, acceptance criteria, test plan) in specs/<slug>/spec.md, report gaps, and get the user's approval. Use when starting spec-driven development or when asked to check/validate a spec. Argument is the feature slug (optionally followed by a spec file path).
allowed-tools: Agent, AskUserQuestion, Read, Glob, Grep, Write, Edit
---

# SDD step 1: Specification

Arguments: `$ARGUMENTS` (slug, optional path to the user's spec). If no slug, ask for one (kebab-case).

The spec is written by the user. You never rewrite or "improve" it. Never guess: gaps become questions to the user.

## Procedure
1. Locate the spec: path given, existing `specs/<slug>/spec.md`, or text pasted by the user. If none, show `~/.claude/skills/sdd-spec/spec-template.md` and ask the user to provide their spec. Do not draft it yourself. If the user only has a rough idea or ticket, point them to `/sdd-write-spec <slug>`, which helps them write it by interview.
2. Save/keep it at `specs/<slug>/spec.md` (create the folder). Make sure the frontmatter has `status: draft`; if the file has none, add only that frontmatter and leave the body untouched. If the file exists with `status: approved`, ask before touching it.
3. Run the `sdd-spec-reviewer` agent with the full spec text and relevant project rules (CLAUDE.md).
4. Show the verdict, gaps and questions, condensed.
5. Gate (AskUserQuestion): "I fixed/updated the spec, re-check" / "Approve as is" / "Stop". On re-check, re-read the file and go back to step 3. Approving with remaining BLOCKER gaps requires an explicit second confirmation.
6. On approval, set frontmatter to `status: approved` and `approved: <today's date>` (only change the frontmatter). Tell the user the next step is `/sdd-plan <slug>`. Do not start it.
