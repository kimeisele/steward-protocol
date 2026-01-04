"""
NAGA Cortex - The Central Nervous System.

"Das Nervensystem, nicht das Gehirn"

The Cortex is the INTELLIGENCE HUB that:
1. AGGREGATES signals from FloodManager, CommitWatcher, StateProxy
2. CORRELATES patterns across multiple signal sources
3. DECIDES what action is needed
4. DISPATCHES to target systems (informing, not replacing)

Key Principles:
- NAGAs ENHANCE existing systems, they don't REPLACE them
- Manas still makes decisions (NAGAs inform with context)
- Shuddhi still heals (NAGAs tell it WHAT to heal)
- Envoy still routes (NAGAs adjust confidence)
- All actions logged to Sesha ledger for auditability

Usage:
    cortex = NagaCortex(naga_orchestrator)
    cortex.receive_signal(flood_signal)  # From FloodManager
    cortex.receive_signal(commit_signal)  # From CommitWatcher
    # Cortex auto-correlates and dispatches when threshold met
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Deque, Dict, List, Optional

from vibe_core.naga.cortex.decisions import (
    CortexDecision,
    DecisionAction,
    DispatchResult,
    decide_bite,
    decide_consult,
    decide_heal,
    decide_none,
    decide_route,
)
from vibe_core.naga.cortex.signals import (
    CommitSignal,
    CorrelatedContext,
    FloodSignal,
    NagaSignal,
    StateSignal,
)

if TYPE_CHECKING:
    from vibe_core.naga.orchestrator import NagaOrchestrator
    from vibe_core.protocols.naga import VajraViolation

logger = logging.getLogger("NAGA.CORTEX")


@dataclass
class CortexConfig:
    """Configuration for NagaCortex behavior."""

    enabled: bool = True
    signal_buffer_size: int = 100  # Max signals to buffer
    correlation_threshold: int = 3  # Min signals before correlating
    max_signal_age_seconds: float = 300.0  # Discard signals older than 5min
    auto_dispatch: bool = True  # Auto-dispatch decisions or queue them
    log_decisions: bool = True  # Log decisions to Sesha ledger

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CortexConfig":
        return cls(
            enabled=data.get("enabled", True),
            signal_buffer_size=data.get("signal_buffer_size", 100),
            correlation_threshold=data.get("correlation_threshold", 3),
            max_signal_age_seconds=data.get("max_signal_age_seconds", 300.0),
            auto_dispatch=data.get("auto_dispatch", True),
            log_decisions=data.get("log_decisions", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "signal_buffer_size": self.signal_buffer_size,
            "correlation_threshold": self.correlation_threshold,
            "max_signal_age_seconds": self.max_signal_age_seconds,
            "auto_dispatch": self.auto_dispatch,
            "log_decisions": self.log_decisions,
        }


@dataclass
class CortexStats:
    """Statistics for Cortex activity."""

    signals_received: int = 0
    signals_discarded_age: int = 0
    signals_discarded_overflow: int = 0
    correlations_performed: int = 0
    decisions_made: int = 0
    decisions_dispatched: int = 0
    decisions_by_action: Dict[str, int] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        uptime = (datetime.now() - self.started_at).total_seconds()
        return {
            "signals_received": self.signals_received,
            "signals_discarded_age": self.signals_discarded_age,
            "signals_discarded_overflow": self.signals_discarded_overflow,
            "correlations_performed": self.correlations_performed,
            "decisions_made": self.decisions_made,
            "decisions_dispatched": self.decisions_dispatched,
            "decisions_by_action": self.decisions_by_action,
            "uptime_seconds": uptime,
        }


class NagaCortex:
    """
    Central Nervous System of the NAGA Federation.

    Responsibilities:
    1. AGGREGATE signals from FloodManager, CommitWatcher, StateProxy
    2. CORRELATE patterns using Sesha, Vasuki, Takshaka intelligence
    3. DECIDE what action is needed
    4. DISPATCH to appropriate system (Envoy, Shuddhi, Manas)

    Design:
    - Signal buffer with bounded size (prevents memory leak)
    - Automatic age-based signal expiry
    - Priority-based decision making (Security > Healing > Routing > Consulting)
    - All decisions logged to Ledger for auditability
    """

    def __init__(
        self,
        naga_orchestrator: "NagaOrchestrator",
        config: Optional[CortexConfig] = None,
    ):
        self._orchestrator = naga_orchestrator
        self._config = config or CortexConfig()
        self._signal_buffer: Deque[NagaSignal] = deque(maxlen=self._config.signal_buffer_size)
        self._stats = CortexStats()
        self._decision_queue: List[CortexDecision] = []

        logger.info(f"[CORTEX] Initialized (threshold={self._config.correlation_threshold})")

    # =========================================================================
    # SIGNAL RECEPTION
    # =========================================================================

    def receive_signal(self, signal: NagaSignal) -> None:
        """
        Receive a signal from the NAGA network.

        Called by:
        - FloodManager when event analyzed
        - CommitWatcher when pattern detected
        - StateProxy when write validated/violated
        """
        if not self._config.enabled:
            return

        self._stats.signals_received += 1

        # Age check
        if signal.age_seconds > self._config.max_signal_age_seconds:
            self._stats.signals_discarded_age += 1
            return

        # Buffer (deque handles overflow automatically)
        old_len = len(self._signal_buffer)
        self._signal_buffer.append(signal)
        if len(self._signal_buffer) == old_len:  # Overflow occurred
            self._stats.signals_discarded_overflow += 1

        # Maybe correlate
        self._maybe_correlate()

    def receive_flood_signal(
        self,
        event_type: str,
        agent_id: Optional[str] = None,
        toxicity_score: float = 0.0,
        patterns: List[str] = None,
        raw_data: Dict[str, Any] = None,
    ) -> None:
        """Convenience method for FloodManager."""
        signal = FloodSignal(
            source_id="flood_manager",
            event_type=event_type,
            agent_id=agent_id,
            toxicity_score=toxicity_score,
            patterns_detected=tuple(patterns or []),
            raw_data=raw_data or {},
        )
        self.receive_signal(signal)

    def receive_commit_signal(
        self,
        pattern: str,
        commit_sha: str,
        files_changed: List[str] = None,
        severity: str = "INFO",
    ) -> None:
        """Convenience method for CommitWatcher."""
        signal = CommitSignal(
            source_id="commit_watcher",
            pattern=pattern,
            commit_sha=commit_sha,
            files_changed=tuple(files_changed or []),
            severity=severity,
        )
        self.receive_signal(signal)

    def receive_state_signal(
        self,
        operation: str,
        path: str,
        violation: bool = False,
        violation_reason: Optional[str] = None,
        dharma_principles: List[str] = None,
    ) -> None:
        """Convenience method for StateProxy."""
        signal = StateSignal(
            source_id="state_proxy",
            operation=operation,
            path=path,
            violation=violation,
            violation_reason=violation_reason,
            dharma_principles=tuple(dharma_principles or []),
        )
        self.receive_signal(signal)

    # =========================================================================
    # CORRELATION
    # =========================================================================

    def _maybe_correlate(self) -> None:
        """Correlate if buffer has enough signals."""
        if len(self._signal_buffer) < self._config.correlation_threshold:
            return

        # Prune old signals first
        self._prune_old_signals()

        if len(self._signal_buffer) < self._config.correlation_threshold:
            return

        # Perform correlation
        signals = list(self._signal_buffer)
        self._signal_buffer.clear()

        context = self.correlate(signals)
        self._stats.correlations_performed += 1

        # Make decision
        decision = self.decide(context)
        self._stats.decisions_made += 1

        action_name = decision.action.name
        self._stats.decisions_by_action[action_name] = self._stats.decisions_by_action.get(action_name, 0) + 1

        # Dispatch or queue
        if decision.action != DecisionAction.NONE:
            if self._config.auto_dispatch:
                self.dispatch(decision)
            else:
                self._decision_queue.append(decision)

    def _prune_old_signals(self) -> None:
        """Remove signals older than max age."""
        max_age = self._config.max_signal_age_seconds
        while self._signal_buffer:
            if self._signal_buffer[0].age_seconds > max_age:
                self._signal_buffer.popleft()
                self._stats.signals_discarded_age += 1
            else:
                break

    def correlate(self, signals: List[NagaSignal]) -> CorrelatedContext:
        """
        Correlate signals into unified context.

        Adds intelligence from the three NAGAs:
        - Sesha: Historical patterns
        - Takshaka: Active threats
        - Vasuki: Peer health
        """
        # Get NAGA intelligence
        sesha_patterns: List[str] = []
        takshaka_threats: List[Dict[str, Any]] = []
        vasuki_peer_health: Dict[str, Any] = {}

        if self._orchestrator.sesha:
            # Get recent patterns from Sesha
            status = self._orchestrator.sesha.get_status()
            if hasattr(status, "recent_patterns"):
                sesha_patterns = status.recent_patterns or []

        if self._orchestrator.takshaka:
            # Get active threats from Takshaka
            status = self._orchestrator.takshaka.get_status()
            if hasattr(status, "active_threats"):
                takshaka_threats = status.active_threats or []

        if self._orchestrator.vasuki:
            # Get peer health from Vasuki
            status = self._orchestrator.vasuki.get_status()
            if hasattr(status, "peer_health"):
                vasuki_peer_health = status.peer_health or {}

        return CorrelatedContext(
            signals=signals,
            sesha_patterns=sesha_patterns,
            takshaka_threats=takshaka_threats,
            vasuki_peer_health=vasuki_peer_health,
        )

    # =========================================================================
    # DECISION
    # =========================================================================

    def decide(self, context: CorrelatedContext) -> CortexDecision:
        """
        Determine what action is needed based on correlated context.

        Priority Order (Security first):
        1. BITE: Security threats → Takshaka
        2. HEAL: Structural violations → Shuddhi
        3. ROUTE: Circuit degradation → Envoy
        4. CONSULT: Cognitive update → Manas
        """
        # 1. Security threats → BITE
        if context.has_security_threat():
            source = context.get_threat_source() or "unknown"
            decision = decide_bite(
                source=source,
                reasoning=f"Security threat detected: {context.takshaka_threats}",
            )
            decision.source_signals = len(context.signals)
            logger.warning(f"[CORTEX] 🐍 BITE decision: {source}")
            return decision

        # 2. Structural violations → HEAL
        if context.has_healable_violation():
            details = context.get_violation_details()
            if details and details.get("path"):
                decision = decide_heal(
                    path=details["path"],
                    rule=details.get("rule", "unknown"),
                    reasoning="Healable violation detected",
                )
                decision.source_signals = len(context.signals)
                logger.info(f"[CORTEX] 🔧 HEAL decision: {details['path']}")
                return decision

        # 3. Routing degradation → ROUTE
        if context.has_circuit_drift():
            circuit = context.get_degraded_circuit()
            if circuit:
                decision = decide_route(
                    circuit_id=circuit,
                    adjustment=-0.2,  # Reduce confidence
                    reasoning="Circuit showing degradation",
                )
                decision.source_signals = len(context.signals)
                logger.info(f"[CORTEX] 📡 ROUTE decision: degrade {circuit}")
                return decision

        # 4. Cognitive context update → CONSULT
        if context.needs_cognitive_update():
            payload = context.get_cognitive_payload()
            decision = decide_consult(
                context=payload,
                reasoning="New intelligence available for Manas",
            )
            decision.source_signals = len(context.signals)
            logger.debug(f"[CORTEX] 🧠 CONSULT decision: {len(payload)} items")
            return decision

        # No action needed
        return decide_none()

    # =========================================================================
    # DISPATCH
    # =========================================================================

    def dispatch(self, decision: CortexDecision) -> DispatchResult:
        """
        Route decision to appropriate system.

        Note: NAGAs INFORM, they don't REPLACE.
        - BITE → Takshaka.bite()
        - HEAL → Shuddhi.purify() (via ServiceRegistry)
        - ROUTE → Envoy confidence adjustment
        - CONSULT → Manas context injection
        """
        self._stats.decisions_dispatched += 1

        # Log to ledger first (audit trail)
        if self._config.log_decisions:
            self._log_decision(decision)

        if decision.action == DecisionAction.BITE:
            return self._dispatch_to_takshaka(decision)
        elif decision.action == DecisionAction.HEAL:
            return self._dispatch_to_shuddhi(decision)
        elif decision.action == DecisionAction.ROUTE:
            return self._dispatch_to_envoy(decision)
        elif decision.action == DecisionAction.CONSULT:
            return self._dispatch_to_manas(decision)
        elif decision.action == DecisionAction.ESCALATE:
            return self._dispatch_escalation(decision)

        return DispatchResult(status="NONE")

    def _log_decision(self, decision: CortexDecision) -> None:
        """Log decision to Sesha ledger for auditability."""
        if self._orchestrator.sesha and hasattr(self._orchestrator.sesha, "_ledger"):
            try:
                self._orchestrator.sesha._ledger.record_event(
                    event_type="NAGA_CORTEX_DECISION",
                    agent_id="naga_cortex",
                    details={
                        "action": decision.action.name,
                        "target": decision.target,
                        "rule": decision.rule,
                        "reasoning": decision.reasoning,
                        "confidence": decision.confidence,
                        "source_signals": decision.source_signals,
                    },
                )
            except Exception as e:
                logger.debug(f"[CORTEX] Failed to log decision: {e}")

    def _dispatch_to_takshaka(self, decision: CortexDecision) -> DispatchResult:
        """Record security bite via Takshaka."""
        if not self._orchestrator.takshaka:
            return DispatchResult(status="UNAVAILABLE")

        try:
            from vibe_core.protocols.naga import VajraViolation

            violation = VajraViolation(
                violation_type="CORTEX_THREAT",
                source=decision.target or "unknown",
                details={
                    "reasoning": decision.reasoning,
                    "confidence": decision.confidence,
                },
            )
            event_id = self._orchestrator.takshaka.bite(violation)
            logger.warning(f"[CORTEX] 🐍 BITE executed: {event_id}")
            return DispatchResult(status="BITTEN", event_id=event_id)
        except Exception as e:
            logger.error(f"[CORTEX] BITE failed: {e}")
            return DispatchResult(status="FAILED", details={"error": str(e)})

    def _dispatch_to_shuddhi(self, decision: CortexDecision) -> DispatchResult:
        """Trigger targeted healing via Shuddhi."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.shuddhi import ShuddhiProtocol

            shuddhi = ServiceRegistry.get(ShuddhiProtocol)
            if not shuddhi:
                return DispatchResult(status="UNAVAILABLE")

            result = shuddhi.purify(
                file_path=Path(decision.target) if decision.target else None,
                rule_id=decision.rule or "unknown",
            )
            status = "HEALED" if getattr(result, "healed", False) else "FAILED"
            logger.info(f"[CORTEX] 🔧 HEAL executed: {status}")
            return DispatchResult(status=status)
        except Exception as e:
            logger.error(f"[CORTEX] HEAL failed: {e}")
            return DispatchResult(status="FAILED", details={"error": str(e)})

    def _dispatch_to_envoy(self, decision: CortexDecision) -> DispatchResult:
        """Adjust circuit confidence via Envoy/Router."""
        # This is informational - we log it, but Envoy manages its own routing
        # Future: Hook into LayeredRouter to actually adjust confidence
        logger.info(f"[CORTEX] 📡 ROUTE advisory: {decision.target} {decision.boost:+.2f}")
        return DispatchResult(
            status="ROUTED",
            details={
                "circuit": decision.target,
                "adjustment": decision.boost,
                "advisory": True,  # Envoy decides whether to apply
            },
        )

    def _dispatch_to_manas(self, decision: CortexDecision) -> DispatchResult:
        """Feed context to Manas."""
        # This is informational - Manas can query NAGA context via API
        logger.debug(f"[CORTEX] 🧠 CONSULT context ready: {len(decision.context)} items")
        return DispatchResult(
            status="CONSULTED",
            details={"context_size": len(decision.context)},
        )

    def _dispatch_escalation(self, decision: CortexDecision) -> DispatchResult:
        """Escalate to human intervention."""
        logger.warning(f"[CORTEX] 🚨 ESCALATION: {decision.reasoning}")
        return DispatchResult(
            status="ESCALATED",
            details={"reason": decision.reasoning},
        )

    # =========================================================================
    # API / STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get Cortex status and statistics."""
        return {
            "enabled": self._config.enabled,
            "signal_buffer_size": len(self._signal_buffer),
            "decision_queue_size": len(self._decision_queue),
            "config": self._config.to_dict(),
            "stats": self._stats.to_dict(),
        }

    def get_queued_decisions(self) -> List[CortexDecision]:
        """Get decisions waiting for manual dispatch."""
        return list(self._decision_queue)

    def dispatch_queued(self) -> List[DispatchResult]:
        """Dispatch all queued decisions."""
        results = []
        while self._decision_queue:
            decision = self._decision_queue.pop(0)
            result = self.dispatch(decision)
            results.append(result)
        return results

    def force_correlate(self) -> Optional[CortexDecision]:
        """Force correlation even if below threshold (for testing)."""
        if not self._signal_buffer:
            return None

        signals = list(self._signal_buffer)
        self._signal_buffer.clear()

        context = self.correlate(signals)
        decision = self.decide(context)

        if decision.action != DecisionAction.NONE and self._config.auto_dispatch:
            self.dispatch(decision)

        return decision
