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
from vibe_core.protocols import VibeAgent, AgentManifest
from vibe_core.config import CityConfig
from vibe_core.scheduling.task import Task

# Import documentation tools

# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin
from .tools.agents_renderer import AgentsRenderer
from .tools.citymap_renderer import CitymapRenderer
from .tools.help_renderer import HelpRenderer
from .tools.readme_renderer import ReadmeRenderer

# Constitutional Oath (optional)
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SCRIBE_CARTRIDGE")


class ScribeCartridge(VibeAgent, OathMixin):
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

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize SCRIBE (The Documentarian) as a VibeAgent.

        Args:
            config: CityConfig instance from Phoenix Config (optional)
        """
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

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

        # PHASE 2.3: Lazy-load root_dir after system interface injection
        # CRITICAL: Scribe writes to SANDBOX, not project root
        # Future: Kernel will provide publish() mechanism to copy sandbox → root
        self._root_dir = None
        self._agents_renderer = None
        self._citymap_renderer = None
        self._help_renderer = None
        self._readme_renderer = None

        logger.info("✅ SCRIBE renderers pending initialization")
        logger.info("📚 SCRIBE: Ready for operation (awaiting system injection)")

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

    # PHASE 2.3: Lazy-loading properties for sandboxed filesystem access
    @property
    def root_dir(self):
        """Lazy-load root_dir after system interface injection.

        CRITICAL: Scribe writes to SANDBOX (/tmp/vibe_os/agents/scribe/docs/),
        NOT to project root. This prevents unauthorized writes to README.md, etc.

        Future: Kernel will provide publish() mechanism to copy sandbox → root.
        """
        if self._root_dir is None:
            self._root_dir = self.system.get_sandbox_path() / "docs"
            self._root_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 SCRIBE root_dir initialized (sandboxed): {self._root_dir}")
            logger.warning("⚠️  SCRIBE writes to SANDBOX. Use kernel.publish() to copy to project root (future feature)")
        return self._root_dir

    @property
    def agents_renderer(self):
        """Lazy-load AgentsRenderer."""
        if self._agents_renderer is None:
            self._agents_renderer = AgentsRenderer(str(self.root_dir))
            logger.debug("📋 AgentsRenderer initialized")
        return self._agents_renderer

    @property
    def citymap_renderer(self):
        """Lazy-load CitymapRenderer."""
        if self._citymap_renderer is None:
            self._citymap_renderer = CitymapRenderer(str(self.root_dir))
            logger.debug("🗺️  CitymapRenderer initialized")
        return self._citymap_renderer

    @property
    def help_renderer(self):
        """Lazy-load HelpRenderer."""
        if self._help_renderer is None:
            self._help_renderer = HelpRenderer(str(self.root_dir))
            logger.debug("❓ HelpRenderer initialized")
        return self._help_renderer

    @property
    def readme_renderer(self):
        """Lazy-load ReadmeRenderer."""
        if self._readme_renderer is None:
            self._readme_renderer = ReadmeRenderer(str(self.root_dir))
            logger.debug("📖 ReadmeRenderer initialized")
        return self._readme_renderer

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
    """Main entry point for standalone usage.

    WARNING: Standalone mode is deprecated. SCRIBE now requires kernel registration
    for system interface injection (sandboxed filesystem access).

    Use via kernel:
        kernel.register_agent(ScribeCartridge())
        kernel.dispatch_task("scribe", {"action": "generate_all"})
    """
    logger.error("❌ SCRIBE standalone mode is deprecated after Phase 2.3 migration")
    logger.error("   SCRIBE requires kernel registration for sandboxed filesystem access")
    logger.error("   Use: kernel.register_agent(ScribeCartridge())")
    import sys
    sys.exit(1)


if __name__ == "__main__":
    main()
