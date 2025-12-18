"""
Sense Loader - Auto-discovery for MANAS Cortex Senses.

OPUS-099: VEDA-4 Pattern for Cortex Auto-Discovery

The 5 Jnanendriyas (Perception Organs) in Samkhya:
- TVAK (Touch)       → PrakritiSense  (System state)
- CHAKSHU (Sight)    → SutraSense     (Doc/Code gaps)
- RASANA (Taste)     → DharmaSense    (Ethical alignment)
- (Future: SHROTRA, GHRANA when converted to BaseSense)

STRICT MODE ENABLED:
    - Any load failure CRASHES with full traceback
    - No silent skipping of broken senses
    - If MANAS loses a sense, it KNOWS immediately

WHY THIS EXISTS:
    Same reason as AnalyzerLoader. Manual import lists are spaghetti.
    They break constantly - someone adds a sense, forgets to import it.
    This loader follows the VEDA-4 fractal pattern: auto-discover, no manual lists.

PATTERN:
    Same as AnalyzerLoader but for senses (cortex perception modules).
    Scans: vibe_core/plugins/opus_assistant/manas/cortex/*_sense.py
    Discovers: Classes inheriting from BaseSense
"""

import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.loaders.base_loader import LoaderRegistry

logger = logging.getLogger("SENSE.LOADER")


# Type aliases
SenseRegistry = Dict[str, Any]  # sense_name -> instance
SenseMetadata = Dict[str, Dict[str, Any]]  # sense_name -> metadata


class SenseLoadError(Exception):
    """Raised when sense loading fails in STRICT MODE."""

    pass


class SenseLoader:
    """
    Auto-discovery loader for MANAS Cortex Senses (Jnanendriyas).

    STRICT MODE: Crashes on any error. No silent failures.

    Unlike PluginLoader, senses are CODE-ONLY (no manifest.json).
    Discovery is by scanning *_sense.py files for BaseSense subclasses.

    Usage:
        # Discover and instantiate all senses
        senses, meta = SenseLoader.discover_and_load(workspace=Path.cwd())

        # In CognitiveKernel - just use the dict directly
        self._senses = senses
        prakriti = senses.get("prakriti_sense")
    """

    # === LOADER CONFIG ===
    item_type = "sense"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*_sense.py"  # Only scan files ending in _sense.py
    base_class_name = "BaseSense"  # String match for loose coupling

    # === STRICT MODE ===
    strict_mode = True  # CRASH on errors, no silent skip

    # === CLASS-LEVEL CACHE ===
    _sense_cache: Optional[SenseRegistry] = None
    _metadata_cache: Optional[SenseMetadata] = None

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
        strict: Optional[bool] = None,
    ) -> Tuple[SenseRegistry, SenseMetadata]:
        """
        Discover and load all senses. CACHED after first call.

        STRICT MODE: Any failure raises SenseLoadError.

        Args:
            scan_paths: Override default paths
            workspace: Workspace to pass to sense constructors
            force_refresh: If True, bypass cache
            strict: Override class-level strict_mode

        Returns:
            Tuple of (sense_instances, metadata)

        Raises:
            SenseLoadError: If any sense fails to load (in strict mode)
        """
        # Return cached if available
        if not force_refresh and cls._sense_cache is not None:
            return cls._sense_cache, cls._metadata_cache or {}

        paths = scan_paths or cls.scan_paths
        workspace = workspace or Path.cwd()
        is_strict = strict if strict is not None else cls.strict_mode

        senses: SenseRegistry = {}
        metadata: SenseMetadata = {}
        errors: List[str] = []

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"[sense] Scan path does not exist: {base_path}")
                continue

            logger.info(f"[sense] Scanning {base_path}...")

            # Scan *_sense.py files
            for py_file in sorted(base_path.glob(cls.file_pattern)):
                # Skip test files
                if py_file.name.startswith("test_"):
                    continue

                try:
                    sense_classes = cls._load_sense_classes(py_file)

                    for sense_class in sense_classes:
                        try:
                            # Instantiate with workspace
                            instance = sense_class(workspace=workspace)
                            name = instance.name

                            senses[name] = instance
                            metadata[name] = {
                                "class": sense_class.__name__,
                                "file": str(py_file),
                                "enabled": instance.is_enabled,
                            }
                            logger.info(f"  ✅ Loaded: {name} ({sense_class.__name__})")

                        except Exception as e:
                            error_msg = f"Failed to instantiate {sense_class.__name__} from {py_file.name}: {e}"
                            logger.error(f"  ❌ {error_msg}")
                            errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Failed to load sense module {py_file.name}: {e}"
                    logger.error(f"  ❌ {error_msg}")
                    errors.append(error_msg)

        # STRICT MODE: Crash on ANY error
        if is_strict and errors:
            error_summary = "\n".join(f"  - {e}" for e in errors)
            raise SenseLoadError(
                f"STRICT MODE: {len(errors)} sense(s) failed to load:\n{error_summary}\n\n"
                f"Fix these errors before continuing. MANAS cannot be blind."
            )

        # Cache results
        cls._sense_cache = senses
        cls._metadata_cache = metadata

        logger.info(f"[sense] Loaded {len(senses)} senses (cached)")
        return senses, metadata

    @classmethod
    def _load_sense_classes(cls, py_file: Path) -> List[Type]:
        """
        Load sense classes from a Python file.

        Finds all classes that inherit from BaseSense.
        Uses proper module import to preserve package context for relative imports.
        """
        import importlib

        # Convert file path to module path
        # e.g., vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
        #    -> vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense
        try:
            parts = py_file.parts
            vibe_idx = None
            for i, part in enumerate(parts):
                if part == "vibe_core":
                    vibe_idx = i
                    break

            if vibe_idx is None:
                raise ImportError(f"Cannot determine module path for {py_file}")

            module_path = ".".join(parts[vibe_idx:]).replace(".py", "")
            module = importlib.import_module(module_path)
            module_name = module.__name__

        except Exception as e:
            raise ImportError(f"Failed to import {py_file}: {e}")

        # Find BaseSense subclasses
        sense_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Must be defined in this module (not imported)
            if obj.__module__ != module_name:
                continue

            # Must inherit from BaseSense (loose check by name)
            if cls._is_sense_subclass(obj):
                sense_classes.append(obj)

        return sense_classes

    @classmethod
    def _is_sense_subclass(cls, candidate: Type) -> bool:
        """
        Check if candidate inherits from BaseSense.

        Uses LOOSE CHECK (name-based) to avoid import path identity issues.
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
        """Clear cached sense data."""
        cls._sense_cache = None
        cls._metadata_cache = None

    @classmethod
    def get_sense(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific sense by name."""
        senses, _ = cls.discover_and_load(workspace=workspace)
        return senses.get(name)

    @classmethod
    def list_senses(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered sense names."""
        senses, _ = cls.discover_and_load(workspace=workspace)
        return list(senses.keys())


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("sense", SenseLoader)
