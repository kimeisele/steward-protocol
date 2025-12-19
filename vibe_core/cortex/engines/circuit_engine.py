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

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

# Lazy import for Runtime Separation (OPUS-016)
try:
    from vibe_core.cartridges.system.envoy.blueprint_generator import (
        BlueprintGenerator,
        CompilationResult,
    )

    BLUEPRINT_AVAILABLE = True
except ImportError:
    BLUEPRINT_AVAILABLE = False
    BlueprintGenerator = None
    CompilationResult = None

# OPUS-118: Import canonical types from shared module
from vibe_core.circuit_types import (
    CircuitExecutionResult,
    CircuitState,
    ErrorRecoveryAttempt,
    InvariantViolation,
    TaskLedgerEntry,
)
from vibe_core.semantic_syscalls import (
    SemanticSyscallExecutor,
    SyscallRequest,
    SyscallResult,
    SyscallType,
)

logger = logging.getLogger("CIRCUIT_EXECUTOR")


def _get_runtime_config():
    """Get runtime config with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config

        return get_config().runtime
    except Exception:
        from vibe_core.phoenix.sections.runtime.section_main import RuntimeConfig

        return RuntimeConfig()


# ============================================================================
# INVARIANT CHECKER - Runtime enforcement of circuit constraints
# ============================================================================


# OPUS-118: InvariantViolation moved to vibe_core/circuit_types.py


class InvariantChecker:
    """
    Runtime invariant checker for cognitive circuits.

    Parses and evaluates invariant expressions against circuit state.
    This is the SECURITY ENFORCEMENT layer - not just documentation.

    Supported invariant patterns:
    - "variable is not empty"
    - "variable == value"
    - "variable != value"
    - "variable >= number"
    - "variable <= number"
    - "variable > number"
    - "variable < number"
    - "variable.path == value"
    - "variable is not in LIST"
    - "variable is in LIST"
    """

    def __init__(self):
        self.violations: List[InvariantViolation] = []

    def check_invariants(
        self,
        invariants: List[str],
        variables: Dict[str, Any],
        state_name: str,
    ) -> bool:
        """
        Check all invariants against current variables.

        Args:
            invariants: List of invariant strings from circuit YAML
            variables: Current state variables
            state_name: Name of current state (for error reporting)

        Returns:
            True if all invariants pass, False if any fail
        """
        if not invariants:
            return True

        all_passed = True

        for invariant in invariants:
            passed, reason = self._evaluate_invariant(invariant, variables)

            if not passed:
                violation = InvariantViolation(
                    invariant=invariant,
                    state=state_name,
                    variables=variables.copy(),
                    reason=reason,
                )
                self.violations.append(violation)
                logger.error(f"🚨 INVARIANT VIOLATION in {state_name}: {invariant}")
                logger.error(f"   Reason: {reason}")
                all_passed = False
            else:
                logger.debug(f"✓ Invariant passed: {invariant}")

        return all_passed

    def _evaluate_invariant(self, invariant: str, variables: Dict[str, Any]) -> tuple[bool, str]:
        """
        Evaluate a single invariant expression.

        Returns:
            (passed: bool, reason: str)
        """
        invariant = invariant.strip()

        try:
            # Pattern: "X is not empty"
            match = re.match(r"(.+)\s+is\s+not\s+empty", invariant, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                value = self._resolve_path(path, variables)
                if value is None or value == "" or value == [] or value == {}:
                    return False, f"{path} is empty (value: {value})"
                return True, ""

            # Pattern: "X is empty"
            match = re.match(r"(.+)\s+is\s+empty", invariant, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                value = self._resolve_path(path, variables)
                if value is None or value == "" or value == [] or value == {}:
                    return True, ""
                return False, f"{path} is not empty (value: {value})"

            # Pattern: "X is not in LIST"
            match = re.match(r"(.+)\s+is\s+not\s+in\s+(\w+)", invariant, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                list_name = match.group(2).strip()
                value = self._resolve_path(path, variables)
                forbidden_list = self._resolve_path(list_name, variables) or []
                if value in forbidden_list:
                    return False, f"{path}={value} is in forbidden list {list_name}"
                return True, ""

            # Pattern: "X is in LIST"
            match = re.match(r"(.+)\s+is\s+in\s+(\w+)", invariant, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                list_name = match.group(2).strip()
                value = self._resolve_path(path, variables)
                allowed_list = self._resolve_path(list_name, variables) or []
                if value not in allowed_list:
                    return False, f"{path}={value} is not in allowed list {list_name}"
                return True, ""

            # Pattern: "X == Y" or "X != Y"
            match = re.match(r"(.+)\s*(==|!=)\s*(.+)", invariant)
            if match:
                left_path = match.group(1).strip()
                operator = match.group(2)
                right_raw = match.group(3).strip()

                left_value = self._resolve_path(left_path, variables)
                right_value = self._parse_value(right_raw, variables)

                if operator == "==":
                    if str(left_value).lower() != str(right_value).lower():
                        return False, f"{left_path}={left_value} != {right_value}"
                    return True, ""
                else:  # !=
                    if str(left_value).lower() == str(right_value).lower():
                        return False, f"{left_path}={left_value} == {right_value}"
                    return True, ""

            # Pattern: "X >= Y" or "X <= Y" or "X > Y" or "X < Y"
            match = re.match(r"(.+)\s*(>=|<=|>|<)\s*(.+)", invariant)
            if match:
                left_path = match.group(1).strip()
                operator = match.group(2)
                right_raw = match.group(3).strip()

                left_value = self._resolve_path(left_path, variables)
                right_value = self._parse_value(right_raw, variables)

                try:
                    left_num = float(left_value) if left_value is not None else 0
                    right_num = float(right_value)
                except (ValueError, TypeError):
                    return False, f"Cannot compare non-numeric values: {left_value} {operator} {right_value}"

                if operator == ">=":
                    if not (left_num >= right_num):
                        return False, f"{left_path}={left_num} < {right_num}"
                elif operator == "<=":
                    if not (left_num <= right_num):
                        return False, f"{left_path}={left_num} > {right_num}"
                elif operator == ">":
                    if not (left_num > right_num):
                        return False, f"{left_path}={left_num} <= {right_num}"
                elif operator == "<":
                    if not (left_num < right_num):
                        return False, f"{left_path}={left_num} >= {right_num}"
                return True, ""

            # Pattern: "X has Y" (object has property)
            match = re.match(r"(.+)\s+has\s+(.+)", invariant, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                property_name = match.group(2).strip()
                value = self._resolve_path(path, variables)
                if value is None:
                    return False, f"{path} is None"
                if isinstance(value, dict):
                    if property_name not in value:
                        return False, f"{path} does not have property '{property_name}'"
                    return True, ""
                return False, f"{path} is not a dict, cannot check for '{property_name}'"

            # Unknown pattern - FAIL-CLOSED for security
            # If we can't parse an invariant, we can't verify it's satisfied.
            # This prevents typos like "role is nota empty" from silently passing.
            logger.warning(f"Unknown invariant pattern (FAILING): {invariant}")
            return False, f"Unknown invariant pattern - cannot verify: '{invariant}'"

        except Exception as e:
            return False, f"Error evaluating invariant: {e}"

    def _resolve_path(self, path: str, variables: Dict[str, Any]) -> Any:
        """Resolve a dotted path against variables dict."""
        parts = path.split(".")
        value = variables

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

        return value

    def _parse_value(self, raw: str, variables: Dict[str, Any]) -> Any:
        """Parse a value from invariant expression."""
        # Check if it's a variable reference
        if "." in raw or raw in variables:
            resolved = self._resolve_path(raw, variables)
            if resolved is not None:
                return resolved

        # String literal
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            return raw[1:-1]

        # Boolean
        if raw.lower() == "true":
            return True
        if raw.lower() == "false":
            return False

        # Number
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            pass

        # Return as string
        return raw

    def get_violations(self) -> List[InvariantViolation]:
        """Get all recorded violations."""
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear recorded violations."""
        self.violations.clear()


# OPUS-118: CircuitState and CircuitExecutionResult moved to vibe_core/circuit_types.py


class CognitiveCircuitExecutor:
    """
    Executes Cognitive Circuits (Neuro-Symbolic Playbooks).

    The executor:
    1. Loads circuit definition from YAML
    2. Manages state transitions based on invariants
    3. Orchestrates syscall execution via SemanticSyscallExecutor
    4. Tracks execution history for audit trail
    5. Emits events for meta-circuit integration (TASK_LEDGER, ERROR_RECOVERY)
    """

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self.syscall_executor = SemanticSyscallExecutor(kernel)
        self.compiler = BlueprintGenerator(kernel)
        self.circuits: Dict[str, Dict] = {}

        # Invariant checker - SECURITY ENFORCEMENT
        self.invariant_checker = InvariantChecker()

        # Meta-circuit callbacks for TASK_LEDGER and ERROR_RECOVERY integration
        self._on_circuit_start: Optional[callable] = None
        self._on_state_transition: Optional[callable] = None
        self._on_circuit_end: Optional[callable] = None
        self._on_error: Optional[callable] = None

        # Load available circuits
        self._load_circuits()

        logger.info("🔌 Cognitive Circuit Executor initialized (with invariant enforcement)")

    def set_meta_callbacks(
        self,
        on_start: Optional[callable] = None,
        on_transition: Optional[callable] = None,
        on_end: Optional[callable] = None,
        on_error: Optional[callable] = None,
    ) -> None:
        """
        Set callbacks for meta-circuit integration.

        These callbacks enable TASK_LEDGER and ERROR_RECOVERY to observe
        circuit execution.

        Args:
            on_start: Called when circuit execution begins
                      Signature: (circuit_id, raw_input, requester_id) -> None
            on_transition: Called on each state transition
                          Signature: (circuit_id, from_state, to_state, variables) -> None
            on_end: Called when circuit execution ends
                   Signature: (circuit_id, success, final_state, output) -> None
            on_error: Called when an error occurs
                     Signature: (circuit_id, state, error) -> Optional[recovery_action]
        """
        self._on_circuit_start = on_start
        self._on_state_transition = on_transition
        self._on_circuit_end = on_end
        self._on_error = on_error
        logger.info("🔗 Meta-circuit callbacks registered")

    def _load_circuits(self) -> None:
        """Load all circuit definitions from YAML files (Recursive)."""
        # Circuits are in vibe_core/playbook/circuits, not relative to this file
        circuits_dir = Path(__file__).parent.parent.parent / "playbook" / "circuits"

        if not circuits_dir.exists():
            logger.warning(f"Circuits directory not found: {circuits_dir}")
            return

        # GAD-5500: Recursive loading for Fractal Circuit Library
        for yaml_file in circuits_dir.glob("**/*.yaml"):
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

        # Map syscall types to circuits
        # Note: DISPATCH_TASK uses direct execution (routes to target agent)
        # Specialized circuits (content, governance, etc.) are for explicit workflows
        circuit_map = {
            SyscallType.SPAWN_COGNITION: "AGENT_BIRTH_V1",
            # DISPATCH_TASK: direct execution - routes to agent
            # ALLOCATE_PRANA: direct execution - kernel handles
            # DESTROY_COGNITION: direct execution - kernel handles
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
        recursion_depth: int = 0,
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
        logger.info(f"🔄 Executing circuit: {circuit_id} (Depth: {recursion_depth})")

        # SAFETY: Check recursion depth
        runtime_config = _get_runtime_config()
        MAX_RECURSION_DEPTH = runtime_config.limits.max_recursion_depth
        if recursion_depth > MAX_RECURSION_DEPTH:
            error_msg = f"MAX_RECURSION_DEPTH ({MAX_RECURSION_DEPTH}) exceeded in circuit {circuit_id}"
            logger.error(f"🚨 {error_msg}")
            return CircuitExecutionResult(
                success=False,
                final_state="RECURSION_LIMIT_EXCEEDED",
                output={"error": error_msg},
                state_history=[],
                syscall_count=0,
                error=error_msg,
            )

        # META-CIRCUIT: Notify start
        if self._on_circuit_start:
            try:
                self._on_circuit_start(circuit_id, raw_input, requester_id)
            except Exception as e:
                logger.warning(f"Meta-callback on_start failed: {e}")

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
                    "syscall_type": compilation.syscall_request.syscall_type.value
                    if compilation.syscall_request
                    else None,
                    "params": compilation.syscall_request.params if compilation.syscall_request else {},
                    "confidence": compilation.confidence,
                },
                # Also store the actual request for later use
                "_syscall_request": compilation.syscall_request,
            },
        )

        states = circuit_def.get("states", {})
        max_transitions = runtime_config.limits.max_circuit_transitions
        syscall_count = 0

        # Clear any previous violations
        self.invariant_checker.clear_violations()

        # Check global circuit invariants at start
        global_invariants = circuit_def.get("invariants", [])
        global_invariant_checks = [inv.get("check", inv) if isinstance(inv, dict) else inv for inv in global_invariants]
        if global_invariant_checks:
            logger.info(f"🔒 Checking {len(global_invariant_checks)} global invariants...")
            if not self.invariant_checker.check_invariants(global_invariant_checks, state.variables, "GLOBAL"):
                violations = self.invariant_checker.get_violations()
                error_msg = f"Global invariant violation: {violations[0].reason if violations else 'unknown'}"
                logger.error(f"🚨 {error_msg}")

                # META-CIRCUIT: Notify error
                if self._on_error:
                    try:
                        self._on_error(circuit_id, "GLOBAL", error_msg)
                    except Exception as e:
                        logger.warning(f"Meta-callback on_error failed: {e}")

                return CircuitExecutionResult(
                    success=False,
                    final_state="INVARIANT_VIOLATION",
                    output={"error": error_msg, "violations": [v.__dict__ for v in violations]},
                    state_history=state.history,
                    syscall_count=syscall_count,
                    error=error_msg,
                )

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

            # ================================================================
            # INVARIANT ENFORCEMENT - Check state invariants BEFORE execution
            # ================================================================
            state_invariants = current_state_def.get("invariants", [])
            if state_invariants:
                logger.info(f"🔒 Checking {len(state_invariants)} invariants for state {current_state_name}...")
                if not self.invariant_checker.check_invariants(state_invariants, state.variables, current_state_name):
                    violations = self.invariant_checker.get_violations()
                    error_msg = f"State invariant violation in {current_state_name}: {violations[-1].reason if violations else 'unknown'}"
                    logger.error(f"🚨 {error_msg}")

                    # META-CIRCUIT: Notify error (may attempt recovery)
                    if self._on_error:
                        try:
                            recovery = self._on_error(circuit_id, current_state_name, error_msg)
                            if recovery:
                                logger.info(f"🔧 Recovery suggested: {recovery}")
                                # Recovery could modify variables or skip state
                        except Exception as e:
                            logger.warning(f"Meta-callback on_error failed: {e}")

                    # HALT EXECUTION - invariants are NOT documentation, they are SECURITY
                    result = CircuitExecutionResult(
                        success=False,
                        final_state="INVARIANT_VIOLATION",
                        output={
                            "error": error_msg,
                            "state": current_state_name,
                            "violations": [v.__dict__ for v in violations],
                        },
                        state_history=state.history,
                        syscall_count=syscall_count,
                        error=error_msg,
                    )

                    if self._on_circuit_end:
                        try:
                            self._on_circuit_end(circuit_id, False, "INVARIANT_VIOLATION", result.output)
                        except Exception as e:
                            logger.warning(f"Meta-callback on_end failed: {e}")

                    return result

            # Check if terminal
            if current_state_def.get("terminal", False):
                state.is_terminal = True
                # BACKWARD COMPATIBILITY: Support both 'output' and 'result' fields
                output_def = current_state_def.get("output") or current_state_def.get("result", {})
                state.output = self._resolve_output(
                    output_def,
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

                elif action == "GENERATE_MICRO_CIRCUIT":
                    # VIBECORTEX: Just-in-Time Circuit Generation
                    context = self._resolve_params(operation.get("context", {}), state.variables)
                    constraints = operation.get("constraints", {})

                    # Get Architect Agent (or fallback to Science)
                    architect = self.kernel.get_agent("architect") or self.kernel.get_agent("science")
                    if not architect:
                        raise RuntimeError("No Architect agent available for circuit generation")

                    # Prompt for circuit generation
                    prompt = f"""
                    TASK: Generate a valid YAML cognitive circuit (micro-circuit) for the following context.

                    CONTEXT:
                    {json.dumps(context, indent=2)}

                    CONSTRAINTS:
                    - Max states: {constraints.get("max_states", 3)}
                    - Allowed tools: {constraints.get("allowed_tools", "ALL")}
                    - Output format: ONLY valid YAML, no markdown blocks.

                    The circuit must follow the standard schema:
                    circuit:
                      id: "MICRO_GENERATED_..."
                      entry_state: "START"
                      states: ...
                    """

                    logger.info("🧠 VibeCortex: Generating micro-circuit...")
                    generated_yaml = architect.run(prompt)  # Assuming .run() or .execute()

                    # Clean markdown code blocks if present
                    if "```yaml" in generated_yaml:
                        generated_yaml = generated_yaml.split("```yaml")[1].split("```")[0]
                    elif "```" in generated_yaml:
                        generated_yaml = generated_yaml.split("```")[1].split("```")[0]

                    try:
                        micro_circuit = yaml.safe_load(generated_yaml)
                        # Unwrap if nested under 'circuit' key
                        if "circuit" in micro_circuit:
                            micro_circuit = micro_circuit["circuit"]

                        # Validate basic structure
                        if "states" not in micro_circuit:
                            raise ValueError("Generated YAML missing 'states'")

                        state.variables["generated_circuit"] = micro_circuit
                        logger.info(f"✨ Micro-circuit generated: {micro_circuit.get('id', 'UNKNOWN')}")

                    except Exception as e:
                        logger.error(f"Failed to parse generated circuit: {e}")
                        state.variables["generation_error"] = str(e)
                        # Don't crash, let invariants handle it

                elif action == "EXECUTE_MICRO_CIRCUIT":
                    # VIBECORTEX: Recursive Execution
                    micro_circuit = state.variables.get("generated_circuit")
                    if not micro_circuit:
                        logger.error("No micro-circuit found to execute")
                        state.variables["micro_result"] = {"success": False, "error": "No circuit generated"}
                    else:
                        logger.info("🚀 Launching Micro-Circuit...")
                        micro_result = self._execute_circuit(
                            micro_circuit,
                            raw_input=state.variables.get("raw_input", ""),  # Pass original input or derived
                            compilation=compilation,  # Pass original compilation context
                            requester_id=requester_id,
                            recursion_depth=recursion_depth + 1,  # RECURSION!
                        )

                        state.variables["micro_result"] = {
                            "success": micro_result.success,
                            "output": micro_result.output,
                            "final_state": micro_result.final_state,
                        }
                        logger.info(f"🏁 Micro-Circuit finished: {micro_result.success}")

                elif action == "EXECUTE_SYSCALL":
                    # The actual syscall execution
                    syscall_type_str = operation.get("syscall_type")
                    syscall_type = SyscallType[syscall_type_str]

                    # For SPAWN_COGNITION, use the pre-compiled request IF it exists and is valid
                    if syscall_type == SyscallType.SPAWN_COGNITION and state.variables.get("_syscall_request"):
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

            # ================================================================
            # POST-OPERATION INVARIANT CHECK - Ensure operations didn't break anything
            # ================================================================
            if state_invariants:
                logger.debug(f"🔒 Re-checking invariants after operations in {current_state_name}...")
                if not self.invariant_checker.check_invariants(state_invariants, state.variables, current_state_name):
                    violations = self.invariant_checker.get_violations()
                    error_msg = f"Post-operation invariant violation in {current_state_name}: {violations[-1].reason if violations else 'unknown'}"
                    logger.error(f"🚨 {error_msg}")

                    if self._on_error:
                        try:
                            self._on_error(circuit_id, current_state_name, error_msg)
                        except Exception as e:
                            logger.warning(f"Meta-callback on_error failed: {e}")

                    result = CircuitExecutionResult(
                        success=False,
                        final_state="INVARIANT_VIOLATION",
                        output={
                            "error": error_msg,
                            "state": current_state_name,
                            "phase": "post_operation",
                            "violations": [v.__dict__ for v in violations],
                        },
                        state_history=state.history,
                        syscall_count=syscall_count,
                        error=error_msg,
                    )

                    if self._on_circuit_end:
                        try:
                            self._on_circuit_end(circuit_id, False, "INVARIANT_VIOLATION", result.output)
                        except Exception as e:
                            logger.warning(f"Meta-callback on_end failed: {e}")

                    return result

            # Evaluate transitions
            # BACKWARD COMPATIBILITY: Support old-style on_success/on_failure format
            transitions = current_state_def.get("transitions", [])
            if not transitions:
                # Convert on_success/on_failure to transitions format
                if "on_success" in current_state_def:
                    transitions.append(
                        {
                            "condition": "true",  # Default: always transition
                            "to": current_state_def["on_success"],
                        }
                    )
                    logger.debug(f"   ⚙️ Converted on_success → {current_state_def['on_success']}")

            next_state = self._evaluate_transitions(
                transitions,
                state.variables,
            )

            if next_state:
                # META-CIRCUIT: Notify state transition
                if self._on_state_transition:
                    try:
                        self._on_state_transition(circuit_id, current_state_name, next_state, state.variables)
                    except Exception as e:
                        logger.warning(f"Meta-callback on_transition failed: {e}")

                state.current_state = next_state
            else:
                # No valid transition - stuck
                error_msg = f"Circuit stuck at state: {current_state_name}"

                # META-CIRCUIT: Notify error (may attempt recovery)
                if self._on_error:
                    try:
                        recovery = self._on_error(circuit_id, current_state_name, error_msg)
                        if recovery:
                            logger.info(f"🔧 Recovery action suggested: {recovery}")
                            # Could implement recovery logic here
                    except Exception as e:
                        logger.warning(f"Meta-callback on_error failed: {e}")

                result = CircuitExecutionResult(
                    success=False,
                    final_state=current_state_name,
                    output={"error": "No valid transition from current state"},
                    state_history=state.history,
                    syscall_count=syscall_count,
                    error=error_msg,
                )

                # META-CIRCUIT: Notify end (failure)
                if self._on_circuit_end:
                    try:
                        self._on_circuit_end(circuit_id, False, current_state_name, result.output)
                    except Exception as e:
                        logger.warning(f"Meta-callback on_end failed: {e}")

                return result

        # Build final result
        final_state = state.current_state
        # BACKWARD COMPATIBILITY: Accept multiple success indicators
        # - Explicit "SUCCESS" state name
        # - Terminal state with result.status == "success"
        # - Terminal state without explicit failure markers
        success = final_state == "SUCCESS"
        if not success and state.is_terminal and state.output:
            # Check if terminal state indicates success via result field
            result_status = state.output.get("status", "").lower()
            success = result_status == "success"

        result = CircuitExecutionResult(
            success=success,
            final_state=final_state,
            output=state.output or {},
            state_history=state.history,
            syscall_count=syscall_count,
            error=None if success else state.output.get("reason") if state.output else None,
        )

        # META-CIRCUIT: Notify end
        if self._on_circuit_end:
            try:
                self._on_circuit_end(circuit_id, success, final_state, result.output)
            except Exception as e:
                logger.warning(f"Meta-callback on_end failed: {e}")

        return result

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
                logger.info(
                    f"   compiled_request.is_syscall = {cr.get('is_syscall')} (type: {type(cr.get('is_syscall'))})"
                )
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

        Supports:
        - "variable is not empty"
        - "variable is empty"
        - "variable == value"
        - "variable != value"
        """
        try:
            condition = condition.strip()

            # Simple boolean literals
            if condition.lower() == "true":
                return True
            if condition.lower() == "false":
                return False

            # Pattern: "X is not empty"
            if " is not empty" in condition:
                path = condition.replace(" is not empty", "").strip()
                value = self._resolve_path(path, variables)
                result = value is not None and value != "" and value != [] and value != {}
                logger.debug(f"Condition check: {path} is not empty? {result} (value: {type(value)})")
                return result

            # Pattern: "X is empty"
            if " is empty" in condition:
                path = condition.replace(" is empty", "").strip()
                value = self._resolve_path(path, variables)
                result = value is None or value == "" or value == [] or value == {}
                logger.debug(f"Condition check: {path} is empty? {result} (value: {type(value)})")
                return result

            # Pattern: "X != Y"
            if " != " in condition:
                parts = condition.split(" != ")
                path = parts[0].strip()
                expected = parts[1].strip().lower()
                value = self._resolve_path(path, variables)

                if expected == "null" or expected == "none":
                    return value is not None

                result = str(value).lower() != expected
                return result

            # Pattern: "X == Y"
            if " == " in condition:
                parts = condition.split(" == ")
                path = parts[0].strip()
                expected = parts[1].strip().lower()
                value = self._resolve_path(path, variables)

                if expected == "null" or expected == "none":
                    return value is None

                if expected in ("true", "false"):
                    result = bool(value) == (expected == "true")
                else:
                    result = str(value).lower() == expected
                return result

            logger.warning(f"Unknown condition format: {condition}")
            return False

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
# META-CIRCUIT MANAGER - Auto-instantiates TASK_LEDGER and ERROR_RECOVERY
# ============================================================================


# OPUS-118: TaskLedgerEntry and ErrorRecoveryAttempt moved to vibe_core/circuit_types.py


class MetaCircuitManager:
    """
    Manages TASK_LEDGER_V1 and ERROR_RECOVERY_V1 as active observers.

    This class implements the meta-circuit logic that was previously just
    YAML definitions. It:

    1. TASK_LEDGER: Tracks progress, detects stuck states, triggers reflection
    2. ERROR_RECOVERY: Classifies errors, attempts recovery, escalates if needed

    Unlike the circuit definitions in YAML, this is the RUNTIME implementation.
    """

    def __init__(self, executor: CognitiveCircuitExecutor):
        self.executor = executor
        self.ledgers: Dict[str, TaskLedgerEntry] = {}
        self.recovery_attempts: List[ErrorRecoveryAttempt] = []

        # Config from TASK_LEDGER_V1 circuit definition
        runtime_config = _get_runtime_config()
        self.reflection_interval_transitions = runtime_config.circuit_recovery.reflection_interval
        self.stuck_threshold_same_state = runtime_config.circuit_recovery.stuck_threshold
        self.max_retry_attempts = runtime_config.circuit_recovery.max_retry_attempts

        # Execution counter for generating IDs
        self._execution_counter = 0

        logger.info("🧠 Meta-Circuit Manager initialized")

    def wire_callbacks(self) -> None:
        """Wire this manager as callbacks to the circuit executor."""
        self.executor.set_meta_callbacks(
            on_start=self._on_circuit_start,
            on_transition=self._on_state_transition,
            on_end=self._on_circuit_end,
            on_error=self._on_error,
        )
        logger.info("🔗 Meta-Circuit Manager wired to executor")

    def _generate_execution_id(self, circuit_id: str) -> str:
        """Generate unique execution ID."""
        import time

        self._execution_counter += 1
        return f"{circuit_id}_{int(time.time())}_{self._execution_counter}"

    # =========================================================================
    # TASK_LEDGER_V1 Implementation
    # =========================================================================

    def _on_circuit_start(self, circuit_id: str, raw_input: str, requester_id: str) -> None:
        """TASK_LEDGER: INIT state - create ledger for execution."""
        import time

        execution_id = self._generate_execution_id(circuit_id)

        ledger = TaskLedgerEntry(
            circuit_id=circuit_id,
            execution_id=execution_id,
            started_at=time.time(),
        )

        self.ledgers[execution_id] = ledger
        logger.info(f"📒 TASK_LEDGER: Initialized tracking for {circuit_id} (exec_id={execution_id})")

    def _on_state_transition(
        self,
        circuit_id: str,
        from_state: str,
        to_state: str,
        variables: Dict[str, Any],
    ) -> None:
        """TASK_LEDGER: TRACK state - record transition, check for stuck."""
        import time

        # Find the active ledger for this circuit
        ledger = self._find_active_ledger(circuit_id)
        if not ledger:
            logger.warning(f"📒 No active ledger for {circuit_id}")
            return

        # Record transition
        ledger.states_visited.append(to_state)
        ledger.transitions.append(
            {
                "from": from_state,
                "to": to_state,
                "timestamp": time.time(),
            }
        )

        # Check for stuck state (same state visited multiple times in a row)
        if to_state == ledger.last_state:
            ledger.stuck_count += 1
            if ledger.stuck_count >= self.stuck_threshold_same_state:
                logger.warning(f"📒 TASK_LEDGER: Stuck detected! {to_state} visited {ledger.stuck_count} times")
                self._trigger_reflection(ledger, "stuck_detected", variables)
        else:
            ledger.stuck_count = 0
            ledger.last_state = to_state

        # Periodic reflection
        if len(ledger.transitions) % self.reflection_interval_transitions == 0:
            self._trigger_reflection(ledger, "periodic", variables)

        logger.debug(f"📒 TASK_LEDGER: Recorded {from_state} → {to_state}")

    def _trigger_reflection(self, ledger: TaskLedgerEntry, reason: str, variables: Dict[str, Any]) -> None:
        """TASK_LEDGER: REFLECT state - evaluate progress."""
        import time

        reflection = {
            "timestamp": time.time(),
            "reason": reason,
            "states_so_far": len(ledger.states_visited),
            "last_state": ledger.last_state,
            "stuck_count": ledger.stuck_count,
            "decision": "continue",  # Default decision
        }

        # Evaluate progress
        if reason == "stuck_detected":
            reflection["decision"] = "replan" if ledger.stuck_count > 5 else "adjust"
            reflection["recommendation"] = "Consider alternative approach"
        elif len(ledger.states_visited) > 15:
            reflection["decision"] = "escalate"
            reflection["recommendation"] = "Taking too many transitions"

        ledger.reflections.append(reflection)
        logger.info(f"🤔 TASK_LEDGER: Reflection - {reason}: decision={reflection['decision']}")

    def _on_circuit_end(self, circuit_id: str, success: bool, final_state: str, output: Dict[str, Any]) -> None:
        """TASK_LEDGER: DONE state - finalize ledger."""
        import time

        ledger = self._find_active_ledger(circuit_id)
        if not ledger:
            return

        ledger.completed_at = time.time()
        ledger.success = success

        duration = ledger.completed_at - ledger.started_at
        logger.info(
            f"📒 TASK_LEDGER: Completed {circuit_id} "
            f"(success={success}, states={len(ledger.states_visited)}, "
            f"reflections={len(ledger.reflections)}, duration={duration:.2f}s)"
        )

    def _find_active_ledger(self, circuit_id: str) -> Optional[TaskLedgerEntry]:
        """Find the most recent active ledger for a circuit."""
        for exec_id in reversed(list(self.ledgers.keys())):
            ledger = self.ledgers[exec_id]
            if ledger.circuit_id == circuit_id and ledger.completed_at is None:
                return ledger
        return None

    # =========================================================================
    # ERROR_RECOVERY_V1 Implementation
    # =========================================================================

    def _on_error(self, circuit_id: str, state: str, error: str) -> Optional[str]:
        """
        ERROR_RECOVERY: DETECT + ANALYZE + REPLAN states.

        Returns recovery action suggestion or None.
        """
        import time

        logger.info(f"🔧 ERROR_RECOVERY: Error in {circuit_id}/{state}: {error}")

        # Classify error type (DETECT state logic)
        error_type = self._classify_error(error)

        # Count previous recovery attempts for this circuit
        recent_attempts = [
            a
            for a in self.recovery_attempts
            if a.state == state and (time.time() - a.timestamp) < 300  # Last 5 minutes
        ]
        retry_count = len(recent_attempts)

        # Determine strategy (ANALYZE + REPLAN logic)
        strategy = self._select_recovery_strategy(error_type, retry_count)

        # Record attempt
        attempt = ErrorRecoveryAttempt(
            error_type=error_type,
            error_message=error,
            state=state,
            timestamp=time.time(),
            strategy=strategy,
            success=False,  # Will be updated if circuit succeeds
            retry_count=retry_count,
        )
        self.recovery_attempts.append(attempt)

        if strategy == "escalate":
            logger.warning(f"🚨 ERROR_RECOVERY: Escalating - {error_type} after {retry_count} attempts")
            return None  # No recovery possible

        logger.info(f"🔧 ERROR_RECOVERY: Suggesting {strategy} for {error_type}")
        return strategy

    def _classify_error(self, error: str) -> str:
        """Classify error based on ERROR_RECOVERY_V1 error_patterns."""
        error_lower = error.lower()

        # Transient errors - can retry
        transient_patterns = ["timeout", "connection", "rate_limit", "temporary", "unavailable"]
        if any(p in error_lower for p in transient_patterns):
            return "transient"

        # Input errors - need adjustment
        input_patterns = ["validation", "parse", "missing", "invalid", "type"]
        if any(p in error_lower for p in input_patterns):
            return "input_error"

        # State errors - need replan
        state_patterns = ["invariant", "precondition", "postcondition", "stuck"]
        if any(p in error_lower for p in state_patterns):
            return "state_error"

        # Resource errors - need escalation
        resource_patterns = ["memory", "disk", "quota", "permission"]
        if any(p in error_lower for p in resource_patterns):
            return "resource_error"

        # Logic errors - need escalation
        logic_patterns = ["assertion", "unexpected", "impossible"]
        if any(p in error_lower for p in logic_patterns):
            return "logic_error"

        return "unknown"

    def _select_recovery_strategy(self, error_type: str, retry_count: int) -> str:
        """Select recovery strategy based on ERROR_RECOVERY_V1 config."""
        if retry_count >= self.max_retry_attempts:
            return "escalate"

        strategies = {
            "transient": "retry_same",
            "input_error": "retry_adjusted",
            "state_error": "replan",
            "resource_error": "escalate",
            "logic_error": "escalate",
            "unknown": "retry_same" if retry_count < 2 else "escalate",
        }

        return strategies.get(error_type, "escalate")

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Get summary of all tracked executions."""
        return {
            "total_executions": len(self.ledgers),
            "active_executions": sum(1 for ledger in self.ledgers.values() if ledger.completed_at is None),
            "successful_executions": sum(1 for ledger in self.ledgers.values() if ledger.success is True),
            "failed_executions": sum(1 for ledger in self.ledgers.values() if ledger.success is False),
            "total_recovery_attempts": len(self.recovery_attempts),
        }


# ============================================================================
# FACTORY
# ============================================================================


def create_circuit_executor(kernel: "RealVibeKernel") -> CognitiveCircuitExecutor:
    """Factory function to create a Cognitive Circuit Executor."""
    return CognitiveCircuitExecutor(kernel)


def create_circuit_executor_with_meta(kernel: "RealVibeKernel") -> tuple[CognitiveCircuitExecutor, MetaCircuitManager]:
    """
    Factory function to create a Cognitive Circuit Executor with meta-circuit support.

    This is the recommended way to create the executor - it automatically
    wires TASK_LEDGER and ERROR_RECOVERY as active observers.
    """
    executor = CognitiveCircuitExecutor(kernel)
    manager = MetaCircuitManager(executor)
    manager.wire_callbacks()
    return executor, manager


__all__ = [
    "CognitiveCircuitExecutor",
    "CircuitState",
    "CircuitExecutionResult",
    "InvariantChecker",
    "InvariantViolation",
    "MetaCircuitManager",
    "TaskLedgerEntry",
    "ErrorRecoveryAttempt",
    "create_circuit_executor",
    "create_circuit_executor_with_meta",
]
