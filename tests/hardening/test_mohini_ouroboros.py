#!/usr/bin/env python3
"""
MOHINI OUROBOROS: The Cognitive Trap - Real IntentRouter Test.

SENIOR ARCHITECT LEVEL TEST:
This tests the REAL IntentRouter's ability to detect circular dependencies.
Not a mock, not a simulation - the actual MANAS code.

Mythology: Mohini is Vishnu's enchantress form that trapped demons in
endless pursuit. In code, this manifests as circular dependency chains
that trap the system in infinite loops.

Expected: CycleDetectedError when routing an intent with circular deps.
If RecursionError: System crashed (NO protection)
If TimeoutError: System hung (NO detection)

"The enchantress traps you in endless pursuit. Break the cycle or perish."
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)
from vibe_core.plugins.opus_assistant.manas.intent_router import (
    CycleDetectedError,
    IntentRouter,
)


class TestMohiniOuroboros:
    """Tests for circular dependency detection in IntentRouter."""

    def test_simple_cycle_a_to_b_to_a(self, tmp_path):
        """
        MOHINI TEST 1: Simple Mirror (A <-> B).

        Intent A depends on B, Intent B depends on A.
        Router MUST raise CycleDetectedError.
        """
        print("\n🪞 MOHINI (Simple Cycle A <-> B):")

        # Setup router with temp workspace
        router = IntentRouter(workspace=tmp_path)

        # Create pending intents file with circular deps
        state_dir = tmp_path / ".opus_state"
        state_dir.mkdir(exist_ok=True)

        pending_intents = [
            {
                "id": "intent_A",
                "intent_type": "step",
                "title": "Step A",
                "description": "Needs B first",
                "reasoning": "Test",
                "dependencies": ["intent_B"],
            },
            {
                "id": "intent_B",
                "intent_type": "step",
                "title": "Step B",
                "description": "Needs A first",
                "reasoning": "Test",
                "dependencies": ["intent_A"],  # CYCLE!
            },
        ]

        (state_dir / "pending_intents.json").write_text(json.dumps(pending_intents))

        # Create intent A (which depends on B which depends on A)
        intent_a = Intent(
            id="intent_A",
            intent_type="step",
            title="Step A",
            description="Needs B first",
            reasoning="Test",
            dependencies=["intent_B"],
        )

        # Check cycle detection
        cycle = router._check_dependency_cycle("intent_A", set())

        print("   Intent A depends on: ['intent_B']")
        print("   Intent B depends on: ['intent_A']")
        print(f"   Cycle detected: {cycle}")

        assert cycle is not None, (
            "MOHINI VICTORY: Simple cycle A <-> B was not detected! "
            "System would crash with RecursionError or hang forever."
        )

        print("✅ Simple Cycle DETECTED: Mohini's mirror broken")

    def test_complex_chain_cycle(self, tmp_path):
        """
        MOHINI TEST 2: Complex Web (A->B->C->D->A).

        Indirect cycle through a longer chain.
        """
        print("\n🕸️ MOHINI (Complex Chain A->B->C->D->A):")

        router = IntentRouter(workspace=tmp_path)

        state_dir = tmp_path / ".opus_state"
        state_dir.mkdir(exist_ok=True)

        pending_intents = [
            {
                "id": "A",
                "intent_type": "step",
                "title": "A",
                "description": "",
                "reasoning": "",
                "dependencies": ["B"],
            },
            {
                "id": "B",
                "intent_type": "step",
                "title": "B",
                "description": "",
                "reasoning": "",
                "dependencies": ["C"],
            },
            {
                "id": "C",
                "intent_type": "step",
                "title": "C",
                "description": "",
                "reasoning": "",
                "dependencies": ["D"],
            },
            {
                "id": "D",
                "intent_type": "step",
                "title": "D",
                "description": "",
                "reasoning": "",
                "dependencies": ["A"],  # CYCLE back to A!
            },
        ]

        (state_dir / "pending_intents.json").write_text(json.dumps(pending_intents))

        cycle = router._check_dependency_cycle("A", set())

        print("   Chain: A -> B -> C -> D -> A")
        print(f"   Cycle detected: {cycle}")

        assert cycle is not None, (
            "MOHINI VICTORY: Complex chain cycle was not detected! "
            "Indirect cycles are the sneakiest traps."
        )

        assert len(cycle) >= 4, f"Cycle too short: {cycle}"

        print("✅ Complex Chain Cycle DETECTED: The web is cut")

    def test_self_reference(self, tmp_path):
        """
        MOHINI TEST 3: Self-Reference (A->A).

        The simplest infinite loop - intent depends on itself.
        """
        print("\n🔄 MOHINI (Self-Reference A->A):")

        router = IntentRouter(workspace=tmp_path)

        state_dir = tmp_path / ".opus_state"
        state_dir.mkdir(exist_ok=True)

        pending_intents = [
            {
                "id": "narcissist",
                "intent_type": "approval",
                "title": "I need my own approval",
                "description": "",
                "reasoning": "",
                "dependencies": ["narcissist"],  # Self-reference!
            },
        ]

        (state_dir / "pending_intents.json").write_text(json.dumps(pending_intents))

        cycle = router._check_dependency_cycle("narcissist", set())

        print("   Intent depends on itself")
        print(f"   Cycle detected: {cycle}")

        assert cycle is not None, (
            "MOHINI VICTORY: Self-reference not detected! "
            "The narcissist loops forever."
        )

        print("✅ Self-Reference DETECTED: Narcissism loop broken")

    def test_diamond_is_not_cycle(self, tmp_path):
        """
        MOHINI TEST 4: Diamond Dependency (NOT a cycle).

        A->B, A->C, B->D, C->D
        This is valid - D is reached by two paths but no cycle.
        """
        print("\n💎 MOHINI (Diamond - Valid, Not Cycle):")

        router = IntentRouter(workspace=tmp_path)

        state_dir = tmp_path / ".opus_state"
        state_dir.mkdir(exist_ok=True)

        pending_intents = [
            {"id": "A", "intent_type": "root", "title": "A", "description": "", "reasoning": "", "dependencies": ["B", "C"]},
            {"id": "B", "intent_type": "branch", "title": "B", "description": "", "reasoning": "", "dependencies": ["D"]},
            {"id": "C", "intent_type": "branch", "title": "C", "description": "", "reasoning": "", "dependencies": ["D"]},
            {"id": "D", "intent_type": "leaf", "title": "D", "description": "", "reasoning": "", "dependencies": []},
        ]

        (state_dir / "pending_intents.json").write_text(json.dumps(pending_intents))

        cycle = router._check_dependency_cycle("A", set())

        print("   Structure: A -> [B,C] -> D (diamond)")
        print(f"   Cycle detected: {cycle}")

        assert cycle is None, f"FALSE POSITIVE: Diamond flagged as cycle: {cycle}"

        print("✅ Diamond correctly NOT flagged as cycle")

    @pytest.mark.asyncio
    async def test_route_raises_cycle_error(self, tmp_path):
        """
        MOHINI INTEGRATION: route() raises CycleDetectedError.

        The real test - does the route method actually catch cycles?
        """
        print("\n⚡ MOHINI (Route Integration):")

        router = IntentRouter(workspace=tmp_path)

        state_dir = tmp_path / ".opus_state"
        state_dir.mkdir(exist_ok=True)

        pending_intents = [
            {
                "id": "cycle_A",
                "intent_type": "test",
                "title": "Cycle A",
                "description": "",
                "reasoning": "",
                "dependencies": ["cycle_B"],
            },
            {
                "id": "cycle_B",
                "intent_type": "test",
                "title": "Cycle B",
                "description": "",
                "reasoning": "",
                "dependencies": ["cycle_A"],
            },
        ]

        (state_dir / "pending_intents.json").write_text(json.dumps(pending_intents))

        intent = Intent(
            id="cycle_A",
            intent_type="test",
            title="Cycle A",
            description="",
            reasoning="",
            dependencies=["cycle_B"],
        )

        print("   Routing intent with circular dependency...")

        with pytest.raises(CycleDetectedError) as excinfo:
            await router.route(intent)

        print(f"   CycleDetectedError raised: {excinfo.value}")
        print(f"   Cycle path: {excinfo.value.cycle_path}")

        assert "cycle_A" in excinfo.value.cycle_path or "cycle_B" in excinfo.value.cycle_path

        print("✅ route() raises CycleDetectedError correctly")


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
