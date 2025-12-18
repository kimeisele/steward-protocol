"""
Tool Loader - VEDA-4 Wrapper around ToolDiscovery.

THE MISSING LINK:
    ToolDiscovery was standalone, not part of the LoaderRegistry.
    ToolLoader brings tools into the unified loading pattern.

FRAKTAL PRINCIPLE (Scope Support):
    - scope="global" → System-level tools (cartridges)
    - scope="opus_private" → OPUS internal tools (cognitive actions)
    - Custom scan_paths for any scope

Usage:
    # System context (global scope)
    system_loader = ToolLoader(scope="global")
    tools, meta = system_loader.load()

    # OPUS context (private scope with custom paths)
    opus_loader = ToolLoader(
        scope="opus_private",
        scan_paths=[Path("vibe_core/plugins/opus_assistant/tools")]
    )
    opus_tools, _ = opus_loader.load()

    # Class-level API (backward compat)
    tools, meta = ToolLoader.discover_and_load()
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.tool_discovery import ToolDiscovery
from vibe_core.tools.tool_protocol import Tool

logger = logging.getLogger("TOOL.LOADER")


# Type aliases
ToolRegistry = Dict[str, Tool]  # tool_name -> instance
ToolMetadata = Dict[str, Dict[str, Any]]  # tool_name -> metadata


class ToolLoadError(Exception):
    """Raised when tool loading fails."""

    pass


class ToolLoader:
    """
    VEDA-4 Wrapper around ToolDiscovery.

    Brings tools into the unified loader pattern with:
    - LoaderRegistry registration
    - Scoped instance support (FRAKTAL)
    - Same API as other loaders

    VEDA-4 PATTERN:
        SHABDA   → ToolDiscovery.discover_all_tools()
        ARTHA    → Tool protocol validation (in ToolDiscovery)
        PRATYAYA → enabled check (future)
        KARMA    → Tool instantiation (in ToolDiscovery)
    """

    # === LOADER CONFIG ===
    item_type = "tool"
    scan_paths = [
        Path("vibe_core/cartridges/system"),
        Path("vibe_core/cartridges/agent_city"),
    ]

    # === CLASS-LEVEL CACHE ===
    _tool_cache: Optional[ToolRegistry] = None
    _metadata_cache: Optional[ToolMetadata] = None

    # === INSTANCE STATE (for scoped usage) ===
    _scope: str
    _custom_scan_paths: Optional[List[Path]]
    _inst_cache: Optional[ToolRegistry]
    _inst_meta: Optional[ToolMetadata]

    def __init__(
        self,
        scope: str = "global",
        scan_paths: Optional[List[Path]] = None,
        root_path: Optional[Path] = None,
    ):
        """
        Create a scoped loader instance.

        FRAKTAL PRINCIPLE:
            - scope="global" → Uses class-level scan_paths (system tools)
            - scope="opus_private" → Uses custom paths (OPUS internal tools)

        Args:
            scope: Loader scope identifier
            scan_paths: Override scan paths for this instance
            root_path: Project root path (default: cwd)
        """
        self._scope = scope
        self._custom_scan_paths = scan_paths
        self._root_path = root_path or Path.cwd()
        self._inst_cache = None
        self._inst_meta = None

    # =========================================================================
    # CLASS-LEVEL API (backward compat, global scope)
    # =========================================================================

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
    ) -> Tuple[ToolRegistry, ToolMetadata]:
        """
        Discover and load all tools. CACHED after first call.

        Args:
            scan_paths: Override default paths
            config: Global config (for API compatibility)
            workspace: Workspace root
            force_refresh: If True, bypass cache

        Returns:
            Tuple of (tool_instances, metadata)
        """
        # Return cached if available
        if not force_refresh and cls._tool_cache is not None:
            return cls._tool_cache, cls._metadata_cache or {}

        root_path = workspace or Path.cwd()
        paths = scan_paths or cls.scan_paths

        # Use ToolDiscovery with custom paths
        discovery = ToolDiscovery(root_path=root_path)
        # Override scan paths
        if scan_paths:
            discovery.SCAN_PATHS = [str(p) for p in paths]

        tools_list = discovery.discover_all_tools()

        # Convert to registry format
        tools: ToolRegistry = {}
        metadata: ToolMetadata = {}

        for tool in tools_list:
            name = tool.name
            tools[name] = tool
            metadata[name] = {
                "class": type(tool).__name__,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema,
            }

        # Cache results
        cls._tool_cache = tools
        cls._metadata_cache = metadata

        logger.info(f"[tool] Loaded {len(tools)} tools (cached)")
        return tools, metadata

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached tool data."""
        cls._tool_cache = None
        cls._metadata_cache = None

    @classmethod
    def get_tool(cls, name: str, workspace: Optional[Path] = None) -> Optional[Tool]:
        """Get a specific tool by name."""
        tools, _ = cls.discover_and_load(workspace=workspace)
        return tools.get(name)

    @classmethod
    def list_tools(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered tool names."""
        tools, _ = cls.discover_and_load(workspace=workspace)
        return list(tools.keys())

    # =========================================================================
    # INSTANCE-LEVEL API (scoped usage - FRAKTAL)
    # =========================================================================

    def load(
        self,
        force_refresh: bool = False,
    ) -> Tuple[ToolRegistry, ToolMetadata]:
        """
        Instance method for scoped loading.

        Uses instance's custom scan_paths if set.
        """
        if not force_refresh and self._inst_cache is not None:
            return self._inst_cache, self._inst_meta or {}

        paths = self._custom_scan_paths or self.scan_paths

        # Create fresh discovery for this scope
        discovery = ToolDiscovery(root_path=self._root_path)
        discovery.SCAN_PATHS = [str(p) for p in paths]

        tools_list = discovery.discover_all_tools()

        # Convert to registry format
        tools: ToolRegistry = {}
        metadata: ToolMetadata = {}

        for tool in tools_list:
            name = tool.name
            tools[name] = tool
            metadata[name] = {
                "class": type(tool).__name__,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema,
                "scope": self._scope,
            }

        # Cache in instance (not shared with class)
        self._inst_cache = tools
        self._inst_meta = metadata

        logger.info(f"[tool:{self._scope}] Loaded {len(tools)} tools")
        return tools, metadata

    def get(self, name: str) -> Optional[Tool]:
        """Get a specific tool by name (instance method)."""
        tools, _ = self.load()
        return tools.get(name)

    def list(self) -> List[str]:
        """List all discovered tool names (instance method)."""
        tools, _ = self.load()
        return list(tools.keys())

    @property
    def scope(self) -> str:
        """Get the scope of this loader instance."""
        return self._scope


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("tool", ToolLoader)
