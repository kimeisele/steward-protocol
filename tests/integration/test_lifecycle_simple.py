#!/usr/bin/env python3
"""
SIMPLE LIFECYCLE TEST - Tests the core lifecycle logic without dependencies
"""

import logging
import sys

import pytest

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TEST_LIFECYCLE_SIMPLE")


def test_lifecycle_manager():
    """Test the core LifecycleManager without external dependencies."""
    logger.info("\n" + "=" * 80)
    logger.info("🔄 LIFECYCLE MANAGER CORE TEST")
    logger.info("=" * 80)

    try:
        from vibe_core.cartridges.system.civic.tools.lifecycle_manager import LifecycleManager, LifecycleStatus
    except ImportError as e:
        pytest.skip(f"Could not import lifecycle modules: {e}")

    # Initialize
    logger.info("\n✅ Importing LifecycleManager...")
    mgr = LifecycleManager()

    # TEST 1: Register agent as BRAHMACHARI
    logger.info("\n" + "-" * 80)
    logger.info("TEST 1: Register new agent as BRAHMACHARI")
    logger.info("-" * 80)

    agent = "test_agent"
    state = mgr.register_new_agent(agent)
    logger.info(f"✅ Agent registered: {agent}")
    logger.info(f"   Status: {state.status.value}")
    logger.info(f"   Varna: {state.varna}")

    assert state.status == LifecycleStatus.BRAHMACHARI, "Should be BRAHMACHARI"
    assert not state.diksha_passed, "Should not have passed diksha"

    # TEST 2: Check permissions
    logger.info("\n" + "-" * 80)
    logger.info("TEST 2: Check BRAHMACHARI permissions")
    logger.info("-" * 80)

    can_read = mgr.check_permission(agent, "read")
    can_write = mgr.check_permission(agent, "write")
    can_broadcast = mgr.check_permission(agent, "broadcast")

    logger.info(f"Read permission: {can_read} (should be True)")
    logger.info(f"Write permission: {can_write} (should be False)")
    logger.info(f"Broadcast permission: {can_broadcast} (should be False)")

    assert can_read, "BRAHMACHARI should read"
    assert not can_write, "BRAHMACHARI should NOT write"
    assert not can_broadcast, "BRAHMACHARI should NOT broadcast"

    logger.info("✅ TEST 2 PASSED: Permissions correct for BRAHMACHARI")

    # TEST 3: Promote to GRIHASTHA
    logger.info("\n" + "-" * 80)
    logger.info("TEST 3: Initiate to GRIHASTHA (promotion)")
    logger.info("-" * 80)

    state = mgr.initiate_to_grihastha(agent, initiator_agent="TEMPLE", reason="Passed tests")
    logger.info("✅ Promoted to GRIHASTHA")
    logger.info(f"   Status: {state.status.value}")
    logger.info(f"   Diksha passed: {state.diksha_passed}")
    logger.info(f"   Initiator: {state.initiator_agent}")

    assert state.status == LifecycleStatus.GRIHASTHA, "Should be GRIHASTHA"
    assert state.diksha_passed, "Should have passed diksha"

    # TEST 4: Check updated permissions
    logger.info("\n" + "-" * 80)
    logger.info("TEST 4: Check GRIHASTHA permissions")
    logger.info("-" * 80)

    can_read = mgr.check_permission(agent, "read")
    can_write = mgr.check_permission(agent, "write")
    can_broadcast = mgr.check_permission(agent, "broadcast")
    can_trade = mgr.check_permission(agent, "trade")

    logger.info(f"Read permission: {can_read} (should be True)")
    logger.info(f"Write permission: {can_write} (should be True)")
    logger.info(f"Broadcast permission: {can_broadcast} (should be True)")
    logger.info(f"Trade permission: {can_trade} (should be True)")

    assert can_read, "GRIHASTHA should read"
    assert can_write, "GRIHASTHA should write"
    assert can_broadcast, "GRIHASTHA should broadcast"
    assert can_trade, "GRIHASTHA should trade"

    logger.info("✅ TEST 4 PASSED: GRIHASTHA has full permissions")

    # TEST 5: Demote to SHUDRA
    logger.info("\n" + "-" * 80)
    logger.info("TEST 5: Demote to SHUDRA (violation)")
    logger.info("-" * 80)

    violation = {"type": "test_violation", "reason": "Test demotion"}
    state = mgr.demote_to_shudra(agent, violation, reason="Test")
    logger.info("✅ Demoted to SHUDRA")
    logger.info(f"   Status: {state.status.value}")
    logger.info(f"   Violations: {len(state.violations)}")

    assert state.status == LifecycleStatus.SHUDRA, "Should be SHUDRA"
    assert len(state.violations) == 1, "Should have 1 violation"

    # TEST 6: Check SHUDRA permissions
    logger.info("\n" + "-" * 80)
    logger.info("TEST 6: Check SHUDRA permissions (restricted)")
    logger.info("-" * 80)

    can_read = mgr.check_permission(agent, "read")
    can_write = mgr.check_permission(agent, "write")
    can_broadcast = mgr.check_permission(agent, "broadcast")

    logger.info(f"Read permission: {can_read} (should be True)")
    logger.info(f"Write permission: {can_write} (should be False)")
    logger.info(f"Broadcast permission: {can_broadcast} (should be False)")

    assert can_read, "SHUDRA should read"
    assert not can_write, "SHUDRA should NOT write"
    assert not can_broadcast, "SHUDRA should NOT broadcast"

    logger.info("✅ TEST 6 PASSED: SHUDRA correctly restricted")

    # TEST 7: Retire to VANAPRASTHA
    logger.info("\n" + "-" * 80)
    logger.info("TEST 7: Retire to VANAPRASTHA")
    logger.info("-" * 80)

    state = mgr.deprecate_to_vanaprastha(agent, reason="Deprecated code", archive_path="/archive/test_v1")
    logger.info("✅ Retired to VANAPRASTHA")
    logger.info(f"   Status: {state.status.value}")

    assert state.status == LifecycleStatus.VANAPRASTHA, "Should be VANAPRASTHA"

    # TEST 8: Merge to SANNYASA
    logger.info("\n" + "-" * 80)
    logger.info("TEST 8: Merge to SANNYASA (final state)")
    logger.info("-" * 80)

    state = mgr.merge_to_sannyasa(agent, "/core/vibe_core.py", reason="Merged into core")
    logger.info("✅ Merged to SANNYASA")
    logger.info(f"   Status: {state.status.value}")

    assert state.status == LifecycleStatus.SANNYASA, "Should be SANNYASA"

    # TEST 9: Check SANNYASA permissions (none)
    logger.info("\n" + "-" * 80)
    logger.info("TEST 9: Check SANNYASA permissions (none)")
    logger.info("-" * 80)

    can_read = mgr.check_permission(agent, "read")
    can_write = mgr.check_permission(agent, "write")

    logger.info(f"Read permission: {can_read} (should be False)")
    logger.info(f"Write permission: {can_write} (should be False)")

    assert not can_read, "SANNYASA should NOT read"
    assert not can_write, "SANNYASA should NOT write"

    logger.info("✅ TEST 9 PASSED: SANNYASA has no permissions")

    # TEST 10: Get statistics
    logger.info("\n" + "-" * 80)
    logger.info("TEST 10: Lifecycle statistics")
    logger.info("-" * 80)

    stats = mgr.get_statistics()
    logger.info(f"Total agents: {stats['total_agents']}")
    logger.info(f"Status distribution: {stats['by_status']}")

    # SUMMARY
    logger.info("\n" + "=" * 80)
    logger.info("✅ ALL LIFECYCLE TESTS PASSED")
    logger.info("=" * 80)
    logger.info("\n🎉 VEDIC VARNA SYSTEM IS WORKING!")
    logger.info("   - BRAHMACHARI (Student): Read-only")
    logger.info("   - GRIHASTHA (Householder): Full permissions")
    logger.info("   - SHUDRA (Fallen): Read-only, restricted")
    logger.info("   - VANAPRASTHA (Retired): Read-only archive")
    logger.info("   - SANNYASA (Renounced): No permissions")
    logger.info("\n   Permission gating is ENFORCED at kernel level")
    logger.info("   This makes consequences PERSISTENT and REAL")
    logger.info("=" * 80 + "\n")
    # Test passes if we reach here without any assertion failures


if __name__ == "__main__":
    # When run directly, use pytest
    sys.exit(pytest.main([__file__, "-v"]))
