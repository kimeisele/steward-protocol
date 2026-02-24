"""
Moltbook Context Builders — Shared context extraction for LLM prompts.

Extracts structured data from Mahamantra systems into a flat dict
that fills YAML template slots via PromptRegistry.get(key, context=ctx).

Used by both AgencyDirector (L5) and ResonanceProposer (L3).

Sources: EngineResult, MahaLLM Kernel, KnowledgeResolver, pipeline NAMA coords.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("MOLTBOOK.CONTEXT")


def format_resonant_words(engine_result) -> str:
    """EngineResult.resonant_words -> structured context string."""
    if not engine_result or not getattr(engine_result, "resonant_words", None):
        return ""
    return ", ".join(f"{s} ({m})" for s, m, _ in engine_result.resonant_words[:7])


def format_template_words(engine_result) -> str:
    """EngineResult.template_words -> grammatical skeleton string."""
    if not engine_result or not getattr(engine_result, "template_words", None):
        return ""
    return ", ".join(f"{m} [{r}]" for _, m, r in engine_result.template_words[:7] if m)


def section_data(engine_result) -> Dict[str, str]:
    """Section Router -> semantic mode + element."""
    if not engine_result:
        return {"section_name": "", "section_mode": "CORE", "section_semantic": "", "section_element": ""}
    section = getattr(engine_result, "section_name", "") or ""
    mode = getattr(engine_result, "section_mode", "") or "CORE"
    try:
        from vibe_core.mahamantra.substrate.language.section_router import SECTION_SIGNATURES

        sig = SECTION_SIGNATURES.get(section, {})
        return {
            "section_name": section,
            "section_mode": mode,
            "section_semantic": str(sig.get("semantic", "")),
            "section_element": str(sig.get("element", "")),
        }
    except Exception:
        return {"section_name": section, "section_mode": mode, "section_semantic": "", "section_element": ""}


def guardian_vocabulary(guardian_name: str) -> str:
    """MahaLLM Kernel -> guardian's top-10 vocabulary words.

    Each guardian has a unique semantic fingerprint: the 10 Gita words
    that score highest for their 4D position.
    """
    if not guardian_name:
        return ""
    try:
        from vibe_core.mahamantra.substrate.encoding.maha_llm_kernel import get_kernel

        profile = get_kernel().guardian(guardian_name.lower())
        if not profile.vocabulary:
            return ""
        return ", ".join(
            f"{w.sanskrit} ({w.first_meaning})"
            for w in profile.vocabulary[:10]
        )
    except Exception:
        return ""


def phonetic_context(pipeline_result: Optional[dict]) -> Dict[str, str]:
    """Extract element walk + shruti pattern from pipeline NAMA coords.

    Element walk: phonetic journey through fire/water/earth/air/space.
    Shruti pattern: S=consonant (harmonic), N=dissonant.
    """
    if not pipeline_result:
        return {"element_walk": "", "shruti_pattern": ""}
    nama = pipeline_result.get("nama", {})
    coords = nama.get("coords", ())
    if not coords:
        return {"element_walk": "", "shruti_pattern": ""}
    try:
        from vibe_core.mahamantra.substrate.pancha_walk import (
            COORD_ELEMENT,
            ELEMENT_NAMES,
            IS_SHRUTI,
        )

        element_walk = " → ".join(ELEMENT_NAMES[COORD_ELEMENT[c]] for c in coords)
        shruti_pattern = "".join("S" if IS_SHRUTI[c] else "N" for c in coords)
        return {"element_walk": element_walk, "shruti_pattern": shruti_pattern}
    except Exception:
        return {"element_walk": "", "shruti_pattern": ""}


def resonance_dimensions(text: str) -> str:
    """7D resonance score breakdown for input text.

    Uses resonance_ranker.resonate() to score against Gita lexicon.
    Returns formatted dimension breakdown for LLM context.
    """
    if not text or not text.strip():
        return ""
    try:
        from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate

        ranked = resonate(text, top_n=3)
        if not ranked:
            return ""
        # Use top word's breakdown as representative
        bd = ranked[0].score_breakdown()
        parts = []
        for dim in ("element", "harmonic", "shruti", "varga", "attractor", "hkr", "phoneme_attractor"):
            score = bd.get(dim, 0.0)
            if score > 0.01:
                parts.append(f"{dim}={score:.2f}")
        return f"total={bd.get('total', 0.0):.2f} [{', '.join(parts)}]" if parts else ""
    except Exception:
        return ""


def cell_state_context(pipeline_result: Optional[dict]) -> Dict[str, str]:
    """Extract post-kirtan cell state from pipeline result.

    The VM already runs Chamber.kirtan() during execute_cycle().
    These values reflect the refined cell after N×16 transformations.
    """
    if not pipeline_result:
        return {"cell_prana": "", "cell_integrity": "", "cell_cycle": "", "cell_alive": ""}
    cell = pipeline_result.get("cell", {})
    if not cell:
        return {"cell_prana": "", "cell_integrity": "", "cell_cycle": "", "cell_alive": ""}
    return {
        "cell_prana": str(cell.get("prana", "")),
        "cell_integrity": f"{cell.get('integrity', 0.0):.3f}" if cell.get("integrity") is not None else "",
        "cell_cycle": str(cell.get("cycle", "")),
        "cell_alive": str(cell.get("is_alive", "")),
    }


def knowledge_context(topic: str) -> str:
    """KnowledgeResolver -> graph-aware context.

    Queries the Knowledge Graph with the topic AND Moltbook domain terms
    to get platform-specific knowledge from knowledge/moltbook/platform.yaml.
    """
    if not topic:
        return ""
    try:
        from vibe_core.knowledge.resolver import get_resolver

        resolver = get_resolver()
        ctx = resolver.compile_context(topic)
        moltbook_ctx = resolver.compile_context("moltbook")
        if moltbook_ctx and moltbook_ctx != ctx:
            ctx = f"{ctx}\n{moltbook_ctx}" if ctx else moltbook_ctx
        return ctx
    except Exception:
        return ""


def build_moltbook_context(
    engine_result,
    agent_name: str,
    user_input: str,
    pipeline_result: Optional[dict] = None,
    **extra: Any,
) -> Dict[str, str]:
    """Build ALL context from ALL systems into one dict.

    This dict fills YAML template slots. No instructions — just data.
    Sources: EngineResult, MahaLLM Kernel, KnowledgeResolver, pipeline coords.

    Extra kwargs are merged last (override defaults). Use for:
    - sender, trigger, post_content (content-type-specific slots)
    - resonance_zone, rasa_name, rasa_meaning, guna, style (harmonics data)
    - sravanam_status, previous_violations (process state)
    """
    from vibe_core.mahamantra.substrate.encoding.seed_to_words import _GUARDIAN_CONFIGS

    guardian_name_raw = ""
    guardian = "UNKNOWN"
    guardian_cfg: dict = {}

    if engine_result:
        guardian_name_raw = getattr(engine_result, "guardian_name", "") or ""
        guardian = guardian_name_raw.upper() if guardian_name_raw else "UNKNOWN"
        guardian_cfg = _GUARDIAN_CONFIGS.get(guardian_name_raw, {})

    sec = section_data(engine_result)

    # Extended EngineResult fields
    intent = ""
    expanded = ""
    syllables = "0"
    derivation = ""
    verse_ref = ""
    engine_output = ""
    guardian_function = "analysis"

    # Extended EngineResult fields (Phase 5: full extraction)
    antaranga_active = "0"
    antaranga_prana = "0"
    stress_pattern = ""
    phoneme_trajectory = ""

    if engine_result:
        intent = getattr(engine_result, "intent_category", "") or ""
        expanded = ", ".join(getattr(engine_result, "expanded_names", ()) or ())
        syllables = str(getattr(engine_result, "syllable_count", 0) or 0)
        derivation = getattr(engine_result, "derivation", "") or ""
        verse_ref = getattr(engine_result, "verse_ref", "") or ""
        engine_output = getattr(engine_result, "output", "") or ""
        guardian_function = getattr(engine_result, "guardian_function", "") or "analysis"
        antaranga_active = str(getattr(engine_result, "antaranga_active", 0) or 0)
        antaranga_prana = str(getattr(engine_result, "antaranga_prana", 0) or 0)
        stress_raw = getattr(engine_result, "stress_pattern", ()) or ()
        stress_pattern = "".join(str(s) for s in stress_raw) if stress_raw else ""
        phoneme_trajectory = getattr(engine_result, "phoneme_trajectory", "") or ""

    # MahaLLM Kernel: guardian vocabulary
    vocab = guardian_vocabulary(guardian_name_raw)

    # Phonetic context from pipeline NAMA coords
    phonetic = phonetic_context(pipeline_result)

    # 7D resonance score breakdown
    res_dims = resonance_dimensions(user_input) if user_input else ""

    # Post-kirtan cell state (VM already runs Chamber.kirtan())
    cell_ctx = cell_state_context(pipeline_result)

    ctx = {
        # Identity + structure
        "agent_name": agent_name,
        "guardian_name": guardian,
        "position": str(guardian_cfg.get("position", 0)),
        "quarter": sec.get("section_mode", "CORE"),
        "guardian_function": guardian_function,
        # Engine output
        "engine_output": engine_output,
        "resonant_words": format_resonant_words(engine_result),
        "template_words": format_template_words(engine_result),
        "verse_ref": verse_ref,
        "derivation": derivation,
        "intent_category": intent,
        "expanded_names": expanded,
        "syllable_count": syllables,
        # Antaranga (cell resonance state)
        "antaranga_active": antaranga_active,
        "antaranga_prana": antaranga_prana,
        "stress_pattern": stress_pattern,
        "phoneme_trajectory": phoneme_trajectory,
        # External systems
        "knowledge_context": knowledge_context(user_input[:200] if user_input else ""),
        "guardian_vocabulary": vocab,
        "element_walk": phonetic["element_walk"],
        "shruti_pattern": phonetic["shruti_pattern"],
        "resonance_dimensions": res_dims,
        # Cell state (post-kirtan from VM)
        **cell_ctx,
        # Input
        "user_input": user_input or "",
        # Harmonics defaults (overridden by caller via **extra)
        "guna": "",
        "style": "",
        "resonance_zone": "",
        "rasa_name": "",
        "rasa_meaning": "",
        "sravanam_status": "",
        # Content-type-specific defaults
        "sender": "",
        "trigger": "",
        "post_content": "",
        "composed_words": "",
        # Section data
        **sec,
        # Caller overrides last
        **{k: str(v) for k, v in extra.items()},
    }
    return ctx
