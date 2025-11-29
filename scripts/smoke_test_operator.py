#!/usr/bin/env python3
"""
SMOKE TEST: Universal Operator Adapter

This script proves the socket is wired and working.
It boots the system via Sarga and sends an intent through the operator.

WHAT WE'RE TESTING:
1. Sarga boot completes (6 phases)
2. SystemContext is built from kernel state
3. Intent flows through the operator
4. Kernel responds

RUN:
    python scripts/smoke_test_operator.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.operator_adapter import UniversalOperatorAdapter
from vibe_core.protocols.operator_protocol import (
    Intent,
    IntentType,
    OperatorType,
    SystemContext,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("SMOKE_TEST")


class MockOperator:
    """
    Mock operator that sends predefined intents.
    Used for testing without human input.
    """

    def __init__(self, intents: list[Intent]):
        self.intents = intents
        self.index = 0
        self._context_received = None

    async def receive_context(self, context: SystemContext) -> None:
        """Store received context for verification."""
        self._context_received = context
        logger.info(f"📥 Context received: kernel={context.kernel_status.value}, agents={context.agents_registered}")

    async def provide_intent(self) -> Intent:
        """Return next predefined intent."""
        if self.index >= len(self.intents):
            # No more intents - shutdown
            return Intent(
                intent_type=IntentType.CONTROL,
                raw_input="exit",
                source_operator=OperatorType.DEGRADED,
            )
        intent = self.intents[self.index]
        self.index += 1
        logger.info(f"📤 Intent provided: {intent.intent_type.value} - {intent.raw_input}")
        return intent

    def is_available(self) -> bool:
        return True

    def get_operator_type(self) -> OperatorType:
        return OperatorType.DEGRADED  # Mock = degraded type


async def smoke_test():
    """Run the smoke test."""
    print("\n" + "=" * 70)
    print("🔥 SMOKE TEST: Universal Operator Adapter")
    print("=" * 70 + "\n")

    # =========================================================================
    # STEP 1: Boot via Sarga
    # =========================================================================
    print("[1/4] Booting system via Sarga...")

    orchestrator = BootOrchestrator()
    kernel = orchestrator.boot()

    print(f"      ✅ Kernel booted: {kernel}")
    print(f"      ✅ Sarga complete: {orchestrator.kernel is not None}")

    # =========================================================================
    # STEP 2: Create Operator Adapter with Mock
    # =========================================================================
    print("\n[2/4] Creating operator adapter with mock operator...")

    # Create test intents
    test_intents = [
        Intent(
            intent_type=IntentType.QUERY,
            raw_input="status",
            source_operator=OperatorType.HUMAN,
        ),
        Intent(
            intent_type=IntentType.QUERY,
            raw_input="?agents",
            source_operator=OperatorType.HUMAN,
        ),
        Intent(
            intent_type=IntentType.CONTROL,
            raw_input="exit",
            source_operator=OperatorType.HUMAN,
        ),
    ]

    mock = MockOperator(test_intents)
    adapter = UniversalOperatorAdapter()
    adapter.register_operator(mock, priority=0)  # Highest priority

    print(f"      ✅ Mock operator registered (priority 0)")
    print(f"      ✅ Test intents: {len(test_intents)}")

    # =========================================================================
    # STEP 3: Build SystemContext
    # =========================================================================
    print("\n[3/4] Building SystemContext from kernel...")

    context = orchestrator._build_system_context()

    print(f"      ✅ boot_id: {context.boot_id}")
    print(f"      ✅ kernel_status: {context.kernel_status.value}")
    print(f"      ✅ agents_registered: {context.agents_registered}")
    print(f"      ✅ sarga_complete: {context.sarga_complete}")
    print(f"      ✅ available_agents: {context.available_agents[:5]}...")

    # =========================================================================
    # STEP 4: Send Intent Through Socket
    # =========================================================================
    print("\n[4/4] Sending intents through socket...")

    results = []
    for i, test_intent in enumerate(test_intents):
        print(f"\n      --- Intent {i+1}/{len(test_intents)} ---")

        # Get decision (this sends context and gets intent)
        intent = await adapter.get_decision(context)
        print(f"      → Received intent: {intent.intent_type.value} - '{intent.raw_input}'")

        # Execute intent
        result = await orchestrator._execute_intent(intent)
        print(f"      → Result: {result}")
        results.append(result)

        if intent.raw_input.lower() == "exit":
            break

    # =========================================================================
    # RESULTS
    # =========================================================================
    print("\n" + "=" * 70)
    print("🎯 SMOKE TEST RESULTS")
    print("=" * 70)

    checks = [
        ("Sarga boot completed", orchestrator.kernel is not None),
        ("SystemContext built", context.boot_id is not None),
        ("Context sent to operator", mock._context_received is not None),
        ("Intent received from operator", len(results) > 0),
        ("Kernel responded", any(r for r in results)),
    ]

    all_passed = True
    for name, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}")
        if not passed:
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("🟢 ALL CHECKS PASSED - THE SOCKET IS LIVE")
    else:
        print("🔴 SOME CHECKS FAILED")
    print("=" * 70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(smoke_test())
    sys.exit(0 if success else 1)
