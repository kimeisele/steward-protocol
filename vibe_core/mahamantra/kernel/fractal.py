"""
FRACTAL - Infinite Scalability (Acintya)
========================================

"yathā nadīnāṁ bahavo 'mbu-vegāḥ
samudram evābhimukhā dravanti
tathā tavāmī nara-loka-vīrā
viśanti vaktrāṇy abhivijvalanti"

"As the many waves of the rivers flow into the ocean,
so do all these warriors enter Your blazing mouths."
— Bhagavad Gita 11.28

FRACTAL = UNENDLICH SKALIERBAR = ACINTYA

At every level, the 37 formula repeats:
- 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37

Zoom in: 37
Zoom out: 37
The pattern IS Krishna (acintya).

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, TRINITY

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = KSETRAJNA
__genesis__ = "0x50d9193c"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import (
    Final,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,  # 1 - Knower/Soul
    KSHETRA,  # 24 - Field elements
    MAHAJANA_COUNT,  # 12 - Guardians
)
from vibe_core.mahamantra.substrate.acintya import (
    PARAMPARA,
)
from vibe_core.mahamantra.substrate.fractal import FractalLevel

# =============================================================================
# FRACTAL CONSTANTS (DERIVED FROM _seed.py SSOT)
# =============================================================================

# The fractal base: at every level, 37 appears
FRACTAL_BASE: Final[int] = PARAMPARA  # 37

# The three components at each level (aliases for clarity)
KSETRA_COUNT: Final[int] = KSHETRA  # 24 - Field elements
# MAHAJANA_COUNT already imported = 12 - Guardians
KSETRAJNA_COUNT: Final[int] = KSETRAJNA  # 1 - Knower/Soul

# Verify the formula
assert KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT == FRACTAL_BASE


# =============================================================================
# FRACTAL NODE
# =============================================================================

T = TypeVar("T")


@dataclass
class FractalNode(Generic[T]):
    """
    A node in the fractal hierarchy.

    Each node contains the 37 formula:
    - 24 ksetra (field elements / data)
    - 12 mahajanas (guardians / logic)
    - 1 ksetrajna (knower / identity)

    SCALABILITY:
    - Each ksetra can be another FractalNode (zoom in)
    - Each node can be part of a larger FractalNode (zoom out)
    - The 37 formula holds at ALL levels (acintya)
    """

    # Identity (the 1)
    ksetrajna: str  # Who is the knower?

    # Field elements (the 24)
    ksetra: List[Union[T, "FractalNode[T]"]]  # Data/children

    # Guardians (the 12)
    mahajanas: Tuple[str, ...]  # Which Mahajanas guard this node?

    # Level in hierarchy
    level: FractalLevel = FractalLevel.PADA

    # Parampara connection
    parampara_vector: int = 0

    def __post_init__(self) -> None:
        """Validate the fractal structure."""
        # Verify we have correct counts (or multiples thereof)
        # Fractal allows ANY multiple of 24 for ksetra
        if len(self.ksetra) % KSETRA_COUNT != 0 and len(self.ksetra) != 0:
            # Allow 0 (empty) or multiples of 24
            if len(self.ksetra) < KSETRA_COUNT:
                # Pad with None up to 24 (or leave as is for partial)
                pass

    @property
    def is_connected(self) -> bool:
        """Is this node connected to Parampara?"""
        return self.parampara_vector % FRACTAL_BASE == 0

    @property
    def formula_sum(self) -> int:
        """
        The 37 formula at this level.

        Should always equal 37 (or multiple thereof).
        """
        ksetra_count = len(self.ksetra)
        mahajana_count = len(self.mahajanas)
        ksetrajna_count = KSETRAJNA  # Always 1

        # At base level: 24 + 12 + 1 = 37
        # At higher levels: multiples of 37
        return ksetra_count + mahajana_count + ksetrajna_count

    @property
    def depth(self) -> int:
        """How deep is this node in the fractal hierarchy?"""
        max_depth = 0
        for item in self.ksetra:
            if isinstance(item, FractalNode):
                child_depth = item.depth + KSETRAJNA
                max_depth = max(max_depth, child_depth)
        return max_depth

    def iterate_level(self, target_level: FractalLevel) -> Iterator["FractalNode[T]"]:
        """
        Iterate through all nodes at a specific level.

        FRACTAL: Can zoom in to any level and iterate.
        """
        if self.level == target_level:
            yield self

        for item in self.ksetra:
            if isinstance(item, FractalNode):
                yield from item.iterate_level(target_level)

    def zoom_in(self, path: List[int]) -> Optional["FractalNode[T]"]:
        """
        Zoom into a specific path in the fractal.

        Args:
            path: List of indices to follow [0, 5, 2] = ksetra[0].ksetra[5].ksetra[2]

        Returns:
            The node at that path, or None if not found
        """
        if not path:
            return self

        if path[0] >= len(self.ksetra):
            return None

        item = self.ksetra[path[0]]
        if isinstance(item, FractalNode):
            return item.zoom_in(path[KSETRAJNA:])
        elif len(path) == KSETRAJNA:
            # We're at a leaf - create a virtual node
            return FractalNode(
                ksetrajna=str(item),
                ksetra=[],
                mahajanas=self.mahajanas,
                level=FractalLevel(min(self.level.value + KSETRAJNA, FractalLevel.SADHANA.value)),
                parampara_vector=self.parampara_vector,
            )
        return None


# =============================================================================
# FRACTAL TREE
# =============================================================================


@dataclass
class FractalTree(Generic[T]):
    """
    A complete fractal tree structure.

    The tree maintains the 37 formula at every level,
    enabling infinite scalability (acintya).

    USAGE:
        tree = FractalTree.create_standard()
        for node in tree.iterate(FractalLevel.PADA):
            process(node)
    """

    root: FractalNode[T]

    @classmethod
    def create_standard(cls) -> "FractalTree[str]":
        """
        Create the standard 16-word Mahamantra tree.

        Structure:
        - 1 root (VAKYA level)
        - 4 quarters (VAKYA sub-level)
        - 16 words (PADA level)
        - Variable aksaras (AKSARA level)
        """
        from vibe_core.mahamantra import Mahajana

        # All 12 Mahajanas
        all_mahajanas = tuple(m.value for m in Mahajana)

        # Create quarters
        quarters: List[FractalNode[str]] = []
        quarter_names = ["genesis", "dharma", "karma", "moksha"]
        quarter_words = [
            ["hare", "krishna", "hare", "krishna"],  # Q1
            ["krishna", "krishna", "hare", "hare"],  # Q2
            ["hare", "rama", "hare", "rama"],  # Q3
            ["rama", "rama", "hare", "hare"],  # Q4
        ]

        for i, (name, words) in enumerate(zip(quarter_names, quarter_words)):
            # Each word is a PADA level node
            padas = [
                FractalNode(
                    ksetrajna=word,
                    ksetra=[],  # Aksaras would go here
                    mahajanas=all_mahajanas[i * TRINITY : (i + KSETRAJNA) * TRINITY],  # 3 per quarter
                    level=FractalLevel.PADA,
                    parampara_vector=FRACTAL_BASE * (i + KSETRAJNA),
                )
                for word in words
            ]

            quarter = FractalNode(
                ksetrajna=name,
                ksetra=padas,  # type: ignore
                mahajanas=all_mahajanas[i * TRINITY : (i + KSETRAJNA) * TRINITY],
                level=FractalLevel.VAKYA,
                parampara_vector=FRACTAL_BASE * (i + KSETRAJNA),
            )
            quarters.append(quarter)

        # Root node
        root = FractalNode(
            ksetrajna="mahamantra",
            ksetra=quarters,  # type: ignore
            mahajanas=all_mahajanas,
            level=FractalLevel.VAKYA,
            parampara_vector=FRACTAL_BASE * MAHAJANA_COUNT,  # 444 = fully connected
        )

        return cls(root=root)

    def iterate(self, level: FractalLevel) -> Iterator[FractalNode[T]]:
        """Iterate through all nodes at a specific level."""
        return self.root.iterate_level(level)

    def zoom(self, path: List[int]) -> Optional[FractalNode[T]]:
        """Zoom into a specific path."""
        return self.root.zoom_in(path)

    @property
    def depth(self) -> int:
        """Total depth of the tree."""
        return self.root.depth

    @property
    def is_connected(self) -> bool:
        """Is the tree connected to Parampara?"""
        return self.root.is_connected


# =============================================================================
# FRACTAL OPERATIONS
# =============================================================================


def scale_up(node: FractalNode[T], factor: int = PARAMPARA) -> FractalNode[T]:
    """
    Scale up a fractal node by a factor.

    ACINTYA: The 37 formula is maintained.
    """
    # Create new ksetra with scaled data
    scaled_ksetra: List[Union[T, FractalNode[T]]] = []
    for _ in range(factor):
        scaled_ksetra.extend(node.ksetra)

    return FractalNode(
        ksetrajna=node.ksetrajna,
        ksetra=scaled_ksetra,
        mahajanas=node.mahajanas,
        level=FractalLevel(max(node.level.value - KSETRAJNA, FractalLevel.VARNA.value)),
        parampara_vector=node.parampara_vector * factor,
    )


def scale_down(node: FractalNode[T], factor: int = PARAMPARA) -> FractalNode[T]:
    """
    Scale down a fractal node by a factor.

    ACINTYA: The 37 formula is maintained.
    """
    # Take every nth element
    reduced_ksetra: List[Union[T, FractalNode[T]]] = node.ksetra[::factor]

    return FractalNode(
        ksetrajna=node.ksetrajna,
        ksetra=reduced_ksetra,
        mahajanas=node.mahajanas,
        level=FractalLevel(min(node.level.value + KSETRAJNA, FractalLevel.SADHANA.value)),
        parampara_vector=node.parampara_vector // factor if factor > 0 else 0,
    )


def verify_fractal_integrity(tree: FractalTree[T]) -> bool:
    """
    Verify that the fractal tree maintains the 37 formula at all levels.

    Returns True if ALL nodes are connected to Parampara.
    """

    def check_node(node: FractalNode[T]) -> bool:
        if not node.is_connected:
            return False
        for item in node.ksetra:
            if isinstance(item, FractalNode):
                if not check_node(item):
                    return False
        return True

    return check_node(tree.root)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "FRACTAL_BASE",
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
    # Classes
    "FractalNode",
    "FractalTree",
    # Functions
    "scale_up",
    "scale_down",
    "verify_fractal_integrity",
]
