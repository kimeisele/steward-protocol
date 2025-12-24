"""
🎯 DETERMINISTIC EXECUTOR (GAD-5000: DETERMINISTIC EXECUTION)
The Dungeon Master - Executes deterministic playbook sequences.

Role:
1. Loads playbooks from YAML (knowledge/playbooks/)
2. Matches user intent to appropriate playbook
3. Executes playbook phases sequentially
4. Tracks state and emits events for visualization
5. Handles errors and conditional logic

Philosophy:
- Input -> Semantic Graph (SANKHYA) -> Playbook Node -> Execution (KARMA)
- No hallucinations. Just rules and state machines.
- Each phase is deterministic: Check -> Execute -> Emit -> Continue.

Enhancements (GOLDEN SHOT):
- LLM Dynamic Routing: Use LLM for ambiguous path decisions
- Evolutionary Loop (EAD): Generate playbook proposals when no match
- Fractal/Nested Playbooks: Support playbooks triggering other playbooks
- State Persistence: Save/restore execution state across restarts
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Jinja2 for template substitution (GAD-5000 Variable Injection)
try:
    from jinja2 import BaseLoader, Environment, UndefinedError

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

# Action Handler Registry (GAD-5000 Registry Pattern)
try:
    from vibe_core.cartridges.system.envoy.action_handlers import (
        ActionContext,
        ActionHandlerRegistry,
        create_default_registry,
    )

    ACTION_HANDLERS_AVAILABLE = True
except ImportError:
    ACTION_HANDLERS_AVAILABLE = False

# Blueprint Generator (GAD-5001 Raw Input → Structured Params)
try:
    from vibe_core.cartridges.system.envoy.blueprint_generator import BlueprintGenerator

    BLUEPRINT_GENERATOR_AVAILABLE = True
except ImportError:
    BLUEPRINT_GENERATOR_AVAILABLE = False

# Cognitive Circuit Executor (GAD-5500 VEDA-4 Integration)
try:
    from vibe_core.circuit_executor import (
        CircuitExecutionResult,
        CognitiveCircuitExecutor,
        MetaCircuitManager,
        create_circuit_executor_with_meta,
    )

    CIRCUIT_EXECUTOR_AVAILABLE = True
except ImportError:
    CIRCUIT_EXECUTOR_AVAILABLE = False

logger = logging.getLogger("DETERMINISTIC_EXECUTOR")


class PhaseStatus(Enum):
    """State machine for playbook phases"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    BLOCKED = "blocked"  # Waiting for approval


class ActionType(Enum):
    """Types of actions a phase can execute"""

    CALL_AGENT = "CALL_AGENT"  # Delegate to another agent
    CHECK_STATE = "CHECK_STATE"  # Validate preconditions
    EXECUTE_SCRIPT = "EXECUTE_SCRIPT"  # Run deterministic script
    EMIT_EVENT = "EMIT_EVENT"  # Emit event to visualization layer


@dataclass
class PlaybookPhase:
    """A single phase within a playbook"""

    phase_id: str
    name: str
    description: str
    actions: List[Dict[str, Any]]
    on_success: str  # Next phase or "COMPLETE"
    on_failure: str  # Next phase or "ABORT"
    state_var: Optional[str] = None
    timeout_seconds: int = 60
    requires_approval: bool = False
    status: PhaseStatus = PhaseStatus.PENDING
    result: Optional[Dict[str, Any]] = None


@dataclass
class PlaybookDefinition:
    """A complete playbook"""

    id: str
    name: str
    description: str
    intent_match: Dict[str, Any]
    phases: List[PlaybookPhase]
    variables: Dict[str, Any] = field(default_factory=dict)
    # Phoenix Config: Templates from YAML (Code/Config Split)
    templates: Dict[str, str] = field(default_factory=dict)


@dataclass
class PlaybookExecution:
    """Tracks a playbook execution in progress"""

    execution_id: str
    playbook_id: str
    user_input: str
    current_phase_id: Optional[str] = None
    phase_results: Dict[str, Any] = field(default_factory=dict)
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    started_at: float = field(default_factory=lambda: datetime.now().timestamp())
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    # GAD-5001: Extracted blueprint values (replaces defaults)
    blueprint_values: Dict[str, Any] = field(default_factory=dict)

    def is_complete(self) -> bool:
        return self.status in ["COMPLETED", "FAILED"]


class DeterministicExecutor:
    """
    The Dungeon Master - GAD-5000 Deterministic Execution Engine.
    Loads playbooks, matches intents, and executes phases deterministically.
    """

    def __init__(self, knowledge_dir: str = "knowledge", playbooks_dir: str = None, ephemeral=None):
        """
        Initialize DeterministicExecutor.

        Args:
            knowledge_dir: Knowledge directory path
            playbooks_dir: Playbooks directory path (optional)
            ephemeral: EphemeralStorage instance (OPUS Phase 2: dependency injection)
        """
        self.knowledge_dir = Path(knowledge_dir)
        self._ephemeral = ephemeral

        # Playbooks location: use explicit path, or detect from project structure
        if playbooks_dir:
            self.playbooks_dir = Path(playbooks_dir)
        else:
            # Primary: vibe_core/playbook/circuits (canonical location)
            # Path: vibe_core/cartridges/system/envoy/deterministic_executor.py
            # Need 5 parents to get to project root: envoy(1) -> system(2) -> cartridges(3) -> vibe_core(4) -> project(5)
            project_root = Path(__file__).parent.parent.parent.parent.parent
            circuits_dir = project_root / "vibe_core" / "playbook" / "circuits"
            if circuits_dir.exists():
                self.playbooks_dir = circuits_dir
            else:
                # Fallback: knowledge/playbooks (legacy location)
                self.playbooks_dir = self.knowledge_dir / "playbooks"

        self.playbooks: Dict[str, PlaybookDefinition] = {}
        self.executions: Dict[str, PlaybookExecution] = {}
        self.state_dir = Path(".playbook_state")  # Persistence directory
        self.state_dir.mkdir(exist_ok=True)

        # Import LLM Engine (GAD-6000)
        self.llm = None
        try:
            from vibe_core.runtime.llm_engine import llm

            self.llm = llm
        except ImportError:
            logger.warning("⚠️  LLM Engine not available (optional)")

        # Initialize Action Handler Registry (GAD-5000 Registry Pattern)
        # OPUS Phase 2: Pass ephemeral storage to handlers via dependency injection
        self.action_registry = None
        if ACTION_HANDLERS_AVAILABLE:
            from vibe_core.cartridges.system.envoy.action_handlers import create_registry_with_ephemeral

            self.action_registry = create_registry_with_ephemeral(ephemeral)
            logger.info(f"✅ Action handlers: {self.action_registry.registered_types}")
        else:
            logger.warning("⚠️  Action handlers not available (using stubs)")

        # Initialize Blueprint Generator (GAD-5001 Raw Input → Structured Params)
        self.blueprint_generator = None
        if BLUEPRINT_GENERATOR_AVAILABLE:
            self.blueprint_generator = BlueprintGenerator()
            logger.info("✅ Blueprint Generator initialized")
        else:
            logger.warning("⚠️  Blueprint Generator not available (using defaults)")

        # Circuit Executor (GAD-5500 VEDA-4) - lazy initialized when kernel available
        # Includes MetaCircuitManager for TASK_LEDGER and ERROR_RECOVERY
        self.circuit_executor = None
        self.meta_circuit_manager = None
        self._circuit_executor_available = CIRCUIT_EXECUTOR_AVAILABLE
        if CIRCUIT_EXECUTOR_AVAILABLE:
            logger.info("✅ Circuit Executor available (will init with kernel + meta-circuits)")
        else:
            logger.warning("⚠️  Circuit Executor not available")

        self._load_playbooks()
        self._load_persisted_executions()
        logger.info(f"🎯 Playbook Engine initialized with {len(self.playbooks)} playbooks")

    def _ensure_circuit_executor(self, kernel) -> bool:
        """
        Lazy-initialize the circuit executor when kernel becomes available.

        Uses create_circuit_executor_with_meta to automatically wire
        TASK_LEDGER and ERROR_RECOVERY as active observers.

        Returns True if circuit executor is ready to use.
        """
        if self.circuit_executor is not None:
            return True

        if not self._circuit_executor_available:
            return False

        if kernel is None:
            return False

        try:
            # Create executor WITH meta-circuit support (TASK_LEDGER + ERROR_RECOVERY)
            self.circuit_executor, self.meta_circuit_manager = create_circuit_executor_with_meta(kernel)
            logger.info("🔌 Circuit Executor initialized with kernel + meta-circuits")
            logger.info("   📒 TASK_LEDGER_V1: Active (tracking progress)")
            logger.info("   🔧 ERROR_RECOVERY_V1: Active (handling errors)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Circuit Executor: {e}")
            self._circuit_executor_available = False
            return False

    def _load_playbooks(self):
        """Load all playbooks/circuits from playbooks directory

        Supports both legacy 'playbook' format and new VEDA-4 'circuit' format.
        """
        if not self.playbooks_dir.exists():
            logger.warning(f"⚠️  Playbooks directory not found: {self.playbooks_dir}")
            return

        for playbook_file in self.playbooks_dir.glob("**/*.yaml"):
            if playbook_file.name in ("schema.yaml", "_registry.yaml"):
                continue  # Skip meta files

            try:
                with open(playbook_file, "r") as f:
                    data = yaml.safe_load(f)

                if not data:
                    logger.warning(f"⚠️  Empty file: {playbook_file.name}")
                    continue

                # Support both legacy 'playbook' and new 'circuit' format
                # Phoenix Config: Templates from YAML (Code/Config Split)
                templates = data.get("templates", {})

                if "playbook" in data:
                    playbook_data = data["playbook"]
                    phases = self._parse_phases(playbook_data.get("phases", []))
                    # Legacy playbooks may have templates in playbook_data
                    if not templates:
                        templates = playbook_data.get("templates", {})
                elif "circuit" in data:
                    # VEDA-4 Cognitive Circuit format
                    circuit_data = data["circuit"]
                    phases = self._parse_circuit_states(circuit_data.get("states", {}))
                    playbook_data = {
                        "id": circuit_data.get("id", playbook_file.stem.upper()),
                        "name": circuit_data.get("id", playbook_file.stem),
                        "description": circuit_data.get("description", ""),
                        "intent_match": circuit_data.get(
                            "intent_match",
                            {
                                "primary": circuit_data.get("domain", "general").upper(),
                            },
                        ),
                        "variables": circuit_data.get("variables", {}),
                    }
                else:
                    logger.warning(f"⚠️  Invalid format in {playbook_file.name} (no 'playbook' or 'circuit' key)")
                    continue

                playbook = PlaybookDefinition(
                    id=playbook_data.get("id", playbook_file.stem),
                    name=playbook_data.get("name", "Unknown"),
                    description=playbook_data.get("description", ""),
                    intent_match=playbook_data.get("intent_match", {}),
                    phases=phases,
                    variables=playbook_data.get("variables", {}),
                    templates=templates,  # Phoenix Config: Templates from YAML
                )

                self.playbooks[playbook.id] = playbook
                logger.info(f"✅ Loaded playbook: {playbook.id} ({playbook.name})")

            except Exception as e:
                logger.error(f"❌ Error loading playbook {playbook_file.name}: {e}")

    def _parse_circuit_states(self, states_data: Dict) -> List["PlaybookPhase"]:
        """Parse VEDA-4 circuit states into playbook phases"""
        phases = []
        for state_id, state_data in states_data.items():
            phase = PlaybookPhase(
                phase_id=state_id,
                name=state_data.get("name", state_id),
                description=state_data.get("description", ""),
                actions=state_data.get("actions", []),
                on_success=state_data.get("on_success", "COMPLETE"),
                on_failure=state_data.get("on_failure", "ABORT"),
                state_var=state_data.get("state_var"),
            )
            phases.append(phase)
        return phases

    def _parse_phases(self, phases_data: List[Dict]) -> List[PlaybookPhase]:
        """Parse phase definitions from YAML"""
        phases = []
        for phase_data in phases_data:
            phase = PlaybookPhase(
                phase_id=phase_data.get("phase_id", "unknown"),
                name=phase_data.get("name", ""),
                description=phase_data.get("description", ""),
                actions=phase_data.get("actions", []),
                on_success=phase_data.get("on_success", "COMPLETE"),
                on_failure=phase_data.get("on_failure", "ABORT"),
                state_var=phase_data.get("state_var"),
                timeout_seconds=phase_data.get("timeout_seconds", 60),
                requires_approval=phase_data.get("requires_approval", False),
            )
            phases.append(phase)
        return phases

    # ===== TEMPLATE RESOLUTION (GAD-5000 VARIABLE INJECTION) =====
    def _resolve_template_variables(
        self,
        value: Any,
        context: Dict[str, Any],
    ) -> Any:
        """
        Resolve Jinja2 template variables in playbook params.

        Supports:
        - {{ variable }} - Direct variable substitution
        - {{ phase_results.phase_name.field }} - Access to previous phase results
        - {{ user_input }} - Original user input
        - {{ playbook.variables.name }} - Playbook-defined variables

        Args:
            value: The value to resolve (string, dict, list, or primitive)
            context: Template context with available variables

        Returns:
            Resolved value with all templates substituted
        """
        if not JINJA2_AVAILABLE:
            # Fallback: simple regex replacement for basic {{ var }} patterns
            return self._resolve_template_fallback(value, context)

        return self._resolve_with_jinja2(value, context)

    def _resolve_with_jinja2(self, value: Any, context: Dict[str, Any]) -> Any:
        """Resolve templates using Jinja2 engine"""
        if isinstance(value, str):
            # Check if string contains template markers
            if "{{" not in value:
                return value
            try:
                env = Environment(loader=BaseLoader())
                template = env.from_string(value)
                resolved = template.render(**context)
                # Try to preserve type for simple substitutions like "{{ number }}"
                if value.strip().startswith("{{") and value.strip().endswith("}}"):
                    # Pure variable reference - try to return original type
                    var_name = value.strip()[2:-2].strip()
                    if var_name in context:
                        return context[var_name]
                return resolved
            except UndefinedError as e:
                logger.warning(f"⚠️  Template variable undefined: {e}")
                return value  # Return original on error
            except Exception as e:
                logger.warning(f"⚠️  Template resolution failed: {e}")
                return value

        elif isinstance(value, dict):
            return {k: self._resolve_with_jinja2(v, context) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._resolve_with_jinja2(item, context) for item in value]

        else:
            # Primitives (int, float, bool, None) pass through
            return value

    def _resolve_template_fallback(self, value: Any, context: Dict[str, Any]) -> Any:
        """Fallback template resolution without Jinja2 (basic {{ var }} only)"""
        if isinstance(value, str):
            if "{{" not in value:
                return value

            # Simple pattern: {{ var_name }} or {{ obj.attr }}
            pattern = r"\{\{\s*([\w.]+)\s*\}\}"

            def replacer(match):
                var_path = match.group(1)
                parts = var_path.split(".")
                result = context
                try:
                    for part in parts:
                        if isinstance(result, dict):
                            result = result.get(part)
                        else:
                            result = getattr(result, part, None)
                        if result is None:
                            return match.group(0)  # Keep original if not found
                    return str(result) if result is not None else match.group(0)
                except Exception:
                    return match.group(0)

            return re.sub(pattern, replacer, value)

        elif isinstance(value, dict):
            return {k: self._resolve_template_fallback(v, context) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._resolve_template_fallback(item, context) for item in value]

        return value

    def _build_template_context(
        self,
        playbook: "PlaybookDefinition",
        execution: "PlaybookExecution",
        intent_vector: Any = None,
    ) -> Dict[str, Any]:
        """
        Build the template context for variable resolution.

        Available in templates:
        - {{ user_input }} - Original user input
        - {{ phase_results }} - Dict of all phase results by state_var
        - {{ playbook_id }} - Current playbook ID
        - Any playbook.variables entries (defaults)
        - Blueprint-extracted values (override defaults) [GAD-5001]
        - Intent vector fields (concepts, agent, etc.)
        """
        context = {
            # Core execution context
            "user_input": execution.user_input,
            "phase_results": execution.phase_results,
            "playbook_id": playbook.id,
            "execution_id": execution.execution_id,
            # Playbook-defined variables (DEFAULTS)
            **playbook.variables,
            # GAD-5001: Blueprint-extracted values (OVERRIDE defaults)
            # This is the key difference: extracted values from raw input
            # replace generic defaults like "New Feature" with actual values
            **execution.blueprint_values,
        }

        # Add intent vector fields if available
        if intent_vector:
            if hasattr(intent_vector, "concepts"):
                context["concepts"] = list(intent_vector.concepts) if intent_vector.concepts else []
            if hasattr(intent_vector, "target_agent"):
                context["target_agent"] = intent_vector.target_agent
            if hasattr(intent_vector, "raw_input"):
                context["raw_input"] = intent_vector.raw_input

        # Flatten phase_results for easier access: {{ phase_name.field }}
        for state_var, result in execution.phase_results.items():
            if isinstance(result, dict):
                context[state_var] = result

        return context

    def find_playbook(self, concepts: Set[str]) -> Optional[PlaybookDefinition]:
        """
        Find the best matching playbook for a set of detected concepts.

        Matching logic:
        - primary: Must match
        - secondary: Optional, but increases confidence
        """
        best_match = None
        best_score = 0

        for playbook in self.playbooks.values():
            intent_match = playbook.intent_match
            primary = intent_match.get("primary")
            secondary = intent_match.get("secondary", [])

            # Primary must be present
            if primary not in concepts:
                continue

            # Score: primary (10 points) + secondary matches (5 points each)
            score = 10
            if secondary:
                for sec in secondary:
                    if sec in concepts:
                        score += 5

            if score > best_score:
                best_score = score
                best_match = playbook

        return best_match

    async def execute(
        self,
        playbook_id: str,
        user_input: str,
        intent_vector: Any,
        kernel: Any = None,
        emit_event=None,
    ) -> Dict[str, Any]:
        """
        Execute a playbook step-by-step.

        GAD-5500: Now routes to VEDA-4 Circuit Executor for syscall intents.

        Args:
            playbook_id: ID of the playbook to execute
            user_input: The original user input
            intent_vector: The IntentVector from UniversalProvider
            kernel: The VibeKernel instance (for submitting tasks)
            emit_event: Async function to emit events

        Returns:
            Execution result with status and phase results
        """
        # =====================================================================
        # GAD-5500: VEDA-4 CIRCUIT ROUTING
        # Try circuit execution first for syscall intents
        # =====================================================================
        if kernel and self._ensure_circuit_executor(kernel):
            try:
                # Check if input compiles to a syscall
                compilation = self.circuit_executor.compiler.compile(user_input, "user")

                if compilation.is_syscall:
                    logger.info(f"🔌 CIRCUIT ROUTE: {compilation.syscall_request.syscall_type.value}")

                    if emit_event:
                        try:
                            await emit_event(
                                "ACTION",
                                f"Routing to Circuit Executor: {compilation.syscall_request.syscall_type.value}",
                                "circuit_executor",
                                {"syscall_type": compilation.syscall_request.syscall_type.value},
                            )
                        except Exception as e:
                            logger.warning(f"Event emission failed: {e}")

                    # Execute via circuit
                    circuit_result = self.circuit_executor.execute(user_input, "user")

                    # Convert CircuitExecutionResult to dict
                    return {
                        "status": "COMPLETED" if circuit_result.success else "FAILED",
                        "execution_mode": "circuit",
                        "circuit_id": circuit_result.final_state,
                        "output": circuit_result.output,
                        "state_history": circuit_result.state_history,
                        "syscall_count": circuit_result.syscall_count,
                        "error": circuit_result.error,
                    }

            except Exception as e:
                logger.warning(f"⚠️  Circuit execution failed, falling back to playbook: {e}")
                # Fall through to traditional playbook execution

        # =====================================================================
        # TRADITIONAL PLAYBOOK EXECUTION (fallback)
        # =====================================================================
        if playbook_id not in self.playbooks:
            logger.error(f"❌ Playbook not found: {playbook_id}")
            return {"status": "FAILED", "error": f"Playbook not found: {playbook_id}"}

        playbook = self.playbooks[playbook_id]
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        execution = PlaybookExecution(execution_id=execution_id, playbook_id=playbook_id, user_input=user_input)

        # GAD-5001: Generate blueprint from raw input (SHABDA actualized)
        # This transforms "Implement JWT auth" → {feature_name: "jwt-auth", ...}
        if self.blueprint_generator and playbook.variables:
            try:
                blueprint_values = await self.blueprint_generator.generate_blueprint(
                    raw_input=user_input,
                    playbook_variables=playbook.variables,
                    playbook_id=playbook_id,
                )
                execution.blueprint_values = blueprint_values
                logger.info(f"📋 Blueprint extracted: {list(blueprint_values.keys())}")
            except Exception as e:
                logger.warning(f"⚠️  Blueprint generation failed (using defaults): {e}")

        # Start execution
        logger.info(f"🚀 Starting playbook execution: {playbook.id} ({execution_id})")

        if emit_event:
            try:
                await emit_event(
                    "ACTION",
                    f"Started playbook: {playbook.name}",
                    "playbook_engine",
                    {"playbook_id": playbook_id, "execution_id": execution_id},
                )
            except Exception as e:
                logger.debug(f"Event emission failed: {e}")

        # Find the first phase
        first_phase = playbook.phases[0] if playbook.phases else None
        if not first_phase:
            execution.status = "FAILED"
            execution.error_message = "Playbook has no phases"
            return self._format_execution_result(execution, playbook)

        # Execute phases sequentially
        current_phase_id = first_phase.phase_id
        max_iterations = 100  # Prevent infinite loops

        for iteration in range(max_iterations):
            if not current_phase_id or current_phase_id in ["COMPLETE", "ABORT"]:
                break

            # Find the phase
            phase = None
            for p in playbook.phases:
                if p.phase_id == current_phase_id:
                    phase = p
                    break

            if not phase:
                logger.warning(f"⚠️  Phase not found: {current_phase_id}")
                break

            # Execute the phase
            logger.info(f"📍 Executing phase: {phase.name}")
            execution.current_phase_id = current_phase_id

            if emit_event:
                try:
                    await emit_event(
                        "THOUGHT",
                        f"Running: {phase.name}",
                        "playbook_engine",
                        {"phase_id": current_phase_id, "phase_name": phase.name},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")

            # Check if approval is required
            if phase.requires_approval:
                phase.status = PhaseStatus.BLOCKED
                if emit_event:
                    try:
                        await emit_event(
                            "ACTION",
                            f"Awaiting approval: {phase.name}",
                            "playbook_engine",
                            {"phase_id": current_phase_id, "requires_approval": True},
                        )
                    except Exception as e:
                        logger.debug(f"Event emission failed: {e}")
                # For now, auto-approve. In production, this would wait for user input
                logger.info(f"⏭️  Auto-approving phase (would wait for user in production): {phase.name}")

            # Execute phase actions
            phase.status = PhaseStatus.RUNNING
            phase_success = await self._execute_phase_actions(
                phase,
                playbook,
                execution,
                intent_vector,
                kernel,
                emit_event,
                execution.execution_id,
            )

            if phase_success:
                phase.status = PhaseStatus.COMPLETED
                if phase.state_var:
                    execution.phase_results[phase.state_var] = phase.result or {}
                current_phase_id = phase.on_success
            else:
                phase.status = PhaseStatus.FAILED
                current_phase_id = phase.on_failure

            # Save execution state after each phase (KARMA LEDGER)
            self._save_execution_state(execution)

            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        f"{'Completed' if phase_success else 'Failed'}: {phase.name}",
                        "playbook_engine",
                        {"phase_id": current_phase_id, "success": phase_success},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")

        # Execution complete
        execution.status = "COMPLETED" if current_phase_id == "COMPLETE" else "FAILED"
        execution.completed_at = datetime.now().timestamp()

        logger.info(f"✅ Playbook execution complete: {execution.execution_id} ({execution.status})")

        return self._format_execution_result(execution, playbook)

    async def _execute_phase_actions(
        self,
        phase: PlaybookPhase,
        playbook: PlaybookDefinition,
        execution: PlaybookExecution,
        intent_vector: Any,
        kernel: Any = None,
        emit_event=None,
        parent_execution_id: Optional[str] = None,
    ) -> bool:
        """
        Execute all actions within a phase.
        Returns True if successful, False if any action fails.
        Supports nested/fractal playbooks via CALL_PLAYBOOK action.
        """
        if not phase.actions:
            return True

        for action in phase.actions:
            # CRITICAL FIX (BREAK 3): Rebuild context EVERY action to get fresh phase_results
            # This ensures that render_output phase can see results from query_status, query_agents, query_tools
            template_context = self._build_template_context(playbook, execution, intent_vector)
            try:
                action_type = action.get("action_type", "EXECUTE_SCRIPT")
                # Support both 'target' and 'agent_id' for backwards compatibility
                target = action.get("target") or action.get("agent_id")
                raw_params = action.get("params", {})

                # RESOLVE TEMPLATE VARIABLES (GAD-5000 Variable Injection)
                params = self._resolve_template_variables(raw_params, template_context)
                # Also resolve target if it contains templates
                resolved_target = self._resolve_template_variables(target, template_context) if target else target

                logger.info(f"  → Executing action: {action_type} ({resolved_target})")
                if raw_params != params:
                    logger.debug(f"    📝 Resolved params: {raw_params} → {params}")

                if action_type == "EMIT_EVENT":
                    # Emit visualization event
                    if emit_event:
                        try:
                            await emit_event("ACTION", f"{resolved_target}", "playbook_engine", params)
                        except Exception as e:
                            logger.debug(f"Event emission failed: {e}")

                elif action_type == "CHECK_STATE":
                    # Validate preconditions via Action Handler Registry
                    if self.action_registry and self.action_registry.has("CHECK_STATE"):
                        handler = self.action_registry.get("CHECK_STATE")
                        action_context = ActionContext(
                            phase_id=phase.phase_id,
                            playbook_id=playbook.id,
                            execution_id=execution.execution_id,
                            user_input=execution.user_input,
                            phase_results=execution.phase_results,
                            kernel=kernel,
                            emit_event=emit_event,
                        )
                        result = await handler.execute(resolved_target, params, action_context)
                        if not result.success:
                            logger.warning(f"  ❌ State check failed: {result.error}")
                            return False
                        phase.result = result.data
                    else:
                        # No action handler - log warning and skip (don't fake success)
                        logger.warning(f"  ⚠️ CHECK_STATE skipped (no handler): {resolved_target}")
                        phase.result = {"skipped": True, "reason": "no_action_handler"}

                elif action_type == "EXECUTE_SCRIPT":
                    # Execute script via Action Handler Registry
                    if self.action_registry and self.action_registry.has("EXECUTE_SCRIPT"):
                        handler = self.action_registry.get("EXECUTE_SCRIPT")
                        action_context = ActionContext(
                            phase_id=phase.phase_id,
                            playbook_id=playbook.id,
                            execution_id=execution.execution_id,
                            user_input=execution.user_input,
                            phase_results=execution.phase_results,
                            kernel=kernel,
                            emit_event=emit_event,
                        )
                        result = await handler.execute(resolved_target, params, action_context)
                        if not result.success:
                            logger.warning(f"  ❌ Script failed: {result.error}")
                            return False
                        phase.result = result.data
                    else:
                        # No action handler - log warning and skip (don't fake success)
                        logger.warning(f"  ⚠️ EXECUTE_SCRIPT skipped (no handler): {resolved_target}")
                        phase.result = {"skipped": True, "reason": "no_action_handler", "script": resolved_target}

                elif action_type == "CALL_AGENT":
                    # Delegate to another agent (PLAYBOOK FIX: Actually call the agent!)
                    logger.info(f"  → Calling agent: {resolved_target}")
                    if kernel:
                        import asyncio

                        from vibe_core.scheduling.task import Task

                        task = Task(agent_id=resolved_target, payload=params)
                        logger.debug(f"  📤 Submitting task to {resolved_target}: {params}")

                        # Submit task (synchronous - returns task_id)
                        task_id = kernel.submit_task(task)
                        logger.debug(f"  📋 Task submitted: {task_id}")

                        # Wait for result (polling with timeout)
                        timeout_sec = phase.timeout_seconds
                        poll_interval = 0.5  # Check every 500ms
                        elapsed = 0
                        result = None

                        while elapsed < timeout_sec:
                            # 1. Drive the kernel (Herzschlag manuell auslösen)
                            if hasattr(kernel, "tick"):
                                kernel.tick()

                            # 2. Check for result
                            result = kernel.get_task_result(task_id)
                            if result:
                                break
                            await asyncio.sleep(poll_interval)
                            elapsed += poll_interval

                        if result:
                            phase.result = {
                                "agent": resolved_target,
                                "result": result,
                                "params": params,
                                "task_id": task_id,
                            }
                            status = result.get("status", "unknown")
                            # Check if agent returned an error
                            if status == "error":
                                error_msg = result.get("error", "Unknown error")
                                logger.warning(f"  ❌ Agent {resolved_target} returned error: {error_msg}")
                                return False  # Fail phase on agent error
                            logger.info(f"  ✓ Agent {resolved_target} returned: {status}")
                        else:
                            logger.warning(f"  ⏱️  Agent {resolved_target} timeout after {timeout_sec}s")
                            phase.result = {"error": "timeout", "agent": resolved_target, "task_id": task_id}
                            return False  # Fail phase on timeout
                    else:
                        logger.warning(f"  ⚠️ No kernel available, cannot execute agent call to {resolved_target}")
                        phase.result = {"error": "No kernel available", "agent": resolved_target}
                        return False  # Fail the phase if no kernel

                elif action_type == "CALL_PLAYBOOK":
                    # Execute nested playbook (FRACTAL/NESTED SUPPORT)
                    nested_playbook_id = resolved_target
                    if nested_playbook_id in self.playbooks:
                        logger.info(f"  🔗 Calling nested playbook: {nested_playbook_id}")
                        nested_result = await self.execute_nested_playbook(
                            playbook_id=nested_playbook_id,
                            user_input=execution.user_input,
                            intent_vector=intent_vector,
                            kernel=kernel,
                            emit_event=emit_event,
                            parent_execution_id=parent_execution_id or execution.execution_id,
                        )
                        phase.result = nested_result
                    else:
                        logger.warning(f"  ⚠️  Nested playbook not found: {nested_playbook_id}")
                        return False

                else:
                    # GENERIC HANDLER DISPATCH (GAD-6000: QUERY_GRAPH, RENDER_TEMPLATE, etc.)
                    # Delegate to Action Handler Registry for all other action types
                    if self.action_registry and self.action_registry.has(action_type):
                        handler = self.action_registry.get(action_type)
                        action_context = ActionContext(
                            phase_id=phase.phase_id,
                            playbook_id=playbook.id,
                            execution_id=execution.execution_id,
                            user_input=execution.user_input,
                            phase_results=execution.phase_results,
                            kernel=kernel,
                            emit_event=emit_event,
                        )
                        # Phoenix Config: Inject circuit templates for RENDER_TEMPLATE handler
                        if action_type == "RENDER_TEMPLATE" and playbook.templates:
                            params = {**params, "circuit_templates": playbook.templates}
                        result = await handler.execute(resolved_target, params, action_context)
                        if not result.success:
                            logger.warning(f"  ❌ {action_type} failed: {result.error}")
                            return False
                        phase.result = result.data
                        logger.info(f"  ✓ {action_type} completed: {resolved_target}")
                    else:
                        logger.warning(f"  ⚠️ Unknown action type (no handler): {action_type}")

            except Exception as e:
                logger.error(f"❌ Action failed: {action} - {e}")
                return False

        return True

    def _format_execution_result(self, execution: PlaybookExecution, playbook: PlaybookDefinition) -> Dict[str, Any]:
        """Format execution results for response"""
        return {
            "status": execution.status,
            "playbook_id": playbook.id,
            "playbook_name": playbook.name,
            "execution_id": execution.execution_id,
            "summary": f"{'✅ Playbook executed successfully' if execution.status == 'COMPLETED' else '❌ Playbook execution failed'}",
            "phases_executed": [
                {
                    "phase_id": p.phase_id,
                    "name": p.name,
                    "status": p.status.value,
                    "result": p.result,
                }
                for p in playbook.phases
                if p.status != PhaseStatus.PENDING
            ],
            "duration_seconds": (execution.completed_at or datetime.now().timestamp()) - execution.started_at,
            "details": execution.phase_results,
        }

    # ===== STATE PERSISTENCE (KARMA LEDGER) =====
    def _save_execution_state(self, execution: PlaybookExecution) -> None:
        """Persist execution state to disk for recovery"""
        state_file = self.state_dir / f"{execution.execution_id}.json"
        try:
            state_data = {
                "execution_id": execution.execution_id,
                "playbook_id": execution.playbook_id,
                "user_input": execution.user_input,
                "current_phase_id": execution.current_phase_id,
                "phase_results": execution.phase_results,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "error_message": execution.error_message,
            }
            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)
            logger.info(f"💾 Saved execution state: {execution.execution_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save execution state: {e}")

    def _load_persisted_executions(self) -> None:
        """Load previously persisted execution states"""
        try:
            for state_file in self.state_dir.glob("*.json"):
                with open(state_file, "r") as f:
                    data = json.load(f)
                    execution_id = data.get("execution_id")
                    if execution_id:
                        execution = PlaybookExecution(
                            execution_id=execution_id,
                            playbook_id=data.get("playbook_id", ""),
                            user_input=data.get("user_input", ""),
                            current_phase_id=data.get("current_phase_id"),
                            phase_results=data.get("phase_results", {}),
                            status=data.get("status", "RUNNING"),
                            started_at=data.get("started_at", datetime.now().timestamp()),
                            completed_at=data.get("completed_at"),
                            error_message=data.get("error_message"),
                        )
                        self.executions[execution_id] = execution
            if self.executions:
                logger.info(f"📂 Loaded {len(self.executions)} persisted execution states")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load persisted executions: {e}")

    # ===== LLM DYNAMIC ROUTING (HYBRID PATH) =====
    async def get_llm_decision(self, context: str, options: List[str]) -> Optional[str]:
        """
        Use LLM to make decision when path is ambiguous.
        Falls back to first option if LLM unavailable.
        """
        if not self.llm or len(options) == 1:
            return options[0] if options else None

        prompt = f"""Given the context: {context}

Choose the most appropriate option:
{chr(10).join([f"{i + 1}. {opt}" for i, opt in enumerate(options)])}

Reply with ONLY the number of your choice (1-{len(options)})."""

        try:
            response = self.llm.speak("PLAYBOOK_ENGINE", context, prompt)
            # Extract first digit from response
            for char in response:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(options):
                        logger.info(f"🧠 LLM Decision: {options[idx]}")
                        return options[idx]
        except Exception as e:
            logger.debug(f"LLM decision failed, using first option: {e}")

        return options[0] if options else None

    # ===== EVOLUTIONARY LOOP (EAD) =====
    def generate_playbook_proposal(self, user_input: str, concepts: Set[str]) -> Dict[str, Any]:
        """
        Generate a PROPOSAL for a new playbook when no matching playbook found.
        This is the safe self-improvement mechanism (EAD - Evolutionary Architecture Dimension).
        The proposal must be approved by a Human (HIL Check) before being added to the system.
        """
        proposal_id = f"PROPOSAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Infer playbook structure from user intent
        concepts_list = list(concepts)
        primary = concepts_list[0] if concepts_list else "CMD_UNKNOWN"
        secondary = concepts_list[1:] if len(concepts_list) > 1 else []

        proposal = {
            "proposal_id": proposal_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "detected_concepts": concepts_list,
            "playbook_draft": {
                "id": f"{primary}_V1",
                "name": f"Auto-generated for {primary}",
                "description": f"Playbook to handle: {user_input[:100]}",
                "intent_match": {"primary": primary, "secondary": secondary},
                "phases": [
                    {
                        "phase_id": "phase_1_validation",
                        "name": "Validation",
                        "description": "Validate input parameters",
                        "actions": [
                            {
                                "action_type": "CHECK_STATE",
                                "target": "input_validation",
                                "params": {},
                            }
                        ],
                        "on_success": "phase_2_execution",
                        "on_failure": "ABORT",
                        "timeout_seconds": 5,
                    },
                    {
                        "phase_id": "phase_2_execution",
                        "name": "Execution",
                        "description": "Execute the requested operation",
                        "actions": [
                            {
                                "action_type": "EMIT_EVENT",
                                "target": "execution_started",
                                "params": {"operation": "automatic"},
                            }
                        ],
                        "on_success": "COMPLETE",
                        "on_failure": "ABORT",
                        "timeout_seconds": 60,
                    },
                ],
            },
            "status": "PENDING_APPROVAL",
            "approval_required": True,
            "message": "⚠️  NEW PLAYBOOK PROPOSAL - Requires Human Approval (HIL Check) before activation",
        }

        logger.info(f"📝 Generated playbook proposal: {proposal_id}")
        logger.info("   Status: PENDING_APPROVAL (awaiting HIL human review)")

        return proposal

    # ===== FRACTAL/NESTED PLAYBOOKS =====
    async def execute_nested_playbook(
        self,
        playbook_id: str,
        user_input: str,
        intent_vector: Any,
        kernel: Any = None,
        emit_event=None,
        parent_execution_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a playbook that can be called from another playbook.
        Supports fractal/recursive playbook structures.
        """
        logger.info(f"🔗 Executing nested playbook: {playbook_id} (parent: {parent_execution_id})")
        result = await self.execute(
            playbook_id=playbook_id,
            user_input=user_input,
            intent_vector=intent_vector,
            kernel=kernel,
            emit_event=emit_event,
        )

        if emit_event and parent_execution_id:
            try:
                await emit_event(
                    "ACTION",
                    f"Nested playbook {playbook_id} completed",
                    "playbook_engine",
                    {
                        "nested_playbook_id": playbook_id,
                        "parent_id": parent_execution_id,
                    },
                )
            except Exception as e:
                logger.debug(f"Event emission failed: {e}")

        return result

    def find_nested_playbook(self, phase_action: Dict[str, Any]) -> Optional[str]:
        """
        Check if a phase action references a nested playbook.
        If action_type is 'CALL_PLAYBOOK', return the playbook ID.
        """
        if phase_action.get("action_type") == "CALL_PLAYBOOK":
            return phase_action.get("target")
        return None
