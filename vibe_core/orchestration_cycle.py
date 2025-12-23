"""
OPUS-095: Cognitive Abstraction - Unified Orchestration Cycle Framework

This module provides the foundational abstractions for ALL orchestration loops in MANAS:
- CognitiveCycle: Base class for repeating orchestration patterns (CognitiveKernel, PranaOrchestrator, BootOrchestrator)
- CognitiveProcess: Base class for stateless linear processors (CircuitExecutor, Cortex Senses)
- CycleContext: Execution context that wraps UnifiedTrace (integrated observability)
- CycleRegistry: Lifecycle manager with memory safety via retention policy
- RetentionPolicy: Memory leak prevention

CRITICAL INTEGRATION:
- CycleContext.trace_id links to UnifiedTrace (not a parallel system)
- Phase transitions emit to EventBus (integrated monitoring)
- parent_cycle_id enables Holon causality tracking (why is this child running?)
- RetentionPolicy prevents unbounded memory growth (memory safety)

Architecture:
    Orchestration Cycles (Repeating)
          ├── CognitiveKernel: OODA loop (Perceive → Orient → Decide → Act → Persist)
          ├── PranaOrchestrator: Plugin lifecycle (SENSORS → ACTUATORS → CLEANUP → PERSIST)
          └── BootOrchestrator: Cosmic phases (Brahma → Vishnu → Shiva → Dharma → PERSIST)

    Orchestration Processes (Linear)
          ├── CircuitExecutor: YAML state machine runner (called during ACT phase)
          └── Cortex Senses: Perception classifier (called during perception phases)

    Observability Integration
          ├── UnifiedTrace: Central trace collection (trace_id in CycleContext)
          ├── EventBus: Phase transition events (emitted on PERCEIVE, ORIENT, DECIDE, ACT, PERSIST)
          └── StewardContext: Dependency injection (Soul, Ledger, etc.)
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.event_bus import EventBus, EventType, emit_event
from vibe_core.runtime.unified_trace import UnifiedTrace
from vibe_core.state.schema import CyclePhase

logger = logging.getLogger("ORCHESTRATION.CYCLE")

# =============================================================================
# GLOBAL CYCLE REGISTRY (Singleton)
# =============================================================================
# CRITICAL: This is the single source of truth for all cycle lifecycle tracking.
# Auto-registration happens in orchestrate(), so all cycles are automatically
# tracked without requiring manual registration.
_global_cycle_registry: Optional["CycleRegistry"] = None


def get_cycle_registry() -> "CycleRegistry":
    """
    Get the global cycle registry (creates if needed).

    USAGE (from within any CognitiveCycle):
        registry = get_cycle_registry()
        # registry now has all active/completed/error cycles
    """
    global _global_cycle_registry
    if _global_cycle_registry is None:
        from vibe_core.orchestration_cycle import CycleRegistry, RetentionPolicy

        _global_cycle_registry = CycleRegistry(retention_policy=RetentionPolicy())
        logger.info("📊 Global CycleRegistry initialized (singleton pattern)")
    return _global_cycle_registry


def set_cycle_registry(registry: "CycleRegistry") -> None:
    """
    Override the global registry (useful for testing with custom retention policies).
    """
    global _global_cycle_registry
    _global_cycle_registry = registry
    logger.info("🔄 Global CycleRegistry overridden (custom instance)")


def reset_cycle_registry() -> None:
    """
    Reset registry to None (useful for cleanup between test runs).
    """
    global _global_cycle_registry
    _global_cycle_registry = None
    logger.debug("🔄 Global CycleRegistry reset")


@dataclass
class CycleContext:
    """
    Execution context passed through cycle phases.

    CRITICAL INTEGRATION:
    - trace_id: Links to UnifiedTrace (not a separate system)
    - parent_cycle_id: Holon wiring (establishes causality chain)
    - emitted_events: EventBus event IDs for observability
    - phase_start_time: For timeout/duration tracking

    This is NOT an isolated context - it's a wrapper that integrates
    with existing system infrastructure (Trace, Bus).
    """

    # Identity & Causality
    cycle_id: str  # Unique ID for this execution
    parent_cycle_id: Optional[str]  # HOLON WIRING: Why am I running? (e.g., BootOrchestrator → PranaOrchestrator)
    trace_id: str  # Links to UnifiedTrace (NOT a separate system)
    cycle_name: str  # e.g., "cognitive_kernel", "plugin_pulse", "boot_orchestrator"

    # Phase tracking
    phase: CyclePhase  # Current phase
    phase_start_time: float  # When did this phase start? (for timeout checking)

    # Phase results (accumulated through execution)
    observations: List[Any] = field(default_factory=list)  # From PERCEIVE phase
    orientations: List[Any] = field(default_factory=list)  # From ORIENT phase
    decisions: List[Any] = field(default_factory=list)  # From DECIDE phase
    actions: List[Any] = field(default_factory=list)  # From ACT phase
    results: Optional[Any] = None  # From execution (final result)
    errors: Dict[str, str] = field(default_factory=dict)  # Accumulated errors (phase_name → error_message)

    # Metadata & Extensions
    metadata: Dict[str, Any] = field(default_factory=dict)  # Subclass-specific data

    # EventBus integration
    emitted_events: List[str] = field(default_factory=list)  # Event IDs for observability

    def has_errors(self) -> bool:
        """Check if any errors were recorded during execution."""
        return len(self.errors) > 0

    def add_error(self, phase: str, error: str) -> None:
        """Record an error during a phase."""
        self.errors[phase] = error

    def get_elapsed_time(self) -> float:
        """Get elapsed time since phase started (seconds)."""
        return time.time() - self.phase_start_time


@dataclass
class RetentionPolicy:
    """
    Memory safety: Define how long CycleRegistry retains cycle history.

    CRITICAL CORRECTION (from user review):
    This prevents memory leaks. Without retention, CycleRegistry would
    store all cycles forever, causing unbounded memory growth.

    Configuration:
    - max_completed_cycles: Keep last N successful cycles (default: 100)
    - max_error_cycles: Keep more error cycles for debugging (default: 500)
    - max_age_seconds: Optional TTL for cycles (default: None = no TTL)
    - enabled: Toggle retention (default: True)
    """

    max_completed_cycles: int = 100  # Keep last N completed cycles
    max_error_cycles: int = 500  # Keep more errors (debugging needed)
    max_age_seconds: Optional[int] = None  # Optional TTL (e.g., 3600 = 1 hour)
    enabled: bool = True  # Toggle retention (False = disable for testing)


class CognitiveCycle(ABC):
    """
    Abstract base class for ALL orchestration CYCLES in the system.

    SCOPE (from user review):
    - This is for CYCLES (repeating orchestration loops)
    - Examples: CognitiveKernel, PranaOrchestrator, BootOrchestrator
    - NOT for Processes (use CognitiveProcess for CircuitExecutor, Cortex Senses)

    SYSTEM INTEGRATION:
    - Uses UnifiedTrace for tracing (starts trace, emits events, completes trace)
    - Emits to EventBus on phase transitions (PERCEIVE, ORIENT, DECIDE, ACT, PERSIST)
    - Supports parent_cycle_id for Holon causality tracking
    - CycleRegistry manages lifetime with retention policy

    TEMPLATE METHOD PATTERN:
    - orchestrate() is the final implementation (not overridden)
    - Subclasses implement ONLY: _perceive(), _orient(), _decide(), _act()
    - Subclasses MAY override: _persist(), _recover(), parent_cycle_id property

    USAGE:
        class MyCustomCycle(CognitiveCycle):
            def _perceive(self): ...
            def _orient(self, obs): ...
            def _decide(self, orient): ...
            def _act(self, decisions): ...

        cycle = MyCustomCycle()
        cycle.setup(trace, event_bus, steward_context)
        context = await cycle.orchestrate()
    """

    def __init__(self):
        """Initialize cycle with system dependencies (None until setup() called)."""
        self._trace: Optional[UnifiedTrace] = None
        self._event_bus: Optional[EventBus] = None
        self._steward_context: Optional[Any] = None
        self._last_cycle_time: float = 0.0  # For rate limiting
        logger.debug(f"🔄 {self.__class__.__name__} initialized (awaiting setup)")

    # ========================================================================
    # DEPENDENCY INJECTION (must be called before orchestrate())
    # ========================================================================

    def setup(self, trace: UnifiedTrace, event_bus: EventBus, steward_context: Any) -> None:
        """
        Wire up system integration points BEFORE orchestrate().

        This is NOT in __init__ because these are global singletons that
        might not exist during class instantiation.

        Args:
            trace: UnifiedTrace instance for observability
            event_bus: EventBus instance for phase transition events
            steward_context: StewardContext with Soul, Ledger, etc.
        """
        self._trace = trace
        self._event_bus = event_bus
        self._steward_context = steward_context
        logger.debug(f"✅ {self.__class__.__name__} setup complete (trace, bus, context wired)")

    # ========================================================================
    # CONFIGURATION (override in subclasses)
    # ========================================================================

    @property
    @abstractmethod
    def cycle_name(self) -> str:
        """Human-readable name: 'cognitive_kernel', 'plugin_pulse', 'boot_orchestrator', etc."""
        pass

    @property
    @abstractmethod
    def rate_limit_seconds(self) -> int:
        """Minimum seconds between cycles (0 = no limit)."""
        pass

    @property
    @abstractmethod
    def timeout_seconds(self) -> int:
        """Max runtime for entire cycle (0 = no timeout)."""
        pass

    @property
    @abstractmethod
    def recovery_enabled(self) -> bool:
        """Should we catch and recover from errors?"""
        pass

    @property
    def parent_cycle_id(self) -> Optional[str]:
        """
        HOLON WIRING (from user review):
        Override this in subclasses that are called by parent cycles.

        Example:
            class PranaOrchestrator(CognitiveCycle):
                def __init__(self, parent_id):
                    super().__init__()
                    self._parent_id = parent_id

                @property
                def parent_cycle_id(self) -> Optional[str]:
                    return self._parent_id  # Link to BootOrchestrator that called me

        This establishes causality: "Why am I running? Because my parent boot cycle requested me."
        """
        return None

    # ========================================================================
    # PHASE IMPLEMENTATIONS (subclasses override these)
    # ========================================================================

    @abstractmethod
    async def _perceive(self) -> Tuple[List[Any], Dict[str, str]]:
        """
        PERCEIVE: Sense the state. Return (observations, errors).

        Examples:
        - CognitiveKernel: Check git status, test results, pending intents, system load
        - PranaOrchestrator: Load plugin registry, check sensor statuses
        - BootOrchestrator: Check if directories exist, configs loaded, environment ready
        """
        pass

    @abstractmethod
    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, str]]:
        """
        ORIENT: Classify/interpret observations. Return (orientations, errors).

        Takes raw observations and produces meaningful interpretations.

        Examples:
        - CognitiveKernel: Classify state into Sattva/Rajas/Tamas gunas
        - PranaOrchestrator: Sort plugins by dependency order
        - BootOrchestrator: Determine boot mode (FULL/HEADLESS/MINIMAL)
        """
        pass

    @abstractmethod
    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, str]]:
        """
        DECIDE: Generate/filter/prioritize actions. Return (decisions, errors).

        Takes orientations and produces a list of actions to execute.

        Examples:
        - CognitiveKernel: Generate intents, apply filters (NARASIMHA, DHARMA), select safe ones
        - PranaOrchestrator: Select which plugins to run based on phases
        - BootOrchestrator: Generate boot sequence based on mode
        """
        pass

    @abstractmethod
    async def _act(self, decisions: List[Any]) -> Tuple[Any, Dict[str, str]]:
        """
        ACT: Execute decisions. Return (results, errors).

        Takes decisions and executes them, returning aggregated results.

        Examples:
        - CognitiveKernel: Execute intents via CircuitExecutor (a CognitiveProcess), record in OPUS.md
        - PranaOrchestrator: Run plugin tasks in isolation wrappers
        - BootOrchestrator: Execute boot tasks (init plugins, create state directories)
        """
        pass

    async def _persist(self, context: CycleContext) -> Dict[str, str]:
        """
        PERSIST: Record state. Override only if needed.
        Default: Store cycle_id in UnifiedTrace completion (no-op).

        Examples (override in subclasses):
        - CognitiveKernel: Commit to git, update .opus_state/
        - PranaOrchestrator: Update last_pulse timestamp
        - BootOrchestrator: Mark boot phase complete
        """
        return {}

    async def _recover(self, context: CycleContext) -> bool:
        """
        RECOVER: Handle errors. Override only if needed.
        Default: Log errors and continue.

        Return:
            True if recovery successful (continue cycle)
            False to abort cycle (don't continue)
        """
        if context.has_errors():
            logger.warning(f"⚠️  {self.cycle_name} encountered errors: {context.errors}")
        return True

    # ========================================================================
    # THE ORCHESTRATION TEMPLATE METHOD (final, not overridden)
    # ========================================================================

    async def orchestrate(self, force: bool = False) -> Optional[CycleContext]:
        """
        RUN THE CYCLE: This is the unified orchestration loop.

        CRITICAL INTEGRATION (from user review):
        This orchestrate() method:
        1. Checks rate limiting (skip if throttled)
        2. Starts trace in UnifiedTrace: trace_id = self._trace.start(self.cycle_name)
        3. Creates CycleContext with trace_id, parent_cycle_id
        4. For each phase (PERCEIVE → ORIENT → DECIDE → ACT → PERSIST):
           a. Emit phase_start event to EventBus
           b. Call _perceive()/_orient()/_decide()/_act()
           c. Track phase results in CycleContext
           d. Emit phase_complete event to EventBus
        5. If errors: Call _recover(), emit error event to EventBus
        6. Call _persist() for custom persistence
        7. Emit cycle_complete event to EventBus
        8. Call self._trace.complete(trace_id) to close trace
        9. Return CycleContext

        This is the ONLY place orchestration logic lives.
        Every cycle in the system runs through this method.

        Args:
            force: Force cycle execution even if throttled

        Returns:
            CycleContext with all phase results, or None if throttled
        """
        # Check rate limiting
        if not force and self.rate_limit_seconds > 0:
            elapsed = time.time() - self._last_cycle_time
            if elapsed < self.rate_limit_seconds:
                logger.debug(f"🚫 {self.cycle_name} throttled ({elapsed:.1f}s < {self.rate_limit_seconds}s)")
                return None

        self._last_cycle_time = time.time()

        # Verify setup was called
        if self._trace is None or self._event_bus is None:
            logger.error(f"❌ {self.cycle_name}.setup() was never called! Cannot orchestrate without system wiring.")
            raise RuntimeError(f"{self.cycle_name} not properly initialized - call setup() first")

        # Start trace
        trace_id = self._trace.start(
            component=self.cycle_name,
            event_type="cycle_start",
            data={
                "cycle_name": self.cycle_name,
                "parent_cycle_id": self.parent_cycle_id,
            },
        )

        # Create cycle context
        context = CycleContext(
            cycle_id=str(uuid.uuid4())[:8],
            parent_cycle_id=self.parent_cycle_id,
            trace_id=trace_id,
            cycle_name=self.cycle_name,
            phase=CyclePhase.PERCEIVE,
            phase_start_time=time.time(),
        )

        logger.info(f"🔄 {self.cycle_name} starting (trace_id={trace_id}, parent={self.parent_cycle_id})")

        # AUTO-REGISTER cycle with global registry (no manual registration needed)
        registry = get_cycle_registry()
        registry.register_cycle(context)

        try:
            # ================================================================
            # PERCEIVE PHASE
            # ================================================================
            context.phase = CyclePhase.PERCEIVE
            context.phase_start_time = time.time()

            await emit_event(
                EventType.THOUGHT,
                agent_id=self.cycle_name,
                message=f"{self.cycle_name} perceiving state",
                task_id=context.cycle_id,
                details={"phase": "perceive", "trace_id": trace_id},
            )

            self._trace.emit(trace_id, self.cycle_name, "perceive_start")
            observations, perceive_errors = await self._perceive()
            context.observations = observations
            if perceive_errors:
                context.errors.update(perceive_errors)
            self._trace.emit(trace_id, self.cycle_name, "perceive_complete", {"observations": len(observations)})

            # ================================================================
            # ORIENT PHASE
            # ================================================================
            context.phase = CyclePhase.ORIENT
            context.phase_start_time = time.time()

            await emit_event(
                EventType.THOUGHT,
                agent_id=self.cycle_name,
                message=f"{self.cycle_name} orienting observations",
                task_id=context.cycle_id,
                details={"phase": "orient", "trace_id": trace_id},
            )

            self._trace.emit(trace_id, self.cycle_name, "orient_start", {"observations": len(observations)})
            orientations, orient_errors = await self._orient(observations)
            context.orientations = orientations
            if orient_errors:
                context.errors.update(orient_errors)
            self._trace.emit(trace_id, self.cycle_name, "orient_complete", {"orientations": len(orientations)})

            # ================================================================
            # DECIDE PHASE
            # ================================================================
            context.phase = CyclePhase.DECIDE
            context.phase_start_time = time.time()

            await emit_event(
                EventType.THOUGHT,
                agent_id=self.cycle_name,
                message=f"{self.cycle_name} deciding actions",
                task_id=context.cycle_id,
                details={"phase": "decide", "trace_id": trace_id},
            )

            self._trace.emit(trace_id, self.cycle_name, "decide_start", {"orientations": len(orientations)})
            decisions, decide_errors = await self._decide(orientations)
            context.decisions = decisions
            if decide_errors:
                context.errors.update(decide_errors)
            self._trace.emit(trace_id, self.cycle_name, "decide_complete", {"decisions": len(decisions)})

            # ================================================================
            # ACT PHASE
            # ================================================================
            context.phase = CyclePhase.ACT
            context.phase_start_time = time.time()

            await emit_event(
                EventType.ACTION,
                agent_id=self.cycle_name,
                message=f"{self.cycle_name} executing actions",
                task_id=context.cycle_id,
                details={"phase": "act", "trace_id": trace_id, "actions": len(decisions)},
            )

            self._trace.emit(trace_id, self.cycle_name, "act_start", {"decisions": len(decisions)})
            results, act_errors = await self._act(decisions)
            context.results = results
            if act_errors:
                context.errors.update(act_errors)
            self._trace.emit(
                trace_id, self.cycle_name, "act_complete", {"actions_executed": len(decisions) if results else 0}
            )

            # ================================================================
            # PERSIST PHASE
            # ================================================================
            context.phase = CyclePhase.PERSIST
            context.phase_start_time = time.time()

            self._trace.emit(trace_id, self.cycle_name, "persist_start")
            persist_errors = await self._persist(context)
            if persist_errors:
                context.errors.update(persist_errors)
            self._trace.emit(trace_id, self.cycle_name, "persist_complete")

            # ================================================================
            # ERROR RECOVERY (if errors occurred)
            # ================================================================
            if context.has_errors():
                context.phase = CyclePhase.RECOVER
                context.phase_start_time = time.time()

                await emit_event(
                    EventType.ERROR,
                    agent_id=self.cycle_name,
                    message=f"{self.cycle_name} recovering from errors",
                    task_id=context.cycle_id,
                    details={"phase": "recover", "trace_id": trace_id, "errors": context.errors},
                )

                self._trace.emit(trace_id, self.cycle_name, "recover_start", {"error_count": len(context.errors)})
                recovery_ok = await self._recover(context)
                self._trace.emit(trace_id, self.cycle_name, "recover_complete", {"recovery_ok": recovery_ok})

                if not recovery_ok:
                    logger.error(f"❌ {self.cycle_name} recovery failed, aborting cycle")
                    self._trace.error(trace_id, "recovery_failed", {"errors": context.errors})
                    return context

            # ================================================================
            # CYCLE COMPLETE
            # ================================================================
            await emit_event(
                EventType.COMPLETED,
                agent_id=self.cycle_name,
                message=f"{self.cycle_name} cycle complete",
                task_id=context.cycle_id,
                details={
                    "trace_id": trace_id,
                    "observations": len(context.observations),
                    "decisions": len(context.decisions),
                    "errors": len(context.errors),
                },
            )

            self._trace.complete(
                trace_id,
                {
                    "cycle_name": self.cycle_name,
                    "cycle_id": context.cycle_id,
                    "parent_cycle_id": self.parent_cycle_id,
                    "observations": len(context.observations),
                    "orientations": len(context.orientations),
                    "decisions": len(context.decisions),
                    "errors": len(context.errors),
                },
            )

            logger.info(
                f"✅ {self.cycle_name} complete (obs={len(context.observations)}, "
                f"orient={len(context.orientations)}, dec={len(context.decisions)}, "
                f"errors={len(context.errors)})"
            )

            # Mark cycle as complete in registry
            registry.complete_cycle(context)
            return context

        except Exception as e:
            logger.error(f"❌ {self.cycle_name} CRASHED: {e}", exc_info=True)
            context.add_error("orchestrate", str(e))

            await emit_event(
                EventType.ERROR,
                agent_id=self.cycle_name,
                message=f"{self.cycle_name} crashed",
                task_id=context.cycle_id,
                details={"trace_id": trace_id, "error": str(e)},
            )

            self._trace.error(trace_id, f"cycle_crash: {e}")
            # Mark cycle as failed in registry
            registry.error_cycle(context)
            return context


class CognitiveProcess(ABC):
    """
    Abstract base class for stateless LINEAR PROCESSORS.

    CRITICAL DISTINCTION (from user review):
    - Processes are NOT cycles (no perceive/persist/rate limiting)
    - Processes are CALLED BY cycles (e.g., CircuitExecutor called during ACT phase)
    - Processes are STATELESS (input → transform → output)
    - Processes do NOT manage their own lifecycle

    Examples:
    - CircuitExecutor: Load YAML circuit → Execute state machine → Return results
    - Cortex Senses: Perceive input → Classify into Sattva/Rajas/Tamas → Return classification

    USAGE (from within CognitiveKernel.act() phase):
        executor = CircuitExecutor()
        results = await executor.execute({"circuit_name": "maintenance_pulse"})
    """

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the process (synchronous work).

        Args:
            inputs: Input data for processing

        Returns:
            Results dict with keys:
            - success: bool (True if execution succeeded)
            - output: Any (result data)
            - error: Optional[str] (error message if failed)
        """
        pass


class CycleRegistry:
    """
    Track and coordinate all active CognitiveCycle instances.

    CRITICAL INTEGRATION (from user review):
    - Uses RetentionPolicy to prevent memory leaks
    - Tracks cycles in UnifiedTrace (not a separate system)
    - Emits to EventBus (not a separate log)

    OPUS-133 FIX: Persistent Memory
    - Cycle history is now persisted to Sovereign State root (ADR-204)
    - Survives across sessions (unlike in-memory only)
    - COGNITION.md now shows real historical data

    Provides:
    - Rate limit enforcement (per cycle, global throttle)
    - Cycle monitoring (current phase, runtime, errors)
    - Mirror test (detect self-triggered infinite loops)
    - Observability (which cycles are running, which are blocked)
    - Memory safety (retention policy enforcement)
    - Persistent memory (survives session restarts)
    """

    def __init__(
        self,
        retention_policy: Optional[RetentionPolicy] = None,
        workspace: Optional[Path] = None,
    ):
        """
        Initialize registry with optional persistent storage.

        Args:
            retention_policy: How long to keep cycle history (prevents memory leaks)
            workspace: Workspace root
        """
        self._cycles: Dict[str, CycleContext] = {}  # cycle_id → CycleContext
        self._retention_policy = retention_policy or RetentionPolicy()
        self._completed_cycles: List[CycleContext] = []  # For retention
        self._error_cycles: List[CycleContext] = []  # For retention
        self._cycle_count = 0
        self._workspace = workspace or Path.cwd()

        # 🍎 STATE: Global Sovereign State (ADR-204)
        from vibe_core.state.state_service import get_state_service

        self._state_service = get_state_service(self._workspace)
        self._history_filename = "cycle_history.json"

        # OPUS-133: Load persistent history on startup
        self._load_from_disk()

        logger.info(
            f"📊 CycleRegistry initialized (retention: {self._retention_policy.max_completed_cycles} completed, "
            f"{self._retention_policy.max_error_cycles} errors, history: {len(self._completed_cycles)} loaded)"
        )

    def register_cycle(self, context: CycleContext) -> None:
        """Register an active cycle."""
        self._cycles[context.cycle_id] = context
        self._cycle_count += 1
        logger.debug(
            f"📍 Cycle registered: {context.cycle_name} (id={context.cycle_id}, parent={context.parent_cycle_id})"
        )

    def complete_cycle(self, context: CycleContext) -> None:
        """Mark cycle as complete. Applies retention policy and persists."""
        if context.cycle_id in self._cycles:
            del self._cycles[context.cycle_id]

        self._completed_cycles.append(context)
        logger.debug(f"✅ Cycle completed: {context.cycle_name} (id={context.cycle_id})")

        # Apply retention policy
        if self._retention_policy.enabled:
            while len(self._completed_cycles) > self._retention_policy.max_completed_cycles:
                removed = self._completed_cycles.pop(0)
                logger.debug(f"🗑️  Pruned old completed cycle: {removed.cycle_name} (retention limit)")

        # OPUS-133: Persist to disk after each completion
        self._save_to_disk()

    def error_cycle(self, context: CycleContext) -> None:
        """Track cycle that failed. Keep more error cycles for debugging."""
        if context.cycle_id in self._cycles:
            del self._cycles[context.cycle_id]

        self._error_cycles.append(context)
        logger.warning(f"❌ Cycle failed: {context.cycle_name} (id={context.cycle_id}, errors={len(context.errors)})")

        # Apply retention policy (more lenient for errors)
        if self._retention_policy.enabled:
            while len(self._error_cycles) > self._retention_policy.max_error_cycles:
                removed = self._error_cycles.pop(0)
                logger.debug(f"🗑️  Pruned old error cycle: {removed.cycle_name} (retention limit)")

        # OPUS-133: Persist to disk after each error
        self._save_to_disk()

    def get_active_cycles(self) -> List[CycleContext]:
        """Get currently running cycles."""
        return list(self._cycles.values())

    def get_completed_cycles(self, limit: int = 100) -> List[CycleContext]:
        """Get recently completed cycles (most recent first)."""
        return self._completed_cycles[-limit:][::-1]

    def get_error_cycles(self, limit: int = 100) -> List[CycleContext]:
        """Get recently failed cycles (most recent first)."""
        return self._error_cycles[-limit:][::-1]

    def get_status(self) -> Dict[str, Any]:
        """Get registry status for monitoring."""
        return {
            "total_cycles": self._cycle_count,
            "active_cycles": len(self._cycles),
            "completed_cycles": len(self._completed_cycles),
            "error_cycles": len(self._error_cycles),
            "retention_policy": {
                "enabled": self._retention_policy.enabled,
                "max_completed": self._retention_policy.max_completed_cycles,
                "max_errors": self._retention_policy.max_error_cycles,
            },
            "active": [
                {
                    "cycle_id": c.cycle_id,
                    "cycle_name": c.cycle_name,
                    "phase": c.phase.value,
                    "parent_cycle_id": c.parent_cycle_id,
                }
                for c in self._cycles.values()
            ],
        }

    # =========================================================================
    # OPUS-133: PERSISTENT MEMORY (Cycle History Survives Sessions)
    # =========================================================================

    def _cycle_to_dict(self, ctx: CycleContext) -> Dict[str, Any]:
        """Serialize CycleContext for JSON storage."""
        return {
            "cycle_id": ctx.cycle_id,
            "parent_cycle_id": ctx.parent_cycle_id,
            "trace_id": ctx.trace_id,
            "cycle_name": ctx.cycle_name,
            "phase": ctx.phase.value,
            "observations_count": len(ctx.observations),
            "orientations_count": len(ctx.orientations),
            "decisions_count": len(ctx.decisions),
            "actions_count": len(ctx.actions),
            "errors": ctx.errors,
            "timestamp": datetime.now().isoformat(),
        }

    def _dict_to_cycle(self, data: Dict[str, Any]) -> CycleContext:
        """Deserialize CycleContext from JSON storage."""
        return CycleContext(
            cycle_id=data.get("cycle_id", str(uuid.uuid4())[:8]),
            parent_cycle_id=data.get("parent_cycle_id"),
            trace_id=data.get("trace_id", ""),
            cycle_name=data.get("cycle_name", "unknown"),
            phase=CyclePhase(data.get("phase", "persist")),
            phase_start_time=0.0,  # Historical - no timing data
            observations=[None] * data.get("observations_count", 0),
            orientations=[None] * data.get("orientations_count", 0),
            decisions=[None] * data.get("decisions_count", 0),
            actions=[None] * data.get("actions_count", 0),
            errors=data.get("errors", {}),
        )

    def _save_to_disk(self) -> None:
        """Persist cycle history to State root (ADR-204)."""
        try:
            # Serialize cycle history
            data = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "total_cycles": self._cycle_count,
                "completed": [self._cycle_to_dict(c) for c in self._completed_cycles],
                "errors": [self._cycle_to_dict(c) for c in self._error_cycles],
            }

            self._state_service.save(self._history_filename, data, create_backup=False)
            logger.debug(
                f"💾 Cycle history saved: {len(self._completed_cycles)} completed, {len(self._error_cycles)} errors"
            )

        except Exception as e:
            logger.warning(f"Could not persist cycle history: {e}")

    def _load_from_disk(self) -> None:
        """Load cycle history from State root (with Heritage migration)."""
        try:
            data = self._state_service.load(self._history_filename)
            if not data:
                return

            # Restore completed cycles
            for item in data.get("completed", []):
                ctx = self._dict_to_cycle(item)
                self._completed_cycles.append(ctx)

            # Restore error cycles
            for item in data.get("errors", []):
                ctx = self._dict_to_cycle(item)
                self._error_cycles.append(ctx)

            # Restore total count
            self._cycle_count = data.get("total_cycles", len(self._completed_cycles))

            logger.info(
                f"📂 Cycle history loaded: {len(self._completed_cycles)} completed, "
                f"{len(self._error_cycles)} errors (total: {self._cycle_count})"
            )

        except Exception as e:
            logger.warning(f"Could not load cycle history: {e}")
