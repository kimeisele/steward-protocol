"""
Unified Loader - Base class for ALL item loaders.

VEDA-4 PATTERN:
    SHABDA   (शब्द)    → Capture Intent     → scan + load_manifest
    ARTHA    (अर्थ)    → Validate Meaning   → validate_manifest
    PRATYAYA (प्रत्यय) → Verify Conditions  → load_config + check_enabled
    KARMA    (कर्म)    → Execute Action     → instantiate

All loaders (Plugin, Agent, Section, Workflow) MUST inherit from this.
"""

import importlib.util
import inspect
import json
import logging
import sys
import zipfile
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from vibe_core.loaders.container_loader import ContainerMounter

logger = logging.getLogger("UNIFIED.LOADER")


# Type variable for item instances
T = TypeVar("T")


@dataclass
class ItemMeta:
    """
    Metadata about a discovered item.

    Universal for ALL item types (plugins, agents, sections, etc.)
    """

    item_id: str
    item_type: str  # "plugin", "agent", "section", "workflow"
    manifest: Dict[str, Any]
    manifest_path: Path
    entry_path: Optional[Path]
    entry_class: Optional[Type]
    config: Dict[str, Any] = field(default_factory=dict)
    loaded_successfully: bool = True
    error: Optional[str] = None
    # OPUS-015/020: Execution mode for process isolation
    execution_mode: str = "thread"  # "thread" | "process"

    def __repr__(self) -> str:
        status = "OK" if self.loaded_successfully else f"FAILED: {self.error}"
        return f"<{self.item_type}:{self.item_id} status={status}>"


# Type aliases
ItemRegistry = Dict[str, Any]  # item_id -> instance
ItemMetadata = Dict[str, ItemMeta]  # item_id -> metadata


class LoaderRegistry:
    """
    Registry of all loader types.

    Each item type registers its loader here for unified discovery.
    """

    _loaders: Dict[str, Type["UnifiedLoader"]] = {}

    @classmethod
    def register(cls, item_type: str, loader_class: Type["UnifiedLoader"]) -> None:
        """Register a loader for an item type."""
        cls._loaders[item_type] = loader_class
        logger.debug(f"Registered loader for '{item_type}': {loader_class.__name__}")

    @classmethod
    def get(cls, item_type: str) -> Optional[Type["UnifiedLoader"]]:
        """Get loader for an item type."""
        return cls._loaders.get(item_type)

    @classmethod
    def all_types(cls) -> List[str]:
        """Get all registered item types."""
        return list(cls._loaders.keys())

    @classmethod
    def discover_all(cls, config: Optional[Dict[str, Any]] = None) -> Dict[str, Tuple[ItemRegistry, ItemMetadata]]:
        """
        Discover ALL items of ALL types.

        Returns:
            Dict mapping item_type -> (instances, metadata)
        """
        results = {}
        for item_type, loader_class in cls._loaders.items():
            instances, metadata = loader_class.discover_and_load(config=config)
            results[item_type] = (instances, metadata)
        return results


class UnifiedLoader(ABC):
    """
    Abstract base class for ALL item loaders.

    VEDA-4 PATTERN - Same structure for everything:
        1. SHABDA   → scan + read manifest
        2. ARTHA    → validate manifest
        3. PRATYAYA → load config + check enabled
        4. KARMA    → instantiate

    Subclasses MUST define:
        - item_type: str (e.g., "plugin", "agent")
        - scan_paths: List[Path] (where to look)
        - entry_suffix: str (e.g., "_main.py")
        - base_class: Type (e.g., KernelPlugin)

    Subclasses MAY override:
        - manifest_filenames: List[str] (default: ["manifest.json"])
        - validate_manifest(): Custom validation
        - instantiate(): Custom instantiation logic
    """

    # === MUST BE OVERRIDDEN ===
    item_type: str = ""  # "plugin", "agent", "section"
    scan_paths: List[Path] = []  # Where to look
    entry_suffix: str = "_main.py"  # Entry point file suffix
    base_class: Optional[Type] = None  # Required base class for items

    # === MAY BE OVERRIDDEN ===
    manifest_filenames: List[str] = ["manifest.json"]  # Supported manifest names
    config_filename: str = "config.yaml"  # Local config file name

    # === CLASS STATE ===
    _cache: Optional[ItemMetadata] = None

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ItemRegistry, ItemMetadata]:
        """
        Discover AND load all items.

        This is the MAIN entry point for loading items.

        Args:
            scan_paths: Override default scan paths
            config: Global config (e.g., from Phoenix)

        Returns:
            Tuple of (instances, metadata)
        """
        paths = scan_paths or cls.scan_paths
        instances: ItemRegistry = {}
        metadata: ItemMetadata = {}

        for base_path in paths:
            if not base_path.exists():
                logger.debug(f"[{cls.item_type}] Scan path does not exist: {base_path}")
                continue

            logger.debug(f"[{cls.item_type}] Scanning {base_path}...")

            for item in base_path.iterdir():
                # 1. Existing: Directory support
                if item.is_dir():
                    # Skip hidden and __pycache__
                    if item.name.startswith((".", "_")):
                        continue

                    # VEDA-4 LOOP
                    meta = cls._process_item_directory(item, config)

                # 2. NEW: Container support (.vibe files)
                elif item.suffix == ".vibe" and zipfile.is_zipfile(item):
                    meta = cls._process_container(item, config)

                else:
                    continue

                if meta is None:
                    continue

                metadata[meta.item_id] = meta

                # Only add to instances if loaded successfully
                if meta.loaded_successfully and meta.entry_class:
                    instance = cls._create_instance(meta, config)
                    if instance:
                        instances[meta.item_id] = instance
                        logger.info(f"  ✅ Loaded: {meta.item_id}")
                    else:
                        meta.loaded_successfully = False
                        meta.error = "Instance creation failed"

        logger.info(f"[{cls.item_type}] Loaded {len(instances)} items")
        return instances, metadata

    @classmethod
    def discover_manifests(
        cls,
        scan_paths: Optional[List[Path]] = None,
    ) -> Tuple[Dict[str, Dict[str, Any]], ItemMetadata]:
        """
        Discover manifests only (no loading).

        Useful for validation and introspection.
        """
        paths = scan_paths or cls.scan_paths
        manifests: Dict[str, Dict[str, Any]] = {}
        metadata: ItemMetadata = {}

        for base_path in paths:
            if not base_path.exists():
                continue

            for item_dir in base_path.iterdir():
                if not item_dir.is_dir():
                    continue
                if item_dir.name.startswith((".", "_")):
                    continue

                # SHABDA - Load manifest only
                manifest_path = cls._find_manifest(item_dir)
                if not manifest_path:
                    continue

                try:
                    manifest = cls._load_manifest(manifest_path)
                    item_id = manifest.get("id", item_dir.name)
                    manifests[item_id] = manifest

                    metadata[item_id] = ItemMeta(
                        item_id=item_id,
                        item_type=cls.item_type,
                        manifest=manifest,
                        manifest_path=manifest_path,
                        entry_path=None,
                        entry_class=None,
                        loaded_successfully=True,
                    )
                except Exception as e:
                    logger.warning(f"Failed to load manifest: {manifest_path}: {e}")

        return manifests, metadata

    # =========================================================================
    # VEDA-4 INTERNAL METHODS
    # =========================================================================

    @classmethod
    def _process_container(
        cls,
        container_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[ItemMeta]:
        """
        Process a .vibe container through VEDA-4 stages.
        """
        try:
            # SHABDA: Inspect without mounting
            inspection = ContainerMounter.inspect(container_path)
            manifest = inspection["manifest"]
            item_id = manifest.get("id", container_path.stem)

            # ARTHA: Validate
            errors = cls._validate_manifest(manifest)
            if errors:
                return ItemMeta(
                    item_id=item_id,
                    item_type=cls.item_type,
                    manifest=manifest,
                    manifest_path=container_path,
                    entry_path=None,
                    entry_class=None,
                    loaded_successfully=False,
                    error=f"Validation failed: {errors}",
                )

            # PRATYAYA: Mount & Load Config
            # We mount now to access internal config if needed
            mount_result = ContainerMounter.mount(container_path)
            # OPUS-015/020: MountResult provides execution_mode
            mount_point = mount_result.mount_point

            # Load config from mounted files if available
            # (Reusing _load_config logic but pointing to mount_point)
            item_config = cls._load_config(mount_point, manifest, config)

            if not item_config.get("enabled", True):
                return ItemMeta(
                    item_id=item_id,
                    item_type=cls.item_type,
                    manifest=manifest,
                    manifest_path=container_path,
                    entry_path=None,
                    entry_class=None,
                    config=item_config,
                    loaded_successfully=False,
                    error="Disabled by config",
                )

            # COGNITIVE PACK: Data-Only Logic
            # Phase 4: "Operation Cortex Injection"
            if manifest.get("type") == "cognitive_pack":
                logger.debug(f"Mounting Cognitive Pack: {item_id}")
                # Use manifest path inside mount_point so .parent gives correct directory
                # (kernel uses manifest_path.parent for genesis_path)
                return ItemMeta(
                    item_id=item_id,
                    item_type="cognitive_pack",  # Override item_type
                    manifest=manifest,
                    manifest_path=mount_point / "manifest.json",
                    entry_path=mount_point,
                    entry_class=None,  # No code execution
                    config=item_config,
                    loaded_successfully=True,  # Success by default for data packs
                )

            # KARMA: Execution Mode Logic
            mode = manifest.get("execution", {}).get("mode", "thread")

            entry_class = None
            if mode == "thread":
                # STRATEGY B: Shared Reality
                # Insert mount content to path
                content_path = mount_point / "content"
                sys.path.insert(0, str(content_path))
                try:
                    entry_path = cls._find_entry_point(content_path, manifest)
                    if entry_path:
                        entry_class = cls._load_entry_class(entry_path, item_id, manifest)
                finally:
                    sys.path.pop(0)

            elif mode == "process":
                # STRATEGY A: Isolated Reality
                # Mark for ProcessManager spawn at kernel level
                logger.info(f"🔒 Container {item_id} requests PROCESS isolation")
                return ItemMeta(
                    item_id=item_id,
                    item_type=cls.item_type,
                    manifest=manifest,
                    manifest_path=container_path,
                    entry_path=mount_point,  # ProcessManager will use this
                    entry_class=None,  # No class - spawned in subprocess
                    config=item_config,
                    loaded_successfully=True,
                    execution_mode="process",  # OPUS-015/020: Kernel reads this
                )

            return ItemMeta(
                item_id=item_id,
                item_type=cls.item_type,
                manifest=manifest,
                manifest_path=container_path,
                entry_path=mount_point,
                entry_class=entry_class,
                config=item_config,
                loaded_successfully=True if entry_class else False,
                execution_mode=mode,  # OPUS-015/020: Usually "thread"
            )

        except Exception as e:
            logger.error(f"Failed to process container {container_path}: {e}")
            return None

    @classmethod
    def _process_item_directory(
        cls,
        item_dir: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[ItemMeta]:
        """
        Process a single item directory through VEDA-4 stages.

        SHABDA   → Find and load manifest
        ARTHA    → Validate manifest
        PRATYAYA → Load config, check enabled
        KARMA    → Load entry point class
        """
        item_id = item_dir.name

        # === SHABDA: Find and load manifest ===
        manifest_path = cls._find_manifest(item_dir)
        if not manifest_path:
            logger.debug(f"  No manifest in {item_dir}")
            return None

        try:
            manifest = cls._load_manifest(manifest_path)
        except Exception as e:
            return ItemMeta(
                item_id=item_id,
                item_type=cls.item_type,
                manifest={},
                manifest_path=manifest_path,
                entry_path=None,
                entry_class=None,
                loaded_successfully=False,
                error=f"Manifest load failed: {e}",
            )

        # Use manifest id if available
        item_id = manifest.get("id", item_id)

        # === ARTHA: Validate manifest ===
        validation_errors = cls._validate_manifest(manifest)
        if validation_errors:
            return ItemMeta(
                item_id=item_id,
                item_type=cls.item_type,
                manifest=manifest,
                manifest_path=manifest_path,
                entry_path=None,
                entry_class=None,
                loaded_successfully=False,
                error=f"Validation failed: {validation_errors}",
            )

        # === ZOLLAMT: GAD-000 Compliance Gate (OPUS-161) ===
        compliance_result = cls._check_gad000_compliance(item_dir, manifest, config)
        if not compliance_result["passed"]:
            if compliance_result["mode"] == "block":
                return ItemMeta(
                    item_id=item_id,
                    item_type=cls.item_type,
                    manifest=manifest,
                    manifest_path=manifest_path,
                    entry_path=None,
                    entry_class=None,
                    loaded_successfully=False,
                    error=f"GAD-000 compliance failed: {compliance_result['reason']}",
                )
            elif compliance_result["mode"] == "warn":
                logger.warning(f"[ZOLLAMT] {item_id}: {compliance_result['reason']}")

        # === PRATYAYA: Load config, check enabled ===
        item_config = cls._load_config(item_dir, manifest, config)

        if not item_config.get("enabled", True):
            logger.debug(f"  Disabled: {item_id}")
            return ItemMeta(
                item_id=item_id,
                item_type=cls.item_type,
                manifest=manifest,
                manifest_path=manifest_path,
                entry_path=None,
                entry_class=None,
                config=item_config,
                loaded_successfully=False,
                error="Disabled by config",
            )

        # === KARMA: Load entry point ===
        entry_path = cls._find_entry_point(item_dir, manifest)
        entry_class = None

        if entry_path and entry_path.exists():
            try:
                entry_class = cls._load_entry_class(entry_path, item_id, manifest)
            except Exception as e:
                return ItemMeta(
                    item_id=item_id,
                    item_type=cls.item_type,
                    manifest=manifest,
                    manifest_path=manifest_path,
                    entry_path=entry_path,
                    entry_class=None,
                    config=item_config,
                    loaded_successfully=False,
                    error=f"Entry point load failed: {e}",
                )

        return ItemMeta(
            item_id=item_id,
            item_type=cls.item_type,
            manifest=manifest,
            manifest_path=manifest_path,
            entry_path=entry_path,
            entry_class=entry_class,
            config=item_config,
            loaded_successfully=True,
        )

    # =========================================================================
    # SHABDA: Manifest Discovery
    # =========================================================================

    @classmethod
    def _find_manifest(cls, item_dir: Path) -> Optional[Path]:
        """Find manifest file in item directory."""
        for filename in cls.manifest_filenames:
            manifest_path = item_dir / filename
            if manifest_path.exists():
                return manifest_path
        return None

    @classmethod
    def _load_manifest(cls, manifest_path: Path) -> Dict[str, Any]:
        """Load manifest from JSON file."""
        with open(manifest_path, "r") as f:
            return json.load(f)

    # =========================================================================
    # ARTHA: Manifest Validation
    # =========================================================================

    @classmethod
    def _validate_manifest(cls, manifest: Dict[str, Any]) -> List[str]:
        """
        Validate manifest against schema.

        Override for type-specific validation.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Type must match
        manifest_type = manifest.get("type")
        if manifest_type and manifest_type != cls.item_type:
            errors.append(f"Type mismatch: expected '{cls.item_type}', got '{manifest_type}'")

        # ID is required
        if not manifest.get("id") and not manifest.get("name"):
            errors.append("Manifest must have 'id' or 'name'")

        return errors

    # =========================================================================
    # ZOLLAMT: GAD-000 Compliance Gate (OPUS-161)
    # =========================================================================

    @classmethod
    def _check_gad000_compliance(
        cls,
        item_dir: Path,
        manifest: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        ZOLLAMT: GAD-000 Compliance Gate.

        Checks if a module meets minimum GAD-000 compliance requirements
        before allowing it to be loaded.

        Args:
            item_dir: Path to the module directory
            manifest: Loaded manifest data
            config: Global configuration

        Returns:
            Dict with:
                - passed: bool - Whether compliance check passed
                - mode: str - "block" | "warn" | "silent"
                - reason: str - Why it failed (if failed)
        """
        # Get compliance mode from config
        loader_config = {}
        if config:
            if hasattr(config, "model_dump"):
                loader_config = config.model_dump().get("loader", {})
            elif isinstance(config, dict):
                loader_config = config.get("loader", {})

        # Check if compliance checking is enabled
        compliance_enabled = loader_config.get("compliance_check", True)
        compliance_mode = loader_config.get("compliance_mode", "warn")

        if not compliance_enabled or compliance_mode == "silent":
            return {"passed": True, "mode": "silent", "reason": ""}

        # Try to use GenesisService for compliance check
        try:
            from vibe_core.genesis import GenesisService

            genesis = GenesisService.get_instance()
            is_compliant = genesis.quick_check(item_dir)

            if is_compliant:
                return {"passed": True, "mode": compliance_mode, "reason": ""}
            else:
                return {
                    "passed": False,
                    "mode": compliance_mode,
                    "reason": "Missing required GAD-000 infrastructure files",
                }

        except ImportError:
            # Genesis service not available - graceful degradation
            logger.debug(f"[ZOLLAMT] Genesis service unavailable, skipping compliance check for {item_dir.name}")
            return {"passed": True, "mode": "silent", "reason": ""}

    # =========================================================================
    # PRATYAYA: Config Loading
    # =========================================================================

    @classmethod
    def _load_config(
        cls,
        item_dir: Path,
        manifest: Dict[str, Any],
        global_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Load config with priority hierarchy.

        Priority (highest wins):
            1. Global config (Phoenix) for this item
            2. Local config.yaml
            3. Manifest top-level settings (enabled, priority)
            4. Manifest defaults
        """
        # Start with manifest defaults
        config: Dict[str, Any] = manifest.get("defaults", {}).copy()

        # Add manifest top-level settings (like enabled, priority)
        for key in ["enabled", "priority"]:
            if key in manifest:
                config[key] = manifest[key]

        # Merge local config.yaml
        local_config_path = item_dir / cls.config_filename
        if local_config_path.exists():
            try:
                import yaml

                with open(local_config_path, "r") as f:
                    local_config = yaml.safe_load(f) or {}
                config.update(local_config)
            except Exception as e:
                logger.warning(f"Failed to load local config: {e}")

        # Merge global config for this item
        if global_config:
            # PHOENIX V2 FIX: Handle Pydantic models (Architectural Fix)
            # If global_config is a Pydantic model (CityConfig), convert to dict
            if hasattr(global_config, "model_dump"):
                global_config_dict = global_config.model_dump()
            elif hasattr(global_config, "dict"):  # Pydantic v1 compat
                global_config_dict = global_config.dict()
            else:
                global_config_dict = global_config

            item_id = manifest.get("id", item_dir.name)
            item_global_config = global_config_dict.get(cls.item_type + "s", {}).get(item_id, {})
            config.update(item_global_config)

        return config

    # =========================================================================
    # KARMA: Entry Point Loading
    # =========================================================================

    @classmethod
    def _find_entry_point(cls, item_dir: Path, manifest: Dict[str, Any]) -> Optional[Path]:
        """Find entry point file."""
        # Check manifest for explicit entry point
        entry_point = manifest.get("entry_point")
        if entry_point:
            return item_dir / entry_point

        # Default: {type}_main.py
        default_entry = item_dir / f"{cls.item_type}{cls.entry_suffix}"
        if default_entry.exists():
            return default_entry

        # Fallback: cartridge_main.py (for backward compat with agents)
        cartridge_entry = item_dir / "cartridge_main.py"
        if cartridge_entry.exists():
            return cartridge_entry

        return None

    @classmethod
    def _load_entry_class(
        cls,
        entry_path: Path,
        item_id: str,
        manifest: Dict[str, Any],
    ) -> Optional[Type]:
        """
        Dynamically load the entry point class.

        Looks for:
            1. Class specified in manifest.entry_class
            2. Class ending with appropriate suffix (Plugin, Cartridge, Section)
            3. First class that inherits from base_class
        """
        # Import module dynamically
        module_name = f"{cls.item_type}_{item_id}"
        spec = importlib.util.spec_from_file_location(module_name, entry_path)

        if spec is None or spec.loader is None:
            logger.debug(f"Cannot create module spec for {entry_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Register in sys.modules
        sys.modules[module_name] = module

        # Determine class suffix to look for
        class_suffix = manifest.get("entry_class")
        if not class_suffix:
            # Derive from item type: plugin -> Plugin, agent -> Cartridge
            suffix_map = {
                "plugin": "Plugin",
                "agent": "Cartridge",
                "section": "Section",
                "workflow": "Workflow",
            }
            class_suffix = suffix_map.get(cls.item_type, cls.item_type.capitalize())

        # Find matching class
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module_name:
                continue

            # Check if class matches expected pattern
            if name.endswith(class_suffix):
                return obj

            # Check if inherits from base_class
            if cls.base_class and issubclass(obj, cls.base_class) and obj is not cls.base_class:
                return obj

        logger.debug(f"No matching class found in {entry_path}")
        return None

    @classmethod
    def _create_instance(
        cls,
        meta: ItemMeta,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """
        Create an instance of the loaded class.

        Override for custom instantiation logic.
        """
        if not meta.entry_class:
            return None

        try:
            # Try with config first
            try:
                return meta.entry_class(config=meta.config)
            except TypeError:
                # Fallback: no config
                return meta.entry_class()
        except Exception as e:
            logger.warning(f"Failed to instantiate {meta.item_id}: {e}")
            return None

    # =========================================================================
    # UTILITY
    # =========================================================================

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached data."""
        cls._cache = None
