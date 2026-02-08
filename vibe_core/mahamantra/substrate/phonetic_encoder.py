"""
PHONETIC ENCODER — Any Language → RAMA Coordinates
===================================================

"sarva-bhūtāni" — all living beings

ONE PATH. ONE TREE. The 49 RAMA Matrix is the root (Shabda Brahman).
All languages are branches — they inherit from the same phonemic tree.

ARCHITECTURE:
    Step 1: IAST greedy longest-match against the 49 Matrix (the ROOT).
            Sanskrit text encodes exactly. Latin letters that exist in
            IAST (a, i, u, k, g, t, d, n, m, s, h, r, l, etc.) also
            match — because IAST uses Latin script.
    Step 2: For characters with NO match in the 49 Matrix (f, w, z, x, q),
            fall back to the nearest articulatory relative (the BRANCH).
    Step 3: Skip non-phonemic characters (spaces, punctuation, digits).

This is NOT two separate tokenizers. It's one tree with branches.
Sanskrit words encode identically whether they have diacritics or not:
    "dharma" → (dha=34, r=42, ma=40) — same as "dharmā" minus the long ā.
    "karma"  → (ka=16, r=42, ma=40) — IAST index knows "ka" is one phoneme.

The old English tokenizer split "dharma" into 5 tokens (d,h,a,r,m,a = wrong).
The unified encoder gets 3 tokens (dha, r, ma = correct) because the IAST
index understands phoneme boundaries via greedy longest-match.

NO LLM. NO EXTERNAL API. PURE PHONETIC MAPPING.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Final, List, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.seed_to_words import SeedResult

from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    ELEMENT_NAMES,
)
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL
from vibe_core.mahamantra.substrate.varnamala_codec import (
    _IAST_INDEX,
    _MAX_IAST_LEN,
    _SKIP_CHARS,
)

# =============================================================================
# IAST DETECTION (utility — no longer used for routing)
# =============================================================================

# Characters that indicate IAST Sanskrit (not present in English/German)
_IAST_MARKERS: Final[frozenset[str]] = frozenset("āīūṛṝḷḹṁḥṅñṭḍṇśṣ")


def detect_language(text: str) -> str:
    """
    Detect input language for routing.

    Returns:
        'sanskrit' if IAST diacriticals detected
        'latin' for English/German/etc (Latin alphabet without diacriticals)

    NOTE: This is kept for backward compatibility and informational use.
    The unified encode_text() no longer branches on this — all text goes
    through the same IAST-rooted path.
    """
    for ch in text:
        if ch in _IAST_MARKERS:
            return "sanskrit"
    return "latin"


# =============================================================================
# ARTICULATORY FALLBACK — The Branch
# =============================================================================
# Sounds that do NOT exist in the 49 Sanskrit Matrix but have a nearest
# articulatory relative. This is the BRANCH from the root — not a separate tree.
#
# Only 5 entries needed. Everything else is already in the IAST index.

_ARTICULATORY_FALLBACK: Final[Dict[str, int]] = {
    "f": 37,   # pha — labiodental fricative → aspirated labial (same lips)
    "w": 44,   # va  — labial approximant → labial semivowel (same lips)
    "z": 23,   # ja  — voiced alveolar fricative → voiced palatal (closest)
    "x": 16,   # ka  — /ks/ cluster → velar component
    "q": 16,   # ka  — /kw/ cluster → velar component
}


# =============================================================================
# UNIFIED ENCODER — One Path, One Tree
# =============================================================================


def _unified_encode(text: str) -> Tuple[int, ...]:
    """
    Encode ANY text through the 49 RAMA Matrix.

    Step 1: IAST greedy longest-match (the ROOT).
            This handles ALL Sanskrit AND most Latin letters because
            IAST uses Latin script: k→ka, g→ga, t→ta, d→da, etc.
    Step 2: Articulatory fallback for non-Sanskrit sounds (the BRANCH).
            Only 5 entries: f→pha, w→va, z→ja, x→ka, q→ka.
    Step 3: Skip non-phonemic characters.

    No detect_language(). No if/else routing. One path.
    """
    coords: List[int] = []
    text_lower = text.lower()
    i = 0

    while i < len(text_lower):
        ch = text_lower[i]

        # Skip non-phonemic characters
        if ch in _SKIP_CHARS or not ch.isalpha() and ch not in _IAST_INDEX:
            i += 1
            continue

        # Step 1: IAST greedy longest-match (ROOT)
        matched = False
        for length in range(min(_MAX_IAST_LEN, len(text_lower) - i), 0, -1):
            candidate = text_lower[i:i + length]
            if candidate in _IAST_INDEX:
                coords.append(_IAST_INDEX[candidate])
                i += length
                matched = True
                break

        if matched:
            continue

        # Step 2: Articulatory fallback (BRANCH)
        if ch in _ARTICULATORY_FALLBACK:
            coords.append(_ARTICULATORY_FALLBACK[ch])
            i += 1
            continue

        # Step 3: Unknown character — skip
        i += 1

    return tuple(coords)


# =============================================================================
# PUBLIC API
# =============================================================================


def encode_text(text: str) -> Tuple[int, ...]:
    """
    Encode ANY text (Sanskrit, English, German) to RAMA coordinates.

    One path for all languages. The 49 Matrix is the root.
    IAST greedy longest-match handles Sanskrit exactly and Latin letters
    naturally. Non-Sanskrit sounds (f, w, z, x, q) fall back to the
    nearest articulatory relative.

    Returns:
        Tuple of RAMA coordinates (0-48).
    """
    return _unified_encode(text)


def encode_with_detail(text: str) -> List[Dict]:
    """
    Encode text with full detail about each mapping.

    Returns list of {grapheme, rama_coord, phoneme, element, is_exact}.
    is_exact is True when the character matched the IAST index directly,
    False when it fell back to articulatory approximation.
    """
    from vibe_core.mahamantra.substrate.rama_grid import rama_to_phoneme as r2p

    details: List[Dict] = []
    text_lower = text.lower()
    i = 0

    while i < len(text_lower):
        ch = text_lower[i]

        if ch in _SKIP_CHARS or not ch.isalpha() and ch not in _IAST_INDEX:
            i += 1
            continue

        # IAST greedy longest-match
        matched = False
        for length in range(min(_MAX_IAST_LEN, len(text_lower) - i), 0, -1):
            candidate = text_lower[i:i + length]
            if candidate in _IAST_INDEX:
                coord = _IAST_INDEX[candidate]
                details.append({
                    "grapheme": candidate,
                    "rama_coord": coord,
                    "phoneme": r2p(coord),
                    "element": ELEMENT_NAMES[COORD_ELEMENT[coord]],
                    "is_exact": True,
                })
                i += length
                matched = True
                break

        if matched:
            continue

        # Articulatory fallback
        if ch in _ARTICULATORY_FALLBACK:
            coord = _ARTICULATORY_FALLBACK[ch]
            details.append({
                "grapheme": ch,
                "rama_coord": coord,
                "phoneme": r2p(coord),
                "element": ELEMENT_NAMES[COORD_ELEMENT[coord]],
                "is_exact": False,
            })
            i += 1
            continue

        i += 1

    return details


def text_to_words(
    text: str,
    seed: int = 0,
    preset: str = "quantum",
) -> "SeedResult":
    """
    THE FULL PIPELINE: Any text → RAMA coords → Synth → Resonant words.

    This is the top-level entry point for the MahaLLM.
    One path for all languages — unified encoding through the 49 Matrix.

    Args:
        text: Any text (Sanskrit, English, German)
        seed: Starting seed for the synth
        preset: Synth preset

    Returns:
        SeedResult with resonant words and meanings.
    """
    from vibe_core.mahamantra.adapters.synth import create_synth
    from vibe_core.mahamantra.substrate.seed_to_words import CoordResult, SeedResult

    coords = encode_text(text)
    if not coords:
        return SeedResult(seed=seed, preset=preset, coords=(), attractor=None)

    synth = create_synth(preset=preset)
    cycle = synth.spell_cycle(tuple(coords), seed)

    coord_results = []
    for i, step in enumerate(cycle.steps):
        rama_coord = step.output_value % VARNAMALA_TOTAL
        coord_results.append(CoordResult(
            step=i,
            synth_value=step.output_value,
            rama_coord=rama_coord,
        ))

    return SeedResult(
        seed=seed,
        preset=preset,
        coords=tuple(coord_results),
        attractor=cycle.final_value % VARNAMALA_TOTAL,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "detect_language",
    "encode_text",
    "encode_with_detail",
    "text_to_words",
]
