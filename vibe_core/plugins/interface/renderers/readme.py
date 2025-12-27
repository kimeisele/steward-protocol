"""
README Renderer.

Generates README.md from:
- pyproject.toml (project metadata)
- kernel.agent_registry (live agents)
- kernel.status (live status)

Zero Hardcoding: All data from existing sources.

UNIFIED UI: Implements generate_content() pattern.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

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

    @property
    def output_file(self) -> str:
        return "README.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def _load_project_data(self) -> None:
        """Load project metadata from pyproject.toml."""
        try:
            import tomlkit

            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                with open(pyproject_path) as f:
                    data = tomlkit.load(f)
                # Recursively convert tomlkit objects to plain Python types
                self._project_data = self._to_plain_dict(data.get("project", {}))
                logger.debug(f"Loaded project data: {self._project_data.get('name')}")
            else:
                logger.warning("pyproject.toml not found")
                self._project_data = {
                    "name": "steward-protocol",
                    "version": "0.0.0",
                    "description": "Unknown",
                }
        except ImportError:
            logger.warning("⚠️ tomlkit not installed - ReadmeRenderer running in fallback mode")
            self._project_data = {
                "name": "steward-protocol",
                "version": "0.0.0",
                "description": "Fallback (tomlkit missing)",
            }
        except Exception as e:
            logger.error(f"Failed to load pyproject.toml: {e}")
            self._project_data = {}

    def _to_plain_dict(self, obj: Any) -> Any:
        """Recursively convert tomlkit objects to plain Python types."""
        if isinstance(obj, dict):
            return {k: self._to_plain_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_plain_dict(item) for item in obj]
        else:
            # Convert tomlkit primitives (String, Integer, etc.) to Python types
            return obj.unwrap() if hasattr(obj, "unwrap") else obj

    def generate_content(self) -> Optional[str]:
        """Generate README.md content (UNIFIED UI pattern)."""
        if not self._template_loader.template_exists("readme.md.j2"):
            logger.warning("Template readme.md.j2 not found, skipping")
            return None

        try:
            context = {
                "project": self._project_data,
                "kernel_status": self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN",
                "agents": self.kernel.agent_registry,
                "system_agents": self._get_system_agents(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            return self._template_loader.render("readme.md.j2", **context)
        except Exception as e:
            logger.error(f"Failed to generate README content: {e}")
            return None

    def _get_system_agents(self) -> list:
        """Get list of system agents from registry."""
        system_agents = []
        for agent_id, agent in self.kernel.agent_registry.items():
            domain = getattr(agent, "domain", "")
            if domain in ("SYSTEM", "CORE", "GOVERNANCE"):
                system_agents.append(agent)
        return system_agents
