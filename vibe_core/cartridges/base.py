#!/usr/bin/env python3
"""
CartridgeBase - ARCH-050

Base class for all Vibe OS cartridges (apps).

A Cartridge represents a specialized domain agent with:
  1. Configuration (metadata, dependencies)
  2. Initialization (load playbooks, tools, LLM provider)
  3. Execution (run_playbook, invoke_action)
  4. Offline-first operation (SmartLocalProvider by default)

Example:
    class ArchivistCartridge(CartridgeBase):
        name = "archivist"
        version = "1.0.0"
        description = "Knowledge base builder - reads documents and summarizes"

        def __init__(self, vibe_root: Path | None = None):
            super().__init__(vibe_root=vibe_root)

        async def summarize_documents(self, folder: str) -> str:
            # Implementation
            pass

    # Usage
    archivist = ArchivistCartridge()
    summary = await archivist.summarize_documents("/path/to/docs")
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CartridgeConfig:
    """Configuration for a cartridge."""

    name: str
    version: str
    description: str
    author: str = "Vibe Agency"
    dependencies: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    offline_capable: bool = True
    requires_api: bool = False


@dataclass
class CartridgeSpec:
    """Metadata about a cartridge."""

    name: str
    version: str
    description: str
    author: str
    class_name: str
    module_path: str
    dependencies: list[str]
    tools: list[str]
    offline_capable: bool
    requires_api: bool
    registered_at: str


class CartridgeBase:
    """
    Base class for all Vibe OS cartridges.

    A cartridge is a specialized application within Vibe OS that solves
    a specific problem (document analysis, code refactoring, research, etc.).

    Responsibilities:
    1. Initialize with domain-specific configuration
    2. Load playbooks (workflow definitions)
    3. Manage tools specific to the domain
    4. Execute actions (run_playbook, invoke_action)
    5. Report status and results

    Design Principles:
    - Offline-first (uses SmartLocalProvider by default)
    - Single responsibility (solve one problem well)
    - Composable (can call other cartridges)
    - Discoverable (registrable in CartridgeRegistry)
    """

    # Metadata (override in subclasses)
    name: str = "base"
    version: str = "0.0.1"
    description: str = "Base cartridge"
    author: str = "Vibe Agency"

    def __init__(self, vibe_root: Path | None = None):
        """
        Initialize the cartridge.

        Args:
            vibe_root: Path to vibe-agency root (auto-detected if None)
        """
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.execution_count = 0

        # Auto-detect vibe root if not provided
        if vibe_root is None:
            vibe_root = self._detect_vibe_root()

        self.vibe_root = Path(vibe_root)

        # Initialize offline-first LLM provider
        self.llm_provider = self._init_llm_provider()

        # Load playbooks and tools
        self.playbooks = self._load_playbooks()
        self.tools = self._load_tools()

        logger.info(f"✅ Cartridge '{self.name}' initialized at {self.vibe_root}")

    def _detect_vibe_root(self) -> Path:
        """Auto-detect the vibe-agency root directory."""
        cwd = Path.cwd()

        # Check if we're already in the root
        if (cwd / ".vibe").exists():
            return cwd

        # Check parent directories
        for parent in cwd.parents:
            if (parent / ".vibe").exists():
                return parent

        raise RuntimeError(
            "Could not detect vibe-agency root. Please set VIBE_ROOT environment variable."
        )

    def _init_llm_provider(self):
        """Initialize the LLM provider (offline-first)."""
        try:
            # Import here to avoid circular imports
            from vibe_core.runtime.providers.factory import LLMProviderFactory

            return LLMProviderFactory.create("smart_local")
        except Exception:
            logger.debug(
                f"Could not initialize LLM provider for {self.name} (fallback to local mode)"
            )
            return None

    def _load_playbooks(self) -> dict[str, Any]:
        """
        Load playbooks for this cartridge.

        Playbooks are YAML workflow definitions stored in:
        vibe_core/cartridges/{cartridge_name}/playbooks/

        Returns:
            Dictionary mapping playbook names to their definitions
        """
        playbooks = {}
        playbook_dir = self.vibe_root / "vibe_core" / "cartridges" / self.name / "playbooks"

        if playbook_dir.exists():
            for playbook_file in playbook_dir.glob("*.yaml"):
                try:
                    import yaml

                    with open(playbook_file) as f:
                        playbooks[playbook_file.stem] = yaml.safe_load(f)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load playbook {playbook_file}: {e}")

        return playbooks

    def _load_tools(self) -> dict[str, Any]:
        """
        Load tools for this cartridge.

        Tools are Python functions/classes that this cartridge uses.
        Override in subclasses to define custom tools.

        Returns:
            Dictionary mapping tool names to their implementations
        """
        return {}

    def get_config(self) -> CartridgeConfig:
        """Get the cartridge configuration."""
        return CartridgeConfig(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            dependencies=[],
            tools=list(self.tools.keys()),
            offline_capable=True,
        )

    def get_spec(self) -> CartridgeSpec:
        """Get the cartridge specification (metadata)."""
        return CartridgeSpec(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            class_name=self.__class__.__name__,
            module_path=self.__class__.__module__,
            dependencies=[],
            tools=list(self.tools.keys()),
            offline_capable=True,
            requires_api=False,
            registered_at=self.created_at,
        )

    def report_status(self) -> dict[str, Any]:
        """Report current status of the cartridge."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "execution_count": self.execution_count,
            "playbooks": list(self.playbooks.keys()),
            "tools": list(self.tools.keys()),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, version={self.version!r})"

    def __str__(self) -> str:
        return f"{self.name} v{self.version} - {self.description}"


__all__ = ["CartridgeBase", "CartridgeConfig", "CartridgeSpec"]
