"""
Renderer Loader - Auto-discovery for UI Renderers.

INHERITS FROM UnifiedLoader - The fractal pattern!

Specifics for Renderers:
- Supports both NEW-style folders (manifest.json) and OLD-style single .py files
- Uses BaseRenderer as base class
- Looks for *Renderer classes in renderer.py or module file
- Returns sorted by priority
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x4b5b92c9"  # GenesisByte: parampara % 37 == 0

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.loaders import ItemMeta, LoaderRegistry, UnifiedLoader

logger = logging.getLogger("RENDERER.LOADER")


# Forward reference to avoid circular import
BaseRenderer: Optional[Type] = None


def _get_base_renderer() -> Type:
    """Lazy load BaseRenderer to avoid circular import."""
    global BaseRenderer
    if BaseRenderer is None:
        from vibe_core.plugins.interface.renderers.base import (
            BaseRenderer as BR,
        )

        BaseRenderer = BR
    return BaseRenderer


class RendererLoader(UnifiedLoader):
    """
    Auto-discovery loader for UI Renderers.

    Inherits from UnifiedLoader - VEDA-4 pattern.

    Renderer-specific:
    - Supports both new-style (folder + manifest.json) and old-style (single .py file)
    - base_class is BaseRenderer
    - Returns renderers sorted by priority

    Usage:
        # Discover all renderers
        renderers, meta = RendererLoader.discover_and_load(kernel=kernel)
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "renderer"
    # Use absolute path based on module location (fixes test cwd issues)
    scan_paths = [Path(__file__).parent / "renderers"]
    manifest_filenames = ["manifest.json"]
    entry_suffix = ".py"

    # base_class set dynamically to avoid circular import
    @classmethod
    def _get_base_class(cls) -> Type:
        return _get_base_renderer()

    # Store kernel reference for renderer instantiation
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
        Discover and load all renderers.

        Supports BOTH:
        - NEW-style: folders with manifest.json + renderer.py
        - OLD-style: single .py files in renderers directory

        Args:
            scan_paths: Override default scan paths
            config: Global config
            kernel: Kernel instance for renderer instantiation

        Returns:
            Tuple of (renderer_instances, metadata)
        """
        cls._kernel = kernel
        paths = scan_paths or cls.scan_paths

        instances: Dict[str, Any] = {}
        metadata: Dict[str, ItemMeta] = {}

        for base_path in paths:
            if not base_path.exists():
                logger.debug(f"[renderer] Scan path does not exist: {base_path}")
                continue

            logger.debug(f"[renderer] Scanning {base_path}...")

            for item in base_path.iterdir():
                # Skip hidden, __pycache__, base.py, _template
                if item.name.startswith((".", "_")) or item.name == "__pycache__":
                    continue
                if item.name == "base.py":
                    continue

                meta = None

                # 1. Directory with manifest.json (NEW-style)
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        meta = cls._process_item_directory(item, config)
                    else:
                        # Directory without manifest - try to load renderer.py
                        renderer_py = item / "renderer.py"
                        if renderer_py.exists():
                            meta = cls._process_old_style_directory(item, config)

                # 2. Single .py file (OLD-style)
                elif item.is_file() and item.suffix == ".py":
                    meta = cls._process_old_style_file(item, config)

                if meta is None:
                    continue

                metadata[meta.item_id] = meta

                # Create instance if loaded successfully
                if meta.loaded_successfully and meta.entry_class:
                    instance = cls._create_instance(meta, config)
                    if instance:
                        instances[meta.item_id] = instance
                        logger.info(f"  ✅ Loaded renderer: {meta.item_id}")
                    else:
                        meta.loaded_successfully = False
                        meta.error = "Instance creation failed"
                elif not meta.loaded_successfully:
                    logger.warning(f"  ⚠️ Renderer {meta.item_id} failed: {meta.error}")

        logger.info(f"[renderer] Loaded {len(instances)} renderers")
        return instances, metadata

    @classmethod
    def _process_old_style_directory(
        cls,
        item_dir: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[ItemMeta]:
        """
        Process a directory without manifest.json (OLD-style).

        Creates synthetic manifest from renderer class.
        """
        renderer_py = item_dir / "renderer.py"
        if not renderer_py.exists():
            return None

        item_id = item_dir.name

        try:
            # Load module and find renderer class
            entry_class = cls._load_entry_class_from_file(renderer_py, item_id)
            if not entry_class:
                return None

            # Create synthetic manifest
            manifest = {
                "type": "renderer",
                "id": item_id,
                "name": entry_class.__name__,
                "entry_point": "renderer.py",
                "entry_class": entry_class.__name__,
                "enabled": True,
                "priority": 50,
            }

            return ItemMeta(
                item_id=item_id,
                item_type="renderer",
                manifest=manifest,
                manifest_path=item_dir,
                entry_path=renderer_py,
                entry_class=entry_class,
                loaded_successfully=True,
            )

        except Exception as e:
            logger.warning(f"Failed to load renderer from {item_dir}: {e}")
            return ItemMeta(
                item_id=item_id,
                item_type="renderer",
                manifest={},
                manifest_path=item_dir,
                entry_path=None,
                entry_class=None,
                loaded_successfully=False,
                error=str(e),
            )

    @classmethod
    def _process_old_style_file(
        cls,
        file_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[ItemMeta]:
        """
        Process a single .py file (OLD-style).

        Creates synthetic manifest from renderer class.
        """
        item_id = file_path.stem

        try:
            entry_class = cls._load_entry_class_from_file(file_path, item_id)
            if not entry_class:
                return None

            # Create synthetic manifest
            manifest = {
                "type": "renderer",
                "id": item_id,
                "name": entry_class.__name__,
                "entry_point": file_path.name,
                "entry_class": entry_class.__name__,
                "enabled": True,
                "priority": 50,
            }

            return ItemMeta(
                item_id=item_id,
                item_type="renderer",
                manifest=manifest,
                manifest_path=file_path,
                entry_path=file_path,
                entry_class=entry_class,
                loaded_successfully=True,
            )

        except Exception as e:
            logger.warning(f"Failed to load renderer from {file_path}: {e}")
            return ItemMeta(
                item_id=item_id,
                item_type="renderer",
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
        """Load renderer class from a Python file."""
        try:
            # Build module path - use vibe_core package structure (not cwd dependent)
            abs_path = file_path.resolve()
            # Find vibe_core in the path and build module path from there
            parts = abs_path.parts
            try:
                vibe_idx = parts.index("vibe_core")
                module_parts = parts[vibe_idx:]
                module_path = ".".join(module_parts)[:-3]  # Remove .py suffix
            except ValueError:
                # Fallback: try relative to cwd if vibe_core not in path
                relative = abs_path.relative_to(Path.cwd())
                module_path = str(relative.with_suffix("")).replace("/", ".")

            module = importlib.import_module(module_path)
            base_cls = cls._get_base_class()

            # Find renderer class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, base_cls)
                    and attr is not base_cls
                    and attr.__module__ == module.__name__
                ):
                    return attr

            return None

        except Exception as e:
            logger.debug(f"Failed to import {file_path}: {e}")
            return None

    # =========================================================================
    # OVERRIDES FOR RENDERER-SPECIFIC BEHAVIOR
    # =========================================================================

    @classmethod
    def _validate_manifest(cls, manifest: Dict[str, Any]) -> List[str]:
        """Renderer-specific manifest validation."""
        errors = []

        # Must have id or name
        if not manifest.get("id") and not manifest.get("name"):
            errors.append("Manifest must have 'id' or 'name'")

        # Type should be renderer (if specified)
        if manifest.get("type") and manifest.get("type") != "renderer":
            errors.append(f"Expected type 'renderer', got '{manifest.get('type')}'")

        return errors

    @classmethod
    def _create_instance(
        cls,
        meta: ItemMeta,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Renderer-specific instantiation - requires kernel."""
        if not meta.entry_class:
            return None

        if cls._kernel is None:
            logger.warning(f"Cannot instantiate {meta.item_id}: no kernel provided")
            return None

        try:
            # Renderers require kernel in constructor
            instance = meta.entry_class(cls._kernel)

            # Validate it's a BaseRenderer
            base_cls = cls._get_base_class()
            if not isinstance(instance, base_cls):
                logger.warning(f"{meta.entry_class.__name__} is not a BaseRenderer")
                return None

            return instance

        except Exception as e:
            logger.warning(f"Failed to instantiate {meta.item_id}: {e}")
            return None


# Register with LoaderRegistry
LoaderRegistry.register("renderer", RendererLoader)
