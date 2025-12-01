"""
COGNITIVE CIRCUIT EXECUTOR
==========================
GAD-5500: Neuro-Symbolic OS Implementation

This module executes Cognitive Circuits - semantic state machines that
orchestrate kernel syscalls.

Unlike traditional playbook executors that run "steps", this executor
manages STATE TRANSITIONS based on INVARIANTS and SYSCALL RESULTS.

Architecture:
    User Intent → Semantic Compiler → Circuit Executor → Kernel Syscalls

The key insight: Circuits are declarative state machines, not imperative scripts.
Each state has invariants that must hold, and transitions are triggered by
syscall completion.

This is the runtime for "ML Light" - deterministic execution of neural output.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import yaml

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

from vibe_core.semantic_syscalls import (
    SyscallType,
    SyscallRequest,
    SyscallResult,
    SemanticSyscallExecutor,
)
from steward.system_agents.envoy.blueprint_generator import (
    BlueprintGenerator,
    CompilationResult,
)

logger = logging.getLogger("CIRCUIT_EXECUTOR")


@dataclass
class CircuitState:
    """Current state of circuit execution."""
    current_state: str
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    syscall_results: Dict[str, SyscallResult] = field(default_factory=dict)
    is_terminal: bool = False
    output: Optional[Dict[str, Any]] = None


@dataclass
class CircuitExecutionResult:
    """Result of executing a cognitive circuit."""
    success: bool
    final_state: str
    output: Dict[str, Any]
    state_history: List[str]
    syscall_count: int
    error: Optional[str] = None


class CognitiveCircuitExecutor:
    """
    Executes Cognitive Circuits (Neuro-Symbolic Playbooks).

    The executor:
    1. Loads circuit definition from YAML
    2. Manages state transitions based on invariants
    3. Orchestrates syscall execution via SemanticSyscallExecutor
    4. Tracks execution history for audit trail
    """

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self.syscall_executor = SemanticSyscallExecutor(kernel)
        self.compiler = BlueprintGenerator(kernel)
        self.circuits: Dict[str, Dict] = {}

        # Load available circuits
        self._load_circuits()

        logger.info("🔌 Cognitive Circuit Executor initialized")

    def _load_circuits(self) -> None:
        """Load all circuit definitions from YAML files."""
        circuits_dir = Path(__file__).parent / "playbook" / "circuits"

        if not circuits_dir.exists():
            logger.warning(f"Circuits directory not found: {circuits_dir}")
            return

        for yaml_file in circuits_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    circuit_def = yaml.safe_load(f)

                if "circuit" in circuit_def:
                    circuit_id = circuit_def["circuit"]["id"]
                    self.circuits[circuit_id] = circuit_def["circuit"]
                    logger.info(f"📍 Loaded circuit: {circuit_id}")

            except Exception as e:
                logger.error(f"Failed to load circuit {yaml_file}: {e}")

    def execute(
        self,
        raw_input: str,
        requester_id: str = "user",
    ) -> CircuitExecutionResult:
        """
        Execute the appropriate circuit for the given input.

        This is the main entry point. It:
        1. Compiles the input using BlueprintGenerator
        2. Determines which circuit to execute
        3. Runs the circuit state machine
        4. Returns the result

        Args:
            raw_input: The raw user input
            requester_id: Who is making this request

        Returns:
            CircuitExecutionResult with final state and output
        """
        logger.info(f"🎯 CIRCUIT EXECUTOR: Processing '{raw_input[:60]}...'")

        # Step 1: Compile input to determine intent
        compilation = self.compiler.compile(raw_input, requester_id)

        if not compilation.is_syscall:
            # Not a syscall - fall back to traditional playbook
            logger.info("📋 Input is not a syscall intent - use traditional playbook")
            return CircuitExecutionResult(
                success=False,
                final_state="NOT_SYSCALL",
                output={"fallback": "traditional_playbook", "vars": compilation.playbook_vars},
                state_history=[],
                syscall_count=0,
                error="Input did not compile to a syscall - use traditional playbook execution",
            )

        # Step 2: Determine which circuit to execute based on syscall type
        syscall_type = compilation.syscall_request.syscall_type

        circuit_map = {
            SyscallType.SPAWN_COGNITION: "AGENT_BIRTH_V1",
            # Future circuits:
            # SyscallType.DISPATCH_TASK: "TASK_DISPATCH_V1",
            # SyscallType.ALLOCATE_PRANA: "RESOURCE_ALLOCATION_V1",
        }

        circuit_id = circuit_map.get(syscall_type)
        if not circuit_id or circuit_id not in self.circuits:
            # Direct syscall execution (no circuit needed)
            logger.info(f"⚡ Direct syscall execution: {syscall_type.value}")
            result = self.syscall_executor.execute(compilation.syscall_request)

            return CircuitExecutionResult(
                success=result.success,
                final_state="DIRECT_EXECUTION",
                output=result.output,
                state_history=["DIRECT_EXECUTION"],
                syscall_count=1,
                error=result.error,
            )

        # Step 3: Execute the circuit
        circuit_def = self.circuits[circuit_id]
        return self._execute_circuit(
            circuit_def,
            raw_input=raw_input,
            compilation=compilation,
            requester_id=requester_id,
        )

    def _execute_circuit(
        self,
        circuit_def: Dict,
        raw_input: str,
        compilation: CompilationResult,
        requester_id: str,
    ) -> CircuitExecutionResult:
        """
        Execute a specific circuit definition.

        This is the state machine driver. It:
        1. Starts at entry_state
        2. Executes operations in current state
        3. Evaluates transitions
        4. Moves to next state
        5. Repeats until terminal state
        """
        circuit_id = circuit_def["id"]
        logger.info(f"🔄 Executing circuit: {circuit_id}")

        # Initialize state
        # IMPORTANT: Store both the full compilation result AND the syscall request
        # The circuit conditions reference "compiled_request.is_syscall" which is on CompilationResult
        state = CircuitState(
            current_state=circuit_def.get("entry_state", "SHABDA"),
            variables={
                "raw_input": raw_input,
                "requester_id": requester_id,
                # Store full compilation for is_syscall check
                "compiled_request": {
                    "is_syscall": compilation.is_syscall,
                    "syscall_type": compilation.syscall_request.syscall_type.value if compilation.syscall_request else None,
                    "params": compilation.syscall_request.params if compilation.syscall_request else {},
                    "confidence": compilation.confidence,
                },
                # Also store the actual request for later use
                "_syscall_request": compilation.syscall_request,
            },
        )

        states = circuit_def.get("states", {})
        max_transitions = 20  # Safety limit
        syscall_count = 0

        while not state.is_terminal and len(state.history) < max_transitions:
            current_state_name = state.current_state
            state.history.append(current_state_name)

            logger.info(f"📍 State: {current_state_name}")

            current_state_def = states.get(current_state_name)
            if not current_state_def:
                return CircuitExecutionResult(
                    success=False,
                    final_state=current_state_name,
                    output={"error": f"Unknown state: {current_state_name}"},
                    state_history=state.history,
                    syscall_count=syscall_count,
                    error=f"Circuit has undefined state: {current_state_name}",
                )

            # Check if terminal
            if current_state_def.get("terminal", False):
                state.is_terminal = True
                state.output = self._resolve_output(
                    current_state_def.get("output", {}),
                    state.variables,
                )
                break

            # Execute operations
            for operation in current_state_def.get("operations", []):
                action = operation.get("action")

                if action == "COMPILE_REQUEST":
                    # Already compiled - keep the dict structure intact
                    # Don't overwrite compiled_request with syscall_request!
                    logger.info("✅ COMPILE_REQUEST: Using pre-compiled syscall")
                    # compiled_request is already set in variables with is_syscall=True

                elif action == "CHECK_CONSTITUTION":
                    # Constitutional check (simplified)
                    role = compilation.syscall_request.params.get("role", "")
                    forbidden = circuit_def.get("forbidden_roles", [])

                    if role.lower() in [r.lower() for r in forbidden]:
                        state.variables["constitutional_check"] = {
                            "passed": False,
                            "violation": f"Role '{role}' is forbidden",
                        }
                    else:
                        state.variables["constitutional_check"] = {"passed": True}

                    logger.info(f"🛡️ Constitutional check: {state.variables['constitutional_check']}")

                elif action == "PREPARE_RESOURCES":
                    # Resource preparation (simplified)
                    state.variables["resources_prepared"] = True
                    logger.info("💰 Resources prepared")

                elif action == "EXECUTE_SYSCALL":
                    # The actual syscall execution
                    syscall_type_str = operation.get("syscall_type")
                    syscall_type = SyscallType[syscall_type_str]

                    # For SPAWN_COGNITION, use the pre-compiled request
                    if syscall_type == SyscallType.SPAWN_COGNITION and "_syscall_request" in state.variables:
                        request = state.variables["_syscall_request"]
                    else:
                        # Resolve params from variables
                        params = self._resolve_params(
                            operation.get("params", {}),
                            state.variables,
                        )

                        request = SyscallRequest(
                            syscall_type=syscall_type,
                            params=params,
                            requester_id=requester_id,
                        )

                    result = self.syscall_executor.execute(request)
                    syscall_count += 1

                    # Store result
                    result_key = f"{syscall_type_str.lower()}_result"
                    state.syscall_results[result_key] = result
                    state.variables[result_key] = result

                    # Special handling for SPAWN_COGNITION
                    if syscall_type == SyscallType.SPAWN_COGNITION:
                        state.variables["spawn_result"] = {
                            "success": result.success,
                            "agent_id": result.output.get("agent_id"),
                            "karma_block_id": result.karma_block_id,
                            "error": result.error,
                        }

                    logger.info(f"⚡ SYSCALL {syscall_type_str}: success={result.success}")

            # Evaluate transitions
            next_state = self._evaluate_transitions(
                current_state_def.get("transitions", []),
                state.variables,
            )

            if next_state:
                state.current_state = next_state
            else:
                # No valid transition - stuck
                return CircuitExecutionResult(
                    success=False,
                    final_state=current_state_name,
                    output={"error": "No valid transition from current state"},
                    state_history=state.history,
                    syscall_count=syscall_count,
                    error=f"Circuit stuck at state: {current_state_name}",
                )

        # Build final result
        final_state = state.current_state
        success = final_state == "SUCCESS"

        return CircuitExecutionResult(
            success=success,
            final_state=final_state,
            output=state.output or {},
            state_history=state.history,
            syscall_count=syscall_count,
            error=None if success else state.output.get("reason"),
        )

    def _evaluate_transitions(
        self,
        transitions: List[Dict],
        variables: Dict[str, Any],
    ) -> Optional[str]:
        """Evaluate transition conditions and return next state."""
        logger.info(f"🔀 Evaluating {len(transitions)} transitions")

        # Log variables for debugging
        if "compiled_request" in variables:
            cr = variables["compiled_request"]
            if isinstance(cr, dict):
                logger.info(f"   compiled_request.is_syscall = {cr.get('is_syscall')} (type: {type(cr.get('is_syscall'))})")
            else:
                logger.info(f"   compiled_request is {type(cr).__name__}, not dict!")

        for transition in transitions:
            condition = transition.get("condition", "")
            target = transition.get("to")

            logger.info(f"   Checking: '{condition}' → {target}")
            result = self._evaluate_condition(condition, variables)
            logger.info(f"   → Eval result: {result}")

            if result:
                logger.info(f"✅ Transition matched: {condition} → {target}")
                return target

        logger.warning("❌ No transition matched!")
        return None

    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string against variables.

        Simple implementation - supports:
        - "compiled_request.is_syscall == true"
        - "constitutional_check.passed == true"
        - "spawn_result.success == true"
        """
        try:
            # Parse condition
            parts = condition.split(" == ")
            if len(parts) != 2:
                logger.debug(f"Condition parse failed (no ==): {condition}")
                return False

            path = parts[0].strip()
            expected = parts[1].strip().lower()

            # Resolve path
            value = self._resolve_path(path, variables)
            logger.debug(f"Condition check: {path} = {value} (expected: {expected})")

            # Compare
            if expected in ("true", "false"):
                result = bool(value) == (expected == "true")
                logger.debug(f"Boolean comparison: bool({value}) == {expected == 'true'} → {result}")
                return result
            else:
                result = str(value).lower() == expected
                logger.debug(f"String comparison: '{str(value).lower()}' == '{expected}' → {result}")
                return result

        except Exception as e:
            logger.warning(f"Condition evaluation failed: {condition} - {e}")
            return False

    def _resolve_path(self, path: str, variables: Dict[str, Any]) -> Any:
        """Resolve a dotted path against variables dict."""
        parts = path.split(".")
        value = variables

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            elif hasattr(value, "__getitem__"):
                try:
                    value = value[part]
                except (KeyError, TypeError):
                    return None
            else:
                return None

        return value

    def _resolve_params(self, params: Dict, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve template expressions in params dict."""
        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and "{{" in value:
                # Template expression - resolve from variables
                path = value.replace("{{", "").replace("}}", "").strip()
                resolved[key] = self._resolve_path(path, variables)
            else:
                resolved[key] = value

        return resolved

    def _resolve_output(self, output_template: Dict, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve output template with variable values."""
        return self._resolve_params(output_template, variables)


# ============================================================================
# FACTORY
# ============================================================================

def create_circuit_executor(kernel: "RealVibeKernel") -> CognitiveCircuitExecutor:
    """Factory function to create a Cognitive Circuit Executor."""
    return CognitiveCircuitExecutor(kernel)


__all__ = [
    "CognitiveCircuitExecutor",
    "CircuitState",
    "CircuitExecutionResult",
    "create_circuit_executor",
]
