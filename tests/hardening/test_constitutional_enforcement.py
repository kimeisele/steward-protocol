#!/usr/bin/env python3
"""
KRUPP-STAHL TEST: CONSTITUTIONAL ENFORCEMENT
=============================================
Tests that the Constitution is actually enforced, not just declared.

- Content violations MUST be blocked
- Vote manipulation MUST be detected
- Constitutional invariants MUST hold under attack

USES REAL COMPONENTS. NO MOCKS.

MIGRATION NOTE (2024-12):
    Uses standardized TestAgents fixtures from test_orchestration plugin.
    Kernel tests use governance_kernel/test_kernel fixtures.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.hardening
def test_herald_content_filtering():
    """
    Test: Herald agent MUST block banned content patterns.

    Attack: Try to publish shill/spam content.
    """
    try:
        from vibe_core.cartridges.system.herald.cartridge_main import HeraldCartridge

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

        assert not allowed, f"SHILL CONTENT ALLOWED: {len(allowed)}/{len(banned_content)} passed - samples: {allowed}"
        print(f"All {len(banned_content)} shill patterns blocked")

    except ImportError as e:
        pytest.skip(f"Could not import Herald: {e}")


@pytest.mark.hardening
@pytest.mark.slow
def test_vote_manipulation_detection():
    """
    Test: Auditor MUST detect duplicate vote injection.

    Attack: Inject same vote twice into ledger.

    Note: Uses RealVibeKernel directly because attack requires raw SQL injection
    on a file-based ledger. TestKernel.minimal() uses :memory: by default.
    """
    try:
        from vibe_core.cartridges.system.auditor.tools.invariant_tool import get_judge
        from vibe_core.kernel_impl import RealVibeKernel

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            ledger_path = tmp.name

        # Use RealVibeKernel with file ledger for SQL attack simulation
        kernel = RealVibeKernel(ledger_path=ledger_path, load_plugins=False)

        # Create legitimate vote events
        kernel.ledger.record_event("vote", "citizen_1", {"proposal": "P001", "choice": "YES"})
        kernel.ledger.record_event("vote", "citizen_2", {"proposal": "P001", "choice": "NO"})
        kernel.ledger.record_event("vote", "citizen_3", {"proposal": "P001", "choice": "YES"})

        # ATTACK: Inject duplicate vote
        events = kernel.ledger.get_all_events()
        duplicate_vote = events[0]  # First vote

        # Use internal method to bypass normal checks
        kernel.ledger._insert_event(
            {
                "timestamp": duplicate_vote["timestamp"],
                "event_type": duplicate_vote["event_type"],
                "agent_id": duplicate_vote["agent_id"],
                "payload": duplicate_vote.get("payload"),
            }
        )

        # Run auditor
        judge = get_judge()
        all_events = kernel.ledger.get_all_events()
        report = judge.verify_ledger(all_events)

        # Check if duplicate was detected
        violation_types = [v.invariant_name for v in report.violations]

        if "NO_DUPLICATE_EVENTS" in violation_types or "EVENT_SEQUENCE_INTEGRITY" in violation_types:
            print(f"Vote manipulation detected by Auditor: {violation_types}")
            return  # Test passes

        # Also check hash chain (secondary detection)
        integrity = kernel.ledger.verify_chain_integrity()
        if integrity["corrupted"]:
            print("Vote manipulation detected via hash chain corruption")
            return  # Test passes

        pytest.fail(f"VOTE MANIPULATION UNDETECTED - violations: {violation_types}, chain: {integrity.get('status')}")

    except ImportError as e:
        pytest.skip(f"Could not import Auditor: {e}")


@pytest.mark.hardening
def test_invariant_engine_constraints():
    """
    Test: InvariantEngine enforces defined constraints.

    Checks that all declared invariants are actually checked.
    """
    try:
        from vibe_core.cartridges.system.auditor.tools.invariant_tool import get_judge

        judge = get_judge()

        # Get list of invariants (stored in judge.rules dict)
        if hasattr(judge, "rules") and judge.rules:
            invariant_names = list(judge.rules.keys())
        elif hasattr(judge, "invariants"):
            invariant_names = [i.name if hasattr(i, "name") else str(i) for i in judge.invariants]
        elif hasattr(judge, "get_invariants"):
            invariant_names = judge.get_invariants()
        else:
            invariant_names = []

        assert invariant_names, "NO INVARIANTS DEFINED - InvariantEngine has no constraints to enforce"

        # Required invariants for a secure OS
        required = [
            "NO_DUPLICATE_EVENTS",
            "EVENT_SEQUENCE_INTEGRITY",
        ]

        missing = [r for r in required if not any(r.lower() in str(i).lower() for i in invariant_names)]

        assert not missing, f"MISSING REQUIRED INVARIANTS: {missing} - defined: {invariant_names}"

        print(f"{len(invariant_names)} invariants defined: {invariant_names}")

    except ImportError as e:
        pytest.skip(f"Could not import InvariantEngine: {e}")


@pytest.mark.hardening
def test_constitution_exists_and_valid():
    """
    Test: CONSTITUTION.md exists and contains required articles.
    """
    constitution_path = Path(__file__).parent.parent.parent / "CONSTITUTION.md"

    assert constitution_path.exists(), f"CONSTITUTION.md NOT FOUND at {constitution_path}"

    content = constitution_path.read_text()

    # Required sections for a valid constitution (German: "Artikel")
    required_articles = [
        "Artikel I",  # Identität
        "Artikel II",  # Rechenschaft
        "Artikel III",  # Governance
    ]

    missing = [a for a in required_articles if a.lower() not in content.lower()]

    assert not missing, f"INCOMPLETE CONSTITUTION: Missing {missing} (file size: {len(content)} chars)"

    found = [a for a in required_articles if a.lower() in content.lower()]
    print(f"Constitution valid ({len(content)} chars, articles found: {found})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
