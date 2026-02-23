"""
Moltbook Content Capability — Thin wrapper for ServiceRegistry access.

The REAL content generation happens in:
    - AgencyDirector._process() → mahamantra() → MahaComposition/LLM
    - ResonanceProposer (registered via plugin at boot)

This capability provides:
    - ServiceRegistry access to the proposer
    - Public API for direct proposer calls (analyze, should_engage)

NO static guardian pools. NO translation layer. NO hardcoded maps.
Guardian selection is DYNAMIC from the Mahamantra pipeline.
Content composition uses MahaComposition (5 scorers incl. WordNet + mode_affinity).
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MOLTBOOK_CONTENT")


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


class ContentCapability:
    """Content intelligence — delegates to ResonanceProposer via ServiceRegistry.

    The proposer owns:
        - analyze(text) → ranked resonant words
        - should_engage(post_id, content, author) → engagement decision
        - _run_pipeline(text) → mahamantra VM result
        - _generate(text) → MahaLanguageEngine result
        - _compose() → LLM or MahaComposition fallback

    The AgencyDirector uses mahamantra infrastructure directly for content
    generation (bypassing proposer gates). This capability exists for
    direct analysis and engagement scoring where I-P-V-O is not needed.
    """

    def __init__(self):
        self._proposer = None

    @property
    def proposer(self):
        if self._proposer is None:
            self._proposer = _get_proposer()
        return self._proposer

    def analyze(self, text: str) -> List:
        """Analyze text → ranked resonant words."""
        return self.proposer.analyze(text)

    def should_engage(self, post_id: str, post_content: str, author: str) -> Optional[Dict]:
        """Engagement scoring (no I-P-V-O needed for votes)."""
        return self.proposer.should_engage(post_id, post_content, author)

    def analyze_feed(self, posts: List[Dict[str, Any]]) -> List:
        """Score and rank feed posts."""
        return self.proposer.analyze_feed(posts)


_content_capability: Optional[ContentCapability] = None


def get_content_capability() -> ContentCapability:
    """Get ContentCapability singleton."""
    global _content_capability
    if _content_capability is None:
        _content_capability = ContentCapability()
    return _content_capability
