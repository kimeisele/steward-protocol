"""
Bridge Loader - Auto-discovery for MANAS Bridge modules.

OPUS-171: VEDA-4 Pattern for Bridge Auto-Discovery

OPUS-167 Bridges extracted from CognitiveKernel:
- GenesisBridge: Infrastructure auto-generation (Stadtamt)
- WeaverBridge: State ↔ Knowledge bridging
- LoggerBridge: Observation logging to OPUS.md

INHERITS: CodeModuleLoader (VEDA-4 compliant)

PATTERN:
    Same as ActionLoader/SenseLoader but for bridges.
    Scans: vibe_core/plugins/opus_assistant/manas/*_bridge.py
    Discovers: Classes ending with "Bridge"
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.loaders.code_module_loader import (
    CodeMetadata,
    CodeModuleLoader,
    CodeModuleLoadError,
    CodeRegistry,
)

logger = logging.getLogger("BRIDGE.LOADER")


# Type aliases
BridgeRegistry = CodeRegistry
BridgeMetadata = CodeMetadata


class BridgeLoadError(CodeModuleLoadError):
    """Raised when bridge loading fails in STRICT MODE."""

    pass


class BridgeLoader(CodeModuleLoader):
    """
    Auto-discovery loader for MANAS Bridge modules.

    OPUS-171: VEDA-4 Pattern for Bridges.

    Bridges are extracted components from CognitiveKernel that handle
    specific cross-cutting concerns:
    - GenesisBridge: GAD-000 infrastructure generation
    - WeaverBridge: State ↔ Knowledge bridging
    - LoggerBridge: OPUS.md observation logging

    Usage:
        # Discover and load all bridges
        bridges, meta = BridgeLoader.discover_and_load(
            workspace=Path.cwd(),
            config=manas_config,
        )

        # Access specific bridges
        genesis = bridges.get("genesis_bridge")
        weaver = bridges.get("weaver_bridge")
        logger = bridges.get("logger_bridge")

        # Or use convenience method
        weaver = BridgeLoader.get_bridge("weaver_bridge")
    """

    # === LOADER CONFIG ===
    item_type = "bridge"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas")]
    file_pattern = "*_bridge.py"
    base_class_name = None  # No common base class, match by name suffix

    # === STRICT MODE ===
    strict_mode = False  # Bridges are optional

    # === CLASS NAME SUFFIX ===
    class_name_suffix = "Bridge"

    @classmethod
    def _is_valid_subclass(cls, candidate: Type) -> bool:
        """
        Check if candidate is a valid Bridge class.

        Override parent to match by name suffix instead of inheritance.
        Bridges don't have a common base class - they're identified by suffix.
        """
        return candidate.__name__.endswith(cls.class_name_suffix)

    @classmethod
    def _instantiate_item(
        cls,
        item_class: Type,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Instantiate a bridge class.

        Bridges take workspace and config in __init__.
        """
        workspace = workspace or Path.cwd()
        config = config or {}

        # Try different constructor signatures
        try:
            # Full signature: workspace + config
            return item_class(workspace=workspace, config=config)
        except TypeError:
            try:
                # Workspace only
                return item_class(workspace=workspace)
            except TypeError:
                # No args
                return item_class()

    # === BRIDGE-SPECIFIC METHODS ===

    @classmethod
    def get_bridge(
        cls,
        name: str,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Get a specific bridge by name."""
        bridges, _ = cls.discover_and_load(workspace=workspace, config=config)
        return bridges.get(name)

    @classmethod
    def list_bridges(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered bridge names."""
        return cls.list_items(workspace)


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("bridge", BridgeLoader)
