"""
OPUS Assistant Kernel Tick - Circuit-Driven Event Handler.

OPUS-029 Phase 7: True Cognitive Circuit Execution

The plugin doesn't just boot and die. It stays ALIVE via EventBus.
Now it executes REAL circuits from opus_assistant/circuits/*.yaml

Circuit-Driven Pattern:
1. Plugin subscribes to EventBus events (KERNEL_TICK, GIT_COMMIT, etc.)
2. On event, find circuits with matching trigger
3. Execute circuits via CognitiveCircuitExecutor
4. Circuits define behavior - NOT hardcoded actions!

This is AUTONOMOUS COGNITION - circuits drive behavior.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

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

        # Initialize services
        self._init_context_service()
        self._init_observation_logger()
        self._init_circuits()

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
            if not events_to_subscribe:
                events_to_subscribe = {"KERNEL_TICK", "GIT_COMMIT"}

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

        Maps circuit actions to plugin methods.
        LOGS observations about circuit execution to the journal!

        Args:
            circuit_def: Circuit definition from YAML
            event: The triggering event
        """
        circuit_id = circuit_def.get("id", "unknown")
        entry_state = circuit_def.get("entry_state", "")
        states = circuit_def.get("states", {})

        # LOG: Circuit starting
        self._log_observation_info(f"Circuit {circuit_id} triggered", "circuit")

        logger.debug(f"⚡ Executing circuit {circuit_id} from state {entry_state}")

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

    async def _execute_action(self, action: Dict[str, Any], event: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single circuit action.

        Maps action targets to plugin methods.

        Args:
            action: Action definition from circuit
            event: The triggering event
            context: Accumulated context from previous actions

        Returns:
            Action result dict
        """
        action_type = action.get("action_type", "")
        target = action.get("target", "")
        params = action.get("params", {})

        try:
            if action_type == "EXECUTE_SCRIPT":
                return await self._execute_script_action(target, params)
            elif action_type == "EMIT_EVENT":
                return await self._emit_event_action(target, params)
            elif action_type == "CHECK_STATE":
                return await self._check_state_action(target, params, context)
            else:
                logger.debug(f"Unknown action type: {action_type}")
                return {"success": False, "error": f"Unknown action type: {action_type}"}
        except Exception as e:
            logger.debug(f"Action {action_type}:{target} failed: {e}")
            return {"success": False, "error": str(e)}

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
        """Regenerate OPUS.md."""
        try:
            result = self._plugin.generate_opus()
            return {"success": True, "result": result}
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

                # LOG: Health status changes
                new_health = context.health.status
                if self._last_health_status and new_health != self._last_health_status:
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
            else:
                return {"success": False, "error": f"Unknown vedic method: {method_name}"}

        except Exception as e:
            logger.error(f"Vedic action failed: {e}")
            return {"success": False, "error": str(e)}

    async def _vedic_demote_agent(self, governance: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Demote an agent via Vedic Governance.

        This is the CONSEQUENCE - trust drop leads to lifecycle demotion.
        """
        from vibe_core.plugins.vedic_governance.ashrama import Ashrama

        agent_id = params.get("agent_id")
        reason = params.get("reason", "Karma consequence")

        if not agent_id:
            return {"success": False, "error": "No agent_id provided"}

        # Get current ashrama
        current = governance.get_agent_ashrama(agent_id)
        if not current:
            return {"success": False, "error": f"Agent {agent_id} not found in governance"}

        current_stage = current.current_ashrama

        # Determine demotion target
        # GRIHASTHA → BRAHMACHARI (back to student)
        # VANAPRASTHA → GRIHASTHA (back to active but probation)
        demotion_map = {
            Ashrama.GRIHASTHA: Ashrama.BRAHMACHARI,
            Ashrama.VANAPRASTHA: Ashrama.GRIHASTHA,
            Ashrama.SANNYASA: Ashrama.VANAPRASTHA,
        }

        new_stage = demotion_map.get(current_stage)
        if not new_stage:
            # BRAHMACHARI can't be demoted further
            return {
                "success": True,
                "demoted": False,
                "reason": f"Agent {agent_id} is already at lowest stage (BRAHMACHARI)",
            }

        # Execute demotion
        success = governance.transition_agent_ashrama(agent_id, new_stage, reason)

        if success:
            logger.warning(f"🕉️ KARMA: Agent '{agent_id}' demoted {current_stage.value} → {new_stage.value}")
            return {
                "success": True,
                "demoted": True,
                "agent_id": agent_id,
                "from_stage": current_stage.value,
                "to_stage": new_stage.value,
                "reason": reason,
            }
        else:
            return {"success": False, "error": "Demotion transition failed"}

    async def _vedic_check_promotions(self, governance: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for agents eligible for accelerated promotion.

        When trust is consistently high, agents can graduate faster.
        """
        from vibe_core.plugins.vedic_governance.ashrama import Ashrama

        accelerated = params.get("accelerated", False)
        threshold_reduction = params.get("threshold_reduction", 0)

        promoted = []

        # Get all agents in BRAHMACHARI stage
        ashrama_registry = governance.get_ashrama_registry()

        for agent_id, transition in ashrama_registry.items():
            if transition.current_ashrama == Ashrama.BRAHMACHARI:
                # Check task completions
                completions = governance._task_completions.get(agent_id, 0)
                required = 3 - threshold_reduction if accelerated else 3

                if completions >= required:
                    success = governance.transition_agent_ashrama(
                        agent_id, Ashrama.GRIHASTHA, reason="Accelerated graduation (trust bonus)"
                    )
                    if success:
                        promoted.append(agent_id)
                        logger.info(f"🕉️ KARMA: Agent '{agent_id}' graduated early (high trust)")

        return {"success": True, "promoted": promoted, "count": len(promoted)}

    # =========================================================================
    # Fallback for events without circuits
    # =========================================================================

    async def _handle_event_fallback(self, event_type: str, event: Any) -> None:
        """Handle events that don't have circuits (backward compat)."""
        if "KERNEL_TICK" in event_type:
            # Minimal tick handling
            if self._tick_count % 10 == 0:
                self._flush_observations()

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
        if self._observation_logger:
            self._observation_logger.flush_to_opus()

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
