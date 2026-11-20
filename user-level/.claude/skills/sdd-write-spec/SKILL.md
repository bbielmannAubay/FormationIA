---
name: sdd-write-spec
description: Help the user write specs/<slug>/spec.md from a free-form description (idea, ticket, issue, notes) by interviewing them, following the SDD spec template and the /sdd-spec conventions. Use when the user wants to draft, write or build a spec for spec-driven development. Argument is the feature slug, optionally followed by a path to the description.
allowed-tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
---

# Write a spec.md (SDD, before step 1)

Arguments: `$ARGUMENTS` (`<slug> [path-to-description]`).

You help the user write their spec; the content is theirs. **Never guess, never invent**: every rule, criterion, test, scope exclusion and edge case must come from the user's description or from their answers. Missing information becomes a question (options with a recommended one first), never a filled-in value. This skill never approves the spec and never runs `/sdd-spec`.

## Procedure
1. Slug: kebab-case; ask if missing. If `specs/<slug>/spec.md` exists, ask before overwriting and offer to stop and use `/sdd-spec <slug>` instead.
2. Description: read the given path, else use the text pasted by the user; if there is none, ask for it.
3. Read `~/.claude/skills/sdd-spec/spec-template.md` and follow its structure exactly (do not copy it elsewhere). You may Grep/Glob the project only to check that APIs/modules named in the description exist; report mismatches to the user, do not fix them.
4. Build a working outline of the 5 sections using only what the description states, remembering the source of each item. List the gaps per section: unclear objective; rules that are vague or untestable (words like "fast", "properly", "etc.", "should handle"); missing out of scope; rules without an acceptance criterion or test; no edge cases (empty/null, bounds, errors, invalid input).
5. Interview with AskUserQuestion (max 4 questions per call), section by section, until no gap remains or the user says to leave it. Ask for concrete input -> output examples. Reword a vague statement only after the user confirms the precise wording. Anything left unresolved is written as `TODO: <question>`.
6. Write `specs/<slug>/spec.md` in the template structure with frontmatter `status: draft` only (no `approved:`): `# Spec: <name>`, `## 1. Context & objective`, `## 2. Expected behaviors` (`- R1: ...`, numbered without gaps), `## 3. Out of scope`, `## 4. Acceptance criteria` (`- AC1 (R1): given <input>, then <output>.`), `## 5. Test plan` (`- R1: <test(s)>`, plus `- Edge cases: ...`).
7. Self-check against what the reviewer will check: R numbering, every R has at least one AC and one test, every test traces to an R, out of scope not empty, edge cases listed. Report remaining `TODO`s and weak spots.
8. Tell the user to review/edit the file, then run `/sdd-spec <slug>` to validate and approve it. Do not run it yourself.
