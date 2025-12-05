"""
Agent Loader - Auto-discovery for Agents.

INHERITS FROM UnifiedLoader - The fraktal pattern!

Specifics for Agents:
- Supports steward.json as alias for manifest.json (backward compat)
- Uses AgentManifest dataclass for manifest parsing
- Looks for *Cartridge classes in cartridge_main.py
- Validates agents with is_valid_agent()
"""

import logging
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
        Path("vibe_core/cartridges/system"),
        Path("vibe_core/cartridges/agent_city"),
    ]
    manifest_filenames = ["manifest.json", "steward.json"]  # steward.json for backward compat
    entry_suffix = "_main.py"
    base_class = None  # We use is_valid_agent() instead

    # === AGENT-SPECIFIC OVERRIDES ===

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
