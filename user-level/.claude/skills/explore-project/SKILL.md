---
name: explore-project
description: Explore a project and write a PROJECT_OVERVIEW.md report covering its architecture, how to launch it and how to run its tests. Splits the exploration across several project-explorer sub-agents when the repo is a monorepo, multi-language, or large. Use when asked to explore, map, onboard on or document a codebase. Optional argument is the project path (default is the current directory).
allowed-tools: Agent, Read, Glob, Grep, Bash, Write
---

# Explore a project

Target: `$ARGUMENTS` if given, otherwise the current working directory. Report: `<target>/PROJECT_OVERVIEW.md`.

Never guess: anything not verifiable from files is reported as "Not determined".

## 1. Reconnaissance (do this yourself, keep it cheap)
- `git -C <target> ls-files | wc -l` (fallback to Glob if not a git repo)
- Top-level listing; find manifests (package.json, pyproject.toml, pom.xml, build.gradle*, go.mod, Cargo.toml, *.csproj, composer.json, Gemfile…) and workspace files (pnpm-workspace.yaml, nx.json, turbo.json, lerna.json, Cargo/go workspaces).
- File counts per extension (to detect languages), e.g. `git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15`.
- Read the README top and root manifest only.

## 2. Decide the split
Fan out ONLY if at least one criterion holds; otherwise spawn a single `project-explorer` in `full` mode and stop after step 5.

| Criterion | Slicing |
|---|---|
| Monorepo (workspace config, or several package manifests) | one slice per package/app; group tiny ones |
| Several languages/ecosystems (e.g. backend + frontend) | one slice per stack |
| Large repo (> ~1,500 tracked files or > ~10 top-level source dirs) | one slice per major top-level directory |

Always add one extra slice for root-level tooling: CI, Dockerfiles, Makefile/scripts, root launch/test commands. Cap at ~6 parallel slices; group the remainder. If you are unsure which criterion applies or how to cut, propose the split to the user instead of guessing.

## 3. Fan out
Launch all slice agents in ONE message (parallel), `subagent_type: project-explorer`. Each prompt must include: mode `slice`, the slice path, a one-line project context, and the instruction to return the structured slice format (no file written).

## 4. Synthesize
Merge slice findings into the report using the template below. If slices contradict or leave gaps on launch/test commands, re-check the files yourself rather than guessing. Write `<target>/PROJECT_OVERVIEW.md`.

Template: 1. Overview · 2. Tech stack · 3. Repository layout (annotated tree + packages table) · 4. Architecture (components, data/control flow, inter-slice dependencies, external services, optional mermaid) · 5. Prerequisites & setup · 6. How to launch (exact commands + sources) · 7. How to run the tests (all / one package / one test / lint / typecheck / CI equivalent, with sources) · 8. Gaps / unverified items.

## 5. Reply
Give a short summary: which split was used and why, plus the report path. Do not paste the whole report.
