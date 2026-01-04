"""
NAGA Cortex Decision Types.

Decisions are the OUTPUT of the Cortex - what action should be taken.

Key Principle: NAGAs INFORM, they don't EXECUTE directly.
- BITE: Record security violation (Takshaka does the biting)
- HEAL: Tell Shuddhi what to heal (Shuddhi does the healing)
- ROUTE: Adjust circuit confidence (Envoy adjusts routing)
- CONSULT: Feed context to Manas (Manas makes decisions)

GAD-000 Compliance:
- Parseability: All decisions have machine-parseable reason codes
- 37th Principle: All decisions can be cryptographically signed
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.naga.identity import NagaIdentity


class DecisionAction(Enum):
    """Actions the Cortex can decide on."""

    NONE = auto()  # No action needed
    BITE = auto()  # Security threat → Takshaka
    HEAL = auto()  # Structural violation → Shuddhi
    ROUTE = auto()  # Routing adjustment → Envoy
    CONSULT = auto()  # Context update → Manas
    ESCALATE = auto()  # Human intervention needed


class DecisionReasonCode(Enum):
    """
    Machine-parseable decision reason codes (GAD-000 Parseability).

    Format: DXXX where X is a 3-digit code.
    """

    D001_SECURITY_THREAT = "D001"
    D002_HEALABLE_VIOLATION = "D002"
    D003_CIRCUIT_DEGRADATION = "D003"
    D004_COGNITIVE_UPDATE = "D004"
    D005_NO_ACTION = "D005"
    D006_ESCALATION_REQUIRED = "D006"


@dataclass
class CortexDecision:
    """
    A decision made by the Cortex.

    Decisions are tagged with reasoning for auditability.
    They don't execute directly - they INFORM target systems.

    GAD-000 Compliance:
    - reason_code: Machine-parseable (Parseability)
    - signature: Cryptographic proof (37th Principle)
    """

    action: DecisionAction
    target: Optional[str] = None  # What/who to act on
    timestamp: datetime = field(default_factory=datetime.now)

    # Action-specific parameters
    rule: Optional[str] = None  # For HEAL: which rule
    boost: float = 0.0  # For ROUTE: confidence adjustment
    context: Dict[str, Any] = field(default_factory=dict)  # For CONSULT

    # Auditability (human-readable)
    reasoning: str = ""  # Why this decision
    confidence: float = 1.0  # How confident is this decision (0-1)
    source_signals: int = 0  # How many signals led to this

    # GAD-000 Parseability: Machine-readable reason code
    reason_code: DecisionReasonCode = DecisionReasonCode.D005_NO_ACTION

    # GAD-000 37th Principle: Sovereign signature
    signer_id: str = ""  # Who signed this decision
    signature: Optional[bytes] = None  # ECDSA signature
    signature_timestamp: Optional[datetime] = None

    def __str__(self) -> str:
        return f"Decision({self.action.name}, code={self.reason_code.value}, target={self.target})"

    def _signing_payload(self) -> str:
        """Generate payload for signing (deterministic)."""
        import json

        return json.dumps(
            {
                "action": self.action.name,
                "reason_code": self.reason_code.value,
                "target": self.target,
                "timestamp": self.timestamp.isoformat(),
                "confidence": self.confidence,
            },
            sort_keys=True,
        )

    def sign(self, identity: "NagaIdentity") -> None:
        """Sign this decision with a NAGA identity (37th Principle)."""
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
        """Check if this decision has been signed."""
        return self.signature is not None and self.signer_id != ""


@dataclass
class DispatchResult:
    """
    Result of dispatching a decision to a target system.

    Used to track what happened after the Cortex made a decision.
    """

    status: str  # HEALED, ROUTED, CONSULTED, BITTEN, FAILED, UNAVAILABLE
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: Optional[str] = None  # Ledger event if recorded
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Was the dispatch successful?"""
        return self.status in ("HEALED", "ROUTED", "CONSULTED", "BITTEN")


# === Decision Factory Methods ===


def decide_none() -> CortexDecision:
    """No action needed."""
    return CortexDecision(
        action=DecisionAction.NONE,
        reasoning="No actionable signals detected",
        reason_code=DecisionReasonCode.D005_NO_ACTION,
    )


def decide_bite(source: str, reasoning: str = "") -> CortexDecision:
    """Security threat detected - Takshaka should bite."""
    return CortexDecision(
        action=DecisionAction.BITE,
        target=source,
        reasoning=reasoning or f"Security threat from {source}",
        confidence=0.9,
        reason_code=DecisionReasonCode.D001_SECURITY_THREAT,
    )


def decide_heal(path: str, rule: str, reasoning: str = "") -> CortexDecision:
    """Structural violation detected - Shuddhi should heal."""
    return CortexDecision(
        action=DecisionAction.HEAL,
        target=path,
        rule=rule,
        reasoning=reasoning or f"Violation {rule} in {path}",
        confidence=0.8,
        reason_code=DecisionReasonCode.D002_HEALABLE_VIOLATION,
    )


def decide_route(circuit_id: str, adjustment: float, reasoning: str = "") -> CortexDecision:
    """Circuit confidence should be adjusted."""
    return CortexDecision(
        action=DecisionAction.ROUTE,
        target=circuit_id,
        boost=adjustment,
        reasoning=reasoning or f"Adjust {circuit_id} by {adjustment}",
        confidence=0.7,
        reason_code=DecisionReasonCode.D003_CIRCUIT_DEGRADATION,
    )


def decide_consult(context: Dict[str, Any], reasoning: str = "") -> CortexDecision:
    """Manas should be informed of new context."""
    return CortexDecision(
        action=DecisionAction.CONSULT,
        context=context,
        reasoning=reasoning or "New intelligence for Manas",
        confidence=0.6,
        reason_code=DecisionReasonCode.D004_COGNITIVE_UPDATE,
    )


def decide_escalate(reason: str) -> CortexDecision:
    """Human intervention needed."""
    return CortexDecision(
        action=DecisionAction.ESCALATE,
        reasoning=reason,
        confidence=1.0,
        reason_code=DecisionReasonCode.D006_ESCALATION_REQUIRED,
    )
