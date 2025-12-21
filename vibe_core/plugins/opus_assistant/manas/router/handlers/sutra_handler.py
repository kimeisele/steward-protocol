"""
Sutra Handler - Documentation intent processing.

OPUS-171 Phase 5: First extracted handler from IntentRouter.

OPUS-071: Supports full wiki sync with GITHUB_TOKEN.

Handles:
- update_readme
- update_opus_documentation
- document_manas
- fix_documentation_drift
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Sutra")


@register_handler
class SutraHandler(BaseHandler):
    """
    Handle documentation-related intents.

    OPUS-071: Supports full wiki sync with GITHUB_TOKEN.

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
        Route to SUTRA for documentation tasks.

        OPUS-071: Now supports full wiki sync with GITHUB_TOKEN!
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import (
            SutraOrchestrator,
            SutraWeaver,
            WikiSync,
        )

        logger.info(f"📜 SUTRA handling: {intent.title}")

        try:
            # Check if this is a sync request
            sync_keywords = {"sync", "push", "update wiki", "publish"}
            is_sync_request = any(kw in intent.title.lower() for kw in sync_keywords)

            # Check for credentials
            wiki_sync = WikiSync(workspace=self._workspace)
            has_creds = wiki_sync.has_credentials()

            if is_sync_request and has_creds:
                # OPUS-071: Full wiki sync!
                logger.info("📜 SUTRA: Executing full wiki sync...")
                orchestrator = SutraOrchestrator(workspace=self._workspace)
                result = orchestrator.generate_and_sync()

                if result.success:
                    return {
                        "success": True,
                        "handler": self.name,
                        "action": "wiki_synced",
                        "pages_synced": result.pages_synced,
                        "wiki_url": result.wiki_url,
                        "message": f"📜 SUTRA synced {len(result.pages_synced)} pages to GitHub Wiki!",
                    }
                else:
                    return {
                        "success": False,
                        "handler": self.name,
                        "action": "sync_failed",
                        "errors": result.errors,
                        "message": f"SUTRA sync failed: {', '.join(result.errors)}",
                    }

            elif is_sync_request and not has_creds:
                # Want to sync but no credentials
                return {
                    "success": False,
                    "handler": self.name,
                    "action": "no_credentials",
                    "message": "📜 SUTRA: Set GITHUB_TOKEN environment variable to enable wiki sync",
                }

            else:
                # Just gather context (preview mode)
                weaver = SutraWeaver(workspace=self._workspace)
                ctx = weaver.gather_context()

                return {
                    "success": True,
                    "handler": self.name,
                    "action": "context_gathered",
                    "agents_found": len(ctx.agents),
                    "modules_found": len(ctx.modules),
                    "has_credentials": has_creds,
                    "message": (
                        f"📜 SUTRA gathered context: {len(ctx.agents)} agents, {len(ctx.modules)} modules. "
                        + ("Ready to sync!" if has_creds else "Set GITHUB_TOKEN to enable sync.")
                    ),
                }

        except Exception as e:
            logger.error(f"SUTRA error: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}
