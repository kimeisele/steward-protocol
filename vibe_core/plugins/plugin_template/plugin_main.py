"""
Plugin Template - Golden Template for New Plugins.

Copy this folder, rename it, and modify to create new plugins.

Steps:
1. cp -r vibe_core/plugins/plugin_template vibe_core/plugins/my_plugin
2. Edit manifest.json: id, name, description, hooks, priority
3. Rename this class and implement your hooks
4. Set enabled: true in manifest.json
"""

import logging
from typing import TYPE_CHECKING, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("PLUGIN_TEMPLATE")


class PluginTemplatePlugin(KernelPlugin):
    """
    Plugin Template - Copy and modify for new plugins.

    Priority: 999 (disabled by default)
    """

    @property
    def plugin_id(self) -> str:
        return "plugin_template"

    @property
    def priority(self) -> int:
        return 999

    def __init__(self):
        """Initialize plugin state."""
        self._kernel: Optional["KernelProtocol"] = None

    def on_boot(self, kernel: "KernelProtocol") -> None:
        """Called when kernel boots."""
        self._kernel = kernel
        logger.info("Plugin template booted")

    def on_shutdown(self, kernel: "KernelProtocol") -> None:
        """Called when kernel shuts down."""
        logger.info("Plugin template shutdown")
