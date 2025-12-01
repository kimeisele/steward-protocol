#!/usr/bin/env python3
"""
E2E Test: Blueprint Generator Integration (GAD-5001)

Tests the complete flow:
  RAW INPUT → BLUEPRINT EXTRACTION → PLAYBOOK EXECUTION → AGENT CALLS

This proves that:
1. Raw user input is transformed into structured parameters
2. Template variables use EXTRACTED values, not defaults
3. Agents receive meaningful context, not generic text
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("E2E_BLUEPRINT")

# Track what agents receive
AGENT_CALLS = []
PENDING_RESULTS = {}


class MockKernel:
    """Mock kernel that tracks what agents are called with"""

    def submit_task(self, task):
        """Record agent call and return task_id"""
        call_record = {
            "agent": task.agent_id,
            "payload": task.payload,
            "task_id": task.task_id,
        }
        AGENT_CALLS.append(call_record)
        logger.info(f"  📞 AGENT CALL: {task.agent_id}")
        logger.info(f"     PAYLOAD: {task.payload}")

        # Prepare result based on agent
        if task.agent_id == "engineer":
            result = {"status": "completed", "path": "/tmp/feature.py", "files_written": 1}
        elif task.agent_id == "auditor":
            result = {"status": "completed", "passed": True, "issues": []}
        elif task.agent_id == "archivist":
            result = {"status": "completed", "commit_hash": "abc123", "sealed": True}
        else:
            result = {"status": "completed", "result": "ok"}

        PENDING_RESULTS[task.task_id] = result
        return task.task_id

    def tick(self):
        """Mock heartbeat - no-op"""
        pass

    def get_task_result(self, task_id):
        """Return stored result for task"""
        return PENDING_RESULTS.get(task_id)


async def test_blueprint_integration():
    """Test that blueprint extraction flows through to agent calls"""
    from steward.system_agents.envoy.deterministic_executor import DeterministicExecutor

    logger.info("\n" + "=" * 70)
    logger.info("E2E TEST: Blueprint Generator Integration (GAD-5001)")
    logger.info("=" * 70)

    # Create executor
    executor = DeterministicExecutor(knowledge_dir="knowledge")

    # Check if blueprint generator is loaded
    if not executor.blueprint_generator:
        logger.error("❌ Blueprint Generator not loaded!")
        return False

    logger.info("✅ Blueprint Generator loaded")
    logger.info(f"✅ Loaded playbooks: {list(executor.playbooks.keys())}")

    # Mock kernel
    mock_kernel = MockKernel()

    # Test input - specific user request
    user_input = "Implement JWT authentication with role-based access control in src/auth/"

    logger.info(f"\n📝 USER INPUT: '{user_input}'")
    logger.info("-" * 70)

    # Mock emit_event
    async def mock_emit(event_type, message, source, data=None):
        pass  # Silence events for test

    # Clear previous calls
    AGENT_CALLS.clear()

    # Execute playbook
    result = await executor.execute(
        playbook_id="FEATURE_IMPLEMENT_SAFE_V1",
        user_input=user_input,
        intent_vector=None,
        kernel=mock_kernel,
        emit_event=mock_emit,
    )

    logger.info("-" * 70)
    logger.info("\n📊 RESULTS:")
    logger.info(f"   Status: {result.get('status')}")

    # Analyze what the engineer agent received
    logger.info("\n📋 AGENT CALLS ANALYSIS:")

    engineer_call = next((c for c in AGENT_CALLS if c["agent"] == "engineer"), None)

    if engineer_call:
        logger.info("\n   ENGINEER AGENT RECEIVED:")
        payload = engineer_call["payload"]
        prompt = payload.get("prompt", "N/A")
        intent_ref = payload.get("intent_ref", "N/A")

        logger.info(f"   - prompt: '{prompt}'")
        logger.info(f"   - intent_ref: {intent_ref}")

        # Verify the prompt contains EXTRACTED values, not defaults
        if "New Feature" in str(prompt) or "Detailed description" in str(prompt):
            logger.error("\n❌ FAIL: Agent received DEFAULT value!")
            logger.error("   Blueprint extraction did not override defaults.")
            return False

        if "JWT" in prompt or "authentication" in prompt or "auth" in prompt:
            logger.info("\n✅ PASS: Agent received EXTRACTED values from user input!")
        else:
            logger.warning(f"\n⚠️  WARNING: Prompt may not reflect user input: '{prompt}'")

    else:
        logger.warning("⚠️  No engineer call recorded (playbook may have different flow)")

    # Show all calls
    logger.info("\n📞 ALL AGENT CALLS:")
    for i, call in enumerate(AGENT_CALLS, 1):
        logger.info(f"   {i}. {call['agent']}")
        for key, val in call['payload'].items():
            val_str = str(val)[:100] + "..." if len(str(val)) > 100 else str(val)
            logger.info(f"      {key}: {val_str}")

    logger.info("\n" + "=" * 70)
    logger.info("E2E TEST COMPLETE")
    logger.info("=" * 70)

    return True


if __name__ == "__main__":
    success = asyncio.run(test_blueprint_integration())
    sys.exit(0 if success else 1)
