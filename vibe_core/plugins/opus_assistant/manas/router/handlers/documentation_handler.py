"""Documentation Handler - documentation intent processing."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict

from vibe_core.source_authority_registry import load_source_authority_registry
from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Documentation")


@register_handler
class DocumentationHandler(BaseHandler):
    """Handle documentation-related intents."""

    name = "documentation"
    intent_types = ["update_readme", "update_opus_documentation", "document_manas", "fix_documentation_drift"]
    agent_type = AgentType.DOCUMENTATION
    priority = 10

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        from vibe_core.loaders import get_cortex

        logger.info("📜 documentation handling: %s", intent.title)
        try:
            documentation = get_cortex("documentation", workspace=self._workspace)
            if documentation is not None:
                if self._kernel:
                    documentation.inject_kernel(self._kernel)
                return documentation.execute(intent)
            logger.warning("⚠️ DocumentationCortexAdapter not available, using legacy fallback")
            return self._handle_legacy(intent)
        except Exception as exc:
            logger.error("documentation handler error: %s", exc)
            return {"success": False, "handler": self.name, "error": str(exc)}

    def _handle_legacy(self, intent: "Intent") -> Dict[str, Any]:
        from vibe_core.plugins.opus_assistant.manas.cortex.documentation_surface import DocumentationSurfaceBuilder

        sync_keywords = {"sync", "push", "update wiki", "publish"}
        registry = load_source_authority_registry(workspace=self._workspace)
        if any(kw in intent.title.lower() for kw in sync_keywords):
            return {
                "success": False,
                "handler": self.name,
                "action": "public_wiki_removed",
                "document_count": len(registry.documents),
                "message": "📜 Local wiki publication was removed. Export authority artifacts here and publish the public membrane via agent-internet.",
            }
        context = DocumentationSurfaceBuilder(workspace=self._workspace).gather_context()
        return {
            "success": True,
            "handler": self.name,
            "action": "documentation_surface_status",
            "agents_found": len(context.agents),
            "modules_found": len(context.modules),
            "document_count": len(registry.documents),
            "message": f"📜 Documentation surface gathered context for {len(registry.documents)} source documents, {len(context.agents)} agents, and {len(context.modules)} modules.",
        }
