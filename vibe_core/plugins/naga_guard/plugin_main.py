"""
NAGA Guard Plugin - Invisible Gate Infiltration.

"Niemand darf es merken" - they infiltrate invisibly.
"Die Polizei, Wächter, Aufpasser" - at every gate.

This plugin implements NAGA infiltration at every kernel hook:
- on_agent_pre_register: Scan agent oath for toxicity
- on_task_submit: Scan task content for injection
- on_task_pre_assign: Rate limit per agent
- on_tool_execute: Audit and validate tool calls
- on_tool_executed: Record outcomes to Ledger

Uses ServiceRegistry to access NAGA services:
- TakshakaProtocol: Toxicity scanning, rate limiting
- SeshaProtocol: Audit logging to Ledger (via Sesha)

SAFETY: This plugin is LIGHTWEIGHT. All heavy analysis is async.
We never block the kernel. If NAGA services aren't available,
we fail open (allow) and log a warning.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.kernel_impl import RealVibeKernel
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

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._stats = GuardStats()
        self._takshaka: Optional["TakshakaService"] = None
        self._sesha: Optional["SeshaProtocol"] = None
        self._enabled = True
        self._toxicity_threshold = self._config.get("toxicity_threshold", 0.7)

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
        Initialize NAGA Guard - connect to NAGA services.

        If services aren't available yet, we'll try again on first use.
        This allows boot order flexibility.
        """
        self._connect_services()

        if self._takshaka:
            logger.info(f"[NAGA.GUARD] Initialized with Takshaka (threshold={self._toxicity_threshold})")
        else:
            logger.warning("[NAGA.GUARD] No Takshaka available - running in audit-only mode")

        return HookResult.ok()

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        """Log final stats on shutdown."""
        stats = self._stats.to_dict()
        logger.info(f"[NAGA.GUARD] Shutdown stats: {stats}")
        return HookResult.ok()

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
