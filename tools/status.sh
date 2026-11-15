#!/usr/bin/env bash
# Where the project stands, in one screen:  tools/status.sh
#
# Read-only. Shows the branch and what is not pushed, the working tree, the version, the venv,
# waiting mailbox messages and whether the graphify graph is current.
set -uo pipefail
cd "$(dirname "$0")/.."

echo "== git"
echo "branch: $(git branch --show-current)"
upstream=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null || true)
if [ -n "$upstream" ]; then
    echo "not pushed to $upstream: $(git rev-list --count "$upstream"..HEAD) commit(s)"
else
    echo "no upstream branch: nothing of this branch is pushed"
fi
dirty=$(git status --short)
if [ -n "$dirty" ]; then echo "uncommitted:"; echo "$dirty" | sed 's/^/  /'; else echo "working tree clean"; fi
echo "recent:"; git log --oneline -5 | sed 's/^/  /'
echo "latest tag: $(git describe --tags --abbrev=0 2>/dev/null || echo none)"

echo
echo "== version"
grep -m1 '__version__ =' src/tess_utils/__init__.py

echo
echo "== venv"
venv="$HOME/Projects/pyDev/pyEnvs/tess-utils"
if [ -x "$venv/bin/python" ]; then
    echo "$venv: $("$venv/bin/python" -V)"
else
    echo "missing: UV_PROJECT_ENVIRONMENT=$venv uv sync --group docs"
fi

echo
echo "== mailbox"
if [ -f "$HOME/.claude/mailbox/cli.py" ]; then
    echo "messages waiting: $(python3 -I "$HOME/.claude/mailbox/cli.py" pending 2>/dev/null || echo 'not configured for this project')"
else
    echo "no mailbox on this machine"
fi

echo
echo "== graph"
tools/graphify_refresh.sh --check
