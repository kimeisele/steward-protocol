"""
SHABDA DECODER — Deterministic Speech-to-Text
===============================================

"śabda-brahma" — Sound is the ultimate reality.

Audio → uint32 frames → ARPAbet phonemes → RAMA coordinates → dictionary → transcript.

Pipeline:
    Audio Frames (10ms, uint32)
        → unpack_frame() → RMS, Varga, F0, Centroid  [shabda_intake.py]
    Per-frame features
        → score_frame() against PhonemeTemplates       [this file]
        → top-1 ARPAbet → ARPABET_TO_RAMA             [this file]
    Per-frame RAMA coords
        → CTC-dedup → phoneme-level sequence           [this file]
        → segment by silence/energy dips               [this file]
    Word-length segments
        → RAMA edit distance vs PronunciationDict      [this file]
        → greedy best match per segment
    Transcript: "not exactly but I came to preach..."

No ML models. No external APIs. Pure phonetic algebra + dictionary lookup.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import PANCHA, WORDS
from vibe_core.mahamantra.sound.shabda_intake import (
    ShabdaStream,
    unpack_frame,
)
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT,
    COORD_VARGA,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA,
    ARPABET_TO_STHANA,
    ARPABET_TO_VARGA,
    SthanaIndex,
    VargaIndex,
)

logger = logging.getLogger("SHABDA_DECODER")


# =============================================================================
# PHONEME TEMPLATES (acoustic fingerprints for each ARPAbet phoneme)
# =============================================================================


@dataclass(frozen=True)
class PhonemeTemplate:
    """Acoustic template for a single ARPAbet phoneme."""

    arpabet: str
    rama_coord: int
    varga: int  # 0-4 (VargaIndex)
    sthana: int  # 0-4 (SthanaIndex)
    sound_class: int  # 0=svara, 1=sparsha, 2=shesha
    f0_required: bool  # voiced?
    f1_center: int  # Hz (0=don't care)
    f2_center: int  # Hz (0=don't care)
    centroid_min: int  # centroid/100 low bound
    centroid_max: int  # centroid/100 high bound
    mfcc_center: Tuple[int, ...] = ()  # 13 MFCC coefficients (×100)


# F1/F2 centers calibrated from Prabhupada's japa recording (experiment 21).
# Bengali/Hindi vocal tract shifts F2 ~+350 Hz vs Peterson & Barney textbook.
# Japa data: ha(453,1543) re(477,1589) kṛ(395,1672) ṣṇa(419,1656) rā(543,1426).
_VOWEL_FORMANTS: Final[Dict[str, Tuple[int, int]]] = {
    "AA": (650, 1550),  # /ɑ/ father  (textbook: 750, 1200)
    "AE": (580, 2050),  # /æ/ bat     (textbook: 660, 1700)
    "AH": (450, 1550),  # /ʌ/ but     (textbook: 520, 1200) — from japa /a/
    "AO": (500, 1200),  # /ɔ/ bought  (textbook: 570, 850)
    "AW": (620, 1450),  # /aʊ/ bout   (textbook: 700, 1100)
    "AY": (620, 1550),  # /aɪ/ bite   (textbook: 700, 1200)
    "EH": (490, 2200),  # /ɛ/ bet     (textbook: 530, 1850)
    "EY": (360, 2550),  # /eɪ/ bait   (textbook: 400, 2200)
    "ER": (420, 1700),  # /ɝ/ bird    (textbook: 490, 1350) — from japa /ṛ/
    "IH": (340, 2300),  # /ɪ/ bit     (textbook: 390, 1950)
    "IY": (250, 2650),  # /i/ beat    (textbook: 280, 2300)
    "OW": (400, 1200),  # /oʊ/ boat   (textbook: 450, 850)
    "OY": (400, 1200),  # /ɔɪ/ boy    (textbook: 450, 850)
    "UH": (310, 1350),  # /ʊ/ book    (textbook: 350, 1000)
    "UW": (270, 1250),  # /u/ boot    (textbook: 300, 900)
}

# Centroid ranges (centroid/100) for consonant classes
_CONSONANT_CENTROID: Final[Dict[str, Tuple[int, int]]] = {
    # Stops: broad energy onset
    "K": (20, 200),
    "G": (20, 200),
    "NG": (10, 80),
    "CH": (40, 250),
    "JH": (40, 200),
    "T": (30, 250),
    "D": (30, 200),
    "TH": (40, 300),
    "DH": (30, 200),
    "N": (10, 80),
    "P": (10, 150),
    "B": (10, 150),
    "F": (80, 350),
    "M": (10, 60),
    # Semivowels
    "Y": (30, 200),
    "R": (20, 180),
    "L": (20, 160),
    "V": (20, 180),
    "W": (20, 150),
    # Sibilants / Fricatives
    "S": (150, 400),
    "SH": (100, 350),
    "Z": (100, 350),
    "ZH": (80, 300),
    "HH": (30, 250),
}


# MFCC prototypes (×100) for 39 ARPAbet phonemes.
# Derived from standard acoustic phonetics reference values
# (Peterson & Barney 1952, Hillenbrand et al. 1995, Stevens 1998).
# 13 coefficients: c0 (log energy), c1-c12 (spectral shape).
_MFCC_PROTOTYPES: Final[Dict[str, Tuple[int, ...]]] = {
    # Computed from synthetic reference signals using our own extract_mfcc().
    # Vowels — two-formant synthesis (F1+F2 resonances + F0 harmonics)
    "AA": (-3292, -1, 112, -103, -29, 41, 129, 124, 84, 13, -37, -73, -72),
    "AE": (-3234, 132, 52, -148, 20, 110, 110, 0, -52, -26, 45, 52, 4),
    "AH": (-3897, 394, 147, -75, 12, 50, 75, 14, -46, -89, -66, -8, 55),
    "AO": (-3627, 295, 200, -65, -34, -14, 52, 63, 59, 17, -19, -54, -53),
    "AW": (-3400, 110, 147, -101, -47, 11, 98, 104, 78, 17, -26, -58, -53),
    "AY": (-3543, 199, 122, -114, -26, 43, 115, 93, 47, -13, -36, -44, -28),
    "EH": (-3629, 389, 8, -61, 138, 137, 13, -136, -122, -7, 93, 75, -4),
    "EY": (-3405, 70, 102, 70, 240, 106, -123, -229, -86, 85, 112, -5, -78),
    "ER": (-4163, 655, 38, -53, 21, 71, 65, -24, -93, -102, -36, 45, 92),
    "IH": (-3904, 558, 19, -64, 149, 154, 3, -173, -161, -28, 84, 67, -4),
    "IY": (-3190, -180, 126, 102, 193, 41, -125, -161, -15, 85, 43, -68, -73),
    "OW": (-3763, 239, 248, -15, 1, 4, 50, 41, 24, -16, -40, -56, -39),
    "OY": (-3763, 239, 248, -15, 1, 4, 50, 41, 24, -16, -40, -56, -39),
    "UH": (-3567, 74, 249, 3, -2, -9, 36, 24, 3, -40, -58, -61, -27),
    "UW": (-3280, -115, 198, 20, 21, -3, 29, 20, 11, -23, -44, -59, -36),
    # Stops — burst noise + optional voicing
    "K": (-2729, -1784, -230, -246, -94, -93, -53, -59, -26, -36, -29, -13, -13),
    "G": (-2677, -1482, 65, 37, 174, 155, 172, 141, 147, 108, 87, 75, 48),
    "NG": (-2666, -1509, 58, 34, 169, 156, 189, 150, 148, 121, 125, 78, 46),
    "CH": (-2811, -1780, -231, -246, -73, -80, -44, -61, -44, -46, -20, -9, -15),
    "JH": (-2634, -1478, 64, 36, 192, 164, 176, 132, 121, 89, 86, 68, 34),
    "T": (-2768, -1787, -212, -236, -82, -80, -14, -38, -32, -16, 2, -8, -15),
    "D": (-2712, -1497, 71, 35, 173, 156, 198, 148, 128, 115, 105, 68, 34),
    "TH": (-2725, -1772, -177, -194, -63, -74, -10, -21, -18, -12, -10, -11, -18),
    "DH": (-2678, -1501, 87, 59, 175, 145, 188, 153, 131, 109, 85, 58, 26),
    "N": (-2666, -1509, 58, 34, 169, 156, 189, 150, 148, 121, 125, 78, 46),
    "P": (-2766, -1759, -192, -219, -83, -73, -33, -50, -3, -4, -2, -1, 4),
    "B": (-2721, -1480, 80, 41, 162, 151, 169, 127, 147, 118, 92, 66, 45),
    "F": (-2785, -1770, -207, -212, -47, -94, -56, -38, -20, -13, -1, -9, -19),
    "M": (-2664, -1483, 68, 27, 157, 162, 194, 142, 131, 117, 116, 63, 37),
    # Semivowels — vowel-like, weaker energy
    "Y": (-3710, -146, 120, 73, 179, 62, -94, -162, -48, 64, 65, -24, -52),
    "R": (-4790, 709, 74, -59, -2, 53, 74, 7, -60, -91, -51, 13, 62),
    "L": (-4616, 509, 216, -50, -8, 12, 54, 24, -19, -67, -68, -45, 1),
    "V": (-3905, -40, 158, 24, 126, 113, 28, -121, -162, -87, 47, 105, 70),
    "W": (-3811, -129, 206, 41, 42, 8, 26, 9, 0, -30, -46, -57, -32),
    # Sibilants / Fricatives — filtered noise
    "S": (-2548, -1780, -229, -233, -96, -97, -35, -16, 6, -5, 8, -15, -15),
    "SH": (-2650, -1804, -194, -208, -72, -53, 2, -1, -8, -23, 2, -16, -22),
    "Z": (-2517, -1531, 13, 0, 153, 154, 178, 134, 120, 91, 87, 50, 34),
    "ZH": (-2453, -1522, 38, 21, 156, 133, 155, 131, 123, 89, 74, 23, 13),
    "HH": (-2572, -1790, -235, -242, -87, -78, -20, -31, 1, -16, 2, -14, -24),
}


def _mfcc_similarity(observed: Tuple[int, ...], template: Tuple[int, ...]) -> float:
    """Cosine similarity on c1-c12 (skipping c0 = log energy).

    c0 is dominated by overall energy and kills phoneme discrimination.
    c1-c12 encode vocal tract shape — the actual spectral fingerprint.
    Standard practice in ASR: drop c0 or replace with log-energy separately.
    """
    if len(observed) < 2 or len(template) < 2:
        return 0.0
    # Skip c0, use c1 onwards
    obs = observed[1:]
    tpl = template[1:]
    dot = sum(a * b for a, b in zip(obs, tpl))
    norm_a = sum(a * a for a in obs) ** 0.5
    norm_b = sum(b * b for b in tpl) ** 0.5
    if norm_a < 1.0 or norm_b < 1.0:
        return 0.0
    return max(0.0, dot / (norm_a * norm_b))


def _build_templates() -> Tuple[PhonemeTemplate, ...]:
    """Build phoneme templates from ARPABET mapping tables."""
    templates: List[PhonemeTemplate] = []

    for arpabet, rama in ARPABET_TO_RAMA.items():
        varga_idx = ARPABET_TO_VARGA.get(arpabet, VargaIndex.KANTHYA)
        sthana_idx = ARPABET_TO_STHANA.get(arpabet, SthanaIndex.GHOSHAVAT)

        if rama < WORDS:
            sound_class = 0
        elif rama < WORDS + PANCHA * PANCHA:
            sound_class = 1
        else:
            sound_class = 2

        f0_required = sthana_idx != SthanaIndex.SPARSHA
        f1, f2 = _VOWEL_FORMANTS.get(arpabet, (0, 0))
        c_min, c_max = _CONSONANT_CENTROID.get(arpabet, (0, 511))
        if sound_class == 0:
            c_min, c_max = 0, 511

        mfcc = _MFCC_PROTOTYPES.get(arpabet, ())

        templates.append(
            PhonemeTemplate(
                arpabet=arpabet,
                rama_coord=rama,
                varga=int(varga_idx),
                sthana=int(sthana_idx),
                sound_class=sound_class,
                f0_required=f0_required,
                f1_center=f1,
                f2_center=f2,
                centroid_min=c_min,
                centroid_max=c_max,
                mfcc_center=mfcc,
            )
        )

    return tuple(templates)


PHONEME_TEMPLATES: Final[Tuple[PhonemeTemplate, ...]] = _build_templates()

# Pre-index: varga → list of template indices (for fast filtering)
_TEMPLATES_BY_VARGA: Final[Dict[int, List[int]]] = {}
for _i, _t in enumerate(PHONEME_TEMPLATES):
    _TEMPLATES_BY_VARGA.setdefault(_t.varga, []).append(_i)


# =============================================================================
# FRAME SCORING (audio frame → phoneme candidates)
# =============================================================================


def score_frame(
    packed: int,
    mfcc: Tuple[int, ...] = (),
    f1: int = 0,
    f2: int = 0,
    prev_rms: int = -1,
) -> List[Tuple[str, float]]:
    """Score an audio frame against all phoneme templates.

    Returns top-3 (arpabet, score) candidates sorted by score descending.
    Score range: 0.0 (no match) to 1.0 (perfect match).

    When MFCC vector is provided (13 ints), weights are:
        MFCC similarity: 0.50, voicing: 0.20, varga: 0.15, energy class: 0.15
    Without MFCC, falls back to legacy weights:
        voicing: 0.30, varga: 0.20, centroid: 0.20, formant: 0.30

    prev_rms: RMS of previous frame (-1 = unknown). Used for temporal
    stop detection: burst onset (prev_rms < 20) or energy dip strongly
    indicates a stop consonant, not a nasal or continuant.
    """
    rms, varga, f0_x10, centroid_100 = unpack_frame(packed)

    if rms < 20:
        return []  # silence

    has_mfcc = len(mfcc) >= 13 and any(c != 0 for c in mfcc)
    is_voiced = f0_x10 > 0
    is_onset = prev_rms >= 0 and prev_rms < 20 and rms >= 20
    is_rms_dip = prev_rms >= 0 and rms < prev_rms * 6 // 10 and prev_rms > 80
    candidates: List[Tuple[str, float]] = []

    # Pre-filter: only templates matching frame varga (± 1 neighbor)
    check_vargas = {varga}
    if varga > 0:
        check_vargas.add(varga - 1)
    if varga < 4:
        check_vargas.add(varga + 1)

    check_indices: List[int] = []
    for v in check_vargas:
        check_indices.extend(_TEMPLATES_BY_VARGA.get(v, []))

    for idx in check_indices:
        t = PHONEME_TEMPLATES[idx]
        score = 0.0

        if has_mfcc and t.mfcc_center:
            # --- MFCC path (primary discriminator) ---

            # MFCC cosine similarity (0.50 weight)
            score += 0.50 * _mfcc_similarity(mfcc, t.mfcc_center)

            # Voicing match (0.20 weight)
            if t.f0_required == is_voiced:
                score += 0.20
            elif not t.f0_required and not is_voiced:
                score += 0.20

            # Varga match (0.15 weight)
            if t.varga == varga:
                score += 0.15
            else:
                score += 0.04

            # Energy class (0.15 weight) — RMS-based
            if rms < 50:
                energy_class = 0  # whisper
            elif rms < 120:
                energy_class = 1  # normal
            else:
                energy_class = 2  # loud

            # Vowels are typically louder, fricatives quieter
            if t.sound_class == 0 and energy_class >= 1:
                score += 0.15
            elif t.sound_class == 2 and energy_class <= 1:
                score += 0.15
            elif t.sound_class == 1:
                score += 0.10  # stops vary
            else:
                score += 0.05

        else:
            # --- Formant path (primary for real audio) ---
            # Weights: voicing(0.15) + varga(0.15) + sound_class(0.15)
            #        + centroid(0.15) + formant(0.40)
            # Formant match is THE key vowel discriminator (F1/F2 fingerprint).

            # Voicing match (0.15 weight)
            if t.f0_required == is_voiced:
                score += 0.15
            elif not t.f0_required and not is_voiced:
                score += 0.15

            # Varga match (0.15 weight)
            if t.varga == varga:
                score += 0.15
            else:
                score += 0.03

            # Sound class match (0.15 weight) — vowel vs consonant vs fricative
            # Determined by RMS + centroid pattern:
            #   Vowels: high RMS (>100), voiced, moderate centroid
            #   Stops:  RMS burst then drop, or low RMS
            #   Nasals: medium RMS (40-120), voiced, low centroid (<80)
            #   Fricatives/Sibilants: noise = high centroid (>200), any voicing
            #   Semivowels: medium RMS, voiced, moderate centroid
            is_high_rms = rms > 100
            is_mid_rms = 40 <= rms <= 120
            is_low_rms = rms < 50
            is_high_centroid = centroid_100 > 200
            is_low_centroid = centroid_100 < 80

            if t.sound_class == 0:  # SVARA (vowel)
                if is_onset or is_rms_dip:
                    score += 0.01  # vowels don't burst from silence
                elif is_voiced and is_high_rms and not is_high_centroid:
                    score += 0.15  # strong vowel evidence
                elif is_voiced and is_mid_rms:
                    score += 0.08  # weak vowel
                else:
                    score += 0.01  # unlikely vowel
            elif t.sound_class == 1:  # SPARSHA (stop/nasal)
                is_nasal = t.sthana == int(SthanaIndex.ANUNASIKA)
                if is_nasal:
                    if is_onset or is_rms_dip:
                        score += 0.01  # nasals don't burst
                    elif is_voiced and is_low_centroid and is_mid_rms:
                        score += 0.15
                    elif is_voiced and is_low_centroid:
                        score += 0.08
                    else:
                        score += 0.01
                else:
                    # Stop consonants — temporal context is THE discriminator
                    if is_onset:
                        score += 0.15  # burst from silence = stop
                    elif is_rms_dip:
                        score += 0.12  # energy dip = stop closure
                    elif not is_voiced and is_low_rms:
                        score += 0.15  # unvoiced stop
                    elif is_voiced and not is_high_rms:
                        score += 0.10  # voiced stop
                    elif not is_voiced:
                        score += 0.08
                    else:
                        score += 0.03
            else:  # SHESHA (semivowel/sibilant/fricative)
                is_sibilant = t.arpabet in ("S", "SH", "Z", "ZH", "HH")
                if is_onset or is_rms_dip:
                    score += 0.01  # continuants don't burst
                elif is_sibilant:
                    if is_high_centroid:
                        score += 0.15
                    elif centroid_100 > 150:
                        score += 0.08
                    else:
                        score += 0.01
                else:
                    if is_voiced and is_mid_rms:
                        score += 0.12
                    elif is_voiced:
                        score += 0.06
                    else:
                        score += 0.01

            # Centroid detail (0.15 weight)
            if t.centroid_min <= centroid_100 <= t.centroid_max:
                score += 0.15
            elif centroid_100 < t.centroid_min:
                dist = t.centroid_min - centroid_100
                score += max(0.0, 0.15 - dist * 0.002)
            else:
                dist = centroid_100 - t.centroid_max
                score += max(0.0, 0.15 - dist * 0.002)

            # Formant match (0.40 weight — THE vowel discriminator)
            # F1 = jaw height (open/close), F2 = tongue position (front/back)
            # Absolute Hz distance / fixed range avoids bias toward high-F2 templates.
            if t.f1_center > 0 and f1 > 0 and f2 > 0:
                f1_err = abs(f1 - t.f1_center) / 500.0  # F1 range ~200-800
                f2_err = abs(f2 - t.f2_center) / 1500.0  # F2 range ~800-2500
                formant_score = max(0.0, 1.0 - (f1_err + f2_err))
                score += 0.40 * formant_score
            elif t.f1_center == 0:
                # Consonant template — no formant expected, partial credit
                score += 0.15

        candidates.append((t.arpabet, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:3]


def _frames_to_phoneme_coords(
    frames: Sequence[int],
    raw_samples: object = None,
    sample_rate: int = 44100,
    hop_ms: int = 10,
    n_fft: int = 1024,
    mfcc_frames: "Sequence[Tuple[int, ...]] | None" = None,
) -> Tuple[int, ...]:
    """Convert packed audio frames to RAMA coords via ARPAbet template scoring.

    For each voiced frame:
        1. Use MFCC vector (if available) or extract formants as fallback
        2. score_frame(packed, mfcc, f1, f2) → top-1 ARPAbet phoneme
        3. ARPABET_TO_RAMA[phoneme] → RAMA coordinate
        4. Majority-vote smoothing (window=5) to reduce frame-level noise

    This is the PHONEME DETECTION path (not the resonance path).
    """
    import numpy as np
    from vibe_core.mahamantra.sound.shabda_intake import extract_formants

    hop = int(sample_rate * hop_ms / 1000)
    has_raw = raw_samples is not None and isinstance(raw_samples, np.ndarray)
    has_mfcc = mfcc_frames is not None and len(mfcc_frames) > 0

    # Phase 1: Per-frame best phoneme
    raw_arpabets: List[str] = []
    prev_frame_rms = 0
    for i, frame in enumerate(frames):
        rms = frame & 0xFF
        if rms < 15:
            raw_arpabets.append("")  # silence marker
            prev_frame_rms = rms
            continue

        # Extract formants from raw audio (primary vowel discriminator)
        f1, f2 = 0, 0
        if has_raw:
            start_sample = i * hop
            end_sample = start_sample + n_fft
            if end_sample <= len(raw_samples):
                audio_frame = raw_samples[start_sample:end_sample]
                f1, f2 = extract_formants(audio_frame, sample_rate)

        candidates = score_frame(frame, f1=f1, f2=f2, prev_rms=prev_frame_rms)
        if candidates:
            raw_arpabets.append(candidates[0][0])
        else:
            raw_arpabets.append("")
        prev_frame_rms = rms

    if not raw_arpabets:
        return ()

    # Phase 2: Majority-vote smoothing (window=5)
    smoothed: List[str] = []
    window = 5
    half_w = window // 2
    for i in range(len(raw_arpabets)):
        if not raw_arpabets[i]:
            smoothed.append("")
            continue
        # Count phonemes in window
        counts: Dict[str, int] = {}
        for j in range(max(0, i - half_w), min(len(raw_arpabets), i + half_w + 1)):
            p = raw_arpabets[j]
            if p:
                counts[p] = counts.get(p, 0) + 1
        if counts:
            best = max(counts, key=lambda k: counts[k])
            smoothed.append(best)
        else:
            smoothed.append("")

    # Phase 3: Convert to RAMA coords
    coords: List[int] = []
    for arpabet in smoothed:
        if not arpabet:
            continue
        rama = ARPABET_TO_RAMA.get(arpabet)
        if rama is not None:
            coords.append(rama)
    return tuple(coords)


# =============================================================================
# SEGMENTATION (stream → word-length segments)
# =============================================================================


@dataclass(frozen=True)
class Segment:
    """A word-length segment of audio frames."""

    start: int  # frame index (inclusive)
    end: int  # frame index (exclusive)
    frames: Tuple[int, ...]

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def duration_ms(self) -> int:
        return self.length * 10


# Segmentation thresholds — tuned for Prabhupada's speaking style
_SILENCE_RMS = 15  # lower threshold catches quieter pauses
_SILENCE_GAP = 2  # 2+ silent frames = word boundary (20ms)
_ENERGY_DIP_RMS = 80  # energy dip threshold (catches inter-word dips)
_ENERGY_DIP_GAP = 3  # 3+ low-energy frames = boundary (30ms)
_MIN_SEGMENT_FRAMES = 5  # 50ms minimum (discard shorter)
_MAX_SEGMENT_FRAMES = 40  # 400ms maximum (typical max single-word length)


def _split_at_rms_minimum(frames: Sequence[int], start: int, end: int) -> List[Tuple[int, int]]:
    """Split a long segment at its internal RMS minimum.

    Finds the frame with lowest RMS in the middle third of the segment,
    splits there. Recursively splits if pieces are still too long.
    Returns list of (start, end) pairs.
    """
    length = end - start
    if length <= _MAX_SEGMENT_FRAMES:
        return [(start, end)]

    # Search for RMS minimum in middle 60% of segment (avoid edges)
    search_start = start + length // 5
    search_end = end - length // 5
    if search_start >= search_end:
        search_start = start + 2
        search_end = end - 2

    min_rms = 256
    min_idx = (search_start + search_end) // 2
    for i in range(search_start, search_end):
        rms = frames[i] & 0xFF
        if rms < min_rms:
            min_rms = rms
            min_idx = i

    # Split at the minimum
    left = _split_at_rms_minimum(frames, start, min_idx)
    right = _split_at_rms_minimum(frames, min_idx, end)
    return left + right


def segment_stream(frames: Sequence[int]) -> List[Segment]:
    """Segment audio frames into word-length chunks.

    Two-pass approach:
    1. Find raw segments by silence (RMS < 15) and energy dips (RMS < 80)
    2. Split oversized segments (> 400ms) at internal RMS minima

    Returns list of Segments, each containing the packed frames.
    """
    if not frames:
        return []

    # Pass 1: Find raw segments by silence/dip boundaries
    raw_segments: List[Tuple[int, int]] = []  # (start, end)
    seg_start = -1
    silence_count = 0
    dip_count = 0

    for i, frame in enumerate(frames):
        rms = frame & 0xFF

        if rms < _SILENCE_RMS:
            silence_count += 1
            dip_count += 1
        elif rms < _ENERGY_DIP_RMS:
            silence_count = 0
            dip_count += 1
        else:
            silence_count = 0
            dip_count = 0

        if seg_start < 0 and rms >= _SILENCE_RMS:
            seg_start = i
            silence_count = 0
            dip_count = 0
            continue

        if seg_start < 0:
            continue

        is_boundary = silence_count >= _SILENCE_GAP or dip_count >= _ENERGY_DIP_GAP

        if is_boundary:
            seg_end = i - silence_count + 1
            if seg_end <= seg_start:
                seg_end = seg_start + 1
            if seg_end - seg_start >= _MIN_SEGMENT_FRAMES:
                raw_segments.append((seg_start, seg_end))
            seg_start = -1
            silence_count = 0
            dip_count = 0

    # Flush final segment
    if seg_start >= 0:
        seg_end = len(frames)
        while seg_end > seg_start and (frames[seg_end - 1] & 0xFF) < _SILENCE_RMS:
            seg_end -= 1
        if seg_end - seg_start >= _MIN_SEGMENT_FRAMES:
            raw_segments.append((seg_start, seg_end))

    # Pass 2: Split oversized segments at RMS minima
    segments: List[Segment] = []
    for s, e in raw_segments:
        pieces = _split_at_rms_minimum(frames, s, e)
        for ps, pe in pieces:
            if pe - ps >= _MIN_SEGMENT_FRAMES:
                segments.append(
                    Segment(
                        start=ps,
                        end=pe,
                        frames=tuple(frames[ps:pe]),
                    )
                )

    return segments


# =============================================================================
# COMMON ENGLISH VOCABULARY (top ~350 words for spoken English coverage)
# =============================================================================

_COMMON_ENGLISH: Final[Tuple[str, ...]] = (
    # Function words (articles, pronouns, prepositions, conjunctions)
    "a",
    "an",
    "the",
    "this",
    "that",
    "these",
    "those",
    "i",
    "me",
    "my",
    "we",
    "us",
    "our",
    "you",
    "your",
    "he",
    "him",
    "his",
    "she",
    "her",
    "it",
    "its",
    "they",
    "them",
    "their",
    "who",
    "what",
    "which",
    "where",
    "when",
    "how",
    "why",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "from",
    "by",
    "as",
    "up",
    "out",
    "about",
    "into",
    "over",
    "after",
    "under",
    "between",
    "and",
    "or",
    "but",
    "not",
    "no",
    "so",
    "if",
    "then",
    "than",
    "because",
    # Common verbs
    "is",
    "am",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "shall",
    "should",
    "can",
    "could",
    "may",
    "might",
    "must",
    "say",
    "said",
    "go",
    "went",
    "gone",
    "come",
    "came",
    "get",
    "got",
    "give",
    "gave",
    "take",
    "took",
    "make",
    "made",
    "know",
    "knew",
    "think",
    "thought",
    "see",
    "saw",
    "want",
    "wanted",
    "look",
    "looked",
    "find",
    "found",
    "tell",
    "told",
    "ask",
    "asked",
    "use",
    "used",
    "try",
    "tried",
    "leave",
    "left",
    "call",
    "called",
    "keep",
    "kept",
    "let",
    "begin",
    "began",
    "seem",
    "seemed",
    "help",
    "show",
    "hear",
    "heard",
    "play",
    "run",
    "ran",
    "move",
    "live",
    "believe",
    "bring",
    "brought",
    "happen",
    "write",
    "wrote",
    "sit",
    "sat",
    "stand",
    "stood",
    "lose",
    "lost",
    "pay",
    "paid",
    "meet",
    "met",
    "set",
    "learn",
    "learned",
    "lead",
    "led",
    "understand",
    "understood",
    "watch",
    "follow",
    "stop",
    "stopped",
    "speak",
    "spoke",
    "read",
    "spend",
    "spent",
    "grow",
    "grew",
    "open",
    "opened",
    "walk",
    "walked",
    "win",
    "won",
    "teach",
    "develop",
    "preach",
    "preached",
    # Common nouns
    "time",
    "year",
    "people",
    "way",
    "day",
    "man",
    "woman",
    "child",
    "children",
    "world",
    "life",
    "hand",
    "part",
    "place",
    "case",
    "week",
    "company",
    "system",
    "program",
    "question",
    "work",
    "government",
    "number",
    "night",
    "point",
    "home",
    "water",
    "room",
    "mother",
    "area",
    "money",
    "story",
    "fact",
    "month",
    "lot",
    "right",
    "study",
    "book",
    "eye",
    "job",
    "word",
    "business",
    "issue",
    "side",
    "kind",
    "head",
    "house",
    "service",
    "friend",
    "father",
    "power",
    "hour",
    "game",
    "line",
    "end",
    "members",
    "family",
    "law",
    "car",
    "city",
    "community",
    "name",
    "boy",
    "boys",
    "girl",
    "girls",
    "group",
    "country",
    "problem",
    "god",
    "lord",
    "soul",
    "spirit",
    "mind",
    "body",
    "heart",
    "love",
    "truth",
    "peace",
    "light",
    "faith",
    "hope",
    # Common adjectives
    "good",
    "new",
    "first",
    "last",
    "long",
    "great",
    "little",
    "own",
    "other",
    "old",
    "right",
    "big",
    "high",
    "different",
    "small",
    "large",
    "next",
    "early",
    "young",
    "important",
    "few",
    "public",
    "bad",
    "same",
    "able",
    "real",
    "best",
    "better",
    "sure",
    "free",
    "true",
    "whole",
    "nice",
    "dear",
    # Common adverbs
    "just",
    "also",
    "very",
    "often",
    "however",
    "too",
    "usually",
    "really",
    "already",
    "always",
    "never",
    "sometimes",
    "together",
    "likely",
    "simply",
    "generally",
    "instead",
    "actually",
    "exactly",
    "enough",
    "well",
    "here",
    "there",
    "now",
    "only",
    "quite",
    "still",
    "back",
    "even",
    "ever",
    "ago",
    "once",
    "much",
    "far",
    "away",
    "again",
    "perhaps",
    "maybe",
    "soon",
    "fortunately",
    "unfortunately",
    "certainly",
    "definitely",
    # Prabhupada-specific vocabulary
    "consciousness",
    "spiritual",
    "material",
    "devotional",
    "transcendental",
    "transcendentalists",
    "supreme",
    "absolute",
    "devotee",
    "devotees",
    "temple",
    "chanting",
    "mantra",
    "meditation",
    "philosophy",
    "knowledge",
    "ignorance",
    "liberation",
    "bondage",
    "karma",
    "dharma",
    "yoga",
    "guru",
    "master",
    "disciple",
    "student",
    "teacher",
    "preaching",
    "mission",
    "movement",
    "society",
    "international",
    "enthusiastic",
    "wonderful",
    "beautiful",
    "merciful",
    "gospel",
    "message",
    "instruction",
    "scripture",
    "bhagavad",
    "gita",
    "vedic",
    "vedas",
    "upanishad",
    "india",
    "america",
    "new",
    "york",
    "san",
    "francisco",
    "eh",
    "ehm",
    "um",
    "uh",
    "oh",
    "yes",
    "no",
    "some",
    "every",
    "many",
    "much",
    "more",
    "most",
    "any",
    "all",
    "each",
    "both",
    "few",
    "several",
)


# =============================================================================
# PRONUNCIATION DICTIONARY (word → RAMA coords)
# =============================================================================


class PronunciationDict:
    """Pronunciation dictionary mapping words to RAMA coordinate sequences.

    Sanskrit words loaded from rama_lexicon.json (4,127 entries, exact coords).
    English words from lexicon meanings + common English vocabulary.

    Lazy-initialized, cached.
    """

    def __init__(self) -> None:
        self._sanskrit: Optional[Dict[str, Tuple[int, ...]]] = None
        self._english: Optional[Dict[str, Tuple[int, ...]]] = None
        self._by_first_coord: Optional[Dict[int, List[str]]] = None
        self._by_length: Optional[Dict[int, List[str]]] = None

    def _add_english_word(self, token: str, coords: Tuple[int, ...]) -> None:
        """Register a single English word in the dictionary."""
        assert self._english is not None
        assert self._by_first_coord is not None
        assert self._by_length is not None
        self._english[token] = coords
        fc = coords[0]
        self._by_first_coord.setdefault(fc, []).append(token)
        self._by_length.setdefault(len(coords), []).append(token)

    @staticmethod
    def _cmu_to_rama(arpabet_seq: Sequence[str]) -> Tuple[int, ...]:
        """Convert CMU ARPAbet phoneme sequence to RAMA coords.

        Strips stress markers (0/1/2) from vowels, maps via ARPABET_TO_RAMA.
        Skips unknown phonemes.
        """
        coords: List[int] = []
        for phone in arpabet_seq:
            clean = phone.rstrip("012")
            rama = ARPABET_TO_RAMA.get(clean)
            if rama is not None:
                coords.append(rama)
        return tuple(coords)

    def _ensure_loaded(self) -> None:
        if self._sanskrit is not None:
            return

        self._sanskrit = {}
        self._english = {}
        self._by_first_coord = {}
        self._by_length = {}

        # 1. Load Sanskrit from SemanticIndex
        from vibe_core.mahamantra.substrate.encoding.semantic_index import get_index

        index = get_index()
        for coord in range(49):
            for word in index.by_rama_position(coord):
                self._sanskrit[word.sanskrit] = word.coords
                fc = word.coords[0] if word.coords else -1
                self._by_first_coord.setdefault(fc, []).append(word.sanskrit)
                self._by_length.setdefault(len(word.coords), []).append(word.sanskrit)

        # 2. Load CMU Pronouncing Dictionary for English words.
        #    CMU dict gives ARPAbet phonemes → ARPABET_TO_RAMA → RAMA coords.
        #    This aligns English dictionary coords with the audio decoder path
        #    (both go through ARPAbet, not letter-by-letter encode_text).
        cmu: dict = {}
        try:
            from nltk.corpus import cmudict

            cmu = cmudict.dict()
        except Exception:
            logger.warning("CMU dict not available, falling back to encode_text")

        from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text

        # 2a. English from lexicon meanings
        seen_english: set = set()
        for coord in range(49):
            for word in index.by_rama_position(coord):
                for meaning in word.meanings:
                    for token in meaning.lower().split():
                        token = token.strip(".,;:()[]\"'!?")
                        if len(token) < 2 or token in seen_english:
                            continue
                        seen_english.add(token)
                        # CMU dict first (phoneme-accurate), encode_text fallback
                        pronunciations = cmu.get(token)
                        if pronunciations:
                            coords = self._cmu_to_rama(pronunciations[0])
                        else:
                            coords = encode_text(token)
                        if coords:
                            self._add_english_word(token, coords)

        # 2b. Common English vocabulary
        for token in _COMMON_ENGLISH:
            if token not in seen_english and token not in self._english:
                pronunciations = cmu.get(token)
                if pronunciations:
                    coords = self._cmu_to_rama(pronunciations[0])
                else:
                    coords = encode_text(token)
                if coords:
                    self._add_english_word(token, coords)

        logger.info(
            "PronunciationDict loaded: %d Sanskrit, %d English (CMU: %d available)",
            len(self._sanskrit),
            len(self._english),
            len(cmu),
        )

    def lookup(self, word: str) -> Optional[Tuple[int, ...]]:
        """Get RAMA coords for a word."""
        self._ensure_loaded()
        assert self._sanskrit is not None and self._english is not None
        return self._sanskrit.get(word) or self._english.get(word.lower())

    def candidates_for_segment(
        self,
        first_coord: int,
        length: int,
        length_tolerance: int = 2,
    ) -> List[Tuple[str, Tuple[int, ...]]]:
        """Get candidate words matching first coordinate and approximate length."""
        self._ensure_loaded()
        assert self._by_first_coord is not None and self._by_length is not None
        assert self._sanskrit is not None and self._english is not None

        by_coord = set(self._by_first_coord.get(first_coord, []))

        by_len: set = set()
        for l in range(max(1, length - length_tolerance), length + length_tolerance + 1):
            by_len.update(self._by_length.get(l, []))

        matches = by_coord & by_len
        result: List[Tuple[str, Tuple[int, ...]]] = []
        for w in matches:
            coords = self._sanskrit.get(w) or self._english.get(w.lower())
            if coords is not None:
                result.append((w, coords))

        return result

    def all_candidates_for_length(
        self,
        length: int,
        length_tolerance: int = 2,
    ) -> List[Tuple[str, Tuple[int, ...]]]:
        """Get ALL candidate words matching approximate length (no coord filter)."""
        self._ensure_loaded()
        assert self._by_length is not None
        assert self._sanskrit is not None and self._english is not None

        result: List[Tuple[str, Tuple[int, ...]]] = []
        seen: set = set()
        for l in range(max(1, length - length_tolerance), length + length_tolerance + 1):
            for w in self._by_length.get(l, []):
                if w in seen:
                    continue
                seen.add(w)
                coords = self._sanskrit.get(w) or self._english.get(w.lower())
                if coords is not None:
                    result.append((w, coords))
        return result

    @property
    def sanskrit_count(self) -> int:
        self._ensure_loaded()
        assert self._sanskrit is not None
        return len(self._sanskrit)

    @property
    def english_count(self) -> int:
        self._ensure_loaded()
        assert self._english is not None
        return len(self._english)

    @property
    def total_count(self) -> int:
        return self.sanskrit_count + self.english_count


# Module-level singleton
_DICT: Optional[PronunciationDict] = None


def get_pronunciation_dict() -> PronunciationDict:
    """Get or create the global PronunciationDict singleton."""
    global _DICT
    if _DICT is None:
        _DICT = PronunciationDict()
    return _DICT


# =============================================================================
# SCORING (RAMA edit distance between observed and candidate)
# =============================================================================


def _score_candidate(
    observed: Tuple[int, ...],
    candidate: Tuple[int, ...],
) -> float:
    """Element-weighted edit distance with strict length gate.

    Scoring:
        Same coord: cost 0
        Same element: cost 0.3
        Same varga class: cost 0.6
        Different: cost 1.0

    Length gate: candidates whose length differs by >60% are rejected (score 0).
    Length penalty: score multiplied by min(n,m)/max(n,m).

    Returns: score in [0.0, 1.0], higher = better match.
    """
    n = len(observed)
    m = len(candidate)

    if n == 0 or m == 0:
        return 0.0

    # Strict length gate: reject grossly mismatched lengths
    max_len = max(n, m)
    min_len = min(n, m)
    if min_len / max_len < 0.4:
        return 0.0

    # Dynamic programming edit distance with weighted substitution costs
    prev = list(range(0, (m + 1) * 10, 10))
    curr = [0] * (m + 1)

    for i in range(1, n + 1):
        curr[0] = i * 10
        for j in range(1, m + 1):
            if observed[i - 1] == candidate[j - 1]:
                sub_cost = 0
            elif COORD_ELEMENT[observed[i - 1]] == COORD_ELEMENT[candidate[j - 1]]:
                sub_cost = 3
            elif COORD_VARGA[observed[i - 1]] == COORD_VARGA[candidate[j - 1]]:
                sub_cost = 6
            else:
                sub_cost = 10

            curr[j] = min(
                prev[j] + 10,  # deletion
                curr[j - 1] + 10,  # insertion
                prev[j - 1] + sub_cost,  # substitution
            )
        prev, curr = curr, prev

    edit_dist = prev[m] / 10.0
    raw_score = 1.0 - (edit_dist / max_len)
    length_penalty = min_len / max_len
    return max(0.0, min(1.0, raw_score * length_penalty))


# =============================================================================
# CTC-STYLE DEDUPLICATION (frame-level → phoneme-level)
# =============================================================================


def _dedup_coords(coords: Tuple[int, ...]) -> Tuple[int, ...]:
    """Collapse consecutive identical RAMA coordinates.

    Frame-level coords repeat the same value for the duration of each phoneme.
    A 300ms /a/ at 10ms/frame → 30× coord 0. This collapses to 1× coord 0.

    Standard CTC (Connectionist Temporal Classification) approach:
    (5, 5, 5, 12, 12, 12, 12, 42, 42) → (5, 12, 42)
    """
    if not coords:
        return ()
    result: List[int] = [coords[0]]
    for c in coords[1:]:
        if c != result[-1]:
            result.append(c)
    return tuple(result)


def _stable_coords(coords: Tuple[int, ...], min_run: int = 3) -> Tuple[int, ...]:
    """Run-length filter: keep only coords that persist for ≥ min_run frames.

    Phonemes last ~60-120ms (6-12 frames at 10ms). Transitional frames between
    phonemes produce 1-2 frame blips of different coords. This filter removes
    those blips, keeping only stable phoneme regions.

    Example (min_run=3):
        (5, 5, 5, 12, 5, 5, 5, 5, 42, 42, 42) → (5, 5, 42)
        The single 12 is a transitional blip (1 frame), removed.
        Both runs of 5 merge into one phoneme after dedup.
        The 42 run (3 frames) qualifies.

    Returns: deduped stable coords (no consecutive duplicates).
    """
    if not coords:
        return ()

    # Phase 1: Run-length encode
    runs: List[Tuple[int, int]] = []  # (coord, count)
    current = coords[0]
    count = 1
    for c in coords[1:]:
        if c == current:
            count += 1
        else:
            runs.append((current, count))
            current = c
            count = 1
    runs.append((current, count))

    # Phase 2: Keep only stable runs (≥ min_run frames)
    stable = [coord for coord, cnt in runs if cnt >= min_run]

    # Phase 3: Dedup (consecutive same coords from merged short-gap runs)
    if not stable:
        # Fallback: if nothing survives the filter, use regular dedup
        return _dedup_coords(coords)
    result: List[int] = [stable[0]]
    for c in stable[1:]:
        if c != result[-1]:
            result.append(c)
    return tuple(result)


# =============================================================================
# TRANSCRIPT DATA TYPES
# =============================================================================


@dataclass(frozen=True)
class TranscriptWord:
    """A single recognized word in the transcript."""

    word: str
    confidence: float  # 0-1
    language: str  # "sanskrit" / "english"
    rama_coords: Tuple[int, ...]
    start_ms: int
    end_ms: int


@dataclass(frozen=True)
class Transcript:
    """Complete transcription result."""

    words: Tuple[TranscriptWord, ...]
    duration_ms: int
    source: str

    @property
    def text(self) -> str:
        return " ".join(w.word for w in self.words)


# =============================================================================
# SHABDA DECODER (main class)
# =============================================================================


class ShabdaDecoder:
    """Deterministic speech-to-text decoder.

    Uses RAMA coordinate space to match audio segments against a pronunciation
    dictionary of Sanskrit (from Gita lexicon) and English words.

    No ML models. No external APIs. Pure phonetic algebra.

    Usage:
        decoder = ShabdaDecoder()
        transcript = decoder.transcribe(stream)
        print(transcript.text)
    """

    def __init__(
        self,
        language: str = "both",
        min_confidence: float = 0.3,
        use_formants: bool = True,
        language_preference: str = "english",
    ) -> None:
        self._language = language
        self._min_confidence = min_confidence
        self._use_formants = use_formants
        self._language_preference = language_preference
        self._dict = get_pronunciation_dict()

    def transcribe(self, stream: ShabdaStream) -> Transcript:
        """Transcribe a full ShabdaStream to text."""
        segments = segment_stream(stream.frames)
        words: List[TranscriptWord] = []

        for seg in segments:
            result = self._decode_segment(
                seg,
                raw_samples=stream.raw_samples,
                sample_rate=stream.sample_rate,
                hop_ms=stream.hop_ms,
                n_fft=stream.n_fft,
                mfcc_frames=stream.mfcc_frames,
            )
            if result is not None:
                words.append(result)

        return Transcript(
            words=tuple(words),
            duration_ms=stream.duration_ms,
            source=stream.source,
        )

    def transcribe_segment(
        self,
        frames: Sequence[int],
        raw_samples: object = None,
        sr: int = 44100,
    ) -> List[TranscriptWord]:
        """Transcribe a pre-segmented sequence of packed frames."""
        segments = segment_stream(frames)
        words: List[TranscriptWord] = []
        for seg in segments:
            result = self._decode_segment(seg)
            if result is not None:
                words.append(result)
        return words

    def _decode_segment(
        self,
        seg: Segment,
        raw_samples: object = None,
        sample_rate: int = 44100,
        hop_ms: int = 10,
        n_fft: int = 1024,
        mfcc_frames: "Sequence[Tuple[int, ...]] | None" = None,
    ) -> Optional[TranscriptWord]:
        """Decode a single segment into a word.

        Uses _frames_to_phoneme_coords (ARPAbet template scoring path):
            frame → score_frame() → top-1 ARPAbet → ARPABET_TO_RAMA → RAMA coord
        Then matches against PronunciationDict (also ARPAbet → RAMA via CMU dict).

        Both paths go through ARPAbet → ARPABET_TO_RAMA, so coords align.
        """
        import numpy as np

        # Slice raw samples for this segment (if available)
        seg_raw = None
        if raw_samples is not None and isinstance(raw_samples, np.ndarray):
            hop = int(sample_rate * hop_ms / 1000)
            start_sample = seg.start * hop
            end_sample = (seg.end + 1) * hop + n_fft
            if end_sample <= len(raw_samples):
                seg_raw = raw_samples[start_sample:end_sample]

        # Slice MFCC frames for this segment
        seg_mfcc = None
        if mfcc_frames is not None:
            seg_mfcc = mfcc_frames[seg.start : seg.end]

        # ARPAbet path: frame → score_frame → top-1 ARPAbet → ARPABET_TO_RAMA
        raw_coords = _frames_to_phoneme_coords(
            seg.frames,
            seg_raw,
            sample_rate,
            hop_ms,
            n_fft,
            mfcc_frames=seg_mfcc,
        )
        if not raw_coords:
            return None

        # Stable-coord filter: keep only coords persisting ≥ 3 frames (30ms),
        # removing transitional noise between phonemes.
        rama_coords = _stable_coords(raw_coords, min_run=3)
        if not rama_coords:
            return None

        # Get candidates from dictionary.
        # Both audio and dictionary coords go through ARPAbet → ARPABET_TO_RAMA,
        # so first_coord matching is tight (±1 for minor varga neighbor tolerance).
        first_coord = rama_coords[0]
        coord_len = len(rama_coords)
        candidates: List[Tuple[str, Tuple[int, ...]]] = []

        for fc in (first_coord, first_coord - 1, first_coord + 1):
            if 0 <= fc < 49:
                candidates.extend(self._dict.candidates_for_segment(fc, coord_len, length_tolerance=3))

        # Fallback: if too few candidates, search by length only
        if len(candidates) < 10:
            candidates.extend(self._dict.all_candidates_for_length(coord_len, length_tolerance=2))

        if not candidates:
            return None

        # Score all candidates
        best_word = ""
        best_score = 0.0
        best_coords: Tuple[int, ...] = ()

        seen: set = set()
        is_sanskrit = self._dict._sanskrit or set()
        pref_bonus = 0.08 if self._language_preference != "both" else 0.0
        for word, word_coords in candidates:
            if word in seen:
                continue
            seen.add(word)
            score = _score_candidate(rama_coords, word_coords)
            # Language preference: small bonus for preferred language
            if pref_bonus > 0.0:
                word_is_sanskrit = word in is_sanskrit
                if self._language_preference == "english" and not word_is_sanskrit:
                    score += pref_bonus
                elif self._language_preference == "sanskrit" and word_is_sanskrit:
                    score += pref_bonus
            if score > best_score:
                best_score = score
                best_word = word
                best_coords = word_coords

        if best_score < self._min_confidence:
            return None

        # Determine language
        assert self._dict._sanskrit is not None
        lang = "sanskrit" if best_word in self._dict._sanskrit else "english"

        return TranscriptWord(
            word=best_word,
            confidence=best_score,
            language=lang,
            rama_coords=best_coords,
            start_ms=seg.start * 10,
            end_ms=seg.end * 10,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PhonemeTemplate",
    "PHONEME_TEMPLATES",
    "Segment",
    "TranscriptWord",
    "Transcript",
    "ShabdaDecoder",
    "PronunciationDict",
    "get_pronunciation_dict",
    "score_frame",
    "segment_stream",
    "_dedup_coords",
    "_stable_coords",
    "_frames_to_phoneme_coords",
    "_mfcc_similarity",
]
