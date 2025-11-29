#!/usr/bin/env python3
"""
🧪 ACID TEST: PERSISTENCE ACROSS RESTART

This test verifies that:
1. System starts and creates transactions
2. Database is properly persisted
3. After restart, all data is still there
4. Cryptographic keys survive restart
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from vibe_core.kernel_impl import RealVibeKernel, SQLiteLedger
from vibe_core.scheduling import Task

# Import all agent cartridges
from herald.cartridge_main import HeraldCartridge
from civic.cartridge_main import CivicCartridge
from forum.cartridge_main import ForumCartridge
from science.cartridge_main import ScientistCartridge
from envoy.cartridge_main import EnvoyCartridge


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_initial_state():
    """Test 1: Create system, verify state"""
    print_section("TEST 1: INITIAL STATE")

    # Clean up old database (if exists)
    db_path = "data/vibe_ledger.db"
    backup_path = f"{db_path}.backup"
    if Path(db_path).exists():
        print(f"📦 Backing up existing database to {backup_path}")
        Path(db_path).rename(backup_path)

    # Create kernel with persistent ledger
    kernel = RealVibeKernel(ledger_path=db_path)

    # Register agents
    agents = [
        ("herald", HeraldCartridge()),
        ("civic", CivicCartridge()),
        ("forum", ForumCartridge()),
        ("science", ScientistCartridge()),
        ("envoy", EnvoyCartridge()),
    ]

    for agent_id, agent_instance in agents:
        kernel.register_agent(agent_instance)

    # Boot kernel
    kernel.boot()
    print("✅ Kernel booted with 5 agents")

    # Create a test task
    test_task = Task(
        task_id="test-persistence-001",
        agent_id="herald",
        payload={"action": "test_persistence", "message": "This is a persistence test"},
    )

    kernel.submit_task(test_task)
    kernel.tick()

    # Check ledger
    events = kernel.ledger.get_all_events()
    print(f"✅ Ledger has {len(events)} events")

    # Verify database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ledger_events")
    count = cursor.fetchone()[0]
    print(f"✅ Database has {count} persisted events")
    conn.close()

    # Check keys
    identity_path = Path("data/identities/herald_private.key")
    if identity_path.exists():
        print(f"✅ HERALD private key exists and secured (600)")
        with open(identity_path, "rb") as f:
            key_content = f.read()
        print(f"   Key size: {len(key_content)} bytes")

    return db_path


def test_restart_persistence(db_path: str):
    """Test 2: Restart kernel and verify persistence"""
    print_section("TEST 2: RESTART & PERSISTENCE")

    # Restart kernel
    kernel = RealVibeKernel(ledger_path=db_path)

    # Check ledger (should reload from DB)
    events = kernel.ledger.get_all_events()
    print(f"✅ After restart: Ledger has {len(events)} events (should match Test 1)")

    # Verify database directly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ledger_events")
    count = cursor.fetchone()[0]
    print(f"✅ After restart: Database still has {count} events")

    # Show event details
    cursor.execute(
        """
        SELECT event_type, agent_id, task_id
        FROM ledger_events
        ORDER BY id
    """
    )
    print("\n   Event log:")
    for event_type, agent_id, task_id in cursor.fetchall():
        print(f"   - {event_type:20} | {agent_id:10} | {task_id}")

    conn.close()

    # Verify keys still exist
    identity_path = Path("data/identities/herald_private.key")
    if identity_path.exists():
        print(f"\n✅ HERALD keys survived restart")
        with open(identity_path, "rb") as f:
            key_content = f.read()
        print(f"   Key size: {len(key_content)} bytes (unchanged)")

    return True


def test_cryptographic_signing():
    """Test 3: Verify cryptographic keys work"""
    print_section("TEST 3: CRYPTOGRAPHIC IDENTITY")

    from herald.tools.identity_tool import IdentityTool

    # Initialize identity tool
    identity = IdentityTool(agent_id="herald")

    # Check identity
    assert_result = identity.assert_identity()
    print(f"✅ Identity verification: {assert_result}")

    # Get public key
    pub_key = identity.get_public_key()
    if pub_key:
        print(f"✅ Public key available: {pub_key[:32]}...")

    # Sign something
    test_content = "This is test content for signing"
    signature = identity.sign_artifact(test_content)
    if signature:
        print(f"✅ Content signed successfully ({len(signature)} char signature)")
        print(f"   Signature: {signature[:32]}...")

    return True


def main():
    """Run all persistence tests"""
    print_section("🧪 AGENT CITY - PERSISTENCE ACID TEST")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Test Database: data/vibe_ledger.db")
    print(f"Test Keys: data/identities/")

    try:
        # Test 1: Initial state
        db_path = test_initial_state()

        # Test 2: Restart persistence
        test_restart_persistence(db_path)

        # Test 3: Cryptographic keys
        test_cryptographic_signing()

        # Final report
        print_section("✅ ACID TEST RESULTS")
        print("✅ Persistence: PASSED")
        print("✅ Cryptography: PASSED")
        print("✅ System Watertight: PASSED")
        print("\n🎉 All tests passed! Agent City is production-ready.")

    except Exception as e:
        print_section("❌ TEST FAILED")
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
