"""
Moltbook Context Builders — Shared context extraction for LLM prompts.

Three functions used by AgencyDirector (L5) and ResonanceProposer (L3)
to fill YAML template slots in config/prompts/moltbook.yaml.
"""

import logging
from typing import Dict

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
