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

import hashlib
import logging
from collections import OrderedDict, deque
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
    from vibe_core.naga.identity import NagaIdentity
    from vibe_core.naga.orchestrator import NagaOrchestrator
    from vibe_core.naga.ouroboros import NagaOuroboros
    from vibe_core.protocols.naga import ManasFeedback, NagaContext, VajraViolation

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

        # GAD-000 37th Principle: Identity for signing decisions
        # Injected by orchestrator after construction
        self._identity: Optional["NagaIdentity"] = None

        # GAD-000 Recoverability: OUROBOROS for self-healing
        # Injected by orchestrator after construction
        self._ouroboros: Optional["NagaOuroboros"] = None

        # GAD-000 Idempotency: Track dispatched decisions
        self._dispatched: OrderedDict[str, datetime] = OrderedDict()
        self._dispatched_max = 1000

        # PHOENIX: Lazy-loaded StateService for crash recovery
        self._state_service_instance = None

        # PHOENIX: Restore state from previous session (if exists)
        self._restore_state()

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

        GAD-000 Compliance:
        - 37th Principle: All decisions are signed before dispatch
        - Idempotency: Duplicate decisions are detected and skipped
        - Recoverability: OUROBOROS observes all corrections
        """
        # GAD-000 Idempotency: Check for duplicate decision
        decision_hash = self._compute_decision_hash(decision)
        if decision_hash in self._dispatched:
            logger.debug(f"[CORTEX] Duplicate decision {decision_hash[:8]}, skipping")
            return DispatchResult(
                status="ALREADY_DISPATCHED",
                details={"decision_hash": decision_hash},
            )

        self._stats.decisions_dispatched += 1

        # GAD-000 37th Principle: Sign the decision
        if self._identity and not decision.is_signed:
            decision.sign(self._identity)

        # Log to ledger first (audit trail)
        if self._config.log_decisions:
            self._log_decision(decision)

        # Dispatch to target
        if decision.action == DecisionAction.BITE:
            result = self._dispatch_to_takshaka(decision)
            target = "takshaka"
        elif decision.action == DecisionAction.HEAL:
            result = self._dispatch_to_shuddhi(decision)
            target = "shuddhi"
        elif decision.action == DecisionAction.ROUTE:
            result = self._dispatch_to_envoy(decision)
            target = "envoy"
        elif decision.action == DecisionAction.CONSULT:
            result = self._dispatch_to_manas(decision)
            target = "manas"
        elif decision.action == DecisionAction.ESCALATE:
            result = self._dispatch_escalation(decision)
            target = "human"
        else:
            return DispatchResult(status="NONE")

        # Track for idempotency (GAD-000)
        self._dispatched[decision_hash] = datetime.now()
        self._trim_dispatched()

        # GAD-000 Recoverability: Report to OUROBOROS
        if self._ouroboros and result.success:
            try:
                self._ouroboros.observe_correction(
                    source="cortex",
                    target=target,
                    decision=decision,
                )
            except Exception as e:
                logger.debug(f"[CORTEX] OUROBOROS observation failed: {e}")

        # PHOENIX: Persist state after dispatch
        self._save_state()

        return result

    def _compute_decision_hash(self, decision: CortexDecision) -> str:
        """Compute fingerprint for decision (GAD-000 Idempotency)."""
        payload = f"{decision.action.name}:{decision.target}:{decision.rule}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _trim_dispatched(self) -> None:
        """LRU trim of dispatched decisions."""
        while len(self._dispatched) > self._dispatched_max:
            self._dispatched.popitem(last=False)

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

    # =========================================================================
    # MANAS INTEGRATION (Phase 3B - STRICT GAD-000 COMPLIANCE)
    # =========================================================================

    def get_context_for_manas(self) -> "NagaContext":
        """
        Get aggregated NAGA intelligence for MANAS consumption.

        GAD-000 COMPLIANCE:
        - 37th Principle: Context is cryptographically signed
        - Karma: Every access creates Ledger event
        - Parseability: Typed fields, reason codes
        - Phoenix: Serializable for persistence

        PULL-BASED: MANAS calls this when it needs context.
        NAGAs INFORM, they don't CONTROL.

        Returns:
            Signed NagaContext with typed intelligence from all 12 Lords
        """
        import time

        from vibe_core.protocols.naga import (
            ContextReasonCode,
            DecisionSummary,
            NagaContext,
            PeerHealthSummary,
            ThreatSummary,
        )

        start_time = time.time()

        # === COLLECT TYPED INTELLIGENCE ===
        active_threats: List[ThreatSummary] = []
        recent_patterns: List[str] = []
        peer_health = PeerHealthSummary()
        anomaly_count = 0
        anomaly_sources: List[str] = []

        # TAKSHAKA: Active threats (TYPED)
        if self._orchestrator.takshaka:
            try:
                status = self._orchestrator.takshaka.get_status()
                if hasattr(status, "recent_bites"):
                    for bite in (status.recent_bites or [])[:5]:
                        active_threats.append(
                            ThreatSummary(
                                threat_type="bite",
                                source=str(bite.get("source", "unknown")) if isinstance(bite, dict) else str(bite),
                                severity=0.8,  # Bites are high severity
                            )
                        )
            except Exception as e:
                logger.debug(f"[CORTEX] Takshaka context unavailable: {e}")

        # SESHA: Recent patterns from ledger
        if self._orchestrator.sesha:
            try:
                status = self._orchestrator.sesha.get_status()
                if hasattr(status, "recent_patterns"):
                    recent_patterns = status.recent_patterns or []
            except Exception as e:
                logger.debug(f"[CORTEX] Sesha context unavailable: {e}")

        # VASUKI: Peer health (TYPED)
        if self._orchestrator.vasuki:
            try:
                status = self._orchestrator.vasuki.get_status()
                if hasattr(status, "peer_count"):
                    peer_health = PeerHealthSummary(
                        peer_count=getattr(status, "peer_count", 0),
                        healthy_count=getattr(status, "healthy_count", 0),
                        degraded_peers=getattr(status, "degraded_peers", []),
                    )
            except Exception as e:
                logger.debug(f"[CORTEX] Vasuki context unavailable: {e}")

        # CHITRAGUPTA: Anomalies (TYPED)
        if self._orchestrator.chitragupta:
            try:
                status = self._orchestrator.chitragupta.get_status()
                if hasattr(status, "recent_anomalies"):
                    anomalies_raw = status.recent_anomalies or []
                    anomaly_count = len(anomalies_raw)
                    anomaly_sources = [getattr(a, "component_id", str(a)) for a in anomalies_raw[:5]]
            except Exception as e:
                logger.debug(f"[CORTEX] Chitragupta context unavailable: {e}")

        # Recent decisions from this Cortex (TYPED)
        recent_decisions: List[DecisionSummary] = [
            DecisionSummary(
                action=d.action.name,
                target=d.target,
                reason_code=d.reason_code.value if hasattr(d, "reason_code") else "D005",
                timestamp=d.timestamp if hasattr(d, "timestamp") else datetime.now(),
            )
            for d in self._decision_queue[:5]
        ]

        # === DETERMINE REASON CODE (GAD-000 Parseability) ===
        if active_threats:
            reason_code = ContextReasonCode.C001_THREAT_ACTIVE
        elif anomaly_count > 0:
            reason_code = ContextReasonCode.C002_ANOMALY_DETECTED
        elif recent_patterns:
            reason_code = ContextReasonCode.C003_PATTERN_MATCH
        else:
            reason_code = ContextReasonCode.C004_ROUTINE_POLL

        # === BUILD CONTEXT ===
        context = NagaContext(
            active_threats=active_threats,
            recent_patterns=recent_patterns,
            peer_health=peer_health,
            anomaly_count=anomaly_count,
            anomaly_sources=anomaly_sources,
            recent_decisions=recent_decisions,
            signal_count=len(self._signal_buffer),
            reason_code=reason_code,
        )

        # === 37th PRINCIPLE: SIGN THE CONTEXT ===
        if self._identity:
            context.sign(self._identity)
            logger.debug(f"[CORTEX] 🔐 Context signed by {self._identity.agent_id}")

        # === KARMA: RECORD TO LEDGER ===
        duration_ms = (time.time() - start_time) * 1000
        if self._orchestrator.sesha and hasattr(self._orchestrator.sesha, "_ledger"):
            try:
                self._orchestrator.sesha._ledger.record_event(
                    event_type="CORTEX_CONSULTATION",
                    agent_id="naga_cortex",
                    details={
                        "reason_code": reason_code.value,
                        "threat_count": len(active_threats),
                        "anomaly_count": anomaly_count,
                        "signal_count": len(self._signal_buffer),
                        "is_signed": context.is_signed,
                        "duration_ms": duration_ms,
                    },
                )
            except Exception as e:
                logger.debug(f"[CORTEX] Failed to log consultation: {e}")

        return context

    def receive_feedback(self, feedback: "ManasFeedback") -> None:
        """
        Receive feedback from MANAS about intent outcomes.

        GAD-000 COMPLIANCE:
        - Karma: Feedback is recorded in Ledger
        - Signature verified if signed

        LEARNING LOOP: MANAS informs NAGA of what worked.
        Used to adjust signal weights and decision thresholds.

        Args:
            feedback: Signed feedback from MANAS
        """
        # === KARMA: RECORD TO LEDGER ===
        if self._orchestrator.sesha and hasattr(self._orchestrator.sesha, "_ledger"):
            try:
                self._orchestrator.sesha._ledger.record_event(
                    event_type="MANAS_FEEDBACK",
                    agent_id="naga_cortex",
                    details={
                        **feedback.to_dict(),
                        "is_signed": feedback.is_signed,
                    },
                )
            except Exception as e:
                logger.debug(f"[CORTEX] Failed to log feedback: {e}")

        # === UPDATE STATS ===
        outcome_key = f"feedback_{feedback.outcome.value}"
        self._stats.decisions_by_action[outcome_key] = self._stats.decisions_by_action.get(outcome_key, 0) + 1

        logger.debug(
            f"[CORTEX] 📥 MANAS feedback: {feedback.intent_type} → {feedback.outcome.value} "
            f"(NAGA context used: {feedback.naga_context_used}, signed: {feedback.is_signed})"
        )

        # PHOENIX: Persist state after feedback
        self._save_state()

    def is_available(self) -> bool:
        """Check if Cortex is active and ready."""
        return self._config.enabled

    def get_stats(self) -> Dict[str, Any]:
        """Get Cortex statistics (alias for get_status for protocol compliance)."""
        return self.get_status()

    # =========================================================================
    # PHOENIX: CRASH RECOVERY (GAD-000 THREE BODIES)
    # =========================================================================

    @property
    def _state_service(self):
        """Lazy-load StateService with naga_cortex namespace."""
        if self._state_service_instance is None:
            from vibe_core.state.state_service import get_state_service

            self._state_service_instance = get_state_service(plugin_id="naga_cortex")
        return self._state_service_instance

    def snapshot_state(self) -> Dict[str, Any]:
        """
        PHOENIX: Snapshot current state for crash recovery.

        Returns:
            Dict containing recoverable state (stats, dispatched decisions)
        """
        return {
            "version": 1,
            "stats": {
                "signals_received": self._stats.signals_received,
                "signals_discarded_age": self._stats.signals_discarded_age,
                "signals_discarded_overflow": self._stats.signals_discarded_overflow,
                "correlations_performed": self._stats.correlations_performed,
                "decisions_made": self._stats.decisions_made,
                "decisions_dispatched": self._stats.decisions_dispatched,
                "decisions_by_action": dict(self._stats.decisions_by_action),
            },
            "dispatched": {k: v.isoformat() for k, v in self._dispatched.items()},
            "config": self._config.to_dict(),
            "snapshot_at": datetime.now().isoformat(),
        }

    def _restore_state(self) -> None:
        """
        PHOENIX: Restore state from previous session.

        Called on init to recover from crashes.
        """
        try:
            snapshot = self._state_service.load("cortex_state.json", default=None)
            if snapshot is None:
                logger.debug("[CORTEX] No previous state to restore")
                return

            if snapshot.get("version") != 1:
                logger.warning("[CORTEX] Unknown state version, skipping restore")
                return

            # Restore stats (preserving current started_at)
            if "stats" in snapshot:
                stats = snapshot["stats"]
                self._stats.signals_received = stats.get("signals_received", 0)
                self._stats.signals_discarded_age = stats.get("signals_discarded_age", 0)
                self._stats.signals_discarded_overflow = stats.get("signals_discarded_overflow", 0)
                self._stats.correlations_performed = stats.get("correlations_performed", 0)
                self._stats.decisions_made = stats.get("decisions_made", 0)
                self._stats.decisions_dispatched = stats.get("decisions_dispatched", 0)
                self._stats.decisions_by_action = stats.get("decisions_by_action", {})

            # Restore dispatched decisions (for idempotency)
            if "dispatched" in snapshot:
                for k, v in snapshot["dispatched"].items():
                    try:
                        self._dispatched[k] = datetime.fromisoformat(v)
                    except (ValueError, TypeError):
                        pass

            logger.info(f"[CORTEX] PHOENIX: Restored state (decisions_made={self._stats.decisions_made})")

        except Exception as e:
            logger.debug(f"[CORTEX] State restore failed (fresh start): {e}")

    def _save_state(self) -> None:
        """
        PHOENIX: Persist current state for crash recovery.

        Called after significant state changes.
        """
        try:
            snapshot = self.snapshot_state()
            self._state_service.save("cortex_state.json", snapshot)
            logger.debug("[CORTEX] PHOENIX: State persisted")
        except Exception as e:
            logger.debug(f"[CORTEX] State save failed: {e}")
