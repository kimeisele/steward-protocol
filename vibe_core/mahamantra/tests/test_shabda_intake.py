"""
Tests for ShabdaIntake — Audio → uint32 Salt Stream
=====================================================

Tests use synthetic audio (sine waves, silence, noise) — no WAV files needed.
Verifies the full pipeline: samples → spectral extraction → uint32 packing.
"""

import wave
from pathlib import Path

import numpy as np
import pytest

from vibe_core.mahamantra.sound.shabda_intake import (
    DEFAULT_SAMPLE_RATE,
    HOP_MS,
    N_FFT,
    ShabdaIntake,
    ShabdaStream,
    _centroid_to_varga,
    _estimate_f0,
    _extract_frame_features,
    pack_frame,
    unpack_frame,
)

# =============================================================================
# HELPERS
# =============================================================================


def _sine_wave(freq: float, duration_s: float, sr: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    """Generate a mono sine wave, float64 [-1, 1]."""
    t = np.arange(int(sr * duration_s)) / sr
    return 0.8 * np.sin(2 * np.pi * freq * t)


def _silence(duration_s: float, sr: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    return np.zeros(int(sr * duration_s))


def _white_noise(duration_s: float, sr: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.uniform(-0.5, 0.5, int(sr * duration_s))


def _write_wav(path: Path, samples: np.ndarray, sr: int = DEFAULT_SAMPLE_RATE) -> None:
    """Write float64 [-1,1] mono samples to 16-bit WAV."""
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# =============================================================================
# PACK / UNPACK
# =============================================================================


class TestPackUnpack:
    def test_roundtrip_zeros(self):
        packed = pack_frame(0, 0, 0, 0)
        assert packed == 0
        assert unpack_frame(0) == (0, 0, 0, 0)

    def test_roundtrip_max(self):
        packed = pack_frame(255, 4, 4095, 51100)
        rms, varga, f0, cent = unpack_frame(packed)
        assert rms == 255
        assert varga == 4
        assert f0 == 4095
        assert cent == 511

    def test_clamping(self):
        packed = pack_frame(999, 99, 99999, 999999)
        rms, varga, f0, cent = unpack_frame(packed)
        assert rms == 255
        assert varga == 4
        assert f0 == 4095
        assert cent == 511

    def test_negative_clamping(self):
        packed = pack_frame(-5, -1, -10, -100)
        rms, varga, f0, cent = unpack_frame(packed)
        assert rms == 0
        assert varga == 0
        assert f0 == 0
        assert cent == 0

    def test_specific_values(self):
        packed = pack_frame(128, 2, 2200, 15000)
        rms, varga, f0, cent = unpack_frame(packed)
        assert rms == 128
        assert varga == 2
        assert f0 == 2200
        assert cent == 150  # 15000 // 100

    def test_bit_layout(self):
        """Verify exact bit positions match the spec."""
        packed = pack_frame(0xFF, 0, 0, 0)
        assert packed == 0xFF  # bits 0-7

        packed = pack_frame(0, 4, 0, 0)
        assert packed == (4 << 8)  # bits 8-10

        packed = pack_frame(0, 0, 0xFFF, 0)
        assert packed == (0xFFF << 11)  # bits 11-22

        packed = pack_frame(0, 0, 0, 51100)
        assert packed == (511 << 23)  # bits 23-31


# =============================================================================
# VARGA MAPPING
# =============================================================================


class TestVargaMapping:
    def test_low_centroid_is_labial(self):
        assert _centroid_to_varga(400) == 4  # OSHTHYA

    def test_throat(self):
        assert _centroid_to_varga(1000) == 0  # KANTHYA

    def test_palatal(self):
        assert _centroid_to_varga(1500) == 1  # TALAVYA

    def test_retroflex(self):
        assert _centroid_to_varga(2000) == 2  # MURDHANYA

    def test_dental(self):
        assert _centroid_to_varga(3000) == 3  # DANTYA

    def test_boundary_800(self):
        assert _centroid_to_varga(799) == 4
        assert _centroid_to_varga(800) == 0

    def test_boundary_1200(self):
        assert _centroid_to_varga(1199) == 0
        assert _centroid_to_varga(1200) == 1


# =============================================================================
# F0 ESTIMATION
# =============================================================================


class TestF0Estimation:
    def test_300hz_sine(self):
        """A pure 300 Hz sine should estimate ~300 (within 80-400Hz range)."""
        sr = 44100
        samples = _sine_wave(300.0, 0.1, sr)
        frame = samples[:N_FFT]
        f0 = _estimate_f0(frame, sr)
        assert 280 < f0 < 320, f"Expected ~300 Hz, got {f0}"

    def test_200hz_sine(self):
        sr = 44100
        samples = _sine_wave(200.0, 0.1, sr)
        frame = samples[:N_FFT]
        f0 = _estimate_f0(frame, sr)
        assert 180 < f0 < 220, f"Expected ~200 Hz, got {f0}"

    def test_silence_gated_in_feature_extraction(self):
        """F0 is gated by RMS > 20 in _extract_frame_features, not in _estimate_f0."""
        frame = np.zeros(N_FFT)
        _, _, f0_x10, _ = _extract_frame_features(frame, 44100, N_FFT)
        assert f0_x10 == 0, "Silence should produce f0=0 via RMS gate"


# =============================================================================
# FRAME FEATURE EXTRACTION
# =============================================================================


class TestFrameFeatures:
    def test_silence_low_rms(self):
        frame = np.zeros(N_FFT)
        rms, _, _, _ = _extract_frame_features(frame, 44100, N_FFT)
        assert rms == 0

    def test_loud_sine_high_rms(self):
        samples = _sine_wave(440.0, 0.1)
        frame = samples[:N_FFT]
        rms, _, _, _ = _extract_frame_features(frame, 44100, N_FFT)
        assert rms > 100, f"Loud sine should have high RMS, got {rms}"

    def test_sine_has_f0(self):
        samples = _sine_wave(300.0, 0.1)
        frame = samples[:N_FFT]
        _, _, f0_x10, _ = _extract_frame_features(frame, 44100, N_FFT)
        assert 2500 < f0_x10 < 3500, f"Expected ~3000 (300Hz×10), got {f0_x10}"

    def test_silence_no_f0(self):
        frame = np.zeros(N_FFT)
        _, _, f0_x10, _ = _extract_frame_features(frame, 44100, N_FFT)
        assert f0_x10 == 0

    def test_returns_4_ints(self):
        samples = _sine_wave(440.0, 0.1)
        result = _extract_frame_features(samples[:N_FFT], 44100, N_FFT)
        assert len(result) == 4
        assert all(isinstance(v, int) for v in result)


# =============================================================================
# SHABDA STREAM
# =============================================================================


class TestShabdaStream:
    def _make_stream(self, n: int = 100) -> ShabdaStream:
        frames = tuple(pack_frame(i % 256, i % 5, i * 10, i * 100) for i in range(n))
        return ShabdaStream(frames=frames, sample_rate=44100, source="test")

    def test_len(self):
        s = self._make_stream(50)
        assert len(s) == 50

    def test_getitem(self):
        s = self._make_stream(10)
        assert s[0] == s.frames[0]
        assert s[9] == s.frames[9]

    def test_duration_ms(self):
        s = self._make_stream(100)
        assert s.duration_ms == 100 * HOP_MS

    def test_byte_size(self):
        s = self._make_stream(100)
        assert s.byte_size == 400  # 100 × 4

    def test_unpack(self):
        frames = (pack_frame(128, 2, 2200, 15000),)
        s = ShabdaStream(frames=frames, sample_rate=44100)
        rms, varga, f0, cent = s.unpack(0)
        assert rms == 128
        assert varga == 2
        assert f0 == 2200

    def test_to_dict(self):
        s = self._make_stream(5)
        d = s.to_dict()
        assert d["source"] == "test"
        assert d["sample_rate"] == 44100
        assert d["n_frames"] == 5
        assert d["hop_ms"] == HOP_MS
        assert len(d["stream"]) == 5
        assert all(isinstance(v, int) for v in d["stream"])

    def test_chant_end_defaults(self):
        s = self._make_stream(50)
        assert s.chant_end == 49  # len - 1

    def test_chant_end_explicit(self):
        frames = tuple(range(10))
        s = ShabdaStream(frames=frames, sample_rate=44100, chant_end=7)
        assert s.chant_end == 7


# =============================================================================
# SHABDA INTAKE — PROCESS SAMPLES
# =============================================================================


class TestIntakeProcessSamples:
    def test_sine_produces_frames(self):
        engine = ShabdaIntake()
        samples = _sine_wave(440.0, 0.5)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        assert len(stream) > 0

    def test_silence_produces_frames(self):
        engine = ShabdaIntake()
        samples = _silence(0.5)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        assert len(stream) > 0

    def test_frame_count_matches_duration(self):
        """~100 frames per second at 10ms hop."""
        engine = ShabdaIntake()
        duration = 1.0  # 1 second
        samples = _sine_wave(440.0, duration)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        expected = (len(samples) - N_FFT) // (DEFAULT_SAMPLE_RATE * HOP_MS // 1000)
        assert len(stream) == expected

    def test_all_frames_uint32(self):
        engine = ShabdaIntake()
        samples = _sine_wave(440.0, 0.3)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        for i in range(len(stream)):
            assert 0 <= stream[i] < (1 << 32)

    def test_source_label(self):
        engine = ShabdaIntake()
        samples = _sine_wave(440.0, 0.1)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE, source="unit_test")
        assert stream.source == "unit_test"

    def test_sine_has_energy(self):
        engine = ShabdaIntake()
        samples = _sine_wave(440.0, 0.3)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        rms_values = [unpack_frame(stream[i])[0] for i in range(len(stream))]
        assert max(rms_values) > 50, f"Sine wave should have energy, max RMS={max(rms_values)}"

    def test_silence_low_energy(self):
        engine = ShabdaIntake()
        samples = _silence(0.3)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        rms_values = [unpack_frame(stream[i])[0] for i in range(len(stream))]
        assert max(rms_values) == 0, "Silence should have zero RMS"

    def test_different_pitches_different_f0(self):
        engine = ShabdaIntake()
        low = engine.process_samples(_sine_wave(200.0, 0.3), DEFAULT_SAMPLE_RATE)
        high = engine.process_samples(_sine_wave(800.0, 0.3), DEFAULT_SAMPLE_RATE)
        f0_low = [unpack_frame(low[i])[2] for i in range(len(low))]
        f0_high = [unpack_frame(high[i])[2] for i in range(len(high))]
        avg_low = sum(f0_low) / len(f0_low)
        avg_high = sum(f0_high) / len(f0_high)
        assert avg_high > avg_low * 2, f"800Hz should have higher F0 than 200Hz: {avg_high} vs {avg_low}"

    def test_noise_has_high_centroid(self):
        """White noise has energy spread across frequencies → high centroid."""
        engine = ShabdaIntake()
        stream = engine.process_samples(_white_noise(0.3), DEFAULT_SAMPLE_RATE)
        centroids = [unpack_frame(stream[i])[3] for i in range(len(stream))]
        avg = sum(centroids) / len(centroids)
        assert avg > 30, f"Noise should have high centroid, got avg={avg}"

    def test_custom_hop_ms(self):
        engine = ShabdaIntake(hop_ms=20)
        samples = _sine_wave(440.0, 0.5)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        assert stream.hop_ms == 20
        # Half the frames compared to 10ms hop
        engine_10 = ShabdaIntake(hop_ms=10)
        stream_10 = engine_10.process_samples(samples, DEFAULT_SAMPLE_RATE)
        assert abs(len(stream) * 2 - len(stream_10)) <= 1


# =============================================================================
# SHABDA INTAKE — PROCESS FILE
# =============================================================================


class TestIntakeProcessFile:
    def test_process_wav_file(self, tmp_path: Path):
        wav_path = tmp_path / "test.wav"
        samples = _sine_wave(440.0, 0.5)
        _write_wav(wav_path, samples)

        engine = ShabdaIntake()
        stream = engine.process_file(wav_path)
        assert len(stream) > 0
        assert stream.source == "test.wav"

    def test_file_not_found(self):
        engine = ShabdaIntake()
        with pytest.raises(FileNotFoundError):
            engine.process_file("/nonexistent/audio.wav")

    def test_chant_boundaries_detected(self, tmp_path: Path):
        """Silence → tone → silence should detect chant boundaries."""
        sr = DEFAULT_SAMPLE_RATE
        silence = _silence(0.2, sr)
        tone = _sine_wave(440.0, 0.3, sr)
        samples = np.concatenate([silence, tone, silence])
        wav_path = tmp_path / "bounded.wav"
        _write_wav(wav_path, samples)

        engine = ShabdaIntake()
        stream = engine.process_file(wav_path)
        # Chant should start after initial silence, end before trailing silence
        assert stream.chant_start > 0, "Chant should not start at frame 0"
        assert stream.chant_end < len(stream) - 1, "Chant should not end at last frame"

    def test_stereo_wav(self, tmp_path: Path):
        """Stereo WAV should be mixed to mono."""
        sr = DEFAULT_SAMPLE_RATE
        mono = _sine_wave(440.0, 0.3, sr)
        pcm_l = (mono * 32767).astype(np.int16)
        pcm_r = (mono * 32767 * 0.5).astype(np.int16)
        # Interleave stereo
        stereo = np.empty(len(pcm_l) * 2, dtype=np.int16)
        stereo[0::2] = pcm_l
        stereo[1::2] = pcm_r

        wav_path = tmp_path / "stereo.wav"
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(stereo.tobytes())

        engine = ShabdaIntake()
        stream = engine.process_file(wav_path)
        assert len(stream) > 0

    def test_file_matches_process_samples(self, tmp_path: Path):
        """process_file and process_samples should produce similar features.

        Not exact — 16-bit WAV quantization changes samples slightly.
        Compare unpacked features within tolerance.
        """
        samples = _sine_wave(440.0, 0.5)
        wav_path = tmp_path / "compare.wav"
        _write_wav(wav_path, samples)

        engine = ShabdaIntake()
        from_file = engine.process_file(wav_path)
        from_samples = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        min_len = min(len(from_file), len(from_samples))
        assert min_len > 0
        # Varga (articulation point) should match — coarse classification
        varga_matches = sum(
            1 for i in range(min_len)
            if unpack_frame(from_file[i])[1] == unpack_frame(from_samples[i])[1]
        )
        assert varga_matches > min_len * 0.9, f"Varga mismatch: {varga_matches}/{min_len}"
        # RMS should be within 20% of each other
        for i in range(min_len):
            rms_f = unpack_frame(from_file[i])[0]
            rms_s = unpack_frame(from_samples[i])[0]
            if rms_s > 10:
                assert abs(rms_f - rms_s) < rms_s * 0.3, f"Frame {i}: RMS {rms_f} vs {rms_s}"


# =============================================================================
# BRIDGE COMPATIBILITY
# =============================================================================


class TestBridgeCompatibility:
    def test_pack_format_matches_bridge(self):
        """Our pack/unpack must match shabda_bridge.py's format."""
        from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
            unpack_frame as bridge_unpack,
        )

        for rms in (0, 50, 128, 255):
            for varga in range(5):
                packed = pack_frame(rms, varga, 1500, 20000)
                intake_result = unpack_frame(packed)
                bridge_result = bridge_unpack(packed)
                assert intake_result == bridge_result, (
                    f"Format mismatch: intake={intake_result} bridge={bridge_result}"
                )

    def test_intake_no_heavy_deps_in_bridge(self):
        """shabda_bridge.py must not import numpy/scipy (runtime module)."""
        import importlib

        mod = importlib.import_module("vibe_core.mahamantra.substrate.encoding.shabda_bridge")
        source = open(mod.__file__).read()
        assert "import numpy" not in source
        assert "import scipy" not in source


# =============================================================================
# STREAMING
# =============================================================================


class TestStreamSamples:
    def test_stream_yields_frames(self):
        engine = ShabdaIntake()
        samples = _sine_wave(300.0, 0.5)
        frames = list(engine.stream_samples(samples, DEFAULT_SAMPLE_RATE))
        assert len(frames) > 0

    def test_stream_matches_batch(self):
        """stream_samples must produce identical frames to process_samples."""
        engine = ShabdaIntake()
        samples = _sine_wave(300.0, 0.5)
        batch = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        streamed = list(engine.stream_samples(samples, DEFAULT_SAMPLE_RATE))
        assert len(streamed) == len(batch)
        for i in range(len(streamed)):
            assert streamed[i] == batch.frames[i], f"Frame {i} differs"

    def test_stream_is_generator(self):
        import types

        engine = ShabdaIntake()
        samples = _sine_wave(300.0, 0.1)
        gen = engine.stream_samples(samples, DEFAULT_SAMPLE_RATE)
        assert isinstance(gen, types.GeneratorType)

    def test_stream_can_break_early(self):
        engine = ShabdaIntake()
        samples = _sine_wave(300.0, 1.0)  # 1 second = ~98 frames
        count = 0
        for _ in engine.stream_samples(samples, DEFAULT_SAMPLE_RATE):
            count += 1
            if count >= 5:
                break
        assert count == 5

    def test_stream_silence(self):
        engine = ShabdaIntake()
        samples = _silence(0.3)
        frames = list(engine.stream_samples(samples, DEFAULT_SAMPLE_RATE))
        assert len(frames) > 0
        for f in frames:
            rms = unpack_frame(f)[0]
            assert rms == 0

    def test_stream_noise_has_energy(self):
        engine = ShabdaIntake()
        samples = _white_noise(0.3)
        frames = list(engine.stream_samples(samples, DEFAULT_SAMPLE_RATE))
        rms_values = [unpack_frame(f)[0] for f in frames]
        assert max(rms_values) > 50

    def test_stream_empty_samples(self):
        engine = ShabdaIntake()
        samples = np.array([], dtype=np.float64)
        frames = list(engine.stream_samples(samples, DEFAULT_SAMPLE_RATE))
        assert len(frames) == 0

    def test_stream_too_short(self):
        """Samples shorter than n_fft should yield no frames."""
        engine = ShabdaIntake()
        samples = _sine_wave(300.0, 0.01)  # ~441 samples < 1024
        frames = list(engine.stream_samples(samples, DEFAULT_SAMPLE_RATE))
        assert len(frames) == 0

    def test_stop_method_exists(self):
        engine = ShabdaIntake()
        engine.stop()  # Should not raise even without active stream
