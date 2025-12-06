"""
Unified Interface Plugin.

This plugin acts as the "Window Manager" for the system.
It loads and orchestrates multiple "Renderers", each responsible for
updating a specific Markdown file in the root directory.

Config-driven from config/interface.yaml (Phoenix Config).
Fractal: Custom agents can register their own renderers!
"""

import importlib
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from vibe_core.phoenix.sections.interface import InterfaceConfig, RendererConfig
from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.plugins.interface.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("INTERFACE_PLUGIN")


class InterfacePlugin(KernelPlugin):
    """
    Unified Interface Plugin.

    Priority: 100 (Late - UI renders after everything else updates)

    Config-driven:
    - Reads from config/interface.yaml
    - Each renderer has its own refresh interval
    - Custom renderers can be added via config (fractal!)
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
        self._interface_config: Optional[InterfaceConfig] = None
        # Track last render time per renderer for interval scheduling
        self._last_render: Dict[str, float] = {}

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots."""
        self._kernel = kernel

        # Load interface config from Phoenix Config
        self._load_interface_config()

        # Discover and load renderers
        self._load_renderers()

        # Initial render on boot - don't wait for ticks!
        self.render_all()

        logger.info(f"InterfacePlugin booted ({len(self._renderers)} views active)")

    def _load_interface_config(self) -> None:
        """Load config from config/interface.yaml."""
        try:
            # Try project root config
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "interface.yaml"
            if config_path.exists():
                self._interface_config = InterfaceConfig.from_yaml(str(config_path))
                logger.debug(f"Loaded interface config from {config_path}")
            else:
                # Fallback to defaults
                from vibe_core.phoenix.sections.interface import get_default_interface_config

                self._interface_config = get_default_interface_config()
                logger.debug("Using default interface config")
        except Exception as e:
            logger.error(f"Failed to load interface config: {e}")
            from vibe_core.phoenix.sections.interface import get_default_interface_config

            self._interface_config = get_default_interface_config()

    def on_tick_pre(self, kernel: "RealVibeKernel") -> None:
        """
        Called BEFORE task processing - ALWAYS runs even if no tasks.
        Trigger renderers based on their configured intervals.
        """
        self._render_scheduled()

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """
        Called after task processing (only if task was processed).
        UI already rendered in on_tick_pre, nothing to do here.
        """
        pass

    def _should_render(self, name: str) -> bool:
        """Check if renderer should run based on its interval."""
        if not self._interface_config:
            return True

        renderer_config = self._interface_config.get_renderer(name)
        if not renderer_config:
            return True

        interval = renderer_config.interval
        if interval <= 0:
            # 0 = render every tick
            return True

        now = time.time()
        last = self._last_render.get(name, 0)
        return (now - last) >= interval

    def _render_scheduled(self) -> None:
        """Render views that are due based on their intervals."""
        now = time.time()
        for name, renderer in self._renderers.items():
            if self._should_render(name):
                try:
                    renderer.render()
                    self._last_render[name] = now
                except Exception as e:
                    logger.error(f"Error rendering view '{name}': {e}")

    def render_all(self) -> None:
        """Force render all views (ignores intervals)."""
        for name, renderer in self._renderers.items():
            try:
                renderer.render()
                self._last_render[name] = time.time()
            except Exception as e:
                logger.error(f"Error rendering view '{name}': {e}")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up."""
        logger.info("InterfacePlugin shutting down")

    def _load_renderers(self) -> None:
        """Dynamically load renderers from the renderers/ directory."""
        renderers_pkg = "vibe_core.plugins.interface.renderers"
        renderers_path = Path(__file__).parent / "renderers"

        if not renderers_path.exists():
            logger.warning(f"Renderers directory not found: {renderers_path}")
            return

        # Get enabled renderers from config
        enabled_renderers = {}
        if self._interface_config:
            enabled_renderers = self._interface_config.get_enabled_renderers()

        # Find all renderer directories and modules
        for item in renderers_path.iterdir():
            if item.name.startswith("_") or item.name == "base.py":
                continue

            # Determine renderer name
            if item.is_dir() and (item / "renderer.py").exists():
                name = item.name
                module_path = f"{renderers_pkg}.{name}.renderer"
            elif item.is_file() and item.suffix == ".py":
                name = item.stem
                module_path = f"{renderers_pkg}.{name}"
            else:
                continue

            # Check if enabled in config
            if enabled_renderers and name not in enabled_renderers:
                logger.debug(f"Skipping disabled renderer: {name}")
                continue

            try:
                module = importlib.import_module(module_path)

                # Find the renderer class (must inherit from BaseRenderer)
                renderer_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseRenderer) and attr is not BaseRenderer:
                        renderer_class = attr
                        break

                if renderer_class:
                    self._renderers[name] = renderer_class(self._kernel)
                    self._last_render[name] = 0  # Initialize last render time
                    logger.debug(f"Loaded renderer: {name}")
                else:
                    logger.warning(f"No BaseRenderer subclass found in {module_path}")

            except Exception as e:
                logger.error(f"Failed to load renderer '{name}': {e}")

    # ==========================================================================
    # FRACTAL API - Custom Renderers
    # ==========================================================================

    def register_custom_renderer(
        self,
        name: str,
        renderer: BaseRenderer,
        interval: int = 0,
        output: str = "",
    ) -> None:
        """
        Register a custom renderer (fractal API).

        Example:
            broker_renderer = BrokerBTCRenderer(kernel)
            interface_plugin.register_custom_renderer(
                name="broker_btc",
                renderer=broker_renderer,
                interval=18000,  # 5 hours
                output="BROKER_BTC.md"
            )
        """
        self._renderers[name] = renderer
        self._last_render[name] = 0

        # Add to config for persistence
        if self._interface_config:
            config = RendererConfig(
                name=name,
                enabled=True,
                output=output or f"{name.upper()}.md",
                interval=interval,
            )
            self._interface_config.add_custom_renderer(name, config)

        logger.info(f"Registered custom renderer: {name} (interval={interval}s)")

    def unregister_custom_renderer(self, name: str) -> bool:
        """Unregister a custom renderer."""
        if name in self._renderers:
            del self._renderers[name]
            self._last_render.pop(name, None)
            if self._interface_config:
                self._interface_config.remove_custom_renderer(name)
            logger.info(f"Unregistered custom renderer: {name}")
            return True
        return False

    def get_renderer_status(self) -> Dict[str, dict]:
        """Get status of all renderers (for OPERATIONS.md)."""
        now = time.time()
        status = {}
        for name, renderer in self._renderers.items():
            last = self._last_render.get(name, 0)
            config = self._interface_config.get_renderer(name) if self._interface_config else None
            status[name] = {
                "active": True,
                "interval": config.interval if config else 0,
                "last_render": last,
                "seconds_since_render": int(now - last) if last > 0 else None,
            }
        return status
