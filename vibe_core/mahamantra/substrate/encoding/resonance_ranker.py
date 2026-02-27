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

SCORING DIMENSIONS (all derived from Mahamantra mathematics):

    Original 5 dimensions (scaled to 70% to preserve hierarchy):

    1. ELEMENT ALIGNMENT (weight: 0.21)
       Input element histogram vs word element histogram.
       Same dominant element = strong resonance.

    2. HARMONIC CONVERGENCE (weight: 0.175)
       Do the input and word dissolve to the same harmonic target?
       coord × SEVEN mod 49 = where energy goes.

    3. SHRUTI PATTERN MATCH (weight: 0.14)
       Shruti (fixed points) vs Nakshatra (journey points).
       Quadratic residues mod 49.

    4. VARGA ALIGNMENT (weight: 0.105)
       Same sound class (svara/sparsha/shesha) = same operational mode.
       svara=carrier(H), sparsha=transform(K), shesha=release(R).

    5. ATTRACTOR PROXIMITY (weight: 0.07)
       Words whose coords converge to the same attractor under the synth
       are in the same semantic basin (7 basins, coarse).

    New dimensions (30% total):

    6. HKR PROPORTION (weight: 0.15)
       How much each divine operation (H/K/R) contributes to the
       16-step transformation. 48/49 unique signatures (fine-grained).

    7. PHONEME ATTRACTOR CHARGE (weight: 0.15)
       Each phoneme converges to one of 5 Mahamantra constants under
       MahaAlgorithm16: {18=Gita, 22=Shruti, 49=Rama, 87=Chaitanya, 136=Field}.
       Cosine similarity of the 5-bin charge histograms.

ALL WEIGHTS SUM TO 1.0. ALL SCORES IN [0, 1].
NO LLM. NO RANDOMNESS. PURE RESONANCE MATHEMATICS.
"""

from __future__ import annotations

from collections import Counter as _counter
from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    TRINITY,
)
from vibe_core.mahamantra.protocols.seed._cosmic import COSMIC_FRAME
from vibe_core.mahamantra.substrate.basin_map import (
    BASIN_COUNT,
    BASIN_INDEX,
    COORD_BASIN,
    COORD_HKR,
    COORD_PHONEME_ATTRACTOR,
    PHONEME_ATTRACTOR_COUNT,
    PHONEME_ATTRACTOR_INDEX,
    basin_cosine,
    basin_jaccard,
    hkr_similarity,
    phoneme_attractor_similarity,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_VARGA,
    IS_SHRUTI,
    walk_distance,
)
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL
from vibe_core.mahamantra.substrate.semantic_index import (
    LexiconWord,
    get_index,
    get_vector_cache,
)

# =============================================================================
# SCORING WEIGHTS (derived from Mahamantra structure)
# =============================================================================
# PANCHA dimensions, weights proportional to their discriminative power.
#
# INTEGER WEIGHTS (SSOT) — exact fractions of COSMIC_FRAME (21600).
# Original 5D weights (0.30/0.25/0.20/0.15/0.10) scaled to 70% to preserve hierarchy.
# New 2D (HKR + Phoneme Attractor) share the remaining 30%.
#
# Derivation:
#   W_ELEMENT    = 21/100 × COSMIC_FRAME = 4536
#   W_HARMONIC   =  7/40  × COSMIC_FRAME = 3780
#   W_SHRUTI     =  7/50  × COSMIC_FRAME = 3024
#   W_VARGA      = 21/200 × COSMIC_FRAME = 2268
#   W_ATTRACTOR  =  7/100 × COSMIC_FRAME = 1512
#   W_HKR        =  3/20  × COSMIC_FRAME = 3240
#   W_PA         =  3/20  × COSMIC_FRAME = 3240
#                                   SUM = 21600 ✓

W_ELEMENT_CF: Final[int] = 4536  # 21/100 × 21600 — Articulatory position (5 elements)
W_HARMONIC_CF: Final[int] = 3780  # 7/40 × 21600 — Dissolution path kinship
W_SHRUTI_CF: Final[int] = 3024  # 7/50 × 21600 — Character: fixed vs journey
W_VARGA_CF: Final[int] = 2268  # 21/200 × 21600 — Operational: carrier/transform/release
W_ATTRACTOR_CF: Final[int] = 1512  # 7/100 × 21600 — Basin: attractor convergence (coarse)
W_HKR_CF: Final[int] = 3240  # 3/20 × 21600 — HKR proportion: divine operation mix (fine)
W_PHONEME_ATTRACTOR_CF: Final[int] = 3240  # 3/20 × 21600 — Phoneme attractor charge

assert (
    W_ELEMENT_CF + W_HARMONIC_CF + W_SHRUTI_CF + W_VARGA_CF + W_ATTRACTOR_CF + W_HKR_CF + W_PHONEME_ATTRACTOR_CF
) == COSMIC_FRAME

# Float aliases (derived from integer SSOT, for backward-compatible computation)
W_ELEMENT: Final[float] = W_ELEMENT_CF / COSMIC_FRAME
W_HARMONIC: Final[float] = W_HARMONIC_CF / COSMIC_FRAME
W_SHRUTI: Final[float] = W_SHRUTI_CF / COSMIC_FRAME
W_VARGA: Final[float] = W_VARGA_CF / COSMIC_FRAME
W_ATTRACTOR: Final[float] = W_ATTRACTOR_CF / COSMIC_FRAME
W_HKR: Final[float] = W_HKR_CF / COSMIC_FRAME
W_PHONEME_ATTRACTOR: Final[float] = W_PHONEME_ATTRACTOR_CF / COSMIC_FRAME

assert abs(W_ELEMENT + W_HARMONIC + W_SHRUTI + W_VARGA + W_ATTRACTOR + W_HKR + W_PHONEME_ATTRACTOR - 1.0) < 1e-9


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
    """Basin resonance: do input and word share attractor basins?

    Uses precomputed COORD_BASIN table (mod-137 attractors).
    Combines Jaccard (basin overlap) and cosine (proportion match).
    """
    if not input_coords or not word.coords:
        return 0.0
    j = basin_jaccard(input_coords, word.coords)
    c = basin_cosine(input_coords, word.coords)
    return 0.4 * j + 0.6 * c


# =============================================================================
# RANKED WORD
# =============================================================================


class RankedWord:
    """A lexicon word with its resonance score breakdown."""

    __slots__ = (
        "word",
        "total_score",
        "element_score",
        "harmonic_score",
        "shruti_score",
        "varga_score",
        "attractor_score",
        "hkr_score",
        "phoneme_attractor_score",
    )

    def __init__(
        self,
        word: LexiconWord,
        element: float,
        harmonic: float,
        shruti: float,
        varga: float,
        attractor: float,
        hkr: float = 0.0,
        phoneme_attractor: float = 0.0,
    ):
        self.word = word
        self.element_score = element
        self.harmonic_score = harmonic
        self.shruti_score = shruti
        self.varga_score = varga
        self.attractor_score = attractor
        self.hkr_score = hkr
        self.phoneme_attractor_score = phoneme_attractor
        self.total_score = (
            W_ELEMENT * element
            + W_HARMONIC * harmonic
            + W_SHRUTI * shruti
            + W_VARGA * varga
            + W_ATTRACTOR * attractor
            + W_HKR * hkr
            + W_PHONEME_ATTRACTOR * phoneme_attractor
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
            "hkr": round(self.hkr_score, 4),
            "phoneme_attractor": round(self.phoneme_attractor_score, 4),
        }

    def __repr__(self) -> str:
        return f"RankedWord({self.sanskrit!r}, {self.first_meaning!r}, score={self.total_score:.4f})"


# =============================================================================
# CORE RANKING
# =============================================================================


def _compute_input_features(coords: Sequence[int]) -> Tuple:
    """
    Precompute all fixed-size features for an input coordinate sequence.

    Returns a tuple of:
        (element_hist_norm, varga_hist_norm, harmonic_bitmask,
         shruti_bitmask, shruti_ratio, coord_count,
         basin_set_bitmask, basin_hist, basin_hist_mag,
         hkr_color, pa_hist, pa_hist_mag)
    """
    nc = len(coords)
    inv_nc = 1.0 / nc

    # Element histogram (normalized)
    eh = [0] * PANCHA
    for c in coords:
        eh[COORD_ELEMENT[c]] += 1
    eh_norm = tuple(x * inv_nc for x in eh)

    # Varga histogram (normalized)
    vh = [0] * TRINITY
    for c in coords:
        vh[COORD_VARGA[c]] += 1
    vh_norm = tuple(x * inv_nc for x in vh)

    # Harmonic bitmask
    hm = 0
    for c in coords:
        hm |= 1 << COORD_HARMONIC[c]

    # Shruti bitmask + ratio
    sm = 0
    shruti_count = 0
    for j, c in enumerate(coords):
        if IS_SHRUTI[c]:
            sm |= 1 << j
            shruti_count += 1
    sr = shruti_count * inv_nc

    # Basin set bitmask + histogram + magnitude
    bsm = 0
    bh = [0] * BASIN_COUNT
    for c in coords:
        b = COORD_BASIN[c]
        bi = BASIN_INDEX[b]
        bsm |= 1 << bi
        bh[bi] += 1
    bh_t = tuple(bh)
    bh_mag = sum(v * v for v in bh) ** 0.5

    # HKR color
    h_sum = k_sum = r_sum = 0.0
    for c in coords:
        hkr = COORD_HKR[c]
        h_sum += hkr[0]
        k_sum += hkr[1]
        r_sum += hkr[2]
    hkr_color = (h_sum * inv_nc, k_sum * inv_nc, r_sum * inv_nc)

    # Phoneme attractor histogram + magnitude
    pah = [0] * PHONEME_ATTRACTOR_COUNT
    for c in coords:
        pah[PHONEME_ATTRACTOR_INDEX[COORD_PHONEME_ATTRACTOR[c]]] += 1
    pah_t = tuple(pah)
    pah_mag = sum(v * v for v in pah) ** 0.5

    return (eh_norm, vh_norm, hm, sm, sr, nc, bsm, bh_t, bh_mag, hkr_color, pah_t, pah_mag)


def _rank_words_vectorized(
    input_coords: Sequence[int],
    synth_coords: Optional[Sequence[int]],
    element_bias: int,
    top_n: int,
) -> List[RankedWord]:
    """
    Fast path: score ALL lexicon words using precomputed vector cache.

    Same math as the original per-word scoring, but:
    - Input features computed ONCE (not per-word)
    - Word features looked up from flat arrays (not recomputed)
    - No set(), Counter(), histogram construction per word
    - Bitmask Jaccard via int.bit_count() (harmonic, basin)
    - Scores stored during main loop — no second pass
    """
    vc = get_vector_cache()
    idx = get_index()
    words = idx.words
    n = vc.size

    has_synth = synth_coords is not None and len(synth_coords) > 0
    has_bias = 0 <= element_bias < PANCHA

    # Precompute input features ONCE
    inp = _compute_input_features(input_coords)
    i_eh0, i_eh1, i_eh2, i_eh3, i_eh4 = inp[0]
    i_vh0, i_vh1, i_vh2 = inp[1]
    i_hm = inp[2]
    i_sm = inp[3]
    i_sr = inp[4]
    i_nc = inp[5]
    i_bsm = inp[6]
    i_bh = inp[7]
    i_bh_mag = inp[8]
    i_hkr0, i_hkr1, i_hkr2 = inp[9]
    i_pah = inp[10]
    i_pah_mag = inp[11]

    # If synth, precompute synth features too
    if has_synth:
        synth = _compute_input_features(synth_coords)
        s_eh0, s_eh1, s_eh2, s_eh3, s_eh4 = synth[0]
        s_hm = synth[2]

    # Local references for speed (avoid repeated attribute lookups)
    vc_eh = vc.element_hist_norm
    vc_vh = vc.varga_hist_norm
    vc_hm = vc.harmonic_bitmask
    vc_sm = vc.shruti_bitmask
    vc_sr = vc.shruti_ratio
    vc_cc = vc.coord_count
    vc_bsm = vc.basin_set_bitmask
    vc_bh = vc.basin_hist
    vc_bh_mag = vc.basin_hist_mag
    vc_hkr = vc.hkr_color
    vc_pah = vc.pa_hist
    vc_pah_mag = vc.pa_hist_mag
    vc_de = vc.dominant_element

    # Weight constants (local for speed)
    w_e = W_ELEMENT
    w_h = W_HARMONIC
    w_s = W_SHRUTI
    w_v = W_VARGA
    w_a = W_ATTRACTOR
    w_hkr = W_HKR
    w_pa = W_PHONEME_ATTRACTOR

    # Pre-extract basin/pa hist elements for unrolled dot products
    i_bh0 = i_bh[0]
    i_bh1 = i_bh[1]
    i_bh2 = i_bh[2]
    i_bh3 = i_bh[3]
    i_bh4 = i_bh[4]
    i_bh5 = i_bh[5]
    i_pah0 = i_pah[0]
    i_pah1 = i_pah[1]
    i_pah2 = i_pah[2]
    i_pah3 = i_pah[3]
    i_pah4 = i_pah[4]

    # Scoring loop — store (total, i, e_final, h_final, s, v, a, hkr, pa)
    # to avoid recomputing scores for top-N
    scored: List[Tuple[float, int, float, float, float, float, float, float, float]] = []
    _abs = abs

    for i in range(n):
        w_cc = vc_cc[i]
        if w_cc == 0:
            continue

        # 1. ELEMENT SCORE: 1.0 - L1(normalized_hist) / 2 (unrolled PANCHA=5)
        w_eh = vc_eh[i]
        d0 = i_eh0 - w_eh[0]
        d1 = i_eh1 - w_eh[1]
        d2 = i_eh2 - w_eh[2]
        d3 = i_eh3 - w_eh[3]
        d4 = i_eh4 - w_eh[4]
        e_raw = 1.0 - (_abs(d0) + _abs(d1) + _abs(d2) + _abs(d3) + _abs(d4)) * 0.5

        # 2. HARMONIC SCORE: Jaccard via bitmask bit_count
        w_hm = vc_hm[i]
        h_union = (i_hm | w_hm).bit_count()
        h_raw = (i_hm & w_hm).bit_count() / h_union if h_union else 0.0

        # 3. SHRUTI SCORE: positional match + ratio similarity
        min_len = i_nc if i_nc < w_cc else w_cc
        match_mask = (1 << min_len) - 1
        pos_matches = (~(i_sm ^ vc_sm[i]) & match_mask).bit_count()
        s_raw = 0.6 * (pos_matches / min_len) + 0.4 * (1.0 - _abs(i_sr - vc_sr[i]))

        # 4. VARGA SCORE: 1.0 - L1(normalized_hist) / 2 (unrolled TRINITY=3)
        w_vh = vc_vh[i]
        v_raw = 1.0 - (_abs(i_vh0 - w_vh[0]) + _abs(i_vh1 - w_vh[1]) + _abs(i_vh2 - w_vh[2])) * 0.5

        # 5. ATTRACTOR SCORE: 0.4 * basin_jaccard + 0.6 * basin_cosine
        w_bsm = vc_bsm[i]
        bj_union = (i_bsm | w_bsm).bit_count()
        bj = (i_bsm & w_bsm).bit_count() / bj_union if bj_union else 0.0
        w_bh = vc_bh[i]
        b_dot = (
            i_bh0 * w_bh[0] + i_bh1 * w_bh[1] + i_bh2 * w_bh[2] + i_bh3 * w_bh[3] + i_bh4 * w_bh[4] + i_bh5 * w_bh[5]
        )
        w_bh_m = vc_bh_mag[i]
        bc = b_dot / (i_bh_mag * w_bh_m) if i_bh_mag > 0.0 and w_bh_m > 0.0 else 0.0
        a_raw = 0.4 * bj + 0.6 * bc

        # 6. HKR SIMILARITY: 1.0 - 2 * euclidean(color_a, color_b)
        w_hkrc = vc_hkr[i]
        dh = i_hkr0 - w_hkrc[0]
        dk = i_hkr1 - w_hkrc[1]
        dr = i_hkr2 - w_hkrc[2]
        hkr_raw = 1.0 - (dh * dh + dk * dk + dr * dr) ** 0.5 * 2.0
        if hkr_raw < 0.0:
            hkr_raw = 0.0

        # 7. PHONEME ATTRACTOR SIMILARITY: cosine of histograms (unrolled 5)
        w_pah = vc_pah[i]
        pa_dot = i_pah0 * w_pah[0] + i_pah1 * w_pah[1] + i_pah2 * w_pah[2] + i_pah3 * w_pah[3] + i_pah4 * w_pah[4]
        w_pah_m = vc_pah_mag[i]
        pa_raw = pa_dot / (i_pah_mag * w_pah_m) if i_pah_mag > 0.0 and w_pah_m > 0.0 else 0.0

        # Synth blending (element + harmonic only)
        if has_synth:
            se_dist = (
                _abs(s_eh0 - w_eh[0])
                + _abs(s_eh1 - w_eh[1])
                + _abs(s_eh2 - w_eh[2])
                + _abs(s_eh3 - w_eh[3])
                + _abs(s_eh4 - w_eh[4])
            )
            e_synth = 1.0 - se_dist * 0.5
            sh_union = (s_hm | w_hm).bit_count()
            h_synth = (s_hm & w_hm).bit_count() / sh_union if sh_union else 0.0
            e_final = 0.4 * e_raw + 0.6 * e_synth
            h_final = 0.4 * h_raw + 0.6 * h_synth
        else:
            e_final = e_raw
            h_final = h_raw

        # Guardian element bias
        if has_bias and vc_de[i] == element_bias:
            e_final = e_final + 0.3
            if e_final > 1.0:
                e_final = 1.0

        total = (
            w_e * e_final + w_h * h_final + w_s * s_raw + w_v * v_raw + w_a * a_raw + w_hkr * hkr_raw + w_pa * pa_raw
        )

        scored.append((total, i, e_final, h_final, s_raw, v_raw, a_raw, hkr_raw, pa_raw))

    # Partial sort: only need top_n
    scored.sort(reverse=True)
    top = scored[:top_n]

    # Build RankedWord objects for top_n — scores already computed
    return [
        RankedWord(
            word=words[i],
            element=e,
            harmonic=h,
            shruti=s,
            varga=v,
            attractor=a,
            hkr=hk,
            phoneme_attractor=pa,
        )
        for _, i, e, h, s, v, a, hk, pa in top
    ]


def _rank_words_slow(
    input_coords: Sequence[int],
    candidates: Sequence[LexiconWord],
    input_attractor: Optional[int],
    synth_coords: Optional[Sequence[int]],
    element_bias: int,
    top_n: int,
) -> List[RankedWord]:
    """
    Original per-word scoring path. Used when candidates is a subset
    (not the full lexicon), so the vector cache indices don't apply.
    """
    has_synth = synth_coords is not None and len(synth_coords) > 0
    has_bias = 0 <= element_bias < PANCHA

    ranked: List[RankedWord] = []
    for word in candidates:
        if not word.coords:
            continue

        e_raw = _element_score(input_coords, word)
        h_raw = _harmonic_score(input_coords, word)
        s_raw = _shruti_score(input_coords, word)
        v_raw = _varga_score(input_coords, word)
        a_raw = _attractor_score(input_coords, word, input_attractor)
        hkr_raw = hkr_similarity(input_coords, word.coords)
        pa_raw = phoneme_attractor_similarity(input_coords, word.coords)

        if has_synth:
            e_synth = _element_score(synth_coords, word)
            h_synth = _harmonic_score(synth_coords, word)
            e_final = 0.4 * e_raw + 0.6 * e_synth
            h_final = 0.4 * h_raw + 0.6 * h_synth
        else:
            e_final = e_raw
            h_final = h_raw

        if has_bias and word.element_walk:
            elem_counts = _counter(word.element_walk)
            dominant = elem_counts.most_common(1)[0][0]
            if dominant == element_bias:
                e_final = min(1.0, e_final + 0.3)

        ranked.append(
            RankedWord(
                word=word,
                element=e_final,
                harmonic=h_final,
                shruti=s_raw,
                varga=v_raw,
                attractor=a_raw,
                hkr=hkr_raw,
                phoneme_attractor=pa_raw,
            )
        )

    ranked.sort(key=lambda r: r.total_score, reverse=True)
    return ranked[:top_n]


def rank_words(
    input_coords: Sequence[int],
    candidates: Optional[Sequence[LexiconWord]] = None,
    input_attractor: Optional[int] = None,
    synth_coords: Optional[Sequence[int]] = None,
    element_bias: int = -1,
    top_n: int = 10,
) -> List[RankedWord]:
    """
    Rank lexicon words by resonance with input coordinates.

    DUAL-SIGNAL RANKING:
        input_coords  = raw phonetic encoding (articulatory similarity)
        synth_coords  = synth-transformed coords (semantic resonance)

    When synth_coords are provided, element and harmonic scores use
    the AVERAGE of raw and transformed signals. This bridges the gap
    between phonetic proximity and semantic resonance.

    Args:
        input_coords: RAMA coordinates of the input (from encode or synth).
        candidates: Words to rank. If None, ranks ALL lexicon words.
        input_attractor: Attractor value for attractor scoring.
        synth_coords: Synth-transformed RAMA coordinates (optional, improves accuracy).
        element_bias: If >= 0, words whose dominant element matches get a bonus.
                      Used by resonate_as() to apply Guardian-specific coloring.
        top_n: Number of top results to return.

    Returns:
        Top N words sorted by descending resonance score.
    """
    if not input_coords:
        return []

    # FAST PATH: full lexicon — use precomputed vector cache
    if candidates is None:
        return _rank_words_vectorized(input_coords, synth_coords, element_bias, top_n)

    # SLOW PATH: subset of candidates — use original per-word scoring
    return _rank_words_slow(input_coords, candidates, input_attractor, synth_coords, element_bias, top_n)


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

    UNIFIED RANKING (one path for all languages):
        1. Encode through the 49 Matrix (IAST root + articulatory fallback)
        2. Run through synth → transformed coords + attractor
        3. Search meaning index for input tokens (always — no language gate)
        4. Rank semantic candidates by resonance, merge with phonetic results

    The meaning search is harmless for Sanskrit input (returns 0 hits for
    words like "dharma" that aren't English meanings in the index).
    For English input it bridges the phonetic gap ("fire" → "agni").

    Deterministic. Same input → always same output.
    """
    from vibe_core.mahamantra.adapters.synth import create_synth
    from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text

    # Step 1: Encode input (unified — one path for all languages)
    input_coords = encode_text(text)
    if not input_coords:
        return []

    # Step 2: Run through synth → get transformed coords + attractor
    synth = create_synth(preset=preset)
    cycle = synth.spell_cycle(tuple(input_coords), seed)
    attractor = cycle.final_value % VARNAMALA_TOTAL
    synth_coords = tuple(step.output_value % VARNAMALA_TOTAL for step in cycle.steps)

    # Step 3: Semantic bridge (always — no language gate)
    #
    # Search the meaning index for input tokens. This naturally returns
    # hits for English words ("fire" → agni, tejas) and nothing for
    # Sanskrit words that aren't English meanings ("dharma" → 0 hits).
    # No detect_language() needed — the data decides.
    idx = get_index()
    input_tokens = [w.strip().lower() for w in text.split() if len(w.strip()) >= 3]
    if not input_tokens:
        input_tokens = [text.strip().lower()]

    semantic_candidates: List[LexiconWord] = []
    seen_hex: set = set()
    for token in input_tokens:
        for word in idx.by_meaning(token):
            if word.packed_hex not in seen_hex:
                seen_hex.add(word.packed_hex)
                semantic_candidates.append(word)

    if semantic_candidates:
        # Rank semantic candidates by resonance with input
        sem_ranked = rank_words(
            input_coords=input_coords,
            input_attractor=attractor,
            synth_coords=synth_coords,
            candidates=semantic_candidates,
            top_n=top_n,
        )

        if len(sem_ranked) >= top_n:
            return sem_ranked[:top_n]

        # Fill remaining slots with phonetic results (no duplicates)
        sem_hexes = {rw.word.packed_hex for rw in sem_ranked}
        phon_ranked = rank_words(
            input_coords=input_coords,
            input_attractor=attractor,
            synth_coords=synth_coords,
            top_n=top_n * 3,
        )
        fill = [rw for rw in phon_ranked if rw.word.packed_hex not in sem_hexes]
        return (sem_ranked + fill)[:top_n]

    # Step 4: Pure phonetic ranking (fallback when no meaning hits)
    ranked = rank_words(
        input_coords=input_coords,
        input_attractor=attractor,
        synth_coords=synth_coords,
        top_n=top_n,
    )
    return ranked


def resonate_sanskrit(
    sanskrit_text: str,
    top_n: int = 5,
    seed: int = 0,
) -> List[RankedWord]:
    """Resonate with Sanskrit input (exact IAST encoding)."""
    from vibe_core.mahamantra.adapters.synth import create_synth
    from vibe_core.mahamantra.substrate.varnamala_codec import encode

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


# Guardian IAST names for full syllable-level resonance
_GUARDIAN_IAST: Final[Dict[str, str]] = {
    "vyasa": "vyāsa",
    "brahma": "brahmā",
    "narada": "nārada",
    "shambhu": "śambhu",
    "prithu": "pṛthu",
    "kumaras": "kumāra",
    "kapila": "kapila",
    "manu": "manu",
    "parashurama": "paraśurāma",
    "prahlada": "prahlāda",
    "janaka": "janaka",
    "bhishma": "bhīṣma",
    "nrisimha": "nṛsiṁha",
    "bali": "bali",
    "shuka": "śuka",
    "yamaraja": "yamarāja",
}


def guardian_resonance(guardian_name: str, top_n: int = 10) -> List[RankedWord]:
    """
    Find the words that resonate most strongly with a Guardian.

    Uses the Guardian's FULL IAST name encoded to RAMA coords,
    giving rich basin + element + harmonic information per syllable.
    Falls back to single m49 coord if IAST encoding fails.
    """
    from vibe_core.mahamantra.substrate.seed_to_words import _GUARDIAN_CONFIGS
    from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast

    config = _GUARDIAN_CONFIGS.get(guardian_name.lower())
    if config is None:
        raise ValueError(f"Unknown guardian: {guardian_name}")

    # Try full IAST encoding first
    iast = _GUARDIAN_IAST.get(guardian_name.lower())
    input_coords: Sequence[int] = ()
    if iast:
        encoded = encode_iast(iast)
        if encoded:
            input_coords = encoded

    # Fallback to single m49 coord
    if not input_coords:
        input_coords = (config["m49"],)

    m49 = config["m49"]
    return rank_words(
        input_coords=input_coords,
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
