"""
BAKE SHABDA BRIDGE — Prabhupada's Japa → Pre-baked Acoustic Signatures
=======================================================================

One-time script. Reads WAV, extracts spectral features per syllable,
maps through existing RAMA/Pancha infrastructure, writes shabda_bridge.json.

Dependencies: wave (stdlib), numpy, scipy (both already installed).
Output: vibe_core/mahamantra/data/shabda_bridge.json

Usage: python scripts/research/bake_shabda_bridge.py
"""

import json
import struct
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from vibe_core.mahamantra.dharma.components.shabda import frequency_to_vibration_id
from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    JIVA_CYCLE,
    MALA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_RAMA,
    SEVEN,
    TRINITY,
)
from vibe_core.mahamantra.substrate._paths import DATA_DIR
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_SUB,
    COORD_VARGA,
    IS_SHRUTI,
    element_histogram,
    element_walk,
)
from vibe_core.mahamantra.substrate.encoding.varnamala_codec import encode, tokenize_iast
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    SANSKRIT_PHONEME_MAP,
)

# =============================================================================
# CONSTANTS
# =============================================================================

WAV_PATH = PROJECT_ROOT / "temp" / "srila prabhupada japa clip.wav"
OUTPUT_PATH = DATA_DIR / "shabda_bridge.json"

# The Mahamantra: 16 words, 32 syllables
MAHAMANTRA_WORDS = [
    "hare", "kṛṣṇa", "hare", "kṛṣṇa",
    "kṛṣṇa", "kṛṣṇa", "hare", "hare",
    "hare", "rāma", "hare", "rāma",
    "rāma", "rāma", "hare", "hare",
]

# Syllable breakdown (how japa is chanted)
MAHAMANTRA_SYLLABLES = [
    "ha", "re", "kṛ", "ṣṇa", "ha", "re", "kṛ", "ṣṇa",
    "kṛ", "ṣṇa", "kṛ", "ṣṇa", "ha", "re", "ha", "re",
    "ha", "re", "rā", "ma", "ha", "re", "rā", "ma",
    "rā", "ma", "rā", "ma", "ha", "re", "ha", "re",
]

# The 6 unique syllable types
UNIQUE_SYLLABLES = ["ha", "re", "kṛ", "ṣṇa", "rā", "ma"]


# =============================================================================
# AUDIO READING
# =============================================================================


def read_wav(path: Path) -> tuple:
    """Read WAV, mix to mono, normalize to [-1, 1]."""
    w = wave.open(str(path), "rb")
    n_channels = w.getnchannels()
    sampwidth = w.getsampwidth()
    sr = w.getframerate()
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)
    w.close()

    fmt = f"<{n_frames * n_channels}h"
    samples = np.array(struct.unpack(fmt, raw), dtype=np.float64)

    if n_channels == 2:
        samples = (samples[0::2] + samples[1::2]) / 2.0

    samples = samples / 32768.0
    return samples, sr


# =============================================================================
# FEATURE EXTRACTION
# =============================================================================


def detect_onsets(samples: np.ndarray, sr: int) -> list:
    """Detect syllable onsets via spectral flux peak-picking."""
    n_fft = 1024
    hop = 512
    prev_spec = np.zeros(n_fft // 2)
    flux = []

    for i in range(0, len(samples) - n_fft, hop):
        frame = samples[i : i + n_fft] * np.hanning(n_fft)
        spec = np.abs(fft(frame))[: n_fft // 2]
        diff = spec - prev_spec
        diff[diff < 0] = 0
        flux.append(np.sum(diff))
        prev_spec = spec.copy()

    flux = np.array(flux)
    flux_smooth = np.convolve(flux, np.ones(5) / 5, mode="same")

    threshold = np.median(flux_smooth) + 1.5 * np.std(flux_smooth)

    peaks, _ = scipy_signal.find_peaks(
        flux_smooth,
        height=threshold,
        distance=int(0.08 * sr / hop),
        prominence=threshold * 0.3,
    )

    onset_times = [p * hop / sr for p in peaks]
    return onset_times


def estimate_f0(segment: np.ndarray, sr: int) -> float:
    """Estimate fundamental frequency via autocorrelation."""
    if len(segment) < 512:
        return 0.0

    autocorr = np.correlate(segment, segment, mode="full")
    autocorr = autocorr[len(autocorr) // 2 :]

    min_lag = sr // 400  # 400 Hz max
    max_lag = sr // 80  # 80 Hz min

    if max_lag >= len(autocorr):
        max_lag = len(autocorr) - 1
    if min_lag >= max_lag:
        return 0.0

    ac_slice = autocorr[min_lag:max_lag]
    if len(ac_slice) == 0:
        return 0.0

    peak_idx = np.argmax(ac_slice) + min_lag
    return sr / peak_idx if peak_idx > 0 else 0.0


def spectral_centroid(segment: np.ndarray, sr: int) -> float:
    """Compute spectral centroid in Hz."""
    N = len(segment)
    if N < 256:
        return 0.0
    yf = np.abs(fft(segment * np.hanning(N)))[: N // 2]
    xf = fftfreq(N, 1 / sr)[: N // 2]
    total = np.sum(yf)
    if total == 0:
        return 0.0
    return float(np.sum(xf * yf) / total)


def harmonic_ratios(segment: np.ndarray, sr: int, f0: float, n_harmonics: int = 8) -> list:
    """Compute harmonic magnitude ratios relative to fundamental."""
    if f0 <= 0 or len(segment) < 512:
        return [0] * n_harmonics

    N = len(segment)
    yf = np.abs(fft(segment * np.hanning(N)))[: N // 2]
    xf = fftfreq(N, 1 / sr)[: N // 2]
    freq_res = sr / N

    ratios = []
    # Get fundamental magnitude
    f0_bin = int(f0 / freq_res) if freq_res > 0 else 0
    f0_mag = yf[f0_bin] if 0 < f0_bin < len(yf) else 1.0
    if f0_mag == 0:
        f0_mag = 1.0

    for h in range(1, n_harmonics + 1):
        target_freq = f0 * h
        target_bin = int(target_freq / freq_res) if freq_res > 0 else 0
        if 0 < target_bin < len(yf):
            # Search small window around target
            lo = max(0, target_bin - 2)
            hi = min(len(yf), target_bin + 3)
            h_mag = float(np.max(yf[lo:hi]))
            ratios.append(int(h_mag / f0_mag * 1000))
        else:
            ratios.append(0)

    return ratios


# =============================================================================
# SYLLABLE ASSIGNMENT
# =============================================================================


def assign_syllables(onset_times: list, duration: float) -> list:
    """Assign Mahamantra syllables to detected onsets proportionally."""
    n_onsets = len(onset_times)
    n_syllables = len(MAHAMANTRA_SYLLABLES)

    if n_onsets == 0:
        return []

    # Duration of chanting (first onset to end)
    chant_start = onset_times[0]
    chant_end = duration

    assignments = []
    for i, onset_t in enumerate(onset_times):
        # Where is this onset proportionally in the chant?
        proportion = (onset_t - chant_start) / (chant_end - chant_start) if chant_end > chant_start else 0
        # Map to syllable index
        syl_idx = min(int(proportion * n_syllables), n_syllables - 1)
        assignments.append(MAHAMANTRA_SYLLABLES[syl_idx])

    return assignments


# =============================================================================
# INFRASTRUCTURE MAPPING
# =============================================================================


def map_syllable_to_rama(syllable: str) -> list:
    """Map a syllable through varnamala_codec to RAMA coordinates."""
    try:
        coords = encode(syllable)
        return list(coords)
    except Exception:
        return []


def map_coords_to_4d(coords: list) -> list:
    """Map RAMA coordinates to 4D decomposition."""
    result = []
    for c in coords:
        if 0 <= c < POSITION_SUM_RAMA:
            result.append({
                "coord": c,
                "element": COORD_ELEMENT[c],
                "varga": COORD_VARGA[c],
                "sub": COORD_SUB[c],
                "harmonic": COORD_HARMONIC[c],
                "is_shruti": c in IS_SHRUTI,
            })
    return result


def get_phoneme_signature(syllable: str) -> dict:
    """Get existing VibrationSignature data for a syllable."""
    sig = SANSKRIT_PHONEME_MAP.get(syllable)
    if sig is None:
        # Try first char
        sig = SANSKRIT_PHONEME_MAP.get(syllable[0]) if syllable else None
    if sig is None:
        return {"articulation": -1, "voicing": -1, "base_frequency": 0, "duration_ratio": 0}
    return {
        "articulation": sig.articulation.value,
        "voicing": sig.voicing.value,
        "base_frequency": sig.base_frequency,
        "duration_ratio": sig.duration_ratio,
    }


# =============================================================================
# MAIN BAKE
# =============================================================================


def bake():
    """Main bake process."""
    print(f"Reading WAV: {WAV_PATH}")
    samples, sr = read_wav(WAV_PATH)
    duration = len(samples) / sr
    print(f"Duration: {duration:.2f}s, Samples: {len(samples)}, Rate: {sr}Hz")

    # 1. Detect onsets
    print("\nDetecting syllable onsets...")
    onset_times = detect_onsets(samples, sr)
    print(f"Detected {len(onset_times)} onsets")

    # 2. Assign syllables
    assignments = assign_syllables(onset_times, duration)
    print(f"Assigned syllables: {' '.join(assignments)}")

    # 3. Extract features per segment
    print("\nExtracting per-segment features...")
    segments = []
    f0_values = []

    for i, onset_t in enumerate(onset_times):
        end_t = onset_times[i + 1] if i + 1 < len(onset_times) else min(onset_t + 0.3, duration)
        start_idx = int(onset_t * sr)
        end_idx = int(end_t * sr)
        segment = samples[start_idx:end_idx]

        if len(segment) < 256:
            continue

        f0 = estimate_f0(segment, sr)
        centroid = spectral_centroid(segment, sr)
        rms = float(np.sqrt(np.mean(segment**2)))
        h_ratios = harmonic_ratios(segment, sr, f0)

        # Map through infrastructure
        syllable = assignments[i] if i < len(assignments) else "ha"
        rama_coords = map_syllable_to_rama(syllable)
        vib_id = frequency_to_vibration_id(f0) if f0 > 0 else 0

        seg_data = {
            "idx": i,
            "onset_ms": int(onset_t * 1000),
            "duration_ms": int((end_t - onset_t) * 1000),
            "syllable": syllable,
            "f0_hz_x10": int(f0 * 10),
            "centroid_hz_x10": int(centroid * 10),
            "rms_x1000": int(rms * 1000),
            "vibration_id": vib_id,
            "rama_coords": rama_coords,
            "harmonic_ratios_x1000": h_ratios,
        }
        segments.append(seg_data)

        if f0 > 80:
            f0_values.append(f0)

        print(f"  Seg {i:2d} [{onset_t:.3f}s] {syllable:4s} "
              f"F0={f0:.1f}Hz VibID={vib_id} centroid={centroid:.0f}Hz")

    # 4. Compute aggregate F0 stats
    if f0_values:
        mean_f0 = float(np.mean(f0_values))
        median_f0 = float(np.median(f0_values))
    else:
        mean_f0 = 0.0
        median_f0 = 0.0

    print(f"\nF0 mean: {mean_f0:.1f} Hz, median: {median_f0:.1f} Hz")
    print(f"VibID(mean): {frequency_to_vibration_id(mean_f0)}")
    print(f"VibID(median): {frequency_to_vibration_id(median_f0)}")

    # 5. Aggregate per syllable type
    print("\nAggregating per syllable type...")
    syllable_data = {}
    for syl in UNIQUE_SYLLABLES:
        syl_segments = [s for s in segments if s["syllable"] == syl]
        n = len(syl_segments)

        rama_coords = map_syllable_to_rama(syl)
        phon_sig = get_phoneme_signature(syl)

        if n > 0:
            avg_centroid = int(sum(s["centroid_hz_x10"] for s in syl_segments) / n)
            avg_rms = int(sum(s["rms_x1000"] for s in syl_segments) / n)
            avg_f0 = int(sum(s["f0_hz_x10"] for s in syl_segments) / n)

            # Average harmonic ratios
            n_h = len(syl_segments[0]["harmonic_ratios_x1000"])
            avg_harmonics = []
            for h_idx in range(n_h):
                vals = [s["harmonic_ratios_x1000"][h_idx] for s in syl_segments if h_idx < len(s["harmonic_ratios_x1000"])]
                avg_harmonics.append(int(sum(vals) / len(vals)) if vals else 0)
        else:
            avg_centroid = 0
            avg_rms = 0
            avg_f0 = 0
            avg_harmonics = [0] * 8

        # Element walk for this syllable's RAMA coords
        if rama_coords:
            e_walk = [COORD_ELEMENT[c] for c in rama_coords if 0 <= c < POSITION_SUM_RAMA]
            e_hist = list(element_histogram(tuple(rama_coords)))
        else:
            e_walk = []
            e_hist = [0] * PANCHA

        syllable_data[syl] = {
            "rama_coords": rama_coords,
            "articulation": phon_sig["articulation"],
            "voicing": phon_sig["voicing"],
            "base_frequency": phon_sig["base_frequency"],
            "duration_ratio": phon_sig["duration_ratio"],
            "centroid_hz_x10": avg_centroid,
            "f0_hz_x10": avg_f0,
            "rms_x1000": avg_rms,
            "harmonics_x1000": avg_harmonics,
            "onset_count": n,
            "element_walk": e_walk,
            "element_histogram": e_hist,
        }

        print(f"  {syl:4s}: {n} occurrences, centroid={avg_centroid/10:.0f}Hz, "
              f"F0={avg_f0/10:.0f}Hz, RAMA={rama_coords}")

    # 6. Harmonic series from mean F0
    print("\nComputing harmonic series...")
    harmonic_vib_ids = []
    harmonic_shruti = []
    harmonic_rama_residues = []
    for h in range(1, 9):
        freq = mean_f0 * h
        vid = frequency_to_vibration_id(freq)
        residue = vid % POSITION_SUM_RAMA
        is_shr = residue in IS_SHRUTI
        harmonic_vib_ids.append(vid)
        harmonic_rama_residues.append(residue)
        harmonic_shruti.append(is_shr)
        print(f"  H{h}: {freq:.1f}Hz → VibID={vid}, RAMA residue={residue}, shruti={is_shr}")

    # 7. Aggregate element histogram across all segments
    all_rama = []
    for seg in segments:
        all_rama.extend(seg["rama_coords"])
    if all_rama:
        agg_element_hist = list(element_histogram(tuple(all_rama)))
    else:
        agg_element_hist = [0] * PANCHA

    # Varga histogram (H=0, K=1, R=2 from varnamala codec)
    varga_counts = [0, 0, 0]
    for seg in segments:
        syl = seg["syllable"]
        if syl in ("ha", "re"):
            varga_counts[0] += 1  # Hare
        elif syl in ("kṛ", "ṣṇa"):
            varga_counts[1] += 1  # Krishna
        elif syl in ("rā", "ma"):
            varga_counts[2] += 1  # Rama

    # 8. Build final JSON
    bridge_data = {
        "meta": {
            "source": "Srila Prabhupada japa recording",
            "file": "srila prabhupada japa clip.wav",
            "fundamental_hz_x10": int(mean_f0 * 10),
            "median_hz_x10": int(median_f0 * 10),
            "vibration_id": frequency_to_vibration_id(mean_f0),
            "vibration_id_median": frequency_to_vibration_id(median_f0),
            "duration_ms": int(duration * 1000),
            "sample_rate": sr,
            "n_segments": len(segments),
            "n_syllable_types": len(UNIQUE_SYLLABLES),
            "bake_version": 1,
        },
        "syllables": syllable_data,
        "segments": segments,
        "harmonic_series": {
            "vibration_ids": harmonic_vib_ids,
            "rama_residues": harmonic_rama_residues,
            "is_shruti": harmonic_shruti,
        },
        "aggregate": {
            "element_histogram": agg_element_hist,
            "varga_histogram": varga_counts,
            "dominant_element": int(np.argmax(agg_element_hist)) if agg_element_hist else 0,
            "mean_rms_x1000": int(np.mean([s["rms_x1000"] for s in segments])) if segments else 0,
            "mean_centroid_hz_x10": int(np.mean([s["centroid_hz_x10"] for s in segments])) if segments else 0,
        },
        "mahamantra_coords": {
            "hare": list(encode("hare")),
            "kṛṣṇa": list(encode("kṛṣṇa")),
            "rāma": list(encode("rāma")),
        },
    }

    # 9. Verify: no floats leaked
    def verify_no_floats(obj, path=""):
        if isinstance(obj, float):
            raise ValueError(f"Float leaked at {path}: {obj}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                verify_no_floats(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                verify_no_floats(v, f"{path}[{i}]")

    verify_no_floats(bridge_data)
    print("\n  No floats leaked in JSON data.")

    # 10. Write JSON
    print(f"\nWriting to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(bridge_data, f, indent=2, ensure_ascii=False)

    file_size = OUTPUT_PATH.stat().st_size
    print(f"Written: {file_size} bytes ({file_size / 1024:.1f} KB)")

    # 11. Summary
    print("\n" + "=" * 60)
    print("SHABDA BRIDGE BAKED SUCCESSFULLY")
    print("=" * 60)
    print(f"  F0 mean: {mean_f0:.1f} Hz → VibID {frequency_to_vibration_id(mean_f0)} (POSITION_SUM_RAMA={POSITION_SUM_RAMA})")
    print(f"  F0 median: {median_f0:.1f} Hz → VibID {frequency_to_vibration_id(median_f0)}")
    print(f"  Segments: {len(segments)}")
    print(f"  Syllable types: {len(syllable_data)}")
    print(f"  Element histogram: {agg_element_hist}")
    print(f"  Name histogram: H={varga_counts[0]} K={varga_counts[1]} R={varga_counts[2]}")
    print(f"  Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    bake()
