"""
KIRTAN RENDERER — The Tongue of the Mahamantra
================================================

"vāg-gadgadā dravate yasya cittaṁ"
"His voice chokes up, his heart melts." (SB 11.2.40)

Renders a VM result dict (27-key output of execute_cycle) into
human-readable text. This is a TONGUE, not a BRAIN.

The renderer checks for enrichment keys (future CycleCompiler
custom ops like MANAS cognition or Language Engine composition)
and falls back to pure resonance rendering.

ARCHITECTURE:
    mahamantra(input) → VM 9 Steps → 27-key result dict
                                          ↓
                                    render(result) → str

    kirtan_chat(input) → mahamantra(input) → result
                              ↓                  ↓
                         [optional LLM]    render(result)
                              ↓
                         enriched output

EXTENSION PATTERN:
    Custom ops add keys to the result dict via CycleCompiler.
    The renderer discovers and uses them. No code changes needed.

    "cognitive_response"  → MANAS integration (future)
    "composed_text"       → Language Engine (future)
    (default)             → Pure resonance rendering (now)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0xa7c1e2f0"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("KIRTAN")


def render(result: Dict) -> str:
    """Render a VM result dict to human-readable Kirtan output.

    Checks for enrichment keys first (future extensions),
    falls back to pure resonance rendering.

    Args:
        result: The 27-key dict from mahamantra(input) / execute_cycle().

    Returns:
        Human-readable string.
    """
    # Future: MANAS cognitive layer adds this via CycleCompiler
    if "cognitive_response" in result:
        return str(result["cognitive_response"])

    # Future: Language Engine adds this via CycleCompiler
    if "composed_text" in result:
        return _render_composed(result)

    # Default: Pure resonance rendering
    return _render_resonance(result)


def _render_resonance(result: Dict) -> str:
    """Render from pure VM resonance data. No LLM, no cognition."""
    guardian = str(result.get("guardian") or "unknown")
    quarter = str(result.get("quarter") or "unknown")
    trinity = str(result.get("trinity_function") or "")

    # Header: Guardian identity
    header = f"[{guardian.upper()} · {quarter} · {trinity}]"

    # Resonant words (smaranam)
    smaranam = result.get("smaranam", ())
    words_lines: List[str] = []
    for rw in smaranam[:5]:
        sanskrit = rw.get("sanskrit", "")
        meaning = rw.get("meaning", "")
        if sanskrit and meaning:
            words_lines.append(f'  "{sanskrit}" ({meaning})')
        elif sanskrit:
            words_lines.append(f'  "{sanskrit}"')

    # Verse reference
    verse = result.get("verse", {})
    verse_ref = ""
    if isinstance(verse, dict):
        ref = verse.get("ref", "")
        if ref:
            verse_ref = ref
    chapter = result.get("chapter", "")
    phase = result.get("gita_phase", "")
    verse_line = ""
    if verse_ref:
        verse_line = f"  {verse_ref}"
        if phase:
            verse_line += f" — {phase}"
    elif chapter and phase:
        verse_line = f"  Chapter {chapter} — {phase}"

    # Assemble
    parts = [header]
    if words_lines:
        parts.append("\n".join(words_lines))
    if verse_line:
        parts.append(verse_line)

    return "\n".join(parts)


def _render_composed(result: Dict) -> str:
    """Render with Language Engine composed text + resonance context."""
    composed = str(result["composed_text"])
    guardian = str(result.get("guardian") or "unknown")
    quarter = str(result.get("quarter") or "unknown")
    trinity = str(result.get("trinity_function") or "")
    header = f"[{guardian.upper()} · {quarter} · {trinity}]"
    return f"{header}\n{composed}"


# =============================================================================
# KIRTAN CHAT — Shadow bridge (goes THROUGH __call__())
# =============================================================================


def kirtan_chat(message: str, *, use_llm: bool = True) -> str:
    """Chat via the canonical VM pipeline with optional LLM enrichment.

    This is the shadow replacement for the 6 legacy chat files.
    ALL routing goes through mahamantra().__call__() → execute_cycle().

    Flow:
        1. mahamantra(message) → 27-key result dict (includes "kirtan" key)
        2. If use_llm=True and LLM available: enrich with LLM using VM
           result as structured context → return LLM response with header
        3. Fallback: return result["kirtan"] (pure resonance rendering)

    Args:
        message: User input text.
        use_llm: If True, attempt LLM enrichment. If False or LLM
                 unavailable, return pure resonance rendering.

    Returns:
        Human-readable response string.
    """
    # Step 1: ALWAYS go through the canonical VM pipeline
    lotus = _get_lotus()
    result = lotus(message)

    # Step 2: Pure resonance rendering is always available
    kirtan_output = result.get("kirtan") or render(result)

    # Step 3: Optional LLM enrichment
    if not use_llm:
        return kirtan_output

    try:
        from vibe_core.runtime.providers.factory import get_llm_provider

        provider = get_llm_provider()

        if not provider.is_available():
            logger.debug("LLM not available, returning pure kirtan")
            return kirtan_output

        prompt = _build_llm_prompt(message, result)
        llm_response = provider.invoke(
            prompt=prompt,
            model=provider.get_available_models()[0],
            max_tokens=512,
            temperature=0.7,
        )

        if llm_response.content and llm_response.content.strip():
            guardian = str(result.get("guardian") or "unknown")
            return f"[{guardian.upper()}] {llm_response.content}"

        # No real content from provider — fall back to kirtan
        logger.debug("LLM returned empty content, returning pure kirtan")
        return kirtan_output

    except Exception as e:
        logger.debug(f"LLM enrichment failed, returning pure kirtan: {e}")
        return kirtan_output


def _build_llm_prompt(message: str, result: Dict) -> str:
    """Build a structured LLM prompt using VM result as context."""
    guardian = str(result.get("guardian") or "unknown")
    quarter = str(result.get("quarter") or "unknown")
    trinity = str(result.get("trinity_function") or "")
    phase = str(result.get("gita_phase") or "")

    # Resonant words as context
    smaranam = result.get("smaranam", ())
    words = ", ".join(
        f"{rw.get('sanskrit', '')} ({rw.get('meaning', '')})" for rw in smaranam[:5] if rw.get("sanskrit")
    )

    # Verse reference
    verse = result.get("verse", {})
    verse_ref = ""
    if isinstance(verse, dict):
        verse_ref = verse.get("ref", "")

    return (
        f"You are {guardian.upper()}, guardian of the {quarter} quarter. "
        f"Your function is {trinity}. "
        f"The current phase is {phase}.\n"
        f"Resonant concepts: {words}\n"
        f"{'Reference: ' + verse_ref if verse_ref else ''}\n"
        f"User says: {message}\n"
        f"Respond concisely as {guardian.upper()}, grounded in the above context."
    )


def _get_lotus():
    """Get or create a bootstrapped MahamantraLotus singleton."""
    global _LOTUS
    if _LOTUS is None:
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        _LOTUS = MahamantraLotus()
        _LOTUS.bootstrap(lazy=True, silent=True)
    return _LOTUS


_LOTUS = None
