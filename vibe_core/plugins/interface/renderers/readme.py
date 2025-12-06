"""
README Renderer.

Generates README.md from:
- pyproject.toml (project metadata)
- kernel.agent_registry (live agents)
- kernel.status (live status)

Zero Hardcoding: All data from existing sources.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from vibe_core.io_service import DocumentType
from vibe_core.loaders import TemplateLoader

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_README")


class ReadmeRenderer(BaseRenderer):
    """
    Generates README.md from pyproject.toml + kernel state.

    Template: knowledge/interface/templates/readme.md.j2
    """

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self._template_loader = TemplateLoader()
        self._project_data: Dict[str, Any] = {}
        self._load_project_data()

    @property
    def name(self) -> str:
        return "readme"

    def _load_project_data(self) -> None:
        """Load project metadata from pyproject.toml."""
        try:
            import tomlkit

            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                with open(pyproject_path) as f:
                    data = tomlkit.load(f)
                self._project_data = dict(data.get("project", {}))
                logger.debug(f"Loaded project data: {self._project_data.get('name')}")
            else:
                logger.warning("pyproject.toml not found")
                self._project_data = {
                    "name": "steward-protocol",
                    "version": "0.0.0",
                    "description": "Unknown",
                }
        except Exception as e:
            logger.error(f"Failed to load pyproject.toml: {e}")
            self._project_data = {}

    def render(self) -> None:
        """Render README.md from template + live data."""
        if not self._template_loader.template_exists("readme.md.j2"):
            logger.warning("Template readme.md.j2 not found, skipping")
            return

        try:
            # Gather context from existing sources
            context = {
                "project": self._project_data,
                "kernel_status": self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN",
                "agents": self.kernel.agent_registry,
                "system_agents": self._get_system_agents(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

            # Render template
            content = self._template_loader.render("readme.md.j2", **context)

            # Write via kernel I/O
            self.kernel.io.write_document(
                name="README.md",
                content=content,
                doc_type=DocumentType.READONLY,
                writer_id="RENDERER_README",
            )

            logger.debug("README.md rendered successfully")

        except Exception as e:
            logger.error(f"Failed to render README.md: {e}")

    def _get_system_agents(self) -> list:
        """Get list of system agents from registry."""
        system_agents = []
        for agent_id, agent in self.kernel.agent_registry.items():
            domain = getattr(agent, "domain", "")
            if domain in ("SYSTEM", "CORE", "GOVERNANCE"):
                system_agents.append(agent)
        return system_agents
