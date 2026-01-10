#!/bin/bash
#
# OPUS-081: Stop Hook - Auto-Commit Edition
# ==========================================
# This hook auto-commits any uncommitted changes before session ends.
# Runtime state and source code are both committed.
#
# See: docs/architecture/OPUS/081-RUNTIME-STATE-MANIFEST.md

# Read the JSON input from stdin (required by Claude Code)
input=$(cat)

# Recursion prevention
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active // "false"')
if [[ "$stop_hook_active" = "true" ]]; then
  exit 0
fi

# Get repo root
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# Check if we're in a git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

# Check for any uncommitted changes (staged or unstaged)
if git diff --quiet && git diff --cached --quiet; then
  # Check for untracked files too
  UNTRACKED=$(git ls-files --others --exclude-standard)
  if [[ -z "$UNTRACKED" ]]; then
    echo "✅ No uncommitted changes"
    exit 0
  fi
fi

# Auto-commit all changes
echo "📦 Auto-committing changes..."

# Stage all changes (including new files)
git add -A

# Get branch name for commit message
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Commit with --no-verify to skip pre-commit hooks
git commit -m "chore(auto): Session checkpoint [$BRANCH]

Auto-committed at: $TIMESTAMP
Session: Claude Code" --no-verify >/dev/null 2>&1

if [[ $? -eq 0 ]]; then
  echo "✅ Changes committed"
else
  echo "⚠️  Nothing to commit (already clean)"
fi

exit 0
