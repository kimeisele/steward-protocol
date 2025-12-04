"""
Agent Loader - Auto-discovery for Agents.

Mirrors the SectionLoader pattern from phoenix/section_loader.py:
- Scans agent directories for manifest files (steward.json or manifest.json)
- Validates manifests against schema
- Loads cartridge implementations dynamically
- Returns dict of agent_id -> AgentManifest or agent instance

FRACTAL PATTERN:
    phoenix/section_loader.py  → Discovers ConfigSection classes
    steward/loader.py          → Discovers Agent manifests/cartridges
"""

import importlib.util
import inspect
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from vibe_core.steward.protocol import AgentManifest, is_valid_agent

logger = logging.getLogger("STEWARD.LOADER")


@dataclass
class AgentMeta:
    """Metadata about a discovered agent."""

    agent_id: str
    manifest: AgentManifest
    manifest_path: Path
    cartridge_path: Optional[Path]
    cartridge_class: Optional[Type]
    loaded_successfully: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "OK" if self.loaded_successfully else f"FAILED: {self.error}"
        return f"<Agent:{self.agent_id} cartridge={self.cartridge_path is not None} status={status}>"


# Type aliases
AgentRegistry = Dict[str, AgentManifest]
AgentInstances = Dict[str, Any]  # agent_id -> instance
AgentMetadata = Dict[str, AgentMeta]


class AgentLoader:
    """
    Auto-discovery loader for Agents.

    Scans directories for manifest files and optionally loads cartridges.

    Usage:
        # Just discover manifests
        manifests, meta = AgentLoader.discover_manifests()

        # Discover and load cartridge instances
        agents, meta = AgentLoader.discover_and_load()
    """

    # Default directories to scan
    DEFAULT_SCAN_PATHS = [
        Path("steward/system_agents"),  # System agents
        Path("agent_city/registry"),  # Citizen agents
    ]

    # Supported manifest filenames (in order of preference)
    MANIFEST_FILENAMES = ["manifest.json", "steward.json"]

    # Cache discovered manifests (class-level)
    _manifest_cache: Optional[AgentRegistry] = None

    @classmethod
    def discover_manifests(
        cls,
        scan_paths: Optional[List[Path]] = None,
    ) -> Tuple[AgentRegistry, AgentMetadata]:
        """
        Discover all agent manifests in the scan paths.

        Args:
            scan_paths: List of directories to scan (default: system_agents + agent_city)

        Returns:
            Tuple of:
            - manifests: Dict mapping agent_id -> AgentManifest
            - metadata: Dict mapping agent_id -> AgentMeta
        """
        if scan_paths is None:
            scan_paths = cls.DEFAULT_SCAN_PATHS

        manifests: AgentRegistry = {}
        metadata: AgentMetadata = {}

        for base_path in scan_paths:
            if not base_path.exists():
                logger.debug(f"Scan path does not exist: {base_path}")
                continue

            logger.info(f"Scanning {base_path} for agents...")

            # Find all directories that contain manifest files
            for agent_dir in base_path.iterdir():
                if not agent_dir.is_dir():
                    continue

                # Skip hidden directories and __pycache__
                if agent_dir.name.startswith((".", "_")):
                    continue

                agent_id = agent_dir.name

                # Find manifest file
                manifest_path = cls._find_manifest_file(agent_dir)
                if manifest_path is None:
                    logger.debug(f"  No manifest found in {agent_dir}")
                    continue

                # Load and parse manifest
                try:
                    manifest = cls._load_manifest(manifest_path, agent_id)
                    manifests[manifest.agent_id] = manifest

                    # Check for cartridge
                    cartridge_path = agent_dir / "cartridge_main.py"

                    metadata[manifest.agent_id] = AgentMeta(
                        agent_id=manifest.agent_id,
                        manifest=manifest,
                        manifest_path=manifest_path,
                        cartridge_path=cartridge_path if cartridge_path.exists() else None,
                        cartridge_class=None,
                        loaded_successfully=True,
                    )

                    logger.debug(f"  Discovered: {manifest.agent_id} ({manifest.name})")

                except Exception as e:
                    logger.warning(f"  Failed to load manifest from {manifest_path}: {e}")
                    metadata[agent_id] = AgentMeta(
                        agent_id=agent_id,
                        manifest=AgentManifest(agent_id=agent_id, name=agent_id),
                        manifest_path=manifest_path,
                        cartridge_path=None,
                        cartridge_class=None,
                        loaded_successfully=False,
                        error=str(e),
                    )

        logger.info(f"Discovered {len(manifests)} agent manifests")
        return manifests, metadata

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        config: Optional[Any] = None,
    ) -> Tuple[AgentInstances, AgentMetadata]:
        """
        Discover manifests AND load cartridge instances.

        Args:
            scan_paths: Directories to scan
            config: Optional config to pass to cartridge constructors

        Returns:
            Tuple of:
            - agents: Dict mapping agent_id -> agent instance
            - metadata: Dict mapping agent_id -> AgentMeta
        """
        manifests, metadata = cls.discover_manifests(scan_paths)

        agents: AgentInstances = {}

        for agent_id, meta in metadata.items():
            if not meta.loaded_successfully:
                continue

            if meta.cartridge_path is None:
                logger.debug(f"  {agent_id}: No cartridge, skipping instance creation")
                continue

            # Try to load cartridge
            try:
                agent, cartridge_class = cls._load_cartridge(
                    meta.cartridge_path,
                    agent_id,
                    config,
                )

                if agent is not None:
                    agents[agent_id] = agent
                    meta.cartridge_class = cartridge_class
                    logger.info(f"  Loaded cartridge: {agent_id}")
                else:
                    meta.loaded_successfully = False
                    meta.error = "Cartridge returned None"

            except Exception as e:
                logger.warning(f"  Failed to load cartridge for {agent_id}: {e}")
                meta.loaded_successfully = False
                meta.error = str(e)

        logger.info(f"Loaded {len(agents)} agent cartridges")
        return agents, metadata

    @classmethod
    def _find_manifest_file(cls, agent_dir: Path) -> Optional[Path]:
        """Find manifest file in agent directory."""
        for filename in cls.MANIFEST_FILENAMES:
            manifest_path = agent_dir / filename
            if manifest_path.exists():
                return manifest_path
        return None

    @classmethod
    def _load_manifest(cls, manifest_path: Path, agent_id_fallback: str) -> AgentManifest:
        """Load and parse a manifest file."""
        with open(manifest_path, "r") as f:
            data = json.load(f)

        return AgentManifest.from_dict(data, agent_id_fallback=agent_id_fallback)

    @classmethod
    def _load_cartridge(
        cls,
        cartridge_path: Path,
        agent_id: str,
        config: Optional[Any] = None,
    ) -> Tuple[Optional[Any], Optional[Type]]:
        """
        Dynamically load a cartridge from cartridge_main.py.

        Args:
            cartridge_path: Path to cartridge_main.py
            agent_id: Agent identifier
            config: Optional config to pass to constructor

        Returns:
            Tuple of (agent_instance, cartridge_class) or (None, None) on failure
        """
        # Import module dynamically
        module_name = f"cartridge_{agent_id}"
        spec = importlib.util.spec_from_file_location(module_name, cartridge_path)

        if spec is None or spec.loader is None:
            logger.debug(f"Cannot create module spec for {cartridge_path}")
            return None, None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Register in sys.modules for pickle/multiprocessing
        import sys

        sys.modules[module_name] = module

        # Find Cartridge class (classes ending with 'Cartridge')
        cartridge_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Cartridge") and obj.__module__ == module_name:
                cartridge_classes.append((name, obj))

        if not cartridge_classes:
            logger.debug(f"No *Cartridge class found in {cartridge_path}")
            return None, None

        # Use first valid cartridge class
        class_name, CartridgeClass = cartridge_classes[0]

        # Instantiate
        try:
            if config:
                try:
                    agent = CartridgeClass(config=config)
                except TypeError:
                    agent = CartridgeClass()
            else:
                agent = CartridgeClass()
        except Exception as e:
            logger.warning(f"Cartridge init error for {class_name}: {e}")
            return None, None

        # Verify it's a valid agent
        if not is_valid_agent(agent):
            logger.debug(f"{class_name} does not implement AgentProtocol")
            return None, None

        return agent, CartridgeClass

    @classmethod
    def validate_manifest(cls, manifest: AgentManifest) -> List[str]:
        """
        Validate a manifest against schema rules.

        Args:
            manifest: AgentManifest to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not manifest.agent_id:
            errors.append("agent_id is required")

        if not manifest.name:
            errors.append("name is required")

        if manifest.compliance_level < 0 or manifest.compliance_level > 3:
            errors.append("compliance_level must be 0-3")

        return errors

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the manifest cache (useful for testing)."""
        cls._manifest_cache = None
