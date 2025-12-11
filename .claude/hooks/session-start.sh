#!/bin/bash
# STEWARD Protocol - Claude Code Web Session Start Hook
# ======================================================
# Ensures git hooks are active in every Claude Code Web session.
#
# GAD-000 Compliance: Machine-parseable output for AI operators.
# This hook runs at session start to enable kernel protection.

set -e

# Output structured JSON for AI parseability
output_json() {
    local status="$1"
    local message="$2"
    local action="$3"
    echo "{\"hook\":\"session-start\",\"status\":\"$status\",\"message\":\"$message\",\"action\":\"$action\"}"
}

# Check if we're in the steward-protocol repo
if [ ! -f "scripts/governance/restore_kernel.sh" ]; then
    output_json "skip" "Not in steward-protocol repository" "none"
    exit 0
fi

# Check current hooksPath
CURRENT_HOOKS_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")

if [ "$CURRENT_HOOKS_PATH" = ".githooks" ]; then
    output_json "ok" "Git hooks already configured" "none"
    exit 0
fi

# Set hooksPath to enable kernel protection
git config --local core.hooksPath .githooks

if [ $? -eq 0 ]; then
    output_json "configured" "Git hooks enabled - kernel protection active" "set_hooks_path"

    # Also output human-readable for logs
    echo ""
    echo "☢️ VISNU KERNEL PROTECTION ACTIVATED"
    echo "   21 files protected (7 kernel + 3 governance + 10 workflows + 1 config)"
    echo "   See: docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md"
    echo ""
else
    output_json "error" "Failed to set git hooks path" "manual_intervention_required"
    exit 1
fi
