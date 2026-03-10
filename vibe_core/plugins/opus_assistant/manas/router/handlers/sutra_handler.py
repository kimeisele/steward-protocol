"""
Sutra Handler - Documentation intent processing.

OPUS-171 Phase 5: First extracted handler from IntentRouter.

Handles:
- update_readme
- update_opus_documentation
- document_manas
- fix_documentation_drift
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xa0848457"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Dict

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Sutra")


@register_handler
class SutraHandler(BaseHandler):
    """
    Handle documentation-related intents.

    Agent-First: This handler belongs to the DOCUMENTATION domain.
    Future routing: Intent → DocAgent → SutraHandler
    """

    # === REQUIRED CLASS ATTRIBUTES ===
    name = "sutra"
    intent_types = [
        "update_readme",
        "update_opus_documentation",
        "document_manas",
        "fix_documentation_drift",
    ]

    # === AGENT-FIRST ROUTING ===
    agent_type = AgentType.DOCUMENTATION
    priority = 10  # High priority for doc intents

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """
        Route to SUTRA for documentation tasks via CortexLoader (VEDA-4).

        OPUS-171 Phase 5.3: Uses CortexLoader for VEDA-4 pattern.
        """
        from vibe_core.loaders import get_cortex

        logger.info(f"📜 SUTRA handling: {intent.title}")

        try:
            # VEDA-4: Get SutraCortex via CortexLoader
            sutra = get_cortex("sutra", workspace=self._workspace)

            if sutra is not None:
                # Inject kernel if available
                if self._kernel:
                    sutra.inject_kernel(self._kernel)

                # Delegate to CortexAdapter.execute()
                return sutra.execute(intent)

            # Fallback to legacy implementation if CortexLoader unavailable
            logger.warning("⚠️ SutraCortexAdapter not available, using legacy import")
            return self._handle_legacy(intent)

        except Exception as e:
            logger.error(f"SUTRA error: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _handle_legacy(self, intent: "Intent") -> Dict[str, Any]:
        """Legacy SUTRA handling (fallback if CortexLoader unavailable)."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator, SutraWeaver

        sync_keywords = {"sync", "push", "update wiki", "publish"}
        is_sync_request = any(kw in intent.title.lower() for kw in sync_keywords)
        orchestrator = SutraOrchestrator(workspace=self._workspace)
        registry = orchestrator.export_source_surface_registry()

        if is_sync_request:
            return {
                "success": False,
                "handler": self.name,
                "action": "public_wiki_removed",
                "document_count": registry["document_count"],
                "message": "📜 SUTRA no longer publishes a local wiki. Export authority artifacts here and publish the public membrane via agent-internet.",
            }

        weaver = SutraWeaver(workspace=self._workspace)
        ctx = weaver.gather_context()

        return {
            "success": True,
            "handler": self.name,
            "action": "source_authority_status",
            "agents_found": len(ctx.agents),
            "modules_found": len(ctx.modules),
            "document_count": registry["document_count"],
            "message": f"📜 SUTRA gathered source-authority context for {registry['document_count']} documents, {len(ctx.agents)} agents, and {len(ctx.modules)} modules.",
        }
