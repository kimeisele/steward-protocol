"""
Moltbook Context Builders — Shared context extraction for LLM prompts.

Functions used by AgencyDirector (L5) and ResonanceProposer (L3)
to fill YAML template slots in config/prompts/moltbook.yaml.

v11 adds: strategic_context(), engagement_context() for topic-first prompts.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("MOLTBOOK.CONTEXT")


def format_resonant_words(engine_result) -> str:
    """EngineResult.resonant_words -> structured context string.

    Format: "sanskrit (meaning), ..." — top 7 words.
    Fills {resonant_words} slot in YAML templates.
    """
    if not engine_result or not getattr(engine_result, "resonant_words", None):
        return ""
    return ", ".join(f"{s} ({m})" for s, m, _ in engine_result.resonant_words[:7])


def section_data(engine_result) -> Dict[str, str]:
    """Section Router -> section name + mode.

    Fills {section_name} and {section_mode} slots in YAML templates.
    """
    if not engine_result:
        return {"section_name": "", "section_mode": "CORE"}
    section = getattr(engine_result, "section_name", "") or ""
    mode = getattr(engine_result, "section_mode", "") or "CORE"
    return {"section_name": section, "section_mode": mode}


def guardian_vocabulary_short(guardian_name: str) -> str:
    """Top-5 guardian vocabulary — meanings only (no Sanskrit).

    Gives LLM a voice fingerprint in ~15 tokens.
    Fills {voice} slot in YAML templates.
    """
    if not guardian_name:
        return ""
    try:
        from vibe_core.mahamantra.substrate.encoding.maha_llm_kernel import get_kernel

        profile = get_kernel().guardian(guardian_name.lower())
        if not profile.vocabulary:
            return ""
        return ", ".join(w.first_meaning for w in profile.vocabulary[:5])
    except Exception:
        return ""


def strategic_context(intent: Optional[Any] = None) -> str:
    """Build strategic reasoning string for LLM prompt.

    Fills {strategic_reasoning} slot in YAML v11 templates.
    """
    if not intent:
        return ""
    reasoning = getattr(intent, "reasoning", "")
    engagement = getattr(intent, "engagement_context", "")
    parts = []
    if reasoning:
        parts.append(reasoning)
    if engagement:
        parts.append(engagement)
    return ". ".join(parts) if parts else ""


def engagement_context(content_type: str = "") -> str:
    """Build engagement insight from FeedbackProtocol history.

    Fills {engagement_context} slot. Reads from registered FeedbackProtocol.
    """
    try:
        from vibe_core.protocols.feedback import get_feedback_safe
        stats = get_feedback_safe().get_stats()
        if stats.total_signals < 3:
            return ""
        return f"Success rate: {stats.success_rate:.0%}. Total: {stats.total_signals}."
    except Exception:
        return ""
