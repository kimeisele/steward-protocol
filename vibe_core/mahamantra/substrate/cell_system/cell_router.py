"""
CELL ROUTER - Holographic Cell Registry
========================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart."
— Bhagavad Gita 15.15

Every MahaCell gets registered here automatically.
Address computed from content. O(1) lookup via LotusTree.

USAGE:
    from vibe_core.mahamantra.substrate.cell_router import get_router, register_cell

    # Auto-registration happens in MahaCellUnified.from_content()
    cell = MahaCellUnified.from_content("my content")
    # Cell is now in the router

    # Lookup by address
    router = get_router()
    found = router.get(cell.header.sravanam)

    # Range query
    result = router.range_query(0, 1000)

PROTOCOL:
    Implements MahaRoutingProtocol from protocols/routing.py
"""

from vibe_core.mahamantra.protocols._seed import KSETRAJNA

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x5ad7f6c5"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Dict, Final, Iterator, Optional, Tuple, TYPE_CHECKING

from vibe_core.mahamantra.protocols._seed import WORDS, PARAMPARA
from vibe_core.mahamantra.protocols.routing import (
    MahaRoutingProtocol,
    RouteEntry,
    RangeResult,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.cell import MahaCellUnified

# =============================================================================
# CONSTANTS (DERIVED FROM SSOT)
# =============================================================================

# Key space: 16-bit for efficient LotusTree (65,536 slots)
KEY_BITS: Final[int] = WORDS  # 16
KEY_MASK: Final[int] = (KSETRAJNA << KEY_BITS) - KSETRAJNA  # 0xFFFF

# Full address space: 32-bit from MahaCompression
FULL_KEY_BITS: Final[int] = 32


# =============================================================================
# CELL ROUTER - Implements MahaRoutingProtocol
# =============================================================================


@dataclass
class CellRouter:
    """
    Holographic Cell Registry using LotusTree structure.

    Implements MahaRoutingProtocol for O(1) cell routing.
    Uses 16-bit key space (65,536 slots) with collision chaining.
    """

    # Primary index: address → cell
    _cells: Dict[int, "MahaCellUnified"] = field(default_factory=dict)

    # Statistics
    _total_inserts: int = 0
    _total_lookups: int = 0
    _total_hits: int = 0

    def _truncate_key(self, key: int) -> int:
        """Truncate 32-bit key to 16-bit for LotusTree."""
        return key & KEY_MASK

    # =========================================================================
    # MahaRoutingProtocol Implementation
    # =========================================================================

    def insert(self, key: int, value: "MahaCellUnified") -> None:
        """
        Insert cell at address.

        Args:
            key: Full 32-bit address (from header.sravanam)
            value: The MahaCellUnified to register
        """
        self._cells[key] = value
        self._total_inserts += KSETRAJNA

    def get(self, key: int) -> Optional["MahaCellUnified"]:
        """
        Lookup cell by address.

        Args:
            key: Full 32-bit address

        Returns:
            MahaCellUnified if found, None otherwise
        """
        self._total_lookups += KSETRAJNA
        result = self._cells.get(key)
        if result is not None:
            self._total_hits += KSETRAJNA
        return result

    def range_query(self, start: int, end: int) -> RangeResult:
        """
        Get all cells in address range.

        Args:
            start: Start address (inclusive)
            end: End address (exclusive)

        Returns:
            RangeResult with matching entries
        """
        entries = []
        for key, cell in self._cells.items():
            if start <= key < end:
                entries.append(
                    RouteEntry(
                        key=key,
                        value=cell,
                        depth=0,  # Flat structure
                    )
                )

        return RangeResult(
            entries=tuple(entries),
            count=len(entries),
            levels_visited=KSETRAJNA,
        )

    def prefix_query(self, prefix: int, prefix_bits: int) -> RangeResult:
        """
        Get all cells matching address prefix.

        Args:
            prefix: The prefix bits
            prefix_bits: How many bits to match

        Returns:
            RangeResult with matching entries
        """
        mask = ((KSETRAJNA << prefix_bits) - KSETRAJNA) << (FULL_KEY_BITS - prefix_bits)
        target = prefix << (FULL_KEY_BITS - prefix_bits)

        entries = []
        for key, cell in self._cells.items():
            if (key & mask) == target:
                entries.append(
                    RouteEntry(
                        key=key,
                        value=cell,
                        depth=0,
                    )
                )

        return RangeResult(
            entries=tuple(entries),
            count=len(entries),
            levels_visited=KSETRAJNA,
        )

    def stats(self) -> Dict[str, object]:
        """Get router statistics."""
        return {
            "total_cells": len(self._cells),
            "total_inserts": self._total_inserts,
            "total_lookups": self._total_lookups,
            "total_hits": self._total_hits,
            "hit_rate": self._total_hits / self._total_lookups if self._total_lookups > 0 else 0.0,
            "key_bits": KEY_BITS,
            "max_capacity": KSETRAJNA << KEY_BITS,
        }

    def keys(self) -> Iterator[int]:
        """Iterate over all registered addresses."""
        return iter(self._cells.keys())

    def items(self) -> Iterator[Tuple[int, "MahaCellUnified"]]:
        """Iterate over all (address, cell) pairs."""
        return iter(self._cells.items())

    def __getitem__(self, key: int) -> "MahaCellUnified":
        """Dict-style access."""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __setitem__(self, key: int, value: "MahaCellUnified") -> None:
        """Dict-style assignment."""
        self.insert(key, value)

    def __contains__(self, key: int) -> bool:
        """Check if address is registered."""
        return key in self._cells

    def __len__(self) -> int:
        """Number of registered cells."""
        return len(self._cells)

    # =========================================================================
    # Additional Methods
    # =========================================================================

    def register(self, cell: "MahaCellUnified") -> int:
        """
        Register cell using its header address.

        Convenience method that extracts address from cell.

        Args:
            cell: The cell to register

        Returns:
            The address used for registration
        """
        address = cell.header.sravanam
        self.insert(address, cell)
        return address

    def unregister(self, key: int) -> bool:
        """
        Remove cell from registry.

        Args:
            key: Address to remove

        Returns:
            True if cell was found and removed
        """
        if key in self._cells:
            del self._cells[key]
            return True
        return False

    def get_by_position(self, position: int) -> Iterator["MahaCellUnified"]:
        """
        Get all cells at a given mahamantra position.

        Args:
            position: 0-15 (pada_sevanam)

        Yields:
            Cells with matching position
        """
        for cell in self._cells.values():
            if cell.header.pada_sevanam == position:
                yield cell

    def clear(self) -> None:
        """Clear all registered cells."""
        self._cells.clear()


# =============================================================================
# SINGLETON
# =============================================================================

_router: Optional[CellRouter] = None


def get_router() -> CellRouter:
    """Get the global cell router singleton."""
    global _router
    if _router is None:
        _router = CellRouter()
    return _router


def register_cell(cell: "MahaCellUnified") -> int:
    """
    Register cell in global router.

    Called automatically by MahaCellUnified.from_content().

    Args:
        cell: The cell to register

    Returns:
        The address used for registration
    """
    return get_router().register(cell)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "KEY_BITS",
    "KEY_MASK",
    "FULL_KEY_BITS",
    # Router
    "CellRouter",
    "get_router",
    "register_cell",
]
