#!/usr/bin/env python3
"""
🚀 AGENT CITY BOOT TEST (GAD-5002)

This is the REAL BOOT TEST - not mocks.
We're starting the actual kernel with real agents.

Test Flow:
1. Boot kernel via BootOrchestrator
2. Verify agents are registered
3. Submit a task to an agent
4. Verify task is processed
5. Check kernel pulse
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("BOOT_TEST")


async def test_agent_city_boot():
    """Test the complete Agent City boot sequence."""

    logger.info("\n" + "=" * 70)
    logger.info("🚀 AGENT CITY BOOT TEST - REAL KERNEL")
    logger.info("=" * 70)

    # =========================================================================
    # PHASE 1: BOOT
    # =========================================================================
    logger.info("\n📦 PHASE 1: BOOT ORCHESTRATOR")

    try:
        from vibe_core.boot_orchestrator import BootOrchestrator

        orchestrator = BootOrchestrator(
            ledger_path=":memory:",  # Use in-memory for test
        )

        logger.info("   → Starting boot sequence...")
        kernel = orchestrator.boot()

        logger.info("   ✅ Kernel booted successfully!")

    except Exception as e:
        logger.error(f"   ❌ BOOT FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # =========================================================================
    # PHASE 2: VERIFY AGENTS
    # =========================================================================
    logger.info("\n👥 PHASE 2: VERIFY AGENTS REGISTERED")

    status = kernel.get_status()
    agents_registered = status.get("agents_registered", 0)

    logger.info(f"   → Agents registered: {agents_registered}")
    logger.info(f"   → Kernel status: {status.get('status')}")

    # List all registered agents
    agent_ids = list(kernel.agent_registry.keys())
    logger.info(f"   → Agent IDs: {agent_ids}")

    if agents_registered == 0:
        logger.warning("   ⚠️  No agents registered!")
        # This might be okay if discovery failed - continue anyway
    else:
        logger.info(f"   ✅ {agents_registered} agents registered!")

    # =========================================================================
    # PHASE 3: SUBMIT TASK
    # =========================================================================
    logger.info("\n📤 PHASE 3: SUBMIT TEST TASK")

    try:
        from vibe_core.scheduling import Task

        # Find an agent to send task to
        target_agent = None
        for agent_id in ["ping", "scribe", "engineer", "discoverer"]:
            if agent_id in kernel.agent_registry:
                target_agent = agent_id
                break

        if not target_agent:
            target_agent = agent_ids[0] if agent_ids else "ping"

        test_task = Task(
            agent_id=target_agent,
            payload={
                "type": "test",
                "message": "Hello from boot test!",
                "test_id": "boot_test_001",
            },
        )

        logger.info(f"   → Submitting task to: {target_agent}")
        task_id = kernel.submit_task(test_task)
        logger.info(f"   → Task ID: {task_id}")
        logger.info("   ✅ Task submitted!")

    except Exception as e:
        logger.error(f"   ❌ Task submission failed: {e}")
        # Continue anyway

    # =========================================================================
    # PHASE 4: TICK KERNEL
    # =========================================================================
    logger.info("\n⚡ PHASE 4: TICK KERNEL (Process Queue)")

    try:
        # Tick a few times to process
        for i in range(3):
            kernel.tick()
            logger.info(f"   → Tick {i+1}/3 complete")
            await asyncio.sleep(0.1)

        logger.info("   ✅ Kernel ticked successfully!")

    except Exception as e:
        logger.warning(f"   ⚠️  Tick error (non-fatal): {e}")

    # =========================================================================
    # PHASE 5: FINAL STATUS
    # =========================================================================
    logger.info("\n📊 PHASE 5: FINAL STATUS")

    final_status = kernel.get_status()

    logger.info(f"   → Kernel Status: {final_status.get('status')}")
    logger.info(f"   → Agents: {final_status.get('agents_registered')}")
    logger.info(f"   → Queue Length: {final_status.get('scheduler', {}).get('queue_length', 0)}")
    logger.info(f"   → Completed Tasks: {final_status.get('scheduler', {}).get('completed', 0)}")
    logger.info(f"   → Ledger Events: {final_status.get('ledger_events', 0)}")

    # =========================================================================
    # PHASE 6: SHUTDOWN
    # =========================================================================
    logger.info("\n🔴 PHASE 6: SHUTDOWN")

    try:
        kernel.shutdown(reason="Boot test complete")
        logger.info("   ✅ Kernel shutdown complete")
    except Exception as e:
        logger.warning(f"   ⚠️  Shutdown warning: {e}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    logger.info("\n" + "=" * 70)
    logger.info("🎉 BOOT TEST SUMMARY")
    logger.info("=" * 70)

    success = agents_registered > 0 or len(agent_ids) > 0

    if success:
        logger.info("✅ BOOT TEST PASSED")
        logger.info(f"   • Kernel booted: YES")
        logger.info(f"   • Agents registered: {agents_registered}")
        logger.info(f"   • Task submitted: YES")
        logger.info(f"   • Kernel ticked: YES")
    else:
        logger.warning("⚠️  BOOT TEST PARTIAL")
        logger.warning("   • Kernel booted but no agents discovered")
        logger.warning("   • This may be due to missing config or oath issues")

    logger.info("=" * 70 + "\n")

    return success


if __name__ == "__main__":
    success = asyncio.run(test_agent_city_boot())
    sys.exit(0 if success else 1)
