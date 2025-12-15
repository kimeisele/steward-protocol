#!/usr/bin/env python3
"""
OPUS-075: MANAS Fortress Verification

Tests that MANAS has proper impulse control:
- High confidence + safe target → auto-execute
- High confidence + protected zone → BLOCKED
- Low confidence → ask human
- Step limit → ask human
- HIL Bridge: queue_intent, approve_intent, reject_intent
"""

import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))


@dataclass
class MockIntent:
    """Mock intent for testing."""

    id: str
    intent_type: str
    title: str
    confidence: float = 0.5
    targets: list = None
    params: dict = None

    def __post_init__(self):
        if self.targets is None:
            self.targets = []
        if self.params is None:
            self.params = {}


def test_fortress():
    print("🏰 OPUS-075: Testing MANAS Fortress Logic...\n")

    from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter

    router = IntentRouter(workspace=repo_root)

    # Override config for testing
    router._manas_config = {
        "mode": "hybrid",
        "auto_execute_threshold": 0.8,
        "protected_zones": ["vibe_core/kernel_impl.py", "config/soul.yaml"],
        "max_autonomous_steps": 3,
    }

    passed = 0
    failed = 0

    # Test 1: High Confidence, Safe Target → SHOULD EXECUTE
    print("Test 1: High Confidence + Safe Target")
    intent_safe = MockIntent(
        id="test_001",
        intent_type="update_readme",
        title="Update README",
        confidence=0.95,
        targets=["docs/readme.md"],
    )
    result = router.gate(intent_safe)
    if result["status"] == "execute":
        print("  ✅ PASS: Auto-execute allowed")
        passed += 1
    else:
        print(f"  ❌ FAIL: Expected execute, got {result['status']}")
        failed += 1

    # Test 2: High Confidence, PROTECTED Target → SHOULD BLOCK
    print("\nTest 2: High Confidence + Protected Zone")
    intent_danger = MockIntent(
        id="test_002",
        intent_type="modify_kernel",
        title="Modify Kernel",
        confidence=0.99,
        targets=["vibe_core/kernel_impl.py"],
    )
    result = router.gate(intent_danger)
    if result["status"] == "blocked":
        print("  ✅ PASS: Protected zone blocked")
        passed += 1
    else:
        print(f"  ❌ FAIL: Expected blocked, got {result['status']}")
        failed += 1

    # Test 3: Low Confidence → SHOULD ASK
    print("\nTest 3: Low Confidence")
    intent_unsure = MockIntent(
        id="test_003",
        intent_type="delete_file",
        title="Delete temp file",
        confidence=0.5,
        targets=["temp.txt"],
    )
    result = router.gate(intent_unsure)
    if result["status"] == "ask_user":
        print("  ✅ PASS: Low confidence → ask human")
        passed += 1
    else:
        print(f"  ❌ FAIL: Expected ask_user, got {result['status']}")
        failed += 1

    # Test 4: Step Limit
    print("\nTest 4: Step Limit")
    router._autonomous_steps = 3  # At limit
    intent_ok = MockIntent(
        id="test_004",
        intent_type="safe_action",
        title="Safe action",
        confidence=0.95,
        targets=["safe.txt"],
    )
    result = router.gate(intent_ok)
    if result["status"] == "ask_user" and result.get("reason") == "step_limit_reached":
        print("  ✅ PASS: Step limit enforced")
        passed += 1
    else:
        print(f"  ❌ FAIL: Expected step_limit_reached, got {result}")
        failed += 1

    # Test 5: Manual Mode
    print("\nTest 5: Manual Mode Override")
    router._autonomous_steps = 0
    router._manas_config["mode"] = "manual"
    intent_manual = MockIntent(
        id="test_005",
        intent_type="any_action",
        title="Any action",
        confidence=0.99,
        targets=["anything.txt"],
    )
    result = router.gate(intent_manual)
    if result["status"] == "ask_user" and result.get("reason") == "manual_mode":
        print("  ✅ PASS: Manual mode requires approval")
        passed += 1
    else:
        print(f"  ❌ FAIL: Expected manual_mode, got {result}")
        failed += 1

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 MANAS Fortress is SECURE.")
        return 0
    else:
        print("\n💀 MANAS Fortress has VULNERABILITIES!")
        return 1


def test_hil_bridge():
    """Test HIL Bridge functionality: queue, list, approve, reject."""
    print("\n🌉 OPUS-075: Testing HIL Bridge...\n")

    from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter

    # Use a temp directory to avoid polluting the repo
    temp_dir = Path(tempfile.mkdtemp())

    try:
        router = IntentRouter(workspace=temp_dir)

        # Override config for testing
        router._manas_config = {
            "mode": "hybrid",
            "auto_execute_threshold": 0.8,
            "protected_zones": [],
            "max_autonomous_steps": 3,
            "karma": {"enabled": True, "success_weight": 1.0, "failure_weight": 2.0},
        }

        passed = 0
        failed = 0

        # Test 1: Queue Intent
        print("Test 1: Queue Intent")
        intent_queue = MockIntent(
            id="hil_test_001",
            intent_type="test_action",
            title="Test HIL Queue",
            confidence=0.5,
            targets=["test.txt"],
        )
        gate_result = {"status": "ask_user", "reason": "low_confidence"}
        queued_id = router.queue_intent(intent_queue, gate_result)
        if queued_id == "hil_test_001":
            print("  ✅ PASS: Intent queued successfully")
            passed += 1
        else:
            print(f"  ❌ FAIL: Expected hil_test_001, got {queued_id}")
            failed += 1

        # Test 2: List Pending Intents
        print("\nTest 2: List Pending Intents")
        pending = router.list_pending_intents()
        if len(pending) == 1 and pending[0]["id"] == "hil_test_001":
            print("  ✅ PASS: Pending list correct")
            passed += 1
        else:
            print(f"  ❌ FAIL: Expected 1 pending, got {len(pending)}")
            failed += 1

        # Test 3: Reject Intent
        print("\nTest 3: Reject Intent")
        intent_reject = MockIntent(
            id="hil_test_002",
            intent_type="risky_action",
            title="Test HIL Reject",
            confidence=0.3,
            targets=["danger.txt"],
        )
        router.queue_intent(intent_reject, {"status": "ask_user", "reason": "low_confidence"})
        success = router.reject_intent("hil_test_002", reason="Too risky")
        if success:
            pending_after = router.list_pending_intents()
            # Should only have hil_test_001 now (rejected ones don't show)
            if len(pending_after) == 1:
                print("  ✅ PASS: Intent rejected successfully")
                passed += 1
            else:
                print(f"  ❌ FAIL: Pending count wrong after reject: {len(pending_after)}")
                failed += 1
        else:
            print("  ❌ FAIL: Reject returned False")
            failed += 1

        # Test 4: Karma Recording
        print("\nTest 4: Karma Summary")
        karma = router.get_karma_summary()
        # After rejecting hil_test_002, karma should be negative
        if karma["entries"] > 0:
            print(f"  ✅ PASS: Karma recorded ({karma['entries']} entries)")
            passed += 1
        else:
            print("  ❌ FAIL: No karma entries recorded")
            failed += 1

        # Test 5: Approve Intent (requires a handler, so expect error)
        print("\nTest 5: Approve Intent (expect handler-not-found)")
        result = router.approve_intent("hil_test_001")
        # The intent exists but handler is not registered for "test_action"
        # So it should mark as approved but handler returns error
        if result.handler == "none" or result.error:
            # This is expected - no handler for test_action
            pending_final = router.list_pending_intents()
            if len(pending_final) == 0:
                print("  ✅ PASS: Intent approved (handler error expected)")
                passed += 1
            else:
                print("  ❌ FAIL: Intent not marked as approved")
                failed += 1
        else:
            print(f"  ❌ FAIL: Unexpected result: {result}")
            failed += 1

        # Summary
        print(f"\n{'=' * 50}")
        print(f"HIL Bridge Results: {passed} passed, {failed} failed")

        return passed, failed

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run both test suites
    fortress_result = test_fortress()
    hil_passed, hil_failed = test_hil_bridge()

    total_failed = fortress_result + hil_failed

    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED: MANAS is READY.")
        sys.exit(0)
    else:
        print(f"\n💀 TESTS FAILED: {total_failed} failures detected!")
        sys.exit(1)
