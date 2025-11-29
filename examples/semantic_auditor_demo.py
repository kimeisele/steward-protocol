#!/usr/bin/env python3
"""
SEMANTIC AUDITOR DEMO - Live Examples

This script demonstrates the Judge and Watchdog in action.
Shows how semantic verification catches logical errors that
unit tests would miss.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

from steward.system_agents.auditor.tools.invariant_tool import (
    get_judge,
    InvariantEngine,
)
from steward.system_agents.auditor.tools.watchdog_tool import Watchdog, WatchdogConfig


def demo_section(title: str):
    """Print a demo section header"""
    print("\n" + "=" * 80)
    print(f"⚖️  {title}")
    print("=" * 80)


def demo_violation_broadcast_without_license():
    """Demo: The Judge catches BROADCAST without LICENSE_VALID"""
    demo_section("VIOLATION #1: BROADCAST Without License")

    print("\n📋 Scenario:")
    print("   HERALD tries to broadcast a message without getting license approval.")
    print("   Unit tests would pass ('does broadcast() run?')")
    print("   But semantically: INVALID (no authorization)")

    judge = InvariantEngine()

    events = [
        {
            "event_type": "BROADCAST",
            "task_id": "herald_task_1",
            "agent_id": "herald",
            "timestamp": "2025-11-24T15:00:00Z",
            "message": "Breaking news!",
        }
    ]

    print("\n📍 Event Ledger:")
    for i, event in enumerate(events):
        print(f"   [{i}] {event['event_type']} - agent:{event['agent_id']}")

    report = judge.verify_ledger(events)

    print(f"\n🔍 Verification Result: {'✅ PASS' if report.passed else '❌ FAIL'}")

    if not report.passed:
        for v in report.violations:
            print(f"\n   🚨 VIOLATION: {v.invariant_name}")
            print(f"      Severity: {v.severity}")
            print(f"      Message: {v.message}")
            print(f"      Rule: {v.context.get('rule_description')}")


def demo_valid_broadcast_sequence():
    """Demo: The Judge approves valid BROADCAST sequence"""
    demo_section("VALID SEQUENCE: BROADCAST With Proper License")

    print("\n📋 Scenario:")
    print("   CIVIC checks license → HERALD gets approval → HERALD broadcasts")
    print("   This is the CORRECT flow")

    judge = InvariantEngine()

    events = [
        {
            "event_type": "LICENSE_CHECK",
            "task_id": "civic_task_1",
            "agent_id": "civic",
            "timestamp": "2025-11-24T15:00:00Z",
        },
        {
            "event_type": "LICENSE_VALID",
            "task_id": "civic_task_1",
            "agent_id": "civic",
            "timestamp": "2025-11-24T15:00:10Z",
            "approved_agent": "herald",
        },
        {
            "event_type": "BROADCAST",
            "task_id": "civic_task_1",
            "agent_id": "herald",
            "timestamp": "2025-11-24T15:00:20Z",
            "message": "Licensed announcement",
        },
    ]

    print("\n📍 Event Ledger:")
    for i, event in enumerate(events):
        print(f"   [{i}] {event['event_type']:20} - agent:{event['agent_id']:6} @ {event['timestamp']}")

    report = judge.verify_ledger(events)

    print(f"\n🔍 Verification Result: {'✅ PASS' if report.passed else '❌ FAIL'}")

    if report.passed:
        print("\n   ✅ All invariants satisfied!")
        print("   ✅ BROADCAST was properly licensed")
    else:
        for v in report.violations:
            print(f"   ❌ {v.invariant_name}: {v.message}")


def demo_credit_transfer_without_proposal():
    """Demo: The Judge catches CREDIT_TRANSFER without PROPOSAL"""
    demo_section("VIOLATION #2: Credit Transfer Without Proposal")

    print("\n📋 Scenario:")
    print("   BANKER tries to transfer credits without community proposal.")
    print("   This bypasses governance!")

    judge = InvariantEngine()

    events = [
        {
            "event_type": "CREDIT_TRANSFER",
            "task_id": "banker_task_1",
            "agent_id": "banker",
            "timestamp": "2025-11-24T15:00:00Z",
            "amount": 1000,
            "to": "some_agent",
        }
    ]

    print("\n📍 Event Ledger:")
    for event in events:
        print(f"   {event['event_type']} - agent:{event['agent_id']}")

    report = judge.verify_ledger(events)

    print(f"\n🔍 Verification Result: {'✅ PASS' if report.passed else '❌ FAIL'}")

    if not report.passed:
        for v in report.violations:
            print(f"\n   🚨 VIOLATION: {v.invariant_name}")
            print(f"      Message: {v.message}")
            print(f"      Why: Credit transfers MUST follow community proposals")


def demo_orphaned_event():
    """Demo: The Judge catches incomplete events"""
    demo_section("VIOLATION #3: Orphaned Event (Missing task_id)")

    print("\n📋 Scenario:")
    print("   An event was recorded but is missing critical metadata.")
    print("   This could indicate a bug or attack.")

    judge = InvariantEngine()

    events = [
        {
            "event_type": "MYSTERIOUS_EVENT",
            "agent_id": "unknown",
            "timestamp": "2025-11-24T15:00:00Z",
            # Missing task_id!
        }
    ]

    print("\n📍 Event Ledger:")
    print(f"   {json.dumps(events[0], indent=6)}")

    report = judge.verify_ledger(events)

    print(f"\n🔍 Verification Result: {'✅ PASS' if report.passed else '❌ FAIL'}")

    if not report.passed:
        for v in report.violations:
            print(f"\n   🚨 VIOLATION: {v.invariant_name}")
            print(f"      Message: {v.message}")
            print(f"      Why: Every event must have complete metadata")


def demo_out_of_order_events():
    """Demo: The Judge detects temporal anomalies"""
    demo_section("VIOLATION #4: Events Out of Chronological Order")

    print("\n📋 Scenario:")
    print("   Events are timestamped incorrectly (maybe clock skew or attack?).")
    print("   This could cause causality violations.")

    judge = InvariantEngine()

    events = [
        {
            "event_type": "EVENT_1",
            "task_id": "task_a",
            "agent_id": "agent_x",
            "timestamp": "2025-11-24T15:00:30Z",
        },
        {
            "event_type": "EVENT_2",
            "task_id": "task_a",
            "agent_id": "agent_y",
            "timestamp": "2025-11-24T15:00:10Z",  # BEFORE the first event!
        },
    ]

    print("\n📍 Event Ledger:")
    for i, event in enumerate(events):
        print(f"   [{i}] {event['event_type']} @ {event['timestamp']}")

    report = judge.verify_ledger(events)

    print(f"\n🔍 Verification Result: {'✅ PASS' if report.passed else '❌ FAIL'}")

    if not report.passed:
        for v in report.violations:
            print(f"\n   🚨 VIOLATION: {v.invariant_name}")
            print(f"      Message: {v.message}")


def demo_duplicate_events():
    """Demo: The Judge catches replay attacks"""
    demo_section("VIOLATION #5: Duplicate Events (Replay Attack)")

    print("\n📋 Scenario:")
    print("   The same event appears twice in the ledger.")
    print("   This could be a replay attack or ledger corruption.")

    judge = InvariantEngine()

    events = [
        {
            "event_type": "BROADCAST",
            "task_id": "task_x",
            "agent_id": "herald",
            "timestamp": "2025-11-24T15:00:00Z",
            "message": "Important announcement",
        },
        {
            "event_type": "BROADCAST",
            "task_id": "task_x",
            "agent_id": "herald",
            "timestamp": "2025-11-24T15:00:00Z",  # EXACT DUPLICATE
            "message": "Important announcement",
        },
    ]

    print("\n📍 Event Ledger:")
    for i, event in enumerate(events):
        print(f"   [{i}] {event['event_type']} - {event['message']}")

    report = judge.verify_ledger(events)

    print(f"\n🔍 Verification Result: {'✅ PASS' if report.passed else '❌ FAIL'}")

    if not report.passed:
        for v in report.violations:
            print(f"\n   🚨 VIOLATION: {v.invariant_name}")
            print(f"      Message: {v.message}")
            print(f"      Why: Replay attacks are a critical security issue")


def demo_watchdog():
    """Demo: The Watchdog monitors in realtime"""
    demo_section("THE WATCHDOG: Continuous Runtime Monitoring")

    print("\n📋 How it works:")
    print("   1. Kernel runs normally")
    print("   2. Watchdog checks ledger every N tasks")
    print("   3. If violation found → Records VIOLATION event")
    print("   4. If CRITICAL → Halts system")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "ledger.jsonl"

        # Create test ledger
        print("\n📍 Creating test ledger with violation...")
        events = [
            {
                "event_type": "BOOT",
                "task_id": "t1",
                "agent_id": "kernel",
                "timestamp": "2025-11-24T15:00:00Z",
            },
            {
                "event_type": "BROADCAST",
                "task_id": "t1",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:00:10Z",
            },
            # Oops, no LICENSE_VALID!
        ]

        with open(ledger_path, "w") as f:
            for event in events:
                json.dump(event, f)
                f.write("\n")

        # Create watchdog
        config = WatchdogConfig(
            ledger_path=ledger_path,
            violations_path=Path(tmpdir) / "violations.jsonl",
            halt_on_critical=True,
        )

        watchdog = Watchdog(config)

        print(f"   ✅ Ledger created with {len(events)} events")

        # Run check
        print("\n📍 Running Watchdog check...")
        result = watchdog.check_invariants()

        print(f"\n   Status: {result['status']}")
        print(f"   New events checked: {result['new_events']}")
        print(f"   Violations found: {len(result['violations'])}")
        print(f"   System should halt: {watchdog.halt_requested}")

        if result["violations"]:
            print("\n   🚨 VIOLATIONS RECORDED:")
            for v in result["violations"]:
                print(f"      - {v['violation_type']}")


def demo_summary():
    """Summary of what we've learned"""
    demo_section("SUMMARY: The Three Layers of Verification")

    print(
        """
LAYER 1: Static Compliance (Traditional)
   ✅ Agents have valid cartridges
   ✅ Documentation is synced
   ✅ Event logs exist
   
   Problem: Doesn't check MEANING

LAYER 2: Semantic Verification (The JUDGE ⚖️)
   ✅ BROADCAST has LICENSE_VALID
   ✅ CREDIT_TRANSFER has PROPOSAL_PASSED
   ✅ No orphaned events
   ✅ Chronological order maintained
   ✅ No duplicate events
   ✅ Proposal workflow integrity
   
   Benefit: LAWS that never break

LAYER 3: Runtime Monitoring (The WATCHDOG 👁️)
   ✅ Continuous ledger monitoring
   ✅ Invariants checked every N tasks
   ✅ VIOLATION events recorded
   ✅ System can halt on CRITICAL
   
   Benefit: Catches problems LIVE

════════════════════════════════════════════════════════════════════════════════

KEY INSIGHT:

   Unit tests check: "Does the code run?"
   The Judge checks: "Does the code MEAN what it should?"
   The Watchdog checks: "Is the system healthy RIGHT NOW?"

Verification is no longer OPTIONAL. It's SYSTEM-IMMANENT.

This is how you build software with an IMMUNE SYSTEM. 🏰
"""
    )


def main():
    """Run all demos"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                    SEMANTIC AUDITOR DEMO                                   ║")
    print("║              The Judge ⚖️ and The Watchdog 👁️                              ║")
    print("║                                                                            ║")
    print("║  Demonstration of semantic verification in STEWARD Protocol               ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

    try:
        demo_violation_broadcast_without_license()
        demo_valid_broadcast_sequence()
        demo_credit_transfer_without_proposal()
        demo_orphaned_event()
        demo_out_of_order_events()
        demo_duplicate_events()
        demo_watchdog()
        demo_summary()

        print("\n✅ All demos completed successfully!\n")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
