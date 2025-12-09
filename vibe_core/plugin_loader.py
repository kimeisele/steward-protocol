"""
Plugin Loader - Auto-discovery for Kernel Plugins.

INHERITS FROM UnifiedLoader - The fraktal pattern!

Specifics for Plugins:
- Supports both NEW-style folders (manifest.json) and OLD-style .py files
- Uses KernelPlugin as base class
- Looks for *Plugin classes in plugin_main.py or module file
- Returns sorted by priority
"""

import importlib
import logging
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.loaders import ItemMeta, LoaderRegistry, UnifiedLoader
from vibe_core.plugin_protocol import KernelPlugin

logger = logging.getLogger("PLUGIN.LOADER")


# Type aliases (backward compat)
PluginRegistry = Dict[str, KernelPlugin]
PluginMetadata = Dict[str, ItemMeta]
PluginMeta = ItemMeta


class PluginLoader(UnifiedLoader):
    """
    Auto-discovery loader for Kernel Plugins.

    Inherits from UnifiedLoader - VEDA-4 pattern.

    Plugin-specific:
    - Supports both new-style (folder + manifest.json) and old-style (single .py file)
    - base_class is KernelPlugin
    - Returns plugins sorted by priority

    Usage:
        # Discover all plugins
        plugins, meta = PluginLoader.discover_and_load()
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "plugin"
    scan_paths = [Path("vibe_core/plugins")]
    manifest_filenames = ["manifest.json"]
    entry_suffix = "_main.py"
    base_class = KernelPlugin

    # =========================================================================
    # OVERRIDE: Discover and Load (with backward compat for old-style plugins)
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[PluginRegistry, PluginMetadata]:
        """
        Discover and load all plugins.

        Supports BOTH:
        - NEW-style: folders with manifest.json + plugin_main.py
        - OLD-style: single .py files in plugins directory

        Returns:
            Tuple of (plugin_instances, metadata), sorted by priority
        """
        paths = scan_paths or cls.scan_paths
        all_plugins: List[KernelPlugin] = []
        metadata: PluginMetadata = {}

        for base_path in paths:
            if not base_path.exists():
                logger.debug(f"[plugin] Scan path does not exist: {base_path}")
                continue

            logger.info(f"[plugin] Scanning {base_path}...")

            # Process directories (NEW-style)
            for item in base_path.iterdir():
                if item.is_dir():
                    # Skip hidden and __pycache__
                    if item.name.startswith((".", "_")):
                        continue

                    # NEW-style: folder with manifest.json
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        meta = cls._process_item_directory(item, config)
                        if meta and meta.loaded_successfully:
                            instance = cls._create_instance(meta, config)
                            if instance:
                                all_plugins.append(instance)
                                metadata[meta.item_id] = meta
                                logger.info(f"  ✅ Loaded: {meta.item_id} (new-style)")
                        elif meta:
                            metadata[meta.item_id] = meta

                elif item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                    # OLD-style: single .py file
                    old_plugins, old_meta = cls._load_old_style_plugin(item, base_path)
                    all_plugins.extend(old_plugins)
                    metadata.update(old_meta)

                elif item.is_file() and item.suffix == ".vibe" and zipfile.is_zipfile(item):
                    # NEW: Container support
                    # Use base implementation for container processing
                    meta = cls._process_container(item, config)
                    if meta and meta.loaded_successfully:
                        instance = cls._create_instance(meta, config)
                        if instance:
                            all_plugins.append(instance)
                            metadata[meta.item_id] = meta
                            logger.info(f"  ✅ Loaded: {meta.item_id} (container)")
                    elif meta:
                        metadata[meta.item_id] = meta

        # Sort by dependencies (Topological Sort)
        sorted_plugins = cls._sort_plugins_by_dependency(all_plugins, metadata)

        # Build registry
        registry: PluginRegistry = {p.plugin_id: p for p in sorted_plugins}

        logger.info(f"[plugin] Total plugins loaded: {len(registry)}")
        return registry, metadata

    @classmethod
    def _sort_plugins_by_dependency(
        cls,
        plugins: List[KernelPlugin],
        metadata: PluginMetadata,
    ) -> List[KernelPlugin]:
        """
        Sort plugins by dependency order (Topological Sort).

        Rules:
        1. If A depends on B, B come before A.
        2. If no dependency, use priority (lower number = earlier boot).
        3. Stable sort for equal priorities.
        """
        # Map plugin_id -> plugin instance
        plugin_map = {p.plugin_id: p for p in plugins}

        # Build graph: plugin_id -> set of dependencies
        graph: Dict[str, set] = {}
        for p in plugins:
            meta = metadata.get(p.plugin_id)
            deps = []
            if meta and meta.manifest:
                deps = meta.manifest.get("depends_on", [])
                # Also support 'dependencies' field (legacy/alternate name)
                if not deps:
                    deps = meta.manifest.get("dependencies", [])

            # Filter deps that actually exist to avoid cycles/errors on missing optional deps
            # (Strict validation typically happens elsewhere, here we just sort what we have)
            valid_deps = {d for d in deps if d in plugin_map}
            graph[p.plugin_id] = valid_deps

        # Topological sort
        result = []
        visited = set()
        temp_mark = set()  # For cycle detection

        def visit(node_id):
            if node_id in temp_mark:
                logger.warning(f"Circular dependency detected involving {node_id}")
                return
            if node_id in visited:
                return

            temp_mark.add(node_id)

            # Visit dependencies first
            for dep_id in graph.get(node_id, []):
                visit(dep_id)

            temp_mark.remove(node_id)
            visited.add(node_id)
            if node_id in plugin_map:
                result.append(plugin_map[node_id])

        # Visit nodes in priority order (so independent nodes respect priority)
        # Lower priority number = boot first (standard convention in this system?)
        # Wait, manifest.json says "priority": 15 for Envoy.
        # Tools is priority 5.
        # So Lower "priority" value means EARLIER boot.
        # sorted(plugins, key=lambda p: p.priority) ensures we visit high-priority (low number) first.

        priority_sorted = sorted(plugins, key=lambda p: p.priority)

        for p in priority_sorted:
            visit(p.plugin_id)

        return result

    @classmethod
    def _load_old_style_plugin(
        cls,
        file_path: Path,
        base_path: Path,
    ) -> Tuple[List[KernelPlugin], PluginMetadata]:
        """
        Load an old-style plugin from a single .py file.

        Backward compat for plugins like envoy_ui.py, settings_ui.py
        """
        plugins: List[KernelPlugin] = []
        metadata: PluginMetadata = {}

        try:
            # Convert file path to module path
            # e.g., vibe_core/plugins/envoy_ui.py -> vibe_core.plugins.envoy_ui
            relative_path = file_path.relative_to(base_path.parent.parent)
            module_name = str(relative_path.with_suffix("")).replace("/", ".")

            module = importlib.import_module(module_name)

            # Find KernelPlugin subclasses
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, KernelPlugin) and attr is not KernelPlugin:
                    try:
                        instance = attr()
                        plugins.append(instance)

                        # Create metadata for old-style plugin
                        meta = ItemMeta(
                            item_id=instance.plugin_id,
                            item_type="plugin",
                            manifest={
                                "id": instance.plugin_id,
                                "type": "plugin",
                                "priority": instance.priority,
                            },
                            manifest_path=file_path,  # Use .py file as "manifest"
                            entry_path=file_path,
                            entry_class=attr,
                            loaded_successfully=True,
                        )
                        metadata[instance.plugin_id] = meta
                        logger.info(f"  ✅ Loaded: {instance.plugin_id} (old-style)")

                    except Exception as e:
                        logger.error(f"   ❌ Failed to instantiate plugin {attr_name}: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to load plugin module {file_path.name}: {e}")

        return plugins, metadata

    # =========================================================================
    # OVERRIDES FOR PLUGIN-SPECIFIC BEHAVIOR
    # =========================================================================

    @classmethod
    def _validate_manifest(cls, manifest: Dict[str, Any]) -> List[str]:
        """
        Plugin-specific manifest validation.

        Checks for required plugin fields.
        """
        errors = []

        # Must have id or name
        if not manifest.get("id") and not manifest.get("name"):
            errors.append("Manifest must have 'id' or 'name'")

        # Priority must be 0-100
        priority = manifest.get("priority", 50)
        if not isinstance(priority, int) or priority < 0 or priority > 100:
            errors.append("priority must be 0-100")

        return errors

    @classmethod
    def _create_instance(
        cls,
        meta: ItemMeta,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[KernelPlugin]:
        """
        Plugin-specific instantiation.

        Validates instance is a KernelPlugin.
        """
        if not meta.entry_class:
            return None

        try:
            # Try with config first
            try:
                instance = meta.entry_class(config=meta.config)
            except TypeError:
                instance = meta.entry_class()

            # Validate it's a KernelPlugin
            if not isinstance(instance, KernelPlugin):
                logger.warning(f"{meta.entry_class.__name__} is not a KernelPlugin")
                return None

            return instance

        except Exception as e:
            logger.warning(f"Failed to instantiate {meta.item_id}: {e}")
            return None

    # =========================================================================
    # BACKWARD COMPAT: Static discover method
    # =========================================================================

    @staticmethod
    def discover(plugin_dir: str = "vibe_core/plugins") -> List[KernelPlugin]:
        """
        Backward compatible discover method.

        Returns list of plugins sorted by priority.
        """
        plugins, _ = PluginLoader.discover_and_load(scan_paths=[Path(plugin_dir)])
        return list(plugins.values())


# Register with LoaderRegistry
LoaderRegistry.register("plugin", PluginLoader)
