"""
Plugin Protocol - OPUS-307 Phase B

Single interface for plugin discovery, loading, and management.
Mirrors CartridgeProtocol pattern for consistency.

GAD-000: One protocol, one service, via DI.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class PluginInfo:
    """Plugin metadata from manifest."""

    plugin_id: str
    name: str
    description: str
    version: str
    priority: int
    path: Path
    capabilities: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    enabled: bool = True
    execution_mode: str = "in_process"


@runtime_checkable
class PluginServiceProtocol(Protocol):
    """
    Protocol for plugin management.

    Single source of truth for:
    - Plugin discovery (manifest scanning)
    - Plugin loading (class instantiation)
    - Plugin listing for CLI
    - DI integration
    """

    def scan(self, force: bool = False) -> int:
        """
        Scan for plugin manifests.

        Args:
            force: Force rescan even if already scanned

        Returns:
            Number of plugins found
        """
        ...

    def get(self, plugin_id: str) -> Optional[PluginInfo]:
        """
        Get plugin info by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            PluginInfo or None if not found
        """
        ...

    def list(self) -> List[PluginInfo]:
        """
        List all discovered plugins.

        Returns:
            List of PluginInfo sorted by priority
        """
        ...

    def load(self, plugin_id: str) -> Optional[Any]:
        """
        Load plugin instance (lazy).

        Args:
            plugin_id: Plugin identifier

        Returns:
            KernelPlugin instance or None if not found
        """
        ...

    def load_all(self) -> List[Any]:
        """
        Load all enabled plugins.

        Returns:
            List of KernelPlugin instances, sorted by dependency/priority
        """
        ...
