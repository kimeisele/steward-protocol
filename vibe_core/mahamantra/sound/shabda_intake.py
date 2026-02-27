"""
SHABDA INTAKE — Audio → uint32 Salt Stream
============================================

The INPUT side of the sound system.
(audio_engine.py is the OUTPUT side: DIW → PCM)

Takes any audio source (WAV file or live microphone) and produces
the same uint32 packed frames used by the Shabda Bridge:

    Bits  0-7  (8): RMS energy (0-255)
    Bits  8-10 (3): Varga (articulation point, 0-4)
    Bits 11-22 (12): F0 (fundamental frequency × 10, 0-4095)
    Bits 23-31 (9): Centroid (spectral centroid / 100, 0-511)

This is the "holographic transcript" — not text, but a 4D acoustic
signature per 10ms frame: energy, articulation, pitch, timbre.

Dependencies: numpy, scipy (spectral analysis), wave (stdlib).
Optional: pyaudio (live mic input).

Usage:
    # From WAV file
    engine = ShabdaIntake()
    stream = engine.process_file("path/to/audio.wav")

    # From microphone (blocking, records for N seconds)
    stream = engine.record(duration_seconds=6.0)

    # Live streaming (yields frames in real-time)
    for frame in engine.stream_live():
        rms, varga, f0_x10, cent = unpack_frame(frame)

    # Inspect a frame
    rms, varga, f0_x10, cent = engine.unpack(stream[0])
"""

from __future__ import annotations

import struct
import threading
import wave
from pathlib import Path
from typing import Generator, List, Tuple

import numpy as np
from scipy.fft import fft, fftfreq
from scipy.linalg import solve_toeplitz

# =============================================================================
# CONSTANTS
# =============================================================================

HOP_MS = 10  # 10ms per frame — matches Shabda Bridge
N_FFT = 1024  # FFT window size
DEFAULT_SAMPLE_RATE = 44100


# =============================================================================
# PACKING (identical to bake script and shabda_bridge.py)
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


def unpack_frame(packed: int) -> Tuple[int, int, int, int]:
    """Unpack uint32 → (rms, varga, f0_x10, centroid_100)."""
    return (
        packed & 0xFF,
        (packed >> 8) & 0x7,
        (packed >> 11) & 0xFFF,
        (packed >> 23) & 0x1FF,
    )


# =============================================================================
# FORMANT EXTRACTION (LPC-based, supplementary channel for decoder)
# =============================================================================


def extract_formants(
    frame: np.ndarray, sr: int, order: int = 12,
) -> Tuple[int, int]:
    """Extract F1 and F2 formant frequencies via LPC analysis.

    Uses pre-emphasis → autocorrelation → Levinson-Durbin (via Toeplitz solver)
    → polynomial roots → select formant candidates by frequency band.

    Args:
        frame: mono audio frame (float64, [-1, 1])
        sr: sample rate in Hz
        order: LPC order (default 12, good for 44.1kHz)

    Returns:
        (f1_hz, f2_hz) as integers. (0, 0) on failure or silence.
    """
    if len(frame) < order + 1:
        return (0, 0)

    # Pre-emphasis (boost high frequencies)
    emphasized = np.append(frame[0], frame[1:] - 0.97 * frame[:-1])

    # Autocorrelation
    autocorr = np.correlate(emphasized, emphasized, mode="full")
    autocorr = autocorr[len(autocorr) // 2:]

    if autocorr[0] < 1e-10:
        return (0, 0)

    # Levinson-Durbin via Toeplitz solver
    try:
        lpc_coeffs = solve_toeplitz(autocorr[:order], autocorr[1:order + 1])
    except (np.linalg.LinAlgError, ValueError):
        return (0, 0)

    # Find roots of LPC polynomial: 1 + a1*z^-1 + a2*z^-2 + ...
    poly = np.concatenate(([1.0], -lpc_coeffs))
    roots = np.roots(poly)

    # Keep roots inside unit circle with positive imaginary part
    formant_freqs: List[float] = []
    for r in roots:
        if np.abs(r) < 1.0 and np.imag(r) > 0:
            freq = np.angle(r) * sr / (2 * np.pi)
            if 90 < freq < sr / 2:
                formant_freqs.append(freq)

    formant_freqs.sort()

    f1 = int(formant_freqs[0]) if len(formant_freqs) >= 1 else 0
    f2 = int(formant_freqs[1]) if len(formant_freqs) >= 2 else 0
    return (f1, f2)


# =============================================================================
# FEATURE EXTRACTION
# =============================================================================


def _centroid_to_varga(centroid_hz: float) -> int:
    """Map spectral centroid to Varga (articulation point).

    Based on acoustic phonetics — where spectral energy concentrates
    maps to where in the vocal tract the sound is produced.
    """
    if centroid_hz < 800:
        return 4  # OSHTHYA (labial)
    elif centroid_hz < 1200:
        return 0  # KANTHYA (throat)
    elif centroid_hz < 1800:
        return 1  # TALAVYA (palatal)
    elif centroid_hz < 2500:
        return 2  # MURDHANYA (retroflex)
    else:
        return 3  # DANTYA (dental/sibilant)


def _estimate_f0(frame: np.ndarray, sr: int) -> float:
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


def _extract_frame_features(
    frame: np.ndarray, sr: int, n_fft: int
) -> Tuple[int, int, int, int]:
    """Extract (rms, varga, f0_x10, centroid_x10) from one audio frame."""
    # RMS energy
    rms = int(np.sqrt(np.mean(frame**2)) * 1000)

    # Spectral centroid
    spec = np.abs(fft(frame * np.hanning(n_fft)))[:n_fft // 2]
    xf = fftfreq(n_fft, 1 / sr)[:n_fft // 2]
    total = np.sum(spec)
    centroid_hz = float(np.sum(xf * spec) / total) if total > 0 else 0.0
    centroid_x10 = int(centroid_hz * 10)

    # Varga from centroid
    varga = _centroid_to_varga(centroid_hz)

    # F0 via autocorrelation (only if voiced)
    if rms > 20:
        f0 = _estimate_f0(frame, sr)
        f0_x10 = int(f0 * 10)
    else:
        f0_x10 = 0

    return rms, varga, f0_x10, centroid_x10


# =============================================================================
# WAV READING
# =============================================================================


def _read_wav(path: Path) -> Tuple[np.ndarray, int]:
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
# INTAKE RESULT
# =============================================================================


class ShabdaStream:
    """A stream of uint32 packed acoustic frames.

    The holographic transcript — each frame is a 4D vector:
    (energy, articulation, pitch, timbre) at 10ms resolution.
    """

    __slots__ = ("frames", "sample_rate", "hop_ms", "n_fft",
                 "chant_start", "chant_end", "source")

    def __init__(
        self,
        frames: Tuple[int, ...],
        sample_rate: int,
        hop_ms: int = HOP_MS,
        n_fft: int = N_FFT,
        chant_start: int = 0,
        chant_end: int = 0,
        source: str = "",
    ):
        self.frames = frames
        self.sample_rate = sample_rate
        self.hop_ms = hop_ms
        self.n_fft = n_fft
        self.chant_start = chant_start
        self.chant_end = chant_end or (len(frames) - 1)
        self.source = source

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, idx: int) -> int:
        return self.frames[idx]

    @property
    def duration_ms(self) -> int:
        return len(self.frames) * self.hop_ms

    @property
    def byte_size(self) -> int:
        return len(self.frames) * 4

    def unpack(self, idx: int) -> Tuple[int, int, int, int]:
        """Unpack frame at index → (rms, varga, f0_x10, centroid_100)."""
        return unpack_frame(self.frames[idx])

    def to_dict(self) -> dict:
        """Export as JSON-serializable dict (all integers, no floats)."""
        return {
            "source": self.source,
            "sample_rate": self.sample_rate,
            "hop_ms": self.hop_ms,
            "n_fft": self.n_fft,
            "n_frames": len(self.frames),
            "chant_start": self.chant_start,
            "chant_end": self.chant_end,
            "duration_ms": self.duration_ms,
            "stream": list(self.frames),
        }


# =============================================================================
# SHABDA INTAKE ENGINE
# =============================================================================


class ShabdaIntake:
    """Audio → uint32 salt stream.

    The input side of the sound system. Takes any audio (file or mic)
    and produces packed uint32 frames identical to the Shabda Bridge format.
    """

    def __init__(self, hop_ms: int = HOP_MS, n_fft: int = N_FFT):
        self.hop_ms = hop_ms
        self.n_fft = n_fft

    def process_file(self, path: str | Path) -> ShabdaStream:
        """Process a WAV file → ShabdaStream."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        samples, sr = _read_wav(path)
        frames = self._extract_stream(samples, sr)

        # Find chant boundaries (energy > 10% of peak)
        rms_values = [f & 0xFF for f in frames]
        peak_rms = max(rms_values) if rms_values else 0
        threshold = peak_rms // 10
        chant_start = 0
        chant_end = len(frames) - 1
        for i, r in enumerate(rms_values):
            if r > threshold:
                chant_start = i
                break
        for i in range(len(rms_values) - 1, -1, -1):
            if rms_values[i] > threshold:
                chant_end = i
                break

        return ShabdaStream(
            frames=tuple(frames),
            sample_rate=sr,
            hop_ms=self.hop_ms,
            n_fft=self.n_fft,
            chant_start=chant_start,
            chant_end=chant_end,
            source=str(path.name),
        )

    def process_samples(
        self, samples: np.ndarray, sample_rate: int, source: str = "live"
    ) -> ShabdaStream:
        """Process raw samples (mono, float64 [-1,1]) → ShabdaStream."""
        frames = self._extract_stream(samples, sample_rate)
        return ShabdaStream(
            frames=tuple(frames),
            sample_rate=sample_rate,
            hop_ms=self.hop_ms,
            n_fft=self.n_fft,
            source=source,
        )

    def record(self, duration_seconds: float = 6.0, sample_rate: int = DEFAULT_SAMPLE_RATE) -> ShabdaStream:
        """Record from microphone → ShabdaStream.

        Requires pyaudio. Blocks for duration_seconds.
        """
        try:
            import pyaudio
        except ImportError:
            raise ImportError("pyaudio required for mic recording: pip install pyaudio")

        chunk = 1024
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk,
        )

        n_chunks = int(sample_rate * duration_seconds / chunk)
        raw_chunks: List[bytes] = []
        for _ in range(n_chunks):
            raw_chunks.append(stream.read(chunk))

        stream.stop_stream()
        stream.close()
        pa.terminate()

        # Decode PCM16 → float64
        raw = b"".join(raw_chunks)
        n_samples = len(raw) // 2
        samples = np.array(
            struct.unpack(f"<{n_samples}h", raw), dtype=np.float64
        ) / 32768.0

        return self.process_samples(samples, sample_rate, source="microphone")

    def stream_live(
        self, sample_rate: int = DEFAULT_SAMPLE_RATE
    ) -> Generator[int, None, None]:
        """Stream from microphone — yields one packed uint32 per hop.

        Requires pyaudio. Runs until the generator is closed or .stop() is called.

        Usage:
            engine = ShabdaIntake()
            for frame in engine.stream_live():
                rms, varga, f0, cent = unpack_frame(frame)
                if should_stop:
                    break
        """
        try:
            import pyaudio
        except ImportError:
            raise ImportError("pyaudio required for live streaming: pip install pyaudio")

        self._stop_event = threading.Event()
        hop = int(sample_rate * self.hop_ms / 1000)
        chunk = self.n_fft  # Read exactly one FFT window per chunk

        pa = pyaudio.PyAudio()
        mic = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk,
        )

        # Ring buffer: accumulates samples, emits frames at hop intervals
        buf = np.zeros(0, dtype=np.float64)

        try:
            while not self._stop_event.is_set():
                raw = mic.read(hop, exception_on_overflow=False)
                new_samples = np.array(
                    struct.unpack(f"<{hop}h", raw), dtype=np.float64
                ) / 32768.0
                buf = np.concatenate([buf, new_samples])

                # Emit all complete frames
                while len(buf) >= self.n_fft:
                    frame = buf[:self.n_fft]
                    rms, varga, f0_x10, centroid_x10 = _extract_frame_features(
                        frame, sample_rate, self.n_fft
                    )
                    yield pack_frame(rms, varga, f0_x10, centroid_x10)
                    buf = buf[hop:]  # Slide by hop, not n_fft (overlapping windows)
        finally:
            mic.stop_stream()
            mic.close()
            pa.terminate()
            self._stop_event.clear()

    def stream_samples(
        self, samples: np.ndarray, sample_rate: int
    ) -> Generator[int, None, None]:
        """Stream from pre-loaded samples — yields one packed uint32 per hop.

        Same frame-by-frame output as process_samples(), but as a generator.
        Useful for testing the streaming interface without a microphone.
        """
        hop = int(sample_rate * self.hop_ms / 1000)
        n_frames = (len(samples) - self.n_fft) // hop
        for i in range(n_frames):
            pos = i * hop
            frame = samples[pos:pos + self.n_fft]
            rms, varga, f0_x10, centroid_x10 = _extract_frame_features(
                frame, sample_rate, self.n_fft
            )
            yield pack_frame(rms, varga, f0_x10, centroid_x10)

    def stop(self) -> None:
        """Stop a running stream_live() generator from another thread."""
        if hasattr(self, "_stop_event"):
            self._stop_event.set()

    def _extract_stream(self, samples: np.ndarray, sr: int) -> List[int]:
        """Core extraction: samples → list of packed uint32 frames."""
        hop = int(sr * self.hop_ms / 1000)
        n_frames = (len(samples) - self.n_fft) // hop

        packed = []
        for i in range(n_frames):
            start = i * hop
            frame = samples[start:start + self.n_fft]
            rms, varga, f0_x10, centroid_x10 = _extract_frame_features(
                frame, sr, self.n_fft
            )
            packed.append(pack_frame(rms, varga, f0_x10, centroid_x10))

        return packed
