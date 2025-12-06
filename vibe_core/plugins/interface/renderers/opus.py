"""
OPUS Renderer - Fractal Dashboard with Hot-Swappable Panels.

VEDA-4 Pattern: Panels are auto-discovered from panels/ directory.
Each panel is independent and can be added/removed without code changes.

UNIFIED UI ARCHITECTURE:
    - OpusRenderer is a SLAVE to InterfacePlugin (the KING)
    - OpusRenderer implements generate_content() → returns string
    - InterfacePlugin writes OPUS.md with UNIFIED header
    - OpusRenderer does NOT call kernel.io directly

Architecture:
    OpusRenderer (this file)
        └── Panels (auto-discovered)
            ├── VisnuPanel (kernel LOC tracking)
            ├── CandidatesPanel (extraction analysis)
            ├── BlockersPanel (bidirectional)
            ├── NextActionsPanel (bidirectional)
            ├── ActivityPanel (git commits)
            └── CommandsPanel (quick commands)
            └── ... (add more by creating .py files!)

To add a new panel:
    1. Create panels/my_panel.py
    2. Extend OpusPanel
    3. Done - auto-discovered on next render!
"""

import importlib
import logging
import pkgutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

import yaml

from vibe_core.io_service import DocumentType

from .base import BaseRenderer
from .panels.base_panel import OpusPanel

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_OPUS")


class OpusRenderer(BaseRenderer):
    """
    OPUS - Fractal Dashboard Renderer.

    Uses VEDA-4 pattern for panel auto-discovery.
    All config from config/opus.yaml.
    """

    CONFIG_PATH = Path("config/opus.yaml")

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self.config = self._load_config()
        self.output_path = Path("OPUS.md")
        self._panels: Dict[str, OpusPanel] = {}
        self._load_panels()

    @property
    def name(self) -> str:
        return "opus"

    @property
    def output_file(self) -> str:
        """Output filename for InterfacePlugin."""
        return "OPUS.md"

    @property
    def doc_type(self) -> DocumentType:
        """OPUS is bidirectional (user can edit blockers/actions)."""
        return DocumentType.BIDIRECTIONAL

    def _load_config(self) -> Dict[str, Any]:
        """Load config from config/opus.yaml."""
        try:
            if self.CONFIG_PATH.exists():
                return yaml.safe_load(self.CONFIG_PATH.read_text()) or {}
        except Exception as e:
            logger.warning(f"Could not load OPUS config: {e}")
        return {}

    def _load_panels(self) -> None:
        """
        VEDA-4: Auto-discover and load panels.

        Same pattern as InterfacePlugin loading renderers.
        """
        panels_pkg = "vibe_core.plugins.interface.renderers.panels"
        panels_path = Path(__file__).parent / "panels"

        if not panels_path.exists():
            logger.warning(f"Panels directory not found: {panels_path}")
            return

        # SHABDA: Discover panel modules
        for importer, module_name, ispkg in pkgutil.iter_modules([str(panels_path)]):
            if module_name in ("base_panel", "__init__"):
                continue

            try:
                # ARTHA: Import module
                module = importlib.import_module(f"{panels_pkg}.{module_name}")

                # PRATYAYA: Find OpusPanel subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, OpusPanel) and attr is not OpusPanel:
                        # KARMA: Instantiate panel
                        panel = attr()

                        # Check if enabled
                        if panel.is_enabled(self.config):
                            self._panels[panel.panel_id] = panel
                            logger.debug(f"Loaded OPUS panel: {panel.panel_id}")
                        else:
                            logger.debug(f"Skipped disabled panel: {panel.panel_id}")

            except Exception as e:
                logger.error(f"Failed to load panel '{module_name}': {e}")

        logger.info(f"OPUS loaded {len(self._panels)} panels")

    def generate_content(self) -> Optional[str]:
        """
        Generate OPUS.md content (UNIFIED UI pattern).

        Returns:
            Markdown content WITHOUT header (InterfacePlugin adds it)
            None if rendering fails
        """
        try:
            return self._compose_panels()
        except Exception as e:
            logger.error(f"Error generating OPUS content: {e}")
            return None

    def render(self) -> None:
        """
        Legacy render method - DEPRECATED.

        InterfacePlugin now calls generate_content() and writes itself.
        This is kept for backwards compatibility only.
        """
        # Legacy path - direct write (shouldn't be called anymore)
        content = self.generate_content()
        if content and self.kernel:
            self.kernel.io.write_document(
                name="OPUS.md",
                content=content,
                doc_type=DocumentType.BIDIRECTIONAL,
                writer_id="opus_renderer",
                add_header=True,
            )

    def _compose_panels(self) -> str:
        """Generate content by composing panels in priority order."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Header
        header = """# OPUS - AI Meister-Kasten

> **Fractal Dashboard with Hot-Swappable Panels**
> Config: `config/opus.yaml` | Panels: auto-discovered | VEDA-4

---
"""

        # Create shared context for panels
        context: Dict[str, Any] = {
            "existing_opus_content": self._read_existing(),
        }

        # Render panels in priority order
        sorted_panels = sorted(self._panels.items(), key=lambda x: x[1].priority)

        panel_contents = []
        for panel_id, panel in sorted_panels:
            try:
                panel_content = panel.render(self.config, context)
                if panel_content:  # Skip empty panels
                    panel_contents.append(panel_content)
            except Exception as e:
                logger.error(f"Error rendering panel {panel_id}: {e}")
                panel_contents.append(f"<!-- Panel {panel_id} failed: {e} -->\n")

        # Footer
        panel_list = ", ".join(p.panel_id for p in sorted(self._panels.values(), key=lambda x: x.priority))
        footer = f"""
*Rendered by OpusRenderer | {timestamp}*
*Active panels: {panel_list}*
"""

        return header + "\n".join(panel_contents) + footer

    def _read_existing(self) -> str:
        """Read existing OPUS.md for bidirectional preservation."""
        try:
            if self.output_path.exists():
                return self.output_path.read_text()
        except Exception:
            pass
        return ""

    def reload_panels(self) -> None:
        """Hot-reload panels (useful for development)."""
        self._panels.clear()
        self._load_panels()
        logger.info("OPUS panels reloaded")

    def list_panels(self) -> Dict[str, Dict[str, Any]]:
        """List all loaded panels with metadata."""
        return {
            panel_id: {
                "priority": panel.priority,
                "enabled": panel.is_enabled(self.config),
                "section_id": panel.section_id,
            }
            for panel_id, panel in self._panels.items()
        }
