"""
SHABDA VIBRATION — Audio Frames → VibrationSignature
======================================================

The INVERSE of text_to_vibration().

text_to_vibration():  Text → VibrationSignature sequence
frame_to_vibration(): Audio → VibrationSignature sequence

This bridges the gap between audio intake and the resonance infrastructure.
Once we have VibrationSignatures from audio, we can use the EXISTING
7D ResonanceRanker for matching — no new scoring logic needed.

Audio features map DIRECTLY to VibrationSignature fields:
    articulation = varga (from centroid) → ArticulationPoint (5 points)
    voicing      = F0 + RMS + centroid  → VoicingType (4 types)
    frequency    = F0                   → NADI_RESONANCE multiples
    duration     = consecutive frames   → AKSARA ratio

No if-else spaghetti. No hand-tuned weights. Pure lookup.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    HALVES,
    KSETRAJNA,
    NADI_RESONANCE,
    QUARTERS,
)
from vibe_core.mahamantra.sound.shabda_intake import unpack_frame
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    ArticulationPoint,
    VibrationSignature,
    VoicingType,
)

# =============================================================================
# CONSTANTS (derived from shabda_processor thresholds — same source of truth)
# =============================================================================

_RMS_VOICED_THRESHOLD = 20
_RMS_VOWEL_THRESHOLD = 80
_NASAL_CENTROID_CEILING = 80
_ASPIRATION_CENTROID_FLOOR = 120
_GHOSHMAHA_RMS_FLOOR = 120


# =============================================================================
# CORE: Audio Frame → VibrationSignature
# =============================================================================


def _varga_to_articulation(varga: int) -> ArticulationPoint:
    """Varga (0-4) → ArticulationPoint. Direct mapping — same 5-point axis."""
    if varga <= 0:
        return ArticulationPoint.KANTHA
    if varga >= QUARTERS:
        return ArticulationPoint.OSHTHA
    return ArticulationPoint(varga)


def _audio_to_voicing(rms: int, f0_x10: int, centroid_100: int) -> VoicingType:
    """Audio features → VoicingType. Same logic as shabda_processor._audio_to_sthana."""
    if f0_x10 == 0:
        return VoicingType.UNVOICED

    # F0 present → voiced. Distinguish aspirated variants.
    if centroid_100 < _NASAL_CENTROID_CEILING:
        return VoicingType.VOICED  # nasal = voiced (no aspiration)

    if rms > _GHOSHMAHA_RMS_FLOOR and centroid_100 > _ASPIRATION_CENTROID_FLOOR:
        return VoicingType.VOICED_ASPIRATED

    if centroid_100 > _ASPIRATION_CENTROID_FLOOR:
        return VoicingType.UNVOICED_ASPIRATED

    return VoicingType.VOICED


def _f0_to_frequency(f0_x10: int) -> int:
    """F0 (in tenths of Hz) → frequency in NADI_RESONANCE (72) scale.

    Maps real F0 to nearest NADI multiple:
        0 Hz    → LILA (48) — unvoiced, consonant territory
        ~72 Hz  → NADI_RESONANCE (72) — low male voice
        ~144 Hz → FIELD_RESONANCE (144) — high male / low female
        ~216 Hz → 3×NADI (216) — female voice
        ~288 Hz → 4×NADI (288) — high female / child
    """
    if f0_x10 == 0:
        return QUARTERS * NADI_RESONANCE // NADI_RESONANCE  # minimal freq marker

    f0_hz = f0_x10 / 10.0
    # Quantize to nearest NADI_RESONANCE multiple
    nadi_multiples = max(KSETRAJNA, round(f0_hz / NADI_RESONANCE))
    return nadi_multiples * NADI_RESONANCE


def frame_to_vibration(packed: int) -> VibrationSignature:
    """Convert one uint32 audio frame to a VibrationSignature.

    The INVERSE of text_to_vibration() — from audio features to the
    same universal phonetic model that text encoding uses.

    Args:
        packed: uint32 audio frame from ShabdaIntake

    Returns:
        VibrationSignature with articulation, voicing, frequency, duration
        Duration is always KSETRAJNA (1 frame) — caller accumulates.
    """
    rms, varga, f0_x10, centroid_100 = unpack_frame(packed)

    return VibrationSignature(
        articulation=_varga_to_articulation(varga),
        voicing=_audio_to_voicing(rms, f0_x10, centroid_100),
        base_frequency=_f0_to_frequency(f0_x10),
        duration_ratio=KSETRAJNA,  # 1 frame; accumulated in stream_to_vibrations
    )


# =============================================================================
# STREAM: Audio Frames → Accumulated VibrationSignature Sequence
# =============================================================================


def stream_to_vibrations(frames: Sequence[int]) -> Tuple[VibrationSignature, ...]:
    """Convert audio frame sequence to accumulated VibrationSignatures.

    Consecutive frames with the SAME (articulation, voicing, frequency)
    are merged into one VibrationSignature with accumulated duration.
    This produces one signature per phoneme, not per frame.

    Silent frames (RMS < threshold) are skipped.

    Returns:
        Tuple of VibrationSignatures, one per detected phoneme.
    """
    if not frames:
        return ()

    signatures: List[VibrationSignature] = []
    current_art = None
    current_voicing = None
    current_freq = 0
    duration = 0

    for packed in frames:
        rms = packed & 0xFF
        if rms < _RMS_VOICED_THRESHOLD:
            # Silence: flush current phoneme
            if current_art is not None and duration > 0:
                signatures.append(VibrationSignature(
                    articulation=current_art,
                    voicing=current_voicing,
                    base_frequency=current_freq,
                    duration_ratio=min(duration, AKSARA_COUNT),
                ))
                current_art = None
                duration = 0
            continue

        sig = frame_to_vibration(packed)

        if (sig.articulation == current_art
                and sig.voicing == current_voicing
                and sig.base_frequency == current_freq):
            # Same phoneme continues — accumulate duration
            duration += KSETRAJNA
        else:
            # New phoneme — flush previous
            if current_art is not None and duration > 0:
                signatures.append(VibrationSignature(
                    articulation=current_art,
                    voicing=current_voicing,
                    base_frequency=current_freq,
                    duration_ratio=min(duration, AKSARA_COUNT),
                ))
            current_art = sig.articulation
            current_voicing = sig.voicing
            current_freq = sig.base_frequency
            duration = KSETRAJNA

    # Flush last phoneme
    if current_art is not None and duration > 0:
        signatures.append(VibrationSignature(
            articulation=current_art,
            voicing=current_voicing,
            base_frequency=current_freq,
            duration_ratio=min(duration, AKSARA_COUNT),
        ))

    return tuple(signatures)


# =============================================================================
# VIBRATION → RAMA COORDINATES (for ResonanceRanker compatibility)
# =============================================================================


def vibrations_to_coords(
    signatures: Sequence[VibrationSignature],
) -> Tuple[int, ...]:
    """Convert VibrationSignatures to RAMA coordinates.

    Uses signature_id modulo VARNAMALA_TOTAL (49) to project into
    the same coordinate space that encode_text() and ARPABET_TO_RAMA use.

    This is the BRIDGE: audio → VibrationSignature → RAMA coords,
    which can then be scored by ResonanceRanker.
    """
    from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL

    coords: List[int] = []
    for sig in signatures:
        coord = sig.signature_id % VARNAMALA_TOTAL
        coords.append(coord)
    return tuple(coords)


# =============================================================================
# CONVENIENCE: Full pipeline Audio → RAMA coords via VibrationSignature
# =============================================================================


def stream_to_vibration_coords(frames: Sequence[int]) -> Tuple[int, ...]:
    """Audio frames → VibrationSignatures → RAMA coordinates.

    Full pipeline: extracts phonemes from audio, projects to RAMA space.
    The resulting coords are compatible with ResonanceRanker and
    PronunciationDict matching.
    """
    sigs = stream_to_vibrations(frames)
    return vibrations_to_coords(sigs)
