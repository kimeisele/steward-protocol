"""
Analyzer Loader - Auto-discovery for MANAS Analyzers.

OPUS-098: VEDA-4 Pattern for Analyzer Discovery

STRICT MODE ENABLED:
    - Any load failure CRASHES with full traceback
    - No silent skipping of broken analyzers
    - If you break an analyzer, you KNOW immediately

WHY THIS EXISTS:
    Manual registration lists (_register_modular_analyzers) are SPAGHETTI.
    They break constantly - someone adds an analyzer, forgets to register it.
    This loader follows the VEDA-4 fractal pattern: auto-discover, no manual lists.

PATTERN:
    Same as PluginLoader/CircuitLoader but for pure-code analyzers (no manifest).
    Scans: vibe_core/plugins/opus_assistant/manas/analyzers/*.py
    Discovers: Classes inheriting from BaseAnalyzer
"""

import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.loaders.base_loader import LoaderRegistry

logger = logging.getLogger("ANALYZER.LOADER")


# Type aliases
AnalyzerRegistry = Dict[str, Any]  # analyzer_name -> instance
AnalyzerMetadata = Dict[str, Dict[str, Any]]  # analyzer_name -> metadata


class AnalyzerLoadError(Exception):
    """Raised when analyzer loading fails in STRICT MODE."""

    pass


class AnalyzerLoader:
    """
    Auto-discovery loader for MANAS Analyzers.

    STRICT MODE: Crashes on any error. No silent failures.

    Unlike PluginLoader, analyzers are CODE-ONLY (no manifest.json).
    Discovery is by scanning Python files for BaseAnalyzer subclasses.

    Usage:
        # Discover and instantiate all analyzers
        analyzers, meta = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # In IntentGenerator - just use the list directly
        self._modular_analyzers = list(analyzers.values())
    """

    # === LOADER CONFIG ===
    item_type = "analyzer"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/analyzers")]
    base_class_name = "BaseAnalyzer"  # String match for loose coupling

    # === STRICT MODE ===
    strict_mode = True  # CRASH on errors, no silent skip

    # === CLASS-LEVEL CACHE ===
    _analyzer_cache: Optional[AnalyzerRegistry] = None
    _metadata_cache: Optional[AnalyzerMetadata] = None

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
        strict: Optional[bool] = None,
    ) -> Tuple[AnalyzerRegistry, AnalyzerMetadata]:
        """
        Discover and load all analyzers. CACHED after first call.

        STRICT MODE: Any failure raises AnalyzerLoadError.

        Args:
            scan_paths: Override default paths
            workspace: Workspace to pass to analyzer constructors
            force_refresh: If True, bypass cache
            strict: Override class-level strict_mode

        Returns:
            Tuple of (analyzer_instances, metadata)

        Raises:
            AnalyzerLoadError: If any analyzer fails to load (in strict mode)
        """
        # Return cached if available
        if not force_refresh and cls._analyzer_cache is not None:
            return cls._analyzer_cache, cls._metadata_cache or {}

        paths = scan_paths or cls.scan_paths
        workspace = workspace or Path.cwd()
        is_strict = strict if strict is not None else cls.strict_mode

        analyzers: AnalyzerRegistry = {}
        metadata: AnalyzerMetadata = {}
        errors: List[str] = []

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"[analyzer] Scan path does not exist: {base_path}")
                continue

            logger.info(f"[analyzer] Scanning {base_path}...")

            # Scan Python files
            for py_file in sorted(base_path.glob("*.py")):
                # Skip __init__, base, tests
                if py_file.name.startswith(("_", "test_")) or py_file.name == "base.py":
                    continue

                try:
                    analyzer_classes = cls._load_analyzer_classes(py_file)

                    for analyzer_class in analyzer_classes:
                        try:
                            # Instantiate with workspace
                            instance = analyzer_class(workspace=workspace)
                            name = instance.name

                            analyzers[name] = instance
                            metadata[name] = {
                                "class": analyzer_class.__name__,
                                "file": str(py_file),
                                "enabled": instance.is_enabled,
                            }
                            logger.info(f"  ✅ Loaded: {name} ({analyzer_class.__name__})")

                        except Exception as e:
                            error_msg = f"Failed to instantiate {analyzer_class.__name__} from {py_file.name}: {e}"
                            logger.error(f"  ❌ {error_msg}")
                            errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Failed to load analyzer module {py_file.name}: {e}"
                    logger.error(f"  ❌ {error_msg}")
                    errors.append(error_msg)

        # STRICT MODE: Crash on ANY error
        if is_strict and errors:
            error_summary = "\n".join(f"  - {e}" for e in errors)
            raise AnalyzerLoadError(
                f"STRICT MODE: {len(errors)} analyzer(s) failed to load:\n{error_summary}\n\n"
                f"Fix these errors before continuing. No silent failures allowed."
            )

        # Cache results
        cls._analyzer_cache = analyzers
        cls._metadata_cache = metadata

        logger.info(f"[analyzer] Loaded {len(analyzers)} analyzers (cached)")
        return analyzers, metadata

    @classmethod
    def _load_analyzer_classes(cls, py_file: Path) -> List[Type]:
        """
        Load analyzer classes from a Python file.

        Finds all classes that inherit from BaseAnalyzer.
        Uses proper module import to preserve package context for relative imports.
        """
        # Convert file path to module path
        # e.g., vibe_core/plugins/opus_assistant/manas/analyzers/contract_analyzer.py
        #    -> vibe_core.plugins.opus_assistant.manas.analyzers.contract_analyzer
        try:
            # Find the module path relative to the project root
            parts = py_file.parts
            # Find where vibe_core starts
            vibe_idx = None
            for i, part in enumerate(parts):
                if part == "vibe_core":
                    vibe_idx = i
                    break

            if vibe_idx is None:
                raise ImportError(f"Cannot determine module path for {py_file}")

            module_path = ".".join(parts[vibe_idx:]).replace(".py", "")

            # Import using standard import mechanism (preserves package context)
            import importlib

            module = importlib.import_module(module_path)
            module_name = module.__name__

        except Exception as e:
            raise ImportError(f"Failed to import {py_file}: {e}")

        # Find BaseAnalyzer subclasses
        analyzer_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Must be defined in this module (not imported)
            if obj.__module__ != module_name:
                continue

            # Must inherit from BaseAnalyzer (loose check by name)
            if cls._is_analyzer_subclass(obj):
                analyzer_classes.append(obj)

        return analyzer_classes

    @classmethod
    def _is_analyzer_subclass(cls, candidate: Type) -> bool:
        """
        Check if candidate inherits from BaseAnalyzer.

        Uses LOOSE CHECK (name-based) to avoid import path identity issues.
        Same pattern as PanelLoader's fractal identity crisis solution.
        """
        # Skip abstract base
        if candidate.__name__ == cls.base_class_name:
            return False

        # Check inheritance chain by name
        for base in inspect.getmro(candidate):
            if base.__name__ == cls.base_class_name:
                return True

        return False

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached analyzer data."""
        cls._analyzer_cache = None
        cls._metadata_cache = None

    @classmethod
    def get_analyzer(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific analyzer by name."""
        analyzers, _ = cls.discover_and_load(workspace=workspace)
        return analyzers.get(name)

    @classmethod
    def list_analyzers(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered analyzer names."""
        analyzers, _ = cls.discover_and_load(workspace=workspace)
        return list(analyzers.keys())


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("analyzer", AnalyzerLoader)
