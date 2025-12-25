"""
OPUS-307 PHASE I.1: THE EXECUTOR SINGULARITY
============================================

This module implements the "Death of DeterministicExecutor" strategy.

THE PROBLEM (discovered in Phase I Research):
- CLI flow uses CognitiveCircuitExecutor (states, actions, transitions)
- Runtime flow uses DeterministicExecutor (phases, actions, on_success/on_failure)
- Same circuit executed via different paths → different executors → semantic mismatch!

THE SOLUTION:
- ALL execution routes to CognitiveCircuitExecutor
- Playbooks are converted to circuits on-the-fly
- DeterministicExecutor becomes a thin wrapper that delegates to this adapter

CONVERSION:
    Playbook (legacy)          →   Circuit (unified)
    ------------------             ------------------
    phases: [                      states:
      {phase_id: "p1", ...}          p1: {...}
      {phase_id: "p2", ...}          p2: {...}
    ]                              entry_state: "p1"

"Ein Executor, eine Engine, eine Wahrheit."
"""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.cortex.engines.circuit_engine import CognitiveCircuitExecutor
    from vibe_core.protocols.ledger import VibeKernel

logger = logging.getLogger("EXECUTOR_SINGULARITY")


@dataclass
class PlaybookToCircuitConverter:
    """
    Converts legacy playbook format to unified circuit format.

    This enables CognitiveCircuitExecutor to execute ALL workloads,
    whether they came from circuits/*.yaml or playbooks/*.yaml.
    """

    @staticmethod
    def convert(playbook_def: Dict[str, Any], playbook_id: str) -> Dict[str, Any]:
        """
        Convert a PlaybookDefinition dict to Circuit format.

        Args:
            playbook_def: Legacy playbook definition dict
            playbook_id: The playbook ID

        Returns:
            Circuit definition dict compatible with CognitiveCircuitExecutor
        """
        # Extract playbook data (handle both raw dict and nested 'playbook' key)
        if "playbook" in playbook_def:
            pb = playbook_def["playbook"]
        elif "circuit" in playbook_def:
            # Already a circuit - return as-is
            return playbook_def
        else:
            pb = playbook_def

        # Get phases
        phases = pb.get("phases", [])
        if not phases:
            logger.warning(f"Playbook {playbook_id} has no phases")
            return playbook_def

        # Convert phases list to states dict
        states = {}
        entry_state = None

        for i, phase in enumerate(phases):
            phase_id = phase.get("phase_id", f"phase_{i}")

            # First phase becomes entry_state
            if entry_state is None:
                entry_state = phase_id

            # Convert phase to state
            state = {
                "name": phase.get("name", phase_id),
                "description": phase.get("description", ""),
                "actions": phase.get("actions", []),
            }

            # Handle on_success / on_failure
            on_success = phase.get("on_success", "COMPLETE")
            on_failure = phase.get("on_failure", "ABORT")

            # For CognitiveCircuitExecutor, we use both formats
            # (it checks actions, on_success/on_failure, and transitions)
            state["on_success"] = on_success
            state["on_failure"] = on_failure

            # Copy additional fields
            if phase.get("state_var"):
                state["state_var"] = phase["state_var"]
            if phase.get("requires_approval"):
                state["requires_approval"] = phase["requires_approval"]
            if phase.get("timeout_seconds"):
                state["timeout_seconds"] = phase["timeout_seconds"]

            states[phase_id] = state

        # Add terminal states if not present
        if "COMPLETE" not in states:
            states["COMPLETE"] = {
                "name": "Complete",
                "description": "Playbook completed successfully",
                "terminal": True,
                "output": {"status": "COMPLETED"},
            }

        if "ABORT" not in states:
            states["ABORT"] = {
                "name": "Abort",
                "description": "Playbook aborted due to failure",
                "terminal": True,
                "output": {"status": "FAILED"},
            }

        # Build circuit definition
        circuit_def = {
            "circuit": {
                "id": pb.get("id", playbook_id),
                "type": "cognitive_circuit",  # Mark as converted playbook
                "description": pb.get("description", ""),
                "entry_state": entry_state,
                "states": states,
                "variables": pb.get("variables", {}),
                "converted_from": "playbook",  # Provenance marker
            }
        }

        # Copy templates if present
        if "templates" in pb or "templates" in playbook_def:
            circuit_def["templates"] = pb.get("templates", playbook_def.get("templates", {}))

        logger.info(f"🔄 Converted playbook → circuit: {playbook_id} ({len(states)} states)")
        return circuit_def


@dataclass
class ExecutorSingularity:
    """
    THE UNIFIED EXECUTOR - One engine to run them all.

    This replaces the split brain of DeterministicExecutor:
    - No more is_syscall checks
    - No more separate playbook execution path
    - EVERYTHING goes through CognitiveCircuitExecutor

    Usage:
        singularity = ExecutorSingularity(kernel)
        result = await singularity.execute(
            playbook_or_circuit_id="SYSTEM_STATUS_V2",
            user_input="status",
            intent_vector=None,
        )
    """

    kernel: "VibeKernel"
    circuit_executor: Optional["CognitiveCircuitExecutor"] = None
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self):
        """Lazy initialize circuit executor."""
        pass

    def _ensure_executor(self) -> bool:
        """Ensure circuit executor is ready."""
        if self.circuit_executor is not None:
            return True

        try:
            from vibe_core.cortex.engines.circuit_engine import create_circuit_executor

            self.circuit_executor = create_circuit_executor(kernel=self.kernel)
            self._initialized = True
            logger.info("🎯 ExecutorSingularity: CognitiveCircuitExecutor ready")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize ExecutorSingularity: {e}")
            return False

    async def execute(
        self,
        playbook_or_circuit_id: str,
        user_input: str,
        intent_vector: Any = None,
        emit_event: Any = None,
        playbook_def: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute ANY workload through CognitiveCircuitExecutor.

        If playbook_def is provided and is legacy format, converts it first.

        Args:
            playbook_or_circuit_id: ID of the circuit/playbook to execute
            user_input: Original user input
            intent_vector: Optional intent vector for context
            emit_event: Optional event emitter
            playbook_def: Optional pre-loaded playbook definition (for conversion)

        Returns:
            Execution result dict
        """
        if not self._ensure_executor():
            return {
                "status": "FAILED",
                "error": "ExecutorSingularity not initialized",
                "execution_mode": "singularity",
            }

        # If playbook_def provided, check if conversion needed
        circuit_def = None
        if playbook_def:
            if "playbook" in playbook_def and "circuit" not in playbook_def:
                # Legacy playbook - convert to circuit
                circuit_def = PlaybookToCircuitConverter.convert(playbook_def, playbook_or_circuit_id)

        try:
            # Execute via CognitiveCircuitExecutor
            # Signature: execute_by_id(circuit_id, input_vars, requester_id)
            result = self.circuit_executor.execute_by_id(
                circuit_id=playbook_or_circuit_id,
                input_vars={"user_input": user_input, "raw_input": user_input},
                requester_id="singularity",
            )

            # Convert CircuitExecutionResult to dict
            return {
                "status": "COMPLETED" if result.success else "FAILED",
                "execution_mode": "singularity",
                "circuit_id": playbook_or_circuit_id,
                "final_state": result.final_state,
                "output": result.output,
                "state_history": result.state_history,
                "error": result.error,
                "details": {
                    "rendered": result.output,
                },
            }

        except Exception as e:
            logger.error(f"❌ ExecutorSingularity failed: {e}", exc_info=True)
            return {
                "status": "FAILED",
                "execution_mode": "singularity",
                "circuit_id": playbook_or_circuit_id,
                "error": str(e),
            }

    def list_available(self) -> List[str]:
        """List all available circuits/playbooks."""
        if not self._ensure_executor():
            return []

        return list(self.circuit_executor._circuits.keys())


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_executor_singularity(kernel: "VibeKernel") -> ExecutorSingularity:
    """
    Create the ExecutorSingularity.

    This is the single entry point for ALL execution in the system.

    Args:
        kernel: The VibeKernel instance

    Returns:
        ExecutorSingularity ready for use
    """
    return ExecutorSingularity(kernel=kernel)
