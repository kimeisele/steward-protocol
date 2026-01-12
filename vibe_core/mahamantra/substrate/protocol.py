"""
PROTOCOL - MantraProtocol Basisklassen
======================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo
mattaḥ smṛtir jñānam apohanaṁ ca"

"Ich sitze in jedermanns Herzen, und von Mir kommen
Erinnerung, Wissen und Vergessen."
— Bhagavad Gita 15.15

SINGLE SOURCE OF TRUTH:
    from vibe_core.mahamantra.substrate.protocol import (
        MantraProtocol,
        WorkerProtocol,
        HeadProtocol,
        ProtocolRegistry,
    )

KEIN DUPLIKAT MEHR. NUR DIESE DATEI.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from abc import ABC
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol as TypingProtocol,
    Type,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.substrate.position import (
    Guardian,
    MantraPosition,
    MAHAMANTRA_POSITIONS,
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
    Basisklasse für ALLE Protokolle im System.

    PRINZIP:
        Position index ist die EINZIGE Konfiguration.
        Alle Properties werden von der Wahrheitstabelle ABGELEITET.

    VERWENDUNG:
        class ShuddhiProtocol(MantraProtocol):
            _position_index = 5  # Das ist alles! Alles andere ist abgeleitet.

            def purify(self, path: Path, rule_id: str) -> ShuddhiResult:
                ...

    ABGELEITETE PROPERTIES:
        - position: Die MantraPosition (voller Kontext)
        - guardian: Mahajana oder Avatara
        - opcode: MantraOpCode
        - quarter: Quarter (GENESIS/DHARMA/KARMA/MOKSHA)
        - is_head: True wenn Avatara-owned
        - parampara_vector: Immer % 37 == 0
        - word: HolyName an dieser Position

    ANTI-MAYAVAD:
        Kein hardcoded OWNER, LOTUS_POSITION, etc.
        Alles leitet sich von der EINEN Quelle ab.
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
        Example: "dharma.kumaras.bind_symbol"
        """
        g = cls.guardian()
        guardian_name = g.value if isinstance(g, (Mahajana, Avatara)) else str(g)
        return f"{cls.lotus_quarter()}.{guardian_name}.{cls.opcode().name.lower()}"

    @classmethod
    def describe(cls) -> str:
        """Human-readable description of this protocol."""
        pos = cls.position()
        typ = "HEAD" if pos.is_head else "WORKER"
        guardian_name = pos.guardian.value if isinstance(pos.guardian, (Mahajana, Avatara)) else str(pos.guardian)
        return (
            f"{cls.__name__}\n"
            f"  Position: {pos.index} ({typ})\n"
            f"  Quarter:  {pos.quarter.name}\n"
            f"  Guardian: {guardian_name.upper()}\n"
            f"  OpCode:   {pos.opcode.name}\n"
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
    Basisklasse für WORKER Protokolle (Mahajana-owned).

    Positionen: 1,2,3, 5,6,7, 9,10,11, 13,14,15
    NICHT: 0, 4, 8, 12 (das sind HEAD Positionen)
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
    Basisklasse für HEAD Protokolle (Avatara-owned).

    Positionen: 0, 4, 8, 12 nur.
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
class MantraAware(TypingProtocol):
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
    Registry aller MantraProtocol Subklassen.

    Mappt Position Index auf Protokollklasse.
    Stellt sicher: ein Protokoll pro Position.
    """

    _registry: ClassVar[Dict[int, Type[MantraProtocol]]] = {}

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
    def all_registered(cls) -> Dict[int, Type[MantraProtocol]]:
        """Get all registered protocols."""
        return dict(cls._registry)

    @classmethod
    def coverage(cls) -> tuple:
        """
        Get registration coverage.

        Returns (registered_count, total_positions).
        """
        return len(cls._registry), 16

    @classmethod
    def missing_positions(cls) -> List[int]:
        """Get list of positions without registered protocols."""
        return [i for i in range(16) if i not in cls._registry]

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._registry.clear()


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
