"""
Code Module Loader - Base class for CODE-ONLY loaders (no manifest).

VEDA-4 PATTERN (Code-Based):
    SHABDA   (शब्द)    → Scan Directories   → scan file patterns
    ARTHA    (अर्थ)    → Validate Class     → check inheritance
    PRATYAYA (प्रत्यय) → Check Enabled      → verify not disabled
    KARMA    (कर्म)    → Instantiate        → create instance

This is the SIBLING of UnifiedLoader:
- UnifiedLoader: manifest.json → config → entry point
- CodeModuleLoader: file pattern → class scan → instantiate

FRAKTAL PRINCIPLE:
    Both loaders register with LoaderRegistry.
    Both return (registry, metadata) tuples.
    Both are composable into scoped instances.

STRICT MODE:
    - Any load failure CRASHES with full traceback
    - No silent skipping of broken modules
    - If you break something, you KNOW immediately

Usage:
    class ActionLoader(CodeModuleLoader):
        item_type = "action"
        scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
        file_pattern = "*_action.py"
        base_class_name = "BaseAction"
"""

import importlib
import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from vibe_core.loaders.base_loader import LoaderRegistry

logger = logging.getLogger("CODE.MODULE.LOADER")


T = TypeVar("T")


@dataclass
class CodeModuleMeta:
    """
    Metadata about a discovered code module.

    Generic for all code-only item types (actions, senses, analyzers).
    """

    item_id: str
    item_type: str
    class_name: str
    file_path: Path
    enabled: bool = True
    loaded_successfully: bool = True
    error: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        status = "OK" if self.loaded_successfully else f"FAILED: {self.error}"
        return f"<{self.item_type}:{self.item_id} class={self.class_name} status={status}>"


# Type aliases
CodeRegistry = Dict[str, Any]  # item_id -> instance
CodeMetadata = Dict[str, Dict[str, Any]]  # item_id -> metadata dict (backward compat)


class CodeModuleLoadError(Exception):
    """Raised when code module loading fails in STRICT MODE."""

    pass


class CodeModuleLoader(ABC):
    """
    Abstract base class for CODE-ONLY loaders.

    VEDA-4 PATTERN (Code-Based):
        1. SHABDA   → Scan directories for matching files
        2. ARTHA    → Find classes inheriting from base_class
        3. PRATYAYA → Check enabled status
        4. KARMA    → Instantiate with workspace

    Subclasses MUST define:
        - item_type: str (e.g., "action", "sense", "analyzer")
        - scan_paths: List[Path] (where to look)
        - file_pattern: str (e.g., "*_action.py")
        - base_class_name: str (e.g., "BaseAction")

    Subclasses MAY override:
        - _create_instance(): Custom instantiation logic
        - _post_process_instance(): Add extra metadata
    """

    # === MUST BE DEFINED BY SUBCLASS ===
    item_type: str = ""
    scan_paths: List[Path] = []
    file_pattern: str = "*.py"
    base_class_name: str = ""

    # === STRICT MODE (default ON) ===
    strict_mode: bool = True

    # === CLASS-LEVEL CACHE ===
    _instance_cache: Optional[CodeRegistry] = None
    _metadata_cache: Optional[CodeMetadata] = None

    # === SCOPE SUPPORT (FRAKTAL) ===
    _scope: str = "global"
    _custom_scan_paths: Optional[List[Path]] = None

    @property
    def scope(self) -> str:
        """Get the scope of this loader instance."""
        return self._scope

    # =========================================================================
    # CONSTRUCTOR (for scoped instances)
    # =========================================================================

    def __init__(
        self,
        scope: str = "global",
        scan_paths: Optional[List[Path]] = None,
    ):
        """
        Create a scoped loader instance.

        FRAKTAL PRINCIPLE:
            - scope="global" → Uses class-level scan_paths
            - scope="opus_private" → Uses custom paths, private registry

        Args:
            scope: Loader scope identifier
            scan_paths: Override scan paths for this instance
        """
        self._scope = scope
        self._custom_scan_paths = scan_paths
        # Instance-level cache (not shared with class)
        self._inst_cache: Optional[CodeRegistry] = None
        self._inst_meta: Optional[CodeMetadata] = None

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
        strict: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[CodeRegistry, CodeMetadata]:
        """
        Discover and load all code modules. CACHED after first call.

        STRICT MODE: Any failure raises CodeModuleLoadError.

        Args:
            scan_paths: Override default paths
            workspace: Workspace to pass to constructors
            force_refresh: If True, bypass cache
            strict: Override class-level strict_mode
            config: Optional config dict (for API compatibility)

        Returns:
            Tuple of (instances, metadata)

        Raises:
            CodeModuleLoadError: If any module fails to load (in strict mode)
        """
        # Return cached if available
        if not force_refresh and cls._instance_cache is not None:
            return cls._instance_cache, cls._metadata_cache or {}

        paths = scan_paths or cls.scan_paths
        workspace = workspace or Path.cwd()
        is_strict = strict if strict is not None else cls.strict_mode

        instances: CodeRegistry = {}
        metadata: CodeMetadata = {}
        errors: List[str] = []

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"[{cls.item_type}] Scan path does not exist: {base_path}")
                continue

            logger.info(f"[{cls.item_type}] Scanning {base_path}...")

            # SHABDA: Scan matching files
            for py_file in sorted(base_path.glob(cls.file_pattern)):
                # Skip test files and internal files
                if cls._should_skip_file(py_file):
                    continue

                try:
                    # ARTHA: Find valid classes
                    item_classes = cls._load_classes(py_file)

                    for item_class in item_classes:
                        try:
                            # PRATYAYA + KARMA: Instantiate
                            instance, meta = cls._create_and_register(item_class, py_file, workspace)

                            if instance is not None:
                                instances[meta.item_id] = instance
                                # Convert to dict for backward compat
                                metadata[meta.item_id] = cls._meta_to_dict(meta)
                                logger.info(f"  ✅ Loaded: {meta.item_id} ({item_class.__name__})")

                        except Exception as e:
                            error_msg = f"Failed to instantiate {item_class.__name__} from {py_file.name}: {e}"
                            logger.error(f"  ❌ {error_msg}")
                            errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Failed to load module {py_file.name}: {e}"
                    logger.error(f"  ❌ {error_msg}")
                    errors.append(error_msg)

        # STRICT MODE: Crash on ANY error
        if is_strict and errors:
            error_summary = "\n".join(f"  - {e}" for e in errors)
            raise CodeModuleLoadError(
                f"STRICT MODE: {len(errors)} {cls.item_type}(s) failed to load:\n{error_summary}\n\n"
                f"Fix these errors before continuing. No silent failures allowed."
            )

        # Cache results
        cls._instance_cache = instances
        cls._metadata_cache = metadata

        logger.info(f"[{cls.item_type}] Loaded {len(instances)} items (cached)")
        return instances, metadata

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached data."""
        cls._instance_cache = None
        cls._metadata_cache = None

    @classmethod
    def get_item(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific item by name."""
        instances, _ = cls.discover_and_load(workspace=workspace)
        return instances.get(name)

    @classmethod
    def list_items(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered item names."""
        instances, _ = cls.discover_and_load(workspace=workspace)
        return list(instances.keys())

    # =========================================================================
    # INSTANCE METHODS (for scoped usage)
    # =========================================================================

    def load(
        self,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
    ) -> Tuple[CodeRegistry, CodeMetadata]:
        """
        Instance method for scoped loading.

        Uses instance's custom scan_paths if set.
        """
        if not force_refresh and self._inst_cache is not None:
            return self._inst_cache, self._inst_meta or {}

        paths = self._custom_scan_paths or self.scan_paths
        instances, metadata = self.__class__.discover_and_load(
            scan_paths=paths,
            workspace=workspace,
            force_refresh=True,  # Don't use class cache
        )

        self._inst_cache = instances
        self._inst_meta = metadata
        return instances, metadata

    def get(self, name: str) -> Optional[Any]:
        """Get a specific item by name (instance method)."""
        items, _ = self.load()
        return items.get(name)

    def list(self) -> List[str]:
        """List all discovered item names (instance method)."""
        items, _ = self.load()
        return list(items.keys())

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    @classmethod
    def _should_skip_file(cls, py_file: Path) -> bool:
        """Check if file should be skipped."""
        name = py_file.name
        # Skip __init__, base classes, test files
        if name.startswith("_"):
            return True
        if name.startswith("test_") and name != f"test_{cls.item_type}.py":
            return True
        if name == "base.py":
            return True
        return False

    @classmethod
    def _load_classes(cls, py_file: Path) -> List[Type]:
        """
        Load classes from a Python file.

        Finds all classes that inherit from base_class.
        Uses proper module import to preserve package context.
        """
        # Convert file path to module path
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
            raise ImportError(f"Failed to import {py_file}: {e}") from e

        # Find matching subclasses
        item_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Must be defined in this module (not imported)
            if obj.__module__ != module_name:
                continue

            # Must inherit from base class (loose check by name)
            if cls._is_valid_subclass(obj):
                item_classes.append(obj)

        return item_classes

    @classmethod
    def _is_valid_subclass(cls, candidate: Type) -> bool:
        """
        Check if candidate inherits from base class.

        Uses LOOSE CHECK (name-based) to avoid import path identity issues.
        """
        # Skip abstract base itself
        if candidate.__name__ == cls.base_class_name:
            return False

        # Check inheritance chain by name
        for base in inspect.getmro(candidate):
            if base.__name__ == cls.base_class_name:
                return True

        return False

    @classmethod
    def _create_and_register(
        cls,
        item_class: Type,
        py_file: Path,
        workspace: Path,
    ) -> Tuple[Optional[Any], CodeModuleMeta]:
        """
        Create instance and build metadata.

        Override in subclass for custom instantiation.
        """
        # Try instantiation with workspace
        try:
            instance = item_class(workspace=workspace)
        except TypeError:
            # Fallback: no workspace
            instance = item_class()

        # Get name from instance
        name = getattr(instance, "name", item_class.__name__)
        enabled = getattr(instance, "is_enabled", True)

        meta = CodeModuleMeta(
            item_id=name,
            item_type=cls.item_type,
            class_name=item_class.__name__,
            file_path=py_file,
            enabled=enabled,
            loaded_successfully=True,
        )

        # Allow subclass to add extra metadata
        cls._post_process_instance(instance, meta)

        return instance, meta

    @classmethod
    def _post_process_instance(cls, instance: Any, meta: CodeModuleMeta) -> None:
        """
        Hook for subclasses to add extra metadata.

        Override to add item-type-specific fields to meta.extra.
        """
        pass

    @classmethod
    def _meta_to_dict(cls, meta: CodeModuleMeta) -> Dict[str, Any]:
        """
        Convert CodeModuleMeta to dict for backward compatibility.

        Existing code expects metadata[name] to be a dict with keys like
        'class', 'file', 'enabled', etc.
        """
        result = {
            "class": meta.class_name,
            "file": str(meta.file_path),
            "enabled": meta.enabled,
        }
        # Merge extra fields (subclass-specific)
        result.update(meta.extra)
        return result
