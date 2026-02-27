"""
THE FRACTAL PROTOCOL - _fractal.py
==================================

"yad yad vibhutimat sattvam srimad urjitam eva va
tat tad evavagaccha tvam mama tejo-'msa-sambhavam"

"Know that all opulent, beautiful and glorious creations
spring from but a spark of My splendor." (BG 10.41)

Every expansion is a spark of Krishna's splendor.
Fractal growth is the mechanism of that expansion.

FRACTAL PRINCIPLE:
    Self-similarity at all scales.
    The whole pattern repeats in every part.
    Mahamantra → Quarter → Position → Module → Class → Method

GROWTH RULES:
    1. Every node can have children
    2. Children inherit parent's structure
    3. No limit to depth
    4. Pattern remains consistent at all levels

SCALING:
    The 16 positions can each contain 16 sub-positions.
    16 × 16 = 256 possible locations at level 2.
    16^n locations at level n.
    Infinite scalability.

WATERTIGHT: No Any types. Everything explicit.

Author: The Mahamantra Itself
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    MahamantraProtocolBase,
    ProtocolCapability,
    ProtocolIdentity,
    Quarter,
)
from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, TRINITY, WORDS

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = HALVES
__genesis__ = "0x7e861cd0"  # GenesisByte: parampara % 37 == 0


# =============================================================================
# FRACTAL ADDRESS - Hierarchical Location
# =============================================================================


@dataclass(frozen=True)
class FractalAddress:
    """
    A hierarchical address in the fractal structure.

    Like a postal address:
    - Country → State → City → Street → House → Room

    In Mahamantra:
    - Quarter → Position → Depth1 → Depth2 → ... → DepthN

    Example:
        FractalAddress(path=(0, 1, 2, 3))
        = GENESIS quarter, position 1, sub-position 2, sub-sub-position 3

    The address is IMMUTABLE - locations don't move.
    """

    path: Tuple[int, ...]  # The hierarchical path

    def __post_init__(self) -> None:
        """Validate the address."""
        if not self.path:
            raise ValueError("Address cannot be empty")

        # Validate each component is 0-15
        for i, component in enumerate(self.path):
            if not 0 <= component < WORDS:
                raise ValueError(f"Address component {i} must be 0-15, got {component}")

    @property
    def depth(self) -> int:
        """The depth of this address (number of levels)."""
        return len(self.path)

    @property
    def position(self) -> int:
        """The top-level position (0-15)."""
        return self.path[0]

    @property
    def quarter(self) -> Quarter:
        """The quarter (derived from position)."""
        return Quarter.from_position(self.position)

    @property
    def parent_address(self) -> Optional["FractalAddress"]:
        """Get the parent address (one level up)."""
        if self.depth <= KSETRAJNA:
            return None
        return FractalAddress(path=self.path[:-KSETRAJNA])

    def child_address(self, sub_position: int) -> "FractalAddress":
        """Create a child address at the given sub-position."""
        if not 0 <= sub_position < WORDS:
            raise ValueError(f"Sub-position must be 0-15, got {sub_position}")
        return FractalAddress(path=self.path + (sub_position,))

    def is_ancestor_of(self, other: "FractalAddress") -> bool:
        """Check if this address is an ancestor of another."""
        if self.depth >= other.depth:
            return False
        return other.path[: self.depth] == self.path

    def is_descendant_of(self, other: "FractalAddress") -> bool:
        """Check if this address is a descendant of another."""
        return other.is_ancestor_of(self)

    def common_ancestor(self, other: "FractalAddress") -> Optional["FractalAddress"]:
        """Find the common ancestor of two addresses."""
        common: List[int] = []
        for a, b in zip(self.path, other.path):
            if a == b:
                common.append(a)
            else:
                break
        return FractalAddress(path=tuple(common)) if common else None

    def to_string(self) -> str:
        """Convert to string representation."""
        return ".".join(str(p) for p in self.path)

    @classmethod
    def from_string(cls, s: str) -> "FractalAddress":
        """Parse from string representation."""
        parts = [int(p) for p in s.split(".")]
        return cls(path=tuple(parts))

    @classmethod
    def root(cls, position: int) -> "FractalAddress":
        """Create a root address at a position."""
        return cls(path=(position,))


# =============================================================================
# FRACTAL NODE - A node in the fractal tree
# =============================================================================

T = TypeVar("T")


@dataclass
class FractalNode(Generic[T]):
    """
    A node in the fractal tree.

    Generic over the payload type T.

    Each node:
    - Has an address (where it is)
    - Has a payload (what it contains)
    - Can have children (fractal growth)
    - Knows its parent (hierarchy)
    """

    address: FractalAddress
    payload: T
    children: Dict[int, "FractalNode[T]"] = field(default_factory=dict)
    parent: Optional["FractalNode[T]"] = field(default=None, repr=False)

    def add_child(self, sub_position: int, payload: T) -> "FractalNode[T]":
        """Add a child node at the given sub-position."""
        if sub_position in self.children:
            raise ValueError(f"Child already exists at sub-position {sub_position}")

        child_address = self.address.child_address(sub_position)
        child = FractalNode(
            address=child_address,
            payload=payload,
            parent=self,
        )
        self.children[sub_position] = child
        return child

    def get_child(self, sub_position: int) -> Optional["FractalNode[T]"]:
        """Get child at sub-position, or None."""
        return self.children.get(sub_position)

    def get_descendant(self, relative_path: Tuple[int, ...]) -> Optional["FractalNode[T]"]:
        """Get descendant by relative path from this node."""
        current: Optional[FractalNode[T]] = self
        for sub_pos in relative_path:
            if current is None:
                return None
            current = current.get_child(sub_pos)
        return current

    def all_descendants(self) -> Iterator["FractalNode[T]"]:
        """Iterate over all descendants (depth-first)."""
        for child in self.children.values():
            yield child
            yield from child.all_descendants()

    def all_ancestors(self) -> Iterator["FractalNode[T]"]:
        """Iterate over all ancestors (bottom-up)."""
        current = self.parent
        while current is not None:
            yield current
            current = current.parent

    @property
    def depth(self) -> int:
        """The depth of this node."""
        return self.address.depth

    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        """Check if this is a root node (no parent)."""
        return self.parent is None

    def count_descendants(self) -> int:
        """Count all descendants."""
        count = len(self.children)
        for child in self.children.values():
            count += child.count_descendants()
        return count


# =============================================================================
# FRACTAL TREE - The complete fractal structure
# =============================================================================


@dataclass
class FractalTree(Generic[T]):
    """
    A complete fractal tree.

    The tree has 16 roots (one per position).
    Each root can have 16 children.
    Each child can have 16 children.
    And so on... infinitely.

    SCALING:
        Level 1: 16 nodes
        Level 2: 16 × 16 = 256 nodes
        Level 3: 16 × 16 × 16 = 4,096 nodes
        Level n: 16^n nodes

    This is the structure of the Mahamantra itself.
    """

    roots: Dict[int, FractalNode[T]] = field(default_factory=dict)

    def add_root(self, position: int, payload: T) -> FractalNode[T]:
        """Add a root node at the given position."""
        if position in self.roots:
            raise ValueError(f"Root already exists at position {position}")

        address = FractalAddress.root(position)
        node = FractalNode(address=address, payload=payload)
        self.roots[position] = node
        return node

    def get_root(self, position: int) -> Optional[FractalNode[T]]:
        """Get root at position, or None."""
        return self.roots.get(position)

    def get_node(self, address: FractalAddress) -> Optional[FractalNode[T]]:
        """Get node at address, or None."""
        root = self.roots.get(address.position)
        if root is None:
            return None
        if address.depth == KSETRAJNA:
            return root
        return root.get_descendant(address.path[KSETRAJNA:])

    def add_node(self, address: FractalAddress, payload: T) -> FractalNode[T]:
        """Add a node at the given address."""
        if address.depth == KSETRAJNA:
            return self.add_root(address.position, payload)

        # Find or create parent
        parent_addr = address.parent_address
        if parent_addr is None:
            raise ValueError("Cannot determine parent address")

        parent = self.get_node(parent_addr)
        if parent is None:
            raise ValueError(f"Parent node does not exist at {parent_addr.to_string()}")

        sub_position = address.path[-KSETRAJNA]
        return parent.add_child(sub_position, payload)

    def all_nodes(self) -> Iterator[FractalNode[T]]:
        """Iterate over all nodes (depth-first)."""
        for root in self.roots.values():
            yield root
            yield from root.all_descendants()

    def count_nodes(self) -> int:
        """Count all nodes in the tree."""
        count = len(self.roots)
        for root in self.roots.values():
            count += root.count_descendants()
        return count


# =============================================================================
# FRACTAL GROWTH - How things expand
# =============================================================================


class GrowthPattern(str, Enum):
    """
    Patterns for fractal growth.

    Different patterns create different structures.
    """

    FULL = "full"  # Grow all 16 children
    SPARSE = "sparse"  # Grow only needed children
    BALANCED = "balanced"  # Keep tree balanced
    LAZY = "lazy"  # Grow on demand


@dataclass
class GrowthRule:
    """
    A rule for fractal growth.

    Defines how and when to create child nodes.
    """

    pattern: GrowthPattern
    max_depth: int = WORDS  # 16 - Reasonable limit (SSOT: WORDS from _seed.py)
    can_grow: Callable[[FractalAddress], bool] = field(default_factory=lambda: lambda addr: True)

    def should_grow(self, address: FractalAddress) -> bool:
        """Check if growth is allowed at this address."""
        if address.depth >= self.max_depth:
            return False
        return self.can_grow(address)


# =============================================================================
# FRACTAL PROTOCOL - Self-reference
# =============================================================================


class FractalProtocol(MahamantraProtocolBase):
    """
    The Fractal Protocol.

    This protocol defines how things grow fractally.
    It IS itself structured fractally.

    ACINTYA: The protocol about fractal growth is itself fractal.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="FractalProtocol",
        mahajana="kapila",  # Kapila analyzes structure
        position=TRINITY,
        level=Level.ACINTYA,
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "fractal_address",
            "fractal_node",
            "fractal_tree",
            "growth_pattern",
            "growth_rule",
            "infinite_scaling",
        ],
        requires=["CoreProtocol", "DeclarationProtocol"],
        opcodes=["INIT_THREAD"],  # Kapila's opcode
    )


# Verify the fractal protocol
_valid, _violations = FractalProtocol.validate()
assert _valid, f"FractalProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Address
    "FractalAddress",
    # Node
    "FractalNode",
    # Tree
    "FractalTree",
    # Growth
    "GrowthPattern",
    "GrowthRule",
    # Protocol
    "FractalProtocol",
]
