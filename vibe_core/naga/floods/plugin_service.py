"""
NAGA Flood: PluginService.

Phase 3A: Paradox Resolution - Code-Loading must be protected.

Surgical Overrides:
- scan: SESHA audit + TAKSHAKA manifest validation
- load: TAKSHAKA security check before loading

NAGA Assignment:
- SESHA: Audit trail for plugin operations
- TAKSHAKA: Validate manifests and plugin code
"""

import logging
from pathlib import Path
from typing import Any, List, Optional

from vibe_core.naga.mixins import SeshaMixin, TakshakaMixin
from vibe_core.plugin_service import PluginService

logger = logging.getLogger("NAGA.FLOOD.PLUGIN")


class FloodedPluginService(SeshaMixin, TakshakaMixin, PluginService):
    """
    NAGA-Flooded PluginService.

    Original PluginService wrapped with:
    - SESHA: Audit logging for all plugin operations
    - TAKSHAKA: Security validation of plugins

    isinstance(flooded, PluginService) == True  # Preserved!
    """

    def scan(self, force: bool = False) -> int:
        """
        Scan for plugins - with NAGA protection.

        SESHA: Records scan operation
        TAKSHAKA: Validates discovered manifests
        """
        # === SESHA: Record scan start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="plugin.scan.start",
                source="FloodedPluginService",
                details={"force": force, "workspace": str(self._workspace)},
            )

        # === Execute original scan ===
        count = super().scan(force)

        # === TAKSHAKA: Validate discovered plugins ===
        if self.takshaka:
            for plugin_id, info in self._plugins.items():
                # Check plugin path for suspicious patterns
                path_str = str(info.path) if info.path else ""
                toxicity = self.takshaka.scan_toxicity(path_str)
                if toxicity.blocked:
                    logger.warning(f"TAKSHAKA: Suspicious plugin path for {plugin_id}: {toxicity.patterns}")

        # === SESHA: Record scan complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="plugin.scan.complete",
                source="FloodedPluginService",
                details={"plugins_found": count},
            )

        return count

    def load(self, plugin_id: str) -> Optional[Any]:
        """
        Load a plugin - with NAGA protection.

        TAKSHAKA: Security check before loading
        SESHA: Audit trail for load operation
        """
        # === SESHA: Record load attempt ===
        if self.sesha:
            self.sesha.record_event(
                event_type="plugin.load.start",
                source="FloodedPluginService",
                details={"plugin_id": plugin_id},
            )

        # === TAKSHAKA: Pre-load security check ===
        if self.takshaka:
            info = self.get(plugin_id)
            if info:
                # Validate plugin capabilities
                caps_str = ",".join(info.capabilities) if info.capabilities else ""
                toxicity = self.takshaka.scan_toxicity(caps_str)
                if toxicity.blocked:
                    logger.warning(f"TAKSHAKA: Blocked plugin {plugin_id} - suspicious capabilities")
                    if self.sesha:
                        self.sesha.record_event(
                            event_type="plugin.load.blocked",
                            source="FloodedPluginService",
                            details={
                                "plugin_id": plugin_id,
                                "reason": "suspicious_capabilities",
                            },
                        )
                    return None

        # === Execute original load ===
        try:
            instance = super().load(plugin_id)
        except Exception as e:
            if self.sesha:
                self.sesha.record_event(
                    event_type="plugin.load.error",
                    source="FloodedPluginService",
                    details={"plugin_id": plugin_id, "error": str(e)},
                )
            raise

        # === SESHA: Record success ===
        if self.sesha and instance:
            self.sesha.record_event(
                event_type="plugin.load.complete",
                source="FloodedPluginService",
                details={"plugin_id": plugin_id},
            )

        return instance

    def load_all(self) -> List[Any]:
        """
        Load all plugins - with NAGA protection.

        SESHA: Audit trail for batch load
        """
        # === SESHA: Record batch load start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="plugin.load_all.start",
                source="FloodedPluginService",
                details={"total_plugins": len(self._plugins)},
            )

        # === Execute original (uses our protected load() method) ===
        instances = super().load_all()

        # === SESHA: Record batch load complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="plugin.load_all.complete",
                source="FloodedPluginService",
                details={"loaded_count": len(instances)},
            )

        return instances


# =============================================================================
# Factory
# =============================================================================


def get_flooded_plugin_service(
    workspace: Optional[Path] = None,
) -> FloodedPluginService:
    """Get a NAGA-flooded PluginService."""
    return FloodedPluginService(workspace=workspace)
