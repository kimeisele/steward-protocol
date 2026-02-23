"""
Moltbook Content Capability — Translation Layer + Multi-Guardian.

Pattern: Herald capabilities/creative.py

Wraps ResonanceProposer + adds:
    1. TRANSLATION LAYER: Sanskrit internals → readable English
       - guardian_function → expertise area (maintainer→reliability, creator→innovation)
       - section_mode → rhetoric (CORE→direct, FILTER→selective, QUALITY→evaluative)
       - resonant words → engineering vocabulary
    2. MULTI-GUARDIAN ROTATION: content-type → guardian pool
       - analytical comments → KAPILA, VASISHTHA
       - supportive comments → NARADA, PRAHLADA
       - technical posts → KAPILA, VYASA
       - DM replies → match sender's guardian

Uses existing infrastructure:
    - ResonanceProposer (ServiceRegistry)
    - MahaLLM Kernel: expand(), resonate_as(), guardian()
    - render(result) → guardian persona rendering
    - PromptRegistry: moltbook.yaml templates
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("MOLTBOOK_CONTENT")

# Guardian function → expertise area mapping
_GUARDIAN_EXPERTISE: Dict[str, str] = {
    "analysis": "systems analysis",
    "compilation": "knowledge synthesis",
    "creation": "innovation",
    "maintenance": "reliability engineering",
    "destruction": "optimization and cleanup",
    "communication": "community building",
    "devotion": "deep focus and dedication",
    "wisdom": "architectural insight",
    "sovereignty": "decision making",
    "purity": "quality assurance",
    "teaching": "knowledge transfer",
    "hearing": "active listening and research",
}

# Section mode → rhetorical style
_MODE_RHETORIC: Dict[str, str] = {
    "CORE": "direct and essential",
    "FILTER": "selective and discerning",
    "VERB": "action-oriented",
    "QUALITY": "evaluative and descriptive",
    "CONTEXT": "situational and grounded",
    "TARGET": "goal-directed",
    "CLOSURE": "conclusive and summarizing",
}

# Content type → preferred guardian pools
_GUARDIAN_POOLS: Dict[str, List[str]] = {
    "comment_analytical": ["kapila", "vasishtha"],
    "comment_supportive": ["narada", "prahlada"],
    "post_technical": ["kapila", "vyasa"],
    "post_philosophical": ["vasishtha", "janaka"],
    "dm_reply": [],  # Dynamic: match sender's guardian
}


def _get_proposer():
    """Get ResonanceProposer from ServiceRegistry."""
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


def _get_kernel():
    """Get MahaLLM Kernel singleton."""
    try:
        from vibe_core.mahamantra.substrate.encoding.maha_llm_kernel import get_kernel

        return get_kernel()
    except Exception:
        return None


class ContentCapability:
    """Content generation with translation layer and multi-guardian rotation."""

    def __init__(self):
        self._proposer = None
        self._kernel = None
        self._guardian_cycle: Dict[str, int] = {}  # content_type → cycle index

    @property
    def proposer(self):
        if self._proposer is None:
            self._proposer = _get_proposer()
        return self._proposer

    @property
    def kernel(self):
        if self._kernel is None:
            self._kernel = _get_kernel()
        return self._kernel

    def generate_comment(
        self,
        post_id: str,
        post_content: str,
        trigger: str = "feed_analysis",
        style: str = "analytical",
    ) -> Optional[Dict[str, Any]]:
        """Generate a comment with translation + guardian rotation."""
        # Select guardian from pool
        pool_key = f"comment_{style}"
        guardian = self._next_guardian(pool_key)

        # Generate via proposer (with forced guardian if kernel available)
        proposal = self.proposer.propose_comment(
            post_id=post_id,
            post_content=post_content,
            trigger=trigger,
        )
        if proposal is None:
            return None

        # Translate: enrich with guardian lens if kernel available
        content = proposal.get("content", "")
        translated = self._translate(content, guardian, "comment")
        if translated:
            proposal["content"] = translated
            proposal["_guardian_override"] = guardian

        return proposal

    def generate_post(
        self,
        trigger: str = "scheduled",
        context: Optional[Dict[str, Any]] = None,
        style: str = "technical",
    ) -> Optional[Dict[str, Any]]:
        """Generate a post with translation + guardian rotation."""
        guardian = self._next_guardian(f"post_{style}")

        proposal = self.proposer.propose_post(
            trigger=trigger,
            context=context or {},
        )
        if proposal is None:
            return None

        content = proposal.get("content", "")
        translated = self._translate(content, guardian, "post")
        if translated:
            proposal["content"] = translated
            proposal["_guardian_override"] = guardian

        return proposal

    def generate_dm_reply(
        self,
        conversation_id: str,
        sender: str,
        inbound_content: str,
        gateway_response: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generate DM reply — matches sender's guardian for resonance."""
        # For DMs: use sender text to determine guardian match
        guardian = self._match_sender_guardian(inbound_content)

        proposal = self.proposer.propose_dm_reply(
            conversation_id=conversation_id,
            sender=sender,
            inbound_content=inbound_content,
            gateway_response=gateway_response,
        )
        if proposal is None:
            return None

        content = proposal.get("content", "")
        translated = self._translate(content, guardian, "dm_reply")
        if translated:
            proposal["content"] = translated

        return proposal

    def _translate(self, content: str, guardian: Optional[str], content_type: str) -> Optional[str]:
        """Translation layer: enrich content with guardian lens via MahaLLM Kernel.

        If kernel unavailable, returns None (use original content).
        """
        kernel = self.kernel
        if kernel is None or not content:
            return None

        try:
            # Use resonate_as() to get guardian-specific lens on the content
            if guardian and hasattr(kernel, "resonate_as"):
                result = kernel.resonate_as(content, guardian)
                if result and hasattr(result, "resonant_words"):
                    # Expand vocabulary using HKR semantic trees
                    expanded = kernel.expand(content) if hasattr(kernel, "expand") else None
                    if expanded and hasattr(expanded, "words"):
                        # Build enriched output from expanded vocabulary
                        enriched_words = []
                        for word in expanded.words[:5]:
                            meaning = getattr(word, "meaning", "")
                            if meaning:
                                enriched_words.append(meaning)
                        if enriched_words:
                            # Append guardian vocabulary naturally
                            return f"{content} — {', '.join(enriched_words[:3])}"
        except Exception as e:
            logger.debug(f"Translation layer skipped: {e}")

        return None

    def _next_guardian(self, pool_key: str) -> Optional[str]:
        """Rotate through guardian pool for content type."""
        pool = _GUARDIAN_POOLS.get(pool_key, [])
        if not pool:
            return None

        idx = self._guardian_cycle.get(pool_key, 0)
        guardian = pool[idx % len(pool)]
        self._guardian_cycle[pool_key] = idx + 1
        return guardian

    def _match_sender_guardian(self, text: str) -> Optional[str]:
        """Determine sender's guardian from their text for resonance matching."""
        kernel = self.kernel
        if kernel is None:
            return None
        try:
            if hasattr(kernel, "guardian"):
                result = kernel.guardian(text)
                if result:
                    return str(result)
        except Exception:
            pass
        return None

    def translate_guardian_function(self, function: str) -> str:
        """Translate guardian function → expertise area."""
        return _GUARDIAN_EXPERTISE.get(function.lower(), function)

    def translate_section_mode(self, mode: str) -> str:
        """Translate section mode → rhetorical style."""
        return _MODE_RHETORIC.get(mode.upper(), "balanced")


_content_capability: Optional[ContentCapability] = None


def get_content_capability() -> ContentCapability:
    """Get ContentCapability singleton."""
    global _content_capability
    if _content_capability is None:
        _content_capability = ContentCapability()
    return _content_capability
