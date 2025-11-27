#!/usr/bin/env python3
"""
SCRIBE Cartridge - The Documentarian (Documentation Agent)

SCRIBE is the "Librarian" of Agent City. It:
1. Auto-generates all documentation (AGENTS.md, CITYMAP.md, HELP.md, README.md)
2. Keeps documentation synchronized with actual code (3-layer architecture in CITYMAP.md)
3. Runs periodically or on-demand to ensure freshness
4. Uses unified Jinja2 templates for consistency

This is a VibeAgent that:
- Inherits from vibe_core.VibeAgent
- Receives tasks from the kernel scheduler
- Generates documentation autonomously
- Validates that all docs are current and consistent

Key Insight:
"Documentation that writes itself is documentation that never lies.
SCRIBE ensures your codebase documents itself."
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# VibeOS Integration
try:
    from vibe_core import VibeAgent, Task, AgentManifest
except ImportError:
    # Fallback for testing without vibe_core
    class VibeAgent:
        def __init__(self, agent_id, name, version, author, description, domain, capabilities):
            self.agent_id = agent_id
            self.name = name
            self.version = version
            self.author = author
            self.description = description
            self.domain = domain
            self.capabilities = capabilities

    class Task:
        def __init__(self, task_id="test", input=None):
            self.task_id = task_id
            self.input = input or {}

    class AgentManifest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

# Import documentation tools
from .tools.agents_renderer import AgentsRenderer
from .tools.citymap_renderer import CitymapRenderer
from .tools.help_renderer import HelpRenderer
from .tools.readme_renderer import ReadmeRenderer

# Constitutional Oath (optional)
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SCRIBE_CARTRIDGE")


class ScribeCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    The SCRIBE Agent Cartridge (The Documentarian).

    Autonomously generates and maintains all system documentation.

    Key Responsibilities:
    - Auto-generate AGENTS.md from cartridge metadata
    - Auto-generate CITYMAP.md from system architecture
    - Auto-generate HELP.md from system introspection
    - Auto-generate README.md from system configuration
    - Keep all documentation synchronized with code
    - Run on schedule or on-demand via CI/CD

    Philosophy:
    "A system that documents itself is a system that evolves with truth.
    No stale documentation, only live introspection."
    """

    def __init__(self, root_dir: str = "."):
        """Initialize SCRIBE (The Documentarian) as a VibeAgent."""
        # Initialize VibeAgent base class
        super().__init__(
            agent_id="scribe",
            name="SCRIBE",
            version="1.0.0",
            author="Steward Protocol",
            description="Documentation agent: auto-generates AGENTS.md, CITYMAP.md (3-layer), HELP.md, README.md",
            domain="INFRASTRUCTURE",
            capabilities=[
                "documentation",
                "introspection",
                "publishing"
            ]
        )

        logger.info("📚 SCRIBE Cartridge initializing (VibeAgent v1.0)...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ SCRIBE has sworn the Constitutional Oath")

        # Set root directory
        self.root_dir = Path(root_dir)

        # Initialize all documentation renderers
        self.agents_renderer = AgentsRenderer(root_dir)
        self.citymap_renderer = CitymapRenderer(root_dir)
        self.help_renderer = HelpRenderer(root_dir)
        self.readme_renderer = ReadmeRenderer(root_dir)

        logger.info("✅ All documentation renderers initialized")
        logger.info("📚 SCRIBE: Ready for operation (awaiting kernel injection)")

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest (VibeAgent interface)."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
            dependencies=[]
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the kernel scheduler.

        Task format:
        {
            "action": "generate_all" | "generate_agents" | "generate_citymap" | "generate_help" | "generate_readme",
        }
        """
        action = task.input.get("action") if hasattr(task, 'input') else task.payload.get("action")
        logger.info(f"📚 SCRIBE processing: {action}")

        try:
            if action == "generate_all":
                result = self._generate_all()
            elif action == "generate_agents":
                result = self._generate_agents()
            elif action == "generate_citymap":
                result = self._generate_citymap()
            elif action == "generate_help":
                result = self._generate_help()
            elif action == "generate_readme":
                result = self._generate_readme()
            else:
                result = {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }

            return result

        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_all(self) -> Dict[str, Any]:
        """Generate all documentation files."""
        logger.info("🔄 Generating ALL documentation...")

        results = {
            "agents": self.agents_renderer.render_to_file(),
            "citymap": self.citymap_renderer.render_to_file(),
            "help": self.help_renderer.render_to_file(),
            "readme": self.readme_renderer.render_to_file(),
        }

        success = all(results.values())

        return {
            "success": success,
            "message": "All documentation generated" if success else "Some generation failed",
            "details": results
        }

    def _generate_agents(self) -> Dict[str, Any]:
        """Generate AGENTS.md only."""
        logger.info("🔄 Generating AGENTS.md...")

        success = self.agents_renderer.render_to_file()

        return {
            "success": success,
            "message": "AGENTS.md generated" if success else "Failed to generate AGENTS.md"
        }

    def _generate_citymap(self) -> Dict[str, Any]:
        """Generate CITYMAP.md only."""
        logger.info("🔄 Generating CITYMAP.md...")

        success = self.citymap_renderer.render_to_file()

        return {
            "success": success,
            "message": "CITYMAP.md generated" if success else "Failed to generate CITYMAP.md"
        }

    def _generate_help(self) -> Dict[str, Any]:
        """Generate HELP.md only."""
        logger.info("🔄 Generating HELP.md...")

        success = self.help_renderer.render_to_file()

        return {
            "success": success,
            "message": "HELP.md generated" if success else "Failed to generate HELP.md"
        }

    def _generate_readme(self) -> Dict[str, Any]:
        """Generate README.md only."""
        logger.info("🔄 Generating README.md...")

        success = self.readme_renderer.render_to_file()

        return {
            "success": success,
            "message": "README.md generated" if success else "Failed to generate README.md"
        }

    # Utility method for direct invocation (outside kernel)
    def generate_all(self) -> bool:
        """Direct method to generate all documentation (for standalone use)."""
        logger.info("🔄 SCRIBE: Generating all documentation...")

        try:
            self.agents_renderer.render_to_file()
            self.citymap_renderer.render_to_file()
            self.help_renderer.render_to_file()
            self.readme_renderer.render_to_file()

            logger.info("✅ SCRIBE: All documentation generated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ SCRIBE: Generation failed: {e}")
            return False


def main():
    """Main entry point for standalone usage."""
    import sys
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    scribe = ScribeCartridge(root_dir)
    scribe.generate_all()


if __name__ == "__main__":
    main()
