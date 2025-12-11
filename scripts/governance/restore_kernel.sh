#!/bin/bash
# VISNU KERNEL AUTO-RESTORE
# =========================
# Pre-commit hook that RESTORES kernel files instead of just blocking.
# Agent changes to kernel files literally disappear.
#
# SECURITY RING 0 - Life, Death, and Rights (3399 LOC total)
#
# Core Orchestration:
#   - vibe_core/kernel_impl.py (1505 LOC)
#   - vibe_core/kernel_ops.py (326 LOC)
# Plugin System:
#   - vibe_core/plugin_protocol.py (402 LOC)
#   - vibe_core/plugin_loader.py (381 LOC)
# Security (Sword, Shield, Gate):
#   - vibe_core/narasimha.py (414 LOC) - Kill-Switch
#   - vibe_core/capability_registry.py (343 LOC) - Permissions
#   - vibe_core/bridge.py (28 LOC) - Constitution Gate
#
# See: docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md

set -e

KERNEL_FILES=(
    # Core Orchestration
    "vibe_core/kernel_impl.py"
    "vibe_core/kernel_ops.py"
    # Plugin System
    "vibe_core/plugin_protocol.py"
    "vibe_core/plugin_loader.py"
    # Security (Sword, Shield, Gate)
    "vibe_core/narasimha.py"
    "vibe_core/capability_registry.py"
    "vibe_core/bridge.py"
)

RESTORED=0

for file in "${KERNEL_FILES[@]}"; do
    # Check if file has staged changes
    if git diff --cached --name-only | grep -q "^${file}$"; then
        # Restore from HEAD
        git checkout HEAD -- "$file"
        git add "$file"
        RESTORED=1
        echo "⚡ RESTORED: $file"
    fi
done

if [ $RESTORED -eq 1 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  KERNEL IS VISNU - ETERNAL AND UNCHANGING                    ║"
    echo "║                                                              ║"
    echo "║  Your changes to kernel files have been DISCARDED.           ║"
    echo "║  The kernel has been restored to its eternal state.          ║"
    echo "║                                                              ║"
    echo "║  Create a PLUGIN instead:                                    ║"
    echo "║    vibe_core/plugins/your_feature/                           ║"
    echo "║                                                              ║"
    echo "║  See: docs/architecture/OPUS/001-KERNEL-EXTRACTION.md        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
fi

# Always exit 0 - changes are restored, commit can proceed
exit 0
