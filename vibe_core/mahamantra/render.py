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

from typing import Dict, List, Optional


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
