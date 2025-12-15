#!/usr/bin/env python3
"""
OPUS-075: MANAS Fortress Verification

Tests that MANAS has proper impulse control:
- High confidence + safe target → auto-execute
- High confidence + protected zone → BLOCKED
- Low confidence → ask human
- Step limit → ask human
"""

import sys
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

    def __post_init__(self):
        if self.targets is None:
            self.targets = []


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


if __name__ == "__main__":
    sys.exit(test_fortress())
