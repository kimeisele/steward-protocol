"""
CartridgeService - OPUS-307 Consolidation

Unified cartridge management service.
Replaces: ManifestRegistry (cartridge parts), CartridgeRegistry, LazyCartridgeRegistry.

GAD-000: Single source of truth, accessed via ServiceRegistry.
"""

import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from vibe_core.protocols.cartridge import CartridgeInfo, CartridgeProtocol, ToolInfo
from vibe_core.utils import safe_read_yaml

logger = logging.getLogger("CARTRIDGE_SERVICE")


class CartridgeService(CartridgeProtocol):
    """
    Unified cartridge management.

    Features:
    - Lazy scanning (YAML only at boot, no Python imports)
    - Lazy loading (classes imported on demand)
    - Single cache for CLI and Kernel
    - Tool discovery and instantiation
    """

    _instance: Optional["CartridgeService"] = None

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._cartridges: Dict[str, CartridgeInfo] = {}
        self._classes: Dict[str, Type] = {}
        self._tools: Dict[str, Any] = {}  # key: "cartridge.tool"
        self._scanned = False

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "CartridgeService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(workspace)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def scan(self, force: bool = False) -> int:
        """Scan for cartridge manifests (YAML only, no imports)."""
        if self._scanned and not force:
            return len(self._cartridges)

        self._cartridges.clear()

        # Scan cartridge directories
        cartridge_roots = [
            self._workspace / "vibe_core" / "cartridges" / "system",
            self._workspace / "vibe_core" / "cartridges" / "agent_city",
        ]

        for root in cartridge_roots:
            if not root.exists():
                continue

            for cartridge_dir in root.iterdir():
                if not cartridge_dir.is_dir():
                    continue
                if cartridge_dir.name.startswith("_"):
                    continue

                self._scan_cartridge(cartridge_dir)

        self._scanned = True
        logger.info(f"Scanned {len(self._cartridges)} cartridges")
        return len(self._cartridges)

    def _scan_cartridge(self, cartridge_dir: Path) -> None:
        """Scan a single cartridge directory."""
        yaml_path = cartridge_dir / "cartridge.yaml"

        try:
            manifest = safe_read_yaml(yaml_path)

            if not manifest:
                return

            # Parse manifest (handle both flat and nested formats)
            meta = manifest.get("meta", manifest)
            agent = manifest.get("agent", manifest)

            cartridge_id = cartridge_dir.name
            full_id = meta.get("id", cartridge_id)
            if "." in full_id:
                cartridge_id = full_id.split(".")[-1]

            info = CartridgeInfo(
                cartridge_id=cartridge_id,
                name=meta.get("name", cartridge_id),
                domain=agent.get("domain", "UNKNOWN"),
                description=meta.get("description", ""),
                version=meta.get("version", "0.1.0"),
                path=cartridge_dir,
                capabilities=agent.get("capabilities", []),
                enabled=manifest.get("config", {}).get("enabled", True),
            )

            # Scan tools
            tools_dir = cartridge_dir / "tools"
            if tools_dir.exists():
                for tool_file in tools_dir.glob("*.py"):
                    if tool_file.name.startswith("_"):
                        continue

                    tool_id = tool_file.stem
                    if tool_id.endswith("_tool"):
                        tool_id = tool_id[:-5]

                    # Infer class name
                    # Handle both "_tool" and "_tools" suffixes (e.g., git_tools.py → GitTools)
                    base_name = "".join(word.title() for word in tool_id.split("_"))
                    # Only add "Tool" suffix if name doesn't already end with "Tool" or "Tools"
                    if base_name.endswith("Tools"):
                        class_name = base_name  # Already has Tools suffix (e.g., GitTools)
                    elif base_name.endswith("Tool"):
                        class_name = base_name  # Already has Tool suffix
                    else:
                        class_name = base_name + "Tool"

                    info.tools[tool_id] = ToolInfo(
                        tool_id=tool_id,
                        tool_file=tool_file.name,
                        tool_class=class_name,
                    )

            self._cartridges[cartridge_id] = info

        except Exception as e:
            logger.warning(f"Failed to scan {cartridge_dir}: {e}")

    def get(self, cartridge_id: str) -> Optional[CartridgeInfo]:
        """Get cartridge info by ID."""
        if not self._scanned:
            self.scan()
        return self._cartridges.get(cartridge_id)

    def list(self) -> List[CartridgeInfo]:
        """List all cartridges."""
        if not self._scanned:
            self.scan()
        return list(self._cartridges.values())

    def load_class(self, cartridge_id: str) -> Optional[Type]:
        """Load cartridge class (lazy)."""
        if cartridge_id in self._classes:
            return self._classes[cartridge_id]

        info = self.get(cartridge_id)
        if not info:
            return None

        # Try cartridge_main.py
        main_path = info.path / "cartridge_main.py"
        if not main_path.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location(
                f"cartridge_{cartridge_id}",
                main_path,
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find cartridge class
            class_name = "".join(word.title() for word in cartridge_id.split("_")) + "Cartridge"
            cls = getattr(module, class_name, None)

            if cls:
                self._classes[cartridge_id] = cls

            return cls

        except Exception as e:
            logger.error(f"Failed to load {cartridge_id}: {e}")
            return None

    def load_tool(self, cartridge_id: str, tool_id: str) -> Optional[Any]:
        """Load a tool from a cartridge (lazy)."""
        cache_key = f"{cartridge_id}.{tool_id}"
        if cache_key in self._tools:
            return self._tools[cache_key]

        info = self.get(cartridge_id)
        if not info:
            return None

        tool_info = info.tools.get(tool_id)
        if not tool_info:
            return None

        tool_path = info.path / "tools" / tool_info.tool_file
        if not tool_path.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location(
                f"tool_{cartridge_id}_{tool_id}",
                tool_path,
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            cls = getattr(module, tool_info.tool_class, None)
            if not cls:
                return None

            instance = cls()
            self._tools[cache_key] = instance
            return instance

        except Exception as e:
            logger.error(f"Failed to load tool {cache_key}: {e}")
            return None

    def instantiate(self, cartridge_id: str, config: Optional[Dict] = None) -> Optional[Any]:
        """Instantiate a cartridge agent."""
        cls = self.load_class(cartridge_id)
        if not cls:
            return None

        try:
            return cls(config)
        except Exception as e:
            logger.error(f"Failed to instantiate {cartridge_id}: {e}")
            return None
