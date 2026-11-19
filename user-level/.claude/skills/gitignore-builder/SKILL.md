---
name: gitignore-builder
description: Create or complete a sensible `.gitignore` tailored to the current project by detecting its stack (languages, package managers, frameworks, databases, editors, OS). Use this skill whenever the user asks to create, generate, fix, update, clean up or review a `.gitignore`, mentions files that should not be committed (logs, `.env`, build output, caches, local databases, editor folders), or notices unwanted files in `git status`, even if they don't say the word "gitignore".
---

# gitignore-builder

Produce a `.gitignore` that matches what the project actually contains, not a generic template pasted blindly. A good one keeps generated, local, secret and machine-specific files out of git while never hiding files the team needs.

## Workflow

### 1. Inspect the project

Look before writing. Do not guess the stack.

- List the repo root and first-level folders (`ls -a`).
- Read the existing `.gitignore` if there is one.
- Detect the stack from marker files: `requirements.txt`, `pyproject.toml`, `package.json`, `pom.xml`, `go.mod`, `Cargo.toml`, `*.csproj`, `Gemfile`, `composer.json`, `Dockerfile`, etc.
- Detect local artifacts actually present: virtualenvs, `node_modules`, build/dist folders, caches, `*.db` / `*.sqlite`, `logs/`, `.env*`, coverage output, editor folders (`.vscode/`, `.idea/`), `.claude/`.
- Run `git status --short` and `git ls-files` to see what is untracked and what is already tracked.

### 2. Decide the rules

Choose rules in these groups, keeping only those relevant to what you detected:

- **Language/runtime artifacts**: bytecode, compiled output, virtualenvs, `node_modules/`, `target/`, `dist/`, `build/`.
- **Tooling caches**: test, lint and type-check caches, coverage reports.
- **Secrets and local config**: `.env`, `.env.*` (but keep `.env.example` with a `!.env.example` negation), key files, local settings.
- **Local data**: SQLite/db files, dumps, generated exports, `logs/` and `*.log`. Ignore the pattern the project already uses for data (for example `data/*.csv`) rather than inventing new ones.
- **OS noise**: `.DS_Store`, `Thumbs.db`, `desktop.ini`.
- **Editor and tool folders**: ignore `.vscode/`, `.idea/`, `.claude/` by default, but keep shared files tracked with negations. Git cannot re-include a file inside an ignored directory, so ignore the directory contents, not the directory itself:

  ```gitignore
  .vscode/*
  !.vscode/settings.json
  !.vscode/extensions.json
  .claude/*
  !.claude/settings.json
  !.claude/hooks/
  !.claude/skills/
  ```

  Only add a negation for a shared file that exists in the repo or is clearly meant to be shared (such as `.claude/settings.json`, hooks and skills, which the team versions). Personal files such as `.claude/settings.local.json` stay ignored.

Why this matters: over-ignoring silently hides files the team needs (and nobody notices until a fresh clone breaks), while under-ignoring leaks secrets and bloats history. When unsure whether a file is shared, check whether it is already tracked (`git ls-files`) and treat tracked files as shared.

### 3. Write the file

- **No `.gitignore` yet**: create one, organized in commented sections (`# Python`, `# Environment`, `# Local data`, `# Editors`, `# OS`).
- **A `.gitignore` already exists**: only **add the missing rules**. Never remove, reorder or rewrite existing lines, since they reflect decisions the team made. Append new rules under a clear section comment, and skip any rule that is already covered by an existing one.
- Use standard gitignore syntax: trailing `/` for directories, `*` globs, `!` negations. Keep it minimal and readable; no duplicated patterns.

### 4. Report already-tracked files, don't fix them

A `.gitignore` has no effect on files git already tracks. After writing, compare the final rules with `git ls-files` (for example `git ls-files -ci --exclude-standard` lists tracked files that now match an ignore rule).

- List those files for the user and explain that they stay tracked until untracked.
- Give the command they can run themselves (`git rm --cached <path>`), but **do not run it** and do not commit. Untracking changes the repo history for everyone, so it is the user's call.

### 5. Summarize

Tell the user briefly: which stack you detected, which rules you added (and why for non-obvious ones), which rules you intentionally left out, and the list of tracked files that still need `git rm --cached`.

## Rules of thumb

- Never ignore lockfiles (`package-lock.json`, `poetry.lock`, etc.) unless the user asks. Libraries and apps commit them.
- Never ignore source, tests, migrations, seed or fixture files, or `requirements.txt`-style dependency manifests.
- Don't add rules for tools the project doesn't use. A short accurate file beats a 500-line template.
