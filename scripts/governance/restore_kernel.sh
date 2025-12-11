#!/bin/bash
# VISNU KERNEL - NUCLEAR OPTION
# =============================
# Dieses Skript setzt Security Ring 0 BRUTAL auf origin/main zurück.
# Nicht HEAD (kann polluted sein), sondern die WAHRE QUELLE.
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

# Fetch origin/main - die WAHRE QUELLE
git fetch origin main --depth=1 2>/dev/null || true

RESTORED=0

for file in "${KERNEL_FILES[@]}"; do
    # Prüfen ob die Datei von origin/main abweicht (staged oder unstaged)
    if ! git diff --quiet origin/main -- "$file" 2>/dev/null; then
        echo "🚨 ALARM: Unerlaubte Änderung an $file"

        # NUCLEAR: Überschreiben mit origin/main (nicht HEAD!)
        git checkout origin/main -- "$file"
        git add "$file"

        echo "✅ RESTORED: $file → origin/main"
        RESTORED=1
    fi
done

if [ $RESTORED -eq 1 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ☢️  NUCLEAR RESET EXECUTED                                   ║"
    echo "║                                                              ║"
    echo "║  Your changes to Security Ring 0 have been OBLITERATED.     ║"
    echo "║  Files restored from origin/main (the TRUE source).         ║"
    echo "║                                                              ║"
    echo "║  The kernel is VISNU. Resistance is futile.                 ║"
    echo "║                                                              ║"
    echo "║  Create a PLUGIN instead:                                    ║"
    echo "║    vibe_core/plugins/your_feature/                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
fi

# Always exit 0 - changes are restored, commit can proceed
exit 0
