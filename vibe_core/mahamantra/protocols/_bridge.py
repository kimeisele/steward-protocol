"""
THE BRIDGE PROTOCOL - _bridge.py
================================

"setu-bandhana" - The building of the bridge.
As Rama built the bridge to Lanka, we build bridges in code.

THE BRIDGE PROTOCOL
===================

Bridges connect different parts of the system:
- Level bridges: Connect different levels (-2 to +4)
- Quarter bridges: Connect different quarters
- System bridges: Connect different systems (legacy ↔ mahamantra)
- Interface bridges: Connect code ↔ user

FRACTAL BRIDGES:
    Every bridge can have sub-bridges.
    A Level bridge can contain Quarter bridges.
    A Quarter bridge can contain Protocol bridges.
    And so on... infinitely.

HOLOGRAPHIC BRIDGES:
    From any bridge, you can access any other bridge.
    The bridge network IS the system.

IMPORTANT:
    This is the PROTOCOL DEFINITION - the abstract structure.
    It imports ONLY from mahamantra/protocols/ (acintya level).

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Callable,
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
)


# =============================================================================
# BRIDGE TYPES - What kind of bridges exist
# =============================================================================

class BridgeType(str, Enum):
    """Types of bridges in the system."""
    LEVEL = "level"           # Connects different levels
    QUARTER = "quarter"       # Connects different quarters
    PROTOCOL = "protocol"     # Connects different protocols
    SYSTEM = "system"         # Connects different systems
    INTERFACE = "interface"   # Connects code to user
    MIGRATION = "migration"   # Connects legacy to new


class BridgeDirection(str, Enum):
    """Direction of bridge traversal."""
    UNIDIRECTIONAL = "uni"    # One way only
    BIDIRECTIONAL = "bi"      # Both directions
    UPSTREAM = "up"           # From lower to higher
    DOWNSTREAM = "down"       # From higher to lower


class BridgeState(str, Enum):
    """Current state of a bridge."""
    BLUEPRINT = "blueprint"   # Not yet built
    BUILDING = "building"     # Under construction
    ACTIVE = "active"         # Operational
    SUSPENDED = "suspended"   # Temporarily paused
    DEPRECATED = "deprecated" # Marked for removal
    DESTROYED = "destroyed"   # No longer exists


# =============================================================================
# BRIDGE ENDPOINT - One side of a bridge
# =============================================================================

@dataclass(frozen=True)
class BridgeEndpoint:
    """
    One endpoint of a bridge.

    Can be a level, quarter, protocol, or system.
    """

    name: str               # Identifier
    endpoint_type: str      # "level", "quarter", "protocol", "system"
    level: Optional[Level] = None
    quarter: Optional[Quarter] = None
    position: Optional[int] = None

    @property
    def address(self) -> str:
        """Get the full address of this endpoint."""
        parts = [self.endpoint_type, self.name]
        if self.level is not None:
            parts.append(f"L{self.level.value}")
        if self.quarter is not None:
            parts.append(self.quarter.value)
        if self.position is not None:
            parts.append(f"P{self.position}")
        return ".".join(parts)

    @classmethod
    def from_level(cls, level: Level) -> "BridgeEndpoint":
        """Create endpoint for a level."""
        return cls(
            name=level.name,
            endpoint_type="level",
            level=level,
        )

    @classmethod
    def from_quarter(cls, quarter: Quarter) -> "BridgeEndpoint":
        """Create endpoint for a quarter."""
        return cls(
            name=quarter.value,
            endpoint_type="quarter",
            quarter=quarter,
        )

    @classmethod
    def from_protocol(cls, name: str, level: Level, quarter: Quarter) -> "BridgeEndpoint":
        """Create endpoint for a protocol."""
        return cls(
            name=name,
            endpoint_type="protocol",
            level=level,
            quarter=quarter,
        )

    @classmethod
    def from_system(cls, name: str) -> "BridgeEndpoint":
        """Create endpoint for a system."""
        return cls(
            name=name,
            endpoint_type="system",
        )


# =============================================================================
# BRIDGE SPEC - The specification of a bridge
# =============================================================================

@dataclass(frozen=True)
class BridgeSpec:
    """
    Specification for a bridge.

    Defines what the bridge connects and how.
    """

    name: str
    bridge_type: BridgeType
    source: BridgeEndpoint
    target: BridgeEndpoint
    direction: BridgeDirection = BridgeDirection.BIDIRECTIONAL

    # Fractal address (bridges can be nested)
    parent_bridge: Optional[str] = None

    @property
    def is_level_crossing(self) -> bool:
        """Does this bridge cross levels?"""
        return self.source.level != self.target.level

    @property
    def is_quarter_crossing(self) -> bool:
        """Does this bridge cross quarters?"""
        return self.source.quarter != self.target.quarter

    @property
    def full_name(self) -> str:
        """Get the full name including parent."""
        if self.parent_bridge:
            return f"{self.parent_bridge}.{self.name}"
        return self.name


# =============================================================================
# BRIDGE - The actual bridge instance
# =============================================================================

T = TypeVar("T")
S = TypeVar("S")


@dataclass
class Bridge(Generic[T, S]):
    """
    A bridge between two parts of the system.

    Generic over:
    - T: The type on the source side
    - S: The type on the target side

    The bridge can transform between T and S.
    """

    spec: BridgeSpec
    state: BridgeState = BridgeState.BLUEPRINT

    # Transform functions
    _to_target: Optional[Callable[[T], S]] = field(default=None, repr=False)
    _to_source: Optional[Callable[[S], T]] = field(default=None, repr=False)

    # Child bridges (fractal)
    _children: Dict[str, "Bridge"] = field(default_factory=dict, repr=False)

    def set_transforms(
        self,
        to_target: Callable[[T], S],
        to_source: Optional[Callable[[S], T]] = None,
    ) -> None:
        """Set the transform functions."""
        self._to_target = to_target
        self._to_source = to_source

    def cross_to_target(self, value: T) -> S:
        """Cross the bridge from source to target."""
        if self._to_target is None:
            raise ValueError(f"Bridge {self.spec.name} has no to_target transform")
        if self.state != BridgeState.ACTIVE:
            raise ValueError(f"Bridge {self.spec.name} is not active (state: {self.state})")
        return self._to_target(value)

    def cross_to_source(self, value: S) -> T:
        """Cross the bridge from target to source."""
        if self._to_source is None:
            raise ValueError(f"Bridge {self.spec.name} has no to_source transform")
        if self.state != BridgeState.ACTIVE:
            raise ValueError(f"Bridge {self.spec.name} is not active (state: {self.state})")
        return self._to_source(value)

    def activate(self) -> None:
        """Activate the bridge."""
        if self._to_target is None:
            raise ValueError(f"Cannot activate bridge {self.spec.name}: no transforms set")
        self.state = BridgeState.ACTIVE

    def suspend(self) -> None:
        """Suspend the bridge."""
        self.state = BridgeState.SUSPENDED

    def deprecate(self) -> None:
        """Mark bridge as deprecated."""
        self.state = BridgeState.DEPRECATED

    def destroy(self) -> None:
        """Destroy the bridge."""
        self.state = BridgeState.DESTROYED
        self._to_target = None
        self._to_source = None

    # === FRACTAL: Child bridges ===

    def add_child(self, child: "Bridge") -> None:
        """Add a child bridge (fractal growth)."""
        self._children[child.spec.name] = child

    def get_child(self, name: str) -> Optional["Bridge"]:
        """Get a child bridge."""
        return self._children.get(name)

    def all_children(self) -> List["Bridge"]:
        """Get all child bridges."""
        return list(self._children.values())


# =============================================================================
# BRIDGE PROTOCOL - The Interface
# =============================================================================

@runtime_checkable
class BridgeProtocol(Protocol):
    """
    The Bridge Protocol - How bridges work.

    Any bridge implementation must satisfy this interface.

    WATERTIGHT - no Any types!
    """

    @property
    def spec(self) -> BridgeSpec:
        """Get the bridge specification."""
        ...

    @property
    def state(self) -> BridgeState:
        """Get the current state."""
        ...

    def activate(self) -> None:
        """Activate the bridge."""
        ...

    def suspend(self) -> None:
        """Suspend the bridge."""
        ...

    def deprecate(self) -> None:
        """Mark as deprecated."""
        ...


# =============================================================================
# BRIDGE REGISTRY - Tracks all bridges
# =============================================================================

class BridgeRegistry:
    """
    Registry of all bridges in the system.

    Provides:
    - Registration of bridges
    - Lookup by name
    - Routing through bridges
    - Health monitoring
    """

    _instance: ClassVar[Optional["BridgeRegistry"]] = None

    def __new__(cls) -> "BridgeRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._bridges = {}
            cls._instance._by_type = {}
        return cls._instance

    _bridges: Dict[str, Bridge]
    _by_type: Dict[BridgeType, List[str]]

    def register(self, bridge: Bridge) -> None:
        """Register a bridge."""
        name = bridge.spec.full_name
        self._bridges[name] = bridge

        # Index by type
        btype = bridge.spec.bridge_type
        if btype not in self._by_type:
            self._by_type[btype] = []
        self._by_type[btype].append(name)

    def get(self, name: str) -> Optional[Bridge]:
        """Get a bridge by name."""
        return self._bridges.get(name)

    def get_by_type(self, bridge_type: BridgeType) -> List[Bridge]:
        """Get all bridges of a type."""
        names = self._by_type.get(bridge_type, [])
        return [self._bridges[n] for n in names if n in self._bridges]

    def get_active(self) -> List[Bridge]:
        """Get all active bridges."""
        return [b for b in self._bridges.values() if b.state == BridgeState.ACTIVE]

    def get_deprecated(self) -> List[Bridge]:
        """Get all deprecated bridges."""
        return [b for b in self._bridges.values() if b.state == BridgeState.DEPRECATED]

    def find_path(self, source: BridgeEndpoint, target: BridgeEndpoint) -> List[Bridge]:
        """
        Find a path of bridges from source to target.

        Returns the sequence of bridges to traverse.
        """
        # Simple implementation: find direct bridge first
        for bridge in self._bridges.values():
            if bridge.state != BridgeState.ACTIVE:
                continue
            if (bridge.spec.source.address == source.address and
                bridge.spec.target.address == target.address):
                return [bridge]
            if (bridge.spec.direction == BridgeDirection.BIDIRECTIONAL and
                bridge.spec.source.address == target.address and
                bridge.spec.target.address == source.address):
                return [bridge]

        # TODO: Implement multi-hop path finding
        return []

    def all_bridges(self) -> List[Bridge]:
        """Get all registered bridges."""
        return list(self._bridges.values())

    def count(self) -> int:
        """Count all bridges."""
        return len(self._bridges)

    def clear(self) -> None:
        """Clear the registry (for testing)."""
        self._bridges.clear()
        self._by_type.clear()


# =============================================================================
# BRIDGE BUILDERS - Fluent API for creating bridges
# =============================================================================

class BridgeBuilder(Generic[T, S]):
    """
    Fluent builder for bridges.

    Usage:
        bridge = BridgeBuilder[int, str]("my_bridge") \
            .from_level(Level.SUBSTRATE) \
            .to_level(Level.CONTRACT) \
            .with_transform(lambda x: str(x)) \
            .build()
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._bridge_type = BridgeType.PROTOCOL
        self._source: Optional[BridgeEndpoint] = None
        self._target: Optional[BridgeEndpoint] = None
        self._direction = BridgeDirection.BIDIRECTIONAL
        self._to_target: Optional[Callable[[T], S]] = None
        self._to_source: Optional[Callable[[S], T]] = None
        self._parent: Optional[str] = None

    def of_type(self, bridge_type: BridgeType) -> "BridgeBuilder[T, S]":
        """Set bridge type."""
        self._bridge_type = bridge_type
        return self

    def from_level(self, level: Level) -> "BridgeBuilder[T, S]":
        """Set source as a level."""
        self._source = BridgeEndpoint.from_level(level)
        self._bridge_type = BridgeType.LEVEL
        return self

    def to_level(self, level: Level) -> "BridgeBuilder[T, S]":
        """Set target as a level."""
        self._target = BridgeEndpoint.from_level(level)
        return self

    def from_quarter(self, quarter: Quarter) -> "BridgeBuilder[T, S]":
        """Set source as a quarter."""
        self._source = BridgeEndpoint.from_quarter(quarter)
        self._bridge_type = BridgeType.QUARTER
        return self

    def to_quarter(self, quarter: Quarter) -> "BridgeBuilder[T, S]":
        """Set target as a quarter."""
        self._target = BridgeEndpoint.from_quarter(quarter)
        return self

    def from_system(self, name: str) -> "BridgeBuilder[T, S]":
        """Set source as a system."""
        self._source = BridgeEndpoint.from_system(name)
        self._bridge_type = BridgeType.SYSTEM
        return self

    def to_system(self, name: str) -> "BridgeBuilder[T, S]":
        """Set target as a system."""
        self._target = BridgeEndpoint.from_system(name)
        return self

    def from_endpoint(self, endpoint: BridgeEndpoint) -> "BridgeBuilder[T, S]":
        """Set source endpoint."""
        self._source = endpoint
        return self

    def to_endpoint(self, endpoint: BridgeEndpoint) -> "BridgeBuilder[T, S]":
        """Set target endpoint."""
        self._target = endpoint
        return self

    def direction(self, direction: BridgeDirection) -> "BridgeBuilder[T, S]":
        """Set direction."""
        self._direction = direction
        return self

    def with_transform(
        self,
        to_target: Callable[[T], S],
        to_source: Optional[Callable[[S], T]] = None,
    ) -> "BridgeBuilder[T, S]":
        """Set transform functions."""
        self._to_target = to_target
        self._to_source = to_source
        return self

    def under(self, parent: str) -> "BridgeBuilder[T, S]":
        """Set parent bridge (fractal)."""
        self._parent = parent
        return self

    def build(self) -> Bridge[T, S]:
        """Build the bridge."""
        if self._source is None or self._target is None:
            raise ValueError("Bridge must have source and target")

        spec = BridgeSpec(
            name=self._name,
            bridge_type=self._bridge_type,
            source=self._source,
            target=self._target,
            direction=self._direction,
            parent_bridge=self._parent,
        )

        bridge: Bridge[T, S] = Bridge(spec=spec)

        if self._to_target is not None:
            bridge.set_transforms(self._to_target, self._to_source)

        return bridge


# =============================================================================
# BRIDGE PROTOCOL DEFINITION - Self-Reference
# =============================================================================

class BridgeProtocolDef(MahamantraProtocolBase):
    """
    The Bridge Protocol.

    This protocol defines how bridges work.
    It IS itself a bridge (Narada - who travels everywhere).

    ACINTYA: The Bridge Protocol is a bridge.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="BridgeProtocol",
        mahajana="narada",  # Narada travels between worlds
        position=2,
        level=Level.CONTRACT,
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "bridge_types",
            "bridge_endpoints",
            "bridge_registry",
            "bridge_routing",
            "bridge_transforms",
            "fractal_bridges",
        ],
        requires=["CoreProtocol", "FractalProtocol"],
        opcodes=["ALLOC_MEM"],  # Narada's opcode - memory/presence everywhere
    )


# Verify the bridge protocol
_valid, _violations = BridgeProtocolDef.validate()
assert _valid, f"BridgeProtocol failed validation: {_violations}"


# =============================================================================
# CONVENIENCE: Get the global registry
# =============================================================================

def get_bridge_registry() -> BridgeRegistry:
    """Get the global bridge registry."""
    return BridgeRegistry()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "BridgeType",
    "BridgeDirection",
    "BridgeState",
    # Types
    "BridgeEndpoint",
    "BridgeSpec",
    "Bridge",
    # Protocol
    "BridgeProtocol",
    # Registry
    "BridgeRegistry",
    "get_bridge_registry",
    # Builder
    "BridgeBuilder",
    # Protocol Definition
    "BridgeProtocolDef",
]
