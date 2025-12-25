"""
Cartridge Protocol - OPUS-307 Consolidation

Single interface for cartridge discovery, loading, and management.
Replaces fragmented: ManifestRegistry, CartridgeRegistry, LazyCartridgeRegistry.

GAD-000: One protocol, one service, via DI.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Type, runtime_checkable


@dataclass
class ToolInfo:
    """Tool metadata from cartridge manifest."""

    tool_id: str
    tool_file: str
    tool_class: str
    description: str = ""
    parameters_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CartridgeInfo:
    """Unified cartridge metadata."""

    cartridge_id: str
    name: str
    domain: str
    description: str
    version: str
    path: Path
    tools: Dict[str, ToolInfo] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    enabled: bool = True


@runtime_checkable
class CartridgeProtocol(Protocol):
    """
    Protocol for cartridge management.

    Single source of truth for:
    - Cartridge discovery (manifest scanning)
    - Cartridge loading (class instantiation)
    - Tool discovery and loading
    - CLI integration
    """

    def scan(self, force: bool = False) -> int:
        """
        Scan for cartridge manifests.

        Args:
            force: Force rescan even if already scanned

        Returns:
            Number of cartridges found
        """
        ...

    def get(self, cartridge_id: str) -> Optional[CartridgeInfo]:
        """
        Get cartridge info by ID.

        Args:
            cartridge_id: Cartridge identifier

        Returns:
            CartridgeInfo or None if not found
        """
        ...

    def list(self) -> List[CartridgeInfo]:
        """
        List all discovered cartridges.

        Returns:
            List of CartridgeInfo
        """
        ...

    def load_class(self, cartridge_id: str) -> Optional[Type]:
        """
        Load cartridge class (lazy).

        Args:
            cartridge_id: Cartridge identifier

        Returns:
            Cartridge class or None if not found
        """
        ...

    def load_tool(self, cartridge_id: str, tool_id: str) -> Optional[Any]:
        """
        Load a tool from a cartridge (lazy).

        Args:
            cartridge_id: Cartridge identifier
            tool_id: Tool identifier

        Returns:
            Tool instance or None if not found
        """
        ...

    def instantiate(self, cartridge_id: str, config: Optional[Dict] = None) -> Optional[Any]:
        """
        Instantiate a cartridge agent.

        Args:
            cartridge_id: Cartridge identifier
            config: Optional configuration

        Returns:
            Cartridge instance or None if not found
        """
        ...
