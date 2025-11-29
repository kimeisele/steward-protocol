#!/usr/bin/env python3
"""
THE SUMMONING SCRIPT.
Command-line interface for The Engineer.

Usage:
    python scripts/summon.py --name "agent_name" --mission "Agent mission"
"""

import argparse
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from steward.system_agents.engineer.cartridge_main import EngineerCartridge

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SUMMONER")


def main():
    parser = argparse.ArgumentParser(description="Summon a new Agent via The Engineer.")
    parser.add_argument("--name", required=True, help="Name of the agent (snake_case)")
    parser.add_argument(
        "--mission", required=True, help="Mission description for the agent"
    )

    args = parser.parse_args()

    logger.info("🔮 SUMMONING RITUAL INITIATED...")
    logger.info(f"   Target: {args.name}")
    logger.info(f"   Mission: {args.mission}")

    try:
        engineer = EngineerCartridge()
        result = engineer.create_agent(args.name, args.mission)

        if "Error" in result:
            logger.error(f"❌ Ritual failed: {result}")
            sys.exit(1)

        logger.info("✨ RITUAL COMPLETE.")
        logger.info(f"   Agent manifest: {result}")
        logger.info(
            f"   To activate: python {args.name}/cartridge_main.py (or load via VibeOS)"
        )

    except Exception as e:
        logger.error(f"❌ Critical failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
