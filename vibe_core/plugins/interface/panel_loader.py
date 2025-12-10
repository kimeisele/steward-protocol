"""
Panel Loader - Auto-discovery for UI Panels.

INHERITS FROM UnifiedLoader - The fractal pattern!

Specifics for Panels:
- Used by OpusRenderer to discover panels in a directory
- Uses BasePanel as base class
- Returns panels sorted by priority
"""

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.loaders import ItemMeta, LoaderRegistry, UnifiedLoader

logger = logging.getLogger("PANEL.LOADER")


# Forward reference to avoid circular import
BasePanel: Optional[Type] = None


def _get_base_panel() -> Type:
    """Lazy load BasePanel to avoid circular import."""
    global BasePanel
    if BasePanel is None:
        from vibe_core.plugins.interface.renderers.opus.panels import (
            BasePanel as BP,
        )

        BasePanel = BP
    return BasePanel


class PanelLoader(UnifiedLoader):
    """
    Auto-discovery loader for UI Panels.

    Inherits from UnifiedLoader - VEDA-4 pattern.

    Panel-specific:
    - Supports both new-style (manifest.json) and old-style (.py files)
    - base_class is BasePanel
    - Returns panels sorted by priority

    Usage:
        # Discover all panels in a directory
        panels, meta = PanelLoader.discover_and_load(
            scan_paths=[Path("vibe_core/plugins/interface/renderers/opus/panels")],
            kernel=kernel
        )
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "panel"
    scan_paths = []  # Set dynamically per renderer
    manifest_filenames = ["manifest.json"]
    entry_suffix = ".py"

    # base_class set dynamically to avoid circular import
    @classmethod
    def _get_base_class(cls) -> Type:
        return _get_base_panel()

    # Store kernel reference for panel instantiation
    _kernel: Optional[Any] = None

    # =========================================================================
    # OVERRIDE: Discover and Load
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        kernel: Optional[Any] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, ItemMeta]]:
        """
        Discover and load all panels in given paths.

        Supports BOTH:
        - NEW-style: files with manifest.json
        - OLD-style: single .py files

        Args:
            scan_paths: Paths to scan for panels
            config: Global config
            kernel: Kernel instance for panel instantiation

        Returns:
            Tuple of (panel_instances, metadata)
        """
        cls._kernel = kernel
        paths = scan_paths or cls.scan_paths

        instances: Dict[str, Any] = {}
        metadata: Dict[str, ItemMeta] = {}

        for base_path in paths:
            if not base_path.exists():
                logger.debug(f"[panel] Scan path does not exist: {base_path}")
                continue

            logger.debug(f"[panel] Scanning {base_path}...")

            for item in base_path.iterdir():
                # Skip hidden, __pycache__, __init__.py
                if item.name.startswith((".", "_")) or item.name == "__pycache__":
                    continue
                if item.name == "__init__.py":
                    continue

                meta = None

                # Single .py file
                if item.is_file() and item.suffix == ".py":
                    meta = cls._process_panel_file(item, config)

                if meta is None:
                    continue

                metadata[meta.item_id] = meta

                # Create instance if loaded successfully
                if meta.loaded_successfully and meta.entry_class:
                    instance = cls._create_instance(meta, config)
                    if instance:
                        instances[meta.item_id] = instance
                        logger.debug(f"  ✅ Loaded panel: {meta.item_id}")
                    else:
                        meta.loaded_successfully = False
                        meta.error = "Instance creation failed"
                elif not meta.loaded_successfully:
                    # ERROR BOUNDARY: Log but don't crash
                    logger.warning(f"  ⚠️ Panel {meta.item_id} failed: {meta.error}")

        # Sort by priority
        sorted_instances = dict(
            sorted(
                instances.items(),
                key=lambda x: getattr(x[1], "priority", 50),
            )
        )

        logger.info(f"[panel] Loaded {len(sorted_instances)} panels")
        return sorted_instances, metadata

    @classmethod
    def _process_panel_file(
        cls,
        file_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[ItemMeta]:
        """
        Process a single panel .py file.

        Creates synthetic manifest from panel class.
        """
        item_id = file_path.stem

        try:
            entry_class = cls._load_entry_class_from_file(file_path, item_id)
            if not entry_class:
                return None

            # Get priority from class if available
            priority = 50
            if hasattr(entry_class, "priority"):
                # It's a property, need to get default
                priority = 50

            # Create synthetic manifest
            manifest = {
                "type": "panel",
                "id": item_id,
                "name": entry_class.__name__,
                "entry_point": file_path.name,
                "entry_class": entry_class.__name__,
                "enabled": True,
                "priority": priority,
            }

            return ItemMeta(
                item_id=item_id,
                item_type="panel",
                manifest=manifest,
                manifest_path=file_path,
                entry_path=file_path,
                entry_class=entry_class,
                loaded_successfully=True,
            )

        except Exception as e:
            # ERROR BOUNDARY: Return failed metadata, don't crash
            logger.warning(f"Failed to load panel from {file_path}: {e}")
            return ItemMeta(
                item_id=item_id,
                item_type="panel",
                manifest={},
                manifest_path=file_path,
                entry_path=None,
                entry_class=None,
                loaded_successfully=False,
                error=str(e),
            )

    @classmethod
    def _load_entry_class_from_file(
        cls,
        file_path: Path,
        item_id: str,
    ) -> Optional[Type]:
        """Load panel class from a Python file."""
        try:
            # Build module path
            abs_path = file_path.resolve()
            relative = abs_path.relative_to(Path.cwd())
            module_path = str(relative.with_suffix("")).replace("/", ".")

            module = importlib.import_module(module_path)
            base_cls = cls._get_base_class()

            # Find panel class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type):
                    # LOGGING: Check candidates
                    if attr.__name__.endswith("Panel") and attr.__name__ != "BasePanel":
                        is_sub = issubclass(attr, base_cls)
                        try:
                            # LOOSE CHECK: If strict check fails, check qualified name
                            if not is_sub:
                                logger.debug(
                                    f"DEBUG: Strict check failed for {attr.__name__} (base: {base_cls.__name__})"
                                )
                                logger.debug(f"       Candidate Bases: {[b.__name__ for b in attr.__bases__]}")

                                for base in attr.__bases__:
                                    if base.__name__ == "BasePanel":
                                        logger.debug(f"DEBUG: MATCH via name for {attr.__name__}")
                                        is_sub = True
                                        break
                        except Exception as e:
                            logger.debug(f"DEBUG: Error in loose check: {e}")

                        if is_sub:
                            # MATCH FOUND - Ignore module mismatch (Fractal Loader Issue)
                            # Since we import by file path, module name is often just the filename
                            # versus the full package path. We trust the class structure check.
                            logger.debug(f"DEBUG: ACCEPTED {attr.__name__}")
                            return attr

            return None

        except Exception as e:
            logger.debug(f"Failed to import {file_path}: {e}")
            raise  # Re-raise to be caught by _process_panel_file

    # =========================================================================
    # OVERRIDES FOR PANEL-SPECIFIC BEHAVIOR
    # =========================================================================

    @classmethod
    def _validate_manifest(cls, manifest: Dict[str, Any]) -> List[str]:
        """Panel-specific manifest validation."""
        errors = []

        if not manifest.get("id") and not manifest.get("name"):
            errors.append("Manifest must have 'id' or 'name'")

        return errors

    @classmethod
    def _create_instance(
        cls,
        meta: ItemMeta,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Panel-specific instantiation - requires kernel."""
        if not meta.entry_class:
            return None

        if cls._kernel is None:
            logger.warning(f"Cannot instantiate {meta.item_id}: no kernel provided")
            return None

        try:
            # Panels require kernel in constructor
            instance = meta.entry_class(cls._kernel)

            # Validate it's a BasePanel
            base_cls = cls._get_base_class()
            if not isinstance(instance, base_cls):
                logger.warning(f"{meta.entry_class.__name__} is not a BasePanel")
                return None

            return instance

        except Exception as e:
            # ERROR BOUNDARY: Return None, don't crash
            logger.warning(f"Failed to instantiate panel {meta.item_id}: {e}")
            return None


# Register with LoaderRegistry
LoaderRegistry.register("panel", PanelLoader)
