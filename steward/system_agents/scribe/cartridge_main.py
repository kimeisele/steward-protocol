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
from typing import Any, Dict, Optional

# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin
from vibe_core.config import CityConfig

# VibeOS Integration
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling.task import Task

# ALL TOOLS: Accessed via kernel (self.system.execute_tool)
# - scribe.agents_renderer - Generate AGENTS.md
# - scribe.citymap_renderer - Generate CITYMAP.md
# - scribe.help_renderer - Generate HELP.md
# - scribe.index_renderer - Generate INDEX.md
# - scribe.readme_renderer - Generate README.md


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
            capabilities=["documentation", "introspection", "publishing"],
        )

        logger.info("📚 SCRIBE Cartridge initializing (VibeAgent v1.0)...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.swear_oath_sync()
            logger.info("✅ SCRIBE has sworn the Constitutional Oath")

        # PHASE 2.3: Lazy-load root_dir after system interface injection
        # CRITICAL: Scribe writes to SANDBOX, not project root
        # Future: Kernel will provide publish() mechanism to copy sandbox → root
        self._root_dir = None

        # NO tool instances owned - agent is NAKED
        # Tools accessed via self.system.execute_tool()
        logger.info("✅ SCRIBE ready (NO tool instances owned)")
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
            dependencies=[],
        )

    # PHASE 2.3: Lazy-loading property for sandboxed filesystem access
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

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the kernel scheduler.

        Task format:
        {
            "action": "generate_all" | "generate_agents" | "generate_citymap" | "generate_help" | "generate_readme",
        }
        """
        action = task.input.get("action") if hasattr(task, "input") else task.payload.get("action")
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
                result = {"success": False, "error": f"Unknown action: {action}"}

            return result

        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}")
            return {"success": False, "error": str(e)}

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
            "AGENTS.md": "scribe.agents_renderer",
            "CITYMAP.md": "scribe.citymap_renderer",
            "HELP.md": "scribe.help_renderer",
            "README.md": "scribe.readme_renderer",
            "INDEX.md": "scribe.index_renderer",
        }

        for doc_name, tool_name in docs.items():
            try:
                # Generate content via kernel routing
                result = self.system.execute_tool(tool_name, {"action": "generate"})
                if not result.success:
                    logger.error(f"   ❌ Failed to render {doc_name}: {result.error}")
                    rendered[doc_name] = False
                    published[doc_name] = False
                    continue

                content = result.output

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
            "message": ("All documentation generated and published" if all_success else "Some steps failed"),
            "rendered": rendered,
            "published": published,
        }

    def _generate_agents(self) -> Dict[str, Any]:
        """Generate AGENTS.md only (with sandbox+publish)."""
        return self._generate_single_doc("AGENTS.md", "scribe.agents_renderer")

    def _generate_citymap(self) -> Dict[str, Any]:
        """Generate CITYMAP.md only (with sandbox+publish)."""
        return self._generate_single_doc("CITYMAP.md", "scribe.citymap_renderer")

    def _generate_help(self) -> Dict[str, Any]:
        """Generate HELP.md only (with sandbox+publish)."""
        return self._generate_single_doc("HELP.md", "scribe.help_renderer")

    def _generate_readme(self) -> Dict[str, Any]:
        """Generate README.md only (with sandbox+publish)."""
        return self._generate_single_doc("README.md", "scribe.readme_renderer")

    def _generate_single_doc(self, doc_name: str, tool_name: str) -> Dict[str, Any]:
        """Helper: Generate single doc with 2-step render+publish.

        Args:
            doc_name: Filename (e.g., "README.md")
            tool_name: Tool name to execute via kernel (e.g., "scribe.readme_renderer")

        Returns:
            Result dict with success status
        """
        logger.info(f"🔄 Generating {doc_name}...")

        try:
            # Step 1: Render to sandbox via kernel routing
            result = self.system.execute_tool(tool_name, {"action": "generate"})
            if not result.success:
                raise RuntimeError(result.error)

            content = result.output

            sandbox_file = self.sandbox_dir / doc_name
            sandbox_file.write_text(content)
            logger.info(f"   ✅ Rendered {doc_name} to sandbox ({len(content)} bytes)")

            # Step 2: Publish to root
            self.system.publish_artifact(f"docs/{doc_name}", doc_name)
            logger.info(f"   📤 Published {doc_name} to project root")

            return {
                "success": True,
                "message": f"{doc_name} generated and published",
                "bytes": len(content),
            }

        except Exception as e:
            logger.error(f"   ❌ Failed to generate {doc_name}: {e}")
            return {
                "success": False,
                "message": f"Failed to generate {doc_name}",
                "error": str(e),
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

    def report_status(self) -> Dict[str, Any]:
        """Report SCRIBE status for observability (Article IV compliance)."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "OPERATIONAL",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "sandbox_initialized": self._root_dir is not None,
            "oath_sworn": getattr(self, "oath_sworn", False),
            "description": "Documentation agent - auto-generates system documentation",
        }


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
