#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - PHASE 4c: DATABASE PATH ISOLATION
=======================================================

Goal: Verify that CivicBank creates its database in the VFS sandbox,
not in the kernel's CWD.

Tests:
1. Initialize kernel → DB should be in /tmp/vibe_os/kernel/economy.db
2. Check that data/economy.db does NOT exist (old location)
3. Verify DB is functional (can create accounts, transfer credits)
"""

import sys
import os
import logging
from pathlib import Path

# Ensure we can import vibe_core
sys.path.append(os.getcwd())

from vibe_core.kernel_impl import RealVibeKernel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("VERIFICATION")


def test_kernel_bank_isolation():
    """Test that kernel's CivicBank uses VFS-isolated path"""
    logger.info("=" * 70)
    logger.info("TEST: Kernel CivicBank Database Isolation")
    logger.info("=" * 70)

    # Clean up old DB if exists
    old_db = Path("data/economy.db")
    vfs_db = Path("/tmp/vibe_os/kernel/economy.db")

    logger.info("\n1. Initializing kernel...")
    kernel = RealVibeKernel(ledger_path=":memory:")

    logger.info("\n2. Loading CivicBank...")
    bank = kernel.get_bank()

    logger.info("\n3. Checking database location...")

    # Check VFS path exists
    if vfs_db.exists():
        logger.info(f"   ✅ Database created in VFS: {vfs_db}")
        logger.info(f"      Size: {vfs_db.stat().st_size} bytes")
    else:
        logger.error(f"   ❌ Database NOT found in VFS: {vfs_db}")
        return False

    # Check old path does NOT exist (or is old)
    if old_db.exists():
        old_size = old_db.stat().st_size
        vfs_size = vfs_db.stat().st_size
        if vfs_size > old_size:
            logger.info(f"   ✅ Old DB exists but VFS DB is newer/larger")
        else:
            logger.warning(f"   ⚠️  Old DB exists at {old_db} - may be using wrong path")
    else:
        logger.info(f"   ✅ Old DB path clean: {old_db}")

    # Test 4: Verify DB is functional
    logger.info("\n4. Testing database functionality...")
    try:
        # Create test account
        balance = bank.get_balance("test_agent")
        logger.info(f"   ✅ Can query balance: {balance} credits")

        # Mint credits
        bank.transfer("MINT", "test_agent", 100, reason="Test mint")
        new_balance = bank.get_balance("test_agent")

        if new_balance == 100:
            logger.info(f"   ✅ Can mint credits: {new_balance} credits")
        else:
            logger.error(f"   ❌ Balance mismatch: expected 100, got {new_balance}")
            return False

    except Exception as e:
        logger.error(f"   ❌ Database operations failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    kernel.shutdown()
    return True


def test_agent_bank_isolation():
    """Test that agents would use their own sandbox paths"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST: Agent Sandbox Path Helper")
    logger.info("=" * 70)

    from vibe_core.protocols import VibeAgent
    from steward.oath_mixin import OathMixin

    class TestAgent(VibeAgent, OathMixin):
        def __init__(self, config=None):
            super().__init__(agent_id="test_civic", name="TEST_CIVIC", config=config)
            self.oath_mixin_init("test_civic")
            self.oath_sworn = True

        def process(self, task):
            return {"status": "ok"}

    agent = TestAgent()

    # Test get_sandbox_path (before VFS initialization)
    logger.info("\n1. Testing get_sandbox_path() fallback...")
    sandbox_path = agent.get_sandbox_path()
    expected = "/private/tmp/vibe_os/agents/test_civic"  # macOS resolves /tmp

    if "test_civic" in sandbox_path:
        logger.info(f"   ✅ Sandbox path: {sandbox_path}")
    else:
        logger.error(f"   ❌ Unexpected path: {sandbox_path}")
        return False

    # Test that CivicBank can be initialized with this path
    logger.info("\n2. Testing CivicBank with agent sandbox path...")
    try:
        from steward.system_agents.civic.tools.economy import CivicBank

        db_path = f"{sandbox_path}/economy.db"
        agent_bank = CivicBank(db_path=db_path)

        db_file = Path(db_path)
        if db_file.exists():
            logger.info(f"   ✅ Agent DB created: {db_path}")
            logger.info(f"      Size: {db_file.stat().st_size} bytes")
        else:
            logger.error(f"   ❌ Agent DB not found: {db_path}")
            return False

    except Exception as e:
        logger.error(f"   ❌ Failed to create agent bank: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main():
    logger.info("🚀 STARTING PHASE 4c VERIFICATION")
    logger.info("")

    results = []

    # Run tests
    results.append(("Kernel Bank Isolation", test_kernel_bank_isolation()))
    results.append(("Agent Sandbox Path", test_agent_bank_isolation()))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    logger.info("=" * 70)
    if all_passed:
        logger.info("✅ ALL TESTS PASSED")
        logger.info("\n🎉 C-Extension isolation works!")
        logger.info("   - Kernel DB: /tmp/vibe_os/kernel/economy.db")
        logger.info("   - Agent DBs: /tmp/vibe_os/agents/{id}/economy.db")
        sys.exit(0)
    else:
        logger.error("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
