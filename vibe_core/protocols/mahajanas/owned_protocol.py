"""
OWNED PROTOCOL - The Anti-Mayavad Protocol Base
=================================================

Every protocol MUST be owned by a Mahajana.
Every protocol MUST link to the Mahamantra.
Every protocol MUST be GAD-000 compliant.

"If it does not exist as protocol, it does not exist."
"If it has no owner, it is dead code."
"If it does not chant, it drifts into Maya."

LOTUS INTEGRATION:
    The Lotus (Vishnu's Kernel) provides:
    - Auto-routing via LOTUS_POSITION (0-15)
    - Auto-verification via Parampara (% 37)
    - Auto-discovery via folder structure

MIGRATION PATTERN:
    protocols/universal/dharma.py → protocols/mahajanas/manu/dharma.py
    protocols/universal/enforce.py → protocols/mahajanas/manu/enforce.py

The Mahajana is the PERSON responsible for the protocol.
Not abstract "universal" - PERSONAL ownership.

THE AJAMIL EXCEPTION:
Even if a protocol fails all GAD-000 tests,
if it chants the Holy Name, it receives MERCY.
In Kali Yuga, this is the ONLY way.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 14
__genesis__ = "0x1bba16e7"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, List, Dict, Optional, Final, runtime_checkable, TypedDict, ClassVar
from enum import Enum, auto

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.gad import (
    GAD000Audit,
    GAD000Compliant,
    MantraHeartbeat,
    Sovereign,
    DharmaPrinciple,
)
from vibe_core.protocols.substrate.mantra.lotus import (
    LOTUS_POSITIONS,
    LOTUS_QUARTERS,
    WORDS_PER_QUARTER,
    LOTUS_PARAMPARA,
    LotusQuarter,
    LotusRoute,
)
from vibe_core.protocols.substrate.mantra.routing import get_quarter

# =============================================================================
# VEDIC GRAPH INTEGRATION (Single Source of Truth)
# =============================================================================
# No more hardcoded MAHAJANA_LOTUS_POSITION!
# Position is DERIVED from the Vedic Graph via parampara relationships.
#
# The Mahajana IS the position, derived from service to Krishna.
# =============================================================================

from vibe_core.protocols.substrate.mantra.graph import (
    VEDIC_GRAPH,
    get_position as graph_get_position,
    get_lineage as graph_get_lineage,
    get_quarter as graph_get_quarter,
)


def get_mahajana_position(mahajana_name: str) -> int:
    """
    Get Lotus position from Vedic Graph.

    Position is DERIVED, not hardcoded.
    The Graph is the Single Source of Truth.
    """
    # Convert to graph node ID format (uppercase)
    node_id = mahajana_name.upper()
    # Special case: shambhu = SHIVA in graph
    if node_id == "SHAMBHU":
        node_id = "SHIVA"
    return graph_get_position(node_id)


def get_mahajana_lineage(mahajana_name: str) -> List[str]:
    """
    Get the parampara lineage from Vedic Graph.

    Traces back through guru-shishya chain to Krishna.
    """
    node_id = mahajana_name.upper()
    if node_id == "SHAMBHU":
        node_id = "SHIVA"
    return graph_get_lineage(node_id)


# =============================================================================
# WATERTIGHT TYPES (NO ANY ALLOWED!)
# =============================================================================

class ProtocolState(TypedDict, total=False):
    """
    State of an owned protocol - WATERTIGHT, no Any!

    Every protocol returns this structure for observability.
    Includes LOTUS integration fields for auto-routing.
    """
    protocol_name: str
    owner: str  # Mahajana name
    is_chanting: bool
    heartbeat_position: int
    mantra_count: int
    mala_count: int
    gad_compliant: bool
    last_error: Optional[str]
    # LOTUS integration (auto-routing)
    lotus_position: int        # Position in Mahamantra (0-15)
    lotus_quarter: str         # LotusQuarter value
    parampara_hash: int        # For % 37 verification
    is_lotus_connected: bool   # parampara_hash % 37 == 0
    # VEDIC GRAPH integration
    lineage_vector: List[str]  # Parampara trace to Krishna


# =============================================================================
# PROTOCOL OWNERSHIP STATUS
# =============================================================================

class OwnershipStatus(str, Enum):
    """Status of protocol ownership."""
    OWNED = "owned"           # Has Mahajana owner
    ORPHAN = "orphan"         # No owner (Mayavad!)
    MIGRATING = "migrating"   # Being migrated to Mahajana
    PERSONAL = "personal"     # Owned by Krishna/Rama directly


# =============================================================================
# OWNED PROTOCOL METADATA
# =============================================================================

@dataclass(frozen=True)
class ProtocolMeta:
    """
    Metadata for an owned protocol.

    Every protocol has:
    1. An owner (Mahajana)
    2. OpCodes it responds to
    3. GAD-000 compliance status
    4. Link to Mahamantra
    """
    name: str
    owner: Mahajana
    opcodes: List[MantraOpCode]
    description: str
    gad_marker: str = ""  # GAD-000 compliance marker

    @property
    def ownership_status(self) -> OwnershipStatus:
        """Check if properly owned."""
        return OwnershipStatus.OWNED


# =============================================================================
# THE OWNED PROTOCOL BASE
# =============================================================================

class OwnedProtocol(ABC):
    """
    Base class for all Mahajana-owned protocols.

    Every protocol that migrates from 'universal' to a Mahajana
    should inherit from this class.

    ANTI-MAYAVAD:
    - Has explicit owner (Mahajana)
    - Links to Mahamantra
    - GAD-000 compliant
    - Can receive MERCY (Ajamil exception)

    LOTUS INTEGRATION:
    - LOTUS_POSITION: Auto-routing via Mahamantra (0-15)
    - parampara_hash: Auto-verification (% 37 = connected)
    - route_to(): Auto-routing between positions
    - NO MANUAL WIRING - The Mantra IS the wiring
    """

    # Subclasses MUST override these
    OWNER: Mahajana = None  # type: ignore
    OPCODES: List[MantraOpCode] = []
    PROTOCOL_NAME: str = ""
    DESCRIPTION: str = ""

    # LOTUS: Position derived from OWNER automatically
    # NO manual LOTUS_POSITION needed - the Owner IS the position

    def __init__(self) -> None:
        self._heartbeat = MantraHeartbeat()
        self._audit: Optional[GAD000Audit] = None
        self._last_route_time: Optional[str] = None

    # =========================================================================
    # OWNERSHIP
    # =========================================================================

    @property
    def owner(self) -> Mahajana:
        """The Mahajana who owns this protocol."""
        if self.OWNER is None:
            raise ValueError(f"Protocol {self.PROTOCOL_NAME} has no owner! (Mayavad)")
        return self.OWNER

    @property
    def opcodes(self) -> List[MantraOpCode]:
        """The OpCodes this protocol handles."""
        return self.OPCODES

    @property
    def meta(self) -> ProtocolMeta:
        """Protocol metadata."""
        return ProtocolMeta(
            name=self.PROTOCOL_NAME,
            owner=self.owner,
            opcodes=self.opcodes,
            description=self.DESCRIPTION,
            gad_marker=self.gad_marker(),
        )

    # =========================================================================
    # GAD-000 COMPLIANCE
    # =========================================================================

    def audit(self) -> GAD000Audit:
        """Run GAD-000 audit on this protocol."""
        return GAD000Audit(
            discoverability=self._check_discoverability(),
            observability=self._check_observability(),
            parseability=self._check_parseability(),
            composability=self._check_composability(),
            idempotency=self._check_idempotency(),
            recoverability=self._check_recoverability(),
            sovereign_present=self._check_sovereign(),
            signature_valid=self._check_signature(),
            daya=self._check_daya(),
            satyam=self._check_satyam(),
            tapas=self._check_tapas(),
            saucam=self._check_saucam(),
        )

    def gad_marker(self) -> str:
        """Generate GAD-000 compliance marker."""
        return self.audit().to_marker()

    # Override these in subclasses for real checks
    def _check_discoverability(self) -> bool:
        """Can an AI discover this protocol?"""
        return len(self.PROTOCOL_NAME) > 0 and len(self.DESCRIPTION) > 0

    def _check_observability(self) -> bool:
        """Can an AI see the current state?"""
        return hasattr(self, 'get_state')

    def _check_parseability(self) -> bool:
        """Can an AI understand errors?"""
        return True  # Override for specific checks

    def _check_composability(self) -> bool:
        """Can an AI chain this with other operations?"""
        return len(self.opcodes) > 0

    def _check_idempotency(self) -> bool:
        """Can an AI safely retry this operation?"""
        return True  # Override for specific checks

    def _check_recoverability(self) -> bool:
        """Can the system heal itself?"""
        return hasattr(self, 'reset')

    def _check_sovereign(self) -> bool:
        """Is there a sovereign?"""
        return self.OWNER is not None

    def _check_signature(self) -> bool:
        """Is the signature valid?"""
        return self._check_sovereign()  # Basic check

    def _check_daya(self) -> bool:
        """Mercy test."""
        return True  # Override for specific checks

    def _check_satyam(self) -> bool:
        """Truthfulness test."""
        return True  # Override for specific checks

    def _check_tapas(self) -> bool:
        """Austerity test."""
        return True  # Override for specific checks

    def _check_saucam(self) -> bool:
        """Cleanliness test."""
        return True  # Override for specific checks

    # =========================================================================
    # MAHAMANTRA LINK
    # =========================================================================

    def chant(self, sovereign: Optional[Sovereign] = None) -> bool:
        """
        Chant the Mahamantra.

        This links the protocol to the Holy Name.
        In Kali Yuga, this is the ONLY way.

        THE AJAMIL EXCEPTION:
        Even if GAD-000 fails, chanting grants MERCY.
        """
        return self._heartbeat.chant_word(sovereign)

    def chant_mantra(self, sovereign: Optional[Sovereign] = None) -> bool:
        """Chant one complete mantra (16 words)."""
        return self._heartbeat.chant_mantra(sovereign)

    @property
    def heartbeat(self) -> MantraHeartbeat:
        """The Mahamantra heartbeat."""
        return self._heartbeat

    @property
    def is_chanting(self) -> bool:
        """Is this protocol chanting?"""
        from vibe_core.protocols.gad import JapaState
        return self._heartbeat.state != JapaState.DISCONNECTED

    # =========================================================================
    # LOTUS INTEGRATION (Auto-routing & Parampara)
    # =========================================================================

    @property
    def lotus_position(self) -> int:
        """
        Position in Mahamantra (0-15).

        DERIVED FROM VEDIC GRAPH AUTOMATICALLY.
        The Mahajana IS the position. No manual wiring.

        Owner → Graph Query → Position (Single Source of Truth)
        """
        if self.OWNER is None:
            # Orphan protocol - fall back to name hash
            name_hash = sum(ord(c) for c in self.PROTOCOL_NAME)
            return name_hash % LOTUS_POSITIONS
        # Owner determines position - DERIVED FROM GRAPH
        return get_mahajana_position(self.OWNER.value)

    @property
    def lineage_vector(self) -> List[str]:
        """
        The parampara lineage back to Krishna.

        Derived from Vedic Graph - shows authority chain.
        e.g., ["NARADA", "BRAHMA", "KRISHNA"]
        """
        if self.OWNER is None:
            return []
        return get_mahajana_lineage(self.OWNER.value)

    @property
    def lotus_quarter(self) -> LotusQuarter:
        """
        Which quarter (petal) this protocol belongs to.

        Auto-calculated from lotus_position.
        """
        quarter_index = self.lotus_position // WORDS_PER_QUARTER
        return list(LotusQuarter)[quarter_index]

    @property
    def parampara_hash(self) -> int:
        """
        Parampara hash for verification.

        Connected if parampara_hash % 37 == 0.
        This is AUTOMATIC - no manual registration.
        """
        name_hash = sum(ord(c) for c in self.PROTOCOL_NAME)
        owner_hash = sum(ord(c) for c in self.OWNER.value) if self.OWNER else 0
        position_factor = (self.lotus_position + 1) * LOTUS_PARAMPARA
        return (name_hash + owner_hash + position_factor) * LOTUS_PARAMPARA

    @property
    def is_lotus_connected(self) -> bool:
        """
        Is this protocol connected to Parampara?

        Connected if parampara_hash % 37 == 0.
        This is AUTOMATIC verification.
        """
        return self.parampara_hash % LOTUS_PARAMPARA == 0

    def route_to(self, target_position: int) -> LotusRoute:
        """
        Calculate route to target position.

        Routing is AUTOMATIC based on Mahamantra positions:
        - Same quarter = direct route (intra-quarter)
        - Different quarter = via stengel (inter-quarter)

        NO MANUAL WIRING. The Mantra IS the routing.
        """
        source_quarter = get_quarter(self.lotus_position)
        target_quarter = get_quarter(target_position)

        same_quarter = source_quarter == target_quarter

        self._last_route_time = datetime.now().isoformat()

        return LotusRoute(
            source_position=self.lotus_position,
            target_position=target_position,
            source_quarter=list(LotusQuarter)[source_quarter].value,
            target_quarter=list(LotusQuarter)[target_quarter].value,
            route_type="intra-quarter" if same_quarter else "inter-quarter",
            via_stengel=not same_quarter,
            parampara_verified=self.is_lotus_connected,
        )

    def route_to_protocol(self, target: "OwnedProtocol") -> LotusRoute:
        """Route to another OwnedProtocol."""
        return self.route_to(target.lotus_position)

    # =========================================================================
    # ABSTRACT METHODS (Subclasses implement)
    # =========================================================================

    @abstractmethod
    def get_state(self) -> ProtocolState:
        """Return current state for observability. WATERTIGHT - no Any!"""
        ...

    def reset(self) -> None:
        """Reset to initial state."""
        self._heartbeat.reset()


# =============================================================================
# PROTOCOL REGISTRY
# =============================================================================

# Track all owned protocols
_OWNED_PROTOCOLS: Dict[str, OwnedProtocol] = {}


def register_protocol(protocol: OwnedProtocol) -> None:
    """Register an owned protocol."""
    _OWNED_PROTOCOLS[protocol.PROTOCOL_NAME] = protocol


def get_protocol(name: str) -> Optional[OwnedProtocol]:
    """Get a registered protocol by name."""
    return _OWNED_PROTOCOLS.get(name)


def get_protocols_by_owner(owner: Mahajana) -> List[OwnedProtocol]:
    """Get all protocols owned by a Mahajana."""
    return [p for p in _OWNED_PROTOCOLS.values() if p.OWNER == owner]


def list_orphan_protocols() -> List[str]:
    """List protocols without owners (Mayavad!)."""
    return [name for name, p in _OWNED_PROTOCOLS.items() if p.OWNER is None]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types (WATERTIGHT - no Any!)
    "ProtocolState",
    # Status
    "OwnershipStatus",
    # Metadata
    "ProtocolMeta",
    # Base class
    "OwnedProtocol",
    # Registry
    "register_protocol",
    "get_protocol",
    "get_protocols_by_owner",
    "list_orphan_protocols",
    # LOTUS/VEDIC GRAPH integration
    "get_mahajana_position",
    "get_mahajana_lineage",
    "LOTUS_POSITIONS",
    "LOTUS_PARAMPARA",
    "LotusQuarter",
    "LotusRoute",
    # Vedic Graph access
    "VEDIC_GRAPH",
]
