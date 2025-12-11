#!/usr/bin/env python3
"""
KERNEL INTEGRITY VERIFICATION (Phase 3: Hash-Verification)
============================================================

KERNEL IS VISNU - ETERNAL AND UNCHANGING.

This script verifies the integrity of core kernel files.
The kernel is FROZEN. All new features MUST be plugins.

Protected Files:
- vibe_core/kernel_impl.py
- vibe_core/plugin_protocol.py
- vibe_core/plugin_loader.py

Usage:
    # Verify integrity (run in CI)
    python scripts/governance/verify_kernel.py --verify

    # Check for changes (run before commit)
    python scripts/governance/verify_kernel.py --check

HASH UPDATES:
    Hash file is MANUALLY edited only. No --generate option.
    If CI fails, the kernel was changed when it shouldn't have been.
    Create a plugin instead. No exceptions.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Files that are protected (should not change without Senior Review)
# SECURITY RING 0 - Life, Death, and Rights
PROTECTED_FILES = [
    # Core Orchestration
    "vibe_core/kernel_impl.py",
    "vibe_core/kernel_ops.py",       # Delegated kernel operations
    # Plugin System
    "vibe_core/plugin_protocol.py",
    "vibe_core/plugin_loader.py",
    # Security (Sword, Shield, Gate)
    "vibe_core/narasimha.py",        # Kill-Switch (The Sword)
    "vibe_core/capability_registry.py",  # Permissions (The Shield)
    "vibe_core/bridge.py",           # Constitution Gate (The Gate)
]

# Hash storage file
HASH_FILE = Path("scripts/governance/kernel_hashes.json")


def get_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    path = Path(file_path)
    if not path.exists():
        return "FILE_NOT_FOUND"
    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def load_hashes() -> dict:
    """Load expected hashes from file."""
    if not HASH_FILE.exists():
        print(f" Hash file not found: {HASH_FILE}")
        print("  CRITICAL: Hash file must exist. This is a setup error.")
        return {}
    return json.loads(HASH_FILE.read_text())


def verify_hashes() -> bool:
    """Verify current files against expected hashes."""
    expected = load_hashes()
    if not expected:
        return False

    all_match = True
    for file, expected_hash in expected.items():
        current_hash = get_file_hash(file)
        if current_hash != expected_hash:
            print(f" INTEGRITY VIOLATION: {file}")
            print(f"    Expected: {expected_hash[:16]}...")
            print(f"    Current:  {current_hash[:16]}...")
            all_match = False
        else:
            print(f" {file}: OK")

    return all_match


def check_changes() -> list:
    """Check which protected files have changed."""
    expected = load_hashes()
    if not expected:
        return []

    changed = []
    for file, expected_hash in expected.items():
        current_hash = get_file_hash(file)
        if current_hash != expected_hash:
            changed.append(file)

    return changed


def main():
    parser = argparse.ArgumentParser(
        description="Kernel Integrity Verification - KERNEL IS VISNU",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    # NO --generate option. Hash file is manually edited only.
    parser.add_argument("--verify", action="store_true", help="Verify integrity against baseline")
    parser.add_argument("--check", action="store_true", help="Check for changes (CI mode)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.verify:
        print(" VERIFYING KERNEL INTEGRITY")
        print("=" * 60)
        if verify_hashes():
            print("\n Kernel integrity verified.")
            sys.exit(0)
        else:
            print("\n KERNEL INTEGRITY COMPROMISED!")
            print("  KERNEL IS VISNU - ETERNAL AND UNCHANGING.")
            print("  All new features MUST be plugins. No exceptions.")
            print("  Revert your kernel changes and create a plugin instead.")
            sys.exit(1)

    elif args.check:
        changed = check_changes()
        if args.json:
            print(json.dumps({"changed": changed, "protected": PROTECTED_FILES}))
        elif changed:
            print(" PROTECTED FILES MODIFIED:")
            for f in changed:
                print(f"  - {f}")
            print("\n  KERNEL IS VISNU - No changes allowed.")
            print("  Create a plugin instead. Revert these changes.")
            sys.exit(1)
        else:
            print(" No protected files modified.")
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
