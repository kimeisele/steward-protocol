#!/usr/bin/env python3
"""
VERIFICATION SCRIPT: Check kernel ledger integrity.

This script performs real actions through agents and verifies they are
recorded in the kernel ledger (not just in local files).

HYPOTHESIS:
- Current state: Agents write to local files but NOT to kernel ledger
- Expected: All actions MUST go through kernel.ledger.record()
"""

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.WARNING)  # Quiet to see results
logger = logging.getLogger("VERIFY_LEDGER")


def verify_ledger_integrity():
    """Run an action and check if it's recorded in kernel ledger."""
    logger.warning("\n" + "=" * 70)
    logger.warning("LEDGER INTEGRITY TEST")
    logger.warning("=" * 70)

    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    try:
        # Boot kernel with agents
        from vibe_core.kernel_impl import RealVibeKernel
        from herald.cartridge_main import HeraldCartridge
        from civic.cartridge_main import CivicCartridge
        from forum.cartridge_main import ForumCartridge
        from science.cartridge_main import ScientistCartridge
        from envoy.cartridge_main import EnvoyCartridge

        kernel = RealVibeKernel()

        agents_to_register = [
            ("herald", HeraldCartridge()),
            ("civic", CivicCartridge()),
            ("forum", ForumCartridge()),
            ("science", ScientistCartridge()),
            ("envoy", EnvoyCartridge()),
        ]

        for agent_id, agent_instance in agents_to_register:
            kernel.register_agent(agent_instance)

        kernel.boot()

        logger.warning(f"\n✅ Kernel booted with {len(kernel.agent_registry)} agents")

        # Get ledger state BEFORE action
        ledger_before = kernel.dump_ledger()
        events_before = len(ledger_before)
        logger.warning(f"📊 Ledger events BEFORE action: {events_before}")

        # Execute an action: Create a proposal
        logger.warning(f"\n🔄 Creating a proposal through FORUM...")
        forum = kernel.agent_registry.get("forum")

        if not forum:
            logger.error("❌ FORUM agent not found")
            return False

        proposal = forum.create_proposal(
            title="Test Ledger Integrity",
            description="This proposal should record in kernel ledger",
            proposer="herald",
            action={"type": "credit_transfer", "params": {"to": "civic", "amount": 10}}
        )

        logger.warning(f"✅ Proposal created: {proposal['id']}")

        # Get ledger state AFTER action
        ledger_after = kernel.dump_ledger()
        events_after = len(ledger_after)
        logger.warning(f"📊 Ledger events AFTER action: {events_after}")

        # Check if ledger was updated
        delta = events_after - events_before

        logger.warning(f"\n" + "=" * 70)
        logger.warning("RESULTS")
        logger.warning("=" * 70)

        if delta == 0:
            logger.error(f"❌ FAIL: Ledger unchanged! (Events: {events_before} → {events_after})")
            logger.error(f"   Action was performed but NOT recorded in kernel ledger.")
            logger.error(f"   DIAGNOSIS: Agent is writing to local files, bypassing kernel.")
            return False

        elif delta > 0:
            logger.warning(f"✅ PASS: Ledger recorded action! (Events: {events_before} → {events_after})")
            logger.warning(f"   {delta} new event(s) in ledger")

            # Show new events
            logger.warning(f"\n   New ledger entries:")
            for event in ledger_after[-delta:]:
                event_type = event.get('event_type', 'UNKNOWN')
                details = event.get('details', {})
                if isinstance(details, str):
                    details = json.loads(details) if details else {}
                logger.warning(f"      - {event_type}: {details.get('proposal_id', details.get('title', '...'))}")

            return True

        else:
            logger.error(f"❌ CRITICAL: Ledger decreased! (Events: {events_before} → {events_after})")
            return False

    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run verification."""
    success = verify_ledger_integrity()

    if success:
        print("\n🎉 LEDGER INTEGRITY VERIFIED\n")
        return 0
    else:
        print("\n🔴 LEDGER INTEGRITY FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
