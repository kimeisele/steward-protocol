#!/usr/bin/env python3
"""
Integration test with REAL kernel and REAL agents
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("REAL_KERNEL_TEST")

from vibe_core.boot_orchestrator import quick_boot
from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor


async def test_with_real_kernel():
    """Test playbook with real kernel and real agents"""

    logger.info("=" * 70)
    logger.info("INTEGRATION TEST: Playbook + Real Kernel + Real Agents")
    logger.info("=" * 70)

    # Boot the real kernel
    logger.info("\n[1/4] Booting kernel...")
    try:
        kernel = quick_boot()
        logger.info(f"✓ Kernel booted: {kernel.get_status().get('agents_registered', 0)} agents")
    except Exception as e:
        logger.error(f"❌ Kernel boot failed: {e}")
        return False

    # Initialize playbook engine
    logger.info("\n[2/4] Loading playbooks...")
    engine = DeterministicExecutor(knowledge_dir="knowledge")
    logger.info(f"✓ Loaded {len(engine.playbooks)} playbooks")

    # Find a simple playbook (content_generation uses envoy + herald)
    playbook = engine.playbooks.get("CONTENT_GENERATION_V1")
    if not playbook:
        logger.error("❌ CONTENT_GENERATION_V1 not found")
        return False

    logger.info(f"✓ Testing: {playbook.name}")

    # Execute with REAL kernel
    logger.info("\n[3/4] Executing playbook with REAL agents...")
    logger.info("-" * 70)

    try:
        result = await engine.execute(
            playbook_id="CONTENT_GENERATION_V1",
            user_input="Write a short article about AI safety",
            intent_vector=None,
            kernel=kernel,
            emit_event=None,
        )

        logger.info("-" * 70)
        logger.info("\n[4/4] ANALYZING RESULTS...")
        logger.info("=" * 70)

        # Check execution status
        logger.info(f"\nStatus: {result.get('status')}")
        logger.info(f"Phases executed: {len(result.get('phases_executed', []))}")

        # Examine each phase result
        logger.info("\n📊 PHASE RESULTS:")
        for i, phase in enumerate(result.get("phases_executed", []), 1):
            logger.info(f"\n  Phase {i}: {phase.get('name')}")
            logger.info(f"    Status: {phase.get('status')}")

            phase_result = phase.get("result", {})
            if isinstance(phase_result, dict):
                if "result" in phase_result:
                    agent_result = phase_result["result"]
                    logger.info(f"    Agent: {phase_result.get('agent', 'unknown')}")
                    logger.info(f"    Agent returned: {type(agent_result).__name__}")

                    if isinstance(agent_result, dict):
                        logger.info(f"    Keys: {list(agent_result.keys())}")
                        logger.info(f"    Preview: {str(agent_result)[:200]}...")
                    else:
                        logger.info(f"    Value: {agent_result}")

        # Final verdict
        logger.info("\n" + "=" * 70)
        if result.get("status") == "COMPLETED":
            logger.info("✅ INTEGRATION TEST PASSED")
            logger.info("   Playbook executed with real agents!")
            return True
        else:
            logger.error("❌ INTEGRATION TEST FAILED")
            logger.error(f"   Status: {result.get('status')}")
            return False

    except Exception as e:
        logger.error(f"\n❌ EXCEPTION: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_with_real_kernel())
    sys.exit(0 if success else 1)
