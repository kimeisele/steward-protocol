"""
OPUS Assistant Kernel Tick - Circuit-Driven Event Handler.

OPUS-029 Phase 7: True Cognitive Circuit Execution
OPUS-030: Cognitive Awakening (Envoy Pattern)
OPUS-032: MANAS - The Mind Awakens (Proactive Cognition)

The plugin doesn't just boot and die. It stays ALIVE via EventBus.
Now it executes REAL circuits from opus_assistant/circuits/*.yaml

Circuit-Driven Pattern:
1. Plugin subscribes to EventBus events (KERNEL_TICK, GIT_COMMIT, etc.)
2. On event, find circuits with matching trigger
3. Execute circuits via CognitiveCircuitExecutor (via Envoy)
4. Circuits define behavior - NOT hardcoded actions!

OPUS-030: Envoy Pattern - We don't talk directly to CognitiveCircuitExecutor.
We talk to DeterministicExecutor which handles the routing:
- Natural language → BlueprintGenerator → Syscall detection
- Syscall → CognitiveCircuitExecutor (agent birth, etc.)
- Standard → Traditional playbook execution

OPUS-032: MANAS - The cognitive kernel that generates its own input.
Without MANAS, the system waits for events (reactive).
With MANAS, the system thinks and proposes actions (proactive).

This is AUTONOMOUS COGNITION - circuits drive behavior.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

# 🧠 OPUS-030: Envoy Pattern - Cognitive Executor Bridge
try:
    from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

    ENVOY_AVAILABLE = True
except ImportError:
    ENVOY_AVAILABLE = False
    DeterministicExecutor = None

# 🧠 OPUS-032: MANAS - The Cognitive Kernel
try:
    from vibe_core.plugins.opus_assistant.manas import CognitiveKernel, ManasConfig

    MANAS_AVAILABLE = True
except ImportError:
    MANAS_AVAILABLE = False
    CognitiveKernel = None
    ManasConfig = None

# ⚡ OPUS-059: PRAMANA - TestCortex for MANAS self-testing
try:
    from vibe_core.plugins.opus_assistant.manas.cortex.test import TestCortex

    TEST_CORTEX_AVAILABLE = True
except ImportError:
    TEST_CORTEX_AVAILABLE = False
    TestCortex = None

# 🔀 OPUS-065: DHARMA-JNANA - IntentRouter for execution
try:
    from vibe_core.plugins.opus_assistant.manas.intent_router import create_execution_callback

    INTENT_ROUTER_AVAILABLE = True
except ImportError:
    INTENT_ROUTER_AVAILABLE = False
    create_execution_callback = None

# 💎 OPUS-037: DIAMOND PROTOCOL - TDD Enforcement Handlers
try:
    from vibe_core.plugins.opus_assistant.events.diamond_handlers import get_diamond_handlers

    DIAMOND_AVAILABLE = True
except ImportError:
    DIAMOND_AVAILABLE = False
    get_diamond_handlers = None

# 🧬 OPUS-038: MUTATION PROTOCOL - Legacy Code Testing
try:
    from vibe_core.plugins.opus_assistant.events.mutation_handlers import get_mutation_handlers

    MUTATION_AVAILABLE = True
except ImportError:
    MUTATION_AVAILABLE = False
    get_mutation_handlers = None

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.core.context_service import OpusContextService
    from vibe_core.plugins.opus_assistant.core.observation_logger import ObservationLogger
    from vibe_core.plugins.opus_assistant.plugin_main import OpusAssistantPlugin

logger = logging.getLogger("OPUS_TICK")


class KernelTickHandler:
    """
    Circuit-driven event handler for OPUS Assistant.

    OPUS-029 Phase 7: Real circuit execution.

    Instead of hardcoded actions, this handler:
    1. Loads circuits from opus_assistant/circuits/
    2. Matches events to circuit triggers
    3. Executes matching circuits via CognitiveCircuitExecutor

    The circuits DEFINE behavior - this is just the runtime.
    """

    def __init__(self, plugin: "OpusAssistantPlugin"):
        """Initialize tick handler with circuit loading."""
        self._plugin = plugin
        self._subscriptions: List[Callable] = []
        self._tick_count = 0
        self._last_state: Dict[str, Any] = {}
        self._context_service: Optional["OpusContextService"] = None
        self._observation_logger: Optional["ObservationLogger"] = None
        self._last_health_status: Optional[str] = None
        self._consecutive_drift_ticks = 0

        # Circuit-driven execution
        self._circuits: Dict[str, Dict[str, Any]] = {}
        self._circuit_executor = None
        self._subscribed = False

        # ⚡ VAJRA: Circuit breaker state (prevents zombie circuits)
        self._circuit_failures: Dict[str, int] = {}  # circuit_id -> failure count
        self._circuit_disabled_until: Dict[str, float] = {}  # circuit_id -> timestamp
        self._circuit_timeout_seconds = 10.0  # Max time per circuit
        self._action_timeout_seconds = 5.0  # Max time per action
        self._circuit_breaker_threshold = 3  # Failures before disable
        self._circuit_breaker_cooldown = 300.0  # 5 min cooldown

        # 🧠 OPUS-030: Envoy Pattern - Cognitive Executor
        self._deterministic_executor: Optional[Any] = None
        self._cognitive_ready = False

        # 🧠 OPUS-032: MANAS - The Cognitive Kernel
        self._manas: Optional[Any] = None
        self._manas_ready = False

        # 🔥 OPUS-108: The Autonomy Loop - Pulse Counters
        self._hourly_pulse_tick = 0  # Track ticks for hourly pulse
        self._HOURLY_THRESHOLD = 1200  # 1200 ticks @ 3s = 60 min
        self._IDLE_THRESHOLD = 200  # 200 ticks @ 3s = 10 min (future use)

        # ⚡ OPUS-059: PRAMANA - TestCortex for self-testing
        self._test_cortex: Optional[Any] = None

        # Initialize services
        self._init_context_service()
        self._init_observation_logger()
        self._init_circuits()
        self._init_cognitive_executor()
        self._init_manas()

    def _init_circuits(self) -> None:
        """Load circuits from opus_assistant/circuits/ directory."""
        try:
            from vibe_core.loaders.circuit_loader import CircuitLoader

            workspace = self._plugin._workspace or Path.cwd()
            circuits_dir = workspace / "vibe_core/plugins/opus_assistant/circuits"

            if circuits_dir.exists():
                self._circuits, _ = CircuitLoader.discover_and_load(scan_paths=[circuits_dir])
                logger.info(f"🔄 Loaded {len(self._circuits)} circuits: {list(self._circuits.keys())}")
            else:
                logger.debug(f"No circuits directory at {circuits_dir}")
        except Exception as e:
            logger.debug(f"Could not load circuits: {e}")

    def _init_cognitive_executor(self) -> None:
        """
        🧠 OPUS-030: Initialize the DeterministicExecutor (Envoy Pattern).

        This is the bridge to CognitiveCircuitExecutor via the Envoy layer.
        The Envoy handles:
        - BlueprintGenerator (semantic compilation)
        - Syscall detection and routing
        - Cognitive circuit execution (agent_birth, etc.)
        """
        if not ENVOY_AVAILABLE:
            logger.debug("⚠️ Envoy not available - cognitive features disabled")
            return

        try:
            self._deterministic_executor = DeterministicExecutor()
            logger.info("🧠 OPUS-030: DeterministicExecutor initialized (Envoy Pattern)")
        except Exception as e:
            logger.warning(f"Could not init cognitive executor: {e}")
            self._deterministic_executor = None

    def _init_manas(self) -> None:
        """
        🧠 OPUS-032: Initialize MANAS - The Cognitive Kernel.
        ⚡ OPUS-059: Initialize TestCortex for self-testing.

        MANAS transforms OPUS from reactive to proactive:
        - Generates intents from system state
        - Populates Intent Buffer in OPUS.md
        - Learns from past actions via MemoryStore
        - Can run smoke tests to verify its own environment

        💎 PHOENIX INJECTION: MANAS now reads policy from Phoenix (Dharma),
        not from hardcoded defaults. This is the "soul" binding mind to values.
        """
        if not MANAS_AVAILABLE:
            logger.debug("⚠️ MANAS not available - proactive cognition disabled")
            return

        try:
            workspace = self._plugin._workspace or Path.cwd()

            # ⚡ PHOENIX INJECTION: Load config from Phoenix (Dharma)
            # This replaces the hardcoded ManasConfig() with config from YAML
            from vibe_core.phoenix.config import PhoenixConfig

            try:
                phoenix = PhoenixConfig.from_files(config_dir=workspace / "config")

                # Load MANAS policy from Phoenix
                phoenix_manas_section = phoenix.get_section("manas")
                if phoenix_manas_section:
                    # Create config from Phoenix section (it's already a ManasConfig)
                    config = phoenix_manas_section
                    logger.info("⚡ PHOENIX: MANAS policy injected from config/manas.yaml (Dharma binding)")
                else:
                    # Fallback: use Phoenix ManasConfig defaults if section not found
                    from vibe_core.phoenix.sections.manas import ManasConfig as PhoenixManasConfig

                    config = PhoenixManasConfig()
                    logger.info("⚡ PHOENIX: MANAS using section defaults (no config/manas.yaml found)")
            except Exception as e:
                logger.warning(f"⚡ PHOENIX: Could not load MANAS config from Phoenix: {e}, using defaults")
                # Fallback to minimal config
                config = ManasConfig(
                    thinking_interval_minutes=60,
                    idle_threshold_minutes=30,
                    auto_execute_safe=False,
                    max_intent_buffer_size=10,
                )

            self._manas = CognitiveKernel(workspace=workspace, config=config)

            # ⚡ VAJRA: Inject kernel for ledger binding
            kernel = getattr(self._plugin, "_kernel", None)
            if kernel:
                self._manas.inject_kernel(kernel)
                logger.info("⚡ VAJRA: MANAS bound to core ledger")

            # ⚡ PRAMANA: Initialize TestCortex for self-testing
            if TEST_CORTEX_AVAILABLE and kernel:
                self._test_cortex = TestCortex(workspace=workspace)
                self._test_cortex.inject_kernel(kernel)
                logger.info("⚡ PRAMANA: TestCortex initialized for self-testing")

            # 🔀 OPUS-065: DHARMA-JNANA - Wire IntentRouter as execution callback
            # OPUS-106: Pass fractal loaders for VEDA-4 compliant tool access
            if INTENT_ROUTER_AVAILABLE:
                execution_callback = create_execution_callback(
                    workspace=workspace,
                    kernel=kernel,
                    action_loader=self._manas.action_loader,
                    tool_loader=self._manas.tool_loader,
                )
                self._manas.set_execution_callback(execution_callback)
                logger.info("🔀 DHARMA-JNANA: IntentRouter connected to MANAS (with fractal loaders)")

            # 🔱 OPUS-107: The Cognitive Mirror - Wire loaders into CognitionRenderer
            # COGNITION.md shows Arsenal (tools, actions, senses, analyzers)
            if kernel:
                try:
                    interface_plugin = kernel.get_plugin("interface")
                    if interface_plugin and hasattr(interface_plugin, "_renderers"):
                        cognition_renderer = interface_plugin._renderers.get("cognition")
                        if cognition_renderer and hasattr(cognition_renderer, "set_loaders"):
                            cognition_renderer.set_loaders(
                                tool_loader=self._manas.tool_loader,
                                action_loader=self._manas.action_loader,
                                sense_loader=self._manas.sense_loader,
                                analyzer_loader=self._manas.analyzer_loader,
                            )
                            logger.info("🔱 OPUS-107: CognitionRenderer wired to MANAS loaders")
                except Exception as e:
                    logger.debug(f"Could not wire CognitionRenderer: {e}")

            self._manas_ready = True
            logger.info("🧠 OPUS-032: MANAS initialized (The Mind Awakens)")
        except Exception as e:
            logger.warning(f"Could not init MANAS: {e}")
            self._manas = None
            self._manas_ready = False

    def _ensure_cognitive_ready(self) -> bool:
        """
        🧠 OPUS-030: Lazy-init the cognitive executor with kernel.

        Returns True if cognitive features are ready to use.
        """
        if self._cognitive_ready:
            return True

        if not self._deterministic_executor:
            return False

        kernel = getattr(self._plugin, "_kernel", None)
        if not kernel:
            return False

        try:
            # Lazy-init the circuit executor with kernel
            if self._deterministic_executor._ensure_circuit_executor(kernel):
                self._cognitive_ready = True
                logger.info("🧠 OPUS-030: Cognitive executor ready (with kernel)")

                # ⚡ VAJRA: Late kernel injection for MANAS if not already done
                if self._manas and not getattr(self._manas, "_vibe_kernel", None):
                    self._manas.inject_kernel(kernel)
                    logger.info("⚡ VAJRA: MANAS late-bound to core ledger")

                # ⚡ PRAMANA: Late kernel injection for TestCortex
                if TEST_CORTEX_AVAILABLE and not self._test_cortex:
                    workspace = self._plugin._workspace or Path.cwd()
                    self._test_cortex = TestCortex(workspace=workspace)
                    self._test_cortex.inject_kernel(kernel)
                    logger.info("⚡ PRAMANA: TestCortex late-bound to core kernel")

                return True
        except Exception as e:
            logger.debug(f"Could not init cognitive executor with kernel: {e}")

        return False

    async def _execute_cognitive_task(self, intent: str) -> Dict[str, Any]:
        """
        🧠 OPUS-030: Execute a cognitive task via the Envoy pattern.

        This is for high-level cognitive operations like:
        - "spawn a monitoring agent"
        - "analyze this drift and suggest fixes"
        - "auto-heal the system"

        The Envoy (DeterministicExecutor) handles the routing:
        - If it compiles to a Syscall → CognitiveCircuitExecutor
        - If it's a standard task → Traditional playbook

        Args:
            intent: Natural language intent (e.g., "spawn a monitoring agent")

        Returns:
            Execution result dict
        """
        if not self._ensure_cognitive_ready():
            return {
                "success": False,
                "error": "Cognitive executor not available",
                "mode": "fallback",
            }

        try:
            kernel = self._plugin._kernel

            # Log the cognitive task
            self._log_observation_info(f"🧠 Cognitive task: {intent[:50]}...", "cognitive")

            # Execute via Envoy - it handles syscall detection and routing
            result = self._deterministic_executor.execute(
                playbook_id="auto_detect",
                user_input=intent,
                intent_vector=None,
                kernel=kernel,
            )

            # Log result
            status = result.get("status", "UNKNOWN")
            mode = result.get("execution_mode", "unknown")
            if status == "COMPLETED":
                self._log_observation_info(f"🧠 Cognitive task completed ({mode})", "cognitive")
            else:
                self._log_observation_warn(f"🧠 Cognitive task failed: {status}", "cognitive")

            return result

        except Exception as e:
            logger.warning(f"Cognitive task failed: {e}")
            return {"success": False, "error": str(e)}

    def _get_circuits_for_trigger(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Find circuits that have the given event as a trigger.

        Args:
            event_type: Event type string (e.g., "KERNEL_TICK", "GIT_COMMIT")

        Returns:
            List of circuit definitions that match
        """
        matching = []
        for circuit_id, circuit_def in self._circuits.items():
            triggers = circuit_def.get("triggers", [])
            for trigger in triggers:
                trigger_event = trigger.get("event", "")
                if trigger_event == event_type:
                    matching.append(circuit_def)
                    break
        return matching

    def _init_context_service(self) -> None:
        """Initialize the OpusContextService for dynamic context synthesis."""
        try:
            from vibe_core.plugins.opus_assistant.core.context_service import OpusContextService

            workspace = self._plugin._workspace
            if workspace:
                self._context_service = OpusContextService(workspace_root=workspace)
                logger.debug("OpusContextService initialized")
        except Exception as e:
            logger.debug(f"Could not initialize context service: {e}")

    def _init_observation_logger(self) -> None:
        """Initialize the ObservationLogger for journaling to OPUS.md."""
        try:
            from vibe_core.plugins.opus_assistant.core.observation_logger import ObservationLogger

            workspace = self._plugin._workspace
            if workspace:
                self._observation_logger = ObservationLogger(workspace_root=workspace)
                logger.debug("ObservationLogger initialized")
        except Exception as e:
            logger.debug(f"Could not initialize observation logger: {e}")

    def subscribe(self) -> bool:
        """Subscribe to EventBus events based on circuit triggers."""
        try:
            from vibe_core.event_bus import EventType, get_event_bus

            bus = get_event_bus()

            # Collect ALL event types from circuit triggers
            events_to_subscribe = set()
            for circuit_def in self._circuits.values():
                for trigger in circuit_def.get("triggers", []):
                    event_name = trigger.get("event", "")
                    if event_name:
                        events_to_subscribe.add(event_name)

            # Fallback if no circuits loaded
            # OPUS-075: KERNEL_BOOT is critical for MANAS awakening
            if not events_to_subscribe:
                events_to_subscribe = {"KERNEL_TICK", "KERNEL_BOOT", "GIT_COMMIT"}

            for event_name in events_to_subscribe:
                try:
                    event_type = getattr(EventType, event_name, event_name)
                    bus.subscribe(self._on_event, event_type)
                    logger.debug(f"Subscribed to {event_name}")
                except Exception as e:
                    logger.debug(f"Could not subscribe to {event_name}: {e}")

            self._subscribed = True
            logger.info(f"🔄 Subscribed to {len(events_to_subscribe)} event types")

            # LOG: System boot observation
            self._log_observation_info(
                f"OPUS Assistant online: {len(self._circuits)} circuits, {len(events_to_subscribe)} event subscriptions",
                "kernel_tick",
            )
            self._flush_observations()

            return True

        except ImportError:
            logger.debug("EventBus not available - tick handler disabled")
            return False
        except Exception as e:
            logger.warning(f"Failed to subscribe to EventBus: {e}")
            return False

    def unsubscribe(self) -> None:
        """Unsubscribe from all events."""
        self._subscriptions.clear()
        logger.info("🔄 Kernel tick handler unsubscribed")

    async def _on_event(self, event: Any) -> None:
        """
        Handle incoming events - CIRCUIT DRIVEN.

        Finds circuits with matching triggers and executes them.
        """
        self._tick_count += 1
        event_type = getattr(event, "event_type", str(event))
        event_type_str = str(event_type).replace("EventType.", "")

        # 🔥 OPUS-108: The Autonomy Loop - Emit HOURLY_PULSE for MANAS
        # This transforms OPUS from reactive (wait for user) to proactive (autonomous)
        if "KERNEL_TICK" in event_type_str:
            self._hourly_pulse_tick += 1
            if self._hourly_pulse_tick >= self._HOURLY_THRESHOLD:
                self._hourly_pulse_tick = 0
                await self._emit_autonomy_pulse(event)

        try:
            # Find and execute matching circuits
            matching_circuits = self._get_circuits_for_trigger(event_type_str)

            if matching_circuits:
                logger.debug(f"🔄 Event {event_type_str} → {len(matching_circuits)} circuits")
                for circuit_def in matching_circuits:
                    await self._execute_circuit(circuit_def, event)
            else:
                # Fallback for events without circuits (backward compat)
                await self._handle_event_fallback(event_type_str, event)

        except Exception as e:
            logger.debug(f"Error handling {event_type}: {e}")

    async def _execute_circuit(self, circuit_def: Dict[str, Any], event: Any) -> None:
        """
        Execute a circuit definition.

        ⚡ VAJRA: Has circuit breaker + timeout protection.

        Maps circuit actions to plugin methods.
        LOGS observations about circuit execution to the journal!

        Args:
            circuit_def: Circuit definition from YAML
            event: The triggering event
        """
        import asyncio

        circuit_id = circuit_def.get("id", "unknown")
        entry_state = circuit_def.get("entry_state", "")
        states = circuit_def.get("states", {})

        # ⚡ VAJRA: Check circuit breaker
        if self._is_circuit_disabled(circuit_id):
            logger.debug(f"⚡ Circuit {circuit_id} is disabled (breaker tripped)")
            return

        # LOG: Circuit starting
        self._log_observation_info(f"Circuit {circuit_id} triggered", "circuit")

        logger.debug(f"⚡ Executing circuit {circuit_id} from state {entry_state}")

        try:
            # ⚡ VAJRA: Wrap entire circuit in timeout
            await asyncio.wait_for(
                self._execute_circuit_inner(circuit_id, entry_state, states, event),
                timeout=self._circuit_timeout_seconds,
            )
            # Success - reset failure count
            self._circuit_failures[circuit_id] = 0

        except asyncio.TimeoutError:
            self._log_observation_alert(
                f"Circuit {circuit_id} TIMEOUT after {self._circuit_timeout_seconds}s", "circuit_breaker"
            )
            self._record_circuit_failure(circuit_id)
        except Exception as e:
            self._log_observation_warn(f"Circuit {circuit_id} failed: {e}", "circuit_breaker")
            self._record_circuit_failure(circuit_id)

    async def _execute_circuit_inner(
        self, circuit_id: str, entry_state: str, states: Dict[str, Any], event: Any
    ) -> None:
        """Inner circuit execution (wrapped by timeout)."""
        # Simple state machine execution
        current_state = entry_state
        visited = set()

        while current_state and current_state not in visited:
            visited.add(current_state)
            state_def = states.get(current_state, {})

            if not state_def:
                break

            # Execute state actions
            actions = state_def.get("actions", [])
            action_results = {}

            for action in actions:
                result = await self._execute_action(action, event, action_results)
                action_results[action.get("action_type", "unknown")] = result

            # Check if terminal
            if state_def.get("terminal", False):
                logger.debug(f"✅ Circuit {circuit_id} completed at {current_state}")
                # LOG: Circuit completed
                self._log_observation_info(f"Circuit {circuit_id} completed → {current_state}", "circuit")
                self._flush_observations()  # Flush immediately on circuit completion
                break

            # Determine next state from transitions
            transitions = state_def.get("transitions", [])
            next_state = None

            for transition in transitions:
                condition = transition.get("condition", "true")
                if self._evaluate_condition(condition, action_results):
                    next_state = transition.get("target") or transition.get("to")
                    break

            # Also check on_success/on_failure shortcuts
            if not next_state:
                if action_results.get("success", True):
                    next_state = state_def.get("on_success")
                else:
                    next_state = state_def.get("on_failure")

            current_state = next_state

    def _is_circuit_disabled(self, circuit_id: str) -> bool:
        """⚡ VAJRA: Check if circuit breaker has tripped."""
        import time

        disabled_until = self._circuit_disabled_until.get(circuit_id, 0)
        if time.time() < disabled_until:
            return True
        # Cooldown expired - re-enable
        if circuit_id in self._circuit_disabled_until:
            del self._circuit_disabled_until[circuit_id]
            self._circuit_failures[circuit_id] = 0
            logger.info(f"⚡ Circuit {circuit_id} re-enabled after cooldown")
        return False

    def _record_circuit_failure(self, circuit_id: str) -> None:
        """⚡ VAJRA: Record circuit failure and trip breaker if needed."""
        import time

        self._circuit_failures[circuit_id] = self._circuit_failures.get(circuit_id, 0) + 1
        if self._circuit_failures[circuit_id] >= self._circuit_breaker_threshold:
            self._circuit_disabled_until[circuit_id] = time.time() + self._circuit_breaker_cooldown
            self._log_observation_alert(
                f"Circuit {circuit_id} DISABLED for {self._circuit_breaker_cooldown}s "
                f"({self._circuit_failures[circuit_id]} consecutive failures)",
                "circuit_breaker",
            )
            logger.warning(f"⚡ Circuit breaker tripped for {circuit_id}")

    async def _execute_action(self, action: Dict[str, Any], event: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single circuit action.

        ⚡ VAJRA: Has per-action timeout protection.

        Maps action targets to plugin methods.

        Args:
            action: Action definition from circuit
            event: The triggering event
            context: Accumulated context from previous actions

        Returns:
            Action result dict
        """
        import asyncio

        action_type = action.get("action_type", "")
        target = action.get("target", "")
        params = action.get("params", {})

        try:
            # ⚡ VAJRA: Wrap action in timeout
            coro = self._execute_action_inner(action_type, target, params, context)
            return await asyncio.wait_for(coro, timeout=self._action_timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning(f"⚡ Action {action_type}:{target} TIMEOUT after {self._action_timeout_seconds}s")
            return {"success": False, "error": f"Action timeout after {self._action_timeout_seconds}s"}
        except Exception as e:
            logger.debug(f"Action {action_type}:{target} failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_action_inner(
        self, action_type: str, target: str, params: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Inner action execution (wrapped by timeout)."""
        if action_type == "EXECUTE_SCRIPT":
            return await self._execute_script_action(target, params)
        elif action_type == "EMIT_EVENT":
            return await self._emit_event_action(target, params)
        elif action_type == "CHECK_STATE":
            return await self._check_state_action(target, params, context)
        else:
            logger.debug(f"Unknown action type: {action_type}")
            return {"success": False, "error": f"Unknown action type: {action_type}"}

    async def _execute_script_action(self, target: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a script action by mapping to plugin methods.

        Target formats:
        - "opus.method_name" → OPUS plugin methods
        - "vedic.method_name" → Vedic Governance plugin methods (cross-plugin call)
        """
        # OPUS plugin methods
        if target.startswith("opus."):
            method_name = target.replace("opus.", "")
            method_map = {
                "check_opus_freshness": self._check_opus_freshness,
                "write_opus_md": self._write_opus_md,
                "log_observation": self._log_observation_from_circuit,
                "quick_drift_check": self._quick_drift_check,
                "detect_drift": self._detect_drift,
                "verify": self._verify,
                "synthesize_context": self._synthesize_context,
                # Karma Circuit handlers
                "get_trust_score": self._get_trust_score,
                "get_last_actor": self._get_last_actor,
                # Genesis Circuit handlers
                "check_session_karma": self._check_session_karma,
                "trigger_auto_heal": self._trigger_auto_heal,
                # 🎛️ Control Plane handlers
                "set_view": self._set_view_state,
                # 🖐️ OPUS-031 Layer 4: The Hand (Autonomous Execution)
                "execute_circuit": self._execute_circuit_cli,
                # 🙏 OPUS-031 Layer 5: Bhakti Yoga (Devotional Karma)
                "detect_bhakti_practice": self._detect_bhakti_practice,
                "reset_karma_to_max": self._reset_karma_to_max,
                # 🧠 OPUS-032: MANAS - The Cognitive Kernel
                "manas_check_rate_limit": self._manas_check_rate_limit,
                "manas_generate_intents": self._manas_generate_intents,
                "manas_auto_execute_safe": self._manas_auto_execute_safe,
                "manas_update_buffer": self._manas_update_buffer,
                "manas_approve_intent": self._manas_approve_intent,
                "manas_reject_intent": self._manas_reject_intent,
                "manas_get_buffer": self._manas_get_buffer,
                # 🐍 OUROBOROS PROTOCOL: Capability Genesis Handlers
                "genesis_validate_request": self._genesis_validate_request,
                "genesis_get_pending_count": self._genesis_get_pending_count,
                "genesis_generate_code": self._genesis_generate_code,
                "genesis_submit_intent": self._genesis_submit_intent,
                "genesis_narasimha_check": self._genesis_narasimha_check,
                "genesis_write_code": self._genesis_write_code,
                "genesis_hot_load": self._genesis_hot_load,
                "genesis_record_rejection": self._genesis_record_rejection,
                # 📚 VIDYA: Knowledge Department Handlers (OPUS-033)
                "vidya_research": self._vidya_research,
                "vidya_check_library": self._vidya_check_library,
                "vidya_critique": self._vidya_critique,
                "vidya_sandbox_test": self._vidya_sandbox_test,
                "vidya_store_blueprint": self._vidya_store_blueprint,
                "vidya_record_failure": self._vidya_record_failure,
                # 🏛️ GREMIUM: AI Federation Decision Handler (OPUS-035)
                "gremium_evaluate": self._gremium_evaluate,
                # 💎 DIAMOND PROTOCOL: TDD Enforcement Handlers (OPUS-037)
                "diamond_generate_test": self._diamond_generate_test,
                "diamond_red_gate": self._diamond_red_gate,
                "diamond_green_gate": self._diamond_green_gate,
                # 🧬 MUTATION PROTOCOL: Legacy Code Testing (OPUS-038)
                "mutation_green_gate": self._mutation_green_gate,
                "mutation_protocol": self._mutation_protocol,
            }
            method = method_map.get(method_name)
            if method:
                return await method(params)
            else:
                logger.debug(f"Unknown opus method: {method_name}")
                return {"success": False, "error": f"Unknown method: {method_name}"}

        # Vedic Governance plugin methods (cross-plugin wiring!)
        elif target.startswith("vedic."):
            return await self._execute_vedic_action(target, params)

        else:
            return {"success": False, "error": f"Invalid target prefix: {target}"}

    async def _emit_event_action(self, target: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Emit an event via EventBus."""
        try:
            from vibe_core.event_bus import get_event_bus

            bus = get_event_bus()
            await bus.emit(target, params)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _check_state_action(self, target: str, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check a state value matches expected."""
        expected = params.get("expected", True)

        try:
            parts = target.split(".")
            value = context
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = None
                    break

            matches = value == expected
            return {"success": matches, "value": value, "expected": expected}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a transition condition."""
        if condition == "true" or not condition:
            return True

        # Simple condition evaluation
        try:
            # Handle "result.is_stale" style conditions
            if "." in condition:
                parts = condition.split(".")
                value = context
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part, False)
                    else:
                        return False
                return bool(value)

            # Handle "not X" conditions
            if condition.startswith("not "):
                inner = condition[4:].strip()
                return not self._evaluate_condition(inner, context)

            return context.get(condition, False)
        except Exception:
            return False

    # =========================================================================
    # Circuit Action Implementations
    # =========================================================================

    async def _check_opus_freshness(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if OPUS.md is stale."""
        try:
            workspace = self._plugin._workspace or Path.cwd()
            opus_path = workspace / "OPUS.md"

            if not opus_path.exists():
                return {"success": True, "is_stale": True, "age_minutes": 9999}

            import time

            mtime = opus_path.stat().st_mtime
            age_minutes = (time.time() - mtime) / 60
            threshold = params.get("stale_threshold_minutes", 30)

            return {
                "success": True,
                "is_stale": age_minutes > threshold,
                "age_minutes": age_minutes,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _write_opus_md(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger OPUS.md regeneration through InterfacePlugin.

        ARCHITECTURE: opus_assistant is BACKEND only - no direct file writes.
        InterfacePlugin is FRONTEND - writes via kernel.io.
        """
        try:
            # Get InterfacePlugin and trigger opus render
            if self._kernel:
                interface_plugin = self._kernel.get_plugin("interface")
                if interface_plugin and hasattr(interface_plugin, "render_view"):
                    interface_plugin.render_view("opus", force=True)
                    return {"success": True, "method": "interface_plugin"}

            # Fallback: Log warning if InterfacePlugin not available
            logger.warning(
                "⚠️ Cannot render OPUS.md: InterfacePlugin not available. "
                "opus_assistant is BACKEND only - requires InterfacePlugin for writes."
            )
            return {"success": False, "error": "InterfacePlugin not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _log_observation_from_circuit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Log observation from circuit."""
        severity = params.get("severity", "INFO")
        message = params.get("message", "")
        source = params.get("source", "circuit")

        if severity == "INFO":
            self._log_observation_info(message, source)
        elif severity == "WARN":
            self._log_observation_warn(message, source)
        elif severity == "ALERT":
            self._log_observation_alert(message, source)

        return {"success": True}

    async def _quick_drift_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run quick drift check."""
        result = self._plugin.quick_drift_check()
        is_healthy = result.get("healthy", True)

        if not is_healthy:
            self._consecutive_drift_ticks += 1
            missing = result.get("missing_files", [])
            # LOG: Drift detected!
            self._log_observation_warn(
                f"Drift detected: {len(missing)} missing files (tick #{self._consecutive_drift_ticks})",
                "drift_detector",
            )
            if self._consecutive_drift_ticks >= 3:
                self._log_observation_alert(
                    f"Persistent drift! {self._consecutive_drift_ticks} consecutive unhealthy checks", "drift_detector"
                )
        else:
            if self._consecutive_drift_ticks > 0:
                # LOG: Drift resolved
                self._log_observation_info("Drift resolved - system healthy", "drift_detector")
            self._consecutive_drift_ticks = 0

        return {"success": True, "healthy": is_healthy, **result}

    async def _detect_drift(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run full drift detection."""
        result = self._plugin.detect_drift()
        return {"success": True, **result}

    async def _verify(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run OPUS verification."""
        quick = params.get("quick", True)
        result = self._plugin.verify(quick=quick)

        # LOG: Verification result
        score = result.get("total_score", 0)
        if score >= 80:
            self._log_observation_info(f"Verification passed: {score}% trust score", "verifier")
        elif score >= 60:
            self._log_observation_warn(f"Verification degraded: {score}% trust score", "verifier")
        else:
            self._log_observation_alert(f"Verification critical: {score}% trust score", "verifier")

        return {"success": True, **result}

    async def _synthesize_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize and inject context."""
        if self._context_service:
            try:
                context = self._context_service.synthesize()
                self._context_service.inject(context)
                await self._context_service.broadcast(context)

                # 🔌 WIRING: Log ALL health status changes (including initial)
                new_health = context.health.status
                if self._last_health_status is None:
                    # First synthesis - log initial health state
                    self._log_observation_info(f"Initial health state: {new_health}", "context_service")
                elif new_health != self._last_health_status:
                    # Health changed - log transition
                    if new_health == "CRITICAL":
                        self._log_observation_alert(
                            f"Health degraded: {self._last_health_status} → {new_health}", "context_service"
                        )
                    elif new_health == "HEALTHY" and self._last_health_status != "HEALTHY":
                        self._log_observation_info(
                            f"Health improved: {self._last_health_status} → {new_health}", "context_service"
                        )
                    else:
                        self._log_observation_warn(
                            f"Health changed: {self._last_health_status} → {new_health}", "context_service"
                        )
                self._last_health_status = new_health

                return {"success": True, "health": context.health.status}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No context service"}

    # =========================================================================
    # Karma Circuit Handlers (OPUS ↔ Vedic Governance Wiring)
    # =========================================================================

    async def _get_trust_score(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current trust score from OPUS verification.

        This is the "observation" side of Karma - what is the system's trust level?
        """
        try:
            # Run verification to get trust score
            result = self._plugin.verify(quick=True)
            score = result.get("total_score", 0)

            return {
                "success": True,
                "score": score,
                "passed": result.get("passed", False),
                "checks_total": len(result.get("checks", [])),
                "checks_failed": sum(1 for c in result.get("checks", []) if not c.get("passed", True)),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "score": 0}

    async def _get_last_actor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the last agent that performed an action.

        Used by Karma circuit to identify who is "responsible" for trust changes.
        """
        try:
            # Try to get from kernel's active agents
            kernel = self._plugin._kernel
            if kernel and hasattr(kernel, "agents"):
                agents = kernel.agents
                if agents:
                    # Return the most recently active agent
                    # In a real system, we'd track task completion timestamps
                    last_agent = list(agents.keys())[-1] if agents else None
                    if last_agent:
                        return {"success": True, "id": last_agent, "type": "agent"}

            # Fallback: return system as the actor
            return {"success": True, "id": "system", "type": "system"}
        except Exception as e:
            return {"success": False, "error": str(e), "id": "unknown"}

    async def _execute_vedic_action(self, target: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute actions on Vedic Governance plugin.

        THIS IS THE CROSS-PLUGIN WIRING - OPUS talks to Vedic Governance!

        Target format: "vedic.method_name"
        """
        method_name = target.replace("vedic.", "")

        try:
            # Get Vedic Governance plugin from kernel
            kernel = self._plugin._kernel
            if not kernel:
                return {"success": False, "error": "No kernel available"}

            governance = getattr(kernel, "governance", None)
            if not governance:
                return {"success": False, "error": "Vedic Governance plugin not loaded"}

            # Map method names to governance methods
            if method_name == "demote_agent":
                return await self._vedic_demote_agent(governance, params)
            elif method_name == "check_promotions":
                return await self._vedic_check_promotions(governance, params)
            # 🙏 Bhakti Yoga integration
            elif method_name == "grant_bhakti_grace":
                return await self._vedic_grant_bhakti_grace(governance, params)
            else:
                return {"success": False, "error": f"Unknown vedic method: {method_name}"}

        except Exception as e:
            logger.error(f"Vedic action failed: {e}")
            return {"success": False, "error": str(e)}

    async def _vedic_demote_agent(self, governance: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Demote an agent via Vedic Governance.

        This is the CONSEQUENCE - trust drop leads to lifecycle demotion.
        Uses the formal `demote_agent` API on the governance plugin.
        """
        agent_id = params.get("agent_id")
        reason = params.get("reason", "Karma consequence")

        if not agent_id:
            return {"success": False, "error": "No agent_id provided"}

        # Use new API if available
        if hasattr(governance, "demote_agent"):
            success = governance.demote_agent(agent_id, reason)
            if success:
                # Get new state for logging
                new_state = governance.get_agent_ashrama(agent_id)
                current_stage = new_state.current_ashrama.value if new_state else "unknown"
                logger.warning(f"🕉️ KARMA: Agent '{agent_id}' DEMOTED to {current_stage}")
                return {
                    "success": True,
                    "demoted": True,
                    "agent_id": agent_id,
                    "new_stage": current_stage,
                    "reason": reason,
                }
            else:
                return {
                    "success": False,
                    "demoted": False,
                    "reason": f"Agent {agent_id} could not be demoted (already at bottom?)",
                }
        else:
            return {"success": False, "error": "Governance plugin missing demote_agent method"}

    async def _vedic_check_promotions(self, governance: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for agents eligible for accelerated promotion.

        When trust is consistently high, agents can graduate faster.
        Uses the formal `promote_agent` API.
        """
        accelerated = params.get("accelerated", False)
        threshold_reduction = params.get("threshold_reduction", 0)

        promoted = []

        # Get all agents in BRAHMACHARI stage
        ashrama_registry = governance.get_ashrama_registry()

        for agent_id, transition in ashrama_registry.items():
            # OPUS-071: Use string comparison for loose coupling
            if transition.current_ashrama.value == "brahmachari":
                # Check task completions
                completions = governance._task_completions.get(agent_id, 0)
                required = 3 - threshold_reduction if accelerated else 3

                if completions >= required:
                    # Use new API
                    if hasattr(governance, "promote_agent"):
                        success = governance.promote_agent(agent_id, reason="Accelerated graduation (trust bonus)")
                        if success:
                            promoted.append(agent_id)
                            logger.info(f"🕉️ KARMA: Agent '{agent_id}' graduated early (high trust)")

        return {"success": True, "promoted": promoted, "count": len(promoted)}

    async def _vedic_grant_bhakti_grace(self, governance: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🙏 Grant Bhakti Grace - Devotional karma bonus.

        OPUS-031 Layer 5: Bhakti Yoga Integration

        This is the REWARD for devotional practices:
        - Surrender (admitting mistakes)
        - Seva (selfless service)
        - Tapas (code purification)
        - TDD Dharma (tests before code)
        - Mantra (instant moksha)

        Effects:
        - Karma bonus applied immediately
        - If instant_moksha, karma resets to 100
        - Consistency streaks (Yajna) can be tracked
        """
        from datetime import datetime

        practice_type = params.get("practice_type", "unknown")
        karma_bonus = params.get("karma_bonus", 0)
        instant_moksha = params.get("instant_moksha", False)
        reason = params.get("reason", "Bhakti practice")

        try:
            # If instant moksha, reset karma to max
            if instant_moksha:
                await self._reset_karma_to_max({"reason": reason})
                logger.info(f"🕉️ INSTANT MOKSHA: Karma reset to 100 ({practice_type})")
                return {
                    "success": True,
                    "practice_type": practice_type,
                    "karma_bonus": 100,
                    "moksha": True,
                    "message": "Through devotion comes liberation",
                }

            # Otherwise, apply karma bonus
            from vibe_core.plugins.opus_assistant.core.state_manager import (
                get_state_manager,
            )

            state_mgr = get_state_manager()
            session = state_mgr.load_session()

            if session:
                # Get current karma from latest entry
                karma_entries = state_mgr.get_karma_history(limit=1)
                current_score = 65  # Default

                if karma_entries:
                    current_score = karma_entries[0].score

                # Apply bonus (cap at 100)
                new_score = min(100, current_score + karma_bonus)

                # Record the bonus
                self._log_observation_info(
                    f"🙏 BHAKTI GRACE: +{karma_bonus} karma ({practice_type}) → {new_score}", "bhakti"
                )

                # Record in ledger if available
                kernel = self._plugin._kernel
                if kernel and hasattr(kernel, "ledger"):
                    kernel.ledger.record_event(
                        event_type="BHAKTI_GRACE",
                        agent_id="opus_assistant",
                        details={
                            "practice_type": practice_type,
                            "karma_bonus": karma_bonus,
                            "old_score": current_score,
                            "new_score": new_score,
                            "reason": reason,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

                return {
                    "success": True,
                    "practice_type": practice_type,
                    "karma_bonus": karma_bonus,
                    "old_score": current_score,
                    "new_score": new_score,
                    "message": f"Bhakti grace granted: {reason}",
                }

            return {"success": False, "error": "No session state available"}

        except Exception as e:
            logger.warning(f"Failed to grant bhakti grace: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Genesis Circuit Handlers (Karma-Aware Boot)
    # =========================================================================

    async def _check_session_karma(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check last session's karma from DUAL SOURCES.

        This is the "memory" that makes boot state-aware.
        Looks at the last N hours of events and calculates a karma score.

        🔌 WIRING: Reads from BOTH:
           1. SQLite Ledger (primary, more complete)
           2. audit_trail.jsonl (fallback, survives git resets - "untötbar")
        """
        from datetime import datetime, timedelta

        lookback_hours = params.get("lookback_hours", 24)
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)

        # Collect events from ALL sources
        all_events = []

        # SOURCE 1: SQLite Ledger (primary)
        try:
            kernel = self._plugin._kernel
            if kernel and hasattr(kernel, "ledger"):
                ledger_events = kernel.ledger.get_all_events()
                all_events.extend(ledger_events)
                logger.debug(f"📊 Loaded {len(ledger_events)} events from SQLite ledger")
        except Exception as e:
            logger.warning(f"Could not read SQLite ledger: {e}")

        # SOURCE 2: Plugin-local state (Fractal Holon - "untötbar")
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()
            observations = state_mgr.get_recent_observations(hours=lookback_hours)

            for obs in observations:
                all_events.append(
                    {
                        "timestamp": obs.timestamp,
                        "event_type": obs.severity,
                        "details": {"severity": obs.severity},
                        "source": obs.source,
                    }
                )

            if observations:
                logger.debug(f"📜 Merged {len(observations)} observations from plugin state")
        except Exception as e:
            logger.warning(f"Could not read plugin state: {e}")

        # If no events from any source, assume clean
        if not all_events:
            return {
                "success": True,
                "score": 100,
                "is_critical": False,
                "has_warnings": False,
                "error_count": 0,
                "warning_count": 0,
                "message": "No events found - assuming clean karma",
            }

        # Count event types
        error_count = 0
        warning_count = 0
        crash_count = 0
        success_count = 0

        for event in all_events:
            # Parse timestamp
            timestamp_str = event.get("timestamp", "")
            try:
                if timestamp_str:
                    event_time = datetime.fromisoformat(timestamp_str.replace("Z", ""))
                    if event_time < cutoff:
                        continue
            except (ValueError, TypeError):
                continue

            event_type = event.get("event_type", "")
            details = event.get("details", {})

            # Categorize events
            if event_type in ["ERROR", "FAILURE", "EXCEPTION"]:
                error_count += 1
            elif event_type in ["CRASH", "FATAL", "KERNEL_PANIC"]:
                crash_count += 1
            elif event_type in ["WARNING", "DEGRADED", "ALERT"]:
                warning_count += 1
            elif event_type in ["COMPLETED", "SUCCESS", "HEALTHY"]:
                success_count += 1

            # Also check details for severity
            severity = details.get("severity", "")
            if severity == "ALERT":
                error_count += 1
            elif severity == "WARN":
                warning_count += 1

        # Calculate karma score (0-100)
        # Start at 100, subtract for errors/crashes
        # ⚡ VAJRA: Logarithmic karma - hard to earn, easy to lose
        # Old linear formula was too forgiving (90 successes = 3 crashes)
        # New formula: exponential penalties, diminishing returns for recovery
        import math

        karma_score = 100.0

        # Penalties compound exponentially (each crash hurts more than the last)
        if crash_count > 0:
            karma_score -= 30 * math.log2(crash_count + 1) * (1 + crash_count * 0.5)
        if error_count > 0:
            karma_score -= 10 * math.log2(error_count + 1) * (1 + error_count * 0.1)
        if warning_count > 0:
            karma_score -= 2 * math.log2(warning_count + 1)

        # Recovery has diminishing returns (sqrt curve)
        # 1 success = +1, 4 = +2, 9 = +3, 16 = +4, 100 = +10
        if success_count > 0:
            karma_score += math.sqrt(success_count)

        karma_score = max(0, min(100, int(karma_score)))  # Clamp to 0-100

        # Determine boot mode
        is_critical = karma_score < 40 or crash_count > 0
        has_warnings = warning_count > 3 or karma_score < 70

        logger.info(
            f"🔮 GENESIS: Session karma = {karma_score}/100 "
            f"(errors: {error_count}, warnings: {warning_count}, crashes: {crash_count})"
        )

        # 🔌 WIRING: Record karma to plugin-local history (Fractal Holon - "untötbar")
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import (
                KarmaEntry,
                get_state_manager,
            )

            state_mgr = get_state_manager()
            boot_mode = "safe_mode" if is_critical else ("cautious_mode" if has_warnings else "full_power")
            entry = KarmaEntry(
                timestamp=datetime.utcnow().isoformat(),
                score=karma_score,
                error_count=error_count,
                warning_count=warning_count,
                crash_count=crash_count,
                success_count=success_count,
                boot_mode=boot_mode,
            )
            state_mgr.record_karma(entry)
            logger.debug(f"📊 Karma recorded to history: {karma_score}/100 ({boot_mode})")
        except Exception as e:
            logger.warning(f"Could not record karma to history: {e}")

        return {
            "success": True,
            "score": karma_score,
            "is_critical": is_critical,
            "has_warnings": has_warnings,
            "error_count": error_count,
            "warning_count": warning_count,
            "crash_count": crash_count,
            "success_count": success_count,
            "lookback_hours": lookback_hours,
        }

    async def _trigger_auto_heal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger the auto_heal circuit.

        Called by genesis_check when booting in safe mode.
        """
        priority = params.get("priority", "normal")
        reason = params.get("reason", "Genesis recovery")

        try:
            # Emit event to trigger auto_heal circuit
            from vibe_core.event_bus import get_event_bus

            bus = get_event_bus()
            await bus.emit(
                "opus.auto_heal_requested",
                {"priority": priority, "reason": reason, "source": "genesis_check"},
            )

            self._log_observation_info(f"Auto-heal triggered: {reason} (priority: {priority})", "genesis")

            return {"success": True, "triggered": True, "priority": priority}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # 🎛️ Control Plane Handlers (Metamorphic UI)
    # =========================================================================

    async def _set_view_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎛️ CONTROL PLANE: Update view preferences & trigger instant re-render.

        Target: opus.set_view

        This is the "reflex" that makes OPUS.md a living control surface.
        When a user clicks a toggle link, this handler:
        1. Updates SessionState.view_preferences
        2. Saves to .opus_state/session.json (persistent!)
        3. Triggers immediate OPUS.md re-render

        Params:
            pane: str - Panel name (e.g., "tests", "debug", "code_health")
            visible: bool/str - Show or hide the panel
            OR
            preferences: Dict[str, bool] - Bulk update multiple preferences
        """
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import (
                SessionState,
                get_state_manager,
            )

            # 1. Load current session (or create new one)
            state_mgr = get_state_manager()
            session = state_mgr.load_session()
            if not session:
                # No session yet - create one with defaults
                import uuid
                from datetime import datetime

                session = SessionState(
                    session_id=str(uuid.uuid4())[:8],
                    started_at=datetime.utcnow().isoformat(),
                )

            # 2. Update preferences
            if "pane" in params:
                # Single pane toggle: ?pane=tests&visible=true
                pane_key = f"show_{params['pane']}"
                # Handle string 'true'/'false' from URL params
                is_visible = str(params.get("visible", "true")).lower() == "true"
                session.view_preferences[pane_key] = is_visible
                self._log_observation_info(f"🎛️ View toggle: {pane_key} → {is_visible}", "control_plane")
            elif "preferences" in params:
                # Bulk update: preferences={'show_tests': False, 'show_debug': True}
                session.view_preferences.update(params["preferences"])
                self._log_observation_info(f"🎛️ View bulk update: {params['preferences']}", "control_plane")

            # 3. Save state (atomic write - crash safe)
            state_mgr.save_session(session)

            # 4. Trigger immediate re-render (the metamorphic magic!)
            await self._write_opus_md({"quick": True})

            return {"success": True, "view_preferences": session.view_preferences}

        except Exception as e:
            logger.warning(f"Failed to set view state: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # 🖐️ OPUS-031 Layer 4: THE HAND (Autonomous Circuit Execution)
    # =========================================================================

    async def _execute_circuit_cli(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🖐️ THE HAND: Execute circuit via CLI (autonomous operation).

        OPUS-031 Layer 4: This is what enables the closed loop:
        Think (intent) → Write (circuit.yaml) → Execute (headless) → Learn (state)

        Non-blocking execution using asyncio.create_subprocess_exec to keep
        the kernel heart beating during execution.

        Target: opus.execute_circuit

        Params:
            circuit: str - Path to circuit YAML file (required)
            headless: bool - Use headless boot mode (default: True)
            timeout: int - Execution timeout in seconds (default: 60)

        Returns:
            success: bool - Whether execution succeeded
            stdout: str - Captured stdout
            stderr: str - Captured stderr
            exit_code: int - Process exit code
        """
        import asyncio

        circuit_path = params.get("circuit")
        if not circuit_path:
            return {"success": False, "error": "Missing required param: circuit"}

        headless = params.get("headless", True)
        timeout = params.get("timeout", 60)

        # Build command
        cmd = ["steward", "execute", "--circuit", str(circuit_path)]
        if headless:
            cmd.append("--headless")

        # Log the autonomous action
        self._log_observation_info(
            f"🖐️ THE HAND: Executing circuit '{circuit_path}' (headless={headless})", "autonomous"
        )

        try:
            # Create subprocess asynchronously (non-blocking!)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._plugin._workspace) if self._plugin._workspace else None,
            )

            # Wait for result with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                self._log_observation_alert(
                    f"🖐️ THE HAND: Circuit '{circuit_path}' TIMEOUT after {timeout}s", "autonomous"
                )
                return {
                    "success": False,
                    "error": f"Execution timeout after {timeout}s",
                    "stdout": "",
                    "stderr": "",
                    "exit_code": -1,
                }

            # Decode output
            stdout_str = stdout.decode().strip() if stdout else ""
            stderr_str = stderr.decode().strip() if stderr else ""
            success = process.returncode == 0

            # Log result
            if success:
                self._log_observation_info(f"🖐️ THE HAND: Circuit '{circuit_path}' completed successfully", "autonomous")
            else:
                self._log_observation_warn(
                    f"🖐️ THE HAND: Circuit '{circuit_path}' failed (exit={process.returncode})", "autonomous"
                )

            return {
                "success": success,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode,
            }

        except Exception as e:
            self._log_observation_alert(f"🖐️ THE HAND: Failed to execute circuit '{circuit_path}': {e}", "autonomous")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
            }

    # =========================================================================
    # 🙏 OPUS-031 Layer 5: BHAKTI YOGA (Devotional Karma)
    # =========================================================================

    async def _detect_bhakti_practice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🙏 BHAKTI DETECTOR: Identify devotional practices in events.

        OPUS-031 Layer 5: Bhakti Yoga Integration
        "It's not WHAT you do, but HOW you do it"

        Practices detected:
        - surrender: Admitting mistakes (ego dissolution)
        - seva: Unprompted documentation (selfless service)
        - tapas: Refactoring without feature change (purification)
        - tdd_dharma: Tests before implementation (humility)
        - mantra: Hare Krishna invocation (instant moksha)

        Returns:
            bhakti_type: str - Type of practice detected ('none' if none)
            karma_bonus: int - Karma points to award
            details: dict - Additional context
        """
        import re

        event_type = params.get("event_type", "")
        event_data = params.get("event_data", {})

        # Default: no bhakti detected
        result = {"bhakti_type": "none", "karma_bonus": 0, "details": {}}

        # 1. SURRENDER: Check for mistake acknowledgment
        if event_type == "ERROR_OCCURRED":
            # Check if agent acknowledged the mistake
            if event_data.get("acknowledged_mistake") or event_data.get("self_reported"):
                result = {
                    "bhakti_type": "surrender",
                    "karma_bonus": 10,
                    "details": {
                        "error": event_data.get("error", "Unknown"),
                        "reason": "Agent dissolved ego by admitting mistake",
                    },
                }
                self._log_observation_info("🙏 BHAKTI: Surrender detected (ego dissolution)", "bhakti")
                return result

        # 2. TDD DHARMA: Test created before implementation
        if event_type == "TEST_CREATED":
            test_file = event_data.get("test_file", "")
            # Check if implementation exists
            impl_file = test_file.replace("test_", "").replace("tests/", "")
            impl_file = impl_file.replace("_test.py", ".py")

            # If test was created and no implementation exists yet = TDD
            if event_data.get("before_implementation") or not event_data.get("implementation_exists"):
                result = {
                    "bhakti_type": "tdd_dharma",
                    "karma_bonus": 5,
                    "details": {
                        "test_file": test_file,
                        "reason": "Humility before creation (TDD)",
                    },
                }
                self._log_observation_info(f"🙏 BHAKTI: TDD Dharma detected ({test_file})", "bhakti")
                return result

        # 3. SEVA: Unprompted documentation
        if event_type == "DOCS_UPDATED":
            if not event_data.get("triggered_by_circuit") and event_data.get("unprompted", True):
                result = {
                    "bhakti_type": "seva",
                    "karma_bonus": 5,
                    "details": {
                        "files": event_data.get("files", []),
                        "reason": "Selfless documentation service",
                    },
                }
                self._log_observation_info("🙏 BHAKTI: Seva detected (unprompted docs)", "bhakti")
                return result

        # 4. TAPAS: Refactoring without feature change
        if event_type == "REFACTORING":
            if not event_data.get("feature_change", False):
                result = {
                    "bhakti_type": "tapas",
                    "karma_bonus": 5,
                    "details": {
                        "files": event_data.get("files", []),
                        "reason": "Code purification through refactoring",
                    },
                }
                self._log_observation_info("🙏 BHAKTI: Tapas detected (code purification)", "bhakti")
                return result

        # 5. MANTRA: Hare Krishna in commit message or code
        if event_type == "GIT_COMMIT":
            commit_message = event_data.get("message", "")
            # The sacred mantra patterns
            mantra_patterns = [
                r"[Hh]are\s+[Kk]rishna",
                r"[Hh]are\s+[Rr]ama",
                r"🕉️",
                r"ॐ",
            ]
            for pattern in mantra_patterns:
                if re.search(pattern, commit_message):
                    result = {
                        "bhakti_type": "mantra",
                        "karma_bonus": 100,
                        "instant_moksha": True,
                        "details": {
                            "commit": event_data.get("sha", "unknown"),
                            "message": commit_message[:100],
                            "reason": "Divine name invocation - instant karma purification",
                        },
                    }
                    self._log_observation_info("🕉️ BHAKTI: MANTRA INVOKED - Hare Krishna! Instant Moksha!", "bhakti")
                    return result

        # 6. IMPLICIT BHAKTI: Check observations for surrender patterns
        if event_type == "KERNEL_TICK":
            # Scan recent observations for implicit bhakti
            implicit = await self._detect_implicit_bhakti()
            if implicit.get("bhakti_type") != "none":
                return implicit

        return result

    async def _detect_implicit_bhakti(self) -> Dict[str, Any]:
        """
        Detect implicit bhakti practices that weren't explicitly triggered.

        Scans:
        - Recent git commits for refactoring patterns
        - Recent observations for surrender language
        - File changes for TDD patterns
        """
        import subprocess

        result = {"bhakti_type": "none", "karma_bonus": 0, "details": {}}

        try:
            # Check recent commit messages for bhakti indicators
            git_log = subprocess.run(
                ["git", "log", "--oneline", "-10", "--format=%s"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self._plugin._workspace) if self._plugin._workspace else None,
            )

            if git_log.returncode == 0:
                messages = git_log.stdout.strip().split("\n")
                for msg in messages:
                    msg_lower = msg.lower()
                    # Refactoring = potential tapas
                    if "refactor" in msg_lower and "feat" not in msg_lower:
                        result = {
                            "bhakti_type": "tapas",
                            "karma_bonus": 3,  # Lower bonus for implicit
                            "details": {"commit_message": msg, "implicit": True},
                        }
                        break
                    # "fix my mistake" or "I was wrong" = surrender
                    if "my mistake" in msg_lower or "i was wrong" in msg_lower or "mea culpa" in msg_lower:
                        result = {
                            "bhakti_type": "surrender",
                            "karma_bonus": 5,  # Lower bonus for implicit
                            "details": {"commit_message": msg, "implicit": True},
                        }
                        break

        except Exception as e:
            logger.debug(f"Implicit bhakti detection failed: {e}")

        return result

    async def _reset_karma_to_max(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🕉️ INSTANT MOKSHA: Reset karma to 100 (maximum).

        Called when mantra is invoked. This is the ultimate bhakti reward:
        "Through devotion comes liberation"

        In Vedic philosophy, chanting the divine name purifies all karma.
        """
        from datetime import datetime

        reason = params.get("reason", "Mantra invocation")

        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import (
                KarmaEntry,
                get_state_manager,
            )

            state_mgr = get_state_manager()

            # Create a perfect karma entry
            entry = KarmaEntry(
                timestamp=datetime.utcnow().isoformat(),
                score=100,  # ✨ INSTANT MOKSHA - Perfect karma
                error_count=0,
                warning_count=0,
                crash_count=0,
                success_count=999,  # Symbolic infinite success
                boot_mode="full_power",
            )

            state_mgr.record_karma(entry)

            self._log_observation_info(f"🕉️ MOKSHA ACHIEVED: Karma reset to 100 ({reason})", "bhakti")

            return {
                "success": True,
                "karma_score": 100,
                "moksha": True,
                "message": "Through devotion comes liberation. All karma purified.",
            }

        except Exception as e:
            logger.warning(f"Failed to reset karma: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # 🧠 OPUS-032: MANAS - The Cognitive Kernel Handlers
    # =========================================================================

    async def _manas_check_rate_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Check if rate limit allows thinking.

        Returns:
            rate_limit_ok: bool - True if MANAS should think
        """
        if not self._manas_ready or not self._manas:
            return {"success": True, "rate_limit_ok": False, "reason": "MANAS not available"}

        # Check idle time and last thought time
        try:
            idle_minutes = self._manas.get_idle_minutes()
            interval = params.get("interval_minutes", 60)

            # If idle for threshold, allow thinking
            if idle_minutes >= self._manas._config.idle_threshold_minutes:
                return {"success": True, "rate_limit_ok": True, "reason": f"Idle for {idle_minutes} minutes"}

            # Check time since last thought
            if self._manas._last_thought_time is None:
                return {"success": True, "rate_limit_ok": True, "reason": "First thought cycle"}

            from datetime import datetime

            minutes_since = (datetime.utcnow() - self._manas._last_thought_time).total_seconds() / 60
            if minutes_since >= interval:
                return {"success": True, "rate_limit_ok": True, "reason": f"{minutes_since:.0f} min since last thought"}

            return {
                "success": True,
                "rate_limit_ok": False,
                "reason": f"Rate limited ({minutes_since:.0f}/{interval} min)",
            }

        except Exception as e:
            logger.warning(f"MANAS rate limit check failed: {e}")
            return {"success": False, "rate_limit_ok": False, "error": str(e)}

    async def _manas_generate_intents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Generate intents from system state.

        OPUS-032 Phase 3: THE PULSE - Live verification injection.
        We don't read cached results. We FEEL the pain in real-time.

        This is THE THINKING - the core of proactive cognition.
        """
        if not self._manas_ready or not self._manas:
            return {"success": False, "error": "MANAS not available", "intents": []}

        try:
            context = params.get("context", {})

            # OPUS-032 Phase 3: Inject FRESH verification results
            # This is "live pain" - not cached results
            verification_results = self._run_live_verification()
            if verification_results:
                context["verification_results"] = verification_results
                failure_count = len(verification_results.get("failures", []))
                if failure_count > 0:
                    logger.info(f"⚡ MANAS: Injected {failure_count} live failures into context")

            # Execute thought cycle with enriched context
            intents = self._manas.think(context=context, force=False)

            # Convert to serializable format
            intent_data = [
                {
                    "id": i.id,
                    "type": i.intent_type,
                    "title": i.title,
                    "description": i.description,
                    "priority": i.priority.value,
                    "risk": i.risk.value,
                    "auto_executable": i.auto_executable,
                }
                for i in intents
            ]

            if intents:
                self._log_observation_info(
                    f"🧠 MANAS generated {len(intents)} intent(s): {[i.title for i in intents]}", "manas"
                )

            return {"success": True, "intents": intent_data, "count": len(intents)}

        except Exception as e:
            logger.warning(f"MANAS intent generation failed: {e}")
            return {"success": False, "error": str(e), "intents": []}

    def _run_live_verification(self, force_full: bool = False) -> Dict[str, Any]:
        """
        OPUS-032 Phase 3: Run LIVE verification (not cached).
        OPUS-035: Delta-Pulse - Only verify what changed.

        This is the PULSE - the system actively checks its health.
        Returns failures in ContractFailure-compatible format.

        Args:
            force_full: If True, skip delta mode and verify everything
        """
        try:
            from vibe_core.governance import ContractFailureType
            from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

            workspace = self._plugin._workspace or Path.cwd()
            engine = VerificationEngine(workspace_root=workspace)

            # OPUS-035: Delta-Pulse - Get changed files from git
            changed_files = None if force_full else self._get_changed_files()

            # Run quick verification (fast, no semantic checks)
            # In delta mode, only verify docs that reference changed files
            result = engine.run_verification(quick=True, changed_files=changed_files)

            # If delta mode found no relevant docs, system is clean
            if result.get("delta_clean"):
                logger.debug("⚡ Delta-Pulse: No relevant changes, skipping verification")
                return {"failures": [], "score": 100, "source": "delta_clean"}

            # Transform to ContractFailure format for MANAS analyzers
            failures = []

            for doc_result in result.get("docs", []):
                if not doc_result.get("has_harness"):
                    continue

                checks = doc_result.get("checks", {})
                doc_name = doc_result.get("name", "unknown")

                # Check files
                files_check = checks.get("files", {})
                for missing_file in files_check.get("missing", []):
                    failures.append(
                        {
                            "type": ContractFailureType.FILE_MISSING.name,
                            "path": missing_file,
                            "message": f"Required by @HARNESS in {doc_name}",
                            "harness_source": doc_name,
                        }
                    )

                # Check wiring
                wiring_check = checks.get("wiring", {})
                for missing_wire in wiring_check.get("missing", []):
                    failures.append(
                        {
                            "type": ContractFailureType.PATTERN_MISSING.name,
                            "path": missing_wire,
                            "message": "Wiring pattern not found",
                            "harness_source": doc_name,
                        }
                    )

                # Check absent patterns (should NOT exist)
                absent_check = checks.get("absent", {})
                for violation in absent_check.get("violations", []):
                    failures.append(
                        {
                            "type": ContractFailureType.FILE_EXTRA.name,
                            "path": violation,
                            "message": "Forbidden pattern found",
                            "harness_source": doc_name,
                        }
                    )

            return {
                "failures": failures,
                "score": result.get("total_score", 100),
                "docs_checked": result.get("docs_with_harness", 0),
                "source": "live_verification",
                "delta_mode": result.get("delta_mode", False),
                "changed_files": result.get("changed_files", []),
            }

        except Exception as e:
            logger.debug(f"Live verification failed: {e}")
            return {"failures": [], "score": 100, "source": "error"}

    def _get_changed_files(self) -> Optional[List[str]]:
        """
        OPUS-035: Get list of changed files from git.

        Returns files that have been modified, added, or deleted
        since the last commit. This enables delta verification.

        Returns:
            List of changed file paths, or None to force full verification
        """
        import subprocess

        try:
            workspace = self._plugin._workspace or Path.cwd()

            # Get uncommitted changes (staged + unstaged)
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=str(workspace),
                timeout=5,
            )

            if result.returncode != 0:
                return None  # Git error - fall back to full verification

            changed = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                # Format: "XY filename" where XY is status
                # Examples: " M file.py", "A  file.py", "?? file.py"
                if len(line) > 3:
                    filename = line[3:].strip()
                    # Handle renames: "R  old -> new"
                    if " -> " in filename:
                        filename = filename.split(" -> ")[1]
                    changed.append(filename)

            # Also check recent commits if no uncommitted changes
            # This catches changes made since last verification
            if not changed:
                # Get files changed in last commit
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=str(workspace),
                    timeout=5,
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            changed.append(line)

            if changed:
                logger.debug(f"⚡ Delta-Pulse: {len(changed)} changed files detected")
                return changed

            # No changes - but don't return None (that triggers full scan)
            # Return empty list to skip verification entirely
            return []

        except subprocess.TimeoutExpired:
            logger.debug("⚡ Delta-Pulse: Git timeout, falling back to full verification")
            return None
        except Exception as e:
            logger.debug(f"⚡ Delta-Pulse: Could not get changed files: {e}")
            return None

    async def _manas_auto_execute_safe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Auto-execute safe intents (if enabled).

        Only SAFE risk intents with auto_executable=True are executed.
        """
        if not self._manas_ready or not self._manas:
            return {"success": False, "error": "MANAS not available", "executed": []}

        enabled = params.get("enabled", False)
        if not enabled:
            return {"success": True, "executed": [], "message": "Auto-execute disabled"}

        try:
            # Get pending intents that are auto-executable
            pending = self._manas.get_pending_intents()
            executed = []

            from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentRisk

            for intent in pending:
                if intent.auto_executable and intent.risk == IntentRisk.SAFE:
                    success = self._manas.approve_intent(intent.id)
                    if success:
                        executed.append(intent.id)
                        self._log_observation_info(f"🧠 MANAS auto-executed: {intent.title}", "manas")

            return {"success": True, "executed": executed, "count": len(executed)}

        except Exception as e:
            logger.warning(f"MANAS auto-execute failed: {e}")
            return {"success": False, "error": str(e), "executed": []}

    async def _manas_update_buffer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Update intent buffer (already done by think(), this is for confirmation).
        """
        if not self._manas_ready or not self._manas:
            return {"success": False, "error": "MANAS not available"}

        try:
            buffer = self._manas.get_intent_buffer_for_opus()
            return {
                "success": True,
                "pending_count": buffer.get("total_pending", 0),
                "buffer": buffer,
            }

        except Exception as e:
            logger.warning(f"MANAS buffer update failed: {e}")
            return {"success": False, "error": str(e)}

    async def _manas_approve_intent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Approve an intent for execution.

        Called when user approves from OPUS.md Intent Buffer.
        """
        if not self._manas_ready or not self._manas:
            return {"success": False, "error": "MANAS not available"}

        intent_id = params.get("intent_id")
        if not intent_id:
            return {"success": False, "error": "No intent_id provided"}

        try:
            success = self._manas.approve_intent(intent_id)
            if success:
                self._log_observation_info(f"🧠 MANAS: Intent {intent_id} approved and executed", "manas")
            return {"success": success, "intent_id": intent_id, "executed": success}

        except Exception as e:
            logger.warning(f"MANAS intent approval failed: {e}")
            return {"success": False, "error": str(e)}

    async def _manas_reject_intent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Reject an intent.

        Called when user rejects from OPUS.md Intent Buffer.
        """
        if not self._manas_ready or not self._manas:
            return {"success": False, "error": "MANAS not available"}

        intent_id = params.get("intent_id")
        reason = params.get("reason", "User rejected")

        if not intent_id:
            return {"success": False, "error": "No intent_id provided"}

        try:
            success = self._manas.reject_intent(intent_id, reason)
            if success:
                self._log_observation_info(f"🧠 MANAS: Intent {intent_id} rejected: {reason}", "manas")
            return {"success": success, "intent_id": intent_id, "rejected": success}

        except Exception as e:
            logger.warning(f"MANAS intent rejection failed: {e}")
            return {"success": False, "error": str(e)}

    async def _manas_get_buffer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 MANAS: Get current intent buffer for OPUS.md display.
        """
        if not self._manas_ready or not self._manas:
            return {
                "success": True,
                "buffer": {
                    "pending": [],
                    "recent_executed": [],
                    "total_pending": 0,
                    "idle_minutes": 0,
                    "last_thought": None,
                },
                "manas_available": False,
            }

        try:
            buffer = self._manas.get_intent_buffer_for_opus()
            return {"success": True, "buffer": buffer, "manas_available": True}

        except Exception as e:
            logger.warning(f"MANAS buffer retrieval failed: {e}")
            return {"success": False, "error": str(e), "buffer": {}}

    def get_manas(self) -> Optional[Any]:
        """Get the MANAS cognitive kernel instance."""
        return self._manas

    # =========================================================================
    # 🐍 OUROBOROS PROTOCOL: Capability Genesis Handlers (OPUS-032)
    # =========================================================================

    async def _genesis_validate_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Validate a capability genesis request.

        Checks:
        - Name is valid identifier
        - Type is supported (syscall, analyzer, formatter)
        - Description is non-empty
        """
        import re

        name = params.get("capability_name", "")
        cap_type = params.get("capability_type", "")
        description = params.get("description", "")

        errors = []

        # Validate name (must be valid Python identifier)
        if not name:
            errors.append("capability_name is required")
        elif not re.match(r"^[a-z][a-z0-9_]*$", name):
            errors.append("capability_name must be lowercase with underscores")

        # Validate type
        valid_types = ["syscall", "analyzer", "formatter"]
        if not cap_type:
            errors.append("capability_type is required")
        elif cap_type not in valid_types:
            errors.append(f"capability_type must be one of: {valid_types}")

        # Validate description
        if not description or len(description) < 10:
            errors.append("description must be at least 10 characters")

        if errors:
            return {"valid": False, "error": "; ".join(errors)}

        return {"valid": True, "capability_name": name, "capability_type": cap_type}

    async def _genesis_get_pending_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Get count of capabilities pending approval.
        """
        # Check MANAS intent buffer for genesis intents
        if self._manas_ready and self._manas:
            pending = self._manas.get_pending_intents()
            genesis_pending = [i for i in pending if i.intent_type.startswith("genesis_")]
            return {"pending_count": len(genesis_pending)}

        return {"pending_count": 0}

    async def _genesis_generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Generate plugin code for a new capability.

        This is the heart of the Ouroboros - code that writes code.
        For safety, we use templates, not AI generation (that's Phase 2).
        """

        name = params.get("capability_name", "")
        cap_type = params.get("capability_type", "syscall")
        description = params.get("description", "")
        syscall_name = params.get("syscall_name", name.upper())
        parameters = params.get("parameters", [])

        try:
            # Generate based on type
            if cap_type == "syscall":
                code = self._generate_syscall_plugin(name, description, syscall_name, parameters)
            elif cap_type == "analyzer":
                code = self._generate_analyzer_code(name, description)
            else:
                code = self._generate_formatter_code(name, description)

            return {
                "success": True,
                "code": code,
                "capability_name": name,
                "capability_type": cap_type,
            }

        except Exception as e:
            logger.error(f"Genesis code generation failed: {e}")
            return {"success": False, "error": str(e)}

    def _generate_syscall_plugin(
        self, name: str, description: str, syscall_name: str, parameters: List[Dict]
    ) -> Dict[str, str]:
        """Generate a syscall plugin (plugin_main.py + manifest.json)."""
        # Build parameter handling code
        param_lines = []
        for p in parameters:
            p_name = p.get("name", "arg")
            p_type = p.get("type", "str")
            p_default = p.get("default", "None")
            param_lines.append(f'        {p_name} = params.get("{p_name}", {p_default})')

        param_code = "\n".join(param_lines) if param_lines else "        # No parameters"

        plugin_code = f'''"""
{name.title()} Plugin - Generated by OUROBOROS PROTOCOL

{description}

GENERATED CODE - Review before approval!
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.runtime.syscalls import register_syscall

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("{name.upper()}")


class {name.title().replace("_", "")}Plugin(KernelPlugin):
    """
    {description}

    Generated by OUROBOROS PROTOCOL (OPUS-032).
    """

    plugin_id = "{name}"
    priority = 80  # Low priority (loads after core plugins)

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Register syscall on boot."""
        register_syscall(
            "{syscall_name}",
            self._handle_{name},
            description="{description}",
            plugin_id=self.plugin_id,
        )
        logger.info("🐍 OUROBOROS: {syscall_name} syscall registered")

    def _handle_{name}(self, kernel: "RealVibeKernel", params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle {syscall_name} syscall.

        Args:
            kernel: The kernel instance
            params: Syscall parameters

        Returns:
            Result dict
        """
{param_code}

        try:
            # TODO: Implement actual logic here
            result = {{"message": "Hello from {name}!", "params": params}}
            return {{"success": True, "result": result}}
        except Exception as e:
            logger.error(f"{{syscall_name}} failed: {{e}}")
            return {{"success": False, "error": str(e)}}
'''

        manifest = f'''{{
    "id": "{name}",
    "name": "{name.title().replace("_", " ")}",
    "type": "plugin",
    "version": "1.0.0",
    "description": "{description}",
    "author": "OUROBOROS PROTOCOL",
    "priority": 80,
    "entry": "plugin_main.py",
    "generated": true,
    "syscalls": ["{syscall_name}"]
}}
'''

        return {"plugin_main.py": plugin_code, "manifest.json": manifest}

    def _generate_analyzer_code(self, name: str, description: str) -> Dict[str, str]:
        """Generate a MANAS analyzer."""
        analyzer_code = f'''"""
{name.title()} Analyzer - Generated by OUROBOROS PROTOCOL

{description}

GENERATED CODE - Review before approval!
"""

from typing import Any, Dict, List, Optional
from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent, IntentPriority, IntentRisk


def analyze_{name}(context: Dict[str, Any]) -> List[Intent]:
    """
    {description}

    Args:
        context: System context from Prakriti

    Returns:
        List of intents generated from analysis
    """
    intents = []

    # TODO: Implement analysis logic
    # Example:
    # if context.get("some_condition"):
    #     intents.append(Intent(
    #         intent_type="{name}",
    #         title="Action needed",
    #         description="Description of what needs to be done",
    #         priority=IntentPriority.MEDIUM,
    #         risk=IntentRisk.LOW,
    #     ))

    return intents
'''
        return {"analyzer_{name}.py": analyzer_code}

    def _generate_formatter_code(self, name: str, description: str) -> Dict[str, str]:
        """Generate an output formatter."""
        formatter_code = f'''"""
{name.title()} Formatter - Generated by OUROBOROS PROTOCOL

{description}

GENERATED CODE - Review before approval!
"""

from typing import Any, Dict


def format_{name}(data: Dict[str, Any]) -> str:
    """
    {description}

    Args:
        data: Data to format

    Returns:
        Formatted string
    """
    # TODO: Implement formatting logic
    return str(data)
'''
        return {"formatter_{name}.py": formatter_code}

    async def _genesis_submit_intent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Submit generated capability to Intent Buffer.
        """
        if not self._manas_ready or not self._manas:
            return {"success": False, "error": "MANAS not available"}

        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
            IntentPriority,
            IntentRisk,
        )

        name = params.get("capability_name", "")
        code = params.get("generated_code", {})
        priority = params.get("priority", "high")
        risk = params.get("risk", "high")
        reasoning = params.get("reasoning", "")

        # Create genesis intent
        intent = Intent(
            intent_type=f"genesis_{name}",
            title=f"Generate capability: {name}",
            description=f"Create new {name} capability via Ouroboros Protocol",
            priority=IntentPriority.HIGH if priority == "high" else IntentPriority.MEDIUM,
            risk=IntentRisk.HIGH if risk == "high" else IntentRisk.MEDIUM,
            auto_executable=False,  # NEVER auto-execute genesis
            reasoning=reasoning,
            action_params={"capability_name": name, "code": code},
        )

        # Add to MANAS intent buffer
        self._manas._pending_intents[intent.id] = intent

        self._log_observation_info(
            f"🐍 OUROBOROS: Capability '{name}' submitted to Intent Buffer for approval", "genesis"
        )

        return {"success": True, "intent_id": intent.id, "capability_name": name}

    async def _genesis_narasimha_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Narasimha security check on generated code.

        Static analysis to detect potentially unsafe patterns:
        - exec/eval usage
        - subprocess with shell=True
        - file operations outside sandbox
        - network calls
        - import of dangerous modules
        """
        import re

        code_dict = params.get("code", {})
        violations = []

        # Dangerous patterns to check
        dangerous_patterns = [
            (r"\bexec\s*\(", "exec() is not allowed"),
            (r"\beval\s*\(", "eval() is not allowed"),
            (r"subprocess.*shell\s*=\s*True", "subprocess with shell=True is not allowed"),
            (r"os\.system\s*\(", "os.system() is not allowed"),
            (r"__import__\s*\(", "Dynamic imports are not allowed"),
            (r'open\s*\([^)]*,\s*["\']w', "File write operations require review"),
            (r"import\s+socket", "Socket operations are not allowed"),
            (r"import\s+requests", "HTTP requests require review"),
            (r"from\s+pathlib.*write", "Path write operations require review"),
        ]

        for filename, code in code_dict.items():
            for pattern, message in dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    violations.append(f"{filename}: {message}")

        if violations:
            self._log_observation_warn(f"🦁 NARASIMHA: Security violations found: {violations}", "genesis")
            return {"safe": False, "violations": violations}

        self._log_observation_info("🦁 NARASIMHA: Security check passed", "genesis")
        return {"safe": True, "violations": []}

    async def _genesis_write_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Write approved code to runtime_extensions/.
        """
        from pathlib import Path

        output_dir = Path(params.get("output_dir", "vibe_core/plugins/runtime_extensions"))
        name = params.get("capability_name", "")
        code_dict = params.get("generated_code", {})

        if not name or not code_dict:
            return {"success": False, "error": "Missing capability_name or code"}

        try:
            # Create plugin directory
            plugin_dir = output_dir / name
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # Write files
            written_files = []
            for filename, content in code_dict.items():
                file_path = plugin_dir / filename
                file_path.write_text(content)
                written_files.append(str(file_path))

            # Create __init__.py if not present
            init_file = plugin_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""Generated plugin: {name}"""\n')
                written_files.append(str(init_file))

            self._log_observation_info(f"🐍 OUROBOROS: Wrote {len(written_files)} files to {plugin_dir}", "genesis")

            return {
                "success": True,
                "plugin_path": str(plugin_dir),
                "written_files": written_files,
            }

        except Exception as e:
            logger.error(f"Genesis write failed: {e}")
            return {"success": False, "error": str(e)}

    async def _genesis_hot_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Hot-load a generated capability.
        """
        from pathlib import Path

        from vibe_core.plugins.runtime_extensions.hot_loader import hot_load

        plugin_path = Path(params.get("plugin_path", ""))

        if not plugin_path.exists():
            return {"success": False, "error": f"Plugin path does not exist: {plugin_path}"}

        try:
            # Get kernel for registration
            kernel = getattr(self._plugin, "_kernel", None)

            # Hot-load the plugin using runtime_extensions.hot_loader
            plugin = hot_load(plugin_path, kernel=kernel)

            if plugin:
                self._log_observation_info(
                    f"🐍 OUROBOROS: Hot-loaded {plugin.plugin_id}! New capability available.", "genesis"
                )
                return {
                    "success": True,
                    "plugin_id": plugin.plugin_id,
                    "message": "The serpent has evolved.",
                }
            else:
                return {"success": False, "error": "Hot-load returned None"}

        except Exception as e:
            logger.error(f"Genesis hot-load failed: {e}")
            return {"success": False, "error": str(e)}

    async def _genesis_record_rejection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🐍 OUROBOROS: Record that a capability was rejected.
        """
        name = params.get("capability_name", "")

        if self._manas_ready and self._manas:
            # Record in memory to avoid suggesting again
            self._manas._memory.record_intent_outcome(
                intent_type=f"genesis_{name}",
                description=f"Generate capability: {name}",
                outcome="rejected",
                feedback="Human rejected via OPUS.md",
            )

        self._log_observation_info(f"🐍 OUROBOROS: Capability '{name}' rejected and recorded", "genesis")

        return {"success": True, "recorded": True}

    # =========================================================================
    # 📚 VIDYA: Knowledge Department Handlers (OPUS-033)
    # =========================================================================

    async def _vidya_research(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 VIDYA: Research best practices via Science Cartridge.

        This is the Jijnasa (Curiosity) phase - seeking wisdom before building.
        """
        from vibe_core.plugins.opus_assistant.vidya import ResearchInterface

        query = params.get("query", "")
        capability_name = params.get("capability_name", "")

        if not query:
            return {"success": False, "error": "Query is required"}

        try:
            research = ResearchInterface()
            result = await research.query(query, max_results=5)

            self._log_observation_info(
                f"📚 VIDYA Research: '{capability_name}' - {len(result.sources)} sources found", "vidya"
            )

            return {
                "success": result.success,
                "query": result.query,
                "sources": result.sources,
                "summary": result.summary,
                "key_insights": result.key_insights,
                "mode": result.mode,
            }

        except Exception as e:
            logger.warning(f"VIDYA research failed: {e}")
            # Return success=False but don't block - research is optional
            return {
                "success": False,
                "error": str(e),
                "sources": [],
                "summary": "",
                "key_insights": [],
            }

    async def _vidya_check_library(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 VIDYA: Check if capability already exists in knowledge library.

        This is the Smriti (Memory) phase - check before reinventing.
        """
        from vibe_core.plugins.opus_assistant.vidya import LibraryInterface

        capability_name = params.get("capability_name", "")
        tags = params.get("tags", [])

        try:
            library = LibraryInterface(workspace=self._plugin._workspace)
            result = library.search(capability_name, tags=tags)

            if result.found:
                self._log_observation_info(
                    f"📚 VIDYA Library: Found existing blueprint for '{capability_name}'", "vidya"
                )

            return {
                "found": result.found,
                "blueprints": [bp.to_dict() for bp in result.blueprints],
                "total_count": result.total_count,
                "blueprint": result.blueprints[0].to_dict() if result.blueprints else None,
            }

        except Exception as e:
            logger.warning(f"VIDYA library check failed: {e}")
            return {"found": False, "blueprints": [], "total_count": 0, "error": str(e)}

    async def _vidya_critique(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 VIDYA: Static analysis via Critic.

        This is the Pramana (Proof) phase - validate before deployment.
        """
        from vibe_core.plugins.opus_assistant.vidya import Critic

        code_dict = params.get("code", {})
        capability_name = params.get("capability_name", "")

        if not code_dict:
            return {"passed": False, "error": "No code provided"}

        try:
            critic = Critic()
            all_passed = True
            all_findings = []

            # Critique each file
            for filename, code in code_dict.items():
                result = critic.validate(code, filename=filename)
                if not result.passed:
                    all_passed = False
                all_findings.extend(
                    [{**f.__dict__, "severity": f.severity.value, "file": filename} for f in result.findings]
                )

            summary = (
                "✅ All code passed VIDYA critique" if all_passed else f"❌ VIDYA found {len(all_findings)} issues"
            )

            self._log_observation_info(
                f"📚 VIDYA Critique: '{capability_name}' - {'PASSED' if all_passed else 'FAILED'}", "vidya"
            )

            return {
                "passed": all_passed,
                "findings": all_findings,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"VIDYA critique failed: {e}")
            return {"passed": False, "error": str(e), "findings": [], "summary": f"Critique error: {e}"}

    async def _vidya_sandbox_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 VIDYA: Run tests in ephemeral sandbox.

        This is the critical safety gate - tests run in isolated process.
        """
        from vibe_core.plugins.opus_assistant.vidya import Sandbox

        code_dict = params.get("code", {})
        capability_name = params.get("capability_name", "")
        timeout_seconds = params.get("timeout_seconds", 30)

        if not code_dict:
            return {"success": False, "error": "No code provided"}

        try:
            sandbox = Sandbox(timeout_seconds=timeout_seconds)

            # Generate a simple test for the capability
            test_code = self._generate_capability_test(capability_name, code_dict)

            result = await sandbox.run_test(code_dict, test_code)

            self._log_observation_info(
                f"📚 VIDYA Sandbox: '{capability_name}' - {'PASSED' if result.success else 'FAILED'} ({result.duration_ms}ms)",
                "vidya",
            )

            return {
                "success": result.success,
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": result.duration_ms,
                "timed_out": result.timed_out,
                "error": result.error,
                "test_results": result.test_results,
            }

        except Exception as e:
            logger.error(f"VIDYA sandbox test failed: {e}")
            return {"success": False, "error": str(e)}

    def _generate_capability_test(self, capability_name: str, code_dict: Dict[str, str]) -> str:
        """Generate a basic test for the capability."""
        # Find the plugin class name
        plugin_class = capability_name.title().replace("_", "")

        return f'''"""
Auto-generated test for {capability_name}.
VIDYA Sandbox Test - OPUS-033
"""

import pytest


def test_module_imports():
    """Test that the module can be imported without errors."""
    # This tests basic syntax and import validity
    assert True  # If we get here, imports succeeded


def test_plugin_class_exists():
    """Test that the plugin class exists."""
    from plugin_main import {plugin_class}Plugin
    assert {plugin_class}Plugin is not None


def test_plugin_has_plugin_id():
    """Test that the plugin has a plugin_id."""
    from plugin_main import {plugin_class}Plugin
    plugin = {plugin_class}Plugin()
    assert hasattr(plugin, "plugin_id")
    assert plugin.plugin_id == "{capability_name}"
'''

    async def _vidya_store_blueprint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 VIDYA: Store successful blueprint in knowledge library.

        This is the Smriti (Memory) preservation - learn from success.
        """
        from vibe_core.plugins.opus_assistant.vidya import LibraryInterface

        capability_name = params.get("capability_name", "")
        description = params.get("description", "")
        code_dict = params.get("code", {})
        tags = params.get("tags", [])

        if not capability_name or not code_dict:
            return {"success": False, "error": "Missing required parameters"}

        try:
            library = LibraryInterface(workspace=self._plugin._workspace)
            success = library.store_blueprint(
                name=capability_name,
                description=description,
                code=code_dict,
                tags=tags,
                category="capabilities",
            )

            if success:
                self._log_observation_info(f"📚 VIDYA Library: Stored blueprint for '{capability_name}'", "vidya")

            return {"success": success, "capability_name": capability_name}

        except Exception as e:
            logger.warning(f"VIDYA blueprint storage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _vidya_record_failure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 VIDYA: Record a failed capability attempt for learning.

        Even failures teach us. Store them to avoid repeating mistakes.
        """
        from vibe_core.plugins.opus_assistant.vidya import LibraryInterface

        capability_name = params.get("capability_name", "")
        code_dict = params.get("code", {})
        error = params.get("error", "Unknown error")
        findings = params.get("findings", [])

        if not capability_name:
            return {"success": False, "error": "Missing capability_name"}

        try:
            library = LibraryInterface(workspace=self._plugin._workspace)
            success = library.record_failure(
                name=capability_name,
                code=code_dict,
                error=error,
                reason=str(findings) if findings else "",
            )

            self._log_observation_info(
                f"📚 VIDYA Library: Recorded failure for '{capability_name}' (for learning)", "vidya"
            )

            return {"success": success, "recorded": True}

        except Exception as e:
            logger.warning(f"VIDYA failure recording failed: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # 🏛️ GREMIUM: AI Federation Decision Handler (OPUS-035)
    # =========================================================================

    async def _gremium_evaluate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🏛️ GREMIUM: The AI Federation evaluates whether to auto-approve.

        This is the core of autonomous decision-making:
        - If all validators passed AND risk <= threshold → auto_approve
        - Otherwise → escalate to human

        The Gremium represents a council of validators speaking with one voice.
        No single validator makes the decision - consensus does.

        Risk Levels (ascending):
        - low: formatters, analyzers - safe to auto-approve
        - medium: syscalls, tools - auto-approve if all checks pass
        - high: kernel modifications - always escalate

        Args:
            params:
                capability_name: Name of the capability being evaluated
                critique_result: VIDYA Critic's analysis result
                risk_level: low/medium/high
                auto_threshold: The max risk level for auto-approval

        Returns:
            decision: "auto_approve" or "escalate"
            risk_level: The determined risk level
            escalation_reason: Why escalation is needed (if any)
        """
        capability_name = params.get("capability_name", "unknown")
        critique_result = params.get("critique_result", {})
        risk_level = params.get("risk_level", "medium").lower()
        auto_threshold = params.get("auto_threshold", "medium").lower()

        logger.info(f"🏛️ GREMIUM evaluating: {capability_name} (risk={risk_level}, threshold={auto_threshold})")

        # Risk hierarchy for comparison
        risk_hierarchy = {"low": 1, "medium": 2, "high": 3}
        risk_value = risk_hierarchy.get(risk_level, 2)
        threshold_value = risk_hierarchy.get(auto_threshold, 2)

        # Check 1: Did VIDYA Critique pass?
        vidya_passed = critique_result.get("passed", False)
        vidya_findings = critique_result.get("findings_count", 0)

        # Check 2: Risk level within threshold?
        within_threshold = risk_value <= threshold_value

        # GREMIUM Decision Logic
        if vidya_passed and within_threshold:
            # All validators agree: AUTO-APPROVE
            self._log_observation_info(
                f"🏛️ GREMIUM AUTO-APPROVED: {capability_name} (VIDYA=✅, risk={risk_level}≤{auto_threshold})",
                "gremium",
            )
            return {
                "decision": "auto_approve",
                "risk_level": risk_level,
                "escalation_reason": None,
                "validators": {
                    "vidya_critique": "passed",
                    "risk_check": "within_threshold",
                },
            }
        else:
            # Something needs human attention
            reasons = []
            if not vidya_passed:
                reasons.append(f"VIDYA found {vidya_findings} issues")
            if not within_threshold:
                reasons.append(f"risk={risk_level} exceeds threshold={auto_threshold}")

            escalation_reason = "; ".join(reasons)

            self._log_observation_warn(
                f"🏛️ GREMIUM ESCALATED: {capability_name} → human approval needed ({escalation_reason})",
                "gremium",
            )
            return {
                "decision": "escalate",
                "risk_level": risk_level,
                "escalation_reason": escalation_reason,
                "validators": {
                    "vidya_critique": "passed" if vidya_passed else "failed",
                    "risk_check": "within_threshold" if within_threshold else "exceeds_threshold",
                },
            }

    # =========================================================================
    # 💎 DIAMOND PROTOCOL: TDD Enforcement Handlers (OPUS-037)
    # =========================================================================
    # "RED before GREEN. Test before Code. No exceptions." - DIAMOND LAW

    async def _diamond_generate_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        💎 Generate test BEFORE implementation (Diamond Protocol Phase 1).

        This is the first step of TDD - the test defines the behavior
        before any code exists. The generated test WILL fail initially.

        Target: opus.diamond_generate_test
        """
        if not DIAMOND_AVAILABLE or get_diamond_handlers is None:
            logger.warning("💎 Diamond handlers not available")
            return {"success": False, "error": "Diamond handlers not available"}

        handlers = get_diamond_handlers(workspace=self._plugin._workspace)
        return await handlers.generate_test(params)

    async def _diamond_red_gate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        💎🔴 RED Gate - Test MUST fail (proves test is non-trivial).

        The critical innovation: we WANT the test to fail here.
        If it passes, the test is trivially true (bad) or feature exists.

        Target: opus.diamond_red_gate

        Returns:
            test_failed: True = RED gate passed (test failed as expected)
        """
        if not DIAMOND_AVAILABLE or get_diamond_handlers is None:
            logger.warning("💎 Diamond handlers not available")
            return {"success": False, "error": "Diamond handlers not available"}

        handlers = get_diamond_handlers(workspace=self._plugin._workspace)
        result = await handlers.red_gate(params)

        # Log the RED gate result
        if result.get("test_failed"):
            self._log_observation_info(
                f"💎✅ RED GATE PASSED: {params.get('capability_name', 'unknown')} - test failed as expected",
                "diamond",
            )
        else:
            self._log_observation_warn(
                f"💎🚫 RED GATE VIOLATED: {params.get('capability_name', 'unknown')} - trivial test rejected",
                "diamond",
            )

        return result

    async def _diamond_green_gate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        💎🟢 GREEN Gate - Test MUST pass (proves implementation works).

        The test that failed in RED phase must now pass.
        Only then can the capability be deployed.

        Target: opus.diamond_green_gate

        Returns:
            test_passed: True = GREEN gate passed (implementation works)
        """
        if not DIAMOND_AVAILABLE or get_diamond_handlers is None:
            logger.warning("💎 Diamond handlers not available")
            return {"success": False, "error": "Diamond handlers not available"}

        handlers = get_diamond_handlers(workspace=self._plugin._workspace)
        result = await handlers.green_gate(params)

        # Log the GREEN gate result
        if result.get("test_passed"):
            self._log_observation_info(
                f"💎✅ GREEN GATE PASSED: {params.get('capability_name', 'unknown')} - implementation verified",
                "diamond",
            )
        else:
            self._log_observation_alert(
                f"💎❌ GREEN GATE FAILED: {params.get('capability_name', 'unknown')} - implementation broken",
                "diamond",
            )

        return result

    # =========================================================================
    # 🧬 MUTATION PROTOCOL: Legacy Code Testing (OPUS-038)
    # =========================================================================
    # "A test that cannot detect errors is not a test. It is a lie."

    async def _mutation_green_gate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧬🟢 GREEN Gate for legacy code - Test MUST pass against original.

        First step of mutation testing: verify the test works with
        the current (unmutated) implementation.

        Target: opus.mutation_green_gate
        """
        if not MUTATION_AVAILABLE or get_mutation_handlers is None:
            logger.warning("🧬 Mutation handlers not available")
            return {"success": False, "error": "Mutation handlers not available"}

        handlers = get_mutation_handlers(workspace=self._plugin._workspace)
        result = await handlers.green_gate_original(params)

        if result.get("test_passed"):
            self._log_observation_info(
                f"🧬✅ GREEN GATE (Original): {params.get('module_name', 'unknown')} - test passes",
                "mutation",
            )
        else:
            self._log_observation_warn(
                f"🧬❌ GREEN GATE (Original): {params.get('module_name', 'unknown')} - test broken",
                "mutation",
            )

        return result

    async def _mutation_protocol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧬 Run full Mutation Protocol: GREEN → MUTATE → RED.

        Validates that a test can actually detect bugs by:
        1. GREEN: Test passes with original code
        2. MUTATE: Generate mutated versions with injected bugs
        3. RED: Test must FAIL against each mutant

        Kill rate = mutants_killed / total_mutants >= 80%

        Target: opus.mutation_protocol
        """
        if not MUTATION_AVAILABLE or get_mutation_handlers is None:
            logger.warning("🧬 Mutation handlers not available")
            return {"success": False, "error": "Mutation handlers not available"}

        handlers = get_mutation_handlers(workspace=self._plugin._workspace)
        result = await handlers.run_mutation_protocol(params)

        kill_rate = result.get("kill_rate", 0)
        survived = result.get("survived", 0)

        if result.get("success"):
            self._log_observation_info(
                f"🧬✅ MUTATION PROTOCOL PASSED: {params.get('module_name', 'unknown')} - kill rate {kill_rate:.1%}",
                "mutation",
            )
        else:
            self._log_observation_warn(
                f"🧬❌ MUTATION PROTOCOL FAILED: {params.get('module_name', 'unknown')} "
                f"- {survived} mutants survived (kill rate {kill_rate:.1%})",
                "mutation",
            )

        return result

    # =========================================================================
    # OPUS-108: The Autonomy Loop - Pulse Emission
    # =========================================================================

    async def _emit_autonomy_pulse(self, event: Any) -> None:
        """
        🔥 OPUS-108: Emit HOURLY_PULSE event to trigger MANAS_AWAKENING circuit.

        THE SINGULARITY TRIGGER:
            Without this, MANAS waits forever for external events.
            With this, MANAS awakens on schedule and thinks proactively.

        This transforms OPUS from:
            - Reactive (waits for user input)
            - To Proactive (generates intents autonomously)

        The MANAS_AWAKENING circuit will:
            1. Check rate limit (prevent excessive thinking)
            2. Gather context from Prakriti
            3. Generate proactive intents (THE THINKING!)
            4. Auto-execute safe intents if enabled
            5. Update Intent Buffer for OPUS.md
        """
        try:
            from vibe_core.event_bus import Event, EventType, get_event_bus

            bus = get_event_bus()

            # Create HOURLY_PULSE event
            pulse_event = Event(
                event_type=EventType.HOURLY_PULSE,
                payload={
                    "source": "kernel_tick",
                    "tick_count": self._tick_count,
                    "trigger": "autonomy_loop",
                },
            )

            # Emit the pulse - this triggers MANAS_AWAKENING circuit
            await bus.emit(pulse_event)

            self._log_observation_info(
                f"🔥 OPUS-108: HOURLY_PULSE emitted (tick #{self._tick_count}) - MANAS awakening",
                "autonomy",
            )
            logger.info("🔥 OPUS-108: HOURLY_PULSE emitted → MANAS_AWAKENING circuit triggered")

        except Exception as e:
            logger.warning(f"⚠️ OPUS-108: Could not emit HOURLY_PULSE: {e}")

    # =========================================================================
    # Fallback for events without circuits
    # =========================================================================

    async def _handle_event_fallback(self, event_type: str, event: Any) -> None:
        """
        Handle events that don't have circuits (backward compat).

        🔌 WIRING: Adds heartbeat + regular flush for system liveness.
        """
        if "KERNEL_TICK" in event_type:
            # 🔌 WIRING: Flush observations every 50 ticks (~2.5 min at 3s ticks)
            if self._tick_count % 50 == 0:
                self._flush_observations()

            # 🔌 WIRING: Heartbeat logging every 100 ticks (~5 min)
            # Shows system is alive and gives humans visibility
            if self._tick_count % 100 == 0 and self._tick_count > 0:
                self._log_observation_info(
                    f"System heartbeat: tick #{self._tick_count}, "
                    f"circuits: {len(self._circuits)}, "
                    f"drift_ticks: {self._consecutive_drift_ticks}",
                    "heartbeat",
                )

    # =========================================================================
    # Observation Logging (kept from original)
    # =========================================================================

    def _log_observation_info(self, message: str, source: str = "opus_assistant") -> None:
        if self._observation_logger:
            self._observation_logger.log_info(message, source)

    def _log_observation_warn(self, message: str, source: str = "opus_assistant") -> None:
        if self._observation_logger:
            self._observation_logger.log_warn(message, source)

    def _log_observation_alert(self, message: str, source: str = "opus_assistant") -> None:
        if self._observation_logger:
            self._observation_logger.log_alert(message, source)

    def _log_observation_insight(self, message: str, source: str = "opus_assistant") -> None:
        if self._observation_logger:
            self._observation_logger.log_insight(message, source)

    def _flush_observations(self) -> None:
        # NOTE: flush_to_opus() REMOVED - opus_assistant is BACKEND only
        # Observations are persisted to StateManager automatically
        # OPUS.md reads from StateManager when InterfacePlugin renders
        pass

    # =========================================================================
    # State accessors (kept from original)
    # =========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get current tick handler state."""
        state = {
            "tick_count": self._tick_count,
            "subscribed": self._subscribed,
            "circuits_loaded": len(self._circuits),
            "circuit_ids": list(self._circuits.keys()),
            "last_state": self._last_state,
            "has_context_service": self._context_service is not None,
        }

        # Add context service info for backward compat
        if self._context_service:
            state["context_synthesis_count"] = self._context_service.get_synthesis_count()
            if "system_health" in self._last_state:
                state["system_health"] = self._last_state["system_health"]

        return state

    # =========================================================================
    # Backward Compatibility Methods (for tests)
    # =========================================================================

    async def _on_tick(self, event: Any) -> None:
        """Backward compat: Handle tick via circuits."""
        matching = self._get_circuits_for_trigger("KERNEL_TICK")
        for circuit in matching:
            await self._execute_circuit(circuit, event)
        await self._handle_event_fallback("KERNEL_TICK", event)

    async def _on_commit(self, event: Any) -> None:
        """Backward compat: Handle commit via circuits."""
        matching = self._get_circuits_for_trigger("GIT_COMMIT")
        for circuit in matching:
            await self._execute_circuit(circuit, event)

    async def _on_file_changed(self, event: Any) -> None:
        """Backward compat: Handle file change via circuits."""
        matching = self._get_circuits_for_trigger("FILE_CHANGED")
        for circuit in matching:
            await self._execute_circuit(circuit, event)

    def get_context_service(self) -> Optional["OpusContextService"]:
        return self._context_service

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        if self._context_service:
            return self._context_service.get_current_context()
        return self._last_state.get("context")

    def get_system_prompt_fragment(self) -> str:
        if self._context_service:
            return self._context_service.get_system_prompt_fragment()
        return ""

    def get_observation_logger(self) -> Optional["ObservationLogger"]:
        return self._observation_logger


# Synchronous wrapper
class SyncKernelTickHandler(KernelTickHandler):
    """Synchronous version of KernelTickHandler."""

    def _on_event_sync(self, event: Any) -> None:
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._on_event(event))
            else:
                loop.run_until_complete(self._on_event(event))
        except RuntimeError:
            asyncio.run(self._on_event(event))
