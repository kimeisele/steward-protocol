"""
SHABDA PROCESSOR — Audio Frames → RAMA Coordinates
====================================================

The GLUE between ShabdaIntake (audio → uint32 frames) and the
phonetic encoding pipeline (RAMA coordinates → resonance → meaning).

Audio vibration is language-agnostic. A spectral centroid of 1500 Hz
maps to TALAVYA (palatal) whether the speaker speaks English, Sanskrit,
or Mandarin. This module converts raw acoustic features into the same
coordinate space that PhoneticEncoder uses for text.

    ShabdaIntake          →  uint32 frames (RMS, Varga, F0, Centroid)
    ShabdaProcessor       →  RAMA coordinates (0-48) + Element walk
    ResonanceRanker       →  scored words from Gita lexicon
    PhoneticBridge        →  PhoneticTensor (varga/sthana vectors)

The mapping uses FOUR acoustic dimensions to narrow 49 → 1 coordinate:

    1. Varga (from centroid)  →  Element (0-4)  →  10 candidates
    2. Sound class (from RMS dynamics)  →  Svara/Sparsha/Shesha  →  2-5 candidates
    3. Sthana (from F0 + RMS + centroid)  →  energy level (0-4)  →  exact coordinate
    4. Vowel quality (from RMS + centroid pattern)  →  short/long/compound/special

Sthana detection uses the SAME 5-level system as PhoneticBridge:

    SPARSHA(0)    = unvoiced stop      → F0 absent, sharp onset
    MAHAPRANA(1)  = aspirated          → F0 present, high centroid (breath)
    GHOSHAVAT(2)  = voiced             → F0 present, moderate energy
    GHOSHMAHA(3)  = voiced aspirated   → F0 present, high energy + high centroid
    ANUNASIKA(4)  = nasal              → F0 present, low centroid (nasal resonance)

For SPARSHA consonants (coords 16-40), COORD_SUB = SthanaIndex directly.
This gives 5×5 = 25 distinct consonant coordinates from audio alone.

No external dependencies. No ML models. Pure phonetic algebra.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import PANCHA
from vibe_core.mahamantra.sound.shabda_intake import unpack_frame
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT,
    COORD_SUB,
    COORD_VARGA,
    Element,
    element_histogram,
    element_walk,
    walk_distance,
    walk_signature,
)

# =============================================================================
# ELEMENT ↔ VARGA ↔ RAMA COORDINATE LOOKUP TABLES
# =============================================================================

# Pre-build: for each (element, varga_class) pair, which RAMA coords are possible?
# varga_class: 0=SVARA (vowel), 1=SPARSHA (consonant stop), 2=SHESHA (semivowel/sibilant)
_ELEMENT_VARGA_TO_COORDS: Tuple[Tuple[Tuple[int, ...], ...], ...] = tuple(
    tuple(
        tuple(c for c in range(49) if COORD_ELEMENT[c] == elem and COORD_VARGA[c] == vc)
        for vc in range(3)
    )
    for elem in range(PANCHA)
)

# Representative coordinate per (element, varga_class): the most common/neutral choice
# For SVARA: short vowel (sub=0) is the neutral form
# For SPARSHA: unvoiced stop (sub=0) is the neutral form
# For SHESHA: first member (sub=0)
_REPRESENTATIVE: Tuple[Tuple[int, ...], ...] = tuple(
    tuple(
        _ELEMENT_VARGA_TO_COORDS[elem][vc][0] if _ELEMENT_VARGA_TO_COORDS[elem][vc] else 0
        for vc in range(3)
    )
    for elem in range(PANCHA)
)


# =============================================================================
# SOUND CLASS DETECTION (from acoustic features)
# =============================================================================

# Thresholds derived from Prabhupada's chanting analysis:
# Vowels: RMS > 80, F0 stable (present), duration > 3 frames
# Stops: RMS spike (>40) after low (<20), short duration
# Sibilants/semivowels: high centroid (>150), medium RMS

_RMS_VOICED_THRESHOLD = 20
_RMS_VOWEL_THRESHOLD = 80
_CENTROID_SIBILANT_THRESHOLD = 150


def _classify_sound(
    rms: int, f0_x10: int, centroid_100: int,
    prev_rms: int = 0,
) -> int:
    """Classify a frame into sound class.

    Returns:
        0 = SVARA (vowel-like: high energy, stable pitch)
        1 = SPARSHA (stop-like: energy onset, brief)
        2 = SHESHA (continuant: sibilant or semivowel)
       -1 = silence (below voiced threshold)
    """
    if rms < _RMS_VOICED_THRESHOLD:
        return -1  # silence

    # Vowel-like: high sustained energy with pitch (check FIRST)
    if rms > _RMS_VOWEL_THRESHOLD and f0_x10 > 0:
        return 0  # SVARA

    # Sibilants: high spectral centroid, may lack clear F0
    if centroid_100 > _CENTROID_SIBILANT_THRESHOLD and f0_x10 == 0:
        return 2  # SHESHA

    # Plosive onset: energy jump from low (only for non-vowel energy)
    if prev_rms < _RMS_VOICED_THRESHOLD and rms > _RMS_VOICED_THRESHOLD:
        return 1  # SPARSHA (onset)

    # Semivowel/nasal: medium energy, has pitch but lower than vowel
    if f0_x10 > 0:
        return 2  # SHESHA (semivowel-like)

    # Default: treat as stop continuation
    return 1  # SPARSHA


# =============================================================================
# STHANA DETECTION (from acoustic features → 5 energy levels)
# =============================================================================

# Maps directly to SthanaIndex from phonetic_bridge.py:
#   0 = SPARSHA     (unvoiced: no F0, sharp onset)         energy=0.2
#   1 = MAHAPRANA   (aspirated: F0 + high centroid/breath)  energy=0.6
#   2 = GHOSHAVAT   (voiced: F0 + moderate energy)          energy=0.8
#   3 = GHOSHMAHA   (voiced aspirated: F0 + max energy)     energy=1.0
#   4 = ANUNASIKA   (nasal: F0 + low centroid resonance)    energy=0.5
#
# For SPARSHA consonants (coords 16-40), COORD_SUB IS the Sthana column.

_NASAL_CENTROID_CEILING = 80
_ASPIRATION_CENTROID_FLOOR = 120
_GHOSHMAHA_RMS_FLOOR = 120


def _audio_to_sthana(rms: int, f0_x10: int, centroid_100: int) -> int:
    """Map audio features to SthanaIndex (0-4).

    This is the CORE innovation: acoustic energy → Vedic articulation energy.
    The same 5-level system that PhoneticBridge uses for text analysis.
    """
    # No pitch → unvoiced stop (ka, ca, ṭa, ta, pa)
    if f0_x10 == 0:
        return 0  # SPARSHA

    # F0 present → voiced. Now distinguish 4 energy levels.

    # Low centroid + F0 = nasal resonance (ṅa, ña, ṇa, na, ma)
    if centroid_100 < _NASAL_CENTROID_CEILING:
        return 4  # ANUNASIKA

    # High energy + high centroid = voiced aspirated (gha, jha, ḍha, dha, bha)
    if rms > _GHOSHMAHA_RMS_FLOOR and centroid_100 > _ASPIRATION_CENTROID_FLOOR:
        return 3  # GHOSHMAHA

    # High centroid but lower energy = aspirated (kha, cha, ṭha, tha, pha)
    if centroid_100 > _ASPIRATION_CENTROID_FLOOR:
        return 1  # MAHAPRANA

    # Default voiced: moderate energy, moderate centroid (ga, ja, ḍa, da, ba)
    return 2  # GHOSHAVAT


def _refine_sub_index(
    sound_class: int, rms: int, f0_x10: int, centroid_100: int, element: int,
) -> int:
    """Refine sub-index within a sound class using Sthana-aware features.

    SVARA sub (0-3): 0=short, 1=long, 2=compound, 3=special (anusvara/visarga)
    SPARSHA sub (0-4): SthanaIndex directly (unvoiced/aspirated/voiced/voiced-asp/nasal)
    SHESHA sub (0-1): 0=antastha (semivowel), 1=ushman (sibilant)
    """
    if sound_class == 0:  # SVARA
        # Special: nasal quality (low centroid) in vowel = anusvara-like
        if centroid_100 < _NASAL_CENTROID_CEILING:
            return 3  # special (anusvara territory)
        # Compound: high energy + high centroid = diphthong-like transition
        if rms > 160 and centroid_100 > _ASPIRATION_CENTROID_FLOOR:
            return 2  # compound
        # Long vs short: sustained energy
        return 1 if rms > 140 else 0

    if sound_class == 1:  # SPARSHA
        # Direct Sthana detection — the 5×5 grid
        return _audio_to_sthana(rms, f0_x10, centroid_100)

    # SHESHA: antastha (semivowel) vs ushman (sibilant)
    return 1 if centroid_100 > _CENTROID_SIBILANT_THRESHOLD else 0


# =============================================================================
# FRAME → RAMA COORDINATE
# =============================================================================


def frame_to_rama(
    packed: int, prev_packed: int = 0,
) -> int:
    """Convert one uint32 audio frame to a RAMA coordinate (0-48).

    Uses 3 acoustic dimensions:
        Varga (centroid) → Element (0-4) → 10 candidates
        Sound class (RMS/F0) → Svara/Sparsha/Shesha → 2-5 candidates
        Sub-index (RMS/F0/centroid detail) → final coordinate

    Args:
        packed: uint32 audio frame from ShabdaIntake
        prev_packed: previous frame (for onset detection)

    Returns:
        RAMA coordinate (0-48), or -1 for silence
    """
    rms, varga, f0_x10, centroid_100 = unpack_frame(packed)
    prev_rms = unpack_frame(prev_packed)[0] if prev_packed else 0

    # Silence → no coordinate
    sound_class = _classify_sound(rms, f0_x10, centroid_100, prev_rms)
    if sound_class < 0:
        return -1

    # Element = Varga (same axis, 0-4)
    element = varga

    # Get candidate coordinates for this (element, sound_class)
    candidates = _ELEMENT_VARGA_TO_COORDS[element][sound_class]
    if not candidates:
        # Fallback: use representative for this element, any class
        return _REPRESENTATIVE[element][0]

    if len(candidates) == 1:
        return candidates[0]

    # Refine using sub-index
    sub = _refine_sub_index(sound_class, rms, f0_x10, centroid_100, element)

    # Find candidate with matching sub, or nearest
    for c in candidates:
        if COORD_SUB[c] == sub:
            return c

    # Nearest sub-index
    best = candidates[0]
    best_dist = abs(COORD_SUB[candidates[0]] - sub)
    for c in candidates[1:]:
        d = abs(COORD_SUB[c] - sub)
        if d < best_dist:
            best = c
            best_dist = d
    return best


# =============================================================================
# STHANA ENERGY (pronunciation intensity per frame)
# =============================================================================

# Float energy values matching PhoneticBridge's STHANA_ENERGY.
# Index = SthanaIndex, Value = energy (0.0-1.0).
STHANA_ENERGY: Tuple[float, ...] = (0.2, 0.6, 0.8, 1.0, 0.5)


def frame_to_sthana(packed: int) -> int:
    """Convert one uint32 audio frame to a SthanaIndex (0-4).

    Returns the pronunciation energy level regardless of sound class:
        0 = SPARSHA     (unvoiced, 0.2)
        1 = MAHAPRANA   (aspirated, 0.6)
        2 = GHOSHAVAT   (voiced, 0.8)
        3 = GHOSHMAHA   (voiced aspirated, 1.0)
        4 = ANUNASIKA   (nasal, 0.5)
       -1 = silence

    This runs PARALLEL to frame_to_rama(). Together they give:
        RAMA coordinate = WHAT phoneme (identity)
        SthanaIndex     = HOW STRONG  (pronunciation energy)
    """
    rms, _varga, f0_x10, centroid_100 = unpack_frame(packed)
    if rms < _RMS_VOICED_THRESHOLD:
        return -1
    return _audio_to_sthana(rms, f0_x10, centroid_100)


def stream_to_sthana_profile(frames: Sequence[int]) -> Tuple[int, ...]:
    """Audio frames → Sthana indices (parallel to stream_to_rama).

    Same length as stream_to_rama(): silence frames removed, same ordering.
    Each value is a SthanaIndex (0-4) giving pronunciation energy.
    """
    profile: List[int] = []
    for frame in frames:
        s = frame_to_sthana(frame)
        if s >= 0:
            profile.append(s)
    return tuple(profile)


def stream_to_energy_contour(frames: Sequence[int]) -> Tuple[float, ...]:
    """Audio frames → energy contour (0.0-1.0 per voiced frame).

    Converts SthanaIndex to float energy via STHANA_ENERGY lookup.
    Same length as stream_to_rama().
    """
    contour: List[float] = []
    for frame in frames:
        s = frame_to_sthana(frame)
        if s >= 0:
            contour.append(STHANA_ENERGY[s])
    return tuple(contour)


# =============================================================================
# STREAM → RAMA COORDINATES (batch + generator)
# =============================================================================


def stream_to_rama(frames: Sequence[int]) -> Tuple[int, ...]:
    """Convert a sequence of uint32 frames to RAMA coordinates.

    Skips silence frames (-1). Returns only voiced coordinates.

    Args:
        frames: sequence of packed uint32 audio frames

    Returns:
        Tuple of RAMA coordinates (0-48), silence removed
    """
    coords: List[int] = []
    prev = 0
    for frame in frames:
        c = frame_to_rama(frame, prev)
        if c >= 0:
            coords.append(c)
        prev = frame
    return tuple(coords)


def stream_to_element_walk(frames: Sequence[int]) -> Tuple[Element, ...]:
    """Audio frames → Element walk (the semantic journey through 5 elements)."""
    coords = stream_to_rama(frames)
    if not coords:
        return ()
    return element_walk(coords)


def stream_to_histogram(frames: Sequence[int]) -> Tuple[int, ...]:
    """Audio frames → Element histogram (distribution across 5 elements)."""
    coords = stream_to_rama(frames)
    if not coords:
        return (0,) * PANCHA
    return element_histogram(coords)


def stream_to_signature(frames: Sequence[int]) -> str:
    """Audio frames → compact walk signature string (S/V/F/W/E)."""
    coords = stream_to_rama(frames)
    if not coords:
        return ""
    return walk_signature(coords)


def compare_streams(
    frames_a: Sequence[int], frames_b: Sequence[int],
) -> float:
    """Compare two audio streams by element-histogram distance.

    Returns:
        float in [0, 1]: 0 = identical distribution, 1 = maximally different
    """
    coords_a = stream_to_rama(frames_a)
    coords_b = stream_to_rama(frames_b)
    if not coords_a or not coords_b:
        return 1.0
    return walk_distance(coords_a, coords_b)
