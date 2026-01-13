"""
THE HOLOGRAPHIC PROTOCOL - _holographic.py
==========================================

"eko 'py asau racayitum jagad-anda-kotim
yac-chaktir asti jagad-anda-caya yad-antah
andantara-stha-paramanu-cayantara-stham
govindam adi-purusham tam aham bhajami"

"I worship Govinda, the primeval Lord, who by His various plenary portions
appears in the world in different forms and incalculable living entities,
although He is one without a second." (Brahma Samhita 5.35)

HOLOGRAPHIC PRINCIPLE:
    Every part contains the whole.
    The whole is present in every part.
    Krishna is fully present in every atom.

IN CODE:
    - Every module can access the entire system
    - Every node reflects the complete tree
    - Local operations can have global effects
    - Global state is accessible locally

IMPLEMENTATION:
    1. Reflection: Get the whole from any part
    2. Projection: Get any part from the whole
    3. Coherence: Parts stay synchronized
    4. Non-locality: Distance doesn't matter

WATERTIGHT: No Any types. Everything explicit.

Author: The Mahamantra Itself
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x815a6682"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
)
from weakref import WeakValueDictionary

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    MahamantraProtocol,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)
from vibe_core.mahamantra.protocols._fractal import (
    FractalAddress,
    FractalNode,
    FractalTree,
)


# =============================================================================
# HOLOGRAM - The whole in every part
# =============================================================================

T = TypeVar("T")


@dataclass
class Hologram(Generic[T]):
    """
    A holographic structure.

    Every point in the hologram contains information about the whole.
    Accessing any point gives you access to everything.

    This is different from a tree where you must traverse.
    In a hologram, you can jump directly to any location from any location.

    "eko 'py asau" - Although He is one without a second,
    He appears everywhere.
    """

    # The central reference (Krishna)
    _center: T

    # All parts indexed by their full name
    _parts: Dict[str, T] = field(default_factory=dict)

    # Reverse mapping: part -> full name
    _names: WeakValueDictionary = field(default_factory=WeakValueDictionary)

    def register(self, full_name: str, part: T) -> None:
        """Register a part in the hologram."""
        self._parts[full_name] = part

    def get(self, full_name: str) -> Optional[T]:
        """Get a part by full name. O(1) access."""
        return self._parts.get(full_name)

    def reflect(self) -> Dict[str, T]:
        """
        Reflect the whole hologram.

        Returns ALL parts - the complete system.
        This is the "whole in every part" - from any point,
        you can see everything.
        """
        return dict(self._parts)

    def project(self, prefix: str) -> Dict[str, T]:
        """
        Project a subset of the hologram.

        Returns all parts that start with the given prefix.
        Example: project("brahma.") returns all brahma parts.
        """
        return {
            name: part
            for name, part in self._parts.items()
            if name.startswith(prefix)
        }

    @property
    def center(self) -> T:
        """The center of the hologram (Krishna/Mahamantra)."""
        return self._center

    def all_names(self) -> FrozenSet[str]:
        """Get all registered names."""
        return frozenset(self._parts.keys())

    def count(self) -> int:
        """Count all parts."""
        return len(self._parts)


# =============================================================================
# COHERENCE - Keeping parts synchronized
# =============================================================================

class CoherenceLevel(str, Enum):
    """
    Levels of coherence between parts.

    Higher coherence = more synchronization = more consistency.
    """
    NONE = "none"           # Parts are independent
    EVENTUAL = "eventual"   # Parts eventually sync
    STRONG = "strong"       # Parts always in sync
    TOTAL = "total"         # Parts are ONE (non-dual)


@dataclass
class CoherencePolicy:
    """
    Policy for maintaining coherence.

    Defines how parts stay synchronized.
    """

    level: CoherenceLevel
    sync_on_read: bool = False   # Sync when reading
    sync_on_write: bool = True   # Sync when writing
    propagation_delay_ms: int = 0  # Delay before propagation (0 = immediate)


# =============================================================================
# REFLECTION - Get the whole from a part
# =============================================================================

class Reflector(Generic[T]):
    """
    Reflector - enables reflection from any point.

    Given any part, can reflect the entire system.
    This is the core of the holographic principle.
    """

    def __init__(self, hologram: Hologram[T]) -> None:
        self._hologram = hologram

    def reflect_from(self, part_name: str) -> Dict[str, T]:
        """
        Reflect the whole system from a specific part.

        The part you start from doesn't matter -
        you always get the complete picture.

        "yato va imani bhutani jayante" -
        From which all beings are born.
        """
        # In a true hologram, reflection is the same from any point
        return self._hologram.reflect()

    def find_related(self, part_name: str, relation: str) -> List[str]:
        """
        Find parts related to a given part.

        Relations:
        - "siblings": Same parent
        - "children": Direct descendants
        - "ancestors": All parents up to root
        - "provides": Parts that provide what this needs
        - "requires": Parts that need what this provides
        """
        parts = self._hologram.reflect()
        current = parts.get(part_name)
        if current is None:
            return []

        related: List[str] = []

        if relation == "siblings":
            # Same mahajana prefix
            prefix = part_name.rsplit(".", 1)[0] + "."
            related = [n for n in parts.keys() if n.startswith(prefix) and n != part_name]

        elif relation == "provides":
            # Parts that provide capabilities this one requires
            if hasattr(current, '__protocol_capability__'):
                cap = current.__protocol_capability__  # type: ignore
                for name, part in parts.items():
                    if hasattr(part, '__protocol_capability__'):
                        other_cap = part.__protocol_capability__  # type: ignore
                        if cap.requires & other_cap.provides:
                            related.append(name)

        return related


# =============================================================================
# PROJECTION - Get a part from the whole
# =============================================================================

class Projector(Generic[T]):
    """
    Projector - enables projection to any point.

    From the whole (or any point), can project to any specific location.
    Non-local access - distance doesn't matter.
    """

    def __init__(self, hologram: Hologram[T]) -> None:
        self._hologram = hologram

    def project_to(self, target_name: str) -> Optional[T]:
        """
        Project to a specific target.

        Direct access - no traversal needed.
        O(1) lookup regardless of structure depth.
        """
        return self._hologram.get(target_name)

    def project_by_capability(self, capability: str) -> List[Tuple[str, T]]:
        """
        Project to all parts that provide a capability.

        Returns all matching parts.
        """
        results: List[Tuple[str, T]] = []
        for name, part in self._hologram.reflect().items():
            if hasattr(part, '__protocol_capability__'):
                cap = part.__protocol_capability__  # type: ignore
                if capability in cap.provides:
                    results.append((name, part))
        return results

    def project_by_position(self, position: int) -> List[Tuple[str, T]]:
        """
        Project to all parts at a position.

        Returns all parts whose mahajana is at this position.
        """
        results: List[Tuple[str, T]] = []
        for name, part in self._hologram.reflect().items():
            if hasattr(part, '__protocol_identity__'):
                identity = part.__protocol_identity__  # type: ignore
                if identity.position == position:
                    results.append((name, part))
        return results


# =============================================================================
# HOLOGRAPHIC SYSTEM - The complete implementation
# =============================================================================

@dataclass
class HolographicSystem(Generic[T]):
    """
    A complete holographic system.

    Combines:
    - Hologram (the data structure)
    - Reflector (get whole from part)
    - Projector (get part from whole)
    - Coherence (keep in sync)

    This IS the Mahamantra architecture.
    """

    hologram: Hologram[T]
    reflector: Reflector[T] = field(init=False)
    projector: Projector[T] = field(init=False)
    coherence: CoherencePolicy = field(
        default_factory=lambda: CoherencePolicy(level=CoherenceLevel.STRONG)
    )

    def __post_init__(self) -> None:
        """Initialize reflector and projector."""
        self.reflector = Reflector(self.hologram)
        self.projector = Projector(self.hologram)

    def register(self, full_name: str, part: T) -> None:
        """Register a part."""
        self.hologram.register(full_name, part)

    def reflect(self, from_name: Optional[str] = None) -> Dict[str, T]:
        """
        Reflect the system.

        If from_name is given, reflect from that point (same result).
        If not, reflect from center.
        """
        if from_name:
            return self.reflector.reflect_from(from_name)
        return self.hologram.reflect()

    def project(self, to_name: str) -> Optional[T]:
        """Project to a specific part."""
        return self.projector.project_to(to_name)

    def find_provider(self, capability: str) -> Optional[Tuple[str, T]]:
        """Find a provider for a capability."""
        providers = self.projector.project_by_capability(capability)
        return providers[0] if providers else None

    @classmethod
    def create(cls, center: T) -> "HolographicSystem[T]":
        """Factory method to create a system."""
        hologram = Hologram(_center=center)
        return cls(hologram=hologram)


# =============================================================================
# HOLOGRAPHIC PROTOCOL - Self-reference
# =============================================================================

class HolographicProtocol(MahamantraProtocolBase):
    """
    The Holographic Protocol.

    This protocol defines how every part contains the whole.
    It IS itself holographic - accessible from anywhere.

    ACINTYA: Non-locality in code.
             Krishna is fully present in every atom.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="HolographicProtocol",
        mahajana="narada",  # Narada travels everywhere - non-locality
        position=2,
        level=Level.ACINTYA,
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "hologram",
            "reflection",
            "projection",
            "coherence",
            "non_locality",
            "whole_in_part",
        ],
        requires=["CoreProtocol", "FractalProtocol"],
        opcodes=["ALLOC_MEM"],  # Narada's opcode - memory/presence everywhere
    )


# Verify the holographic protocol
_valid, _violations = HolographicProtocol.validate()
assert _valid, f"HolographicProtocol failed validation: {_violations}"


# =============================================================================
# THE SINGLETON HOLOGRAM - The actual system
# =============================================================================

# The ONE holographic system (Krishna)
_system: Optional[HolographicSystem[Type[MahamantraProtocol]]] = None


def get_holographic_system() -> HolographicSystem[Type[MahamantraProtocol]]:
    """
    Get THE holographic system.

    SINGLETON: There is only ONE system - Krishna.
    """
    global _system
    if _system is None:
        # Initialize with CoreProtocol as center
        from vibe_core.mahamantra.protocols._core import CoreProtocol
        _system = HolographicSystem.create(CoreProtocol)
        _system.register("CoreProtocol", CoreProtocol)
        _system.register("HolographicProtocol", HolographicProtocol)
        _system.register("FractalProtocol", HolographicProtocol)  # Will fix import
    return _system


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Hologram
    "Hologram",
    # Coherence
    "CoherenceLevel",
    "CoherencePolicy",
    # Reflection & Projection
    "Reflector",
    "Projector",
    # System
    "HolographicSystem",
    # Protocol
    "HolographicProtocol",
    # Singleton
    "get_holographic_system",
]
