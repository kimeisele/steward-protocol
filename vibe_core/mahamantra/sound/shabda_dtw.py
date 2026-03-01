"""
SHABDA DTW — Dynamic Time Warping Speech Matcher
==================================================

Late-binding speech recognition: instead of classifying each frame into a phoneme
(early binding, structurally broken for consonants), we keep the audio as an MFCC
matrix and compare it against word-level MFCC templates via DTW.

Pipeline:
    1. Audio segment → MFCC matrix (13 coefficients × N frames)
    2. Dictionary word → phoneme sequence (CMU dict) → synthetic MFCC template
    3. DTW(audio_mfcc, template_mfcc) → normalized alignment cost
    4. Lowest cost = best match

The synthetic MFCC templates are generated from acoustic first principles:
    - Vowels: spectral envelope from F1/F2 formant peaks → mel filterbank → DCT
    - Stops: silence frame + burst frame (high-energy broadband)
    - Nasals: low-frequency resonance + anti-formant
    - Fricatives: high-frequency noise band
    - Semivowels: formant glides

No ML models. Pure signal processing + linear algebra.

References:
    - Sakoe & Chiba (1978): DTW for speech recognition
    - Davis & Mermelstein (1980): MFCC extraction
    - Peterson & Barney (1952) + Prabhupada calibration: formant values
"""

from __future__ import annotations

import math
from typing import Dict, Final, List, Optional, Sequence, Tuple

import numpy as np
from scipy.fft import dct

# =============================================================================
# PHONEME MFCC PROFILES
# =============================================================================

# Speaker-calibrated formant values (from experiment 21, Prabhupada japa).
# Each vowel: (F1_Hz, F2_Hz, duration_frames)
# Duration: short vowels ~4 frames, long vowels ~6, diphthongs ~8
_VOWEL_PARAMS: Final[Dict[str, Tuple[int, int, int]]] = {
    "AA": (650, 1550, 5),  # /ɑ/ father
    "AE": (580, 2050, 5),  # /æ/ bat
    "AH": (450, 1550, 4),  # /ʌ/ but — most common, short
    "AO": (500, 1200, 5),  # /ɔ/ bought
    "AW": (620, 1450, 6),  # /aʊ/ bout (diphthong)
    "AY": (620, 1550, 6),  # /aɪ/ bite (diphthong)
    "EH": (490, 2200, 4),  # /ɛ/ bet
    "EY": (360, 2550, 6),  # /eɪ/ bait (diphthong)
    "ER": (420, 1700, 5),  # /ɝ/ bird
    "IH": (340, 2300, 4),  # /ɪ/ bit — short
    "IY": (250, 2650, 5),  # /i/ beat
    "OW": (400, 1200, 6),  # /oʊ/ boat (diphthong)
    "OY": (400, 1200, 6),  # /ɔɪ/ boy (diphthong)
    "UH": (310, 1350, 4),  # /ʊ/ book — short
    "UW": (270, 1250, 5),  # /u/ boot
}

# Consonant parameters: (type, duration_frames, spectral_character)
# type: "stop_v"=voiced stop, "stop_u"=unvoiced stop, "nasal", "fric_v"=voiced fricative,
#       "fric_u"=unvoiced fricative, "affricate", "semivowel", "liquid", "glide"
# spectral_character: centroid_hz (where energy concentrates)
_CONSONANT_PARAMS: Final[Dict[str, Tuple[str, int, int]]] = {
    # Stops (1 silence + 1 burst = 2 frames)
    "B": ("stop_v", 2, 800),
    "D": ("stop_v", 2, 2500),
    "G": ("stop_v", 2, 1500),
    "P": ("stop_u", 2, 800),
    "T": ("stop_u", 2, 3500),
    "K": ("stop_u", 2, 2000),
    # Affricates (2-3 frames)
    "CH": ("affricate", 3, 3500),
    "JH": ("affricate", 3, 2500),
    # Fricatives (3-4 frames)
    "F": ("fric_u", 3, 4000),
    "V": ("fric_v", 3, 3500),
    "TH": ("fric_u", 3, 5000),
    "DH": ("fric_v", 3, 3000),
    "S": ("fric_u", 3, 5500),
    "Z": ("fric_v", 3, 4500),
    "SH": ("fric_u", 3, 4000),
    "ZH": ("fric_v", 3, 3500),
    "HH": ("fric_u", 2, 1500),
    # Nasals (3 frames, low-freq resonance)
    "M": ("nasal", 3, 300),
    "N": ("nasal", 3, 400),
    "NG": ("nasal", 3, 350),
    # Liquids/Glides (3-4 frames)
    "L": ("liquid", 3, 500),
    "R": ("liquid", 3, 1200),
    "W": ("glide", 3, 600),
    "Y": ("glide", 3, 2200),
}

# Standard MFCC extraction parameters (must match shabda_intake.py)
_SAMPLE_RATE = 44100
_N_FFT = 1024
_N_MELS = 26
_N_MFCC = 13


def _mel(hz: float) -> float:
    """Hz → Mel scale."""
    return 2595.0 * math.log10(1.0 + hz / 700.0)


def _hz(mel_val: float) -> float:
    """Mel → Hz."""
    return 700.0 * (10.0 ** (mel_val / 2595.0) - 1.0)


def _mel_filterbank(sr: int = _SAMPLE_RATE, n_fft: int = _N_FFT, n_mels: int = _N_MELS) -> np.ndarray:
    """Build mel filterbank matrix [n_mels × n_fft//2]."""
    n_freq = n_fft // 2
    mel_lo = _mel(0)
    mel_hi = _mel(sr / 2)
    mel_points = np.linspace(mel_lo, mel_hi, n_mels + 2)
    hz_points = np.array([_hz(m) for m in mel_points])
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)

    fb = np.zeros((n_mels, n_freq))
    for i in range(n_mels):
        lo, center, hi = bin_points[i], bin_points[i + 1], bin_points[i + 2]
        for j in range(lo, min(center, n_freq)):
            fb[i, j] = (j - lo) / max(center - lo, 1)
        for j in range(center, min(hi, n_freq)):
            fb[i, j] = (hi - j) / max(hi - center, 1)
    return fb


# Cache the filterbank
_FB: Optional[np.ndarray] = None


def _get_fb() -> np.ndarray:
    global _FB
    if _FB is None:
        _FB = _mel_filterbank()
    return _FB


def _spectrum_to_mfcc(power_spectrum: np.ndarray) -> np.ndarray:
    """Power spectrum [n_fft//2] → 13 MFCC coefficients (float)."""
    fb = _get_fb()
    n_freq = min(len(power_spectrum), fb.shape[1])
    mel_energies = fb[:, :n_freq] @ power_spectrum[:n_freq]
    mel_energies = np.maximum(mel_energies, 1e-10)
    log_mel = np.log(mel_energies)
    cepstral = np.asarray(dct(log_mel, type=2, norm="ortho"))[:_N_MFCC]
    return cepstral


def _synthesize_vowel_spectrum(f1: int, f2: int) -> np.ndarray:
    """Generate a power spectrum with formant peaks at F1 and F2.

    Models the vocal tract as two resonant peaks (Gaussian bumps in
    the frequency domain) on a sloped baseline (glottal source).
    """
    n_freq = _N_FFT // 2
    freqs = np.arange(n_freq) * _SAMPLE_RATE / _N_FFT

    # Glottal source: -12 dB/octave slope
    source = 1.0 / np.maximum(freqs, 20.0) ** 2
    source = source / np.max(source)

    # Formant resonances (Gaussian peaks, bandwidth ~80-120 Hz)
    bw1 = 80.0  # F1 bandwidth
    bw2 = 100.0  # F2 bandwidth
    f1_peak = np.exp(-0.5 * ((freqs - f1) / bw1) ** 2)
    f2_peak = np.exp(-0.5 * ((freqs - f2) / bw2) ** 2)

    # F3 (fixed ~2700 Hz, weak) for naturalness
    f3_peak = 0.3 * np.exp(-0.5 * ((freqs - 2700) / 120.0) ** 2)

    spectrum = source * (1.0 + 8.0 * f1_peak + 6.0 * f2_peak + 3.0 * f3_peak)
    return spectrum


def _synthesize_noise_spectrum(centroid: int, bandwidth: int = 800) -> np.ndarray:
    """Generate a noise-band power spectrum centered at `centroid` Hz."""
    n_freq = _N_FFT // 2
    freqs = np.arange(n_freq) * _SAMPLE_RATE / _N_FFT
    spectrum = np.exp(-0.5 * ((freqs - centroid) / bandwidth) ** 2)
    return spectrum * 0.5  # lower energy than voiced


def _synthesize_nasal_spectrum(centroid: int) -> np.ndarray:
    """Generate nasal consonant spectrum: low-freq resonance + anti-formant."""
    n_freq = _N_FFT // 2
    freqs = np.arange(n_freq) * _SAMPLE_RATE / _N_FFT

    # Low-frequency nasal resonance (~250 Hz)
    nasal_peak = np.exp(-0.5 * ((freqs - 250) / 60.0) ** 2)
    # Anti-formant (notch) around centroid
    anti = 1.0 - 0.8 * np.exp(-0.5 * ((freqs - centroid) / 100.0) ** 2)

    spectrum = nasal_peak * anti * 0.3
    return spectrum


def _silence_mfcc() -> np.ndarray:
    """MFCC vector for silence (very low energy, flat spectrum)."""
    n_freq = _N_FFT // 2
    spectrum = np.ones(n_freq) * 1e-6
    return _spectrum_to_mfcc(spectrum)


def phoneme_mfcc_profile(arpabet: str) -> np.ndarray:
    """Generate MFCC profile for a phoneme: [n_frames × 13] matrix.

    Vowels: onset (transition in) + core + outro (transition out)
    Stops: silence + burst
    Fricatives: sustained noise
    Nasals: low-frequency sustained
    """
    if arpabet in _VOWEL_PARAMS:
        f1, f2, n_frames = _VOWEL_PARAMS[arpabet]
        core_spectrum = _synthesize_vowel_spectrum(f1, f2)
        core_mfcc = _spectrum_to_mfcc(core_spectrum)

        frames = []
        for i in range(n_frames):
            # Slight spectral tilt variation across vowel duration
            # (onset slightly more centralized, core stable, outro fading)
            t = i / max(n_frames - 1, 1)
            if t < 0.2:  # onset
                blend = 0.7 + 0.3 * (t / 0.2)
            elif t > 0.8:  # outro
                blend = 0.7 + 0.3 * ((1.0 - t) / 0.2)
            else:  # core
                blend = 1.0
            frames.append(core_mfcc * blend)
        return np.array(frames)

    elif arpabet in _CONSONANT_PARAMS:
        ctype, n_frames, centroid = _CONSONANT_PARAMS[arpabet]

        if ctype in ("stop_v", "stop_u"):
            # Stop: 1 frame silence + 1 frame burst
            sil = _silence_mfcc()
            burst = _spectrum_to_mfcc(_synthesize_noise_spectrum(centroid, 1200))
            return np.array([sil, burst])

        elif ctype == "affricate":
            # Affricate: silence + burst + fricative
            sil = _silence_mfcc()
            burst = _spectrum_to_mfcc(_synthesize_noise_spectrum(centroid, 1000))
            fric = _spectrum_to_mfcc(_synthesize_noise_spectrum(centroid, 600))
            return np.array([sil, burst, fric])

        elif ctype in ("fric_u", "fric_v"):
            noise = _spectrum_to_mfcc(_synthesize_noise_spectrum(centroid, 800))
            return np.array([noise] * n_frames)

        elif ctype == "nasal":
            nasal = _spectrum_to_mfcc(_synthesize_nasal_spectrum(centroid))
            return np.array([nasal] * n_frames)

        elif ctype in ("liquid", "glide", "semivowel"):
            # Liquid/glide: formant-like but with lower energy
            spectrum = _synthesize_vowel_spectrum(400, centroid)
            mfcc = _spectrum_to_mfcc(spectrum) * 0.8
            return np.array([mfcc] * n_frames)

    # Fallback: single silence frame
    return np.array([_silence_mfcc()])


def word_mfcc_template(arpabet_seq: Sequence[str]) -> np.ndarray:
    """Build word-level MFCC template by concatenating phoneme profiles.

    Input: ARPAbet phoneme sequence (e.g. ["B", "AH", "T"] for "but")
    Output: [total_frames × 13] MFCC matrix
    """
    profiles = [phoneme_mfcc_profile(phone.rstrip("012")) for phone in arpabet_seq]
    if not profiles:
        return np.array([_silence_mfcc()])
    return np.vstack(profiles)


# =============================================================================
# DYNAMIC TIME WARPING
# =============================================================================


def dtw_cost(
    audio_mfcc: np.ndarray,
    template_mfcc: np.ndarray,
) -> float:
    """Compute DTW alignment cost between audio and template MFCC matrices.

    Both inputs: [N × 13] and [M × 13] numpy arrays (float MFCC coefficients).

    Returns normalized alignment cost (lower = better match).
    Normalized by path length to make scores comparable across different
    word lengths.

    Sakoe-Chiba band constraint with radius = max(N, M) // 3
    to prevent degenerate warping.
    """
    n = len(audio_mfcc)
    m = len(template_mfcc)

    if n == 0 or m == 0:
        return float("inf")

    # Sakoe-Chiba band radius
    band = max(n, m) // 3 + 1

    # Cost matrix (only compute within band)
    INF = 1e30
    cost = np.full((n + 1, m + 1), INF)
    cost[0, 0] = 0.0

    for i in range(1, n + 1):
        j_lo = max(1, i - band)
        j_hi = min(m, i + band)
        for j in range(j_lo, j_hi + 1):
            # Euclidean distance between MFCC vectors
            d = np.sqrt(np.sum((audio_mfcc[i - 1] - template_mfcc[j - 1]) ** 2))
            cost[i, j] = d + min(
                cost[i - 1, j],  # insertion (audio frame skipped in template)
                cost[i, j - 1],  # deletion (template frame skipped in audio)
                cost[i - 1, j - 1],  # match
            )

    # Normalize by the longer sequence to avoid bias toward long templates
    return cost[n, m] / max(n, m)


def dtw_score(
    audio_mfcc: np.ndarray,
    template_mfcc: np.ndarray,
) -> float:
    """DTW similarity score: 0.0 (no match) to 1.0 (perfect match).

    Converts DTW cost to a bounded score using exponential decay,
    with a length-ratio penalty to prevent long templates from dominating.
    """
    cost = dtw_cost(audio_mfcc, template_mfcc)
    if cost == float("inf"):
        return 0.0

    # Length ratio penalty: penalize templates much longer/shorter than audio
    n, m = len(audio_mfcc), len(template_mfcc)
    length_ratio = min(n, m) / max(n, m)
    # Quadratic penalty: ratio 1.0→1.0, ratio 0.5→0.25, ratio 0.25→0.0625
    length_penalty = length_ratio**2

    # Exponential decay: score = exp(-cost / scale)
    # Scale 5.0 tuned for real MFCC values (range ~±10 per coefficient)
    raw_score = math.exp(-cost / 5.0)
    return raw_score * length_penalty


# =============================================================================
# VOWEL ANCHOR EXTRACTION
# =============================================================================


def extract_vowel_anchor(
    mfcc_frames: Sequence[Tuple[int, ...]],
    packed_frames: Sequence[int],
) -> Optional[str]:
    """Identify the dominant vowel in a segment using formant analysis.

    Uses the existing calibrated formant templates to find the strongest
    vowel in the high-RMS voiced region of the segment.

    Returns ARPAbet vowel string (e.g. "AH") or None.
    """
    from vibe_core.mahamantra.sound.shabda_intake import unpack_frame, extract_formants

    vowel_votes: Dict[str, int] = {}

    for packed in packed_frames:
        rms, varga, f0_x10, centroid_100 = unpack_frame(packed)
        if rms < 60 or f0_x10 == 0:
            continue  # skip silence and unvoiced

        # Score against vowel templates using calibrated F1/F2
        # (simplified version of score_frame, vowel-only)
        # We don't have raw samples here, so use centroid as rough F2 proxy
        # and varga as rough articulation proxy
        best_vowel = ""
        best_dist = float("inf")
        for vowel, (f1_c, f2_c, _) in _VOWEL_PARAMS.items():
            # Map varga to expected F2 range
            # varga 0 (kanth) → low F2 (~1200), varga 1 (talav) → mid-high (~1800)
            # varga 2 (murdh) → high (~2200), varga 4 (oshth) → low (~800)
            est_f2 = centroid_100 * 100  # rough estimate
            dist = abs(est_f2 - f2_c) / 1500.0
            if dist < best_dist:
                best_dist = dist
                best_vowel = vowel

        if best_vowel and best_dist < 0.5:
            vowel_votes[best_vowel] = vowel_votes.get(best_vowel, 0) + 1

    if not vowel_votes:
        return None

    return max(vowel_votes, key=lambda k: vowel_votes[k])


def extract_vowel_anchor_formants(
    packed_frames: Sequence[int],
    raw_samples: Optional[np.ndarray],
    sample_rate: int,
    seg_start: int,
    hop: int,
    n_fft: int,
) -> Optional[str]:
    """Identify dominant vowel using actual F1/F2 formant extraction.

    More accurate than centroid-based but requires raw_samples.
    """
    from vibe_core.mahamantra.sound.shabda_intake import unpack_frame, extract_formants

    vowel_votes: Dict[str, int] = {}

    for i, packed in enumerate(packed_frames):
        rms, varga, f0_x10, centroid_100 = unpack_frame(packed)
        if rms < 60 or f0_x10 == 0:
            continue

        if raw_samples is None:
            continue

        start_sample = (seg_start + i) * hop
        end_sample = start_sample + n_fft
        if end_sample > len(raw_samples):
            continue

        f1, f2 = extract_formants(raw_samples[start_sample:end_sample], sample_rate)
        if f1 == 0 or f2 == 0:
            continue

        best_vowel = ""
        best_dist = float("inf")
        for vowel, (f1_c, f2_c, _) in _VOWEL_PARAMS.items():
            f1_err = abs(f1 - f1_c) / 500.0
            f2_err = abs(f2 - f2_c) / 1500.0
            dist = f1_err + f2_err
            if dist < best_dist:
                best_dist = dist
                best_vowel = vowel

        if best_vowel and best_dist < 0.8:
            vowel_votes[best_vowel] = vowel_votes.get(best_vowel, 0) + 1

    if not vowel_votes:
        return None

    return max(vowel_votes, key=lambda k: vowel_votes[k])


# =============================================================================
# CANDIDATE FILTERING
# =============================================================================


# Map each ARPAbet vowel to similar vowels (for candidate expansion)
_VOWEL_NEIGHBORS: Final[Dict[str, Tuple[str, ...]]] = {
    "AA": ("AH", "AO", "AY"),
    "AE": ("EH", "AH"),
    "AH": ("AA", "ER", "AE"),
    "AO": ("AA", "OW"),
    "AW": ("AH", "AA", "UH"),
    "AY": ("AA", "AH", "AE"),
    "EH": ("AE", "IH", "EY"),
    "EY": ("EH", "IH", "IY"),
    "ER": ("AH", "UH"),
    "IH": ("IY", "EH", "EY"),
    "IY": ("IH", "EY"),
    "OW": ("AO", "UH"),
    "OY": ("AO", "OW"),
    "UH": ("UW", "AH", "ER"),
    "UW": ("UH", "OW"),
}


def filter_candidates_by_vowel(
    anchor_vowel: str,
    candidates: Sequence[Tuple[str, Sequence[str]]],
) -> List[Tuple[str, Sequence[str]]]:
    """Filter word candidates to those containing the anchor vowel (or neighbors).

    Input: anchor_vowel (ARPAbet), candidates as [(word, arpabet_seq), ...]
    Output: filtered list
    """
    allowed = {anchor_vowel}
    allowed.update(_VOWEL_NEIGHBORS.get(anchor_vowel, ()))

    result = []
    for word, phones in candidates:
        word_vowels = {p.rstrip("012") for p in phones if p.rstrip("012") in _VOWEL_PARAMS}
        if word_vowels & allowed:
            result.append((word, phones))

    return result


# =============================================================================
# AUDIO MFCC EXTRACTION (from packed frames / raw samples)
# =============================================================================


def segment_to_mfcc_matrix(
    packed_frames: Sequence[int],
    raw_samples: Optional[np.ndarray],
    sample_rate: int,
    seg_start: int,
    hop: int,
    n_fft: int,
    mfcc_frames: Optional[Sequence[Tuple[int, ...]]] = None,
) -> np.ndarray:
    """Extract MFCC matrix [N × 13] for an audio segment.

    Uses pre-computed mfcc_frames if available (from ShabdaStream),
    otherwise extracts from raw_samples.

    MFCCs are stored as int (×100) in the stream, so we convert back to float.
    """
    from vibe_core.mahamantra.sound.shabda_intake import extract_mfcc

    frames_out = []

    for i in range(len(packed_frames)):
        rms = packed_frames[i] & 0xFF
        if rms < 10:
            # Very quiet frame — use near-silence MFCC
            frames_out.append(_silence_mfcc())
            continue

        # Try pre-computed MFCCs first
        if mfcc_frames is not None and i < len(mfcc_frames):
            mfcc_ints = mfcc_frames[i]
            if any(c != 0 for c in mfcc_ints):
                # Convert int (×100) back to float
                frames_out.append(np.array([c / 100.0 for c in mfcc_ints]))
                continue

        # Extract from raw audio
        if raw_samples is not None:
            start_sample = (seg_start + i) * hop
            end_sample = start_sample + n_fft
            if end_sample <= len(raw_samples):
                audio_frame = raw_samples[start_sample:end_sample]
                mfcc_ints = extract_mfcc(audio_frame, sample_rate, n_fft)
                if any(c != 0 for c in mfcc_ints):
                    frames_out.append(np.array([c / 100.0 for c in mfcc_ints]))
                    continue

        frames_out.append(_silence_mfcc())

    if not frames_out:
        return np.array([_silence_mfcc()])

    return np.array(frames_out)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "phoneme_mfcc_profile",
    "word_mfcc_template",
    "dtw_cost",
    "dtw_score",
    "extract_vowel_anchor",
    "extract_vowel_anchor_formants",
    "filter_candidates_by_vowel",
    "segment_to_mfcc_matrix",
]
