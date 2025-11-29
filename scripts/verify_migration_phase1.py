#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - PHASE 1: EMERGENCY TRIAGE
===============================================

Goal: Verify that all agents boot successfully without import-time crashes.
Focus: CivicCartridge and its dependencies (Economy, Bank, Vault, Cryptography).

This script attempts to instantiate the agents that were previously reported to crash.
"""

import logging
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("VERIFICATION")


def test_agent_boot(agent_name, module_path, class_name):
    logger.info(f"🧪 Testing boot: {agent_name}...")
    try:
        # Dynamic import
        module = __import__(module_path, fromlist=[class_name])
        AgentClass = getattr(module, class_name)

        # Instantiate
        agent = AgentClass()

        logger.info(f"   ✅ {agent_name} booted successfully!")
        return True
    except Exception as e:
        logger.error(f"   ❌ {agent_name} CRASHED: {e}")
        logger.error(traceback.format_exc())
        return False


def main():
    logger.info("🚀 STARTING MIGRATION PHASE 1 VERIFICATION")
    logger.info("==========================================")

    agents_to_test = [
        (
            "CivicCartridge",
            "steward.system_agents.civic.cartridge_main",
            "CivicCartridge",
        ),
        (
            "AuditorCartridge",
            "steward.system_agents.auditor.cartridge_main",
            "AuditorCartridge",
        ),
        (
            "ScienceCartridge",
            "steward.system_agents.science.cartridge_main",
            "ScientistCartridge",
        ),
        (
            "ArchivistCartridge",
            "steward.system_agents.archivist.cartridge_main",
            "ArchivistCartridge",
        ),
    ]

    failures = []

    for name, mod, cls in agents_to_test:
        if not test_agent_boot(name, mod, cls):
            failures.append(name)

    logger.info("==========================================")
    if failures:
        logger.error(
            f"❌ VERIFICATION FAILED. {len(failures)} agents crashed: {', '.join(failures)}"
        )
        sys.exit(1)
    else:
        logger.info("✅ VERIFICATION PASSED. All critical agents booted successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
