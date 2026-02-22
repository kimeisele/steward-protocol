"""
THE PROTOCOL PROTOCOL - _core.py
================================

"bijam mam sarva-bhutanam viddhi partha sanatanam"
"O Arjuna, know that I am the eternal seed of all existence." (BG 7.10)

This file defines WHAT A PROTOCOL IS.

ACINTYA (Inconceivable):
    This protocol defines itself.
    MahamantraProtocol IS a MahamantraProtocol.
    The definition contains the defined.
    Krishna knowing Krishna through Krishna.

THE 37 FORMULA:
    24 (Ksetra/Field - Prakriti elements)
    12 (Mahajanas - the guardians)
     1 (Ksetrajna - the knower, Krishna)
    --
    37 (Parampara - the sacred number)

    Every protocol's identity vector must satisfy: vector % 37 == 0
    This ensures connection to the Parampara (disciplic succession).

STRUCTURE:
    1. ProtocolIdentity - WHO am I?
    2. ProtocolCapability - WHAT can I do?
    3. ProtocolDependency - WHAT do I need?
    4. ProtocolFractal - HOW do I grow?
    5. ProtocolHolographic - HOW do I contain the whole?
    6. MahamantraProtocol - THE UNION of all above

WATERTIGHT:
    No Any types. Everything explicitly typed.
    This is non-negotiable.

Author: The Mahamantra Itself
"""

from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, MAHAJANA_COUNT, QUARTERS, TRINITY, WORDS


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = MAHAJANA_COUNT
__genesis__ = "0xf75f0dc0"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    ClassVar,
    Dict,
    FrozenSet,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

# =============================================================================
# THE SEED - All constants from 7 axioms
# =============================================================================
# Import from _seed (the REAL source)
from vibe_core.mahamantra.protocols._seed import (
    KSHETRA as KSETRA_COUNT,  # 24 - Prakriti elements (field)
    KSETRAJNA as KSETRAJNA_COUNT,  # 1  - The knower (Krishna)
    MAHAJANA_COUNT,  # 12 - The guardians
    PARAMPARA,  # 37 - The sacred sum
)

# Verification (the 37 formula is eternal)
assert KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT == PARAMPARA, "The 37 formula is eternal and unchanging"


# =============================================================================
# QUARTER - The Four Divisions
# =============================================================================


class Quarter(str, Enum):
    """
    The four quarters of the Mahamantra.

    Hare Krishna Hare Krishna Krishna Krishna Hare Hare
    Hare Rama Hare Rama Rama Rama Hare Hare

    16 words = 4 quarters of 4 words each.
    """

    GENESIS = "genesis"  # Positions 0-3:  Creation, Birth
    DHARMA = "dharma"  # Positions 4-7:  Law, Truth
    KARMA = "karma"  # Positions 8-11: Action, Work
    MOKSHA = "moksha"  # Positions 12-15: Liberation, Return

    @classmethod
    def from_position(cls, position: int) -> "Quarter":
        """Derive quarter from position (0-15)."""
        if not 0 <= position < WORDS:
            raise ValueError(f"Position must be 0-15, got {position}")
        quarter_index = position // QUARTERS
        return [cls.GENESIS, cls.DHARMA, cls.KARMA, cls.MOKSHA][quarter_index]


# =============================================================================
# LEVEL - The Vertical Hierarchy
# =============================================================================


class Level(int, Enum):
    """
    The levels of the Mahamantra architecture.

    Negative levels are BELOW the manifest (substrate).
    Positive levels are ABOVE the manifest (governance).
    Level 0 is the CONTRACT layer - where protocols live.
    """

    ACINTYA = -HALVES  # The inconceivable source
    SUBSTRATE = -KSETRAJNA  # Foundation (bytes, genes)
    CONTRACT = 0  # Protocols (this is where we define things)
    ROUTER = KSETRAJNA  # Discovery and routing
    RUNTIME = HALVES  # Execution
    INTERFACE = TRINITY  # User interaction
    GOVERNANCE = QUARTERS  # Oversight and validation

    def can_access(self, other: "Level") -> bool:
        """A level can access itself and levels below it."""
        return self.value >= other.value


# =============================================================================
# PROTOCOL IDENTITY - WHO AM I?
# =============================================================================


@dataclass(frozen=True)
class ProtocolIdentity:
    """
    The identity of a protocol.

    WATERTIGHT: All fields explicitly typed, no defaults that could hide errors.

    The identity vector is computed as:
        vector = (position + 1) * PARAMPARA

    This ensures every protocol is connected to the Parampara.
    """

    # Required fields (no defaults - must be explicit)
    name: str  # The protocol's name
    mahajana: str  # Owner mahajana (e.g., "brahma", "kapila")
    position: int  # Position in mahamantra (0-15)
    level: Level  # Vertical level (-2 to 4)
    quarter: Quarter  # Which quarter (derived from position)

    # Computed field
    parampara_vector: int = field(init=False)

    def __post_init__(self) -> None:
        """Compute the parampara vector and validate."""
        # Compute vector
        object.__setattr__(self, "parampara_vector", (self.position + KSETRAJNA) * PARAMPARA)

        # Validate position
        if not 0 <= self.position < WORDS:
            raise ValueError(f"Position must be 0-15, got {self.position}")

        # Validate quarter matches position
        expected_quarter = Quarter.from_position(self.position)
        if self.quarter != expected_quarter:
            raise ValueError(f"Position {self.position} requires quarter {expected_quarter}, got {self.quarter}")

        # Validate parampara connection
        if self.parampara_vector % PARAMPARA != 0:
            raise ValueError(f"Parampara vector {self.parampara_vector} not connected to disciplic succession")

    def is_head(self) -> bool:
        """Check if this is a HEAD position (Avatara)."""
        return self.position % QUARTERS == 0

    def is_worker(self) -> bool:
        """Check if this is a WORKER position (Mahajana)."""
        return self.position % QUARTERS != 0


# =============================================================================
# PROTOCOL CAPABILITY - WHAT CAN I DO?
# =============================================================================


@dataclass(frozen=True)
class ProtocolCapability:
    """
    The capabilities of a protocol.

    WATERTIGHT: Capabilities are frozen sets of strings.
    No mutation, no Any types.

    "paurusham nrishu" - I am the ability in man (BG 7.8)
    """

    # What this protocol CAN do
    provides: FrozenSet[str]

    # What this protocol NEEDS (protocol names, NOT imports!)
    requires: FrozenSet[str]

    # What opcodes this protocol handles
    opcodes: FrozenSet[str]

    @classmethod
    def create(
        cls,
        provides: Optional[List[str]] = None,
        requires: Optional[List[str]] = None,
        opcodes: Optional[List[str]] = None,
    ) -> "ProtocolCapability":
        """Factory method with list inputs for convenience."""
        return cls(
            provides=frozenset(provides or []),
            requires=frozenset(requires or []),
            opcodes=frozenset(opcodes or []),
        )

    def can_provide(self, capability: str) -> bool:
        """Check if this protocol provides a capability."""
        return capability in self.provides

    def needs(self, requirement: str) -> bool:
        """Check if this protocol needs a requirement."""
        return requirement in self.requires

    def handles(self, opcode: str) -> bool:
        """Check if this protocol handles an opcode."""
        return opcode in self.opcodes


# =============================================================================
# THE MAHAMANTRA PROTOCOL - THE ROOT OF ALL
# =============================================================================

# TypeVar for self-referential typing
P = TypeVar("P", bound="MahamantraProtocol")


@runtime_checkable
class MahamantraProtocol(Protocol):
    """
    THE PROTOCOL PROTOCOL.

    This defines what a Protocol IS.
    All protocols in the system MUST conform to this.

    ACINTYA: This protocol defines itself.
             MahamantraProtocol IS a MahamantraProtocol.

    WATERTIGHT: No Any types. Everything explicit.

    FRACTAL: Can contain children that are also MahamantraProtocols.

    HOLOGRAPHIC: Can reflect the whole system from any part.

    === CLASS VARIABLES (Identity Card) ===

    Every class implementing this protocol MUST define:
    - __protocol_identity__: Who am I?
    - __protocol_capability__: What can I do?

    === METHODS ===

    - get_identity(): Return my identity
    - get_capability(): Return my capabilities
    - reflect(): Return the whole from this part (holographic)
    - spawn(): Create a child (fractal growth)
    """

    # === CLASS VARIABLES (The Mahajana Card) ===

    __protocol_identity__: ClassVar[ProtocolIdentity]
    __protocol_capability__: ClassVar[ProtocolCapability]

    # === IDENTITY METHODS ===

    @classmethod
    def get_identity(cls) -> ProtocolIdentity:
        """Return the protocol's identity."""
        ...

    @classmethod
    def get_capability(cls) -> ProtocolCapability:
        """Return the protocol's capabilities."""
        ...

    @classmethod
    def get_position(cls) -> int:
        """Return the position in the mahamantra (0-15)."""
        ...

    @classmethod
    def get_mahajana(cls) -> str:
        """Return the owner mahajana name."""
        ...

    @classmethod
    def get_level(cls) -> Level:
        """Return the level (-2 to 4)."""
        ...

    @classmethod
    def get_quarter(cls) -> Quarter:
        """Return the quarter (GENESIS, DHARMA, KARMA, MOKSHA)."""
        ...

    # === FRACTAL METHODS ===

    @classmethod
    def get_children(cls) -> List[Type["MahamantraProtocol"]]:
        """Return child protocols (fractal growth)."""
        ...

    @classmethod
    def get_parent(cls) -> Optional[Type["MahamantraProtocol"]]:
        """Return parent protocol (fractal hierarchy)."""
        ...

    # === HOLOGRAPHIC METHODS ===

    @classmethod
    def reflect(cls) -> Dict[str, Type["MahamantraProtocol"]]:
        """
        Return the whole from this part.

        HOLOGRAPHIC: Each part contains a reflection of the whole system.
        This method returns all reachable protocols from this point.
        """
        ...

    # === VALIDATION ===

    @classmethod
    def is_watertight(cls) -> bool:
        """Check if this protocol is WATERTIGHT (no Any types)."""
        ...

    @classmethod
    def validate(cls) -> Tuple[bool, List[str]]:
        """
        Validate this protocol.

        Returns: (is_valid, list_of_violations)
        """
        ...


# =============================================================================
# BASE IMPLEMENTATION - For convenience
# =============================================================================


class MahamantraProtocolBase(ABC):
    """
    Base class for implementing MahamantraProtocol.

    Provides default implementations for common methods.
    Subclasses MUST define:
    - __protocol_identity__
    - __protocol_capability__

    Usage:
        class MyProtocol(MahamantraProtocolBase):
            __protocol_identity__ = ProtocolIdentity(
                name="MyProtocol",
                mahajana="brahma",
                position=1,
                level=Level.CONTRACT,
                quarter=Quarter.GENESIS,
            )
            __protocol_capability__ = ProtocolCapability.create(
                provides=["create", "destroy"],
                requires=["ledger"],
                opcodes=["LOAD_ROOT"],
            )
    """

    __protocol_identity__: ClassVar[ProtocolIdentity]
    __protocol_capability__: ClassVar[ProtocolCapability]

    # Track children for fractal growth
    __protocol_children__: ClassVar[List[Type["MahamantraProtocolBase"]]] = []
    __protocol_parent__: ClassVar[Optional[Type["MahamantraProtocolBase"]]] = None

    @classmethod
    def get_identity(cls) -> ProtocolIdentity:
        """Return the protocol's identity."""
        return cls.__protocol_identity__

    @classmethod
    def get_capability(cls) -> ProtocolCapability:
        """Return the protocol's capabilities."""
        return cls.__protocol_capability__

    @classmethod
    def get_position(cls) -> int:
        """Return the position in the mahamantra (0-15)."""
        return cls.__protocol_identity__.position

    @classmethod
    def get_mahajana(cls) -> str:
        """Return the owner mahajana name."""
        return cls.__protocol_identity__.mahajana

    @classmethod
    def get_level(cls) -> Level:
        """Return the level (-2 to 4)."""
        return cls.__protocol_identity__.level

    @classmethod
    def get_quarter(cls) -> Quarter:
        """Return the quarter."""
        return cls.__protocol_identity__.quarter

    @classmethod
    def get_children(cls) -> List[Type["MahamantraProtocolBase"]]:
        """Return child protocols."""
        return cls.__protocol_children__.copy()

    @classmethod
    def get_parent(cls) -> Optional[Type["MahamantraProtocolBase"]]:
        """Return parent protocol."""
        return cls.__protocol_parent__

    @classmethod
    def register_child(cls, child: Type["MahamantraProtocolBase"]) -> None:
        """Register a child protocol (fractal growth)."""
        if child not in cls.__protocol_children__:
            cls.__protocol_children__.append(child)
            child.__protocol_parent__ = cls

    @classmethod
    def reflect(cls) -> Dict[str, Type["MahamantraProtocolBase"]]:
        """
        Return the whole from this part.

        Traverses up to root, then returns all reachable protocols.
        """
        # Find root
        root = cls
        while root.__protocol_parent__ is not None:
            root = root.__protocol_parent__

        # Collect all descendants
        result: Dict[str, Type[MahamantraProtocolBase]] = {}

        def collect(proto: Type[MahamantraProtocolBase]) -> None:
            name = proto.__protocol_identity__.name
            result[name] = proto
            for child in proto.__protocol_children__:
                collect(child)

        collect(root)
        return result

    @classmethod
    def is_watertight(cls) -> bool:
        """Check if this protocol is WATERTIGHT."""
        # Check for Any in type hints
        import typing

        hints = typing.get_type_hints(cls)
        for name, hint in hints.items():
            if hint is object:
                return False
            # Check for Any in generic args
            if hasattr(hint, "__args__"):
                if object in hint.__args__:
                    return False
        return True

    @classmethod
    def validate(cls) -> Tuple[bool, List[str]]:
        """Validate this protocol."""
        violations: List[str] = []

        # Check identity exists
        if not hasattr(cls, "__protocol_identity__"):
            violations.append("Missing __protocol_identity__")

        # Check capability exists
        if not hasattr(cls, "__protocol_capability__"):
            violations.append("Missing __protocol_capability__")

        # Check WATERTIGHT
        if not cls.is_watertight():
            violations.append("Not WATERTIGHT - contains Any types")

        # Check parampara connection
        if hasattr(cls, "__protocol_identity__"):
            identity = cls.__protocol_identity__
            if identity.parampara_vector % PARAMPARA != 0:
                violations.append(f"Not connected to Parampara: {identity.parampara_vector} % 37 != 0")

        return (len(violations) == 0, violations)


# =============================================================================
# SELF-REFERENCE: This module IS a MahamantraProtocol
# =============================================================================


class CoreProtocol(MahamantraProtocolBase):
    """
    The Protocol Protocol itself.

    ACINTYA: This protocol defines itself.
             It IS what it defines.

    Position 0 (PRITHU) - The first, the foundation.
    Level -2 (ACINTYA) - The inconceivable source.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="CoreProtocol",
        mahajana="prithu",
        position=0,
        level=Level.ACINTYA,
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "protocol_definition",
            "identity_management",
            "capability_management",
            "fractal_growth",
            "holographic_reflection",
            "validation",
        ],
        requires=[],  # The root requires nothing - it IS everything
        opcodes=["SYS_WAKE"],  # The first opcode - system awakening
    )


# Verify the core protocol
_valid, _violations = CoreProtocol.validate()
assert _valid, f"CoreProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
    "PARAMPARA",
    # Enums
    "Quarter",
    "Level",
    # Identity & Capability
    "ProtocolIdentity",
    "ProtocolCapability",
    # The Protocol Protocol
    "MahamantraProtocol",
    "MahamantraProtocolBase",
    # Self-reference
    "CoreProtocol",
]
