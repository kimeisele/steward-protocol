"""
NAGA CORTEX Protocol - Das Nervensystem (Signal Aggregation Protocol)

The Cortex is the INTELLIGENCE HUB that:
1. AGGREGATES signals from FloodManager, CommitWatcher, StateProxy
2. CORRELATES patterns across multiple signal sources
3. PROVIDES context to MANAS (pull-based, not push)
4. LEARNS from MANAS feedback

CRITICAL PRINCIPLE: NAGAs INFORM, they don't CONTROL.
- MANAS decides WHEN to query NAGA context
- NAGA is DIENEND (Shesha), nicht BESTIMMEND
- Loose coupling via ServiceRegistry
- Optional: If no NAGA, MANAS works anyway

GAD-000 COMPLIANCE:
- 37th Principle: All NagaContext is cryptographically signed
- Parseability: Typed fields, no Dict[str, Any]
- Karma: Every access creates Ledger event
- Phoenix: Serializable for persistence
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from vibe_core.naga.identity import NagaIdentity


class ContextReasonCode(str, Enum):
    """Machine-parseable reason codes for context generation (GAD-000 Parseability)."""

    C001_THREAT_ACTIVE = "C001"  # Active security threat
    C002_ANOMALY_DETECTED = "C002"  # Behavioral anomaly
    C003_PATTERN_MATCH = "C003"  # Historical pattern match
    C004_ROUTINE_POLL = "C004"  # Routine context request
    C005_EMERGENCY = "C005"  # Emergency escalation


@dataclass
class ThreatSummary:
    """Typed summary of a security threat (replaces Dict[str, Any])."""

    threat_type: str  # "bite", "toxicity", "injection", etc.
    source: str  # Who/what is the threat source
    severity: float  # 0.0 (low) to 1.0 (critical)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_type": self.threat_type,
            "source": self.source,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DecisionSummary:
    """Typed summary of a Cortex decision (replaces Dict[str, Any])."""

    action: str  # BITE, HEAL, ROUTE, CONSULT, ESCALATE
    target: Optional[str]
    reason_code: str  # D001, D002, etc.
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "target": self.target,
            "reason_code": self.reason_code,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PeerHealthSummary:
    """Typed summary of peer health (replaces Dict[str, Any])."""

    peer_count: int = 0
    healthy_count: int = 0
    degraded_peers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peer_count": self.peer_count,
            "healthy_count": self.healthy_count,
            "degraded_peers": self.degraded_peers,
        }


@dataclass
class NagaContext:
    """
    Aggregated NAGA intelligence for MANAS consumption.

    GAD-000 COMPLIANCE:
    - 37th Principle: Cryptographically signed by Cortex
    - Parseability: Typed fields, reason codes, no Dict[str, Any]
    - Karma: Generated context creates Ledger event
    - Phoenix: Serializable for persistence

    PULL-BASED: MANAS queries this, NAGA doesn't push.
    """

    # === TYPED INTELLIGENCE (No Dict[str, Any]!) ===
    active_threats: List[ThreatSummary] = field(default_factory=list)
    recent_patterns: List[str] = field(default_factory=list)
    peer_health: PeerHealthSummary = field(default_factory=PeerHealthSummary)
    anomaly_count: int = 0
    anomaly_sources: List[str] = field(default_factory=list)
    recent_decisions: List[DecisionSummary] = field(default_factory=list)
    signal_count: int = 0

    # === GAD-000 PARSEABILITY ===
    reason_code: ContextReasonCode = ContextReasonCode.C004_ROUTINE_POLL
    generated_at: datetime = field(default_factory=datetime.utcnow)

    # === GAD-000 37th PRINCIPLE (Sovereign Signature) ===
    signer_id: str = ""
    signature: Optional[bytes] = None
    signature_timestamp: Optional[datetime] = None

    def _signing_payload(self) -> str:
        """Generate deterministic payload for signing."""
        import json

        return json.dumps(
            {
                "reason_code": self.reason_code.value,
                "signal_count": self.signal_count,
                "threat_count": len(self.active_threats),
                "anomaly_count": self.anomaly_count,
                "generated_at": self.generated_at.isoformat(),
            },
            sort_keys=True,
        )

    def sign(self, identity: "NagaIdentity") -> None:
        """Sign this context with a NAGA identity (37th Principle)."""
        payload = self._signing_payload()
        self.signature = identity.sign(payload.encode())
        self.signer_id = identity.agent_id
        self.signature_timestamp = datetime.now()

    def verify(self, identity: "NagaIdentity") -> bool:
        """Verify the signature against a NAGA identity."""
        if not self.signature:
            return False
        payload = self._signing_payload()
        return identity.verify(payload.encode(), self.signature)

    @property
    def is_signed(self) -> bool:
        """Check if this context has been signed."""
        return self.signature is not None and self.signer_id != ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for MANAS consumption."""
        import base64

        return {
            "active_threats": [t.to_dict() for t in self.active_threats],
            "recent_patterns": self.recent_patterns,
            "peer_health": self.peer_health.to_dict(),
            "anomaly_count": self.anomaly_count,
            "anomaly_sources": self.anomaly_sources,
            "recent_decisions": [d.to_dict() for d in self.recent_decisions],
            "signal_count": self.signal_count,
            "reason_code": self.reason_code.value,
            "generated_at": self.generated_at.isoformat(),
            "signer_id": self.signer_id,
            "is_signed": self.is_signed,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None,
        }


class FeedbackOutcome(str, Enum):
    """Typed outcomes for MANAS feedback (replaces str)."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class ManasFeedback:
    """
    Feedback from MANAS to NAGA Cortex for learning.

    GAD-000 COMPLIANCE:
    - Typed fields (no raw strings for outcome)
    - 37th Principle: Signed by MANAS
    - Karma: Recorded in Ledger

    Sent after intent execution to inform NAGA of outcomes.
    """

    intent_id: str
    intent_type: str
    outcome: FeedbackOutcome
    confidence_used: float
    naga_context_used: bool
    execution_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # === GAD-000 37th PRINCIPLE ===
    signer_id: str = ""
    signature: Optional[bytes] = None

    def _signing_payload(self) -> str:
        """Generate deterministic payload for signing."""
        import json

        return json.dumps(
            {
                "intent_id": self.intent_id,
                "intent_type": self.intent_type,
                "outcome": self.outcome.value,
                "timestamp": self.timestamp.isoformat(),
            },
            sort_keys=True,
        )

    def sign(self, identity: "NagaIdentity") -> None:
        """Sign this feedback."""
        payload = self._signing_payload()
        self.signature = identity.sign(payload.encode())
        self.signer_id = identity.agent_id

    @property
    def is_signed(self) -> bool:
        return self.signature is not None and self.signer_id != ""

    def to_dict(self) -> Dict[str, Any]:
        import base64

        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type,
            "outcome": self.outcome.value,
            "confidence_used": self.confidence_used,
            "naga_context_used": self.naga_context_used,
            "execution_ms": self.execution_ms,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "signer_id": self.signer_id,
            "is_signed": self.is_signed,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None,
        }


@runtime_checkable
class NagaCortexProtocol(Protocol):
    """
    NAGA Cortex - Das Nervensystem, nicht das Gehirn.

    The Cortex is the INTELLIGENCE HUB that:
    1. AGGREGATES signals from FloodManager, CommitWatcher, StateProxy
    2. CORRELATES patterns across multiple signal sources
    3. PROVIDES context to MANAS (pull-based, not push)
    4. LEARNS from MANAS feedback

    CRITICAL PRINCIPLE: NAGAs INFORM, they don't CONTROL.
    - MANAS decides WHEN to query NAGA context
    - NAGA is DIENEND (Shesha), nicht BESTIMMEND
    - Loose coupling via ServiceRegistry
    - Optional: If no NAGA, MANAS works anyway

    Integration:
        # In CognitiveKernel
        cortex = ServiceRegistry.get(NagaCortexProtocol)
        if cortex:
            context = cortex.get_context_for_manas()
            # Use in think() cycle
    """

    def get_context_for_manas(self) -> NagaContext:
        """
        Get aggregated NAGA intelligence for MANAS consumption.

        PULL-BASED: MANAS calls this when it needs context.
        Returns current state of all NAGA observations.

        Returns:
            NagaContext with aggregated intelligence
        """
        ...

    def receive_feedback(self, feedback: ManasFeedback) -> None:
        """
        Receive feedback from MANAS about intent outcomes.

        LEARNING LOOP: MANAS informs NAGA of what worked.
        Used to adjust signal weights and decision thresholds.

        Args:
            feedback: Outcome of intent execution
        """
        ...

    def is_available(self) -> bool:
        """Check if Cortex is active and ready."""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get Cortex statistics."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullNagaCortex:
    """No-op NagaCortex for when Cortex is unavailable."""

    def get_context_for_manas(self) -> NagaContext:
        return NagaContext()

    def receive_feedback(self, feedback: ManasFeedback) -> None:
        pass  # Silently ignore

    def is_available(self) -> bool:
        return False

    def get_stats(self) -> Dict[str, Any]:
        return {"available": False, "reason": "NagaCortex not initialized"}
