"""
BAKE SHABDA BRIDGE — Prabhupada's Japa → Continuous Signature Stream
=====================================================================

One-time script. Reads WAV, extracts frame-by-frame acoustic features,
packs each frame into a uint32, writes continuous stream to shabda_bridge.json.

The WAV can be deleted after baking — the signature is not reversible to audio.

Each frame (10ms) is packed as:
    Bits  0-7  (8): RMS energy (0-255)
    Bits  8-10 (3): Varga (articulation point, 0-4)
    Bits 11-22 (12): F0 (fundamental frequency × 10, 0-4095)
    Bits 23-31 (9): Centroid (spectral centroid / 100, 0-511)

638 frames × 4 bytes = 2,552 bytes. Fits in Antaranga (16 KB).

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
    WORDS,
)
from vibe_core.mahamantra.substrate._paths import DATA_DIR
from vibe_core.mahamantra.substrate import (
    COORD_ELEMENT,
    COORD_VARGA,
    IS_SHRUTI,
    element_histogram,
)
from vibe_core.mahamantra.substrate.encoding.varnamala_codec import encode

# =============================================================================
# CONSTANTS
# =============================================================================

WAV_PATH = PROJECT_ROOT / "temp" / "srila prabhupada japa clip.wav"
OUTPUT_PATH = DATA_DIR / "shabda_bridge.json"

HOP_MS = 10  # 10ms per frame
N_FFT = 1024  # FFT window size

# Mahamantra syllable sequence (32 syllables)
MAHAMANTRA_SYLLABLES = [
    "ha", "re", "kṛ", "ṣṇa", "ha", "re", "kṛ", "ṣṇa",
    "kṛ", "ṣṇa", "kṛ", "ṣṇa", "ha", "re", "ha", "re",
    "ha", "re", "rā", "ma", "ha", "re", "rā", "ma",
    "rā", "ma", "rā", "ma", "ha", "re", "ha", "re",
]

UNIQUE_SYLLABLES = ["ha", "re", "kṛ", "ṣṇa", "rā", "ma"]


# =============================================================================
# PACKING (32-bit per frame)
# =============================================================================

def pack_frame(rms: int, varga: int, f0_x10: int, centroid_x10: int) -> int:
    """Pack one frame into a uint32.

    Bits  0-7  (8): RMS (0-255)
    Bits  8-10 (3): Varga (0-4)
    Bits 11-22 (12): F0×10 (0-4095)
    Bits 23-31 (9): Centroid/100 (0-511)
    """
    r = min(255, max(0, rms))
    v = min(4, max(0, varga))
    f = min(4095, max(0, f0_x10))
    c = min(511, max(0, centroid_x10 // 100))
    return r | (v << 8) | (f << 11) | (c << 23)


def unpack_frame(packed: int) -> dict:
    """Unpack a uint32 back to features (for verification)."""
    return {
        "rms": packed & 0xFF,
        "varga": (packed >> 8) & 0x7,
        "f0_x10": (packed >> 11) & 0xFFF,
        "centroid_100": (packed >> 23) & 0x1FF,
    }


# =============================================================================
# AUDIO READING
# =============================================================================

def read_wav(path: Path) -> tuple:
    """Read WAV, mix to mono, normalize to [-1, 1]."""
    w = wave.open(str(path), "rb")
    n_channels = w.getnchannels()
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

def centroid_to_varga(centroid_hz: float) -> int:
    """Map spectral centroid to Varga (articulation point).

    Based on acoustic phonetics — where the spectral energy concentrates
    maps to where in the vocal tract the sound is produced.
    """
    if centroid_hz < 800:
        return 4  # OSHTHYA (labial) — rounded, low centroid
    elif centroid_hz < 1200:
        return 0  # KANTHYA (throat) — open, mid-low
    elif centroid_hz < 1800:
        return 1  # TALAVYA (palatal) — front, mid
    elif centroid_hz < 2500:
        return 2  # MURDHANYA (retroflex) — mid-high
    else:
        return 3  # DANTYA (dental/sibilant) — high centroid


def estimate_f0(frame: np.ndarray, sr: int) -> float:
    """F0 via autocorrelation."""
    autocorr = np.correlate(frame, frame, mode="full")
    autocorr = autocorr[len(autocorr) // 2:]
    min_lag = sr // 400
    max_lag = min(sr // 80, len(autocorr) - 1)
    if max_lag <= min_lag:
        return 0.0
    ac_slice = autocorr[min_lag:max_lag]
    if len(ac_slice) == 0:
        return 0.0
    peak = np.argmax(ac_slice) + min_lag
    return sr / peak if peak > 0 else 0.0


# =============================================================================
# SYLLABLE ASSIGNMENT
# =============================================================================

def assign_syllable_per_frame(frame_idx: int, n_frames: int, chant_start_frame: int, chant_end_frame: int) -> str:
    """Map a frame index to its Mahamantra syllable position."""
    if frame_idx < chant_start_frame or frame_idx > chant_end_frame:
        return ""  # silence
    chant_range = chant_end_frame - chant_start_frame
    if chant_range <= 0:
        return ""
    proportion = (frame_idx - chant_start_frame) / chant_range
    syl_idx = min(int(proportion * len(MAHAMANTRA_SYLLABLES)), len(MAHAMANTRA_SYLLABLES) - 1)
    return MAHAMANTRA_SYLLABLES[syl_idx]


# =============================================================================
# MAIN BAKE
# =============================================================================

def bake():
    print(f"Reading WAV: {WAV_PATH}")
    samples, sr = read_wav(WAV_PATH)
    duration = len(samples) / sr
    print(f"Duration: {duration:.2f}s, Samples: {len(samples)}, Rate: {sr}Hz")

    hop = int(sr * HOP_MS / 1000)
    n_frames = (len(samples) - N_FFT) // hop

    print(f"Hop: {HOP_MS}ms ({hop} samples), Frames: {n_frames}")

    # 1. Find chant boundaries (where energy > threshold)
    frame_rms = []
    for i in range(n_frames):
        start = i * hop
        frame = samples[start:start + N_FFT]
        rms = np.sqrt(np.mean(frame**2))
        frame_rms.append(rms)

    rms_arr = np.array(frame_rms)
    threshold = np.max(rms_arr) * 0.1
    voiced = rms_arr > threshold
    chant_start = 0
    chant_end = n_frames - 1
    for i in range(n_frames):
        if voiced[i]:
            chant_start = i
            break
    for i in range(n_frames - 1, -1, -1):
        if voiced[i]:
            chant_end = i
            break

    print(f"Chant region: frame {chant_start}-{chant_end} "
          f"({chant_start * HOP_MS}ms - {chant_end * HOP_MS}ms)")

    # 2. Frame-by-frame feature extraction + packing
    print("\nExtracting continuous signature stream...")
    packed_stream = []
    f0_values = []
    syllable_frames = {s: [] for s in UNIQUE_SYLLABLES}

    for i in range(n_frames):
        start = i * hop
        frame = samples[start:start + N_FFT]

        # RMS
        rms = int(np.sqrt(np.mean(frame**2)) * 1000)

        # Spectral centroid
        spec = np.abs(fft(frame * np.hanning(N_FFT)))[:N_FFT // 2]
        xf = fftfreq(N_FFT, 1 / sr)[:N_FFT // 2]
        total = np.sum(spec)
        centroid_hz = float(np.sum(xf * spec) / total) if total > 0 else 0.0
        centroid_x10 = int(centroid_hz * 10)

        # Varga
        varga = centroid_to_varga(centroid_hz)

        # F0
        if rms > 20:
            f0 = estimate_f0(frame, sr)
            f0_x10 = int(f0 * 10)
            if f0 > 80:
                f0_values.append(f0)
        else:
            f0_x10 = 0

        # Pack
        packed = pack_frame(rms, varga, f0_x10, centroid_x10)
        packed_stream.append(packed)

        # Track per syllable
        syl = assign_syllable_per_frame(i, n_frames, chant_start, chant_end)
        if syl in syllable_frames:
            syllable_frames[syl].append(i)

    print(f"Packed {len(packed_stream)} frames ({len(packed_stream) * 4} bytes)")

    # Verify pack/unpack round-trip
    for p in packed_stream[:5]:
        u = unpack_frame(p)
        p2 = pack_frame(u["rms"], u["varga"], u["f0_x10"], u["centroid_100"] * 100)
        assert p == p2, f"Pack/unpack mismatch: {p} != {p2}"
    print("Pack/unpack round-trip verified.")

    # 3. Compute aggregate statistics
    if f0_values:
        mean_f0 = float(np.mean(f0_values))
        median_f0 = float(np.median(f0_values))
    else:
        mean_f0 = 0.0
        median_f0 = 0.0

    # 4. Per-syllable aggregates
    syllable_data = {}
    for syl in UNIQUE_SYLLABLES:
        idxs = syllable_frames[syl]
        if not idxs:
            syllable_data[syl] = {"n_frames": 0, "rama_coords": list(encode(syl))}
            continue

        syl_packed = [packed_stream[i] for i in idxs]
        syl_unpacked = [unpack_frame(p) for p in syl_packed]

        avg_rms = int(np.mean([u["rms"] for u in syl_unpacked]))
        avg_f0 = int(np.mean([u["f0_x10"] for u in syl_unpacked]))
        avg_cent = int(np.mean([u["centroid_100"] for u in syl_unpacked]))

        rama_coords = list(encode(syl))
        e_hist = list(element_histogram(tuple(rama_coords)))

        syllable_data[syl] = {
            "n_frames": len(idxs),
            "rama_coords": rama_coords,
            "element_histogram": e_hist,
            "avg_rms": avg_rms,
            "avg_f0_x10": avg_f0,
            "avg_centroid_100": avg_cent,
        }

    # 5. Harmonic series
    harmonic_vib_ids = []
    harmonic_shruti = []
    for h in range(1, 9):
        freq = mean_f0 * h
        vid = frequency_to_vibration_id(freq) if freq > 0 else 0
        residue = vid % POSITION_SUM_RAMA
        harmonic_vib_ids.append(vid)
        harmonic_shruti.append(residue in IS_SHRUTI)

    # 6. Build JSON
    bridge_data = {
        "meta": {
            "source": "Srila Prabhupada japa recording",
            "bake_version": 2,
            "hop_ms": HOP_MS,
            "n_fft": N_FFT,
            "sample_rate": sr,
            "duration_ms": int(duration * 1000),
            "n_frames": len(packed_stream),
            "chant_start_frame": chant_start,
            "chant_end_frame": chant_end,
            "fundamental_hz_x10": int(mean_f0 * 10),
            "median_hz_x10": int(median_f0 * 10),
            "vibration_id": frequency_to_vibration_id(mean_f0) if mean_f0 > 0 else 0,
            "vibration_id_median": frequency_to_vibration_id(median_f0) if median_f0 > 0 else 0,
            "pack_format": "RMS(8)|Varga(3)|F0x10(12)|Centroid/100(9) = uint32",
        },
        "stream": packed_stream,
        "syllables": syllable_data,
        "harmonic_series": {
            "vibration_ids": harmonic_vib_ids,
            "is_shruti": harmonic_shruti,
        },
        "mahamantra_coords": {
            "hare": list(encode("hare")),
            "kṛṣṇa": list(encode("kṛṣṇa")),
            "rāma": list(encode("rāma")),
        },
    }

    # 7. Verify no floats
    def verify_no_floats(obj, path=""):
        if isinstance(obj, float):
            raise ValueError(f"Float at {path}: {obj}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                verify_no_floats(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                verify_no_floats(v, f"{path}[{i}]")

    verify_no_floats(bridge_data)
    print("No floats in data.")

    # 8. Write
    print(f"\nWriting to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(bridge_data, f, ensure_ascii=False)

    file_size = OUTPUT_PATH.stat().st_size
    print(f"Written: {file_size} bytes ({file_size / 1024:.1f} KB)")

    # 9. Summary
    print("\n" + "=" * 60)
    print("SHABDA BRIDGE v2 — CONTINUOUS STREAM")
    print("=" * 60)
    print(f"  Frames: {len(packed_stream)} × uint32 = {len(packed_stream) * 4} bytes")
    print(f"  Fits Antaranga (16KB): {len(packed_stream) * 4 <= 16384}")
    print(f"  F0 mean: {mean_f0:.1f} Hz → VibID {frequency_to_vibration_id(mean_f0) if mean_f0 > 0 else 0}")
    print(f"  F0 median: {median_f0:.1f} Hz → VibID {frequency_to_vibration_id(median_f0) if median_f0 > 0 else 0}")
    syl_summary = ', '.join(f'{s}={d["n_frames"]}' for s, d in syllable_data.items())
    print(f"  Syllable frames: {syl_summary}")
    print(f"  Harmonics: {harmonic_vib_ids}")
    print(f"  WAV can now be deleted — signature is not reversible.")
    print(f"  Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    bake()
