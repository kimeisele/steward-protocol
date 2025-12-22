#!/bin/bash
# VISNU KERNEL - NUCLEAR OPTION (TOTAL LOCKDOWN)
# ==============================================
# Dieses Skript setzt Security Ring 0 BRUTAL auf origin/main zurück.
# Nicht HEAD (kann polluted sein), sondern die WAHRE QUELLE.
#
# SECURITY RING 0 - Code + Watchers + Laws
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
# Governance (The Watchers):
#   - scripts/governance/restore_kernel.sh - THIS FILE
#   - scripts/governance/verify_kernel.py - Hash verification
#   - scripts/governance/kernel_hashes.json - Blessed hashes
# Infrastructure (The Laws):
#   - .github/workflows/* (ALL 10 workflow files) - The Supreme Court
#   - .pre-commit-config.yaml - The Local Police
#
# Total: 7 kernel + 3 governance + 10 workflows + 2 config = 22 files
#
# See: docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md

set -e

PROTECTED_FILES=(
    # Core Orchestration
    "vibe_core/kernel_impl.py"
    "vibe_core/kernel_ops.py"
    "vibe_core/ledger.py"
    # Plugin System
    "vibe_core/plugin_protocol.py"
    "vibe_core/plugin_loader.py"
    # Security (Sword, Shield, Gate)
    "vibe_core/narasimha.py"
    "vibe_core/capability_registry.py"
    "vibe_core/bridge.py"
    # Governance (The Watchers watch themselves)
    "scripts/governance/restore_kernel.sh"
    "scripts/governance/verify_kernel.py"
    "scripts/governance/kernel_hashes.json"
    # Infrastructure - Workflows (The Supreme Court)
    ".github/workflows/attest.yml"
    ".github/workflows/container-build.yml"
    ".github/workflows/deploy.yml"
    ".github/workflows/factory.yml"
    ".github/workflows/heartbeat.yml"
    ".github/workflows/integration-tests.yml"
    ".github/workflows/scheduled-agents.yml"
    ".github/workflows/scribe-docs.yml"
    ".github/workflows/steward-ci.yml"
    ".github/workflows/system-cycle.yml"
    # Infrastructure - Config (The Local Police)
    ".pre-commit-config.yaml"
    ".gitignore"
)

# Fetch origin/main - die WAHRE QUELLE
git fetch origin main --depth=1 2>/dev/null || true

RESTORED=0

for file in "${PROTECTED_FILES[@]}"; do
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
    echo "║  ☢️  NUCLEAR RESET EXECUTED (TOTAL LOCKDOWN)                  ║"
    echo "║                                                              ║"
    echo "║  Your changes to Security Ring 0 have been OBLITERATED.     ║"
    echo "║  Files restored from origin/main (the TRUE source).         ║"
    echo "║                                                              ║"
    echo "║  Protected: Code + Watchers + Laws                          ║"
    echo "║  The kernel is VISNU. Resistance is futile.                 ║"
    echo "║                                                              ║"
    echo "║  Create a PLUGIN instead:                                    ║"
    echo "║    vibe_core/plugins/your_feature/                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
fi

# Check for UNAUTHORIZED new workflow files
# (files in .github/workflows that don't exist in origin/main)
if [ -d ".github/workflows" ]; then
    for file in .github/workflows/*.yml .github/workflows/*.yaml; do
        [ -e "$file" ] || continue  # Skip if no match
        if ! git ls-tree origin/main -- "$file" &>/dev/null || [ -z "$(git ls-tree origin/main -- "$file")" ]; then
            echo "🚨 ALARM: Unauthorized NEW workflow detected: $file"
            rm -f "$file"
            git rm --cached "$file" 2>/dev/null || true
            echo "💀 DESTROYED: $file (not in origin/main)"
            RESTORED=1
        fi
    done
fi

# Always exit 0 - changes are restored, commit can proceed
exit 0
