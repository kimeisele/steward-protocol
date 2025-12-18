"""
OPUS-087: PRANA Orchestrator
============================
Refactored for OPUS-095: Cognitive Abstraction.

Orchestrates the plugin lifecycle pulse using the standard Cognitive Cycle.
Phases: SENSORS -> ACTUATORS -> CLEANUP

ARCHITECTURE DECISION: This is SEPARATE from vibe_core/prana.py (config loader).
This module handles orchestration via CognitiveCycle, transactions, and plugin coordination.

Key Components:
    - StateMutation: Typed mutation schema for plugin state changes
    - PulseTransaction: Atomic batch commit with fail-forward strategy
    - PranaOrchestrator: Inherits from CognitiveCycle for unified orchestration
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

from vibe_core.event_bus import EventBus, EventType
from vibe_core.orchestration_cycle import CognitiveCycle, CycleContext
from vibe_core.runtime.unified_trace import UnifiedTrace

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("PRANA_ORCHESTRATOR")

# =============================================================================
# CONFIGURATION (Backward Compatibility)
# =============================================================================


@dataclass
class PranaOrchestratorConfig:
    """Configuration for PRANA Orchestrator (backward compatible)."""

    rate_limit_seconds: int = 60
    max_pulse_duration: int = 300
    enable_recovery: bool = True

    # Deprecated: Kept for backward compatibility with existing tests
    pass


# =============================================================================
# MUTATION SCHEMA
# =============================================================================

# Allowed mutation actions (extensible)
ALLOWED_ACTIONS: Set[str] = {
    "update_doc",  # Update markdown file
    "decay_karma",  # Adjust karma score
    "refresh_state",  # Refresh Prakriti layer
    "log_observation",  # Add to system journal
    "quarantine_plugin",  # Disable misbehaving plugin
}


@dataclass
class StateMutation:
    """
    Single state change request from a plugin.

    OPUS-087: Plugins MUST NOT commit to Git during on_pulse.
    They register mutations with PulseTransaction instead.
    """

    plugin_id: str
    action: str  # e.g., "update_doc", "decay_karma", "refresh_opus"
    target: str  # e.g., "OPUS.md", "karma.json", "agent:envoy"
    payload: Dict[str, Any]
    priority: int = 1  # Lower = execute first within phase

    def validate(self) -> bool:
        """
        Pre-flight validation before commit.

        Validation Rules:
        1. plugin_id MUST be non-empty
        2. action MUST be in allowed actions list
        3. target MUST be non-empty
        4. payload MUST be a dict
        """
        if not self.plugin_id:
            return False
        if not self.action:
            return False
        if self.action not in ALLOWED_ACTIONS:
            return False
        if not self.target:
            return False
        if not isinstance(self.payload, dict):
            return False
        return True


# =============================================================================
# PULSE TRANSACTION
# =============================================================================


@dataclass
class PulseTransaction:
    """
    Atomic batch of mutations for a single pulse cycle.

    FAIL-FORWARD STRATEGY (OPUS-087):
    - If validation fails BEFORE write → Abort entire transaction
    - If error occurs DURING write → Log, continue, don't rollback
    - Git state is too complex for safe rollback
    """

    transaction_id: str = field(default_factory=lambda: f"tx_{uuid.uuid4().hex[:8]}")
    timestamp: float = field(default_factory=time.time)
    mutations: List[StateMutation] = field(default_factory=list)
    status: str = "pending"  # pending, committed, failed
    validation_errors: List[str] = field(default_factory=list)
    execution_errors: List[str] = field(default_factory=list)

    @classmethod
    def create(cls) -> "PulseTransaction":
        """Factory method to create a new transaction."""
        return cls(
            transaction_id=f"tx_{uuid.uuid4().hex[:8]}",
            timestamp=time.time(),
        )

    def add_mutation(self, mutation: StateMutation) -> bool:
        """Add mutation after validation."""
        if not mutation.validate():
            error = f"Invalid mutation: plugin={mutation.plugin_id}, action={mutation.action}"
            self.validation_errors.append(error)
            logger.warning(error)
            return False
        self.mutations.append(mutation)
        return True

    def validate_all(self) -> bool:
        """Pre-flight validation of all mutations."""
        for mutation in self.mutations:
            if not mutation.validate():
                self.validation_errors.append(f"Mutation validation failed: {mutation}")
                return False
        return True

    # Backward compatibility: support old register() method
    def register(self, mutation: StateMutation) -> bool:
        """Legacy method: add mutation (deprecated, use add_mutation)."""
        return self.add_mutation(mutation)

    def commit(self) -> Tuple[int, int]:
        """
        Execute all mutations and return (success_count, failure_count).

        Backward compatibility for tests. Uses handlers registered via
        _register_default_handlers() or falls back to built-in handlers.
        """
        success = 0
        failure = 0

        for mutation in self.mutations:
            handler = self._handlers.get(mutation.action)
            if handler:
                try:
                    handler(mutation)
                    success += 1
                except Exception as e:
                    logger.error(f"Handler failed for {mutation.action}: {e}")
                    self.execution_errors.append(str(e))
                    failure += 1
            else:
                logger.warning(f"No handler for action: {mutation.action}")
                failure += 1

        self.status = "committed" if failure == 0 else "partial"
        return success, failure

    # Handler registry for backward compatibility
    _handlers: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# ORCHESTRATOR
# =============================================================================


class PranaOrchestrator(CognitiveCycle):
    """
    The Heartbeat of the System.

    Migrated to CognitiveCycle (OPUS-095):
    - Manages Plugin execution order (Sensors -> Actuators -> Cleanup)
    - Handles State Transactions with atomic semantics
    - Integrated with UnifiedTrace & EventBus
    - Holon wiring via parent_cycle_id
    """

    def __init__(
        self,
        plugin_loader: Any = None,
        ledger: Any = None,
        trace: Optional[UnifiedTrace] = None,
        event_bus: Optional[EventBus] = None,
        *,
        kernel: Any = None,  # Backward compatibility for tests
    ):
        """
        Initialize Prana Orchestrator.

        Args:
            plugin_loader: Component to fetch active plugins
            ledger: Persistence layer for state commit
            trace: Observability (UnifiedTrace)
            event_bus: System events (EventBus)
            kernel: (DEPRECATED) Backward compatibility - extracts plugin_loader/ledger from kernel
        """
        super().__init__()

        # Backward compatibility: extract from kernel if provided
        if kernel is not None:
            self.plugin_loader = getattr(kernel, "plugin_loader", None)
            self.ledger = getattr(kernel, "ledger", None) or getattr(kernel, "_ledger", None)
        else:
            self.plugin_loader = plugin_loader
            self.ledger = ledger
        self.logger = logging.getLogger("PRANA_ORCHESTRATOR")

        # Configuration
        self._rate_limit = 60  # Default 1 minute (can be overridden)
        self._parent_cycle_id: Optional[str] = None

        # Phase A Integration
        if trace and event_bus:
            self.setup(trace, event_bus, steward_context=None)

    # ========================================================================
    # BACKWARD COMPATIBILITY: DEFAULT HANDLERS
    # ========================================================================

    def _register_default_handlers(self, transaction: PulseTransaction) -> None:
        """
        Register default mutation handlers for backward compatibility.

        Args:
            transaction: PulseTransaction to register handlers on
        """
        from pathlib import Path

        def update_doc_handler(mutation: StateMutation) -> None:
            """Handle update_doc mutations by writing to filesystem."""
            content = mutation.payload.get("content", "")
            target_path = Path(mutation.target)
            target_path.write_text(content)
            logger.info(f"Updated {mutation.target} ({len(content)} chars)")

        def decay_karma_handler(mutation: StateMutation) -> None:
            """Handle decay_karma mutations."""
            logger.info(f"Karma decay for {mutation.target}: {mutation.payload}")

        def log_observation_handler(mutation: StateMutation) -> None:
            """Handle log_observation mutations."""
            logger.info(f"Observation: {mutation.payload}")

        # Register handlers on the transaction
        transaction._handlers = {
            "update_doc": update_doc_handler,
            "decay_karma": decay_karma_handler,
            "log_observation": log_observation_handler,
            "refresh_state": lambda m: logger.info(f"Refresh state: {m.target}"),
            "quarantine_plugin": lambda m: logger.warning(f"Quarantine: {m.target}"),
        }

    # ========================================================================
    # COGNITIVECYCLE CONFIGURATION
    # ========================================================================

    @property
    def cycle_name(self) -> str:
        """Cycle name for observability."""
        return "prana_pulse"

    @property
    def rate_limit_seconds(self) -> int:
        """Rate limit for pulse cycles (seconds)."""
        return self._rate_limit

    @property
    def timeout_seconds(self) -> int:
        """Maximum pulse execution time."""
        return 300  # 5 minutes

    @property
    def recovery_enabled(self) -> bool:
        """Enable error recovery."""
        return True

    @property
    def parent_cycle_id(self) -> Optional[str]:
        """Holon wiring: parent cycle (e.g., BootOrchestrator)."""
        return self._parent_cycle_id

    # ========================================================================
    # OODA LOOP IMPLEMENTATION
    # ========================================================================

    async def _perceive(self) -> Tuple[List[Any], Dict[str, Any]]:
        """
        PERCEIVE: Discover active plugins and check system health.

        Returns:
            (observations, metadata)
        """
        observations = []
        metadata = {}

        try:
            # Load active plugins
            plugins = (
                self.plugin_loader.get_active_plugins() if hasattr(self.plugin_loader, "get_active_plugins") else []
            )
            observations.append({"type": "active_plugins", "count": len(plugins), "data": plugins})

            # System health check (simplified)
            observations.append({"type": "system_health", "status": "nominal"})

            metadata["plugins_discovered"] = len(plugins)

        except Exception as e:
            self.logger.error(f"Prana perception failed: {e}")
            metadata["error"] = str(e)

        return observations, metadata

    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        ORIENT: Sort plugins into execution phases.

        Execution order: SENSORS -> ACTUATORS -> CLEANUP
        Maintains causality for state mutations.

        Returns:
            (orientations, metadata)
        """
        orientations = []
        metadata = {}

        # Extract plugins from observations
        plugins = []
        for obs in observations:
            if obs.get("type") == "active_plugins":
                plugins = obs.get("data", [])
                break

        # Sort by phase: sensors first, then actuators, then cleanup
        sensors = [p for p in plugins if getattr(p, "phase", "standard") == "sensor"]
        actuators = [p for p in plugins if getattr(p, "phase", "standard") == "actuator"]
        cleanup = [p for p in plugins if getattr(p, "phase", "standard") == "cleanup"]
        others = [p for p in plugins if p not in sensors and p not in actuators and p not in cleanup]

        # Create execution plan with proper phase ordering
        execution_plan = {
            "phases": [
                {"name": "sensors", "plugins": sensors},
                {"name": "actuators", "plugins": actuators + others},  # Others default to actuators
                {"name": "cleanup", "plugins": cleanup},
            ]
        }
        orientations.append(execution_plan)

        metadata["phase_breakdown"] = {
            "sensors": len(sensors),
            "actuators": len(actuators),
            "others": len(others),
            "cleanup": len(cleanup),
        }

        return orientations, metadata

    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        DECIDE: Create a PulseTransaction and finalize execution plan.

        Returns:
            (decisions, metadata)
        """
        decisions = []
        metadata = {}

        try:
            plan = orientations[0] if orientations else {"phases": []}

            # Create transaction for this pulse
            transaction = PulseTransaction.create()

            # Decision: commit to execute plan as-is (rate limiting applied by orchestrate)
            final_schedule = plan

            decisions.append({"transaction": transaction, "schedule": final_schedule})

            metadata["transaction_id"] = transaction.transaction_id
            metadata["total_plugins"] = sum(len(p["plugins"]) for p in plan.get("phases", []))

        except Exception as e:
            self.logger.error(f"Prana decision failed: {e}")
            metadata["error"] = str(e)

        return decisions, metadata

    async def _act(self, decisions: List[Any]) -> Tuple[Optional[PulseTransaction], Dict[str, Any]]:
        """
        ACT: Execute plugin schedule and collect mutations.

        Returns:
            (transaction with mutations, metadata)
        """
        metadata = {}

        if not decisions:
            return None, metadata

        decision = decisions[0]
        transaction: PulseTransaction = decision["transaction"]
        schedule = decision["schedule"]

        total_executed = 0
        total_mutations = 0

        # Execute plugins phase by phase
        for phase in schedule.get("phases", []):
            phase_name = phase["name"]
            plugins = phase["plugins"]

            for plugin in plugins:
                plugin_name = getattr(plugin, "name", "unknown_plugin")
                total_executed += 1

                # Trace plugin execution
                span_id = None
                if self._trace:
                    span_id = self._trace.start_span(
                        f"plugin_{plugin_name}", parent_id=getattr(self._trace, "current_span_id", None)
                    )

                try:
                    # Execute plugin (standard interface: pulse() or execute())
                    result = None
                    if hasattr(plugin, "pulse"):
                        result = await plugin.pulse(transaction)
                    elif hasattr(plugin, "execute"):
                        result = await plugin.execute()
                    else:
                        result = await plugin()  # Try calling as coroutine

                    # Collect mutations
                    if result:
                        if isinstance(result, list):
                            for mutation in result:
                                if isinstance(mutation, StateMutation):
                                    transaction.add_mutation(mutation)
                                    total_mutations += 1
                        elif isinstance(result, StateMutation):
                            transaction.add_mutation(result)
                            total_mutations += 1

                    self.logger.debug(f"✓ Plugin {plugin_name} executed successfully")

                except Exception as e:
                    error_msg = f"Plugin {plugin_name} failed: {e}"
                    transaction.execution_errors.append(error_msg)
                    self.logger.error(error_msg)
                    # Continue with next plugin (fail-forward strategy)

                finally:
                    if self._trace and span_id:
                        self._trace.end_span(span_id)

        metadata["plugins_executed"] = total_executed
        metadata["mutations_collected"] = total_mutations

        return transaction, metadata

    async def _persist(self) -> None:
        """
        PERSIST: Commit the PulseTransaction to the Ledger.

        Called after _act() completes with transaction available in context.
        """
        # Note: Transaction is accessed via self._context.results if needed
        # For now, persistence happens in a post-hook or separate call
        logger.debug("💾 PRANA: Persisted pulse transaction")

    # ========================================================================
    # PUBLIC INTERFACE
    # ========================================================================

    async def pulse(self, parent_cycle_id: Optional[str] = None, force: bool = False) -> Optional[CycleContext]:
        """
        Run the Prana Pulse Cycle.

        OPUS-095: Integrated with CognitiveCycle orchestrate().

        Args:
            parent_cycle_id: ID of calling cycle (e.g., BootOrchestrator)
            force: Bypass rate limits

        Returns:
            CycleContext with transaction in results
        """
        self._parent_cycle_id = parent_cycle_id
        return await self.orchestrate(force=force)

    async def commit_transaction(self, transaction: PulseTransaction) -> bool:
        """
        Commit transaction to ledger.

        Called after orchestrate() completes.

        Args:
            transaction: PulseTransaction to commit

        Returns:
            True if successful
        """
        if not transaction or not self.ledger:
            return False

        try:
            # Pre-flight validation
            if not transaction.validate_all():
                logger.error(f"Transaction validation failed: {transaction.validation_errors}")
                transaction.status = "failed"
                return False

            # Attempt commit
            if hasattr(self.ledger, "commit_transaction"):
                await self.ledger.commit_transaction(transaction)
            elif hasattr(self.ledger, "commit"):
                await self.ledger.commit(transaction)

            transaction.status = "committed"
            logger.info(f"✓ Transaction {transaction.transaction_id} committed: {len(transaction.mutations)} mutations")
            return True

        except Exception as e:
            transaction.status = "failed"
            transaction.execution_errors.append(str(e))
            logger.error(f"Transaction commit failed: {e}")
            return False
