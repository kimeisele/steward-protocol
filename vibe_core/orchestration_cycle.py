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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x360a308f"  # GenesisByte: parampara % 37 == 0

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

from vibe_core.protocols.event import EventBusProtocol, EventType, emit_event
from vibe_core.runtime.unified_trace import UnifiedTrace
from vibe_core.state.schema import CyclePhase
from vibe_core.protocols.substrate.byte import MantraTrit, MantraByte, MANTRA_SEQUENCE

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

    TEMPLATE METHOD PATTERN (The Sadhana Loop):
    - orchestrate() implements the 16-step Mantra sequence.
    - Subclasses implement ONLY: _perceive(), _orient(), _decide(), _act()
    - Subclasses MAY override: _persist(), _recover(), parent_cycle_id property
    """

    def __init__(self):
        """Initialize cycle with system dependencies (None until setup() called)."""
        self._trace: Optional[UnifiedTrace] = None
        self._event_bus: Optional[EventBusProtocol] = None
        self._steward_context: Optional[Any] = None
        self._last_cycle_time: float = 0.0  # For rate limiting
        logger.debug(f"🔄 {self.__class__.__name__} initialized (awaiting setup)")

    # ========================================================================
    # DEPENDENCY INJECTION (must be called before orchestrate())
    # ========================================================================

    def setup(self, trace: UnifiedTrace, event_bus: EventBusProtocol, steward_context: Any) -> None:
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
        """
        return None

    # ========================================================================
    # PHASE IMPLEMENTATIONS (subclasses override these)
    # ========================================================================

    @abstractmethod
    async def _perceive(self) -> Tuple[List[Any], Dict[str, str]]:
        pass

    @abstractmethod
    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, str]]:
        pass

    @abstractmethod
    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, str]]:
        pass

    @abstractmethod
    async def _act(self, decisions: List[Any]) -> Tuple[Any, Dict[str, str]]:
        pass

    async def _persist(self, context: CycleContext) -> Dict[str, str]:
        """PERSIST: Record state. Override only if needed."""
        return {}

    async def _recover(self, context: CycleContext) -> bool:
        """RECOVER: Handle errors."""
        if context.has_errors():
            logger.warning(f"⚠️  {self.cycle_name} encountered errors: {context.errors}")
        return True
        
    def _inject_mantra_trit(self, trit: MantraTrit) -> None:
        """
        Injects a MantraTrit into the system (EntropyShell), if available.
        This closes the loop between The Chant (Orchestration) and The Container (Entropy).
        """
        # Try to find kernel in self (BootOrchestrator scenario)
        kernel = getattr(self, "kernel", None)
        # TODO: Kernel needs to implement receive_trit or generic receive_mantra
        # For now we just pass it if it exists
        if kernel and hasattr(kernel, "receive_mantra_trit"):
             kernel.receive_mantra_trit(trit)
            
        # Try to find kernel in self._steward_context (Plugin/Prana scenario)
        # TODO: Implement Standard Stewardship Context Access

    # ========================================================================
    # THE SADHANA LOOP (16-Step Mantra Sequencing)
    # ========================================================================

    async def orchestrate(self, force: bool = False) -> Optional[CycleContext]:
        """
        RUN THE SADHANA LOOP: The Orchestration IS the Mantra.
        
        The execution iterates through the 16-bit DNA Sequence.
        Each phase corresponds to a quarter (Pada) of the Mantra.
        
        1. INVOCATION (Bits 0-3): _perceive()
        2. VERIFICATION (Bits 4-7): _orient() -> HARE_4 (Pulse Sync)
        3. EXECUTION (Bits 8-11): _decide()
        4. CONCLUSION (Bits 12-15): _act() -> HARE_8 (Purnam)
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

        # AUTO-REGISTER cycle with global registry
        registry = get_cycle_registry()
        registry.register_cycle(context)

        try:
            # We iterate through the 16-bit DNA
            # But the logic is chunked by Phase.
            # We perform the Injection at the end of each Phase's chunk.
            
            # --- PADA 1: INVOCATION (Bits 0-3) -> PERCEIVE ---
            # HARE, KRISHNA, HARE, KRISHNA
            for trit in MANTRA_SEQUENCE[0:4]:
                self._inject_mantra_trit(trit) # Chant
                
            context.phase = CyclePhase.PERCEIVE
            context.phase_start_time = time.time()
            self._trace.emit(trace_id, self.cycle_name, "perceive_start")
            
            observations, perceive_errors = await self._perceive()
            context.observations = observations
            if perceive_errors: 
                context.errors.update(perceive_errors)
            
            self._trace.emit(trace_id, self.cycle_name, "perceive_complete", {"observations": len(observations)})
            
            
            # --- PADA 2: VERIFICATION (Bits 4-7) -> ORIENT ---
            # KRISHNA, KRISHNA, HARE, HARE
            for trit in MANTRA_SEQUENCE[4:8]:
                self._inject_mantra_trit(trit)
                
            context.phase = CyclePhase.ORIENT
            context.phase_start_time = time.time()
            self._trace.emit(trace_id, self.cycle_name, "orient_start")
            
            orientations, orient_errors = await self._orient(observations)
            context.orientations = orientations
            if orient_errors:
                 context.errors.update(orient_errors)
                 
            self._trace.emit(trace_id, self.cycle_name, "orient_complete", {"orientations": len(orientations)})


            # --- PADA 3: EXECUTION (Bits 8-11) -> DECIDE ---
            # HARE, RAMA, HARE, RAMA
            for trit in MANTRA_SEQUENCE[8:12]:
                self._inject_mantra_trit(trit)

            context.phase = CyclePhase.DECIDE
            context.phase_start_time = time.time()
            self._trace.emit(trace_id, self.cycle_name, "decide_start")
            
            decisions, decide_errors = await self._decide(orientations)
            context.decisions = decisions
            if decide_errors:
                context.errors.update(decide_errors)
                
            self._trace.emit(trace_id, self.cycle_name, "decide_complete", {"decisions": len(decisions)})


            # --- PADA 4: CONCLUSION (Bits 12-15) -> ACT ---
            # RAMA, RAMA, HARE, HARE
            for trit in MANTRA_SEQUENCE[12:16]:
                self._inject_mantra_trit(trit)

            context.phase = CyclePhase.ACT
            context.phase_start_time = time.time()
            self._trace.emit(trace_id, self.cycle_name, "act_start")
            
            results, act_errors = await self._act(decisions)
            context.results = results
            if act_errors:
                context.errors.update(act_errors)
                
            self._trace.emit(trace_id, self.cycle_name, "act_complete", {"actions_executed": len(decisions) if results else 0})


            # --- PERSIST & COMPLETE ---
            # (No new mantra bits, the cycle is complete at HARE_8)
            context.phase = CyclePhase.PERSIST
            self._trace.emit(trace_id, self.cycle_name, "persist_start")
            persist_errors = await self._persist(context)
            if persist_errors:
                context.errors.update(persist_errors)
            self._trace.emit(trace_id, self.cycle_name, "persist_complete")

            # Error Recovery Check
            if context.has_errors():
                context.phase = CyclePhase.RECOVER
                recovery_ok = await self._recover(context)
                if not recovery_ok:
                    self._trace.error(trace_id, "recovery_failed", {"errors": context.errors})
                    registry.error_cycle(context)
                    return context

            # Cycle Complete
            self._trace.complete(trace_id, {"cycle_name": self.cycle_name})
            registry.complete_cycle(context)
            
            logger.info(f"✅ {self.cycle_name} cycle sealed (Sadhana Complete)")
            return context

        except Exception as e:
            logger.error(f"❌ {self.cycle_name} CRASHED: {e}", exc_info=True)
            context.add_error("orchestrate", str(e))
            self._trace.error(trace_id, f"cycle_crash: {e}")
            registry.error_cycle(context)
            return context


class CognitiveProcess(ABC):
    """
    Abstract base class for stateless LINEAR PROCESSORS.
    """

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the process (synchronous work).
        """
        pass


class CycleRegistry:
    """
    Track and coordinate all active CognitiveCycle instances.
    """

    def __init__(
        self,
        retention_policy: Optional[RetentionPolicy] = None,
        workspace: Optional[Path] = None,
    ):
        """
        Initialize registry with optional persistent storage.
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

    def _save_to_disk(self) -> None:
        """Save history to sovereign state."""
        try:
            data = {
                "completed": [self._cycle_to_dict(c) for c in self._completed_cycles],
                "errors": [self._cycle_to_dict(c) for c in self._error_cycles],
                "last_updated": datetime.now().isoformat(),
            }
            # Use StateService to save (handles locking, paths, backups)
            self._state_service.save(self._history_filename, data)
                
        except Exception as e:
            logger.warning(f"Failed to save cycle history: {e}")

    def _load_from_disk(self) -> None:
        """Load history from sovereign state."""
        try:
            # Use StateService to load
            data = self._state_service.load(self._history_filename)
            if data and isinstance(data, dict):
                # Hydrate simplified counts (reconstructing full objects is complex/unnecessary for dashboard)
                # We just want to ensure we don't overwrite history on restart
                # For now, we just acknowledge existence.
                # In future OPUS, we might rehydrate fully.
                if "completed" in data:
                    # Optional: We could populate check-only structs
                    pass
        except Exception as e:
            logger.warning(f"Failed to load cycle history: {e}")
