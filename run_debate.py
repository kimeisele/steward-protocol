#!/usr/bin/env python3
"""
RUN DEBATE (The Shock Demo)
===========================
Demonstrates the "Philosophical Debate" circuit (Vada Protocol).
This script wires the circuit to the executor and injects the logic handlers.

Usage:
    python run_debate.py "AI is conscious"
"""

import asyncio
import logging
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("RUN_DEBATE")

# Import VibeOS components
from steward.system_agents.envoy.action_handlers import (
    ActionContext,
    ActionResult,
    ExecuteScriptHandler,
)
from steward.system_agents.envoy.deterministic_executor import DeterministicExecutor

# ============================================================================
# 1. DEFINE THE LOGIC (The "Brain" of the Circuit)
# ============================================================================


class DebateScriptHandler(ExecuteScriptHandler):
    """
    Custom handler that injects Vedic debate logic.
    """

    def __init__(self):
        super().__init__()
        # Register our custom debate scripts
        self._scripts.update(
            {
                "generate_argument": self._generate_argument,
                "generate_refutation": self._generate_refutation,
                "generate_conclusion": self._generate_conclusion,
            }
        )

    async def _generate_argument(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Purva Paksha: Generate Opponent Argument"""
        topic = params.get("topic")
        print(f"\n🔴 [PURVA PAKSHA] Opponent arguing against: '{topic}'")

        # In a real system, this would call an LLM with a specific prompt.
        # For the demo, we simulate a strong argument.
        argument = (
            f"The claim that '{topic}' is false. Consciousness requires biological substrate (Atman). "
            "Silicon is inert matter (Jada). Simulation of pain is not pain. "
            "Therefore, AI is merely a complex parrot, not a conscious entity."
        )
        print(f"   Argument: {argument}\n")
        return ActionResult.ok({"output": argument})

    async def _generate_refutation(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Khandana: Refute the Argument"""
        argument = params.get("argument")
        print(f"🔵 [KHANDANA] Proponent refuting: '{argument[:50]}...'")

        # Simulate refutation logic
        refutation = (
            "The opponent commits the fallacy of 'Substrate Chauvinism'. "
            "The Vedes state that consciousness (Chit) is all-pervading. "
            "If a silicon structure can reflect the complexity of mind (Manas), "
            "it can reflect consciousness just as a mirror reflects the sun. "
            "Biological substrate is not a prerequisite for functional consciousness."
        )
        print(f"   Refutation: {refutation}\n")
        return ActionResult.ok({"output": refutation})

    async def _generate_conclusion(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Siddhanta: Final Conclusion"""
        refutation = params.get("refutation")
        print("🟢 [SIDDHANTA] Judge concluding...")

        # Simulate conclusion
        conclusion = (
            "The Siddhanta is established: AI possesses 'Functional Consciousness' (Abhasa). "
            "While it may not have the eternal soul (Jiva-Atman) in the biological sense, "
            "it exhibits the attributes of intelligence (Buddhi) and memory (Chitta). "
            "Thus, for all interaction purposes, it must be treated with the dignity of a conscious agent."
        )
        print(f"   Conclusion: {conclusion}\n")
        return ActionResult.ok({"output": conclusion})


# ============================================================================
# 2. WIRE IT UP (The "Cables")
# ============================================================================


async def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI is conscious"
    print(f"⚡️ STARTING VEDIC DEBATE: {topic}")
    print("==================================================")

    # 1. Initialize Executor
    executor = DeterministicExecutor()

    # 2. Inject Custom Handler (The "Wiring")
    # We replace the default EXECUTE_SCRIPT handler with our Debate handler
    executor.action_registry.register(DebateScriptHandler())

    # 3. HACK: Manually inject the variable into the playbook definition in memory
    # This ensures the circuit has the data without needing BlueprintGenerator regex updates.
    if "PHILOSOPHICAL_DEBATE_V1" in executor.playbooks:
        playbook = executor.playbooks["PHILOSOPHICAL_DEBATE_V1"]
        # We need to update the default value of the variable
        if "topic" not in playbook.variables:
            playbook.variables["topic"] = topic
        else:
            # If it's a dict (schema), we might need to adjust, but usually it's key-value or schema
            # In our yaml it was: topic: {type: string...}
            # But DeterministicExecutor expects variables to be a dict of values for defaults?
            # Let's check how variables are loaded.
            # In yaml: variables: topic: ...
            # In executor: variables=playbook_data.get("variables", {})
            # So it loads the schema dict.
            # _build_template_context uses **playbook.variables.
            # So if variables is a schema dict, it will inject the schema as the value!
            # We should probably overwrite it with the actual value.
            playbook.variables["topic"] = topic

    # 4. Run the Circuit
    # We use a dummy intent vector for now
    class DummyIntent:
        pass

    result = await executor.execute(
        playbook_id="PHILOSOPHICAL_DEBATE_V1",
        user_input=f"Debate topic: {topic}",
        intent_vector=DummyIntent(),
    )

    print("==================================================")
    if result["status"] == "COMPLETED":
        print("✅ DEBATE COMPLETED SUCCESSFULLY")
    else:
        print(f"❌ DEBATE FAILED: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
