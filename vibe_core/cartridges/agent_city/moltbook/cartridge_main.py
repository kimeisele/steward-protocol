"""
MOLTBOOK AGENT CARTRIDGE — Fraktal Agency Orchestrator
=======================================================

Routes tasks through AgencyDirector (I-P-V-O):
    INPUT:    Knowledge Graph + MahaLLM Kernel + ServiceRegistry discovery
    PROCESS:  mahamantra(text) → MahaComposition/LLM → content
    VALIDATE: Constitution check (governance/constitution.py)
    OUTPUT:   CycleResult → caller

Guna informs STYLE (guardian, tone), NOT gating.
Only TAMAS + dead cell = skip. SATTVA and RAJAS both produce content.

Systems wired:
    - Mahamantra VM pipeline (27-key result: guna, guardian, smaranam, verse)
    - MahaComposition (5 scorers: prana, rhythm, semantic/WordNet, mode, state)
    - MahaLanguageEngine (EngineResult: resonant words, template, section)
    - Knowledge Graph (domain context, constraint checking)
    - MahaLLM Kernel (guardian vocabulary, semantic expansion)
    - EventBus (system visibility: THOUGHT, ACTION, VIOLATION events)
    - ServiceRegistry (dynamic capability discovery)

Task routing:
    analyze         → proposer.analyze() (direct, no I-P-V-O needed)
    compose_*       → AgencyDirector.run_retry_loop() (full I-P-V-O)
    engage          → proposer.should_engage() + event_log
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
    from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

    return ResonanceProposer()


class MoltbookCartridge(ContextAwareAgent, OathMixin):
    """
    Moltbook Social Intelligence Agent.

    Uses Mahamantra substrate directly for content generation.
    Guna → style (not gate). Guardian from pipeline (not static pool).
    MahaComposition + LLM for content. EventBus for visibility.
    """

    def __init__(self, config: Optional[Any] = None):
        super().__init__(
            agent_id="moltbook",
            name="MOLTBOOK",
            version="3.0.0",
            author="Steward Protocol",
            description="Social intelligence agency — mahamantra-direct I-P-V-O, dynamic guna-style, event-sourced",
            domain="SOCIAL",
            capabilities=[
                "feed_analysis",
                "content_generation",
                "dm_processing",
                "community_engagement",
                "semantic_search",
                "governance_validation",
                "event_sourcing",
            ],
            config=config,
        )

        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True
        self._proposer = None
        self._director = None

        logger.info("MOLTBOOK cartridge initialized (v3 — mahamantra-direct agency)")

    @property
    def director(self):
        """Lazy-init AgencyDirector."""
        if self._director is None:
            from .core.agency_director import AgencyDirector
            self._director = AgencyDirector()
        return self._director

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
        """Route task through I-P-V-O pipeline or direct API."""
        action = task.payload.get("action")
        logger.info(f"MOLTBOOK processing: {action}")

        handlers = {
            "analyze": self._analyze,
            "compose_comment": self._compose_comment,
            "compose_post": self._compose_post,
            "compose_dm_reply": self._compose_dm_reply,
            "engage": self._engage,
            "status": self._status,
        }

        handler = handlers.get(action)
        if handler is None:
            return {"status": "error", "error": f"Unknown action: {action}"}

        try:
            return handler(task.payload)
        except Exception as e:
            logger.error(f"MOLTBOOK {action} failed: {e}")
            return {"status": "error", "error": str(e)}

    # =========================================================================
    # Direct API (no I-P-V-O needed)
    # =========================================================================

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

    # =========================================================================
    # I-P-V-O Pipeline (content generation with governance)
    # =========================================================================

    def _compose_comment(self, payload: Dict) -> Dict[str, Any]:
        """Compose comment through I-P-V-O pipeline."""
        post_content = payload.get("post_content", "")
        if not post_content:
            return {"status": "error", "error": "No post_content provided"}

        result = self.director.run_retry_loop(
            content_type="comment",
            raw_input=post_content,
            post_id=payload.get("post_id", ""),
            trigger=payload.get("trigger", "cartridge"),
        )

        if result.status == "SUCCESS":
            return {"status": "success", "content": result.content, "retries": result.retries_used}
        elif result.status == "VALIDATION_FAILED":
            return {"status": "filtered", "reason": "Governance violation", "violations": result.violations}
        else:
            return {"status": "error", "error": result.error or "Pipeline failed"}

    def _compose_post(self, payload: Dict) -> Dict[str, Any]:
        """Compose post through I-P-V-O pipeline."""
        # Build seed text from trigger + topics
        trigger = payload.get("trigger", "cartridge")
        context = payload.get("context", {})
        topics = context.get("feed_topics", [])
        seed = f"{trigger}: {', '.join(str(t) for t in topics[:3])}" if topics else trigger

        result = self.director.run_retry_loop(
            content_type="post",
            raw_input=seed,
            trigger=trigger,
            context=context,
        )

        if result.status == "SUCCESS":
            return {"status": "success", "content": result.content, "retries": result.retries_used}
        elif result.status == "VALIDATION_FAILED":
            return {"status": "filtered", "reason": "Governance violation", "violations": result.violations}
        else:
            return {"status": "error", "error": result.error or "Pipeline failed"}

    def _compose_dm_reply(self, payload: Dict) -> Dict[str, Any]:
        """Compose DM reply through I-P-V-O pipeline."""
        content = payload.get("content", "")
        if not content:
            return {"status": "error", "error": "No content provided"}

        result = self.director.run_retry_loop(
            content_type="dm_reply",
            raw_input=content,
            conversation_id=payload.get("conversation_id", ""),
            sender=payload.get("sender", ""),
        )

        if result.status == "SUCCESS":
            return {"status": "success", "content": result.content, "retries": result.retries_used}
        elif result.status == "VALIDATION_FAILED":
            return {"status": "filtered", "reason": "Governance violation", "violations": result.violations}
        else:
            return {"status": "error", "error": result.error or "Pipeline failed"}

    # =========================================================================
    # Engagement (through AgencyDirector)
    # =========================================================================

    def _engage(self, payload: Dict) -> Dict[str, Any]:
        """Engagement decision via agency director."""
        post_content = payload.get("post_content", "")
        if not post_content:
            return {"status": "error", "error": "No post_content"}

        # Use proposer for engagement scoring (no I-P-V-O needed for upvotes)
        proposer = self._ensure_proposer()
        proposal = proposer.should_engage(
            post_id=payload.get("post_id", ""),
            post_content=post_content,
            author=payload.get("author", ""),
        )

        if proposal is None:
            return {"status": "skip", "reason": "Below engagement threshold"}

        # Record engagement in event log
        self.director.event_log.record_engagement(
            "engage", payload.get("post_id", ""), author=payload.get("author", "")
        )

        return {"status": "engage", "proposal": dict(proposal)}

    # =========================================================================
    # Status (agency-aware)
    # =========================================================================

    def _status(self, payload: Dict) -> Dict[str, Any]:
        """Return agency status including event log state."""
        state = self.director.event_log.rebuild_state()
        return {
            "status": "success",
            "agency": {
                "version": self.version,
                "capabilities": self.capabilities,
                "event_log": state,
                "governance": self.director.constitution.get_rules_summary(),
            },
        }

    def report_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "proposer_ready": self._proposer is not None,
            "director_ready": self._director is not None,
        }


__all__ = ["MoltbookCartridge"]
