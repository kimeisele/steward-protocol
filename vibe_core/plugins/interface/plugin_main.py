"""
Unified Interface Plugin.

This plugin acts as the "Window Manager" for the system.
It loads and orchestrates multiple "Renderers", each responsible for
updating a specific Markdown file in the root directory.
"""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from vibe_core.plugin_protocol import KernelPlugin

from .renderers.base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("INTERFACE_PLUGIN")


class InterfacePlugin(KernelPlugin):
    """
    Unified Interface Plugin.

    Priority: 100 (Late - UI renders after everything else updates)
    """

    @property
    def plugin_id(self) -> str:
        return "interface"

    @property
    def priority(self) -> int:
        return 100

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None
        self._renderers: Dict[str, BaseRenderer] = {}
        self._enabled_views: List[str] = []

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots."""
        self._kernel = kernel

        # Load config
        if hasattr(self, "config") and self.config:
            self._enabled_views = self.config.get("enabled_views", [])

        # Discover and load renderers
        self._load_renderers()

        logger.info(f"🖥️  Interface Plugin booted ({len(self._renderers)} views active)")

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """
        Called after task processing.
        Trigger all active renderers.
        """
        for name, renderer in self._renderers.items():
            try:
                renderer.render()
            except Exception as e:
                logger.error(f"Error rendering view '{name}': {e}")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up."""
        logger.info("🖥️  Interface Plugin shutting down")

    def _load_renderers(self) -> None:
        """Dynamically load renderers from the renderers/ directory."""
        renderers_pkg = "vibe_core.plugins.interface.renderers"
        renderers_path = Path(__file__).parent / "renderers"

        if not renderers_path.exists():
            logger.warning(f"Renderers directory not found: {renderers_path}")
            return

        # Iterate over modules in renderers/
        for _, name, _ in pkgutil.iter_modules([str(renderers_path)]):
            if name == "base":
                continue

            if self._enabled_views and name not in self._enabled_views:
                continue

            try:
                module = importlib.import_module(f"{renderers_pkg}.{name}")

                # Find the renderer class (must inherit from BaseRenderer)
                renderer_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseRenderer) and attr is not BaseRenderer:
                        renderer_class = attr
                        break

                if renderer_class:
                    self._renderers[name] = renderer_class(self._kernel)
                    logger.debug(f"Loaded renderer: {name}")
                else:
                    logger.warning(f"No BaseRenderer subclass found in {name}.py")

            except Exception as e:
                logger.error(f"Failed to load renderer '{name}': {e}")
