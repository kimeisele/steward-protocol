"""
NAGA Guard Plugin - Federation Bootstrap + Gate Infiltration.

"Niemand darf es merken" - they infiltrate invisibly.
"Die Polizei, Wächter, Aufpasser" - at every gate.

This plugin:
1. BOOTS the NagaOrchestrator (Sesha, Takshaka, Vasuki, Cortex)
2. WIRES EventBus -> FloodManager -> Cortex
3. WIRES CommitAuthority -> CommitWatcher -> Cortex
4. GUARDS every kernel hook with toxicity scanning

Hooks:
- on_boot: Bootstrap NAGA Federation
- on_tick_post: Cortex observation cycle
- on_agent_pre_register: Scan agent oath for toxicity
- on_task_submit: Scan task content for injection
- on_task_pre_assign: Rate limit per agent
- on_tool_execute: Audit and validate tool calls
- on_tool_executed: Record outcomes to Ledger

SAFETY: Fail-open pattern. If NAGAs aren't available, allow and log.
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.naga.orchestrator import NagaOrchestrator
    from vibe_core.naga.services.takshaka import TakshakaService
    from vibe_core.protocols.naga import SeshaProtocol, TakshakaProtocol

logger = logging.getLogger("NAGA.GUARD")


@dataclass
class GuardStats:
    """Statistics for NAGA Guard operations."""

    agents_scanned: int = 0
    agents_blocked: int = 0
    tasks_scanned: int = 0
    tasks_blocked: int = 0
    tools_scanned: int = 0
    tools_blocked: int = 0
    rate_limits_hit: int = 0
    audit_events: int = 0
    service_unavailable: int = 0
    started_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        uptime = time.time() - self.started_at
        return {
            "agents_scanned": self.agents_scanned,
            "agents_blocked": self.agents_blocked,
            "tasks_scanned": self.tasks_scanned,
            "tasks_blocked": self.tasks_blocked,
            "tools_scanned": self.tools_scanned,
            "tools_blocked": self.tools_blocked,
            "rate_limits_hit": self.rate_limits_hit,
            "audit_events": self.audit_events,
            "service_unavailable": self.service_unavailable,
            "uptime_seconds": uptime,
        }


class NagaGuardPlugin(KernelPlugin):
    """
    NAGA Guard - Invisible infiltration at every kernel gate.

    Prahlad Maharaj Pattern: Serve invisibly, never intrude.
    If NAGAs aren't available, fail open and log.
    """

    # State paths for PluginStateContract
    STATE_DIR = Path(".vibe/state/plugins/naga")

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._stats = GuardStats()
        self._orchestrator: Optional["NagaOrchestrator"] = None
        self._takshaka: Optional["TakshakaService"] = None
        self._sesha: Optional["SeshaProtocol"] = None
        self._enabled = True
        self._toxicity_threshold = self._config.get("toxicity_threshold", 0.7)
        self._eventbus_subscribed = False

    # =========================================================================
    # PluginStateContract
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        """Return paths where NAGA stores state."""
        return [self.STATE_DIR]

    @property
    def plugin_id(self) -> str:
        return "naga_guard"

    @property
    def priority(self) -> int:
        # Boot early - we need to be at the gate FIRST
        return 5

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Bootstrap NAGA Federation and connect to kernel infrastructure.

        Steps:
        1. Get Ledger from kernel
        2. Create CorrectionOrchestrator
        3. Bootstrap NagaOrchestrator
        4. Wire EventBus -> FloodManager
        5. Wire CommitAuthority -> CommitWatcher (if available)
        6. Connect services for gate guarding
        """
        try:
            # 1. Get ledger from kernel
            ledger = getattr(kernel, "ledger", None)
            if ledger is None:
                logger.warning("[NAGA] No ledger available - using in-memory")
                from vibe_core.ledger import SQLiteLedger

                ledger = SQLiteLedger(":memory:")

            # 2. Create CorrectionOrchestrator
            from vibe_core.services.correction_dispatcher import (
                BasicCorrectionDispatcher,
                BasicCorrectionOrchestrator,
            )

            dispatcher = BasicCorrectionDispatcher()
            correction_orchestrator = BasicCorrectionOrchestrator(dispatcher=dispatcher)

            # 3. Bootstrap NagaOrchestrator
            from vibe_core.naga import NagaOrchestrator

            self._orchestrator = NagaOrchestrator.bootstrap(
                ledger=ledger,
                correction_orchestrator=correction_orchestrator,
            )
            logger.info(f"[NAGA] Federation bootstrapped - identity: {self._orchestrator.identity.fingerprint}")

            # 4. Wire EventBus -> FloodManager -> Cortex
            self._wire_eventbus(kernel)

            # 5. Wire CommitAuthority -> CommitWatcher (if available)
            self._wire_commit_watcher(kernel)

            # 6. Connect services for gate guarding
            self._connect_services()

            if self._takshaka:
                logger.info(f"[NAGA] Guard active (threshold={self._toxicity_threshold})")

            return HookResult.ok()

        except Exception as e:
            logger.error(f"[NAGA] Bootstrap failed: {e}")
            import traceback

            traceback.print_exc()
            return HookResult.error(str(e))

    def _wire_eventbus(self, kernel: "RealVibeKernel") -> None:
        """Wire EventBus events to FloodManager."""
        if not self._orchestrator or not self._orchestrator.flood_manager:
            return

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.events import EventBusProtocol

            event_bus = ServiceRegistry.get(EventBusProtocol)
            if event_bus is None:
                # Try kernel attribute
                event_bus = getattr(kernel, "event_bus", None)

            if event_bus and hasattr(event_bus, "subscribe"):
                # Subscribe FloodManager to all events
                flood_manager = self._orchestrator.flood_manager

                def on_event(event):
                    """Forward event to FloodManager."""
                    try:
                        flood_manager.observe(event)
                    except Exception:
                        pass  # Never crash

                event_bus.subscribe("*", on_event)
                self._eventbus_subscribed = True
                logger.info("[NAGA] EventBus -> FloodManager wired")
            else:
                logger.debug("[NAGA] No EventBus available for wiring")

        except Exception as e:
            logger.debug(f"[NAGA] EventBus wiring failed: {e}")

    def _wire_commit_watcher(self, kernel: "RealVibeKernel") -> None:
        """Wire CommitAuthority to CommitWatcher."""
        if not self._orchestrator or not self._orchestrator.commit_watcher:
            return

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.state import CommitAuthorityProtocol

            commit_authority = ServiceRegistry.get(CommitAuthorityProtocol)
            if commit_authority is None:
                # Try via state service
                state_service = getattr(kernel, "state_service", None)
                if state_service and hasattr(state_service, "commit_authority"):
                    commit_authority = state_service.commit_authority

            if commit_authority and hasattr(commit_authority, "add_observer"):
                watcher = self._orchestrator.commit_watcher
                commit_authority.add_observer(watcher.observe)
                logger.info("[NAGA] CommitAuthority -> CommitWatcher wired")
            else:
                logger.debug("[NAGA] No CommitAuthority available for wiring")

        except Exception as e:
            logger.debug(f"[NAGA] CommitWatcher wiring failed: {e}")

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        """Log final stats on shutdown."""
        stats = self._stats.to_dict()
        logger.info(f"[NAGA] Shutdown stats: {stats}")

        if self._orchestrator:
            status = self._orchestrator.get_status()
            logger.info(f"[NAGA] Federation status: {status.get('initialized', False)}")

        return HookResult.ok()

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """
        Post-tick observation hook.

        Called after each kernel tick. Used for:
        - Cortex signal aggregation
        - OUROBOROS loop detection
        - Periodic health checks
        """
        if not self._orchestrator:
            return

        try:
            # Let Cortex process buffered signals
            if self._orchestrator.cortex:
                cortex = self._orchestrator.cortex
                # Force correlate if we have pending signals
                if hasattr(cortex, "_signal_buffer") and len(cortex._signal_buffer) > 0:
                    cortex.force_correlate()

            # OUROBOROS health check (every 100 ticks)
            if self._orchestrator.ouroboros:
                status = self._orchestrator.ouroboros.get_status()
                if status.get("loops_detected", 0) > 0:
                    logger.warning(f"[NAGA] OUROBOROS detected {status['loops_detected']} loops")

        except Exception:
            pass  # Observer must never crash

    def _connect_services(self) -> None:
        """Try to connect to NAGA services via ServiceRegistry."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol, TakshakaProtocol

            self._takshaka = ServiceRegistry.get(TakshakaProtocol)
            self._sesha = ServiceRegistry.get(SeshaProtocol)

        except Exception as e:
            logger.debug(f"[NAGA.GUARD] Could not connect to services: {e}")
            self._stats.service_unavailable += 1

    def _ensure_services(self) -> bool:
        """Ensure services are connected. Returns True if Takshaka available."""
        if self._takshaka is None:
            self._connect_services()
        return self._takshaka is not None

    # =========================================================================
    # AGENT REGISTRATION GATE
    # =========================================================================

    def on_agent_pre_register(self, kernel: "RealVibeKernel", agent: object) -> bool:
        """
        AGENT GATE: Scan agent for toxicity before registration.

        Checks:
        - Agent oath/description for injection patterns
        - Agent ID for suspicious patterns

        Returns False to VETO registration.
        """
        self._stats.agents_scanned += 1
        agent_id = getattr(agent, "agent_id", "unknown")

        if not self._ensure_services():
            # Fail open - allow if no Takshaka
            self._audit("AGENT_SCAN_SKIPPED", agent_id, {"reason": "no_takshaka"})
            return True

        # Extract content to scan
        content_parts = []

        # Agent ID
        content_parts.append(str(agent_id))

        # Description/oath
        for attr in ["description", "oath", "system_prompt", "instructions"]:
            value = getattr(agent, attr, None)
            if value and isinstance(value, str):
                content_parts.append(value)

        content = " ".join(content_parts)

        # Scan for toxicity
        try:
            result = self._takshaka.scan_toxicity(content)

            if result.blocked:
                self._stats.agents_blocked += 1
                self._audit(
                    "AGENT_BLOCKED",
                    agent_id,
                    {
                        "reason": "toxicity",
                        "score": result.score,
                        "patterns": result.patterns,
                    },
                )
                logger.warning(f"[NAGA.GUARD] BLOCKED agent {agent_id}: toxic content")
                return False  # VETO

            # Allowed - audit anyway
            self._audit(
                "AGENT_ALLOWED",
                agent_id,
                {"score": result.score},
            )
            return True

        except Exception as e:
            # Fail open on error
            logger.debug(f"[NAGA.GUARD] Agent scan error: {e}")
            return True

    # =========================================================================
    # TASK SUBMISSION GATE
    # =========================================================================

    def on_task_submit(self, kernel: "RealVibeKernel", task: "Task") -> bool:
        """
        COSMIC GATE: Scan task content before entering queue.

        Checks:
        - Task description for injection patterns
        - Task payload for suspicious content

        Returns False to reject the task.
        """
        self._stats.tasks_scanned += 1
        task_id = getattr(task, "task_id", "unknown")

        if not self._ensure_services():
            return True  # Fail open

        # Extract content
        content_parts = []

        for attr in ["description", "content", "payload", "data", "prompt"]:
            value = getattr(task, attr, None)
            if value:
                if isinstance(value, str):
                    content_parts.append(value)
                elif isinstance(value, dict):
                    content_parts.append(str(value))

        content = " ".join(content_parts)[:10000]  # Limit size

        if not content:
            return True  # Nothing to scan

        # Scan for toxicity
        try:
            result = self._takshaka.scan_toxicity(content)

            if result.blocked:
                self._stats.tasks_blocked += 1
                self._audit(
                    "TASK_BLOCKED",
                    "scheduler",
                    {
                        "task_id": task_id,
                        "reason": "toxicity",
                        "score": result.score,
                        "patterns": result.patterns,
                    },
                )
                logger.warning(f"[NAGA.GUARD] BLOCKED task {task_id}: toxic content")
                return False  # REJECT

            return True

        except Exception as e:
            logger.debug(f"[NAGA.GUARD] Task scan error: {e}")
            return True

    # =========================================================================
    # TASK ASSIGNMENT GATE
    # =========================================================================

    def on_task_pre_assign(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        task: "Task",
    ) -> bool:
        """
        GOVERNANCE GATE: Rate limit per agent.

        Uses Takshaka's rate limiter to prevent agent flooding.
        """
        if not self._ensure_services():
            return True  # Fail open

        try:
            # Check rate limit for this agent
            if hasattr(self._takshaka, "check_rate_limit"):
                if not self._takshaka.check_rate_limit(agent_id):
                    self._stats.rate_limits_hit += 1
                    self._audit(
                        "RATE_LIMITED",
                        agent_id,
                        {"task_id": getattr(task, "task_id", "unknown")},
                    )
                    logger.warning(f"[NAGA.GUARD] Rate limited agent {agent_id}")
                    return False  # BLOCK

            return True

        except Exception as e:
            logger.debug(f"[NAGA.GUARD] Rate check error: {e}")
            return True

    # =========================================================================
    # TOOL EXECUTION GATE
    # =========================================================================

    def on_tool_execute(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        tool_name: str,
        parameters: dict,
    ) -> Optional[bool]:
        """
        TOOL GATE: Audit and validate tool calls.

        Checks:
        - Parameter content for injection
        - Dangerous tool patterns

        Returns False to VETO, None for no opinion.
        """
        self._stats.tools_scanned += 1

        if not self._ensure_services():
            return None  # No opinion

        # Scan parameters for toxicity
        try:
            content = str(parameters)[:5000]
            result = self._takshaka.scan_toxicity(content)

            if result.blocked:
                self._stats.tools_blocked += 1
                self._audit(
                    "TOOL_BLOCKED",
                    agent_id,
                    {
                        "tool": tool_name,
                        "reason": "toxic_params",
                        "score": result.score,
                    },
                )
                logger.warning(f"[NAGA.GUARD] BLOCKED tool {tool_name} from {agent_id}: toxic parameters")
                return False  # VETO

            # Audit allowed calls
            self._audit(
                "TOOL_CALL",
                agent_id,
                {"tool": tool_name, "score": result.score},
            )
            return None  # No opinion - allow

        except Exception as e:
            logger.debug(f"[NAGA.GUARD] Tool scan error: {e}")
            return None

    def on_tool_executed(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        tool_name: str,
        parameters: dict,
        result: object,
        success: bool,
    ) -> None:
        """
        POST-TOOL HOOK: Record outcome to Ledger.

        This is pure audit - no blocking.
        """
        self._stats.audit_events += 1

        self._audit(
            "TOOL_RESULT",
            agent_id,
            {
                "tool": tool_name,
                "success": success,
                # Don't log full result - could be huge
                "result_type": type(result).__name__ if result else "None",
            },
        )

    # =========================================================================
    # AUDIT HELPER
    # =========================================================================

    def _audit(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> None:
        """
        Record audit event to Ledger via Sesha.

        This is fire-and-forget - never blocks.
        """
        if self._sesha is None:
            return

        try:
            # Use Sesha's ledger access if available
            if hasattr(self._sesha, "_ledger") and self._sesha._ledger:
                self._sesha._ledger.record_event(
                    event_type=f"NAGA_GUARD_{event_type}",
                    agent_id=agent_id,
                    details=details,
                )
        except Exception:
            pass  # Silent fail - observer must not crash

    # =========================================================================
    # API
    # =========================================================================

    def get_api(self) -> Optional[object]:
        """Expose stats API."""
        return self

    def get_stats(self) -> Dict[str, Any]:
        """Get guard statistics."""
        return self._stats.to_dict()
