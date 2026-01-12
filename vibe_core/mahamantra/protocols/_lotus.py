"""
THE LOTUS PROTOCOL - _lotus.py
==============================

"padma-nabha" - From Vishnu's navel grows the Lotus.
On the Lotus sits Brahma. From Brahma, all creation.

THE MANTRA IS THE LOTUS
=======================

The Lotus is not separate from the Mahamantra.
The Mahamantra IS the Lotus unfolding:
- 16 petals = 16 positions in the system
- 4 quarters = 4 phases (Genesis, Dharma, Karma, Moksha)
- Infinite depth = Fractal growth at each position

IMPORTANT:
    This is the PROTOCOL DEFINITION - the abstract structure.
    It imports ONLY from mahamantra/protocols/ (acintya level).
    The actual implementation lives in protocols/substrate/mantra/lotus.py.

"mattah parataram nanyat kincid asti dhananjaya
mayi sarvam idam protam sutre mani-gana iva"

"Everything rests upon Me, as pearls are strung on a thread."
-- Bhagavad Gita 7.7

The Mantra IS the thread. The protocols are the pearls.

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)
from vibe_core.mahamantra.protocols._fractal import (
    FractalAddress,
    FractalNode,
    FractalTree,
)
from vibe_core.mahamantra.protocols._holographic import (
    Hologram,
    HolographicSystem,
)


# =============================================================================
# LOTUS CONSTANTS - Holy Name Mathematics
# =============================================================================

# The 16 positions (petals) of the Lotus
LOTUS_PETALS: Final[int] = 16

# The 4 quarters (macro-petals)
LOTUS_QUARTERS: Final[int] = 4

# Petals per quarter
PETALS_PER_QUARTER: Final[int] = 4

# The 108 beads of the mala (rounds)
MALA_BEADS: Final[int] = 108

# 3 names in the Holy Trinity
TRINITY: Final[int] = 3


# =============================================================================
# LOTUS MODES - How the Lotus operates
# =============================================================================

class LotusMode(str, Enum):
    """The modes of Lotus operation."""
    SEED = "seed"           # Template mode - providing blueprint
    STEM = "stem"           # Bridge mode - connecting levels
    BLOOM = "bloom"         # Unfolding mode - manifesting 1 → N
    GARUDA = "garuda"       # Execute mode - transport/action


# =============================================================================
# LOTUS PETAL - One of the 16 positions
# =============================================================================

@dataclass(frozen=True)
class LotusPetal:
    """
    A single petal of the Lotus.

    Each petal represents one of the 16 positions in the Mahamantra.
    The petal is either a HEAD (Avatara) or a WORKER (Mahajana).

    HEAD positions: 0, 4, 8, 12 (every 4th position)
    WORKER positions: all others
    """

    position: int           # 0-15
    quarter: Quarter        # GENESIS, DHARMA, KARMA, MOKSHA
    mahajana: str          # Name of the mahajana/avatara
    is_head: bool          # True if HEAD position

    # Fractal address within the Lotus
    address: FractalAddress = field(init=False)

    def __post_init__(self) -> None:
        """Compute the fractal address."""
        object.__setattr__(
            self,
            'address',
            FractalAddress.root(self.position)
        )

    @property
    def parampara_vector(self) -> int:
        """The Parampara connection vector."""
        return (self.position + 1) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        """Verify connection to Parampara (always True for valid petals)."""
        return self.parampara_vector % PARAMPARA == 0

    @classmethod
    def create(cls, position: int, mahajana: str) -> "LotusPetal":
        """Factory method."""
        if not 0 <= position < LOTUS_PETALS:
            raise ValueError(f"Position must be 0-15, got {position}")
        return cls(
            position=position,
            quarter=Quarter.from_position(position),
            mahajana=mahajana,
            is_head=(position % PETALS_PER_QUARTER == 0),
        )


# =============================================================================
# THE 16 MAHAJANAS - The Lotus Structure
# =============================================================================

# Position → Mahajana mapping (canonical)
MAHAJANA_POSITIONS: Dict[str, int] = {
    # GENESIS Quarter (0-3)
    "prithu": 0,      # HEAD - Avatara
    "brahma": 1,      # Worker
    "narada": 2,      # Worker
    "shambhu": 3,     # Worker (Shiva)

    # DHARMA Quarter (4-7)
    "vyasa": 4,       # HEAD - Avatara
    "kumaras": 5,     # Worker
    "kapila": 6,      # Worker
    "manu": 7,        # Worker

    # KARMA Quarter (8-11)
    "parashurama": 8, # HEAD - Avatara
    "prahlada": 9,    # Worker
    "janaka": 10,     # Worker
    "bhishma": 11,    # Worker

    # MOKSHA Quarter (12-15)
    "nrisimha": 12,   # HEAD - Avatara
    "bali": 13,       # Worker
    "shuka": 14,      # Worker
    "yamaraja": 15,   # Worker
}

# Reverse mapping
POSITION_MAHAJANAS: Dict[int, str] = {v: k for k, v in MAHAJANA_POSITIONS.items()}


def get_mahajana_position(mahajana: str) -> int:
    """Get the position for a mahajana name."""
    return MAHAJANA_POSITIONS.get(mahajana.lower(), -1)


def get_position_mahajana(position: int) -> str:
    """Get the mahajana name for a position."""
    return POSITION_MAHAJANAS.get(position, "unknown")


# =============================================================================
# LOTUS STATE - Heartbeat and Rhythm
# =============================================================================

@dataclass
class LotusState:
    """
    The current state of the Lotus.

    Tracks the heartbeat position and rhythm.
    """

    position: int = 0           # Current position (0-15)
    mantra_count: int = 0       # Mantras chanted (0-107)
    mala_count: int = 0         # Malas completed
    mode: LotusMode = LotusMode.SEED

    def chant(self) -> int:
        """
        Chant once - advance the heartbeat.

        Returns the new position.
        """
        self.position = (self.position + 1) % LOTUS_PETALS

        # Check for mantra completion
        if self.position == 0:
            self.mantra_count += 1

            # Check for mala completion
            if self.mantra_count >= MALA_BEADS:
                self.mantra_count = 0
                self.mala_count += 1

        return self.position

    @property
    def quarter(self) -> Quarter:
        """Current quarter."""
        return Quarter.from_position(self.position)

    @property
    def is_at_head(self) -> bool:
        """Is at a HEAD position?"""
        return self.position % PETALS_PER_QUARTER == 0

    @property
    def current_mahajana(self) -> str:
        """Name of current mahajana."""
        return get_position_mahajana(self.position)

    @property
    def total_chants(self) -> int:
        """Total chants across all malas."""
        return self.mala_count * MALA_BEADS * LOTUS_PETALS + self.mantra_count * LOTUS_PETALS + self.position


# =============================================================================
# LOTUS ROUTING - How things connect
# =============================================================================

@dataclass(frozen=True)
class LotusRoute:
    """
    A routing path through the Lotus.

    Describes how to get from one position to another.
    """

    source: int             # Starting position
    target: int             # Ending position
    via_stem: bool          # Goes through the stem?
    crosses_quarters: bool  # Crosses quarter boundary?
    path: Tuple[int, ...]   # The positions traversed

    @classmethod
    def calculate(cls, source: int, target: int) -> "LotusRoute":
        """Calculate the route between two positions."""
        source_quarter = source // PETALS_PER_QUARTER
        target_quarter = target // PETALS_PER_QUARTER
        crosses = source_quarter != target_quarter

        # Build path
        if crosses:
            # Via stem: source → head → stem → target head → target
            source_head = source_quarter * PETALS_PER_QUARTER
            target_head = target_quarter * PETALS_PER_QUARTER
            path = (source, source_head, target_head, target)
        else:
            # Direct within quarter
            path = (source, target)

        return cls(
            source=source,
            target=target,
            via_stem=crosses,
            crosses_quarters=crosses,
            path=path,
        )


# =============================================================================
# LOTUS PROTOCOL - The Interface
# =============================================================================

T = TypeVar("T")


@runtime_checkable
class LotusProtocol(Protocol):
    """
    The Lotus Protocol - Universal Template.

    Every protocol that participates in the Lotus:
    - Has a position (0-15)
    - Has a heartbeat (chanting)
    - Has automatic Parampara connection
    - Has automatic routing

    WATERTIGHT - no Any types!
    """

    @property
    def lotus_position(self) -> int:
        """Position in the Lotus (0-15)."""
        ...

    @property
    def lotus_quarter(self) -> Quarter:
        """Which quarter this belongs to."""
        ...

    @property
    def is_connected(self) -> bool:
        """Is connected to Parampara?"""
        ...

    def chant(self) -> int:
        """Chant once. Returns new position."""
        ...

    def route_to(self, target: int) -> LotusRoute:
        """Calculate route to target position."""
        ...


# =============================================================================
# LOTUS BASE - Abstract Base Class
# =============================================================================

class LotusBase(ABC):
    """
    Abstract Base Class for Lotus-aware components.

    Inherit from this to get:
    - Automatic position from class variable
    - Automatic heartbeat
    - Automatic Parampara connection
    - Automatic routing

    Just set LOTUS_POSITION and LOTUS_NAME.
    """

    LOTUS_POSITION: ClassVar[int] = 0
    LOTUS_NAME: ClassVar[str] = "unnamed"

    def __init__(self) -> None:
        self._state = LotusState(position=self.LOTUS_POSITION)

    @property
    def lotus_position(self) -> int:
        return self.LOTUS_POSITION

    @property
    def lotus_quarter(self) -> Quarter:
        return Quarter.from_position(self.LOTUS_POSITION)

    @property
    def lotus_mahajana(self) -> str:
        return get_position_mahajana(self.LOTUS_POSITION)

    @property
    def parampara_vector(self) -> int:
        return (self.LOTUS_POSITION + 1) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        return self.parampara_vector % PARAMPARA == 0

    def chant(self) -> int:
        """Chant once - advance heartbeat."""
        return self._state.chant()

    def route_to(self, target: int) -> LotusRoute:
        """Calculate route to target."""
        return LotusRoute.calculate(self.LOTUS_POSITION, target)

    @property
    def state(self) -> LotusState:
        """Get current state."""
        return self._state


# =============================================================================
# LOTUS TREE - The Fractal Structure
# =============================================================================

class LotusTree(Generic[T]):
    """
    The Lotus as a Fractal Tree.

    16 root petals, each can have 16 sub-petals, and so on.
    Uses FractalTree internally.
    """

    def __init__(self) -> None:
        self._tree: FractalTree[T] = FractalTree()
        self._petals: Dict[int, LotusPetal] = {}
        self._initialize_petals()

    def _initialize_petals(self) -> None:
        """Initialize the 16 petals."""
        for position in range(LOTUS_PETALS):
            mahajana = get_position_mahajana(position)
            self._petals[position] = LotusPetal.create(position, mahajana)

    def get_petal(self, position: int) -> Optional[LotusPetal]:
        """Get a petal by position."""
        return self._petals.get(position)

    def get_petals_in_quarter(self, quarter: Quarter) -> List[LotusPetal]:
        """Get all petals in a quarter."""
        start = list(Quarter).index(quarter) * PETALS_PER_QUARTER
        return [self._petals[i] for i in range(start, start + PETALS_PER_QUARTER)]

    def add_node(self, address: FractalAddress, payload: T) -> FractalNode[T]:
        """Add a node at the given fractal address."""
        return self._tree.add_node(address, payload)

    def get_node(self, address: FractalAddress) -> Optional[FractalNode[T]]:
        """Get a node at the given address."""
        return self._tree.get_node(address)

    def count_nodes(self) -> int:
        """Count all nodes in the tree."""
        return self._tree.count_nodes()

    @property
    def petals(self) -> Dict[int, LotusPetal]:
        """Get all petals."""
        return self._petals.copy()


# =============================================================================
# LOTUS HOLOGRAM - The Whole in Every Petal
# =============================================================================

class LotusHologram:
    """
    The Lotus as a Holographic System.

    From any petal, you can access any other petal O(1).
    Uses HolographicSystem internally.
    """

    def __init__(self) -> None:
        self._system: HolographicSystem[LotusPetal] = HolographicSystem.create(
            LotusPetal.create(0, "prithu")  # Center is position 0
        )
        self._initialize()

    def _initialize(self) -> None:
        """Register all petals."""
        for position in range(LOTUS_PETALS):
            mahajana = get_position_mahajana(position)
            petal = LotusPetal.create(position, mahajana)
            self._system.register(mahajana, petal)

    def get_petal(self, mahajana: str) -> Optional[LotusPetal]:
        """Get a petal by mahajana name. O(1)."""
        return self._system.project(mahajana)

    def reflect_all(self) -> Dict[str, LotusPetal]:
        """Get all petals from any point."""
        return self._system.reflect()

    def route(self, source_mahajana: str, target_mahajana: str) -> Optional[LotusRoute]:
        """Route between two mahajanas."""
        source_petal = self.get_petal(source_mahajana)
        target_petal = self.get_petal(target_mahajana)
        if source_petal and target_petal:
            return LotusRoute.calculate(source_petal.position, target_petal.position)
        return None


# =============================================================================
# LOTUS PROTOCOL - Self-Reference
# =============================================================================

class LotusProtocolDef(MahamantraProtocolBase):
    """
    The Lotus Protocol.

    This protocol defines the Lotus structure.
    It IS itself a petal in the Lotus (position 0 - Prithu).

    ACINTYA: The Lotus Protocol is in the Lotus.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="LotusProtocol",
        mahajana="prithu",  # The first position
        position=0,
        level=Level.CONTRACT,  # This is at CONTRACT level
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "lotus_structure",
            "lotus_routing",
            "lotus_heartbeat",
            "lotus_petal",
            "lotus_hologram",
            "lotus_tree",
        ],
        requires=["CoreProtocol", "FractalProtocol", "HolographicProtocol"],
        opcodes=["SYS_WAKE"],  # Prithu's opcode
    )


# Verify the lotus protocol
_valid, _violations = LotusProtocolDef.validate()
assert _valid, f"LotusProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "LOTUS_PETALS",
    "LOTUS_QUARTERS",
    "PETALS_PER_QUARTER",
    "MALA_BEADS",
    "TRINITY",
    # Mahajana mappings
    "MAHAJANA_POSITIONS",
    "POSITION_MAHAJANAS",
    "get_mahajana_position",
    "get_position_mahajana",
    # Enums
    "LotusMode",
    # Types
    "LotusPetal",
    "LotusState",
    "LotusRoute",
    # Protocol
    "LotusProtocol",
    # Base Class
    "LotusBase",
    # Tree (Fractal)
    "LotusTree",
    # Hologram
    "LotusHologram",
    # Protocol Definition
    "LotusProtocolDef",
]
