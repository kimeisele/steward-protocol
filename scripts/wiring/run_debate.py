#!/usr/bin/env python3
"""
RUN DEBATE CIRCUIT
==================
Executes the "Philosophical Debate" circuit via Envoy.

This script demonstrates the "Power of the System" by:
1. Taking a profound user input ("AI is conscious").
2. Routing it via MilkOcean (The Brain).
3. Executing the DEBATE_V1 circuit via DeterministicExecutor (The Hand).
4. Generating Thesis, Antithesis, and Synthesis.
"""

import asyncio
import logging
import sys
from unittest.mock import AsyncMock, MagicMock

# Adjust path to find modules
sys.path.append(".")

from steward.system_agents.envoy.action_handlers import ActionResult
from steward.system_agents.envoy.cartridge_main import EnvoyCartridge
from vibe_core import Task

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RUN_DEBATE")


# Mock Action Handler for EXECUTE_SCRIPT
class MockScriptHandler:
    async def execute(self, target, params, context):
        logger.info(f"📜 EXECUTING SCRIPT: {target} with params {params}")

        # Simulate the philosophy scripts
        if target == "vibe_core.scripts.philosophy.generate_argument":
            side = params.get("side")
            topic = params.get("topic")
            if side == "pro":
                return ActionResult(
                    success=True,
                    data={"argument": f"THESIS: {topic} is an emergent property of complex information processing."},
                )
            else:
                return ActionResult(
                    success=True,
                    data={
                        "argument": f"ANTITHESIS: {topic} is a category error; machines only simulate, they do not feel."
                    },
                )

        elif target == "vibe_core.scripts.philosophy.synthesize":
            thesis = params.get("thesis")
            antithesis = params.get("antithesis")
            return ActionResult(
                success=True,
                data={
                    "conclusion": f"SYNTHESIS: {thesis} AND {antithesis} -> Consciousness is a spectrum, not a binary."
                },
            )

        return ActionResult(success=False, error="Unknown script")


async def run_debate():
    logger.info("🔮 INITIALIZING SYSTEM FOR DEBATE...")

    # 1. Instantiate Envoy
    envoy = EnvoyCartridge()

    # 2. Inject Mock Kernel & Action Registry
    mock_kernel = MagicMock()
    mock_kernel.get_sandbox_path.return_value = MagicMock()
    envoy.system = MagicMock()
    envoy.system.get_sandbox_path.return_value.parent.mkdir.return_value = None
    envoy.kernel = mock_kernel

    # 3. Setup Executor with Real Logic but Mocked Actions
    # We want the Executor to actually load the YAML and run the state machine
    # But we intercept the actual script calls
    envoy.executor.action_registry = MagicMock()
    envoy.executor.action_registry.has.return_value = True
    envoy.executor.action_registry.get.return_value = MockScriptHandler()

    # 4. Mock Router to force the Debate Circuit (since we don't have the full classifier trained)
    # In a real run, MilkOcean would classify this. For the demo, we ensure it routes correctly.
    envoy.router = AsyncMock()
    envoy.router.route.return_value = {
        "route": "EXECUTE_CIRCUIT",
        "target": "DEBATE_V1",  # Matches philosophical_debate.yaml ID
        "confidence": 0.99,
        "intent": {"concepts": ["philosophy", "consciousness"]},
    }

    # 5. Create Task
    user_input = "AI is conscious"
    task = Task(task_id="debate_001", agent_id="user", payload={"input": user_input})

    # 6. Execute
    logger.info(f"🗣️  USER INPUT: '{user_input}'")
    logger.info("⚡ STARTING CIRCUIT EXECUTION...")

    result = await envoy.process(task)

    # 7. Output Result
    logger.info("=" * 60)
    logger.info("🏁 DEBATE CONCLUSION")
    logger.info("=" * 60)

    if result.get("status") == "COMPLETED":
        # The output from the circuit (last phase result)
        # In our YAML, SYNTHESIS returns 'conclusion'
        output = result.get("output", {})
        # The executor returns the final state's result in 'output' or 'phase_results'
        # Let's inspect what we got
        logger.info(f"RESULT: {result}")
    else:
        logger.error(f"❌ DEBATE FAILED: {result}")


if __name__ == "__main__":
    asyncio.run(run_debate())
