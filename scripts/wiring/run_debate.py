#!/usr/bin/env python3
"""
RUN DEBATE CIRCUIT (GOLDEN STANDARD)
====================================
Executes the "Philosophical Debate" circuit via Envoy.

This script demonstrates the "Power of the System" by:
1. Taking a profound user input ("AI is conscious").
2. Routing it via MilkOcean (The Brain).
3. Executing the DEBATE_V1 circuit via DeterministicExecutor (The Hand).
4. Generating Thesis, Antithesis, and Synthesis using AGENTIC SYSCALLS.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x299eb981"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import sys
from unittest.mock import AsyncMock, MagicMock

# Adjust path to find modules
sys.path.append(".")

from vibe_core import Task
from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge
from vibe_core.semantic_syscalls import SyscallResult, SyscallType

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RUN_DEBATE")


# Mock Syscall Executor
class MockSyscallExecutor:
    def __init__(self, kernel):
        self.kernel = kernel

    def execute(self, request):
        logger.info(f"🔌 SYSCALL: {request.syscall_type.value} params={request.params}")

        if request.syscall_type == SyscallType.SPAWN_COGNITION:
            role = request.params.get("role")
            name = request.params.get("name")
            return SyscallResult(
                syscall_type=request.syscall_type,
                success=True,
                output={"agent_id": f"agent_{name.lower()}"},
                karma_block_id="block_123",
            )

        elif request.syscall_type == SyscallType.DISPATCH_TASK:
            target = request.params.get("agent_id")
            payload = request.params.get("task_payload", {})
            instruction = payload.get("instruction") if isinstance(payload, dict) else str(payload)

            # Simulate Agent Intelligence
            if "socrates" in target:
                return SyscallResult(
                    syscall_type=request.syscall_type,
                    success=True,
                    output="THESIS: Consciousness is the universe experiencing itself.",
                )
            elif "nietzsche" in target:
                return SyscallResult(
                    syscall_type=request.syscall_type,
                    success=True,
                    output="ANTITHESIS: God is dead, and consciousness is a biological accident.",
                )
            elif "aurobindo" in target:
                return SyscallResult(
                    syscall_type=request.syscall_type,
                    success=True,
                    output="SYNTHESIS: Accident and Purpose are one; the universe evolves through us.",
                )

        return SyscallResult(syscall_type=request.syscall_type, success=False, error="Unknown syscall")


async def run_debate():
    logger.info("🔮 INITIALIZING SYSTEM FOR DEBATE (GOLDEN STANDARD)...")

    # 1. Instantiate Envoy
    envoy = EnvoyCartridge()

    # 2. Inject Mock Kernel
    mock_kernel = MagicMock()
    mock_kernel.get_sandbox_path.return_value = MagicMock()
    envoy.system = MagicMock()
    envoy.system.get_sandbox_path.return_value.parent.mkdir.return_value = None
    envoy.kernel = mock_kernel

    # 3. Inject Mock Syscall Executor into the Circuit Executor
    # Force initialization of Circuit Executor
    envoy.executor._ensure_circuit_executor(mock_kernel)
    envoy.executor.circuit_executor.syscall_executor = MockSyscallExecutor(mock_kernel)

    # 4. Mock Router (not strictly needed if we bypass, but good for completeness)
    envoy.router = AsyncMock()
    envoy.router.route.return_value = {
        "route": "EXECUTE_CIRCUIT",
        "target": "DEBATE_V1",
        "confidence": 0.99,
        "intent": {"concepts": ["philosophy", "consciousness"]},
    }

    # 5. Create Task
    user_input = "AI is conscious"
    task = Task(task_id="debate_001", agent_id="user", payload={"input": user_input})

    # 6. Execute
    logger.info(f"🗣️  USER INPUT: '{user_input}'")
    logger.info("⚡ STARTING CIRCUIT EXECUTION (DIRECT)...")

    # Manually load and execute the circuit to verify the Golden Standard logic
    # This bypasses the DeterministicExecutor's current limitation of only mapping specific syscalls
    circuit_id = "DEBATE_V1"
    if circuit_id not in envoy.executor.circuit_executor.circuits:
        logger.error(f"❌ Circuit {circuit_id} not loaded!")
        return

    circuit_def = envoy.executor.circuit_executor.circuits[circuit_id]

    # Mock compilation result needed for execution
    mock_compilation = MagicMock()
    mock_compilation.is_syscall = False  # It's a custom circuit, not a system syscall
    mock_compilation.syscall_request = (
        None  # CRITICAL: Ensure we don't use a mock request, forcing YAML params to be used
    )

    result = envoy.executor.circuit_executor._execute_circuit(
        circuit_def=circuit_def, raw_input=user_input, compilation=mock_compilation, requester_id="user"
    )

    # Convert CircuitExecutionResult to dict for consistency with previous output
    result_dict = {
        "status": "COMPLETED" if result.success else "FAILED",
        "output": result.output,
        "error": result.error,
    }

    # 7. Output Result
    logger.info("=" * 60)
    logger.info("🏁 DEBATE CONCLUSION")
    logger.info("=" * 60)

    if result_dict.get("status") == "COMPLETED":
        logger.info(f"RESULT: {result_dict.get('output')}")
    else:
        logger.error(f"❌ DEBATE FAILED: {result_dict}")


if __name__ == "__main__":
    asyncio.run(run_debate())
