"""
SHABDA BRIDGE — Prabhupada's Japa as Continuous Acoustic Stream
================================================================

"śabda-brahma" — Transcendental Sound is the ultimate reality.

v2: Continuous frame-by-frame stream from Srila Prabhupada's japa recording.
638 frames × uint32 = 2,552 bytes. Fits in Antaranga (16 KB).

Each frame (10ms) is packed as:
    Bits  0-7  (8): RMS energy (0-255)
    Bits  8-10 (3): Varga (articulation point, 0-4)
    Bits 11-22 (12): F0 (fundamental frequency × 10, 0-4095)
    Bits 23-31 (9): Centroid (spectral centroid / 100, 0-511)

CORE FUNCTION:
    prabhupada_salt(syllable_position) → uint32
    When the system processes Mahamantra position N (0-31),
    this returns Prabhupada's ACTUAL acoustic measurement for that exact position.

NO NUMPY. NO SCIPY. PURE PYTHON + JSON + SEED CONSTANTS.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Final, FrozenSet, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
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

# 32 syllable positions in one Mahamantra round
_MAHAMANTRA_SYLLABLES: Final[Tuple[str, ...]] = (
    "ha", "re", "kṛ", "ṣṇa", "ha", "re", "kṛ", "ṣṇa",
    "kṛ", "ṣṇa", "kṛ", "ṣṇa", "ha", "re", "ha", "re",
    "ha", "re", "rā", "ma", "ha", "re", "rā", "ma",
    "rā", "ma", "rā", "ma", "ha", "re", "ha", "re",
)

# Loaded state (lazily initialized)
_meta: Optional[Dict] = None
_stream: Optional[Tuple[int, ...]] = None
_syllable_data: Optional[Dict[str, dict]] = None
_harmonic_vib_ids: Optional[Tuple[int, ...]] = None
_mahamantra_coords: Optional[Dict[str, Tuple[int, ...]]] = None
_mahamantra_coord_set: Optional[FrozenSet[int]] = None
_salt_lut: Optional[Tuple[int, ...]] = None  # 32-entry LUT: position → packed frame


def _ensure_loaded() -> None:
    """Load bridge data. No external deps. Pure JSON."""
    global _meta, _stream, _syllable_data, _harmonic_vib_ids
    global _mahamantra_coords, _mahamantra_coord_set, _salt_lut

    if _stream is not None:
        return

    if not _DATA_PATH.exists():
        _meta = {}
        _stream = ()
        _syllable_data = {}
        _harmonic_vib_ids = ()
        _mahamantra_coords = {}
        _mahamantra_coord_set = frozenset()
        _salt_lut = (0,) * len(_MAHAMANTRA_SYLLABLES)
        return

    with open(_DATA_PATH) as f:
        raw = json.load(f)

    _meta = raw.get("meta", {})
    _stream = tuple(raw.get("stream", []))
    _syllable_data = raw.get("syllables", {})
    _harmonic_vib_ids = tuple(raw.get("harmonic_series", {}).get("vibration_ids", []))

    mc = raw.get("mahamantra_coords", {})
    _mahamantra_coords = {k: tuple(v) for k, v in mc.items()}

    # Build flat set of all Mahamantra RAMA coordinates
    all_coords: set = set()
    for coords in _mahamantra_coords.values():
        all_coords.update(coords)
    _mahamantra_coord_set = frozenset(all_coords)

    # Build the 32-position salt LUT from the continuous stream
    _salt_lut = _build_salt_lut()


def _build_salt_lut() -> Tuple[int, ...]:
    """Map each of the 32 Mahamantra syllable positions to a packed frame.

    Each position gets the center frame from its proportional region
    of the chant. O(1) lookup after construction.
    """
    assert _meta is not None
    assert _stream is not None

    n_positions = len(_MAHAMANTRA_SYLLABLES)
    chant_start = _meta.get("chant_start_frame", 0)
    chant_end = _meta.get("chant_end_frame", len(_stream) - 1)
    chant_range = chant_end - chant_start

    if chant_range <= 0 or not _stream:
        return (0,) * n_positions

    lut = []
    for p in range(n_positions):
        # Center frame for this syllable position
        center = chant_start + (p * chant_range + chant_range // 2) // n_positions
        center = min(center, len(_stream) - 1)
        lut.append(_stream[center])

    return tuple(lut)


# =============================================================================
# FRAME PACKING / UNPACKING (pure integer math)
# =============================================================================


def unpack_frame(packed: int) -> Tuple[int, int, int, int]:
    """Unpack uint32 → (rms, varga, f0_x10, centroid_100).

    Bits  0-7  (8): RMS energy (0-255)
    Bits  8-10 (3): Varga (0-4)
    Bits 11-22 (12): F0×10 (0-4095)
    Bits 23-31 (9): Centroid/100 (0-511)
    """
    rms = packed & 0xFF
    varga = (packed >> 8) & 0x7
    f0_x10 = (packed >> 11) & 0xFFF
    centroid_100 = (packed >> 23) & 0x1FF
    return rms, varga, f0_x10, centroid_100


# =============================================================================
# CORE: POSITION-BASED SALT
# =============================================================================


def prabhupada_salt(syllable_position: int) -> int:
    """Prabhupada's acoustic salt for Mahamantra position (0-31).

    When the system processes position N of the Mahamantra,
    this returns the packed uint32 from Prabhupada's ACTUAL chanting
    at that exact position. O(1) lookup.

    The packed value contains: RMS | Varga | F0×10 | Centroid/100.
    Use unpack_frame() to decompose.
    """
    _ensure_loaded()
    assert _salt_lut is not None
    n = len(_salt_lut)
    if n == 0:
        return 0
    return _salt_lut[syllable_position % n]


def stream_frame(frame_index: int) -> int:
    """Raw packed frame at index (0 to n_frames-1). O(1) lookup.

    Returns 0 if index out of range.
    """
    _ensure_loaded()
    assert _stream is not None
    if 0 <= frame_index < len(_stream):
        return _stream[frame_index]
    return 0


def stream_length() -> int:
    """Number of frames in the continuous stream."""
    _ensure_loaded()
    assert _stream is not None
    return len(_stream)


def syllable_at_position(position: int) -> str:
    """Which syllable is at Mahamantra position (0-31)?"""
    return _MAHAMANTRA_SYLLABLES[position % len(_MAHAMANTRA_SYLLABLES)]


# =============================================================================
# LOOKUPS
# =============================================================================


def acoustic_signature(syllable: str) -> Optional[dict]:
    """Get pre-baked acoustic signature for a Mahamantra syllable.

    Returns dict with: n_frames, rama_coords, element_histogram,
    avg_rms, avg_f0_x10, avg_centroid_100.

    Returns None if syllable not found.
    """
    _ensure_loaded()
    assert _syllable_data is not None
    return _syllable_data.get(syllable)


def get_meta() -> Dict:
    """Get recording metadata."""
    _ensure_loaded()
    assert _meta is not None
    return _meta


# =============================================================================
# SCORING
# =============================================================================


def _word_rama_coords(packed_hex: str) -> Tuple[int, ...]:
    """Get RAMA coordinates for a Gita word via varnamala_codec."""
    try:
        from vibe_core.mahamantra.substrate.semantic_index import get_index

        idx = get_index()
        idx._ensure_loaded()
        word = idx._hex_to_word.get(packed_hex)
        if word and hasattr(word, "coords") and word.coords:
            return tuple(word.coords)
        if word and hasattr(word, "sanskrit"):
            from vibe_core.mahamantra.substrate.encoding.varnamala_codec import encode
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
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_ELEMENT

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
    # Build Mahamantra element histogram from syllable data
    assert _syllable_data is not None
    mahamantra_hist = _mahamantra_element_histogram()

    dot = sum(a * b for a, b in zip(word_hist, mahamantra_hist))
    norm_a_sq = sum(a * a for a in word_hist)
    norm_b_sq = sum(b * b for b in mahamantra_hist)

    if dot > 0 and norm_a_sq > 0 and norm_b_sq > 0:
        denom_sq = norm_a_sq * norm_b_sq
        x = denom_sq
        for _ in range(TRINITY):
            if x > 0:
                x = (x + denom_sq // x) // 2
        if x > 0:
            cosine_x1000 = dot * 1000 // x
            if cosine_x1000 > 100:
                return min(0.7, cosine_x1000 / 1000 * 0.7)

    # Layer 3: VARGA — Check if word has similar varga distribution
    try:
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_VARGA

        word_varga = [0, 0, 0]
        for c in word_coords:
            if 0 <= c < POSITION_SUM_RAMA:
                v = COORD_VARGA[c]
                if v < TRINITY:
                    word_varga[v] += 1

        assert _syllable_data is not None
        total_word = sum(word_varga) or 1
        total_mantra = 0
        mantra_varga = [0, 0, 0]
        for syl_data in _syllable_data.values():
            coords = syl_data.get("rama_coords", [])
            count = syl_data.get("n_frames", 1)
            for c in coords:
                if 0 <= c < POSITION_SUM_RAMA:
                    v = COORD_VARGA[c]
                    if v < TRINITY:
                        mantra_varga[v] += count
                        total_mantra += count

        if total_mantra > 0:
            dist = sum(abs(word_varga[i] / total_word - mantra_varga[i] / total_mantra) for i in range(TRINITY))
            sim = max(0.0, 1.0 - dist)
            if sim > 0.2:
                return min(0.4, sim * 0.4)
    except Exception:
        pass

    return 0.0


@lru_cache(maxsize=1)
def _mahamantra_element_histogram() -> Tuple[int, ...]:
    """Aggregate element histogram across all Mahamantra syllable RAMA coords."""
    assert _syllable_data is not None
    hist = [0] * PANCHA
    try:
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_ELEMENT

        for syl_data in _syllable_data.values():
            n = syl_data.get("n_frames", 1)
            for c in syl_data.get("rama_coords", []):
                if 0 <= c < POSITION_SUM_RAMA:
                    hist[COORD_ELEMENT[c]] += n
    except Exception:
        pass
    return tuple(hist)


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

    if vibration_id in _harmonic_vib_ids:
        idx = _harmonic_vib_ids.index(vibration_id)
        return max(0.5, 1.0 - idx * 0.06)

    min_dist = min(abs(vibration_id - h) for h in _harmonic_vib_ids)

    if min_dist == 0:
        return 1.0
    return min(0.5, SEVEN / (SEVEN + min_dist))


# =============================================================================
# DIAGNOSTIC
# =============================================================================


def diagnose() -> None:
    """Print acoustic bridge analysis for debugging."""
    _ensure_loaded()
    assert _meta is not None
    assert _syllable_data is not None
    assert _stream is not None
    assert _harmonic_vib_ids is not None
    assert _salt_lut is not None

    print("SHABDA BRIDGE v2 — Prabhupada Continuous Acoustic Stream")
    print("=" * 58)
    print(f"Source: {_meta.get('source', '?')}")
    print(f"Bake version: {_meta.get('bake_version', '?')}")
    print(f"F0: {_meta.get('fundamental_hz_x10', 0) / 10:.1f} Hz (mean)")
    print(f"F0: {_meta.get('median_hz_x10', 0) / 10:.1f} Hz (median)")
    print(f"VibID: {_meta.get('vibration_id', 0)}")
    print(f"Frames: {len(_stream)} × uint32 = {len(_stream) * 4} bytes")
    print(f"Duration: {_meta.get('duration_ms', 0)}ms")
    print(f"Chant region: frame {_meta.get('chant_start_frame', 0)}-{_meta.get('chant_end_frame', 0)}")
    print()

    print("Syllable Signatures:")
    sig_header = f"  {'Syl':5s} {'RAMA':>12s} {'Frames':>6s} {'AvgRMS':>6s} {'AvgF0':>7s} {'AvgCent':>7s}"
    print(sig_header)
    print("  " + "─" * 50)
    for syl, data in _syllable_data.items():
        coords_str = str(data.get("rama_coords", []))
        print(f"  {syl:5s} {coords_str:>12s} "
              f"{data.get('n_frames', 0):6d} "
              f"{data.get('avg_rms', 0):6d} "
              f"{data.get('avg_f0_x10', 0) / 10:6.1f}Hz "
              f"{data.get('avg_centroid_100', 0) * 100:6.0f}Hz")

    print(f"\nHarmonic Series (VibIDs): {list(_harmonic_vib_ids)}")

    print("\nSalt LUT (32 positions):")
    for i in range(0, len(_salt_lut), 8):
        chunk = _salt_lut[i:i + 8]
        syls = [_MAHAMANTRA_SYLLABLES[j] for j in range(i, min(i + 8, len(_salt_lut)))]
        for j, (syl, packed) in enumerate(zip(syls, chunk)):
            rms, varga, f0_x10, cent = unpack_frame(packed)
            print(f"  [{i + j:2d}] {syl:4s} → RMS={rms:3d} V={varga} F0={f0_x10 / 10:.0f}Hz C={cent * 100}Hz")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "acoustic_score",
    "acoustic_scores_batch",
    "acoustic_signature",
    "diagnose",
    "get_meta",
    "prabhupada_salt",
    "stream_frame",
    "stream_length",
    "syllable_at_position",
    "unpack_frame",
    "vibration_alignment",
]
