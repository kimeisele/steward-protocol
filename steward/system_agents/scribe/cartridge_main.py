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
from .tools.index_renderer import IndexRenderer

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
        self._index_renderer = None

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
    def sandbox_dir(self):
        """Lazy-load sandbox directory for output files.

        CRITICAL: Scribe writes to SANDBOX (/tmp/vibe_os/agents/scribe/docs/),
        NOT to project root. This prevents unauthorized writes to README.md, etc.

        After rendering to sandbox, use system.publish_artifact() to copy to root.
        """
        if self._root_dir is None:
            self._root_dir = self.system.get_sandbox_path() / "docs"
            self._root_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 SCRIBE sandbox initialized: {self._root_dir}")
        return self._root_dir

    @property
    def agents_renderer(self):
        """Lazy-load AgentsRenderer.

        CRITICAL: Pass PROJECT ROOT (not sandbox) for source code introspection.
        Scribe needs to READ real source, but WRITE to sandbox.
        """
        if self._agents_renderer is None:
            # Use "." (project root) for introspection, NOT sandbox
            self._agents_renderer = AgentsRenderer(root_dir=".")
            logger.debug("📋 AgentsRenderer initialized (source: project root)")
        return self._agents_renderer

    @property
    def citymap_renderer(self):
        """Lazy-load CitymapRenderer.

        CRITICAL: Pass PROJECT ROOT for architecture introspection.
        """
        if self._citymap_renderer is None:
            self._citymap_renderer = CitymapRenderer(root_dir=".")
            logger.debug("🗺️  CitymapRenderer initialized (source: project root)")
        return self._citymap_renderer

    @property
    def help_renderer(self):
        """Lazy-load HelpRenderer.

        CRITICAL: Pass PROJECT ROOT for codebase introspection.
        """
        if self._help_renderer is None:
            self._help_renderer = HelpRenderer(root_dir=".")
            logger.debug("❓ HelpRenderer initialized (source: project root)")
        return self._help_renderer

    @property
    def readme_renderer(self):
        """Lazy-load ReadmeRenderer.

        CRITICAL: Pass PROJECT ROOT for project introspection.
        """
        if self._readme_renderer is None:
            self._readme_renderer = ReadmeRenderer(root_dir=".")
            logger.debug("📖 ReadmeRenderer initialized (source: project root)")
        return self._readme_renderer

    @property
    def index_renderer(self):
        """Lazy-load IndexRenderer.

        CRITICAL: Pass PROJECT ROOT for filesystem introspection.
        """
        if self._index_renderer is None:
            self._index_renderer = IndexRenderer(root_dir=".")
            logger.debug("📑 IndexRenderer initialized (source: project root)")
        return self._index_renderer

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
        """Generate all documentation files.

        PHASE 2.5: Two-step process:
        1. Render to sandbox (safe writes)
        2. Publish to project root (controlled via whitelist)
        """
        logger.info("🔄 Generating ALL documentation...")

        # Step 1: Render all docs to sandbox
        rendered = {}
        published = {}

        docs = {
            "AGENTS.md": self.agents_renderer,
            "CITYMAP.md": self.citymap_renderer,
            "HELP.md": self.help_renderer,
            "README.md": self.readme_renderer,
            "INDEX.md": self.index_renderer,
        }

        for doc_name, renderer in docs.items():
            try:
                # Generate content via introspection
                # Try scan_and_render() first, fall back to render()
                if hasattr(renderer, 'scan_and_render'):
                    content = renderer.scan_and_render()
                elif hasattr(renderer, 'render'):
                    content = renderer.render()
                else:
                    raise AttributeError(f"Renderer for {doc_name} has no render method")

                # Write to sandbox
                sandbox_file = self.sandbox_dir / doc_name
                sandbox_file.write_text(content)
                rendered[doc_name] = True
                logger.info(f"   ✅ Rendered {doc_name} to sandbox ({len(content)} bytes)")

            except Exception as e:
                logger.error(f"   ❌ Failed to render {doc_name}: {e}")
                rendered[doc_name] = False
                published[doc_name] = False
                continue

            # Step 2: Publish to project root
            try:
                self.system.publish_artifact(f"docs/{doc_name}", doc_name)
                published[doc_name] = True
                logger.info(f"   📤 Published {doc_name} to project root")

            except Exception as e:
                logger.error(f"   ❌ Failed to publish {doc_name}: {e}")
                published[doc_name] = False

        all_success = all(rendered.values()) and all(published.values())

        return {
            "success": all_success,
            "message": "All documentation generated and published" if all_success else "Some steps failed",
            "rendered": rendered,
            "published": published
        }

    def _generate_agents(self) -> Dict[str, Any]:
        """Generate AGENTS.md only (with sandbox+publish)."""
        return self._generate_single_doc("AGENTS.md", self.agents_renderer)

    def _generate_citymap(self) -> Dict[str, Any]:
        """Generate CITYMAP.md only (with sandbox+publish)."""
        return self._generate_single_doc("CITYMAP.md", self.citymap_renderer)

    def _generate_help(self) -> Dict[str, Any]:
        """Generate HELP.md only (with sandbox+publish)."""
        return self._generate_single_doc("HELP.md", self.help_renderer)

    def _generate_readme(self) -> Dict[str, Any]:
        """Generate README.md only (with sandbox+publish)."""
        return self._generate_single_doc("README.md", self.readme_renderer)

    def _generate_single_doc(self, doc_name: str, renderer) -> Dict[str, Any]:
        """Helper: Generate single doc with 2-step render+publish.

        Args:
            doc_name: Filename (e.g., "README.md")
            renderer: Renderer instance with scan_and_render() or render() method

        Returns:
            Result dict with success status
        """
        logger.info(f"🔄 Generating {doc_name}...")

        try:
            # Step 1: Render to sandbox
            # Try scan_and_render() first, fall back to render()
            if hasattr(renderer, 'scan_and_render'):
                content = renderer.scan_and_render()
            elif hasattr(renderer, 'render'):
                content = renderer.render()
            else:
                raise AttributeError(f"Renderer has no scan_and_render() or render() method")

            sandbox_file = self.sandbox_dir / doc_name
            sandbox_file.write_text(content)
            logger.info(f"   ✅ Rendered {doc_name} to sandbox ({len(content)} bytes)")

            # Step 2: Publish to root
            self.system.publish_artifact(f"docs/{doc_name}", doc_name)
            logger.info(f"   📤 Published {doc_name} to project root")

            return {
                "success": True,
                "message": f"{doc_name} generated and published",
                "bytes": len(content)
            }

        except Exception as e:
            logger.error(f"   ❌ Failed to generate {doc_name}: {e}")
            return {
                "success": False,
                "message": f"Failed to generate {doc_name}",
                "error": str(e)
            }

    # Utility method for direct invocation (outside kernel)
    def generate_all(self) -> bool:
        """Direct method to generate all documentation.

        DEPRECATED after Phase 2.3: Requires kernel registration for system interface.
        This method is kept for backwards compatibility but will fail without kernel.
        """
        logger.warning("⚠️  generate_all() is deprecated. Use kernel.dispatch_task() instead.")

        try:
            result = self._generate_all()
            return result["success"]
        except Exception as e:
            logger.error(f"❌ SCRIBE: Generation failed: {e}")
            logger.error("   Hint: SCRIBE requires kernel registration after Phase 2.3")
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
