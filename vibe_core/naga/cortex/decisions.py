"""
NAGA Cortex Decision Types.

Decisions are the OUTPUT of the Cortex - what action should be taken.

Key Principle: NAGAs INFORM, they don't EXECUTE directly.
- BITE: Record security violation (Takshaka does the biting)
- HEAL: Tell Shuddhi what to heal (Shuddhi does the healing)
- ROUTE: Adjust circuit confidence (Envoy adjusts routing)
- CONSULT: Feed context to Manas (Manas makes decisions)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional


class DecisionAction(Enum):
    """Actions the Cortex can decide on."""

    NONE = auto()  # No action needed
    BITE = auto()  # Security threat → Takshaka
    HEAL = auto()  # Structural violation → Shuddhi
    ROUTE = auto()  # Routing adjustment → Envoy
    CONSULT = auto()  # Context update → Manas
    ESCALATE = auto()  # Human intervention needed


@dataclass
class CortexDecision:
    """
    A decision made by the Cortex.

    Decisions are tagged with reasoning for auditability.
    They don't execute directly - they INFORM target systems.
    """

    action: DecisionAction
    target: Optional[str] = None  # What/who to act on
    timestamp: datetime = field(default_factory=datetime.now)

    # Action-specific parameters
    rule: Optional[str] = None  # For HEAL: which rule
    boost: float = 0.0  # For ROUTE: confidence adjustment
    context: Dict[str, Any] = field(default_factory=dict)  # For CONSULT

    # Auditability
    reasoning: str = ""  # Why this decision
    confidence: float = 1.0  # How confident is this decision (0-1)
    source_signals: int = 0  # How many signals led to this

    def __str__(self) -> str:
        return f"Decision({self.action.name}, target={self.target}, confidence={self.confidence:.2f})"


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
    )


def decide_bite(source: str, reasoning: str = "") -> CortexDecision:
    """Security threat detected - Takshaka should bite."""
    return CortexDecision(
        action=DecisionAction.BITE,
        target=source,
        reasoning=reasoning or f"Security threat from {source}",
        confidence=0.9,
    )


def decide_heal(path: str, rule: str, reasoning: str = "") -> CortexDecision:
    """Structural violation detected - Shuddhi should heal."""
    return CortexDecision(
        action=DecisionAction.HEAL,
        target=path,
        rule=rule,
        reasoning=reasoning or f"Violation {rule} in {path}",
        confidence=0.8,
    )


def decide_route(circuit_id: str, adjustment: float, reasoning: str = "") -> CortexDecision:
    """Circuit confidence should be adjusted."""
    return CortexDecision(
        action=DecisionAction.ROUTE,
        target=circuit_id,
        boost=adjustment,
        reasoning=reasoning or f"Adjust {circuit_id} by {adjustment}",
        confidence=0.7,
    )


def decide_consult(context: Dict[str, Any], reasoning: str = "") -> CortexDecision:
    """Manas should be informed of new context."""
    return CortexDecision(
        action=DecisionAction.CONSULT,
        context=context,
        reasoning=reasoning or "New intelligence for Manas",
        confidence=0.6,
    )


def decide_escalate(reason: str) -> CortexDecision:
    """Human intervention needed."""
    return CortexDecision(
        action=DecisionAction.ESCALATE,
        reasoning=reason,
        confidence=1.0,
    )
