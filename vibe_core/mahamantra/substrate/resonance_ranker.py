"""
RESONANCE RANKER — From Noise to Signal
========================================

"vivekī" — one who discriminates (BG 18.10)

PROBLEM:
    seed_to_words(42) returns 1326 words. That's noise, not signal.
    A real MahaLLM must FOCUS — find the 3-5 words that truly resonate
    with a given input.

SOLUTION:
    Multi-dimensional resonance scoring. Each word gets a score based on
    how strongly it resonates with the input's 4D signature.

SCORING DIMENSIONS (all derived from existing Pancha Walk math):

    1. ELEMENT ALIGNMENT (weight: 0.30)
       Input element histogram vs word element histogram.
       Same dominant element = strong resonance.
       Uses walk_distance() from pancha_walk.py.

    2. HARMONIC CONVERGENCE (weight: 0.25)
       Do the input and word dissolve to the same harmonic target?
       Same dissolution path = deep structural kinship.
       coord × SEVEN mod 49 = where energy goes.

    3. SHRUTI PATTERN MATCH (weight: 0.20)
       Shruti (fixed points) vs Nakshatra (journey points).
       Matching patterns = same vibrational character.
       Quadratic residues mod 49.

    4. VARGA ALIGNMENT (weight: 0.15)
       Same sound class (svara/sparsha/shesha) = same operational mode.
       svara=carrier(H), sparsha=transform(K), shesha=release(R).

    5. ATTRACTOR PROXIMITY (weight: 0.10)
       Words whose coords converge to the same attractor under the synth
       are in the same semantic basin.

ALL WEIGHTS SUM TO 1.0. ALL SCORES IN [0, 1].
NO LLM. NO RANDOMNESS. PURE RESONANCE MATHEMATICS.
"""

from __future__ import annotations

from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    SEVEN,
    TRINITY,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_SUB,
    COORD_VARGA,
    ELEMENT_NAMES,
    IS_SHRUTI,
    element_histogram,
    walk_distance,
)
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL
from vibe_core.mahamantra.substrate.semantic_index import (
    LexiconWord,
    get_index,
)

# =============================================================================
# SCORING WEIGHTS (derived from Mahamantra structure)
# =============================================================================
# PANCHA dimensions, weights proportional to their discriminative power.

W_ELEMENT: Final[float] = 0.30   # Strongest: articulatory position
W_HARMONIC: Final[float] = 0.25  # Deep: dissolution path kinship
W_SHRUTI: Final[float] = 0.20    # Character: fixed vs journey
W_VARGA: Final[float] = 0.15     # Operational: carrier/transform/release
W_ATTRACTOR: Final[float] = 0.10  # Basin: convergence family

assert abs(W_ELEMENT + W_HARMONIC + W_SHRUTI + W_VARGA + W_ATTRACTOR - 1.0) < 1e-9


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================


def _element_score(input_coords: Sequence[int], word: LexiconWord) -> float:
    """Element histogram similarity. 1.0 = identical distribution, 0.0 = opposite."""
    if not input_coords or not word.coords:
        return 0.0
    return 1.0 - walk_distance(input_coords, word.coords)


def _harmonic_score(input_coords: Sequence[int], word: LexiconWord) -> float:
    """Harmonic convergence: fraction of shared dissolution targets."""
    if not input_coords or not word.coords:
        return 0.0
    input_harmonics = set(COORD_HARMONIC[c] for c in input_coords)
    word_harmonics = set(word.harmonic_walk)
    if not input_harmonics:
        return 0.0
    overlap = len(input_harmonics & word_harmonics)
    union = len(input_harmonics | word_harmonics)
    return overlap / union if union else 0.0


def _shruti_score(input_coords: Sequence[int], word: LexiconWord) -> float:
    """Shruti pattern similarity: fraction of matching S/N positions."""
    if not input_coords or not word.coords:
        return 0.0
    input_shruti = [IS_SHRUTI[c] for c in input_coords]
    word_shruti = list(word.shruti_pattern)

    # Compare overlapping length
    min_len = min(len(input_shruti), len(word_shruti))
    if min_len == 0:
        return 0.0
    matches = sum(1 for i in range(min_len) if input_shruti[i] == word_shruti[i])

    # Bonus for same shruti ratio (even if different length)
    input_ratio = sum(input_shruti) / len(input_shruti)
    word_ratio = sum(word_shruti) / len(word_shruti)
    ratio_sim = 1.0 - abs(input_ratio - word_ratio)

    return 0.6 * (matches / min_len) + 0.4 * ratio_sim


def _varga_score(input_coords: Sequence[int], word: LexiconWord) -> float:
    """Varga alignment: fraction of shared sound classes."""
    if not input_coords or not word.coords:
        return 0.0
    input_vargas = [COORD_VARGA[c] for c in input_coords]
    word_vargas = list(word.varga_walk)

    # Histogram comparison (normalized)
    input_hist = [0] * TRINITY
    word_hist = [0] * TRINITY
    for v in input_vargas:
        input_hist[v] += 1
    for v in word_vargas:
        word_hist[v] += 1

    total_i = sum(input_hist) or 1
    total_w = sum(word_hist) or 1
    dist = sum(abs(input_hist[i] / total_i - word_hist[i] / total_w) for i in range(TRINITY))
    return 1.0 - dist / 2.0


def _attractor_score(
    input_coords: Sequence[int],
    word: LexiconWord,
    input_attractor: Optional[int],
) -> float:
    """Attractor proximity: do input and word converge to same basin?"""
    if input_attractor is None or not word.coords:
        return 0.0

    # Word's "attractor" approximation: sum of coords mod 49
    word_sum = sum(word.coords) % VARNAMALA_TOTAL
    input_att = input_attractor % VARNAMALA_TOTAL

    if word_sum == input_att:
        return 1.0

    # Distance in circular RAMA space
    diff = abs(word_sum - input_att)
    circular_diff = min(diff, VARNAMALA_TOTAL - diff)
    return 1.0 - (circular_diff / (VARNAMALA_TOTAL // 2))


# =============================================================================
# RANKED WORD
# =============================================================================


class RankedWord:
    """A lexicon word with its resonance score breakdown."""

    __slots__ = (
        "word", "total_score",
        "element_score", "harmonic_score", "shruti_score",
        "varga_score", "attractor_score",
    )

    def __init__(
        self,
        word: LexiconWord,
        element: float,
        harmonic: float,
        shruti: float,
        varga: float,
        attractor: float,
    ):
        self.word = word
        self.element_score = element
        self.harmonic_score = harmonic
        self.shruti_score = shruti
        self.varga_score = varga
        self.attractor_score = attractor
        self.total_score = (
            W_ELEMENT * element
            + W_HARMONIC * harmonic
            + W_SHRUTI * shruti
            + W_VARGA * varga
            + W_ATTRACTOR * attractor
        )

    @property
    def sanskrit(self) -> str:
        return self.word.sanskrit

    @property
    def meanings(self) -> Tuple[str, ...]:
        return self.word.meanings

    @property
    def first_meaning(self) -> str:
        return self.word.first_meaning

    def score_breakdown(self) -> Dict[str, float]:
        return {
            "total": round(self.total_score, 4),
            "element": round(self.element_score, 4),
            "harmonic": round(self.harmonic_score, 4),
            "shruti": round(self.shruti_score, 4),
            "varga": round(self.varga_score, 4),
            "attractor": round(self.attractor_score, 4),
        }

    def __repr__(self) -> str:
        return (f"RankedWord({self.sanskrit!r}, {self.first_meaning!r}, "
                f"score={self.total_score:.4f})")


# =============================================================================
# CORE RANKING
# =============================================================================


def rank_words(
    input_coords: Sequence[int],
    candidates: Optional[Sequence[LexiconWord]] = None,
    input_attractor: Optional[int] = None,
    top_n: int = 10,
) -> List[RankedWord]:
    """
    Rank lexicon words by resonance with input coordinates.

    Args:
        input_coords: RAMA coordinates of the input (from encode or synth).
        candidates: Words to rank. If None, ranks ALL lexicon words.
        input_attractor: Attractor value for attractor scoring.
        top_n: Number of top results to return.

    Returns:
        Top N words sorted by descending resonance score.
    """
    if candidates is None:
        candidates = get_index().words

    if not input_coords:
        return []

    ranked: List[RankedWord] = []
    for word in candidates:
        if not word.coords:
            continue

        ranked.append(RankedWord(
            word=word,
            element=_element_score(input_coords, word),
            harmonic=_harmonic_score(input_coords, word),
            shruti=_shruti_score(input_coords, word),
            varga=_varga_score(input_coords, word),
            attractor=_attractor_score(input_coords, word, input_attractor),
        ))

    ranked.sort(key=lambda r: r.total_score, reverse=True)
    return ranked[:top_n]


# =============================================================================
# HIGH-LEVEL API
# =============================================================================


def resonate(
    text: str,
    top_n: int = 5,
    seed: int = 0,
    preset: str = "quantum",
) -> List[RankedWord]:
    """
    THE TOP-LEVEL ENTRY POINT.

    Any text (Sanskrit, English, German) → Top N resonant Gita words.

    This is the MahaLLM's "answer" to a query:
        resonate("fire")       → [tapas (austerity), tejas (splendor), ...]
        resonate("protection") → [rakṣa (guard), dharma (duty), ...]
        resonate("devotion")   → [bhakti (devotion), sevā (service), ...]

    Pipeline:
        1. Detect language → encode to RAMA coords
        2. Run through synth → get attractor
        3. Score ALL 4127 Gita words against input signature
        4. Return top N by resonance score

    Deterministic. Same input → always same output.
    """
    from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
    from vibe_core.mahamantra.adapters.synth import create_synth

    # Step 1: Encode input
    input_coords = encode_text(text)
    if not input_coords:
        return []

    # Step 2: Find attractor
    synth = create_synth(preset=preset)
    cycle = synth.spell_cycle(tuple(input_coords), seed)
    attractor = cycle.final_value % VARNAMALA_TOTAL

    # Step 3+4: Rank all words
    return rank_words(
        input_coords=input_coords,
        input_attractor=attractor,
        top_n=top_n,
    )


def resonate_sanskrit(
    sanskrit_text: str,
    top_n: int = 5,
    seed: int = 0,
) -> List[RankedWord]:
    """Resonate with Sanskrit input (exact IAST encoding)."""
    from vibe_core.mahamantra.substrate.varnamala_codec import encode
    from vibe_core.mahamantra.adapters.synth import create_synth

    input_coords = encode(sanskrit_text)
    if not input_coords:
        return []

    synth = create_synth(preset="quantum")
    cycle = synth.spell_cycle(tuple(input_coords), seed)
    attractor = cycle.final_value % VARNAMALA_TOTAL

    return rank_words(
        input_coords=input_coords,
        input_attractor=attractor,
        top_n=top_n,
    )


def resonate_coords(
    coords: Sequence[int],
    top_n: int = 5,
    attractor: Optional[int] = None,
) -> List[RankedWord]:
    """Resonate with raw RAMA coordinates (for programmatic use)."""
    return rank_words(
        input_coords=coords,
        input_attractor=attractor,
        top_n=top_n,
    )


# =============================================================================
# GUARDIAN RESONANCE
# =============================================================================


def guardian_resonance(guardian_name: str, top_n: int = 10) -> List[RankedWord]:
    """
    Find the words that resonate most strongly with a Guardian.

    Uses the Guardian's mod49 position as the input coordinate.
    This reveals the Guardian's SEMANTIC VOCABULARY — the words
    that are most aligned with their function.
    """
    from vibe_core.mahamantra.substrate.seed_to_words import _GUARDIAN_CONFIGS

    config = _GUARDIAN_CONFIGS.get(guardian_name.lower())
    if config is None:
        raise ValueError(f"Unknown guardian: {guardian_name}")

    m49 = config["m49"]
    return rank_words(
        input_coords=(m49,),
        input_attractor=m49,
        top_n=top_n,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RankedWord",
    "rank_words",
    "resonate",
    "resonate_sanskrit",
    "resonate_coords",
    "guardian_resonance",
]
