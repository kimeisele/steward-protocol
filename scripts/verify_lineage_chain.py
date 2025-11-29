#!/usr/bin/env python3
"""
🔍 PARAMPARA CHAIN VERIFICATION SCRIPT 🔍

This script verifies the integrity of the Parampara lineage chain.
It checks:
1. Genesis Block exists and is valid
2. All block hashes are correct
3. All chain links are intact
4. No tampering has occurred

Usage:
    python scripts/verify_lineage_chain.py [--export-json output.json]
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.lineage import LineageChain, LineageEventType


def verify_chain(chain: LineageChain) -> bool:
    """
    Perform comprehensive chain verification.

    Returns:
        True if all checks pass, False otherwise
    """
    print("=" * 70)
    print("🔍 PARAMPARA CHAIN VERIFICATION")
    print("=" * 70)

    # Check 1: Chain exists
    chain_length = chain.get_chain_length()
    if chain_length == 0:
        print("❌ FAIL: Chain is empty")
        return False

    print(f"✅ Chain length: {chain_length} blocks")

    # Check 2: Genesis Block exists
    genesis = chain.get_genesis_block()
    if not genesis:
        print("❌ FAIL: Genesis Block not found")
        return False

    print(f"✅ Genesis Block found (hash: {genesis.hash[:32]}...)")

    # Check 3: Genesis Block structure
    if genesis.index != 0:
        print(f"❌ FAIL: Genesis Block has wrong index: {genesis.index}")
        return False

    if genesis.event_type != LineageEventType.GENESIS:
        print(f"❌ FAIL: Genesis Block has wrong event type: {genesis.event_type}")
        return False

    print("✅ Genesis Block structure valid")

    # Check 4: Genesis anchors (GAD-000 and CONSTITUTION)
    anchors = genesis.data.get("anchors", {})
    philosophy_hash = anchors.get("philosophy_hash", "")
    constitution_hash = anchors.get("constitution_hash", "")

    if not philosophy_hash or philosophy_hash == "0" * 64:
        print("⚠️  WARNING: GAD-000 hash not found or invalid")
    else:
        print(f"✅ GAD-000 anchored: {philosophy_hash[:16]}...")

    if not constitution_hash or constitution_hash == "0" * 64:
        print("⚠️  WARNING: CONSTITUTION hash not found or invalid")
    else:
        print(f"✅ CONSTITUTION anchored: {constitution_hash[:16]}...")

    # Check 5: Full chain integrity
    print("\n🔗 Verifying chain integrity...")
    if not chain.verify_chain():
        print("❌ FAIL: Chain integrity check failed")
        return False

    print("✅ All blocks verified - chain is intact")

    # Check 6: List all events
    print("\n📜 Chain Events:")
    print("-" * 70)
    blocks = chain.get_all_blocks()
    for block in blocks:
        agent_str = f"({block.agent_id})" if block.agent_id else "(SYSTEM)"
        print(f"  [{block.index}] {block.event_type} {agent_str} @ {block.timestamp}")

    print("-" * 70)
    print(f"\n✅ ALL CHECKS PASSED - PARAMPARA CHAIN IS VALID")
    print("=" * 70)

    return True


def test_tampering(chain: LineageChain) -> None:
    """
    Test tampering detection by attempting to modify the database.

    WARNING: This is destructive! Only use on test chains.
    """
    print("\n🧪 Testing tampering detection...")

    # Get latest block
    latest = chain.get_latest_block()
    if not latest:
        print("No blocks to tamper with")
        return

    print(f"Original hash: {latest.hash[:32]}...")

    # Attempt to modify data directly in DB (simulating tampering)
    try:
        chain.conn.execute(
            "UPDATE blocks SET data = ? WHERE idx = ?",
            ('{"tampered": true}', latest.index),
        )
        chain.conn.commit()

        print("Database modified (tampered)")

        # Now verify - this should fail
        if chain.verify_chain():
            print("❌ FAIL: Tampering not detected!")
        else:
            print("✅ SUCCESS: Tampering detected correctly")

    except Exception as e:
        print(f"❌ Error during tampering test: {e}")


def main():
    parser = argparse.ArgumentParser(description="Verify Parampara lineage chain")
    parser.add_argument(
        "--db-path",
        default="/tmp/vibe_os/kernel/lineage.db",
        help="Path to lineage database",
    )
    parser.add_argument("--export-json", help="Export chain to JSON file")
    parser.add_argument(
        "--test-tamper",
        action="store_true",
        help="Test tampering detection (destructive!)",
    )

    args = parser.parse_args()

    # Load chain
    try:
        chain = LineageChain(db_path=args.db_path)
    except Exception as e:
        print(f"❌ Failed to load chain: {e}")
        return 1

    # Verify chain
    if not verify_chain(chain):
        return 1

    # Export to JSON if requested
    if args.export_json:
        try:
            chain.export_to_json(args.export_json)
            print(f"\n📄 Chain exported to {args.export_json}")
        except Exception as e:
            print(f"❌ Failed to export: {e}")
            return 1

    # Test tampering if requested
    if args.test_tamper:
        test_tampering(chain)

    return 0


if __name__ == "__main__":
    sys.exit(main())
