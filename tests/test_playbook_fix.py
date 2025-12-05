#!/usr/bin/env python3
"""
Quick test to verify CALL_AGENT fix in deterministic_executor.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PLAYBOOK_FIX_TEST")

from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor
from vibe_core.scheduling.task import Task


class MockKernel:
    """Mock kernel that actually returns results"""

    def __init__(self):
        self.calls = []

    async def submit_task(self, task: Task):
        """Mock submit_task that returns a result dict like real kernel"""
        self.calls.append({"agent_id": task.agent_id, "payload": task.payload})

        logger.info(f"MockKernel: Received task for {task.agent_id} with payload: {task.payload}")

        # Simulate agent response
        return {
            "status": "success",
            "agent": task.agent_id,
            "mock_result": f"Result from {task.agent_id}",
            "payload_echo": task.payload,
        }


async def test_playbook_execution():
    """Test that CALL_AGENT actually calls agents"""

    logger.info("=" * 60)
    logger.info("TESTING PLAYBOOK CALL_AGENT FIX")
    logger.info("=" * 60)

    # Initialize executor
    engine = DeterministicExecutor(knowledge_dir="knowledge")
    logger.info(f"✓ Loaded {len(engine.playbooks)} playbooks")

    # Create mock kernel
    kernel = MockKernel()

    # Find a playbook to test (content_generation has CALL_AGENT)
    playbook = engine.playbooks.get("CONTENT_GENERATION_V1")

    if not playbook:
        logger.error("❌ CONTENT_GENERATION_V1 playbook not found!")
        return False

    logger.info(f"\n✓ Testing playbook: {playbook.name}")
    logger.info(f"  Phases: {len(playbook.phases)}")

    # Execute playbook
    try:
        result = await engine.execute(
            playbook_id="CONTENT_GENERATION_V1",
            user_input="Test content generation",
            intent_vector=None,
            kernel=kernel,
            emit_event=None,
        )

        logger.info("\n" + "=" * 60)
        logger.info("EXECUTION RESULT:")
        logger.info("=" * 60)
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Phases executed: {len(result.get('phases_executed', []))}")

        # Check if agents were actually called
        logger.info(f"\n🔍 MockKernel calls: {len(kernel.calls)}")
        for i, call in enumerate(kernel.calls):
            logger.info(f"  Call {i + 1}: {call['agent_id']} <- {call['payload']}")

        # Verify
        if len(kernel.calls) > 0:
            logger.info("\n✅ SUCCESS: Agents were actually called!")
            logger.info(f"   {len(kernel.calls)} agent call(s) made")
            return True
        else:
            logger.error("\n❌ FAILURE: No agents were called!")
            logger.error("   CALL_AGENT is still stubbed or failed")
            return False

    except Exception as e:
        logger.error(f"\n❌ EXCEPTION: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_playbook_execution())
    sys.exit(0 if success else 1)
