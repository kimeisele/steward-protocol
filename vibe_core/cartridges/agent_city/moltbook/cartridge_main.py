"""
MOLTBOOK AGENT CARTRIDGE — Thin Delegation Layer
==================================================

Delegates to ResonanceProposer (registered in ServiceRegistry by plugin).
Does NOT call private methods. Does NOT duplicate gate logic.
The plugin owns the heartbeat + proposer lifecycle.
The cartridge routes tasks to proposer's public API.
"""

import logging
from typing import Any, Dict, Optional

from vibe_core import Task, VibeAgent
from vibe_core.agents import ContextAwareAgent
from vibe_core.protocols import AgentManifest
from vibe_core.steward import OathMixin

logger = logging.getLogger("MOLTBOOK_CARTRIDGE")


def _get_proposer():
    """Get ResonanceProposer from ServiceRegistry (registered by plugin at boot)."""
    try:
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.moltbook_content import ContentProposalProtocol

        proposer = ServiceRegistry.get(ContentProposalProtocol)
        if proposer is not None:
            return proposer
    except Exception:
        pass
    # Fallback: create directly (for standalone use without plugin)
    from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

    return ResonanceProposer()


class MoltbookCartridge(ContextAwareAgent, OathMixin):
    """
    Moltbook Social Intelligence Agent.

    Thin layer — delegates to ResonanceProposer public API.
    Plugin (plugin_main.py) owns the heartbeat, client, and proposer lifecycle.
    """

    def __init__(self, config: Optional[Any] = None):
        super().__init__(
            agent_id="moltbook",
            name="MOLTBOOK",
            version="1.0.0",
            author="Steward Protocol",
            description="Social intelligence engine — feed analysis, content generation, community engagement",
            domain="SOCIAL",
            capabilities=[
                "feed_analysis",
                "content_generation",
                "dm_processing",
                "community_engagement",
                "semantic_search",
            ],
            config=config,
        )

        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True
        self._proposer = None

        logger.info("MOLTBOOK cartridge initialized")

    def _ensure_proposer(self):
        if self._proposer is None:
            self._proposer = _get_proposer()
        return self._proposer

    def get_manifest(self) -> AgentManifest:
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """Route task to proposer's public API."""
        action = task.payload.get("action")
        logger.info(f"MOLTBOOK processing: {action}")

        handlers = {
            "analyze": self._analyze,
            "compose_comment": self._compose_comment,
            "compose_post": self._compose_post,
            "compose_dm_reply": self._compose_dm_reply,
            "engage": self._engage,
        }

        handler = handlers.get(action)
        if handler is None:
            return {"status": "error", "error": f"Unknown action: {action}"}

        try:
            return handler(task.payload)
        except Exception as e:
            logger.error(f"MOLTBOOK {action} failed: {e}")
            return {"status": "error", "error": str(e)}

    def _analyze(self, payload: Dict) -> Dict[str, Any]:
        """Analyze text via proposer's public analyze() method."""
        text = payload.get("text", "")
        if not text:
            return {"status": "error", "error": "No text provided"}

        proposer = self._ensure_proposer()
        ranked = proposer.analyze(text)

        return {
            "status": "success",
            "words": [{"sanskrit": rw.sanskrit, "score": round(rw.total_score, 4)} for rw in ranked[:7]],
        }

    def _compose_comment(self, payload: Dict) -> Dict[str, Any]:
        """Compose comment via proposer's propose_comment()."""
        post_content = payload.get("post_content", "")
        if not post_content:
            return {"status": "error", "error": "No post_content provided"}

        proposer = self._ensure_proposer()
        proposal = proposer.propose_comment(
            post_id=payload.get("post_id", ""),
            post_content=post_content,
            trigger=payload.get("trigger", "cartridge"),
        )

        if proposal is None:
            return {"status": "filtered", "reason": "Rejected by system gates"}

        return {"status": "success", "proposal": dict(proposal)}

    def _compose_post(self, payload: Dict) -> Dict[str, Any]:
        """Compose post via proposer's propose_post()."""
        proposer = self._ensure_proposer()
        proposal = proposer.propose_post(
            trigger=payload.get("trigger", "cartridge"),
            context=payload.get("context", {}),
        )

        if proposal is None:
            return {"status": "filtered", "reason": "Requires RAJAS + alive + integrity > 0.5"}

        return {"status": "success", "proposal": dict(proposal)}

    def _compose_dm_reply(self, payload: Dict) -> Dict[str, Any]:
        """Compose DM reply via proposer's propose_dm_reply()."""
        content = payload.get("content", "")
        if not content:
            return {"status": "error", "error": "No content provided"}

        proposer = self._ensure_proposer()
        proposal = proposer.propose_dm_reply(
            conversation_id=payload.get("conversation_id", ""),
            sender=payload.get("sender", ""),
            inbound_content=content,
        )

        if proposal is None:
            return {"status": "filtered", "reason": "Rejected by system gates"}

        return {"status": "success", "proposal": dict(proposal)}

    def _engage(self, payload: Dict) -> Dict[str, Any]:
        """Engagement decision via proposer's should_engage()."""
        post_content = payload.get("post_content", "")
        if not post_content:
            return {"status": "error", "error": "No post_content"}

        proposer = self._ensure_proposer()
        proposal = proposer.should_engage(
            post_id=payload.get("post_id", ""),
            post_content=post_content,
            author=payload.get("author", ""),
        )

        if proposal is None:
            return {"status": "skip", "reason": "Rejected by system gates"}

        return {"status": "engage", "proposal": dict(proposal)}

    def report_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "proposer_ready": self._proposer is not None,
        }


__all__ = ["MoltbookCartridge"]
