#!/usr/bin/env python3
"""
TEST: LIFECYCLE ENFORCER - Demonstrating that the simulation is REAL (not a mock)

This test shows the progression:
1. New agent registers as BRAHMACHARI (Student) - READ-ONLY
2. Agent tries to broadcast -> REJECTED by LIFECYCLE ENFORCER
3. Agent gets TEMPLE (Science) initiation -> Promoted to GRIHASTHA
4. Agent broadcasts -> SUCCESS with karma (ledger) recorded
5. Agent violates Constitution -> DEMOTED to SHUDRA
6. Agent tries to broadcast -> REJECTED (fallen status)

This is the ESSENCE of what makes it REAL:
- Persistent state (ledger)
- Enforceable consequences (lifecycle gates)
- Proper progression (student -> householder -> fallen -> retired)
"""

import logging
import sys
from datetime import datetime, timezone

import pytest

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TEST_LIFECYCLE")


def test_lifecycle_enforcer():
    """Run comprehensive lifecycle tests."""
    logger.info("\n" + "=" * 80)
    logger.info("LIFECYCLE ENFORCER TEST SUITE")
    logger.info("=" * 80)

    try:
        from steward.system_agents.civic.tools.lifecycle_enforcer import LifecycleEnforcer
        from steward.system_agents.civic.tools.lifecycle_manager import LifecycleStatus
    except ImportError as e:
        pytest.skip(f"Could not import lifecycle modules: {e}")

    # Initialize enforcer
    enforcer = LifecycleEnforcer()
    logger.info("LifecycleEnforcer initialized")

    # TEST 1: Register new agent as BRAHMACHARI
    logger.info("\n" + "-" * 80)
    logger.info("TEST 1: Register new agent as BRAHMACHARI (Student)")
    logger.info("-" * 80)

    test_agent = "test_pulse"
    state = enforcer.lifecycle_mgr.register_new_agent(test_agent)
    logger.info(f"Agent {test_agent} registered")
    logger.info(f"   Status: {state.status.value}")
    logger.info(f"   Varna: {state.varna}")

    # Compare status (handle enum vs string serialization)
    status_val = state.status.value if hasattr(state.status, "value") else str(state.status)
    assert (
        status_val.lower() == LifecycleStatus.BRAHMACHARI.value.lower()
    ), f"TEST 1 FAILED: Agent not BRAHMACHARI (got {status_val})"

    # TEST 2: Try to broadcast as BRAHMACHARI -> SHOULD BE REJECTED
    logger.info("\n" + "-" * 80)
    logger.info("TEST 2: BRAHMACHARI tries to broadcast -> SHOULD REJECT")
    logger.info("-" * 80)

    permission = enforcer.check_action_permission(test_agent, "write", cost=1)
    logger.info("Permission check result:")
    logger.info(f"   Permitted: {permission.permitted}")
    logger.info(f"   Reason: {permission.reason}")
    logger.info(f"   Status: {permission.lifecycle_status}")

    assert not permission.permitted, "TEST 2 FAILED: BRAHMACHARI should NOT have write permission"
    logger.info("TEST 2 PASSED: BRAHMACHARI correctly blocked from writing")

    # TEST 3: Initiate agent to GRIHASTHA (simulating TEMPLE passing tests)
    logger.info("\n" + "-" * 80)
    logger.info("TEST 3: TEMPLE initiates BRAHMACHARI -> GRIHASTHA")
    logger.info("-" * 80)

    test_results = {
        "passed": True,
        "tests": ["philosophy_101", "coding_ethics", "constitutional_oath"],
        "score": 95,
    }

    success = enforcer.authorize_brahmachari_to_grihastha(test_agent, test_results, initiator="TEMPLE")
    assert success, "TEST 3 FAILED: Initiation failed"

    # Verify state changed
    state = enforcer.lifecycle_mgr.get_lifecycle_state(test_agent)
    assert (
        state.status == LifecycleStatus.GRIHASTHA
    ), f"TEST 3 FAILED: Status is {state.status.value}, expected GRIHASTHA"
    logger.info("TEST 3 PASSED: Agent promoted to GRIHASTHA")

    # TEST 4: Try to broadcast as GRIHASTHA -> SHOULD SUCCEED
    logger.info("\n" + "-" * 80)
    logger.info("TEST 4: GRIHASTHA tries to broadcast -> SHOULD PERMIT")
    logger.info("-" * 80)

    permission = enforcer.check_action_permission(test_agent, "write", cost=1)
    logger.info("Permission check result:")
    logger.info(f"   Permitted: {permission.permitted}")
    logger.info(f"   Reason: {permission.reason}")
    logger.info(f"   Status: {permission.lifecycle_status}")

    assert permission.permitted, "TEST 4 FAILED: GRIHASTHA should have write permission"
    logger.info("TEST 4 PASSED: GRIHASTHA correctly permitted to write")

    # TEST 5: Report a violation -> Demote to SHUDRA
    logger.info("\n" + "-" * 80)
    logger.info("TEST 5: Violation reported -> Demote to SHUDRA (Fallen)")
    logger.info("-" * 80)

    violation = {
        "type": "constitutional_violation",
        "reason": "Attempted to bypass LIFECYCLE ENFORCER",
        "severity": "high",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    success = enforcer.report_violation(test_agent, violation)
    assert success, "TEST 5 FAILED: Violation report failed"

    state = enforcer.lifecycle_mgr.get_lifecycle_state(test_agent)
    assert state.status == LifecycleStatus.SHUDRA, f"TEST 5 FAILED: Status is {state.status.value}, expected SHUDRA"
    logger.info("TEST 5 PASSED: Agent demoted to SHUDRA")

    # TEST 6: Try to broadcast as SHUDRA -> SHOULD REJECT
    logger.info("\n" + "-" * 80)
    logger.info("TEST 6: SHUDRA tries to broadcast -> SHOULD REJECT")
    logger.info("-" * 80)

    permission = enforcer.check_action_permission(test_agent, "write", cost=1)
    logger.info("Permission check result:")
    logger.info(f"   Permitted: {permission.permitted}")
    logger.info(f"   Reason: {permission.reason}")
    logger.info(f"   Status: {permission.lifecycle_status}")

    assert not permission.permitted, "TEST 6 FAILED: SHUDRA should NOT have write permission"
    logger.info("TEST 6 PASSED: SHUDRA correctly blocked from writing")

    # TEST 7: Verify persistence - Reload and check state survives
    logger.info("\n" + "-" * 80)
    logger.info("TEST 7: Verify KARMA (persistence) - State survives restart")
    logger.info("-" * 80)

    # Create new instance (simulating restart)
    logger.info("   Creating new LifecycleManager instance (simulating server restart)...")
    from steward.system_agents.civic.tools.lifecycle_manager import LifecycleManager

    manager2 = LifecycleManager()
    state_after = manager2.get_lifecycle_state(test_agent)

    assert state_after, "TEST 7 FAILED: State not persisted"
    assert (
        state_after.status == LifecycleStatus.SHUDRA
    ), f"TEST 7 FAILED: Persisted state is {state_after.status.value}, expected SHUDRA"
    logger.info("TEST 7 PASSED: KARMA confirmed - state persisted across restart")
    logger.info(f"   Agent {test_agent} still SHUDRA after simulated restart")

    # TEST 8: Deprecate to VANAPRASTHA
    logger.info("\n" + "-" * 80)
    logger.info("TEST 8: Deprecate agent to VANAPRASTHA (Retired)")
    logger.info("-" * 80)

    state = enforcer.lifecycle_mgr.deprecate_to_vanaprastha(
        test_agent,
        reason="Code deprecated in favor of newer version",
        archive_path="/archive/test_pulse_v1",
    )

    assert state.status == LifecycleStatus.VANAPRASTHA, f"TEST 8 FAILED: Not VANAPRASTHA (got {state.status.value})"
    logger.info("TEST 8 PASSED: Agent retired to VANAPRASTHA")

    # TEST 9: Get statistics
    logger.info("\n" + "-" * 80)
    logger.info("TEST 9: Enforcement statistics")
    logger.info("-" * 80)

    stats = enforcer.get_enforcement_status()
    logger.info(f"Enforcer Status: {stats['enforcer_active']}")
    logger.info(f"Enforcer Type: {stats['enforcer_type']}")
    logger.info(f"Permission Gates: {stats['permission_gates_enabled']}")
    logger.info(f"Lifecycle Stats: {stats['lifecycle_statistics']}")

    # SUMMARY
    logger.info("\n" + "=" * 80)
    logger.info("ALL TESTS PASSED")
    logger.info("=" * 80)
    logger.info("\nLIFECYCLE ENFORCER IS WORKING!")
    logger.info("   - New agents register as BRAHMACHARI (read-only)")
    logger.info("   - Permission gates REJECT unqualified actions")
    logger.info("   - TEMPLE can initiate agents to GRIHASTHA")
    logger.info("   - Violations demote agents to SHUDRA")
    logger.info("   - State persists across restarts (KARMA)")
    logger.info("   - This is NOT a mock - consequences are REAL")
    logger.info("\nThe simulation is now bound by KARMA and DHARMA")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
