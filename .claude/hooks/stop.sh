#!/bin/bash
#
# OPUS-081: Stop Hook - Runtime State Aware
# ==========================================
# This hook delegates to scripts/git_gatekeeper.py which distinguishes
# between SOURCE CODE (must be committed) and RUNTIME STATE (can be dirty).
#
# Runtime state files (OPUS.md, .opus_state/, dashboards) are IGNORED.
# Only actual source code changes will block exit.
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
GATEKEEPER="$REPO_ROOT/scripts/git_gatekeeper.py"

# Delegate to Gatekeeper if it exists
if [[ -f "$GATEKEEPER" ]]; then
    cd "$REPO_ROOT"
    python3 "$GATEKEEPER"
    exit_code=$?

    if [[ $exit_code -ne 0 ]]; then
        echo "Run 'git status' to see uncommitted source files." >&2
    fi

    exit $exit_code
fi

# Fallback: If no gatekeeper, use simple dirty check
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "There are uncommitted changes. Please commit and push." >&2
  exit 2
fi

exit 0
