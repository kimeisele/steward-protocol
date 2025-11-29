#!/usr/bin/env python3
"""
🧪 PARAMPARA TEST SUITE 🧪

This script tests the Parampara blockchain implementation:
1. Creates Genesis Block
2. Simulates kernel boot
3. Registers agents
4. Verifies chain integrity
5. Exports chain to JSON

Usage:
    python scripts/test_parampara.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.lineage import LineageChain, LineageEventType
from datetime import datetime


def test_parampara():
    """Run comprehensive Parampara tests"""

    print("=" * 70)
    print("🧪 PARAMPARA TEST SUITE")
    print("=" * 70)

    # Clean up old test database
    test_db_path = "/tmp/vibe_os/kernel/test_lineage.db"
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()
        print("🗑️  Removed old test database")

    # Test 1: Initialize chain and create Genesis Block
    print("\n[TEST 1] Creating Genesis Block...")
    try:
        chain = LineageChain(db_path=test_db_path)
        print("✅ Genesis Block created successfully")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

    # Verify Genesis Block
    genesis = chain.get_genesis_block()
    if not genesis:
        print("❌ FAIL: Genesis Block not found")
        return False

    print(f"   Index: {genesis.index}")
    print(f"   Hash: {genesis.hash[:32]}...")
    print(f"   Event Type: {genesis.event_type}")

    # Check anchors
    anchors = genesis.data.get("anchors", {})
    print(f"   GAD-000 Hash: {anchors.get('philosophy_hash', 'MISSING')[:16]}...")
    print(
        f"   CONSTITUTION Hash: {anchors.get('constitution_hash', 'MISSING')[:16]}..."
    )

    # Test 2: Simulate Kernel Boot
    print("\n[TEST 2] Simulating Kernel Boot...")
    try:
        chain.add_block(
            event_type=LineageEventType.KERNEL_BOOT,
            agent_id=None,
            data={
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "agents_registered": 0,
            },
        )
        print("✅ KERNEL_BOOT block added")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

    # Test 3: Register multiple agents
    print("\n[TEST 3] Registering agents...")
    test_agents = [
        {
            "agent_id": "herald",
            "name": "Herald",
            "version": "1.0.0",
            "author": "System",
            "capabilities": ["broadcast", "announcement"],
        },
        {
            "agent_id": "scribe",
            "name": "Scribe",
            "version": "1.0.0",
            "author": "System",
            "capabilities": ["documentation", "markdown"],
        },
        {
            "agent_id": "auditor",
            "name": "Auditor",
            "version": "1.0.0",
            "author": "System",
            "capabilities": ["verification", "audit"],
        },
    ]

    for agent_data in test_agents:
        try:
            # Add AGENT_REGISTERED block
            chain.add_block(
                event_type=LineageEventType.AGENT_REGISTERED,
                agent_id=agent_data["agent_id"],
                data={
                    "name": agent_data["name"],
                    "version": agent_data["version"],
                    "author": agent_data["author"],
                    "capabilities": agent_data["capabilities"],
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # Add OATH_SWORN block
            chain.add_block(
                event_type=LineageEventType.OATH_SWORN,
                agent_id=agent_data["agent_id"],
                data={
                    "constitution_hash": "test_hash_123",
                    "timestamp": datetime.utcnow().isoformat(),
                    "verified": True,
                },
            )

            print(f"✅ Registered: {agent_data['agent_id']}")
        except Exception as e:
            print(f"❌ FAIL for {agent_data['agent_id']}: {e}")
            return False

    # Test 4: Verify chain integrity
    print("\n[TEST 4] Verifying chain integrity...")
    if chain.verify_chain():
        print("✅ Chain integrity verified")
    else:
        print("❌ FAIL: Chain integrity check failed")
        return False

    # Test 5: Query agent lineage
    print("\n[TEST 5] Querying agent lineage...")
    for agent_data in test_agents:
        agent_id = agent_data["agent_id"]
        lineage = chain.get_agent_lineage(agent_id)
        print(f"   {agent_id}: {len(lineage)} events")

        if len(lineage) != 2:  # Should have REGISTERED + OATH_SWORN
            print(f"   ⚠️  WARNING: Expected 2 events, found {len(lineage)}")

    # Test 6: Export to JSON
    print("\n[TEST 6] Exporting chain to JSON...")
    export_path = "/tmp/vibe_os/kernel/test_lineage.json"
    try:
        chain.export_to_json(export_path)
        print(f"✅ Chain exported to {export_path}")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

    # Test 7: Display chain summary
    print("\n[TEST 7] Chain Summary...")
    print("-" * 70)
    blocks = chain.get_all_blocks()
    for block in blocks:
        agent_str = f"({block.agent_id})" if block.agent_id else "(SYSTEM)"
        print(
            f"  Block {block.index:2d}: {block.event_type:20s} {agent_str:15s} {block.hash[:16]}..."
        )
    print("-" * 70)
    print(f"Total blocks: {len(blocks)}")

    # Test 8: Simulate Kernel Shutdown
    print("\n[TEST 8] Simulating Kernel Shutdown...")
    try:
        chain.add_block(
            event_type=LineageEventType.KERNEL_SHUTDOWN,
            agent_id=None,
            data={
                "reason": "Test complete",
                "timestamp": datetime.utcnow().isoformat(),
                "agents_active": len(test_agents),
            },
        )
        print("✅ KERNEL_SHUTDOWN block added")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

    # Final verification
    print("\n[FINAL] Final chain verification...")
    if chain.verify_chain():
        print("✅ Chain still valid after all operations")
    else:
        print("❌ FAIL: Chain corrupted")
        return False

    # Close chain
    chain.close()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - PARAMPARA IS OPERATIONAL")
    print("=" * 70)
    print(f"\nTest database: {test_db_path}")
    print(f"Export JSON: {export_path}")

    return True


if __name__ == "__main__":
    success = test_parampara()
    sys.exit(0 if success else 1)
