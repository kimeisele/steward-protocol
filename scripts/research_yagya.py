#!/usr/bin/env python3
"""
THE RESEARCH YAGYA 🕯️
Sacred Ritual of Knowledge Acquisition

This script performs the Research Yagya - a coordinated operation where:
1. WATCHMAN (Kshatriya) verifies the temple is clean
2. CIVIC BANK prepares the offering (credits)
3. SCIENCE (Brahmin) performs research work
4. Results are preserved as sacred knowledge

No mocks. No fakes. Only real work.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Core imports
from civic.tools.economy import CivicBank
from watchman.cartridge_main import WatchmanCartridge
from science.cartridge_main import ScientistCartridge
from vibe_core import Task

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger("YAGYA")


def print_ritual(text: str):
    """Print ritual messages with spacing."""
    print(f"\n{text}")


def perform_yagya(topic: str = None, depth: str = "advanced"):
    """
    Perform the Research Yagya.

    Args:
        topic: Research topic (default: Autonomous Agent Economics)
        depth: Research depth - "quick", "standard", or "advanced"
    """

    if topic is None:
        topic = "Autonomous AI Agent Service Economy Models and Smart Contracts"

    print_ritual("🕉️  BEGINNING THE RESEARCH YAGYA...")
    print_ritual(f"📖 Research Topic: {topic}")
    print_ritual(f"⚡ Research Depth: {depth}")

    # Initialize the Priests (Load Agents)
    bank = CivicBank()
    watchman = WatchmanCartridge()
    scientist = ScientistCartridge()

    # ==================== STEP 1: TEMPLE CHECK ====================
    print_ritual("\n⚔️  KSHATRIYA CHECK (Watchman Patrol)...")
    try:
        patrol_result = watchman.run_patrol()
        print(json.dumps(patrol_result, indent=2))

        if patrol_result.get("status") != "clean":
            print_ritual("❌ TEMPLE UNCLEAN. ABORTING YAGYA.")
            print_ritual(f"Violations found: {patrol_result.get('violations', [])}")
            return False

        print_ritual("✅ Temple is clean. Proceeding with offering.")
    except Exception as e:
        print_ritual(f"❌ Patrol failed: {e}")
        return False

    # ==================== STEP 2: THE OFFERING ====================
    print_ritual("\n💰 THE OFFERING (Preparing Credits)...")
    try:
        science_balance = bank.get_balance("science")
        print_ritual(f"   Current Science Balance: {science_balance} Credits")

        # If Science doesn't have enough, grant them
        required_balance = 50
        if science_balance < required_balance:
            tx_id = bank.transfer(
                sender_id="MINT",
                receiver_id="science",
                amount=required_balance - science_balance,
                reason="YAGYA_GRANT",
                service_type="grant"
            )
            print_ritual(f"   ✓ Granted credits via TX: {tx_id}")
            science_balance = bank.get_balance("science")

        print_ritual(f"   ✓ Science Ready Balance: {science_balance} Credits")
    except Exception as e:
        print_ritual(f"❌ Offering failed: {e}")
        return False

    # ==================== STEP 3: IGNITE THE FIRE ====================
    print_ritual(f"\n🔥 IGNITING FIRE: Researching...")
    print_ritual(f"   Topic: {topic}")

    try:
        # Call the research method directly
        result = scientist.research_topic(topic)

        # Deduct API usage fee
        try:
            bank.transfer(
                sender_id="science",
                receiver_id="CIVIC",
                amount=5,
                reason="API_USAGE_FEE",
                service_type="platform_fee"
            )
            print_ritual("   ✓ 5 Credits sacrificed to Platform.")
        except Exception as fee_error:
            print_ritual(f"   ⚠️  Fee deduction failed (non-critical): {fee_error}")

    except Exception as e:
        print_ritual(f"❌ Research failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ==================== STEP 4: PRESERVE AS SACRED TEXT ====================
    print_ritual("\n🍎 PRASAD RECEIVED (Knowledge Preserved)...")

    try:
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("data/science/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"yagya_{timestamp}.json"

        # Save the result
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print_ritual(f"   ✓ Knowledge preserved in: {output_file}")

        # Print summary
        if isinstance(result, dict):
            print_ritual("\n📜 Research Summary:")
            if "briefing" in result:
                briefing = result["briefing"]
                if isinstance(briefing, dict):
                    if "title" in briefing:
                        print_ritual(f"   Title: {briefing['title']}")
                    if "key_findings" in briefing:
                        print_ritual(f"   Key Findings: {len(briefing['key_findings'])} found")
                    if "sources" in briefing:
                        print_ritual(f"   Sources Consulted: {len(briefing['sources'])}")

    except Exception as e:
        print_ritual(f"❌ Failed to preserve knowledge: {e}")
        return False

    # ==================== CLOSING ====================
    print_ritual("\n🙏 YAGYA COMPLETE.")
    print_ritual("   SHANTI SHANTI SHANTI")
    print_ritual("   (Peace, Peace, Peace)")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Execute the Research Yagya")
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Research topic to investigate"
    )
    parser.add_argument(
        "--depth",
        type=str,
        default="advanced",
        choices=["quick", "standard", "advanced"],
        help="Research depth level"
    )

    args = parser.parse_args()

    success = perform_yagya(topic=args.topic, depth=args.depth)
    sys.exit(0 if success else 1)
