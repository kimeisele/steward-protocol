"""
My Plugin - Example plugin with CLI commands.

Copy this folder to vibe_core/plugins/my_plugin/ and modify.

Steps:
1. cp -r docs/templates/cli_plugin vibe_core/plugins/my_plugin
2. Edit manifest.json: id, name, namespace, commands
3. Rename MyPlugin class and implement handlers
4. Run: steward my-hello --name Kim
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x9ade801c"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.cli.monitors import SystemMonitor
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MY_PLUGIN")


class MyPlugin(KernelPlugin):
    """
    Example plugin with CLI commands.

    Demonstrates:
    - Offline command (no kernel needed)
    - Boot command (kernel required)
    - GAD-000 compliant handlers (return data, not print)
    """

    @property
    def plugin_id(self) -> str:
        return "my_plugin"

    @property
    def priority(self) -> int:
        return 100

    def __init__(self):
        """Initialize plugin state."""
        self._kernel: Optional["RealVibeKernel"] = None

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots."""
        self._kernel = kernel
        logger.info("MyPlugin booted")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel shuts down."""
        logger.info("MyPlugin shutdown")

    # =========================================================================
    # CLI HANDLERS - GAD-000 Compliant (return data, not print!)
    # =========================================================================

    def cmd_hello(self, name: str = "World") -> Dict[str, Any]:
        """
        Say hello - OFFLINE command (no kernel needed).

        Usage:
            steward my-hello
            steward my-hello --name Kim
            steward --json my-hello
        """
        return {
            "greeting": f"Hello, {name}!",
            "timestamp": datetime.now().isoformat(),
        }

    def cmd_status(self) -> Dict[str, Any]:
        """
        Show plugin status - BOOT command (kernel required).

        Usage:
            steward my-status
            steward --json my-status
        """
        if not self._kernel:
            return {"error": "Kernel not available"}

        return {
            "plugin_id": self.plugin_id,
            "kernel_available": True,
            "agents": len(self._kernel.agent_registry),
            "timestamp": datetime.now().isoformat(),
        }

    # =========================================================================
    # MONITORS - Optional, for 'steward observe'
    # =========================================================================

    def get_monitors(self) -> List["SystemMonitor"]:
        """
        Return monitors for Glass Box introspection.

        Optional - implement if you have observable state.
        See vibe_core/cli/monitors.py for SystemMonitor protocol.
        """
        return []
