"""
NAGA Shared Types - The Foundation

Extracted from naga.py god file (2861 lines → fractal modules).

Contains:
- NagaType: The 7 members of NAGA Service Agency
- StatusDetails: Typed status metrics (no Dict[str, Any])
- NagaStatus: Service health status
- EventDict: Typed event structure (Sesha/Vasuki)
- ErrorContext: Typed error context (Prahlad)
- ManifestDict: Typed manifest structure (Kulika)

PROMPT.md: "Protocol statt konkrete Klassen"
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, TypedDict


class NagaType(str, Enum):
    """
    The NAGA Service Agency (NSA) - 7 Members.

    WICHTIG: "NAGA Service Agency" ist der NAME des Dienstes, nicht die RASSE.
    4 echte Nagas (🐍 Schlangen-Rasse) + 3 Personnel (andere Wesen).

    Mythological Hierarchy (Srimad Bhagavatam Canto 7):
    - Vishnu (Intent) → Narada (Messenger) → Prahlad (Governor)
    - Prahlad herrscht über die Nagas (post-Hiranyakashipu)
    """

    # ===== INFRASTRUCTURE LAYER - Echte Nagas (🐍 Schlangen-Rasse) =====

    # Original 3 (PROMPT.md Level 2)
    SESHA = "sesha"  # 🐍 Ananta Shesha - Vishnus Bett, trägt die Welten
    VASUKI = "vasuki"  # 🐍 Samudra Manthan Seil - Transformation
    TAKSHAKA = "takshaka"  # 🐍 König der Nagas - beißt erst, fragt später

    # Phase 9 Addition
    KALIYA = "kaliya"  # 🐍 Von Krishna bezwungen - Isolation, nicht Tod

    # ===== GOVERNANCE LAYER - Personnel (KEINE Nagas von Rasse) =====

    # Phase 9 Additions
    NARADA = "narada"  # 🎵 Deva-Rishi - Messenger zwischen Welten
    CHITRAGUPTA = "chitragupta"  # 📜 Yamas Assistent - himmlischer Buchhalter

    # Phase 10: Governor
    PRAHLAD = "prahlad"  # 👑 Daitya-Prinz - herrscht über die Nagas

    @property
    def is_infrastructure(self) -> bool:
        """True if this is a real Naga (serpent race) - infrastructure layer."""
        return self in (NagaType.SESHA, NagaType.VASUKI, NagaType.TAKSHAKA, NagaType.KALIYA)

    @property
    def is_governance(self) -> bool:
        """True if this is personnel (not a Naga by race) - governance layer."""
        return self in (NagaType.NARADA, NagaType.CHITRAGUPTA, NagaType.PRAHLAD)

    @property
    def symbol(self) -> str:
        """Get the appropriate emoji for this member."""
        if self == NagaType.PRAHLAD:
            return "👑"
        elif self == NagaType.NARADA:
            return "🎵"
        elif self == NagaType.CHITRAGUPTA:
            return "📜"
        else:
            return "🐍"

    @classmethod
    def infrastructure_members(cls) -> list["NagaType"]:
        """Get all infrastructure layer members (real Nagas)."""
        return [cls.SESHA, cls.VASUKI, cls.TAKSHAKA, cls.KALIYA]

    @classmethod
    def governance_members(cls) -> list["NagaType"]:
        """Get all governance layer members (personnel)."""
        return [cls.NARADA, cls.CHITRAGUPTA, cls.PRAHLAD]


class StatusDetails(TypedDict, total=False):
    """
    Typed status details - STAMBHA (The Pillar).

    Replaces Dict[str, Any] in NagaStatus to prevent status poisoning.
    Prahlad's DNA: Explicit metrics, no surprises.
    """

    # Performance metrics (bounded integers)
    queue_size: int
    processing_rate: float  # events/second
    latency_ms: float  # average latency

    # Health indicators
    last_error: str  # Max 200 chars
    degraded_reason: str  # Why degraded (if any)

    # Resource usage
    memory_mb: float
    connections: int


@dataclass
class NagaStatus:
    """
    Status of a NAGA service.

    HALAHALA HARDENED: Uses StatusDetails TypedDict instead of Dict[str, Any].
    """

    naga_type: NagaType
    healthy: bool = True
    last_heartbeat: Optional[datetime] = None
    events_processed: int = 0
    errors: int = 0
    message: str = ""
    details: StatusDetails = field(default_factory=lambda: StatusDetails())

    def to_dict(self) -> Dict[str, object]:
        """Serialize to dict. Returns Dict[str, object] not Dict[str, Any]."""
        return {
            "type": self.naga_type.value,
            "healthy": self.healthy,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "events_processed": self.events_processed,
            "errors": self.errors,
            "message": self.message,
            "details": dict(self.details),
        }


# =============================================================================
# KURUKSHETRA WEAPONS (TypedDicts to replace Any)
# =============================================================================


class EventDict(TypedDict, total=False):
    """
    Typed event structure for Sesha and Vasuki.
    Replaces Dict[str, Any].
    """

    event_type: str
    agent_id: str
    timestamp: str
    details: Dict[str, object]
    signature: Optional[str]
    sequence: int
    hash: str


class ErrorContext(TypedDict, total=False):
    """
    Typed error context for Prahlad.
    Replaces Dict[str, Any].
    """

    traceback: str
    locals: Dict[str, str]
    input_data: str
    user_id: str
    component: str
    severity: str


class ManifestDict(TypedDict, total=False):
    """
    Typed manifest structure for Kulika.
    Replaces Dict[str, Any].
    """

    name: str
    version: str
    author: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    config: Dict[str, object]
    varna: str
    ashrama: str