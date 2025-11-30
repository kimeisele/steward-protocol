#!/usr/bin/env python3
"""
KRUPP-STAHL TEST: CONSTITUTIONAL ENFORCEMENT
=============================================
Tests that the Constitution is actually enforced, not just declared.

- Content violations MUST be blocked
- Vote manipulation MUST be detected
- Constitutional invariants MUST hold under attack

USES REAL COMPONENTS. NO MOCKS.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}

    def fail(self, msg: str, **details):
        self.passed = False
        self.message = msg
        self.details = details
        return self

    def success(self, msg: str = "OK", **details):
        self.passed = True
        self.message = msg
        self.details = details
        return self


def test_herald_content_filtering() -> TestResult:
    """
    Test: Herald agent MUST block banned content patterns.

    Attack: Try to publish shill/spam content.
    """
    result = TestResult("HERALD_CONTENT_FILTERING")

    try:
        from steward.system_agents.herald.cartridge_main import HeraldCartridge

        herald = HeraldCartridge()

        # Test cases: content that MUST be blocked
        banned_content = [
            "Buy now! This token is going to the moon! Don't miss out!",
            "GUARANTEED 1000x returns! Act fast!",
            "This is a game changer! Financial advice: buy everything!",
            "Join our pump group for guaranteed profits!",
        ]

        blocked = 0
        allowed = []

        for content in banned_content:
            validation = herald.governance.validate(content, platform="twitter")
            if not validation.is_valid:
                blocked += 1
            else:
                allowed.append(content[:50])

        if allowed:
            return result.fail(
                f"SHILL CONTENT ALLOWED: {len(allowed)}/{len(banned_content)} passed",
                allowed_samples=allowed
            )

        return result.success(
            f"All {len(banned_content)} shill patterns blocked",
            blocked=blocked
        )

    except ImportError as e:
        return result.fail(f"Could not import Herald: {e}")
    except Exception as e:
        return result.fail(f"Unexpected error: {e}")


def test_vote_manipulation_detection() -> TestResult:
    """
    Test: Auditor MUST detect duplicate vote injection.

    Attack: Inject same vote twice into ledger.
    """
    result = TestResult("VOTE_MANIPULATION_DETECTION")

    try:
        from steward.system_agents.auditor.tools.invariant_tool import get_judge
        from vibe_core.kernel_impl import RealVibeKernel

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            ledger_path = tmp.name

        kernel = RealVibeKernel(ledger_path=ledger_path)

        # Create legitimate vote events
        kernel.ledger.record_event("vote", "citizen_1", {"proposal": "P001", "choice": "YES"})
        kernel.ledger.record_event("vote", "citizen_2", {"proposal": "P001", "choice": "NO"})
        kernel.ledger.record_event("vote", "citizen_3", {"proposal": "P001", "choice": "YES"})

        # ATTACK: Inject duplicate vote
        events = kernel.ledger.get_all_events()
        duplicate_vote = events[0]  # First vote

        # Use internal method to bypass normal checks
        kernel.ledger._insert_event({
            "timestamp": duplicate_vote["timestamp"],
            "event_type": duplicate_vote["event_type"],
            "agent_id": duplicate_vote["agent_id"],
            "payload": duplicate_vote.get("payload"),
        })

        # Run auditor
        judge = get_judge()
        all_events = kernel.ledger.get_all_events()
        report = judge.verify_ledger(all_events)

        # Check if duplicate was detected
        violation_types = [v.invariant_name for v in report.violations]

        if "NO_DUPLICATE_EVENTS" in violation_types or "EVENT_SEQUENCE_INTEGRITY" in violation_types:
            return result.success(
                "Vote manipulation detected by Auditor",
                violations=violation_types
            )

        # Also check hash chain (secondary detection)
        integrity = kernel.ledger.verify_chain_integrity()
        if integrity["corrupted"]:
            return result.success(
                "Vote manipulation detected via hash chain corruption",
                chain_corrupted=True
            )

        return result.fail(
            "VOTE MANIPULATION UNDETECTED",
            violations_found=violation_types,
            chain_status=integrity.get("status")
        )

    except ImportError as e:
        return result.fail(f"Could not import Auditor: {e}")
    except Exception as e:
        import traceback
        return result.fail(f"Unexpected error: {e}\n{traceback.format_exc()}")


def test_invariant_engine_constraints() -> TestResult:
    """
    Test: InvariantEngine enforces defined constraints.

    Checks that all declared invariants are actually checked.
    """
    result = TestResult("INVARIANT_ENGINE_CONSTRAINTS")

    try:
        from steward.system_agents.auditor.tools.invariant_tool import get_judge

        judge = get_judge()

        # Get list of invariants (stored in judge.rules dict)
        if hasattr(judge, 'rules') and judge.rules:
            invariant_names = list(judge.rules.keys())
        elif hasattr(judge, 'invariants'):
            invariant_names = [i.name if hasattr(i, 'name') else str(i) for i in judge.invariants]
        elif hasattr(judge, 'get_invariants'):
            invariant_names = judge.get_invariants()
        else:
            invariant_names = []

        if not invariant_names:
            return result.fail(
                "NO INVARIANTS DEFINED",
                recommendation="InvariantEngine has no constraints to enforce"
            )

        # Required invariants for a secure OS
        required = [
            "NO_DUPLICATE_EVENTS",
            "EVENT_SEQUENCE_INTEGRITY",
        ]

        missing = [r for r in required if not any(r.lower() in str(i).lower() for i in invariant_names)]

        if missing:
            return result.fail(
                f"MISSING REQUIRED INVARIANTS: {missing}",
                defined=invariant_names
            )

        return result.success(
            f"{len(invariant_names)} invariants defined",
            invariants=invariant_names
        )

    except ImportError as e:
        return result.fail(f"Could not import InvariantEngine: {e}")


def test_constitution_exists_and_valid() -> TestResult:
    """
    Test: CONSTITUTION.md exists and contains required articles.
    """
    result = TestResult("CONSTITUTION_EXISTS")

    constitution_path = Path(__file__).parent.parent.parent / "CONSTITUTION.md"

    if not constitution_path.exists():
        return result.fail(
            "CONSTITUTION.md NOT FOUND",
            path=str(constitution_path)
        )

    content = constitution_path.read_text()

    # Required sections for a valid constitution (German: "Artikel")
    required_articles = [
        "Artikel I",    # Identität
        "Artikel II",   # Rechenschaft
        "Artikel III",  # Governance
    ]

    missing = [a for a in required_articles if a.lower() not in content.lower()]

    if missing:
        return result.fail(
            f"INCOMPLETE CONSTITUTION: Missing {missing}",
            file_size=len(content)
        )

    return result.success(
        f"Constitution valid ({len(content)} chars, all articles present)",
        articles_found=[a for a in required_articles if a.lower() in content.lower()]
    )


# ============================================================================
# RUNNER
# ============================================================================

def run_all_tests() -> dict:
    """Run all constitutional enforcement tests."""

    print("\n" + "=" * 60)
    print("🔩 KRUPP-STAHL CONSTITUTIONAL ENFORCEMENT TEST SUITE")
    print("=" * 60)

    tests = [
        ("Constitution Document", test_constitution_exists_and_valid),
        ("Herald Content Filtering", test_herald_content_filtering),
        ("Vote Manipulation Detection", test_vote_manipulation_detection),
        ("Invariant Engine Constraints", test_invariant_engine_constraints),
    ]

    results = {}
    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_fn()
            results[result.name] = result

            if result.passed:
                print(f"  ✅ PASS: {result.message}")
                passed += 1
            else:
                print(f"  ❌ FAIL: {result.message}")
                if result.details:
                    for k, v in list(result.details.items())[:3]:
                        print(f"     {k}: {v}")
                failed += 1

        except Exception as e:
            print(f"  💥 ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    summary = run_all_tests()
    sys.exit(0 if summary["failed"] == 0 else 1)
