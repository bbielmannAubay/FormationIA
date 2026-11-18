#!/usr/bin/env bash
# SessionStart hook (startup|resume): mirror ~/.claude into
# FormationIA/user-level/.claude/, honoring user-level/.gitignore (ignored files
# are never copied), then commit it locally (no push).

REPO="/c/Users/Maki/Documents/projects/FormationIA"
SUBDIR="user-level/.claude"
SRC="$HOME/.claude"

[ -d "$SRC" ] || exit 0
[ -d "$REPO/.git" ] || { echo "sync_claude_md: $REPO is not a git clone" >&2; exit 0; }

cd "$REPO" || exit 0
mkdir -p "$SUBDIR"

# All candidate files in ~/.claude, relative to it (skip nested .git dirs)
files=()
while IFS= read -r -d '' f; do files+=("$f"); done < <(
  cd "$SRC" && find . -name .git -prune -o -type f -print0 | sed -z 's#^\./##'
)
[ "${#files[@]}" -gt 0 ] || exit 0

# Ask git which of them user-level/.gitignore ignores (--no-index: ignore tracked state)
declare -A ignored
while IFS= read -r -d '' p; do ignored["$p"]=1; done < <(
  for f in "${files[@]}"; do printf '%s\0' "$SUBDIR/$f"; done \
    | git check-ignore --no-index -z --stdin
)

# Copy the non-ignored files that are new or changed
declare -A keep
for f in "${files[@]}"; do
  [ -n "${ignored[$SUBDIR/$f]}" ] && continue
  keep["$f"]=1
  mkdir -p "$SUBDIR/$(dirname "$f")"
  cmp -s "$SRC/$f" "$SUBDIR/$f" || cp "$SRC/$f" "$SUBDIR/$f"
done

# Mirror deletions: drop files that no longer exist (or are now ignored) in the source
while IFS= read -r -d '' f; do
  [ -n "${keep[$f]}" ] || rm -f "$SUBDIR/$f"
done < <(cd "$SUBDIR" && find . -type f -print0 | sed -z 's#^\./##')
find "$SUBDIR" -mindepth 1 -type d -empty -delete

git add -A -- "$SUBDIR"
if ! git diff --cached --quiet -- "$SUBDIR"; then
  # Commit only this path so other staged/untracked work in the clone is untouched
  git commit -q -m "chore: sync user-level .claude folder" -- "$SUBDIR" \
    && echo "sync_claude_md: committed $SUBDIR in FormationIA (not pushed)" >&2
fi
exit 0
