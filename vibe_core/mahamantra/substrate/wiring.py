"""
WIRING PROTOCOL - Folder IS Wiring
==================================

"yadā yadā hi dharmasya glānir bhavati bhārata"
"Whenever and wherever there is a decline in dharma..."
— Bhagavad Gita 4.7

THE LAW:
========

    IM FOLDER = LINKED
    KEIN FOLDER = EXISTIERT NICHT

This is GAD-000 applied to structure:
    "If it doesn't exist as protocol, it doesn't exist."

FOLDER = PROTOCOL = EXISTENCE = WIRING

DERIVES FROM SSOT:
    position.py → MAHAMANTRA_POSITIONS is the ONE source
    This file provides WIRING utilities derived from SSOT

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xa117b53a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)

# === DERIVE FROM SSOT ===
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)
from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.substrate.seed import (
    PARAMPARA,
    WORDS as TOTAL_POSITIONS,
    QUARTERS as QUARTER_COUNT,
    WORDS_PER_QUARTER as POSITIONS_PER_QUARTER,
)

# === EXPOSE PRITHU IMPLEMENTATION (The Avatar) ===
from vibe_core.mahamantra.dharma.prithu import PrithuService

# THE AVATAR MANIFESTS (Singleton)
# This allows mahamantra.mod.prithu to have .execute()
prithu = PrithuService()


# =============================================================================
# THE LAW: FOLDER = WIRING
# =============================================================================

FOLDER_IS_WIRING: Final[bool] = True
NO_FOLDER_NO_EXISTENCE: Final[bool] = True

# Fractal constants (derived from SSOT)
FRACTAL_BASE: Final[int] = TOTAL_POSITIONS  # 16^n scaling


# =============================================================================
# DERIVED LOOKUPS (from SSOT: MAHAMANTRA_POSITIONS)
# =============================================================================


def _get_guardian_name(pos: MantraPosition) -> str:
    """Get guardian name from MantraPosition."""
    if isinstance(pos.guardian, Avatara):
        return pos.guardian.value
    return pos.guardian.value


def _get_folder_path(pos: MantraPosition) -> str:
    """Derive folder path from MantraPosition."""
    return f"{pos.quarter.value}/{_get_guardian_name(pos)}"


# Build lookup tables DERIVED from MAHAMANTRA_POSITIONS (SSOT)
POSITION_BY_FOLDER: Final[Dict[str, MantraPosition]] = {_get_folder_path(pos): pos for pos in MAHAMANTRA_POSITIONS}

POSITION_BY_NAME: Final[Dict[str, MantraPosition]] = {_get_guardian_name(pos): pos for pos in MAHAMANTRA_POSITIONS}

POSITION_BY_INDEX: Final[Dict[int, MantraPosition]] = {pos.index: pos for pos in MAHAMANTRA_POSITIONS}


# =============================================================================
# FOLDER EXISTENCE CHECK
# =============================================================================


def folder_exists(folder_path: str) -> bool:
    """
    Check if protocol folder exists.

    FOLDER = EXISTENCE:
    If folder doesn't exist in SSOT mapping, protocol doesn't exist.

    PROTOCOL-FIRST: Checks MAHAMANTRA_POSITIONS, not filesystem.
    """
    return folder_path in POSITION_BY_FOLDER


def get_position_from_folder(folder_path: str) -> Optional[MantraPosition]:
    """
    Get position from folder path.

    FOLDER = WIRING:
    The folder path determines the position.

    DERIVED from MAHAMANTRA_POSITIONS.
    """
    return POSITION_BY_FOLDER.get(folder_path)


def get_position_from_name(name: str) -> Optional[MantraPosition]:
    """Get position from owner name. DERIVED from SSOT."""
    return POSITION_BY_NAME.get(name.lower())


def get_position_by_index(index: int) -> Optional[MantraPosition]:
    """Get position by index (0-15). DERIVED from SSOT."""
    return POSITION_BY_INDEX.get(index)


def get_position_by_opcode(opcode: MantraOpCode) -> Optional[MantraPosition]:
    """
    Get position by OpCode. DERIVED from SSOT.

    Routes operation to guardian.
    """
    for pos in MAHAMANTRA_POSITIONS:
        if pos.opcode == opcode:
            return pos
    return None


# =============================================================================
# WIRING PROTOCOL
# =============================================================================


@runtime_checkable
class WiringProtocol(Protocol):
    """
    Protocol for folder-based wiring.

    THE LAW:
        IM FOLDER = LINKED
        KEIN FOLDER = EXISTIERT NICHT
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index (0-15)."""
        ...

    @classmethod
    def folder_path(cls) -> str:
        """Get folder path (quarter/name)."""
        ...

    @classmethod
    def is_wired(cls) -> bool:
        """Check if properly wired (folder exists)."""
        ...

    @classmethod
    def parampara_vector(cls) -> int:
        """Get parampara vector."""
        ...


@dataclass
class WiringVerification:
    """
    Verification result for folder wiring.

    GAD-000:
        If it doesn't exist as protocol, it doesn't exist.
    """

    folder_path: str
    exists: bool
    position: Optional[int]
    is_connected: bool
    violations: List[str]

    @property
    def is_valid(self) -> bool:
        """Is the wiring valid?"""
        return self.exists and self.is_connected and len(self.violations) == 0


def verify_wiring(folder_path: str) -> WiringVerification:
    """
    Verify that a folder is properly wired.

    PROTOCOL-FIRST: Checks MAHAMANTRA_POSITIONS (SSOT).

    Checks:
    1. Folder exists in SSOT mapping
    2. Parampara connection is valid
    """
    violations: List[str] = []

    pos = get_position_from_folder(folder_path)

    if pos is None:
        violations.append(f"Folder '{folder_path}' not in MAHAMANTRA_POSITIONS")
        return WiringVerification(
            folder_path=folder_path,
            exists=False,
            position=None,
            is_connected=False,
            violations=violations,
        )

    if not pos.is_connected:
        violations.append(f"Position {pos.index} not connected to parampara")

    return WiringVerification(
        folder_path=folder_path,
        exists=True,
        position=pos.index,
        is_connected=pos.is_connected,
        violations=violations,
    )


# =============================================================================
# FRACTAL GROWTH
# =============================================================================


def calculate_fractal_depth(total_nodes: int) -> int:
    """
    Calculate fractal depth from total nodes.

    Level 0: 4 nodes (quarters)
    Level 1: 16 nodes (positions)
    Level 2: 256 nodes
    Level n: 16^n nodes
    """
    import math

    if total_nodes <= QUARTER_COUNT:
        return 0
    if total_nodes <= TOTAL_POSITIONS:
        return 1
    return int(math.log(total_nodes, FRACTAL_BASE)) + 1


def calculate_total_nodes(depth: int) -> int:
    """Calculate total nodes at fractal depth."""
    return FRACTAL_BASE**depth


# =============================================================================
# FRACTAL __getattr__ FACTORY (Pure Discovery)
# =============================================================================


def fractal_getattr(caller_file: str):
    """
    Create a __getattr__ function for fractal folder discovery.

    PURE FRACTAL: The filesystem IS the configuration.

    Args:
        caller_file: Pass __file__ from the calling module

    Returns:
        A __getattr__ function that discovers submodules dynamically

    Usage:
        # In vibe_core/mahamantra/genesis/__init__.py:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr
        __getattr__ = fractal_getattr(__file__)

        # Now: from vibe_core.mahamantra.genesis import brahma  # JUST WORKS
    """
    from pathlib import Path

    caller_path = Path(caller_file).resolve()
    caller_dir = caller_path.parent

    def _getattr(name: str):
        """
        Dynamic module/package discovery.

        Priority:
        1. Subpackage (folder with __init__.py)
        2. Module (.py file)
        3. Class discovery within module
        """
        import importlib

        # Skip private/dunder names
        if name.startswith("_"):
            raise AttributeError(f"module has no attribute '{name}'")

        # 1. Check for subpackage (folder with __init__.py)
        subpackage_dir = caller_dir / name
        if subpackage_dir.is_dir():
            init_file = subpackage_dir / "__init__.py"
            if init_file.exists():
                module_path = _compute_module_path(subpackage_dir)
                if module_path:
                    return importlib.import_module(module_path)

        # 2. Check for module (.py file)
        module_file = caller_dir / f"{name}.py"
        if module_file.exists():
            module_path = _compute_module_path(module_file)
            if module_path:
                module = importlib.import_module(module_path)

                # 3. Try to discover main class (same logic as adapters)
                main_class = _discover_main_class(module, name)
                if main_class:
                    return main_class

                return module

        raise AttributeError(f"module has no attribute '{name}'")

    def _compute_module_path(path: Path) -> Optional[str]:
        """Compute the full module path from filesystem path."""
        path = path.resolve()
        parts = path.parts
        try:
            vibe_idx = parts.index("vibe_core")
        except ValueError:
            return None

        module_parts = list(parts[vibe_idx:])
        if module_parts and module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]

        return ".".join(module_parts)

    def _discover_main_class(module, name: str):
        """Discover the main class in a module."""
        # 1. Try __all__
        if hasattr(module, "__all__") and module.__all__:
            first = module.__all__[0]
            if hasattr(module, first):
                obj = getattr(module, first)
                if isinstance(obj, type):
                    return obj()

        # 2. Try naming conventions
        name_cap = name.capitalize()
        candidates = [
            f"Maha{name_cap}",
            f"{name_cap}Service",
            f"{name_cap}",
            f"Lotus{name_cap}",
        ]
        for candidate in candidates:
            if hasattr(module, candidate):
                obj = getattr(module, candidate)
                if isinstance(obj, type):
                    return obj()

        # 3. First public class defined in this module
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue
            if "Result" in attr_name or "State" in attr_name:
                continue
            obj = getattr(module, attr_name)
            if isinstance(obj, type) and getattr(obj, "__module__", None) == module.__name__:
                return obj()

        return None

    return _getattr


def enable_fractal_discovery(caller_globals: dict, caller_file: str) -> None:
    """
    Enable fractal discovery for a module.

    EVEN SIMPLER USAGE:
        from vibe_core.mahamantra.substrate.wiring import enable_fractal_discovery
        enable_fractal_discovery(globals(), __file__)

        # Done. No __getattr__ assignment needed.
    """
    caller_globals["__getattr__"] = fractal_getattr(caller_file)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "FOLDER_IS_WIRING",
    "NO_FOLDER_NO_EXISTENCE",
    "POSITIONS_PER_QUARTER",
    "QUARTER_COUNT",
    "FRACTAL_BASE",
    # Lookup tables (DERIVED from SSOT)
    "POSITION_BY_FOLDER",
    "POSITION_BY_NAME",
    "POSITION_BY_INDEX",
    # Functions
    "folder_exists",
    "get_position_from_folder",
    "get_position_from_name",
    "get_position_by_index",
    # Protocol
    "WiringProtocol",
    "WiringVerification",
    "verify_wiring",
    # Fractal
    "calculate_fractal_depth",
    "calculate_total_nodes",
    # FRACTAL DISCOVERY
    "fractal_getattr",
    "enable_fractal_discovery",
]
