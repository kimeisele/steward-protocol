"""
PluginService - OPUS-307 Phase B

Unified plugin management service.
Wraps PluginLoader + ManifestRegistry into single source of truth.

GAD-000: Single service, accessed via ServiceRegistry.

NAGA HARDENING (Gemini Prescription):
    PluginService is the entry point for ALL plugin code.
    If a malicious plugin gets loaded, the entire system is compromised.

    Solution: Inherit from NagaBaseService + @naga_governed
    - Sesha: Records every scan/load operation (audit trail)
    - Chitragupta: Profiles execution time (anomaly detection)
    - Takshaka: Validates plugin paths (path traversal protection)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x1a57370a"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.plugin import PluginInfo, PluginServiceProtocol

logger = logging.getLogger("PLUGIN_SERVICE")


class PluginService(NagaBaseService, PluginServiceProtocol):
    """
    Unified plugin management.

    Features:
    - Lazy scanning (manifests only at boot)
    - Lazy loading (classes imported on demand)
    - Single cache for Kernel and CLI
    - Priority/dependency-based ordering

    NOTE: Use get_plugin_service() to access via ServiceRegistry.
    """

    def __init__(self, workspace: Optional[Path] = None):
        super().__init__(service_name="PluginService")
        self._workspace = workspace or Path.cwd()
        self._plugins: Dict[str, PluginInfo] = {}
        self._instances: Dict[str, Any] = {}
        self._scanned = False

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "PluginService":
        """Get singleton instance (backward compat - use get_plugin_service())."""
        return get_plugin_service(workspace)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.unregister(PluginServiceProtocol)

    @naga_governed(operation="plugin_scan", log_args=True)
    def scan(self, force: bool = False) -> int:
        """Scan for plugin manifests. NAGA-GOVERNED: Recorded by Sesha, profiled by Chitragupta."""
        if self._scanned and not force:
            return len(self._plugins)

        self._plugins.clear()

        # Use ManifestRegistry for discovery
        from vibe_core.loaders.manifest_registry import ManifestRegistry

        ManifestRegistry._ensure_scanned()
        entries = ManifestRegistry.get_enabled("plugin")

        for entry in entries:
            try:
                manifest = entry.manifest or {}

                plugin_id = entry.id

                info = PluginInfo(
                    plugin_id=plugin_id,
                    name=manifest.get("name", plugin_id),
                    description=manifest.get("description", ""),
                    version=manifest.get("version", "0.1.0"),
                    priority=entry.priority,
                    path=entry.path.parent,  # manifest path -> parent dir
                    capabilities=manifest.get("capabilities", []),
                    depends_on=manifest.get("depends_on", []),
                    enabled=entry.enabled,
                    execution_mode=manifest.get("execution_mode", "in_process"),
                )

                self._plugins[plugin_id] = info

            except Exception as e:
                logger.warning(f"Failed to parse plugin {entry.id}: {e}")

        self._scanned = True
        logger.info(f"Scanned {len(self._plugins)} plugins")
        return len(self._plugins)

    def get(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin info by ID."""
        if not self._scanned:
            self.scan()
        return self._plugins.get(plugin_id)

    def list(self) -> List[PluginInfo]:
        """List all plugins, sorted by priority."""
        if not self._scanned:
            self.scan()
        # Sort by priority (lower = earlier boot)
        return sorted(self._plugins.values(), key=lambda p: p.priority)

    @naga_governed(operation="plugin_load", log_args=True, validate_input=True)
    def load(self, plugin_id: str) -> Optional[Any]:
        """Load a single plugin instance (lazy). NAGA-GOVERNED: Validated by Takshaka, recorded by Sesha."""
        if plugin_id in self._instances:
            return self._instances[plugin_id]

        info = self.get(plugin_id)
        if not info:
            return None

        # Use PluginLoader for actual loading
        from vibe_core.plugin_loader import PluginLoader

        plugins, _ = PluginLoader.discover_and_load(scan_paths=[info.path.parent])

        instance = plugins.get(plugin_id)
        if instance:
            self._instances[plugin_id] = instance

        return instance

    @naga_governed(operation="plugin_load_all", log_args=True)
    def load_all(self) -> List[Any]:
        """
        Load all enabled plugins. NAGA-GOVERNED: Recorded by Sesha, profiled by Chitragupta.

        Uses PluginLoader.discover_from_registry() for proper
        dependency resolution and priority ordering.
        """
        from vibe_core.plugin_loader import PluginLoader

        plugins_map, metadata = PluginLoader.discover_from_registry()

        # Cache instances
        for plugin_id, instance in plugins_map.items():
            self._instances[plugin_id] = instance

        # Return sorted by dependency/priority (PluginLoader already sorts)
        return list(plugins_map.values())

    def get_loaded(self, plugin_id: str) -> Optional[Any]:
        """Get already-loaded plugin instance."""
        return self._instances.get(plugin_id)

    def list_loaded(self) -> List[Any]:
        """List all loaded plugin instances."""
        return list(self._instances.values())


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_plugin_service(workspace: Optional[Path] = None) -> PluginService:
    """
    Get PluginService through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        PluginService → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees plugin operations)
    - NAGA profiling (Chitragupta tracks scan/load timing)
    - NAGA isolation (Kaliya handles plugin errors)

    Args:
        workspace: Optional workspace path (only used on first creation)

    Returns:
        PluginService wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(PluginServiceProtocol)
    if existing is not None:
        return existing

    # Create new instance
    instance = PluginService(workspace)

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(PluginServiceProtocol, instance)
    logger.info("✅ PluginService registered via ServiceRegistry (NAGA-observed)")

    return ServiceRegistry.get(PluginServiceProtocol)  # type: ignore
