"""
Unified Interface Plugin.

This plugin acts as the "Window Manager" for the system.
It loads and orchestrates multiple "Renderers", each responsible for
updating a specific Markdown file in the root directory.

Config-driven from config/interface.yaml (Phoenix Config).
Fractal: Custom agents can register their own renderers!
"""

import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.phoenix.sections.interface import InterfaceConfig, RendererConfig
from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
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

    @property
    def pulse_phase(self) -> PulsePhase:
        """Interface renders during CLEANUP phase (after all work is done)."""
        return PulsePhase.CLEANUP

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None
        self._renderers: Dict[str, BaseRenderer] = {}
        self._interface_config: Optional[InterfaceConfig] = None
        # Track last render time per renderer for interval scheduling
        self._last_render: Dict[str, float] = {}

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots."""
        self._kernel = kernel
        self._project_root = Path.cwd()

        # Load interface config from Phoenix Config
        self._load_interface_config()

        # Discover and load renderers
        self._load_renderers()

        # OPUS-306: Skip initial render on boot for faster startup
        # Rendering will happen on first pulse (PRANA heartbeat)
        # This reduces boot time by ~14 seconds
        logger.info(f"InterfacePlugin booted ({len(self._renderers)} views active, render deferred)")

    def on_pulse(self, kernel: "RealVibeKernel", transaction: Any) -> HookResult:
        """
        CLEANUP phase: Render all UI after TaskManager has executed.

        This is called by PRANA during the CLEANUP phase (phase 4 of 4),
        ensuring the UI always shows the current state after work is done.

        Args:
            kernel: The kernel instance
            transaction: PulseTransaction (unused for rendering)

        Returns:
            HookResult indicating success
        """
        try:
            self._render_scheduled()
            logger.info("🎨 CLEANUP: Interface rendered (UI synced to current state)")
            return HookResult.ok(data={"renderers": len(self._renderers)})
        except Exception as e:
            logger.error(f"Interface rendering failed: {e}", exc_info=True)
            return HookResult.error(f"Interface rendering failed: {e}")

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
        """
        Render views that are due based on their intervals.

        UNIFIED UI ARCHITECTURE:
        - InterfacePlugin is the KING (single writer)
        - Renderers are SLAVES (content generators only)
        - All writes go through InterfacePlugin with UNIFIED headers

        Law 2 (Error Boundaries):
        - Each renderer wrapped in try/except
        - One bad renderer doesn't kill the entire UI system
        - Error placeholder written instead of crash

        Skipped in test mode to prevent file overwrites.
        Skipped during git operations to prevent conflicts.
        """
        if self._is_test_mode():
            return

        if self._is_git_in_progress():
            return

        for name in self._renderers:
            self.render_view(name)

    def render_view(self, name: str, force: bool = False) -> None:
        """
        Render a specific view.

        Args:
            name: Name of the renderer to run
            force: If True, bypass interval check and test mode check
        """
        # Skip if test mode (unless forced)
        if self._is_test_mode() and not force:
            return

        # Skip if not due (unless forced)
        if not force and not self._should_render(name):
            return

        renderer = self._renderers.get(name)
        if not renderer:
            logger.warning(f"Renderer '{name}' not found")
            return

        now = time.time()
        try:
            # NEW: Try unified approach first (generate_content)
            content = renderer.generate_content()
            if content is not None:
                # KING writes with unified header
                self._write_unified(renderer, content)

            self._last_render[name] = now
        except Exception as e:
            logger.error(f"Renderer '{name}' failed: {e}")
            # Law 2: Write error placeholder instead of crashing
            self._render_error_placeholder(name, e)
            self._last_render[name] = now
            # Continue with other renderers!

    def _render_error_placeholder(self, name: str, error: Exception) -> None:
        """
        Law 2: Write error placeholder instead of crashing.

        When a renderer fails, write a human-readable error message
        to the output file so the user knows what happened.
        """
        try:
            from datetime import datetime

            # Get output path from renderers (if available)
            renderer = self._renderers.get(name)
            if not renderer:
                return

            config = renderer.get_config()
            if not config:
                return

            output_path = Path(config.output)
            error_msg = str(error)[:200]  # Truncate long errors

            error_content = f"""<!--
UI ERROR: Renderer '{name}' failed
Error: {error_msg}
Time: {datetime.utcnow().isoformat()} UTC
-->

# {name.upper()}.md

**Rendering Error** - System still operational.

The `{name}` renderer encountered an error and could not generate content.

**Error Details:**

```
{str(error)[:500]}
```

This is a temporary placeholder. The system will retry on the next render cycle.
"""

            output_path.write_text(error_content)
            logger.warning(f"Error placeholder written to {output_path}")

        except Exception as e:
            logger.error(f"Failed to write error placeholder for '{name}': {e}")

    def _write_unified(self, renderer: BaseRenderer, content: str) -> None:
        """
        Write content through I/O service with UNIFIED header.

        This is the ONLY place where UI files get written.
        All renderers produce content, InterfacePlugin writes.
        """

        # Get output config
        output_file = renderer.output_file
        doc_type = renderer.doc_type
        writer_id = f"RENDERER_{renderer.name.upper()}"

        # Write through kernel I/O (header added by io_service)
        if self._kernel and hasattr(self._kernel, "io"):
            result = self._kernel.io.write_document(
                name=output_file,
                content=content,
                doc_type=doc_type,
                writer_id=writer_id,
                add_header=True,
            )
            if result.error:
                # logger.error(f"Failed to write {output_file}: {result.error}")
                # For debugging purpose, we raise
                raise RuntimeError(f"Failed to write {output_file}: {result.error}")
        else:
            # logger.warning(f"Cannot write {output_file}: kernel.io not available")
            raise RuntimeError(f"Cannot write {output_file}: kernel.io not available")

    def _is_test_mode(self) -> bool:
        """Check if running in pytest - skip file rendering in tests."""
        return bool(os.environ.get("PYTEST_CURRENT_TEST"))

    def _is_git_in_progress(self) -> bool:
        """
        Check if git is in the middle of a merge, cherry-pick, or rebase.

        During these operations, the kernel should NOT auto-generate files
        as it will cause merge conflicts and dirty working trees.

        Returns:
            True if git operation is in progress, False otherwise
        """
        git_dir = Path(".git")

        # Check for merge state
        if (git_dir / "MERGE_HEAD").exists():
            logger.warning("⚠️ Git merge in progress - skipping render to avoid conflicts")
            return True

        # Check for cherry-pick state
        if (git_dir / "CHERRY_PICK_HEAD").exists():
            logger.warning("⚠️ Git cherry-pick in progress - skipping render to avoid conflicts")
            return True

        # Check for rebase state
        if (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists():
            logger.warning("⚠️ Git rebase in progress - skipping render to avoid conflicts")
            return True

        return False

    def render_all(self) -> None:
        """Force render all views (ignores intervals).

        IMPORTANT: Skipped in test mode to prevent test kernels from
        overwriting real interface files (OPUS.md, ENVOY.md, etc.).

        CRITICAL: Also skipped during git operations (merge/cherry-pick/rebase)
        to prevent conflicts and dirty working trees.
        """
        if self._is_test_mode():
            logger.debug("InterfacePlugin: Skipping render in test mode")
            return

        if self._is_git_in_progress():
            logger.warning("InterfacePlugin: Skipping render during git operation")
            return

        for name, renderer in self._renderers.items():
            try:
                # Try unified approach first
                content = renderer.generate_content()
                if content is not None:
                    self._write_unified(renderer, content)
                else:
                    # Legacy fallback
                    renderer.render()
                self._last_render[name] = time.time()
            except Exception as e:
                logger.error(f"Error rendering view '{name}': {e}")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up."""
        logger.info("InterfacePlugin shutting down")

    def _load_renderers(self) -> None:
        """
        Load renderers using RendererLoader - VEDA-4 compliant.

        Supports:
        - Config Injection (Pratyaya)
        - Context Injection (for Containers)
        - Registry Metadata (GAD-000)
        """
        from vibe_core.plugins.interface.renderer_loader import RendererLoader

        logger.info("Loading renderers via RendererLoader...")

        # 1. Config Injection: Pass only the renderers config section
        renderer_config = {}
        if self._interface_config and hasattr(self._interface_config, "renderers"):
            # If Pydantic model, it behaves like dict access for renderers field potentially?
            # InterfaceConfig.renderers is a Dict[str, RendererConfig]
            # UnifiedLoader expects Dict[str, Any]
            # Convert configs to dicts
            for name, r_conf in self._interface_config.renderers.items():
                if hasattr(r_conf, "dict"):
                    renderer_config[name] = r_conf.dict()
                elif hasattr(r_conf, "model_dump"):
                    renderer_config[name] = r_conf.model_dump()
                else:
                    renderer_config[name] = r_conf

        # 2. Discovery
        renderers, metadata = RendererLoader.discover_and_load(config=renderer_config, kernel=self._kernel)

        self._renderers = {}
        self._renderer_metadata = {}  # NEW: Registry Pattern

        for name, renderer in renderers.items():
            meta = metadata.get(name)
            if meta and meta.loaded_successfully:
                self._renderers[name] = renderer
                self._renderer_metadata[name] = meta

                # 3. Context Injection (The "Relative Path" Trap)
                # Inject the root path so renderer knows where it lives (e.g. inside a zip)
                if hasattr(renderer, "set_root_path") and meta.entry_path:
                    # If entry_path is a file (e.g. .py), use its parent. If dir/container, use it directly.
                    # Fix: is_dir() can be flaky or context-dependent. Use suffix check.
                    root = meta.entry_path.parent if meta.entry_path.suffix == ".py" else meta.entry_path
                    logger.info(
                        f"DEBUG: Injecting root path for {name}: {root} (derived from source: {meta.entry_path})"
                    )
                    renderer.set_root_path(root)
                    logger.debug(f"  Context injected for {name}: {root}")

            else:
                logger.error(f"Renderer {name} failed: {meta.error if meta else 'unknown'}")

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

    # ==========================================================================
    # GAD-000 COMPLIANCE: MACHINE DISCOVERABILITY API
    # ==========================================================================

    def get_registered_documents(self) -> list:
        """
        GAD-000 Test 1: Machine-discoverable document registry.

        Returns list of all documents managed by renderers with their metadata.
        Allows AI agents to discover what documents exist and their properties.
        """
        documents = []
        for name, renderer in self._renderers.items():
            config = renderer.get_config()
            if not config:
                continue

            sections = []
            if config.sections:
                for section in config.sections:
                    sections.append(
                        {
                            "id": section.id,
                            "owner": section.owner,
                            "element_type": section.element_type,
                            "source": section.source,
                        }
                    )

            documents.append(
                {
                    "id": name,
                    "path": str(config.output),
                    "mode": config.mode if hasattr(config, "mode") else "unidirectional",
                    "interval": config.interval,
                    "enabled": config.enabled,
                    "sections": sections,
                    "renderer_type": type(renderer).__name__,
                }
            )

        return documents

    def get_ui_schema(self) -> dict:
        """
        GAD-000 Schema: Machine-discoverable UI system configuration.

        Returns the full UI schema including element types, layouts,
        ownership types, and all registered documents.
        """
        element_types = {}
        layouts = {}
        ownership_types = {}

        if self._interface_config:
            element_types = {
                name: {"settings": et.settings if hasattr(et, "settings") else {}}
                for name, et in (self._interface_config.element_types or {}).items()
            }
            layouts = {
                name: {"structure": str(layout)} for name, layout in (self._interface_config.layouts or {}).items()
            }
            ownership_types = {
                name: {
                    "marker_start": ot.marker_start if hasattr(ot, "marker_start") else "",
                    "marker_end": ot.marker_end if hasattr(ot, "marker_end") else "",
                }
                for name, ot in (self._interface_config.ownership_types or {}).items()
            }

        return {
            "element_types": element_types,
            "layouts": layouts,
            "ownership_types": ownership_types,
            "renderers": self.get_registered_documents(),
            "custom_renderers": list(self._interface_config.custom_renderers.keys()) if self._interface_config else [],
        }
