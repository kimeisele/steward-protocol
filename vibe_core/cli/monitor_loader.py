"""
MonitorLoader - Discovers system monitors from plugins.

The "Glass Box" discovery layer - finds all observable endpoints
in the system without hardcoding.

VEDA-4 Pattern:
  SHABDA   → Scan plugins for get_monitors()
  ARTHA    → Build monitor registry
  PRATYAYA → Validate monitor definitions
  KARMA    → Return discoverable monitors
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x7defd610"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from .monitors import MonitorDefinition, MonitorRegistry, MonitorSnapshot, SystemMonitor

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MONITOR_LOADER")


class MonitorLoader:
    """
    Discovers and manages system monitors from plugins.

    Similar to CLILoader, but for introspection instead of commands.
    """

    # Cache for discovered monitors
    _cache: Optional[MonitorRegistry] = None
    _monitors: Dict[str, SystemMonitor] = {}

    @classmethod
    def discover_monitors(
        cls,
        kernel: "RealVibeKernel",
        force_refresh: bool = False,
    ) -> MonitorRegistry:
        """
        Discover all monitors from registered plugins.

        Args:
            kernel: The booted kernel with plugins
            force_refresh: Bypass cache

        Returns:
            Dict mapping monitor_id to MonitorDefinition
        """
        if not force_refresh and cls._cache is not None:
            return cls._cache

        registry: MonitorRegistry = {}
        cls._monitors = {}

        # Get all plugins from kernel
        plugins = []
        if hasattr(kernel, "plugin_manager"):
            plugins = kernel.plugin_manager.plugins
        elif hasattr(kernel, "plugins"):
            plugins = kernel.plugins
        elif hasattr(kernel, "_plugins"):
            plugins = kernel._plugins
        else:
            logger.warning("Kernel has no plugin source (checked plugin_manager, plugins, _plugins)")
            return registry

        for plugin in plugins:
            try:
                monitors = plugin.get_monitors()
                for monitor in monitors:
                    if monitor.monitor_id in registry:
                        logger.warning(f"Monitor collision: {monitor.monitor_id} already registered")
                        continue

                    definition = MonitorDefinition(
                        monitor_id=monitor.monitor_id,
                        monitor_type=monitor.monitor_type,
                        plugin_id=plugin.plugin_id,
                        description=monitor.description,
                    )
                    registry[monitor.monitor_id] = definition
                    cls._monitors[monitor.monitor_id] = monitor
                    logger.debug(f"Registered monitor: {monitor.monitor_id}")

            except Exception as e:
                logger.warning(f"Failed to get monitors from {plugin.plugin_id}: {e}")

        cls._cache = registry
        logger.info(f"MonitorLoader: Discovered {len(registry)} monitors")
        return registry

    @classmethod
    def get_snapshot(
        cls,
        monitor_id: str,
        kernel: Optional["RealVibeKernel"] = None,
    ) -> Optional[MonitorSnapshot]:
        """
        Get a point-in-time snapshot from a specific monitor.

        Args:
            monitor_id: The monitor to query
            kernel: Optional kernel for re-discovery

        Returns:
            MonitorSnapshot or None if not found
        """
        # Re-discover if needed
        if monitor_id not in cls._monitors and kernel:
            cls.discover_monitors(kernel, force_refresh=True)

        monitor = cls._monitors.get(monitor_id)
        if not monitor:
            return None

        try:
            return monitor.snapshot()
        except Exception as e:
            logger.error(f"Failed to get snapshot from {monitor_id}: {e}")
            return None

    @classmethod
    def get_all_snapshots(
        cls,
        kernel: "RealVibeKernel",
    ) -> Dict[str, MonitorSnapshot]:
        """
        Get snapshots from all monitors.

        Args:
            kernel: The booted kernel

        Returns:
            Dict mapping monitor_id to snapshot
        """
        cls.discover_monitors(kernel)
        snapshots = {}

        for monitor_id, monitor in cls._monitors.items():
            try:
                snapshots[monitor_id] = monitor.snapshot()
            except Exception as e:
                logger.warning(f"Failed to snapshot {monitor_id}: {e}")

        return snapshots

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached monitors."""
        cls._cache = None
        cls._monitors = {}

    @classmethod
    def list_monitors(cls) -> List[MonitorDefinition]:
        """Get list of all discovered monitors."""
        if cls._cache is None:
            return []
        return list(cls._cache.values())
