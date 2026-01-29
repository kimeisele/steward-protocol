#!/usr/bin/env python3
"""
VERIFY ENVOY WIRING
===================
Tests the integration of MilkOceanRouter and DeterministicExecutor into EnvoyCartridge.

Scenario:
1. Instantiate EnvoyCartridge.
2. Mock MilkOceanRouter to return "EXECUTE_CIRCUIT".
3. Mock DeterministicExecutor to return success.
4. Send "Debate: AI is conscious" task.
5. Verify routing and execution flow.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x5740eee6"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import sys
from unittest.mock import AsyncMock, MagicMock

# Adjust path to find modules
sys.path.append(".")

from vibe_core import Task
from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_WIRING")


async def test_envoy_wiring():
    logger.info("🧪 Starting Envoy Wiring Verification...")

    # 1. Instantiate Envoy
    envoy = EnvoyCartridge()

    # Inject Mock Kernel
    mock_kernel = MagicMock()
    mock_kernel.get_sandbox_path.return_value = MagicMock()  # Path object
    envoy.system = MagicMock()
    envoy.system.get_sandbox_path.return_value.parent.mkdir.return_value = None
    envoy.kernel = mock_kernel

    # 2. Mock Components (to test WIRING, not the components themselves)
    # Mock Router
    envoy.router = AsyncMock()
    envoy.router.route.return_value = {
        "route": "EXECUTE_CIRCUIT",
        "target": "DEBATE_V1",
        "confidence": 0.95,
        "intent": {"concepts": ["philosophy", "consciousness"]},
    }

    # Mock Executor
    envoy.executor = AsyncMock()
    envoy.executor.execute.return_value = {
        "status": "COMPLETED",
        "output": "Debate concluded: AI is conscious.",
        "execution_mode": "circuit",
    }

    # 3. Create Task
    task = Task(task_id="test_task_001", agent_id="envoy", payload={"input": "Debate: AI is conscious"})

    # 4. Process Task
    logger.info("📨 Sending Task: 'Debate: AI is conscious'")
    result = await envoy.process(task)

    # 5. Assertions
    logger.info("🔍 Verifying Results...")

    # Check Router was called
    envoy.router.route.assert_called_once_with("Debate: AI is conscious")
    logger.info("✅ Router called correctly")

    # Check Executor was called
    envoy.executor.execute.assert_called_once()
    call_args = envoy.executor.execute.call_args[1]
    assert call_args["playbook_id"] == "DEBATE_V1"
    assert call_args["user_input"] == "Debate: AI is conscious"
    assert call_args["kernel"] == mock_kernel
    logger.info("✅ Executor called correctly with Kernel injection")

    # Check Result
    assert result["status"] == "COMPLETED"
    assert result["output"] == "Debate concluded: AI is conscious."
    logger.info("✅ Result returned correctly")

    logger.info("🎉 ENVOY WIRING VERIFIED SUCCESSFUL!")


if __name__ == "__main__":
    asyncio.run(test_envoy_wiring())
