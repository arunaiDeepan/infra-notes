#!/bin/sh
# Per-clone setup for the Obsidian <-> GitHub markdown bridge.
#
# Run this once after cloning the repo. It configures:
#   - core.hooksPath        -> .githooks (so the pre-commit hook runs)
#   - filter.obsidian.clean -> obsidian_to_github.py (working tree -> index)
#   - filter.obsidian.smudge-> github_to_obsidian.py (index -> working tree)
#   - filter.obsidian.required = false (silent passthrough if python missing)
#
# Re-running is safe (overwrites with the same values).

set -eu

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: not inside a git work tree" >&2
    exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Pick a python interpreter; prefer 'python', fall back to 'py' (Windows launcher).
if command -v python >/dev/null 2>&1; then
    PY=python
elif command -v py >/dev/null 2>&1; then
    PY=py
else
    echo "Warning: no python interpreter found in PATH." >&2
    echo "  The filter is required=false so files will pass through unchanged" >&2
    echo "  until python is installed. Configuring anyway." >&2
    PY=python
fi

# Verify the converter scripts exist.
for f in scripts/obsidian_to_github.py scripts/github_to_obsidian.py; do
    if [ ! -f "$f" ]; then
        echo "Error: $f is missing from this checkout" >&2
        exit 1
    fi
done

git config core.hooksPath .githooks
git config filter.obsidian.clean  "$PY scripts/obsidian_to_github.py"
git config filter.obsidian.smudge "$PY scripts/github_to_obsidian.py"
git config filter.obsidian.required false

cat <<EOF
[obsidian-bridge] installed for this clone:
  core.hooksPath        = .githooks
  filter.obsidian.clean  = $PY scripts/obsidian_to_github.py
  filter.obsidian.smudge = $PY scripts/github_to_obsidian.py
  filter.obsidian.required = false

To apply the smudge filter to .md files already in the working tree, run:
  git rm --cached -r -- '*.md' && git checkout -- '*.md'
(Or just edit a file; new commits get full bidirectional conversion automatically.)
EOF
