"""
Agent Loader - Auto-discovery for Agents.

INHERITS FROM UnifiedLoader - The fraktal pattern!

Specifics for Agents:
- Supports steward.json as alias for manifest.json (backward compat)
- Uses AgentManifest dataclass for manifest parsing
- Looks for *Cartridge classes in cartridge_main.py
- Validates agents with is_valid_agent()
"""

import importlib.util
import logging
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.loaders import ItemMeta, LoaderRegistry, UnifiedLoader
from vibe_core.steward.protocol import AgentManifest, is_valid_agent

logger = logging.getLogger("STEWARD.LOADER")


# Type aliases (keep for backward compatibility)
AgentRegistry = Dict[str, AgentManifest]
AgentInstances = Dict[str, Any]
AgentMetadata = Dict[str, ItemMeta]  # Now uses ItemMeta from UnifiedLoader

# Backward compat: AgentMeta is now ItemMeta
AgentMeta = ItemMeta


class AgentLoader(UnifiedLoader):
    """
    Auto-discovery loader for Agents.

    Inherits from UnifiedLoader - VEDA-4 pattern.

    Agent-specific:
    - manifest_filenames includes "steward.json" for backward compat
    - entry_suffix is "_main.py" (cartridge_main.py)
    - Validates with is_valid_agent()

    Usage:
        # Just discover manifests
        manifests, meta = AgentLoader.discover_manifests()

        # Discover and load cartridge instances
        agents, meta = AgentLoader.discover_and_load()
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "agent"
    scan_paths = [
        # Runtime Separation (OPUS-016): Library containers have HIGHEST priority
        Path("library"),
        # Source folders (for development/fallback)
        Path("vibe_core/cartridges/system"),
        Path("vibe_core/cartridges/agent_city"),
    ]
    manifest_filenames = ["manifest.json", "steward.json"]  # steward.json for backward compat
    entry_suffix = "_main.py"
    base_class = None  # We use is_valid_agent() instead

    # === AGENT-SPECIFIC OVERRIDES ===

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[AgentInstances, AgentMetadata]:
        """
        Discover and load all agents (folders + containers).

        OPUS-307 Phase F: Uses ManifestRegistry for cartridges.
        Still scans library path for .vibe containers.

        Supports precedence: Container (.vibe) > Folder.
        Supports recursion: Scans 'hollows/' inside containers.
        """
        # OPUS-307: If no custom paths, use ManifestRegistry + library scan
        if scan_paths is None:
            return cls._discover_from_registry_and_library(config)

        paths = scan_paths

        # Runtime Separation (OPUS-016): Add library_path from config
        # Runtime Separation (OPUS-016): Add library_path from config
        if config:
            lib_path_str = None

            # 1. Try PhoenixConfig Object Access (Attribute access)
            if hasattr(config, "paths"):
                try:
                    # config.paths.system.library_path
                    # Need to handle if paths or system is missing/None
                    paths_cfg = getattr(config, "paths", None)
                    if paths_cfg:
                        system_cfg = getattr(paths_cfg, "system", None)
                        if system_cfg:
                            lib_path_str = getattr(system_cfg, "library_path", None)
                except Exception:
                    pass

            # 2. Try Dict Access (if not found yet)
            if not lib_path_str and isinstance(config, dict):
                try:
                    lib_path_str = config.get("paths", {}).get("system", {}).get("library_path")
                    # Fallback: check top level for simpler configs or passed args
                    if not lib_path_str:
                        lib_path_str = config.get("library_path")
                except Exception:
                    pass

            if lib_path_str:
                lib_path = Path(lib_path_str)
                if lib_path.exists():
                    logger.info(f"[loader] 📚 Adding Runtime Library: {lib_path}")
                    # Prepend to prioritize Library over System?
                    # User said: "Prioritize Library Containers over System Cartridges? (Yes, Library is User Space/Runtime)."
                    if isinstance(paths, list):
                        paths.insert(0, lib_path)
                    else:
                        # If it was a tuple or default? cls.scan_paths is list.
                        paths = [lib_path] + list(paths)

        # Candidate tracking: agent_id -> (instance, metadata)
        candidates: Dict[str, Tuple[Any, ItemMeta]] = {}

        for base_path in paths:
            if not base_path.exists():
                continue

            logger.info(f"[agent] Scanning {base_path}...")

            # Helper to process candidates
            def add_candidate(meta: ItemMeta, instance: Any):
                if not meta or not meta.loaded_successfully:
                    return

                # Get ID (handle agent_id vs id)
                aid = meta.manifest.get("agent_id") or meta.item_id

                # Precedence Logic
                if aid in candidates:
                    existing_instance, existing_meta = candidates[aid]
                    is_new_container = str(meta.manifest_path).endswith(".vibe")
                    is_old_container = str(existing_meta.manifest_path).endswith(".vibe")

                    if is_new_container and not is_old_container:
                        logger.info(f"  🆙 Upgrading {aid} to Container (shadows folder)")
                        candidates[aid] = (instance, meta)
                    elif not is_new_container and is_old_container:
                        logger.debug(f"  ⏭️ Ignoring folder {aid} (shadowed by container)")
                    else:
                        logger.warning(f"  ⚠️ Duplicate agent ID {aid}. Keeping first.")
                else:
                    candidates[aid] = (instance, meta)
                    type_label = "container" if str(meta.manifest_path).endswith(".vibe") else "folder"
                    logger.info(f"  ✅ Loaded: {aid} ({type_label})")

            # Process items
            for item in base_path.iterdir():
                # 1. Folder Support
                if item.is_dir():
                    if item.name.startswith((".", "_")):
                        continue

                    # Check for manifest
                    if cls._find_manifest(item):
                        meta = cls._process_item_directory(item, config)
                        if meta and meta.loaded_successfully:
                            instance = cls._create_instance(meta, config)
                            # Allow manifest-only loading (instance=None) for Generics
                            add_candidate(meta, instance)

                # 2. Container Support (.vibe)
                elif item.suffix == ".vibe" and importlib.util.find_spec("zipfile") and zipfile.is_zipfile(item):
                    meta = cls._process_container(item, config)
                    if meta and meta.loaded_successfully:
                        instance = cls._create_instance(meta, config)
                        add_candidate(meta, instance)

                        # RECURSION (Fractal Depth)
                        if meta.entry_path:
                            hollows_path = meta.entry_path / "hollows"
                            if hollows_path.exists() and hollows_path.is_dir():
                                logger.info(f"  🪆 Scanning hollows in {meta.item_id}...")
                                nested_agents, nested_meta = cls.discover_and_load(
                                    scan_paths=[hollows_path], config=config
                                )
                                for nid, nmeta in nested_meta.items():
                                    ninstance = nested_agents.get(nid)
                                    add_candidate(nmeta, ninstance)

        # Build results
        instances = {aid: inst for aid, (inst, _) in candidates.items() if inst is not None}
        metadata = {aid: meta for aid, (_, meta) in candidates.items()}

        return instances, metadata

    @classmethod
    def _discover_from_registry_and_library(
        cls,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[AgentInstances, AgentMetadata]:
        """
        OPUS-307 Phase F: Discover agents via ManifestRegistry + library containers.

        Uses ManifestRegistry for cartridges (NO iterdir!).
        Still scans library path for .vibe containers.
        """
        from vibe_core.loaders.manifest_registry import ManifestRegistry

        candidates: Dict[str, Tuple[Any, ItemMeta]] = {}

        def add_candidate(meta: ItemMeta, instance: Any):
            if not meta or not meta.loaded_successfully:
                return
            aid = meta.manifest.get("agent_id") or meta.item_id
            if aid not in candidates:
                candidates[aid] = (instance, meta)
                logger.info(f"  ✅ Loaded: {aid}")

        # 1. Load cartridges from ManifestRegistry
        ManifestRegistry._ensure_scanned()
        entries = ManifestRegistry.get_enabled("cartridge")

        logger.info(f"[agent] Loading {len(entries)} cartridges from ManifestRegistry...")

        for entry in entries:
            meta = cls._process_item_directory(entry.parent_dir, config)
            if meta and meta.loaded_successfully:
                instance = cls._create_instance(meta, config)
                add_candidate(meta, instance)

        # 2. Scan library path for .vibe containers (if exists)
        library_path = Path("library")
        if library_path.exists():
            logger.info(f"[agent] Scanning library: {library_path}...")
            for item in library_path.iterdir():
                if item.suffix == ".vibe" and zipfile.is_zipfile(item):
                    meta = cls._process_container(item, config)
                    if meta and meta.loaded_successfully:
                        instance = cls._create_instance(meta, config)
                        add_candidate(meta, instance)

        # Build results
        instances = {aid: inst for aid, (inst, _) in candidates.items() if inst is not None}
        metadata = {aid: meta for aid, (_, meta) in candidates.items()}

        logger.info(f"[agent] Total agents loaded: {len(instances)}")
        return instances, metadata

    @classmethod
    def _validate_manifest(cls, manifest: Dict[str, Any]) -> List[str]:
        """
        Agent-specific manifest validation.

        Supports BOTH formats:
        - New format: top-level id, name, type
        - Old format (steward.json): identity.agent_id, identity.name
        """
        errors = []

        # Check for id/name in either format
        has_id = bool(
            manifest.get("id")
            or manifest.get("agent_id")
            or (manifest.get("identity") and manifest["identity"].get("agent_id"))
        )
        has_name = bool(manifest.get("name") or (manifest.get("identity") and manifest["identity"].get("name")))

        if not has_id:
            errors.append("Manifest must have 'id' or 'identity.agent_id'")
        if not has_name:
            errors.append("Manifest must have 'name' or 'identity.name'")

        # Agent-specific: compliance_level must be 0-3
        compliance = (
            manifest.get("compliance_level")
            or (manifest.get("governance") and manifest["governance"].get("compliance_level"))
            or 1
        )
        if not isinstance(compliance, int) or compliance < 0 or compliance > 3:
            errors.append("compliance_level must be 0-3")

        return errors

    @classmethod
    def _find_entry_point(cls, item_dir: Path, manifest: Dict[str, Any]) -> Optional[Path]:
        """
        Agent-specific entry point finding.

        Agents use cartridge_main.py (not agent_main.py).
        """
        # Check manifest for explicit entry point
        entry_point = manifest.get("entry_point")
        if entry_point:
            return item_dir / entry_point

        # Default for agents: cartridge_main.py
        cartridge_entry = item_dir / "cartridge_main.py"
        if cartridge_entry.exists():
            return cartridge_entry

        # Support GAD-000 content/ directory structure
        cartridge_entry_content = item_dir / "content" / "cartridge_main.py"
        if cartridge_entry_content.exists():
            return cartridge_entry_content

        return None

    @classmethod
    def _load_entry_class(
        cls,
        entry_path: Path,
        item_id: str,
        manifest: Dict[str, Any],
    ) -> Optional[Type]:
        """
        Agent-specific class loading.

        Looks for *Cartridge classes and validates with is_valid_agent().
        """
        import importlib.util
        import inspect
        import sys

        # Import module dynamically
        module_name = f"cartridge_{item_id}"
        spec = importlib.util.spec_from_file_location(module_name, entry_path)

        if spec is None or spec.loader is None:
            logger.debug(f"Cannot create module spec for {entry_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Register in sys.modules for pickle/multiprocessing
        sys.modules[module_name] = module

        # Find Cartridge class (classes ending with 'Cartridge')
        cartridge_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Cartridge") and obj.__module__ == module_name:
                cartridge_classes.append((name, obj))

        if not cartridge_classes:
            logger.debug(f"No *Cartridge class found in {entry_path}")
            return None

        # Return first valid cartridge class
        return cartridge_classes[0][1]

    @classmethod
    def _create_instance(
        cls,
        meta: ItemMeta,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """
        Agent-specific instantiation.

        Validates instance with is_valid_agent().
        """
        if not meta.entry_class:
            return None

        try:
            # Try with config first
            try:
                instance = meta.entry_class(config=meta.config)
            except TypeError:
                instance = meta.entry_class()

            # Agent-specific: validate with is_valid_agent
            if not is_valid_agent(instance):
                logger.debug(f"{meta.entry_class.__name__} does not implement AgentProtocol")
                return None

            return instance

        except Exception as e:
            logger.warning(f"Failed to instantiate {meta.item_id}: {e}")
            return None

    # === BACKWARD COMPATIBILITY METHODS ===

    @classmethod
    def discover_manifests(
        cls,
        scan_paths: Optional[List[Path]] = None,
    ) -> Tuple[AgentRegistry, AgentMetadata]:
        """
        Discover all agent manifests.

        Backward compatible wrapper around UnifiedLoader.discover_manifests().
        Returns AgentManifest objects instead of raw dicts.
        """
        paths = scan_paths or cls.scan_paths
        raw_manifests, metadata = super().discover_manifests(scan_paths=paths)

        # Convert raw manifests to AgentManifest objects
        agent_manifests: AgentRegistry = {}
        for item_id, manifest_dict in raw_manifests.items():
            try:
                agent_manifest = AgentManifest.from_dict(manifest_dict, agent_id_fallback=item_id)
                agent_manifests[item_id] = agent_manifest
            except Exception as e:
                logger.warning(f"Failed to parse AgentManifest for {item_id}: {e}")

        return agent_manifests, metadata

    @classmethod
    def validate_manifest(cls, manifest: AgentManifest) -> List[str]:
        """
        Validate an AgentManifest.

        Backward compatible method.
        """
        errors = []

        if not manifest.agent_id:
            errors.append("agent_id is required")

        if not manifest.name:
            errors.append("name is required")

        if manifest.compliance_level < 0 or manifest.compliance_level > 3:
            errors.append("compliance_level must be 0-3")

        return errors


# Register with LoaderRegistry
LoaderRegistry.register("agent", AgentLoader)
