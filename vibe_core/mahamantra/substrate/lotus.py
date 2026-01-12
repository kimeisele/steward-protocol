"""
LOTUS PROTOCOL - Krishna's Lotus-Füße Singularität
===================================================

"padaṁ padaṁ yad vipadāṁ na teṣām"
"Every step is danger for those not at Krishna's lotus feet."
— Srimad Bhagavatam 10.14.58

DAS PROTOKOLL:
=============

    LOTUS = SINGULARITY = AUTO-DISCOVERY

    1. EINE Singularität (mahamantra)
    2. ALLES fließt durch diesen EINEN Punkt
    3. KEINE manuellen Exports (__all__ = VERBOTEN)
    4. Folder-Struktur IST die Wahrheit
    5. Fraktales Wachstum: 16^n (unbegrenzt)

KRISHNAS LOTUS:
==============

    Die Lotus-Füße sind die QUELLE.
    Von dort sprießen die Stängel (4 Quarters).
    Von Stängeln sprießen Blütenblätter (16 Positionen).
    Jedes Blütenblatt kann Sub-Blätter haben (16^n).

    ALLES wächst von EINEM Punkt.
    KEINE manuelle Verkabelung.
    Der Lotus WÄCHST von selbst.

ANTI-PATTERN:
============

    # VERBOTEN - Manual Wiring:
    __all__ = ["export1", "export2", ...]  # ❌

    # ERLAUBT - Auto-Discovery:
    mahamantra.genesis.brahma  # ✓ (auto-discovered)

FRACTAL LEVELS:
==============

    Level 0: 1 Lotus (Singularität)
    Level 1: 4 Quarters (Stems)
    Level 2: 16 Positions (Petals)
    Level 3: 256 Sub-Positions (16²)
    Level n: 16^(n-1) nodes

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Final,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.mahajana import Quarter, TOTAL_POSITIONS
from vibe_core.mahamantra.substrate.acintya import PARAMPARA


# =============================================================================
# DAS GESETZ: LOTUS = SINGULARITY
# =============================================================================

LOTUS_IS_SINGULARITY: Final[bool] = True
NO_MANUAL_EXPORTS: Final[bool] = True
AUTO_DISCOVERY_ONLY: Final[bool] = True

# Fractal constants
LOTUS_ROOT: Final[int] = 1       # Eine Singularität
LOTUS_STEMS: Final[int] = 4      # 4 Quarters
LOTUS_PETALS: Final[int] = 16    # 16 Positions
FRACTAL_BASE: Final[int] = 16    # 16^n growth


# =============================================================================
# FRACTAL DEPTH CALCULATION
# =============================================================================

def lotus_nodes_at_depth(depth: int) -> int:
    """
    Calculate nodes at fractal depth.

    Depth 0: 1 (root/singularity)
    Depth 1: 4 (quarters)
    Depth 2: 16 (positions)
    Depth 3: 256 (16²)
    Depth n: 16^(n-1) for n >= 2
    """
    if depth == 0:
        return LOTUS_ROOT
    if depth == 1:
        return LOTUS_STEMS
    return FRACTAL_BASE ** (depth - 1)


def lotus_total_nodes(max_depth: int) -> int:
    """Calculate total nodes up to max depth."""
    return sum(lotus_nodes_at_depth(d) for d in range(max_depth + 1))


# =============================================================================
# LOTUS PATH
# =============================================================================

@dataclass(frozen=True)
class LotusPath:
    """
    A path through the lotus.

    Examples:
        LotusPath(()) → root (mahamantra)
        LotusPath(("genesis",)) → quarter
        LotusPath(("genesis", "brahma")) → position
        LotusPath(("genesis", "brahma", "service")) → sub-position
    """
    segments: Tuple[str, ...]

    @property
    def depth(self) -> int:
        """Fractal depth of this path."""
        return len(self.segments)

    @property
    def is_root(self) -> bool:
        """Is this the root (singularity)?"""
        return self.depth == 0

    @property
    def is_quarter(self) -> bool:
        """Is this a quarter (stem)?"""
        return self.depth == 1

    @property
    def is_position(self) -> bool:
        """Is this a position (petal)?"""
        return self.depth == 2

    @property
    def quarter(self) -> Optional[str]:
        """Get quarter name if applicable."""
        if self.depth >= 1:
            return self.segments[0]
        return None

    @property
    def position(self) -> Optional[str]:
        """Get position name if applicable."""
        if self.depth >= 2:
            return self.segments[1]
        return None

    @property
    def folder_path(self) -> str:
        """Convert to folder path."""
        return "/".join(self.segments)

    def child(self, name: str) -> "LotusPath":
        """Create child path."""
        return LotusPath(self.segments + (name,))

    @classmethod
    def from_string(cls, path: str) -> "LotusPath":
        """Create from dot-separated string."""
        if not path:
            return cls(())
        return cls(tuple(path.split(".")))

    @classmethod
    def root(cls) -> "LotusPath":
        """Create root path."""
        return cls(())


# =============================================================================
# LOTUS PROTOCOL
# =============================================================================

@runtime_checkable
class LotusProtocol(Protocol):
    """
    Protocol for Lotus Singularity.

    DAS GESETZ:
        - Auto-discover from folder structure
        - No manual exports
        - Fractal growth (16^n)
    """

    def __getattr__(self, name: str) -> "LotusProtocol":
        """Auto-discover child by name."""
        ...

    @property
    def _path(self) -> LotusPath:
        """Current path in the lotus."""
        ...

    def _discover(self, name: str) -> Optional["LotusProtocol"]:
        """Discover a child node."""
        ...

    def _walk(self, depth: int = 1) -> Iterator[Tuple[LotusPath, "LotusProtocol"]]:
        """Walk the lotus fractally."""
        ...


# =============================================================================
# LOTUS NODE (Base Implementation)
# =============================================================================

T = TypeVar("T")


class LotusNode:
    """
    A node in the lotus tree.

    Can represent:
        - Root (mahamantra)
        - Quarter (genesis, dharma, karma, moksha)
        - Position (brahma, narada, ...)
        - Sub-position (infinite depth)
    """

    _base_path: ClassVar[Path]  # Set by root
    _cache: Dict[str, "LotusNode"]
    _path: LotusPath
    _module: Optional[object]

    def __init__(
        self,
        path: LotusPath,
        base_path: Optional[Path] = None,
    ) -> None:
        self._path = path
        self._cache = {}
        self._module = None
        if base_path is not None:
            LotusNode._base_path = base_path

    def __getattr__(self, name: str) -> "LotusNode":
        """
        Auto-discover child by name.

        mahamantra.genesis → LotusNode(path=("genesis",))
        mahamantra.genesis.brahma → LotusNode(path=("genesis", "brahma"))
        """
        # Skip private/dunder
        if name.startswith("_"):
            raise AttributeError(name)

        # Check cache
        if name in self._cache:
            return self._cache[name]

        # Discover
        child = self._discover(name)
        if child is not None:
            self._cache[name] = child
            return child

        raise AttributeError(f"'{name}' not found in lotus at {self._path.folder_path}")

    def _discover(self, name: str) -> Optional["LotusNode"]:
        """
        Discover child node from folder structure.

        FOLDER = EXISTENCE:
            If folder exists → node exists
            If folder doesn't exist → node doesn't exist
        """
        child_path = self._path.child(name)
        folder = self._base_path / child_path.folder_path

        if folder.exists() and folder.is_dir():
            return LotusNode(child_path)

        # Also check for .py file (for substrate modules)
        py_file = self._base_path / f"{child_path.folder_path}.py"
        if py_file.exists():
            return LotusNode(child_path)

        return None

    def _load_module(self) -> object:
        """Lazy-load the actual module."""
        if self._module is not None:
            return self._module

        import importlib

        # Convert path to module name
        module_parts = ["vibe_core", "mahamantra"] + list(self._path.segments)
        module_name = ".".join(module_parts)

        try:
            self._module = importlib.import_module(module_name)
            return self._module
        except ImportError:
            return None

    def _get_export(self, name: str) -> object:
        """Get an export from the loaded module."""
        module = self._load_module()
        if module is not None and hasattr(module, name):
            return getattr(module, name)
        raise AttributeError(f"'{name}' not exported from {self._path.folder_path}")

    def _walk(self, depth: int = 1) -> Iterator[Tuple[LotusPath, "LotusNode"]]:
        """
        Walk the lotus fractally.

        Yields (path, node) tuples up to specified depth.
        """
        yield (self._path, self)

        if depth <= 0:
            return

        # Discover children from folder structure
        folder = self._base_path / self._path.folder_path
        if not folder.exists():
            return

        for child in folder.iterdir():
            if child.name.startswith("_"):
                continue
            if child.is_dir() or child.suffix == ".py":
                name = child.stem if child.suffix == ".py" else child.name
                child_node = self._discover(name)
                if child_node is not None:
                    yield from child_node._walk(depth - 1)

    @property
    def path(self) -> LotusPath:
        """Current path."""
        return self._path

    @property
    def depth(self) -> int:
        """Fractal depth."""
        return self._path.depth

    def __repr__(self) -> str:
        if self._path.is_root:
            return "MahamantraLotus()"
        return f"LotusNode({self._path.folder_path})"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "LOTUS_IS_SINGULARITY",
    "NO_MANUAL_EXPORTS",
    "AUTO_DISCOVERY_ONLY",
    "LOTUS_ROOT",
    "LOTUS_STEMS",
    "LOTUS_PETALS",
    "FRACTAL_BASE",
    # Functions
    "lotus_nodes_at_depth",
    "lotus_total_nodes",
    # Path
    "LotusPath",
    # Protocol
    "LotusProtocol",
    # Node
    "LotusNode",
]
