"""
NAGA INTERFACE GROUPS - Achintya Bhedabheda Pattern

"Krishna ist eins und verschieden."
- Qualitativ GLEICH (alle Protocol)
- Quantitativ VERSCHIEDEN (spezifische Rolle)

Each group is a gene family. Each NAGA inherits from its group.
This is the DNA that makes Any-fixes OBVIOUS.

GROUPS:
1. SECURITY  - intercept, bite, quarantine (Takshaka, Narasimha, Kaliya)
2. GOVERNANCE - audit, verify, approve (Prahlad, VedicGovernance)
3. DATA - read, write, sync (Sesha, Ledger)
4. TRANSFORM - analyze, transform (Ananta, Shuddhi, Vasuki)
5. OBSERVE - observe, record, report (Narada, Chitragupta, Cortex)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Protocol, runtime_checkable


# =============================================================================
# SHARED TYPES (Used across groups)
# =============================================================================


class Verdict(str, Enum):
    """Security verdict - used by SECURITY group."""
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"


@dataclass
class Subject:
    """What is being judged - used by SECURITY group."""
    subject_type: str  # "service", "agent", "request", "code"
    identifier: str
    context: str = ""


@dataclass
class AuditResult:
    """Result of governance audit - used by GOVERNANCE group."""
    passed: bool
    score: float  # 0.0 - 1.0
    violations: List[str]
    timestamp: datetime


@dataclass
class Observation:
    """What was observed - used by OBSERVE group."""
    event_type: str
    source: str
    timestamp: datetime
    data: str  # Serialized, not Dict[str, Any]!


@dataclass
class Analysis:
    """Result of analysis - used by TRANSFORM group."""
    target: str
    findings: List[str]
    suggested_action: str
    confidence: float  # 0.0 - 1.0


@dataclass
class TransformResult:
    """Result of transformation - used by TRANSFORM group."""
    success: bool
    before_hash: str
    after_hash: str
    changes: List[str]


# =============================================================================
# GROUP 1: SECURITY (Takshaka, Narasimha, Kaliya)
# =============================================================================


@runtime_checkable
class SecurityProtocol(Protocol):
    """
    Base protocol for all security NAGAs.

    Qualitatively: Can intercept, bite, quarantine
    Quantitatively: Different triggers, different responses
    """

    def intercept(self, subject: Subject) -> Verdict:
        """Judge a subject - ALLOW, DENY, ESCALATE, QUARANTINE."""
        ...

    def bite(self, subject: Subject, reason: str) -> None:
        """Record a violation (Takshaka's specialty)."""
        ...

    def is_quarantined(self, identifier: str) -> bool:
        """Check if target is in quarantine (Kaliya's specialty)."""
        ...


# =============================================================================
# GROUP 2: GOVERNANCE (Prahlad, VedicGovernance)
# =============================================================================


@runtime_checkable
class GovernanceProtocol(Protocol):
    """
    Base protocol for all governance NAGAs.

    Qualitatively: Can audit, verify, approve
    Quantitatively: Different rules, different domains
    """

    def audit(self, target: str) -> AuditResult:
        """Audit a target for compliance."""
        ...

    def verify(self, claim: str) -> bool:
        """Verify a claim is true."""
        ...

    def get_dharma_score(self) -> float:
        """Get overall dharma compliance score."""
        ...


# =============================================================================
# GROUP 3: DATA (Sesha, Ledger)
# =============================================================================


@runtime_checkable
class DataProtocol(Protocol):
    """
    Base protocol for all data NAGAs.

    Qualitatively: Can read, write, sync
    Quantitatively: Different storage, different guarantees
    """

    def get_hash(self) -> str:
        """Get current state hash."""
        ...

    def get_sequence(self) -> int:
        """Get current sequence number."""
        ...

    def is_synced(self) -> bool:
        """Check if data is synchronized."""
        ...


# =============================================================================
# GROUP 4: TRANSFORM (Ananta, Shuddhi, Vasuki)
# =============================================================================


@runtime_checkable
class TransformProtocol(Protocol):
    """
    Base protocol for all transformation NAGAs.

    Qualitatively: Can analyze, transform
    Quantitatively: Different transformations, different targets
    """

    def analyze(self, target: str) -> Analysis:
        """Analyze a target."""
        ...

    def can_transform(self, target: str) -> bool:
        """Check if transformation is possible."""
        ...

    def transform(self, target: str, strategy: str) -> TransformResult:
        """Transform a target using strategy."""
        ...


# =============================================================================
# GROUP 5: OBSERVE (Narada, Chitragupta, Cortex)
# =============================================================================


@runtime_checkable
class ObserveProtocol(Protocol):
    """
    Base protocol for all observation NAGAs.

    Qualitatively: Can observe, record, report
    Quantitatively: Different focus, different metrics
    """

    def observe(self, event_type: str, source: str, data: str) -> Observation:
        """Observe an event."""
        ...

    def get_observations(self, since: Optional[datetime] = None) -> List[Observation]:
        """Get recorded observations."""
        ...

    def get_observation_count(self) -> int:
        """Get total observation count."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "Verdict",
    "Subject",
    "AuditResult",
    "Observation",
    "Analysis",
    "TransformResult",
    # Groups
    "SecurityProtocol",
    "GovernanceProtocol",
    "DataProtocol",
    "TransformProtocol",
    "ObserveProtocol",
]
