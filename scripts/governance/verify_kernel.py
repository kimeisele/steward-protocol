#!/usr/bin/env python3
"""
KERNEL INTEGRITY VERIFICATION (Phase 3: Hash-Verification)
============================================================

This script verifies the integrity of core kernel files.
Once the kernel is stable, these files should NEVER change without
explicit Senior Review approval.

Protected Files:
- vibe_core/kernel_impl.py
- vibe_core/plugin_protocol.py
- vibe_core/plugin_loader.py

Usage:
    # Generate hashes (run once when kernel is finalized)
    python scripts/governance/verify_kernel.py --generate

    # Verify integrity (run in CI)
    python scripts/governance/verify_kernel.py --verify

    # Check for changes (run before commit)
    python scripts/governance/verify_kernel.py --check
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Files that are protected (should not change without Senior Review)
PROTECTED_FILES = [
    "vibe_core/kernel_impl.py",
    "vibe_core/plugin_protocol.py",
    "vibe_core/plugin_loader.py",
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


def generate_hashes() -> dict:
    """Generate hashes for all protected files."""
    hashes = {}
    for file in PROTECTED_FILES:
        file_hash = get_file_hash(file)
        hashes[file] = file_hash
        print(f"  {file}: {file_hash[:16]}...")
    return hashes


def save_hashes(hashes: dict) -> None:
    """Save hashes to file."""
    HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    HASH_FILE.write_text(json.dumps(hashes, indent=2))
    print(f"\n Hashes saved to: {HASH_FILE}")


def load_hashes() -> dict:
    """Load expected hashes from file."""
    if not HASH_FILE.exists():
        print(f" Hash file not found: {HASH_FILE}")
        print("  Run with --generate first to create baseline hashes.")
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
        description="Kernel Integrity Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--generate", action="store_true", help="Generate baseline hashes")
    parser.add_argument("--verify", action="store_true", help="Verify integrity against baseline")
    parser.add_argument("--check", action="store_true", help="Check for changes (CI mode)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.generate:
        print(" GENERATING KERNEL HASHES")
        print("=" * 60)
        hashes = generate_hashes()
        save_hashes(hashes)
        print("\n Baseline hashes generated. Commit kernel_hashes.json to lock them in.")
        sys.exit(0)

    elif args.verify:
        print(" VERIFYING KERNEL INTEGRITY")
        print("=" * 60)
        if verify_hashes():
            print("\n Kernel integrity verified.")
            sys.exit(0)
        else:
            print("\n KERNEL INTEGRITY COMPROMISED!")
            print("  These files require SENIOR REVIEW if changes are intentional.")
            sys.exit(1)

    elif args.check:
        changed = check_changes()
        if args.json:
            print(json.dumps({"changed": changed, "protected": PROTECTED_FILES}))
        elif changed:
            print(" PROTECTED FILES MODIFIED:")
            for f in changed:
                print(f"  - {f}")
            print("\n  These changes require SENIOR REVIEW approval.")
            sys.exit(1)
        else:
            print(" No protected files modified.")
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
