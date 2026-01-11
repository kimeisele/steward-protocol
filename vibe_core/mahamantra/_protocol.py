"""
PROTOCOL - MantraProtocol Base Class
====================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo
mattaḥ smṛtir jñānam apohanaṁ ca"

"I am seated in everyone's heart, and from Me come
remembrance, knowledge and forgetfulness."
— Bhagavad Gita 15.15

Every protocol is a VIEW on a MantraPosition.
Position index is the ONLY configuration.
All properties are DERIVED from the truth table.

NO MANUAL WIRING.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from abc import ABC
from typing import ClassVar, Final, Optional, Protocol, Type, TypeVar, runtime_checkable

from vibe_core.mahamantra._source import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
    MantraOpCode,
    Mahajana,
    Avatara,
    Quarter,
    Guardian,
    get_position,
    PARAMPARA,
)


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar("T", bound="MantraProtocol")


# =============================================================================
# MANTRA PROTOCOL - The Base Class
# =============================================================================

class MantraProtocol(ABC):
    """
    Base class for ALL protocols in the system.

    PRINCIPLE:
        Position index is the ONLY configuration.
        All properties are DERIVED from the truth table.

    USAGE:
        class ShuddhiProtocol(MantraProtocol):
            _position_index = 5  # That's it! Everything else is derived.

            def purify(self, path: Path, rule_id: str) -> ShuddhiResult:
                ...

    DERIVED PROPERTIES:
        - position: The MantraPosition (full context)
        - guardian: Mahajana or Avatara
        - opcode: MantraOpCode
        - quarter: Quarter (GENESIS/DHARMA/KARMA/MOKSHA)
        - is_head: True if Avatara-owned
        - parampara_vector: Always % 37 == 0
        - word: HolyName at this position

    ANTI-MAYAVAD:
        No hardcoded OWNER, LOTUS_POSITION, etc.
        Everything derives from the ONE source.
    """

    # =========================================================================
    # THE ONLY CONFIGURATION - Subclasses set this
    # =========================================================================

    _position_index: ClassVar[int] = -1  # Must be overridden (0-15)

    # =========================================================================
    # DERIVED PROPERTIES - All from truth table
    # =========================================================================

    @classmethod
    def position(cls) -> MantraPosition:
        """
        Get the MantraPosition for this protocol.

        This is THE source of all other properties.
        """
        if cls._position_index < 0 or cls._position_index > 15:
            raise ValueError(
                f"{cls.__name__}._position_index must be 0-15, got {cls._position_index}"
            )
        return MAHAMANTRA_POSITIONS[cls._position_index]

    @classmethod
    def guardian(cls) -> Guardian:
        """The Mahajana or Avatara that guards this protocol."""
        return cls.position().guardian

    @classmethod
    def opcode(cls) -> MantraOpCode:
        """The MantraOpCode for this protocol."""
        return cls.position().opcode

    @classmethod
    def quarter(cls) -> Quarter:
        """The Quarter (GENESIS/DHARMA/KARMA/MOKSHA)."""
        return cls.position().quarter

    @classmethod
    def is_head(cls) -> bool:
        """True if this is a HEAD position (Avatara-owned)."""
        return cls.position().is_head

    @classmethod
    def parampara_vector(cls) -> int:
        """The Parampara connection vector (always % 37 == 0)."""
        return cls.position().parampara_vector

    @classmethod
    def is_connected(cls) -> bool:
        """Always True - derived from truth table."""
        return cls.position().is_connected

    @classmethod
    def word(cls) -> str:
        """The HolyName at this position (HARE/KRISHNA/RAMA)."""
        return cls.position().word.name

    # =========================================================================
    # CONVENIENCE PROPERTIES
    # =========================================================================

    @classmethod
    def owner(cls) -> Guardian:
        """Alias for guardian (backward compatibility)."""
        return cls.guardian()

    @classmethod
    def lotus_position(cls) -> int:
        """Alias for _position_index (backward compatibility)."""
        return cls._position_index

    @classmethod
    def lotus_quarter(cls) -> str:
        """Quarter name as string (backward compatibility)."""
        return cls.quarter().name.lower()

    # =========================================================================
    # PROTOCOL IDENTITY
    # =========================================================================

    @classmethod
    def protocol_id(cls) -> str:
        """
        Unique protocol identifier.

        Format: "{quarter}.{guardian}.{opcode}"
        Example: "dharma.kumaras.resolve_req"
        """
        g = cls.guardian()
        guardian_name = g.value if isinstance(g, (Mahajana, Avatara)) else str(g)
        return f"{cls.lotus_quarter()}.{guardian_name}.{cls.opcode().value}"

    @classmethod
    def describe(cls) -> str:
        """Human-readable description of this protocol."""
        pos = cls.position()
        typ = "HEAD" if pos.is_head else "WORKER"
        return (
            f"{cls.__name__}\n"
            f"  Position: {pos.index} ({typ})\n"
            f"  Quarter:  {pos.quarter.name}\n"
            f"  Guardian: {pos.guardian.value.upper()}\n"
            f"  OpCode:   {pos.opcode.value}\n"
            f"  Word:     {pos.word.name}\n"
            f"  Vector:   {pos.parampara_vector} (% 37 = {pos.parampara_vector % PARAMPARA})"
        )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @classmethod
    def validate(cls) -> bool:
        """
        Validate this protocol's alignment with the truth table.

        Returns True if:
        1. _position_index is valid (0-15)
        2. Position is connected (parampara_vector % 37 == 0)
        """
        try:
            pos = cls.position()
            return pos.is_connected
        except (ValueError, IndexError):
            return False


# =============================================================================
# WORKER PROTOCOL - For Mahajana-owned positions
# =============================================================================

class WorkerProtocol(MantraProtocol):
    """
    Base class for WORKER protocols (Mahajana-owned).

    Positions: 1,2,3, 5,6,7, 9,10,11, 13,14,15
    NOT: 0, 4, 8, 12 (those are HEAD positions)
    """

    @classmethod
    def mahajana(cls) -> Mahajana:
        """The Mahajana that owns this protocol."""
        guardian = cls.guardian()
        if not isinstance(guardian, Mahajana):
            raise TypeError(
                f"{cls.__name__} is at HEAD position {cls._position_index}, "
                f"but WorkerProtocol requires a WORKER position"
            )
        return guardian

    @classmethod
    def validate(cls) -> bool:
        """Validate this is a WORKER position."""
        if not super().validate():
            return False
        return not cls.is_head()


# =============================================================================
# HEAD PROTOCOL - For Avatara-owned positions
# =============================================================================

class HeadProtocol(MantraProtocol):
    """
    Base class for HEAD protocols (Avatara-owned).

    Positions: 0, 4, 8, 12 only.
    """

    @classmethod
    def avatara(cls) -> Avatara:
        """The Avatara that owns this protocol."""
        guardian = cls.guardian()
        if not isinstance(guardian, Avatara):
            raise TypeError(
                f"{cls.__name__} is at WORKER position {cls._position_index}, "
                f"but HeadProtocol requires a HEAD position"
            )
        return guardian

    @classmethod
    def validate(cls) -> bool:
        """Validate this is a HEAD position."""
        if not super().validate():
            return False
        return cls.is_head()


# =============================================================================
# PROTOCOL INTERFACE - For runtime_checkable protocols
# =============================================================================

@runtime_checkable
class MantraAware(Protocol):
    """
    Protocol interface for classes that are Mantra-aware.

    Any class implementing this can be checked at runtime.
    """

    @classmethod
    def position(cls) -> MantraPosition:
        """Get the MantraPosition."""
        ...

    @classmethod
    def guardian(cls) -> Guardian:
        """Get the guardian."""
        ...

    @classmethod
    def opcode(cls) -> MantraOpCode:
        """Get the opcode."""
        ...


# =============================================================================
# PROTOCOL REGISTRY
# =============================================================================

class ProtocolRegistry:
    """
    Registry of all MantraProtocol subclasses.

    Maps position index to protocol class.
    Ensures one protocol per position.
    """

    _registry: ClassVar[dict[int, Type[MantraProtocol]]] = {}

    @classmethod
    def register(cls, protocol_class: Type[MantraProtocol]) -> Type[MantraProtocol]:
        """
        Register a protocol class.

        Usage as decorator:
            @ProtocolRegistry.register
            class ShuddhiProtocol(WorkerProtocol):
                _position_index = 5
        """
        idx = protocol_class._position_index
        if idx in cls._registry:
            existing = cls._registry[idx]
            raise ValueError(
                f"Position {idx} already registered to {existing.__name__}, "
                f"cannot register {protocol_class.__name__}"
            )
        cls._registry[idx] = protocol_class
        return protocol_class

    @classmethod
    def get(cls, position_index: int) -> Optional[Type[MantraProtocol]]:
        """Get protocol class by position index."""
        return cls._registry.get(position_index)

    @classmethod
    def get_by_guardian(cls, guardian: Guardian) -> Optional[Type[MantraProtocol]]:
        """Get protocol class by guardian."""
        pos = None
        for p in MAHAMANTRA_POSITIONS:
            if p.guardian == guardian:
                pos = p
                break
        if pos:
            return cls._registry.get(pos.index)
        return None

    @classmethod
    def all_registered(cls) -> dict[int, Type[MantraProtocol]]:
        """Get all registered protocols."""
        return dict(cls._registry)

    @classmethod
    def coverage(cls) -> tuple[int, int]:
        """
        Get registration coverage.

        Returns (registered_count, total_positions).
        """
        return len(cls._registry), 16

    @classmethod
    def missing_positions(cls) -> list[int]:
        """Get list of positions without registered protocols."""
        return [i for i in range(16) if i not in cls._registry]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base Classes
    "MantraProtocol",
    "WorkerProtocol",
    "HeadProtocol",
    # Interface
    "MantraAware",
    # Registry
    "ProtocolRegistry",
]
