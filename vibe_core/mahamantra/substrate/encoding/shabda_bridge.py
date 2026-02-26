"""
SHABDA BRIDGE — Acoustic Signature Layer from Prabhupada's Japa
================================================================

"śabda-brahma" — Transcendental Sound is the ultimate reality.

Maps real acoustic features from Srila Prabhupada's japa recording
to the existing RAMA coordinate / VibrationSignature infrastructure.

DATA (precomputed, data/shabda_bridge.json, ~10 KB):
    - "syllables": {syllable: {acoustic signature as integers}}
    - "segments": [{per-onset spectral features mapped to RAMA coords}]
    - "harmonic_series": VibrationID integers for each harmonic
    - "mahamantra_coords": canonical RAMA coords for hare/kṛṣṇa/rāma

RUNTIME (zero external dependencies):
    1. Load bridge data → integer signatures (once, ~0.5ms)
    2. acoustic_signature(syllable) → pre-baked signature dict
    3. acoustic_score(text, packed_hex) → [0, 1] similarity to Mahamantra
    4. vibration_alignment(vib_id) → [0, 1] proximity to Prabhupada's harmonics

NO NUMPY. NO SCIPY. PURE PYTHON + JSON + SEED CONSTANTS.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Final, FrozenSet, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_RAMA,
    SEVEN,
    TRINITY,
)

# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# DATA
# =============================================================================

from vibe_core.mahamantra.substrate._paths import DATA_DIR

_DATA_PATH: Final[Path] = DATA_DIR / "shabda_bridge.json"

# Loaded state (lazily initialized)
_meta: Optional[Dict] = None
_syllable_data: Optional[Dict[str, dict]] = None
_segment_data: Optional[List[dict]] = None
_harmonic_vib_ids: Optional[Tuple[int, ...]] = None
_mahamantra_coords: Optional[Dict[str, Tuple[int, ...]]] = None
_mahamantra_coord_set: Optional[FrozenSet[int]] = None
_mahamantra_element_hist: Optional[Tuple[int, ...]] = None


def _ensure_loaded() -> None:
    """Load bridge data. No external deps. Pure JSON."""
    global _meta, _syllable_data, _segment_data, _harmonic_vib_ids
    global _mahamantra_coords, _mahamantra_coord_set, _mahamantra_element_hist

    if _syllable_data is not None:
        return

    if not _DATA_PATH.exists():
        _meta = {}
        _syllable_data = {}
        _segment_data = []
        _harmonic_vib_ids = ()
        _mahamantra_coords = {}
        _mahamantra_coord_set = frozenset()
        _mahamantra_element_hist = (0,) * PANCHA
        return

    with open(_DATA_PATH) as f:
        raw = json.load(f)

    _meta = raw.get("meta", {})
    _syllable_data = raw.get("syllables", {})
    _segment_data = raw.get("segments", [])
    _harmonic_vib_ids = tuple(raw.get("harmonic_series", {}).get("vibration_ids", []))

    mc = raw.get("mahamantra_coords", {})
    _mahamantra_coords = {k: tuple(v) for k, v in mc.items()}

    # Build flat set of all Mahamantra RAMA coordinates
    all_coords: set = set()
    for coords in _mahamantra_coords.values():
        all_coords.update(coords)
    _mahamantra_coord_set = frozenset(all_coords)

    # Pre-baked aggregate element histogram
    agg = raw.get("aggregate", {})
    _mahamantra_element_hist = tuple(agg.get("element_histogram", [0] * PANCHA))


# =============================================================================
# LOOKUPS
# =============================================================================


def acoustic_signature(syllable: str) -> Optional[dict]:
    """Get pre-baked acoustic signature for a Mahamantra syllable.

    Returns dict with: rama_coords, articulation, voicing, centroid_hz_x10,
    f0_hz_x10, rms_x1000, harmonics_x1000, element_walk, element_histogram.

    Returns None if syllable not found.
    """
    _ensure_loaded()
    assert _syllable_data is not None
    return _syllable_data.get(syllable)


def segment_at(index: int) -> Optional[dict]:
    """Get pre-baked segment data at a given index (0-based)."""
    _ensure_loaded()
    assert _segment_data is not None
    if 0 <= index < len(_segment_data):
        return _segment_data[index]
    return None


def get_meta() -> Dict:
    """Get recording metadata."""
    _ensure_loaded()
    assert _meta is not None
    return _meta


# =============================================================================
# SCORING
# =============================================================================


def _word_rama_coords(packed_hex: str) -> Tuple[int, ...]:
    """Get RAMA coordinates for a Gita word via varnamala_codec.

    Lazy import to avoid circular deps at module load.
    """
    try:
        from vibe_core.mahamantra.substrate.encoding.varnamala_codec import encode

        # packed_hex → word text → RAMA coords
        from vibe_core.mahamantra.substrate.semantic_index import get_index

        idx = get_index()
        idx._ensure_loaded()
        word = idx._hex_to_word.get(packed_hex)
        if word and hasattr(word, "coords") and word.coords:
            return tuple(word.coords)
        # Fallback: try to decode packed_hex as word text
        if word and hasattr(word, "sanskrit"):
            return encode(word.sanskrit)
    except Exception:
        pass
    return ()


@lru_cache(maxsize=256)
def _word_element_histogram(coords_key: Tuple[int, ...]) -> Tuple[int, ...]:
    """Compute element histogram for RAMA coordinates."""
    if not coords_key:
        return (0,) * PANCHA

    try:
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
            COORD_ELEMENT,
        )

        hist = [0] * PANCHA
        for c in coords_key:
            if 0 <= c < POSITION_SUM_RAMA:
                hist[COORD_ELEMENT[c]] += 1
        return tuple(hist)
    except Exception:
        return (0,) * PANCHA


def acoustic_score(text: str, packed_hex: str) -> float:
    """Score how acoustically close a Gita word is to the Mahamantra.

    Three layers (highest wins):
        Layer 1 — COORD:   RAMA coordinate overlap with Mahamantra phonemes → [0, 1.0]
        Layer 2 — ELEMENT: Element walk similarity to Mahamantra → [0, 0.7]
        Layer 3 — VARGA:   Varga distribution similarity → [0, 0.4]

    Returns: score in [0.0, 1.0].
    """
    _ensure_loaded()
    assert _mahamantra_coord_set is not None
    assert _mahamantra_element_hist is not None

    if not packed_hex:
        return 0.0

    word_coords = _word_rama_coords(packed_hex)
    if not word_coords:
        return 0.0

    word_coord_set = frozenset(word_coords)

    # Layer 1: COORD — RAMA coordinate overlap with Mahamantra
    overlap = word_coord_set & _mahamantra_coord_set
    if overlap:
        score = len(overlap) / len(word_coord_set)
        return min(1.0, score)

    # Layer 2: ELEMENT — Element histogram cosine similarity
    word_hist = _word_element_histogram(word_coords)
    mahamantra_hist = _mahamantra_element_hist

    # Integer cosine: dot / (norm_a * norm_b)
    dot = sum(a * b for a, b in zip(word_hist, mahamantra_hist))
    norm_a_sq = sum(a * a for a in word_hist)
    norm_b_sq = sum(b * b for b in mahamantra_hist)

    if dot > 0 and norm_a_sq > 0 and norm_b_sq > 0:
        # Approximate cosine using integer math
        # cos = dot / sqrt(norm_a_sq * norm_b_sq)
        # Scale to [0, 0.7]
        denom_sq = norm_a_sq * norm_b_sq
        # Integer sqrt approximation (Newton's method, 3 iterations)
        x = denom_sq
        for _ in range(TRINITY):
            if x > 0:
                x = (x + denom_sq // x) // 2
        if x > 0:
            cosine_x1000 = dot * 1000 // x
            if cosine_x1000 > 100:  # > 0.1 threshold
                return min(0.7, cosine_x1000 / 1000 * 0.7)

    # Layer 3: VARGA — Check if word has similar varga distribution
    try:
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_VARGA

        word_varga = [0, 0, 0]  # H(svara+shesha), K(sparsha), R(antastha)
        for c in word_coords:
            if 0 <= c < POSITION_SUM_RAMA:
                v = COORD_VARGA[c]
                if v < TRINITY:
                    word_varga[v] += 1

        # Compare to Mahamantra varga (loaded from aggregate)
        assert _syllable_data is not None
        total_word = sum(word_varga) or 1
        total_mantra = 0
        mantra_varga = [0, 0, 0]
        for syl_data in _syllable_data.values():
            coords = syl_data.get("rama_coords", [])
            count = syl_data.get("onset_count", 1)
            for c in coords:
                if 0 <= c < POSITION_SUM_RAMA:
                    v = COORD_VARGA[c]
                    if v < TRINITY:
                        mantra_varga[v] += count
                        total_mantra += count

        if total_mantra > 0:
            # Similarity: 1 - normalized L1 distance
            dist = sum(abs(word_varga[i] / total_word - mantra_varga[i] / total_mantra) for i in range(TRINITY))
            sim = max(0.0, 1.0 - dist)
            if sim > 0.2:
                return min(0.4, sim * 0.4)
    except Exception:
        pass

    return 0.0


def acoustic_scores_batch(
    text: str,
    packed_hexes: Sequence[str],
) -> List[float]:
    """Score multiple Gita words against the Mahamantra acoustic profile."""
    _ensure_loaded()
    return [acoustic_score(text, phex) for phex in packed_hexes]


# =============================================================================
# VIBRATION ALIGNMENT
# =============================================================================


def vibration_alignment(vibration_id: int) -> float:
    """How close is a VibrationID to Prabhupada's harmonic series?

    Returns [0, 1]:
        1.0 if vibration_id is an exact harmonic
        Decays by 1/distance otherwise
    """
    _ensure_loaded()
    assert _harmonic_vib_ids is not None

    if not _harmonic_vib_ids:
        return 0.0

    # Exact match with any harmonic
    if vibration_id in _harmonic_vib_ids:
        # Higher harmonics get slightly lower score
        idx = _harmonic_vib_ids.index(vibration_id)
        return max(0.5, 1.0 - idx * 0.06)

    # Distance to nearest harmonic
    min_dist = min(abs(vibration_id - h) for h in _harmonic_vib_ids)

    if min_dist == 0:
        return 1.0
    # Inverse distance, scaled by SEVEN
    return min(0.5, SEVEN / (SEVEN + min_dist))


# =============================================================================
# DIAGNOSTIC
# =============================================================================


def diagnose(top_n: int = 10) -> None:
    """Print acoustic bridge analysis for debugging."""
    _ensure_loaded()
    assert _meta is not None
    assert _syllable_data is not None
    assert _segment_data is not None
    assert _harmonic_vib_ids is not None

    print("SHABDA BRIDGE — Prabhupada Acoustic Signatures")
    print("=" * 55)
    print(f"Source: {_meta.get('source', '?')}")
    print(f"F0: {_meta.get('fundamental_hz_x10', 0) / 10:.1f} Hz (mean)")
    print(f"F0: {_meta.get('median_hz_x10', 0) / 10:.1f} Hz (median)")
    print(f"VibID: {_meta.get('vibration_id', 0)} (POSITION_SUM_RAMA={POSITION_SUM_RAMA})")
    print(f"Segments: {_meta.get('n_segments', 0)}")
    print(f"Duration: {_meta.get('duration_ms', 0)}ms")
    print()

    print("Syllable Signatures:")
    print(f"  {'Syl':5s} {'RAMA':>10s} {'Art':>3s} {'Voi':>3s} {'F0':>7s} {'Cent':>7s} {'RMS':>5s} {'N':>3s}")
    print("  " + "─" * 50)
    for syl, data in _syllable_data.items():
        print(f"  {syl:5s} {str(data.get('rama_coords', '')):>10s} "
              f"{data.get('articulation', -1):3d} {data.get('voicing', -1):3d} "
              f"{data.get('f0_hz_x10', 0) / 10:6.1f}Hz "
              f"{data.get('centroid_hz_x10', 0) / 10:6.0f}Hz "
              f"{data.get('rms_x1000', 0) / 1000:.3f} "
              f"{data.get('onset_count', 0):3d}")

    print(f"\nHarmonic Series (VibIDs): {list(_harmonic_vib_ids)}")

    print(f"\nSegment Timeline:")
    for seg in _segment_data[:top_n]:
        print(f"  [{seg.get('onset_ms', 0):5d}ms] {seg.get('syllable', '?'):5s} "
              f"F0={seg.get('f0_hz_x10', 0) / 10:.0f}Hz "
              f"VibID={seg.get('vibration_id', 0)}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "acoustic_score",
    "acoustic_scores_batch",
    "acoustic_signature",
    "diagnose",
    "get_meta",
    "segment_at",
    "vibration_alignment",
]
