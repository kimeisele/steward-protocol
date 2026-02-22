"""
LOTUS FINDER - Import-Level Routing (The Missing Bridge)
========================================================

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya"
"O Arjuna, there is no truth superior to Me."
— Bhagavad Gita 7.7

THE PROBLEM:
    778 files write: from vibe_core.mahamantra.substrate.seed import X
    This couples them to the PHYSICAL LOCATION of seed.py.
    Move seed.py → 82 files break.

    The Lotus (LotusNode.__getattr__) routes at RUNTIME.
    But Python's import system routes at IMPORT TIME.
    These are two separate discovery mechanisms.
    Until now, they were disconnected.

THE SOLUTION:
    A sys.meta_path Finder that makes Python's import system
    go through the Lotus principle: FOLDER = EXISTENCE = WIRING.

    When Python asks "where is vibe_core.mahamantra.substrate.seed?",
    the LotusFinder scans the substrate tree to find seed.py —
    wherever it actually lives. Move seed.py to substrate/core/seed.py,
    the finder resolves it. Zero breakage.

    This is NOT a redirect table. This is DISCOVERY.
    The finder builds its map from the filesystem, just like LotusNode.
    No hardcoded dicts. No manual wiring.

INSTALLATION:
    Called once at mahamantra package init time.
    Must be installed BEFORE any substrate imports happen.

    import vibe_core.mahamantra.substrate.lotus_finder as lf
    lf.install()

DESIGN PRINCIPLES:
    1. ZERO BREAKAGE: All existing imports continue to work unchanged.
    2. FOLDER = EXISTENCE: If a .py file exists anywhere in substrate/,
       it's discoverable at its original import path.
    3. LAZY: The module map is built on first miss, not at install time.
    4. TRANSPARENT: If the file IS at the expected location, Python's
       normal import handles it. The finder only activates on MISS.
    5. NO LOGIC IN __init__.py: The finder replaces _LAZY_IMPORTS.
       __init__.py can become a clean, empty file.
"""

from __future__ import annotations

__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x00000000"

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional, Sequence

logger = logging.getLogger("LOTUS.FINDER")

# The root of the substrate package on disk
_SUBSTRATE_ROOT: Path = Path(__file__).parent

# The dotted prefix we intercept
_SUBSTRATE_PREFIX = "vibe_core.mahamantra.substrate."

# Cache: module_name (e.g. "seed") -> absolute Path to .py file
_MODULE_MAP: Optional[Dict[str, Path]] = None


def _build_module_map() -> Dict[str, Path]:
    """
    Scan the substrate tree and build a map of module_name -> file_path.

    LOTUS PRINCIPLE: FOLDER = EXISTENCE = WIRING.
    If a .py file exists, it's in the map. Period.

    This handles:
    - Flat files: substrate/seed.py -> "seed"
    - Nested files: substrate/core/seed.py -> "seed" (if substrate/seed.py doesn't exist)
    - Subpackages: substrate/language/ -> "language" (if __init__.py exists)

    Priority: direct child wins over nested child (backward compat).
    """
    module_map: Dict[str, Path] = {}

    # Pass 1: Direct children (highest priority — current layout)
    for py_file in _SUBSTRATE_ROOT.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        name = py_file.stem
        module_map[name] = py_file

    # Pass 1b: Direct subpackages
    for child_dir in _SUBSTRATE_ROOT.iterdir():
        if child_dir.is_dir() and not child_dir.name.startswith(("_", ".")):
            init = child_dir / "__init__.py"
            if init.exists():
                module_map[child_dir.name] = init

    # Pass 2: Nested .py files (lower priority — for AFTER reorganization)
    # Only register if the name isn't already taken by a direct child.
    # COLLISION DETECTION: crash hard if two nested files share a stem.
    # Collect ALL nested files first, then detect collisions
    nested_by_name: Dict[str, list] = {}
    for py_file in _SUBSTRATE_ROOT.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        if py_file.parent == _SUBSTRATE_ROOT:
            continue
        name = py_file.stem
        nested_by_name.setdefault(name, []).append(py_file)

    for name, paths in sorted(nested_by_name.items()):
        # Direct child already owns this name — skip (direct wins)
        if name in module_map:
            continue
        # Two nested files with same stem — COLLISION
        if len(paths) > 1:
            collision_paths = [str(p.relative_to(_SUBSTRATE_ROOT)) for p in paths]
            raise ImportError(
                f"[LOTUS.FINDER] NAMESPACE COLLISION: '{name}' found in "
                f"{collision_paths}. Rename one or add a direct child "
                f"substrate/{name}.py to disambiguate."
            )
        module_map[name] = paths[0]

    logger.debug("[LOTUS.FINDER] Built module map: %d modules", len(module_map))
    return module_map


def _get_module_map() -> Dict[str, Path]:
    """Get or build the module map (lazy singleton)."""
    global _MODULE_MAP
    if _MODULE_MAP is None:
        _MODULE_MAP = _build_module_map()
    return _MODULE_MAP


def invalidate_cache() -> None:
    """
    Invalidate the module map cache.

    Call this after moving files to force re-scan.
    The next import will rebuild the map from the filesystem.
    """
    global _MODULE_MAP
    _MODULE_MAP = None


class _LotusLoader(importlib.abc.Loader):
    """Loader that loads a module from a resolved file path."""

    def __init__(self, fullname: str, path: Path) -> None:
        self._fullname = fullname
        self._path = path

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> Optional[ModuleType]:
        return None  # Use default module creation

    def exec_module(self, module: ModuleType) -> None:
        # Set __file__ BEFORE execution so class-level Path(__file__) works
        module.__file__ = str(self._path)
        module.__loader__ = self
        if hasattr(module, "__spec__") and module.__spec__ is not None:
            module.__spec__.origin = str(self._path)
        # Use the standard SourceFileLoader to actually execute the module
        loader = importlib.machinery.SourceFileLoader(self._fullname, str(self._path))
        loader.exec_module(module)


class LotusFinder(importlib.abc.MetaPathFinder):
    """
    MetaPath Finder that resolves substrate modules via Lotus discovery.

    ONLY activates when Python's normal import FAILS to find the module.
    This means:
    - If seed.py is at substrate/seed.py (current layout), Python finds it
      normally. The finder never fires. Zero overhead.
    - If seed.py is MOVED to substrate/core/seed.py, Python's normal import
      fails. The finder activates, scans the tree, finds it. Zero breakage.

    This is the bridge between Python's import system and the Lotus principle.
    """

    def find_module(self, fullname: str, path: Optional[Sequence[str]] = None):
        """Legacy API — delegate to find_spec."""
        spec = self.find_spec(fullname, path)
        if spec is not None:
            return spec.loader
        return None

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]],
        target: Optional[ModuleType] = None,
    ) -> Optional[importlib.machinery.ModuleSpec]:
        """
        Find a module spec for a substrate module.

        Only intercepts vibe_core.mahamantra.substrate.X imports.
        Only activates when the module ISN'T already found by Python.
        """
        # Only handle substrate submodules
        if not fullname.startswith(_SUBSTRATE_PREFIX):
            return None

        # Extract the module name after "vibe_core.mahamantra.substrate."
        remainder = fullname[len(_SUBSTRATE_PREFIX) :]

        # Only handle direct submodules (e.g., "seed"), not deep paths
        # (e.g., "language.engine" — Python handles those normally once
        # the parent package is found)
        if "." in remainder:
            return None

        module_name = remainder

        # Check if Python already found it (avoid double-loading)
        if fullname in sys.modules:
            return None

        # Look up in the Lotus module map
        module_map = _get_module_map()
        resolved_path = module_map.get(module_name)

        if resolved_path is None:
            return None

        # Check: is this a package (directory with __init__.py) or a module (.py file)?
        if resolved_path.name == "__init__.py":
            # Package
            return importlib.machinery.ModuleSpec(
                fullname,
                _LotusLoader(fullname, resolved_path),
                origin=str(resolved_path),
                is_package=True,
            )
        else:
            # Module
            return importlib.machinery.ModuleSpec(
                fullname,
                _LotusLoader(fullname, resolved_path),
                origin=str(resolved_path),
            )


# Singleton finder instance
_finder: Optional[LotusFinder] = None


def install() -> None:
    """
    Install the LotusFinder into sys.meta_path.

    MUST be called before any substrate imports.
    Idempotent — safe to call multiple times.

    After installation, Python's import system goes through the Lotus
    for any substrate module it can't find at the expected path.
    """
    global _finder
    if _finder is not None:
        return  # Already installed

    _finder = LotusFinder()
    # Append (not prepend) — Python's normal finder gets first shot.
    # LotusFinder only activates on MISS.
    sys.meta_path.append(_finder)
    logger.debug("[LOTUS.FINDER] Installed into sys.meta_path")


def uninstall() -> None:
    """Remove the LotusFinder from sys.meta_path."""
    global _finder
    if _finder is not None and _finder in sys.meta_path:
        sys.meta_path.remove(_finder)
    _finder = None


def is_installed() -> bool:
    """Check if the LotusFinder is active."""
    return _finder is not None and _finder in sys.meta_path
