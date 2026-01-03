"""
RemedyLoader - Dynamic Discovery for Shuddhi Remedies.

OPUS-307: No more hardcoded imports!

This loader follows the VEDA-4 pattern:
    SHABDA   → Scan remedies/ directory
    ARTHA    → Validate CSTRemedy inheritance
    PRATYAYA → Check rule_id property
    KARMA    → Register remedy class

The system can now:
1. Auto-discover all remedies from vibe_core/shuddhi/remedies/
2. Scale to hundreds of remedies without code changes
3. Allow runtime addition of new remedies
4. Let the system write its own remedies (GAD-000)
"""

import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type

from vibe_core.shuddhi.remedies.base import CSTRemedy

logger = logging.getLogger("SHUDDHI.LOADER")


class RemedyLoader:
    """
    VEDA-4 compliant loader for Shuddhi remedies.

    Discovers CSTRemedy subclasses from the remedies directory
    and registers them by rule_id.

    Usage:
        loader = RemedyLoader()
        remedies = loader.discover_and_load()
        # remedies = {"subprocess_timeout": SubprocessTimeoutRemedy, ...}
    """

    # Default scan path (relative to vibe_core)
    DEFAULT_REMEDIES_PATH = Path(__file__).parent / "remedies"

    # Files to skip during scanning
    SKIP_FILES = {"__init__.py", "base.py"}

    def __init__(
        self,
        scan_paths: Optional[List[Path]] = None,
    ):
        """
        Initialize the remedy loader.

        Args:
            scan_paths: Override default scan paths (for extensibility)
        """
        self._scan_paths = scan_paths or [self.DEFAULT_REMEDIES_PATH]
        self._cache: Optional[Dict[str, Type[CSTRemedy]]] = None

    def discover_and_load(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, Type[CSTRemedy]]:
        """
        Discover and load all remedy classes.

        Returns:
            Dict mapping rule_id -> CSTRemedy class
        """
        if not force_refresh and self._cache is not None:
            return self._cache

        remedies: Dict[str, Type[CSTRemedy]] = {}

        for scan_path in self._scan_paths:
            if not scan_path.exists():
                logger.debug(f"[REMEDY] Scan path does not exist: {scan_path}")
                continue

            logger.debug(f"[REMEDY] Scanning {scan_path}...")

            for py_file in scan_path.glob("*.py"):
                # Skip excluded files
                if py_file.name in self.SKIP_FILES:
                    continue

                # SHABDA: Load the module
                module = self._load_module(py_file)
                if module is None:
                    continue

                # ARTHA + PRATYAYA: Find CSTRemedy subclasses
                for remedy_class in self._find_remedy_classes(module):
                    # KARMA: Register by rule_id
                    try:
                        # Instantiate to get rule_id (it's a property)
                        instance = remedy_class()
                        rule_id = instance.rule_id

                        if rule_id in remedies:
                            logger.warning(
                                f"[REMEDY] Duplicate rule_id '{rule_id}' - "
                                f"keeping {remedies[rule_id].__name__}, "
                                f"ignoring {remedy_class.__name__}"
                            )
                            continue

                        remedies[rule_id] = remedy_class
                        logger.debug(f"[REMEDY] Registered: {rule_id} -> {remedy_class.__name__}")

                    except Exception as e:
                        logger.warning(f"[REMEDY] Failed to register {remedy_class.__name__}: {e}")

        logger.info(f"[REMEDY] Loaded {len(remedies)} remedies")
        self._cache = remedies
        return remedies

    def _load_module(self, py_file: Path):
        """
        Dynamically load a Python module from file.

        SHABDA: Capture the intent (code).
        """
        module_name = f"shuddhi_remedy_{py_file.stem}"

        # Check if already loaded
        if module_name in sys.modules:
            return sys.modules[module_name]

        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                logger.debug(f"[REMEDY] Cannot create spec for {py_file}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module

        except Exception as e:
            logger.warning(f"[REMEDY] Failed to load {py_file}: {e}")
            return None

    def _find_remedy_classes(self, module) -> List[Type[CSTRemedy]]:
        """
        Find all CSTRemedy subclasses in a module.

        ARTHA: Validate the meaning (proper inheritance).
        """
        remedy_classes = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Must be defined in this module (not imported)
            if obj.__module__ != module.__name__:
                continue

            # Must be a CSTRemedy subclass
            if not issubclass(obj, CSTRemedy):
                continue

            # Must not be the base class itself
            if obj is CSTRemedy:
                continue

            remedy_classes.append(obj)

        return remedy_classes

    def list_rule_ids(self) -> List[str]:
        """List all discovered rule IDs."""
        remedies = self.discover_and_load()
        return list(remedies.keys())

    def get_remedy(self, rule_id: str) -> Optional[Type[CSTRemedy]]:
        """Get a specific remedy class by rule_id."""
        remedies = self.discover_and_load()
        return remedies.get(rule_id)

    def clear_cache(self) -> None:
        """Clear the cache (for hot-reloading)."""
        self._cache = None

    def add_scan_path(self, path: Path) -> None:
        """
        Add a custom scan path for extensibility.

        Use Case: Agent-written remedies in a separate directory.
        """
        if path not in self._scan_paths:
            self._scan_paths.append(path)
            self._cache = None  # Invalidate cache


# Module-level singleton for convenience
_default_loader: Optional[RemedyLoader] = None


def get_remedy_loader() -> RemedyLoader:
    """Get the default remedy loader singleton."""
    global _default_loader
    if _default_loader is None:
        _default_loader = RemedyLoader()
    return _default_loader


def discover_remedies() -> Dict[str, Type[CSTRemedy]]:
    """Convenience function to discover all remedies."""
    return get_remedy_loader().discover_and_load()
