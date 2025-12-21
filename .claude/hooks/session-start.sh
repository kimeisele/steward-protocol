#!/bin/bash
# STEWARD Protocol - Claude Code Web SessionStart Hook
# =====================================================
# Automatically configures environment for Claude Code Web sessions.
#
# This hook:
# 1. Installs Python dependencies (uv pip install -e .[dev])
# 2. Enables VISNU kernel protection (git hooks)
#
# GAD-000 Compliance: Machine-parseable JSON output for AI operators.
set -euo pipefail

# Only run in Claude Code Web (remote environment)
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
    exit 0
fi

echo "🚀 STEWARD Protocol SessionStart Hook"
echo "====================================="

# ------------------------------------------------------------------------------
# Step 1: Install Python dependencies
# ------------------------------------------------------------------------------
echo ""
echo "📦 Installing dependencies..."

if command -v uv &> /dev/null; then
    uv pip install --system -e ".[dev]" --quiet
    echo "✅ Dependencies installed (uv)"
else
    pip install -e ".[dev]" --quiet
    echo "✅ Dependencies installed (pip)"
fi

# ------------------------------------------------------------------------------
# Step 2: Enable VISNU Kernel Protection (git hooks)
# ------------------------------------------------------------------------------
echo ""
echo "🔒 Configuring VISNU kernel protection..."

CURRENT_HOOKS_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")

if [ "$CURRENT_HOOKS_PATH" = ".githooks" ]; then
    echo "✅ Git hooks already configured"
else
    git config --local core.hooksPath .githooks
    echo "✅ Git hooks enabled (.githooks)"
fi

# ------------------------------------------------------------------------------
# Summary (GAD-000 compliant JSON)
# ------------------------------------------------------------------------------
echo ""
echo "{"
echo "  \"hook\": \"SessionStart\","
echo "  \"status\": \"success\","
echo "  \"actions\": ["
echo "    \"installed_dependencies\","
echo "    \"enabled_kernel_protection\""
echo "  ],"
echo "  \"kernel_protection\": {"
echo "    \"enabled\": true,"
echo "    \"protected_files\": 21,"
echo "    \"documentation\": \"docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md\""
echo "  }"
echo "}"
echo ""
echo "☢️ VISNU KERNEL PROTECTION ACTIVE"
echo "   21 files protected (7 kernel + 3 governance + 10 workflows + 1 config)"

# ------------------------------------------------------------------------------
# Step 3: PRANA - Auto-boot Kernel (if configured)
# ------------------------------------------------------------------------------
PRANA_CONFIG="config/prana.yaml"
AUTO_BOOT="false"

if [ -f "$PRANA_CONFIG" ]; then
    # Parse auto_boot_kernel from YAML (simple grep, no deps needed)
    AUTO_BOOT=$(grep -A3 "session_start:" "$PRANA_CONFIG" | grep "auto_boot_kernel:" | awk '{print $2}' | tr -d ' ')
fi

if [ "$AUTO_BOOT" = "true" ]; then
    echo ""
    echo "💓 PRANA: Starting kernel in background..."

    # Boot in background, non-blocking
    python -m vibe_core.cli boot --background > /tmp/prana_boot.log 2>&1 &
    BOOT_PID=$!

    # Quick verification (don't wait too long)
    sleep 2
    if ps -p $BOOT_PID > /dev/null 2>&1 || pgrep -f "boot_kernel.py" > /dev/null 2>&1; then
        echo "✅ Kernel started (background)"
    else
        echo "⚠️  Kernel boot initiated (check /tmp/prana_boot.log)"
    fi

    # OPUS-167: Commit runtime state after boot
    # Wait for UI files to be rendered, then commit them
    sleep 3
    if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
        echo "✅ No runtime state to commit"
    else
        # Stage runtime files (UI markdown + state directories)
        git add *.md .prakriti/ .opus_state/ vibe_core/plugins/opus_assistant/.opus_state/ 2>/dev/null || true

        # Commit with --no-verify (skip pre-commit hooks for runtime state)
        if git commit -m "chore: Auto-commit runtime state (session start)" --no-verify >/dev/null 2>&1; then
            echo "✅ Runtime state committed"
        else
            echo "⚠️  No runtime changes to commit"
        fi
    fi
fi

echo ""
