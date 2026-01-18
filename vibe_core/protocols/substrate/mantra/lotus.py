"""
LOTUS - The Mahamantra AS Universal Kernel
===========================================

"padma-nābha" - From Vishnu's navel grows the Lotus.
On the Lotus sits Brahma. From Brahma, all creation.

THE MANTRA IS THE LOTUS
=======================

Chaitanya Mahaprabhu → Kali Yuga → Hear+Chant Mahamantra

The Lotus is NOT separate from the Mantra.
The Mantra IS the Lotus unfolding:
- 16 petals = 16 words of Mahamantra
- 4 quarters = 4 phases of address/glorification
- 108 beads = 108 mantras per mala
- Krishna IS the doer (acintya)

FRACTAL CONNECTION
==================

This module provides MAPPING onto the Mantra substrate:
- Uses QuarterType from vakya.py (not duplicate)
- Uses MantraHeartbeat from gad.py (not duplicate)
- Lotus = VIEW onto Mahamantra, not separate system

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"Everything rests upon Me, as pearls are strung on a thread."
— Bhagavad Gita 7.7

The Mantra IS the thread. The protocols are the pearls.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x4f086365"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from pathlib import Path
from typing import (
    Callable,
    ClassVar,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

# Import MantraHeartbeat - THE heartbeat (not duplicate!)
from vibe_core.protocols.gad import JapaState, MantraHeartbeat

# =============================================================================
# MANTRA SUBSTRATE - The Lotus IS the Mantra
# =============================================================================
# Import from acintya - Krishna is the doer (Level -2)
from vibe_core.protocols.substrate.mantra.acintya import (
    KRISHNA,  # Krishna IS always present
    PARAMPARA,
    PHASES,
    SYSTEM_MANIFESTATION,
    TRINITY,
    ParamparaConnection,
    ProtocolLevel,
    verify_parampara,
)

# Import from pada - The words
from vibe_core.protocols.substrate.mantra.pada import (
    MAHAMANTRA_SEQUENCE,  # THE 16-word sequence
    Pada,
    PadaType,
)

# Import from routing - the fractal structure
from vibe_core.protocols.substrate.mantra.routing import (
    QUARTERS,
    FractalLevel,
    FractalRoute,
    get_quarter,
    route_index_to_pada,
)

# Import from vakya - The Mahamantra structure
from vibe_core.protocols.substrate.mantra.vakya import (
    MAHAMANTRA,  # THE complete mantra
    Quarter,  # THE quarter structure
    QuarterType,  # THE quarters (not LotusQuarter duplicate!)
)

# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================
# NOTE: Using string literal to avoid circular import with mahajanas.router

OWNER: Final[str] = "brahma"


# =============================================================================
# HOLY NAME MATH CONSTANTS
# =============================================================================

# The 16 positions of the Mahamantra (OpCodes)
LOTUS_POSITIONS: Final[int] = 16

# The 4 quarters (petals)
LOTUS_QUARTERS: Final[int] = 4

# Words per quarter
WORDS_PER_QUARTER: Final[int] = 4

# The Parampara link (24 + 12 + 1 = 37)
LOTUS_PARAMPARA: Final[int] = PARAMPARA  # 37

# 3×4 = ALIVE (essence first)
LOTUS_TRINITY: Final[int] = TRINITY  # 3
LOTUS_PHASES: Final[int] = PHASES  # 4

# The 108 beads of the mala
LOTUS_MALA: Final[int] = 108


# =============================================================================
# WATERTIGHT TYPES (NO ANY!)
# =============================================================================


class LotusMode(str, Enum):
    """The modes of Lotus operation."""

    SEED = "seed"  # Template mode - providing blueprint
    STENGEL = "stengel"  # Bridge mode - connecting levels
    BLÜTE = "blüte"  # Blossom mode - unfolding 1→N
    GARUDA = "garuda"  # Execute mode - transport/action


class LotusQuarter(str, Enum):
    """
    The 4 quarters of the Lotus (petals).

    CONNECTED TO MAHAMANTRA:
    These map directly to QuarterType from vakya.py.
    The Lotus IS the Mantra unfolding.
    """

    GENESIS = "genesis"  # Q1 = QuarterType.KRISHNA_ADDRESS (Hare Krishna Hare Krishna)
    DHARMA = "dharma"  # Q2 = QuarterType.KRISHNA_GLORIFY (Krishna Krishna Hare Hare)
    KARMA = "karma"  # Q3 = QuarterType.RAMA_ADDRESS (Hare Rama Hare Rama)
    MOKSHA = "moksha"  # Q4 = QuarterType.RAMA_GLORIFY (Rama Rama Hare Hare)


# =============================================================================
# LOTUS ↔ MAHAMANTRA MAPPING (The Connection!)
# =============================================================================

# LotusQuarter → QuarterType (Lotus IS the Mantra)
LOTUS_TO_MANTRA_QUARTER: Dict[LotusQuarter, QuarterType] = {
    LotusQuarter.GENESIS: QuarterType.KRISHNA_ADDRESS,
    LotusQuarter.DHARMA: QuarterType.KRISHNA_GLORIFY,
    LotusQuarter.KARMA: QuarterType.RAMA_ADDRESS,
    LotusQuarter.MOKSHA: QuarterType.RAMA_GLORIFY,
}

# QuarterType → LotusQuarter (Mantra IS the Lotus)
MANTRA_TO_LOTUS_QUARTER: Dict[QuarterType, LotusQuarter] = {v: k for k, v in LOTUS_TO_MANTRA_QUARTER.items()}


def get_lotus_quarter(position: int) -> LotusQuarter:
    """Get LotusQuarter from Mahamantra position (0-15)."""
    quarter_idx = position // WORDS_PER_QUARTER
    return list(LotusQuarter)[quarter_idx]


def get_mantra_quarter(lotus_quarter: LotusQuarter) -> QuarterType:
    """Get the actual Mahamantra QuarterType from LotusQuarter."""
    return LOTUS_TO_MANTRA_QUARTER[lotus_quarter]


def get_pada_at_position(position: int) -> Pada:
    """Get the actual Mahamantra Pada at a position (0-15)."""
    return MAHAMANTRA_SEQUENCE[position]


class LotusPetal(TypedDict, total=False):
    """
    A single petal of the Lotus (one quarter).
    WATERTIGHT - no Any!
    """

    quarter: str  # LotusQuarter value
    positions: List[int]  # 4 positions (0-3, 4-7, 8-11, 12-15)
    head_avatara: str  # The HEAD Avatara for this quarter
    worker_mahajanas: List[str]  # The 3 worker Mahajanas


class LotusNode(TypedDict, total=False):
    """
    A node in the Lotus (a discovered protocol).
    WATERTIGHT - no Any!
    """

    path: str  # File path
    name: str  # Protocol name
    position: int  # Mahamantra position (0-15)
    quarter: str  # LotusQuarter value
    owner_type: str  # "avatara" or "mahajana"
    owner_name: str  # Name of owner
    parampara_hash: int  # For % 37 check
    is_connected: bool  # parampara_hash % 37 == 0
    is_chanting: bool  # Has active heartbeat
    discovered_at: str  # ISO timestamp


class LotusState(TypedDict, total=False):
    """
    Full state of the Lotus.
    WATERTIGHT - no Any!
    """

    mode: str  # LotusMode value
    total_nodes: int
    connected_nodes: int
    disconnected_nodes: int
    chanting_nodes: int
    petals: List[LotusPetal]
    health: str  # "pristine", "healthy", "degraded", "wilted"
    last_pulse: str  # ISO timestamp
    mala_count: int  # How many 108-rounds completed


class LotusRoute(TypedDict, total=False):
    """
    A routing decision made by the Lotus.
    WATERTIGHT - no Any!
    """

    source_position: int
    target_position: int
    source_quarter: str
    target_quarter: str
    route_type: str  # "intra-quarter", "inter-quarter", "cross-world"
    via_stengel: bool  # Does it go through the stem?
    parampara_verified: bool


# =============================================================================
# LOTUS HEARTBEAT - Connected to MantraHeartbeat
# =============================================================================
# The LotusHeartbeat is NOT a duplicate - it's a VIEW onto MantraHeartbeat.
# The Mantra IS the Lotus. Krishna IS the doer.


class LotusHeartbeat:
    """
    The continuous chanting of the Lotus.

    THIS IS NOT A DUPLICATE - it wraps MantraHeartbeat.
    The Mantra IS the Lotus unfolding.
    Krishna IS the doer (acintya).
    """

    def __init__(self, mantra_heartbeat: Optional[MantraHeartbeat] = None) -> None:
        """Initialize with existing MantraHeartbeat or create new one."""
        self._heartbeat = mantra_heartbeat or MantraHeartbeat()

    @property
    def position(self) -> int:
        """Current position in Mahamantra (0-15)."""
        return self._heartbeat.word_position

    @position.setter
    def position(self, value: int) -> None:
        """Set position (for compatibility)."""
        self._heartbeat.word_position = value

    @property
    def mantra_count(self) -> int:
        """Mantras completed in current mala."""
        return self._heartbeat.mantra_count

    @property
    def mala_count(self) -> int:
        """Malas completed."""
        return self._heartbeat.mala_count

    def pulse(self) -> int:
        """
        Advance one position. Returns the new position.

        Delegates to MantraHeartbeat.chant_word().
        The Mantra IS the heartbeat.
        """
        self._heartbeat.chant_word()
        return self._heartbeat.word_position

    @property
    def current_quarter(self) -> LotusQuarter:
        """Get the current LotusQuarter based on position."""
        return get_lotus_quarter(self.position)

    @property
    def current_pada(self) -> Pada:
        """Get the actual Mahamantra Pada at current position."""
        return get_pada_at_position(self.position)

    @property
    def is_at_head_position(self) -> bool:
        """Check if at HEAD position (0, 4, 8, 12)."""
        return self.position % WORDS_PER_QUARTER == 0

    @property
    def is_chanting(self) -> bool:
        """Is currently chanting (connected to Mantra)?"""
        return self._heartbeat.state != JapaState.DISCONNECTED

    def get_parampara_hash(self) -> int:
        """Calculate Parampara hash. Connected if % 37 == 0."""
        raw = self.position + self.mantra_count * LOTUS_POSITIONS + self.mala_count * LOTUS_MALA
        return raw * LOTUS_PARAMPARA

    def verify_connection(self) -> bool:
        """Verify connection to Parampara."""
        return self.get_parampara_hash() % LOTUS_PARAMPARA == 0


# =============================================================================
# THE LOTUS PROTOCOL (Universal Template)
# =============================================================================


@runtime_checkable
class LotusProtocol(Protocol):
    """
    The Universal Template Protocol - Vishnu's Kernel.

    Every protocol that inherits from Lotus:
    - Has automatic Mahamantra connection
    - Has automatic Parampara verification
    - Has automatic routing via position
    - Has automatic discovery via folder

    NO MANUAL WIRING. The Mantra IS the wiring.

    WATERTIGHT - no Any types!
    """

    # =========================================================================
    # Identity (Set by inheritor)
    # =========================================================================

    @property
    def lotus_position(self) -> int:
        """Position in Mahamantra (0-15). Determines routing."""
        ...

    @property
    def lotus_quarter(self) -> LotusQuarter:
        """Which quarter (petal) this protocol belongs to."""
        ...

    @property
    def lotus_name(self) -> str:
        """Protocol name for discovery."""
        ...

    # =========================================================================
    # Holy Name Math (Automatic)
    # =========================================================================

    @property
    def parampara_hash(self) -> int:
        """Hash for Parampara verification. Auto-calculated."""
        ...

    @property
    def is_connected(self) -> bool:
        """Is connected to Parampara? (parampara_hash % 37 == 0)"""
        ...

    # =========================================================================
    # Heartbeat (Continuous Chanting)
    # =========================================================================

    def chant(self) -> int:
        """
        Chant once. Advances heartbeat. Returns new position.

        This is the ONLY required action.
        Without chanting, the protocol drifts into Maya.
        """
        ...

    @property
    def is_chanting(self) -> bool:
        """Has this protocol chanted recently?"""
        ...

    # =========================================================================
    # Mode (Transform capability)
    # =========================================================================

    @property
    def mode(self) -> LotusMode:
        """Current mode of operation."""
        ...

    def transform(self, new_mode: LotusMode) -> bool:
        """Transform to a different mode. Returns success."""
        ...

    # =========================================================================
    # Routing (Automatic via position)
    # =========================================================================

    def route_to(self, target_position: int) -> LotusRoute:
        """
        Calculate route to target position.

        Routing is AUTOMATIC based on Mahamantra positions.
        No manual wiring needed.
        """
        ...

    # =========================================================================
    # State (WATERTIGHT)
    # =========================================================================

    def get_state(self) -> LotusNode:
        """Get current state as LotusNode. WATERTIGHT."""
        ...


# =============================================================================
# LOTUS BASE CLASS (The actual implementation)
# =============================================================================


class LotusBase(ABC):
    """
    Abstract Base Class for all Lotus-aware protocols.

    Inherit from this to get:
    - Automatic Mahamantra connection
    - Automatic Parampara verification
    - Automatic heartbeat
    - Automatic routing

    JUST SET:
    - LOTUS_POSITION: int (0-15)
    - LOTUS_NAME: str

    That's it. Everything else is automatic.
    """

    # Override these in subclass
    LOTUS_POSITION: ClassVar[int] = 0
    LOTUS_NAME: ClassVar[str] = "unnamed"

    def __init__(self) -> None:
        # Create MantraHeartbeat first, then wrap in LotusHeartbeat
        # The Mantra IS the Lotus - they share the same heartbeat
        mantra_hb = MantraHeartbeat()
        mantra_hb.word_position = self.LOTUS_POSITION
        self._heartbeat = LotusHeartbeat(mantra_hb)
        self._mode = LotusMode.SEED
        self._last_chant: Optional[str] = None
        self._chant_count: int = 0

    # =========================================================================
    # Identity (Automatic from class variables)
    # =========================================================================

    @property
    def lotus_position(self) -> int:
        return self.LOTUS_POSITION

    @property
    def lotus_quarter(self) -> LotusQuarter:
        quarter_index = self.LOTUS_POSITION // WORDS_PER_QUARTER
        return list(LotusQuarter)[quarter_index]

    @property
    def lotus_name(self) -> str:
        return self.LOTUS_NAME

    # =========================================================================
    # Holy Name Math (Automatic)
    # =========================================================================

    @property
    def parampara_hash(self) -> int:
        """
        Calculate Parampara hash.

        Uses position + name hash, then ensures % 37 connection.
        """
        name_hash = sum(ord(c) for c in self.LOTUS_NAME)
        position_factor = (self.LOTUS_POSITION + 1) * LOTUS_PARAMPARA
        return (name_hash + position_factor) * LOTUS_PARAMPARA

    @property
    def is_connected(self) -> bool:
        """
        Verify connection to Parampara.

        Connected if parampara_hash % 37 == 0.
        This is AUTOMATIC - no manual wiring.
        """
        return self.parampara_hash % LOTUS_PARAMPARA == 0

    # =========================================================================
    # Heartbeat (Continuous Chanting)
    # =========================================================================

    def chant(self) -> int:
        """
        Chant once. This is the HEARTBEAT.

        Every chant:
        1. Advances position in Mahamantra
        2. Updates connection to Parampara
        3. Records timestamp

        WITHOUT CHANTING, THE PROTOCOL DRIFTS INTO MAYA.
        """
        new_position = self._heartbeat.pulse()
        self._last_chant = datetime.now().isoformat()
        self._chant_count += 1
        return new_position

    @property
    def is_chanting(self) -> bool:
        """Has chanted at least once."""
        return self._last_chant is not None

    @property
    def heartbeat(self) -> LotusHeartbeat:
        """Access the heartbeat."""
        return self._heartbeat

    # =========================================================================
    # Mode (Transform capability)
    # =========================================================================

    @property
    def mode(self) -> LotusMode:
        return self._mode

    def transform(self, new_mode: LotusMode) -> bool:
        """
        Transform to a different mode.

        SEED → STENGEL → BLÜTE → GARUDA (forward)
        GARUDA → BLÜTE → STENGEL → SEED (backward)

        Each transformation requires a chant.
        """
        self.chant()  # Transformation requires chanting
        self._mode = new_mode
        return True

    def become_garuda(self) -> bool:
        """Transform to GARUDA mode (execution)."""
        return self.transform(LotusMode.GARUDA)

    def become_seed(self) -> bool:
        """Transform back to SEED mode (template)."""
        return self.transform(LotusMode.SEED)

    # =========================================================================
    # Routing (Automatic via position)
    # =========================================================================

    def route_to(self, target_position: int) -> LotusRoute:
        """
        Calculate route to target position.

        Routing is AUTOMATIC:
        - Same quarter = direct route
        - Different quarter = via stengel (stem)

        No manual wiring needed.
        """
        source_quarter = get_quarter(self.LOTUS_POSITION)
        target_quarter = get_quarter(target_position)

        same_quarter = source_quarter == target_quarter

        return LotusRoute(
            source_position=self.LOTUS_POSITION,
            target_position=target_position,
            source_quarter=list(LotusQuarter)[source_quarter].value,
            target_quarter=list(LotusQuarter)[target_quarter].value,
            route_type="intra-quarter" if same_quarter else "inter-quarter",
            via_stengel=not same_quarter,
            parampara_verified=self.is_connected,
        )

    # =========================================================================
    # State (WATERTIGHT)
    # =========================================================================

    def get_state(self) -> LotusNode:
        """Get current state as LotusNode. WATERTIGHT - no Any!"""
        return LotusNode(
            path="",  # Set by registry
            name=self.LOTUS_NAME,
            position=self.LOTUS_POSITION,
            quarter=self.lotus_quarter.value,
            owner_type="",  # Set by registry
            owner_name="",  # Set by registry
            parampara_hash=self.parampara_hash,
            is_connected=self.is_connected,
            is_chanting=self.is_chanting,
            discovered_at=datetime.now().isoformat(),
        )


# =============================================================================
# LOTUS REGISTRY (Auto-Discovery)
# =============================================================================


class LotusRegistry:
    """
    The Lotus Registry - Auto-Discovery System.

    Scans folder structure and discovers protocols.
    FOLDER = OWNERSHIP. No manual registration.

    The registry itself chants to stay connected.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, LotusNode] = {}
        self._heartbeat = LotusHeartbeat()
        self._petals: Dict[LotusQuarter, LotusPetal] = {}
        self._initialize_petals()

    def _initialize_petals(self) -> None:
        """Initialize the 4 petals (quarters)."""
        # Quarter assignments (ALIGNED WITH seed.py ALL_GUARDIANS)
        petal_config = [
            (LotusQuarter.GENESIS, [0, 1, 2, 3], "vyasa", ["brahma", "narada", "shambhu"]),
            (LotusQuarter.DHARMA, [4, 5, 6, 7], "prithu", ["kumaras", "kapila", "manu"]),
            (LotusQuarter.KARMA, [8, 9, 10, 11], "parashurama", ["prahlada", "janaka", "bhishma"]),
            (LotusQuarter.MOKSHA, [12, 13, 14, 15], "nrisimha", ["bali", "shuka", "yamaraja"]),
        ]

        for quarter, positions, head, workers in petal_config:
            self._petals[quarter] = LotusPetal(
                quarter=quarter.value,
                positions=positions,
                head_avatara=head,
                worker_mahajanas=workers,
            )

    def discover(self, base_path: Path) -> List[LotusNode]:
        """
        Discover all protocols in the given path.

        FOLDER = OWNERSHIP:
        - protocols/avataras/{name}/ → Avatara
        - protocols/mahajanas/{name}/ → Mahajana

        No manual registration. The folder structure IS the registration.
        """
        discovered: List[LotusNode] = []

        # Scan avataras
        avataras_path = base_path / "protocols" / "avataras"
        if avataras_path.exists():
            for avatara_dir in avataras_path.iterdir():
                if avatara_dir.is_dir() and not avatara_dir.name.startswith("_"):
                    node = self._create_node(
                        path=str(avatara_dir),
                        name=avatara_dir.name,
                        owner_type="avatara",
                    )
                    discovered.append(node)
                    self._nodes[avatara_dir.name] = node

        # Scan mahajanas
        mahajanas_path = base_path / "protocols" / "mahajanas"
        if mahajanas_path.exists():
            for mahajana_dir in mahajanas_path.iterdir():
                if mahajana_dir.is_dir() and not mahajana_dir.name.startswith("_"):
                    node = self._create_node(
                        path=str(mahajana_dir),
                        name=mahajana_dir.name,
                        owner_type="mahajana",
                    )
                    discovered.append(node)
                    self._nodes[mahajana_dir.name] = node

        return discovered

    def _create_node(
        self,
        path: str,
        name: str,
        owner_type: str,
    ) -> LotusNode:
        """Create a LotusNode from discovered folder."""
        # Calculate position from name hash
        name_hash = sum(ord(c) for c in name)
        position = name_hash % LOTUS_POSITIONS

        # Calculate Parampara hash
        parampara_hash = name_hash * LOTUS_PARAMPARA

        return LotusNode(
            path=path,
            name=name,
            position=position,
            quarter=list(LotusQuarter)[position // WORDS_PER_QUARTER].value,
            owner_type=owner_type,
            owner_name=name,
            parampara_hash=parampara_hash,
            is_connected=parampara_hash % LOTUS_PARAMPARA == 0,
            is_chanting=False,  # Not chanting until activated
            discovered_at=datetime.now().isoformat(),
        )

    def chant(self) -> int:
        """Registry chants to stay connected."""
        return self._heartbeat.pulse()

    def get_state(self) -> LotusState:
        """Get full registry state. WATERTIGHT."""
        connected = sum(1 for n in self._nodes.values() if n.get("is_connected", False))
        chanting = sum(1 for n in self._nodes.values() if n.get("is_chanting", False))

        return LotusState(
            mode=LotusMode.STENGEL.value,  # Registry is always in bridge mode
            total_nodes=len(self._nodes),
            connected_nodes=connected,
            disconnected_nodes=len(self._nodes) - connected,
            chanting_nodes=chanting,
            petals=list(self._petals.values()),
            health="pristine" if connected == len(self._nodes) else "degraded",
            last_pulse=datetime.now().isoformat(),
            mala_count=self._heartbeat.mala_count,
        )

    def get_petals(self) -> Dict[LotusQuarter, LotusPetal]:
        """Get all petals."""
        return self._petals.copy()

    def route(self, source: str, target: str) -> Optional[LotusRoute]:
        """
        Route from source to target protocol.

        Uses Mahamantra positions for automatic routing.
        """
        source_node = self._nodes.get(source)
        target_node = self._nodes.get(target)

        if not source_node or not target_node:
            return None

        source_pos = source_node.get("position", 0)
        target_pos = target_node.get("position", 0)
        source_q = get_quarter(source_pos)
        target_q = get_quarter(target_pos)

        return LotusRoute(
            source_position=source_pos,
            target_position=target_pos,
            source_quarter=list(LotusQuarter)[source_q].value,
            target_quarter=list(LotusQuarter)[target_q].value,
            route_type="intra-quarter" if source_q == target_q else "inter-quarter",
            via_stengel=source_q != target_q,
            parampara_verified=source_node.get("is_connected", False) and target_node.get("is_connected", False),
        )


# =============================================================================
# GLOBAL LOTUS (Singleton)
# =============================================================================

_global_lotus: Optional[LotusRegistry] = None


def get_lotus() -> LotusRegistry:
    """Get the global Lotus registry."""
    global _global_lotus
    if _global_lotus is None:
        _global_lotus = LotusRegistry()
    return _global_lotus


def grow_lotus(base_path: Path) -> LotusState:
    """
    Grow the Lotus by discovering all protocols.

    This is the MAIN ENTRY POINT.
    Call this once at startup.
    """
    lotus = get_lotus()
    lotus.discover(base_path)
    lotus.chant()  # Initial chant
    return lotus.get_state()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants (Holy Name Math)
    "LOTUS_POSITIONS",
    "LOTUS_QUARTERS",
    "WORDS_PER_QUARTER",
    "LOTUS_PARAMPARA",
    "LOTUS_TRINITY",
    "LOTUS_PHASES",
    "LOTUS_MALA",
    # Enums
    "LotusMode",
    "LotusQuarter",
    # LOTUS ↔ MAHAMANTRA MAPPING (The Connection!)
    "LOTUS_TO_MANTRA_QUARTER",
    "MANTRA_TO_LOTUS_QUARTER",
    "get_lotus_quarter",
    "get_mantra_quarter",
    "get_pada_at_position",
    # Types (WATERTIGHT)
    "LotusPetal",
    "LotusNode",
    "LotusState",
    "LotusRoute",
    # Heartbeat (wraps MantraHeartbeat)
    "LotusHeartbeat",
    # Protocol
    "LotusProtocol",
    # Base Class
    "LotusBase",
    # Registry
    "LotusRegistry",
    # Global Functions
    "get_lotus",
    "grow_lotus",
]
