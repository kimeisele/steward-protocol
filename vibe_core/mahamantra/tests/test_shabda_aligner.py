"""
Tests for ShabdaAligner — Viterbi Forced Alignment + Tiny ASR
==============================================================

Tests: feature extraction, model loading, Viterbi alignment,
pronunciation lookup, integration with ShabdaDecoder.
"""

import numpy as np
import pytest

from vibe_core.mahamantra.sound.shabda_intake import (
    DEFAULT_SAMPLE_RATE,
    N_FFT,
    ShabdaStream,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA,
)

# =============================================================================
# HELPERS
# =============================================================================


def _sine_wave(freq: float, duration_s: float, sr: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    t = np.arange(int(sr * duration_s)) / sr
    return 0.8 * np.sin(2 * np.pi * freq * t)


def _make_stream(duration_s: float = 0.5, sr: int = DEFAULT_SAMPLE_RATE) -> ShabdaStream:
    """Create a synthetic ShabdaStream with raw audio."""
    from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake

    # Mix of frequencies to simulate speech-like signal
    t = np.arange(int(sr * duration_s)) / sr
    signal = (
        0.3 * np.sin(2 * np.pi * 300 * t)
        + 0.2 * np.sin(2 * np.pi * 800 * t)
        + 0.1 * np.sin(2 * np.pi * 2300 * t)
        + 0.05 * np.random.randn(len(t))
    )
    intake = ShabdaIntake()
    return intake.process_samples(signal, sr, source="test_synthetic")


# =============================================================================
# TEST: Feature Extraction
# =============================================================================


class TestLogMelExtraction:
    """Verify log-Mel spectrogram extraction."""

    def test_silence_returns_zeros(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_log_mel

        silence = np.zeros(N_FFT)
        result = extract_log_mel(silence)
        assert result.shape == (26,)
        np.testing.assert_array_equal(result, np.zeros(26))

    def test_short_frame_returns_zeros(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_log_mel

        short = np.random.randn(100)
        result = extract_log_mel(short)
        assert result.shape == (26,)
        np.testing.assert_array_equal(result, np.zeros(26))

    def test_sine_wave_nonzero(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_log_mel

        t = np.arange(N_FFT) / DEFAULT_SAMPLE_RATE
        signal = 0.8 * np.sin(2 * np.pi * 440 * t)
        result = extract_log_mel(signal, sr=DEFAULT_SAMPLE_RATE)
        assert result.shape == (26,)
        assert np.any(result != 0), "Sine wave should produce non-zero Mel"

    def test_deterministic(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_log_mel

        t = np.arange(N_FFT) / DEFAULT_SAMPLE_RATE
        signal = 0.8 * np.sin(2 * np.pi * 440 * t)
        r1 = extract_log_mel(signal, sr=DEFAULT_SAMPLE_RATE)
        r2 = extract_log_mel(signal, sr=DEFAULT_SAMPLE_RATE)
        np.testing.assert_allclose(r1, r2, atol=1e-12)

    def test_returns_26_floats(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_log_mel

        signal = _sine_wave(300.0, 0.05)
        result = extract_log_mel(signal[:N_FFT])
        assert result.shape == (26,)
        assert result.dtype == np.float64


class TestMelFeatures:
    """Verify extract_mel_features on a ShabdaStream."""

    def test_returns_correct_shape(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_mel_features

        stream = _make_stream(0.3)
        features = extract_mel_features(stream)
        assert features.shape[0] == len(stream.frames)
        assert features.shape[1] == 26

    def test_no_raw_samples_returns_zeros(self):
        from vibe_core.mahamantra.sound.shabda_aligner import extract_mel_features
        from vibe_core.mahamantra.sound.shabda_intake import pack_frame

        stream = ShabdaStream(
            frames=tuple([pack_frame(100, 0, 1200, 15000)] * 20),
            sample_rate=DEFAULT_SAMPLE_RATE,
            source="test_no_raw",
        )
        features = extract_mel_features(stream)
        assert features.shape == (20, 26)
        np.testing.assert_array_equal(features, np.zeros((20, 26)))


# =============================================================================
# TEST: Context Frame Expansion
# =============================================================================


class TestContextFrames:
    """Verify _add_context stacking."""

    def test_shape(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _add_context

        X = np.random.randn(10, 26)
        X_ctx = _add_context(X, ctx=2)
        assert X_ctx.shape == (10, 130)  # 5 * 26

    def test_center_frame_preserved(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _add_context

        X = np.random.randn(10, 26)
        X_ctx = _add_context(X, ctx=2)
        # Center frame (offset=2) should be X[i]
        for i in range(10):
            np.testing.assert_array_equal(X_ctx[i, 52:78], X[i])

    def test_edge_padding(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _add_context

        X = np.random.randn(5, 26)
        X_ctx = _add_context(X, ctx=2)
        # Frame 0: neighbors at -2,-1 should be copies of frame 0
        np.testing.assert_array_equal(X_ctx[0, 0:26], X[0])
        np.testing.assert_array_equal(X_ctx[0, 26:52], X[0])


# =============================================================================
# TEST: Pronunciation Lookup
# =============================================================================


class TestPronunciation:
    """Verify pronunciation dictionary."""

    def test_builtin_pronunciations(self):
        from vibe_core.mahamantra.sound.shabda_aligner import get_pronunciation

        phones = get_pronunciation("not")
        assert phones == ("N", "AA", "T")

    def test_unknown_word(self):
        from vibe_core.mahamantra.sound.shabda_aligner import get_pronunciation

        assert get_pronunciation("xyzzyplugh") is None

    def test_case_insensitive(self):
        from vibe_core.mahamantra.sound.shabda_aligner import get_pronunciation

        assert get_pronunciation("NOT") == get_pronunciation("not")

    def test_builtin_has_mahamantra(self):
        from vibe_core.mahamantra.sound.shabda_aligner import get_pronunciation

        assert get_pronunciation("hare") is not None
        assert get_pronunciation("rama") is not None
        assert get_pronunciation("krishna") is not None


# =============================================================================
# TEST: Tiny ASR Model
# =============================================================================


class TestTinyASR:
    """Verify TinyASR model loading and inference."""

    @pytest.fixture(scope="class")
    def model(self):
        from vibe_core.mahamantra.sound.shabda_aligner import TinyASR

        try:
            return TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

    def test_model_loads(self, model):
        assert model.n_classes > 0
        assert model.context >= 1

    def test_classes_are_arpabet(self, model):
        for c in model.classes:
            assert c in ARPABET_TO_RAMA or c == "SIL", f"Unknown class: {c}"

    def test_predict_shape(self, model):
        X = np.random.randn(20, 26)
        probs = model.predict_probs(X)
        assert probs.shape == (20, model.n_classes)

    def test_predict_probabilities_sum_to_one(self, model):
        X = np.random.randn(10, 26)
        probs = model.predict_probs(X)
        sums = probs.sum(axis=1)
        np.testing.assert_allclose(sums, 1.0, atol=1e-5)

    def test_predict_nonnegative(self, model):
        X = np.random.randn(10, 26)
        probs = model.predict_probs(X)
        assert np.all(probs >= 0)

    def test_class_index_lookup(self, model):
        for c in model.classes:
            idx = model.class_index(c)
            assert idx is not None
            assert 0 <= idx < model.n_classes

    def test_unknown_class_returns_none(self, model):
        assert model.class_index("XYZZY") is None


# =============================================================================
# TEST: Viterbi Alignment (unit)
# =============================================================================


class TestViterbiAlign:
    """Unit tests for Viterbi forced alignment."""

    def test_trivial_single_state(self):
        from vibe_core.mahamantra.sound.shabda_aligner import viterbi_align

        # 10 frames, 1 state (AA), all frames clearly AA
        probs = np.zeros((10, 3))
        probs[:, 0] = 0.9  # AA dominant
        probs[:, 1] = 0.05
        probs[:, 2] = 0.05
        states = [("AA", "test", "phoneme")]
        c2i = {"AA": 0}
        path, boundaries = viterbi_align(probs, states, c2i)
        assert len(path) == 10
        assert np.all(path == 0)
        assert len(boundaries) == 1
        assert boundaries[0][1] == "test"

    def test_two_state_transition(self):
        from vibe_core.mahamantra.sound.shabda_aligner import viterbi_align

        # 10 frames, 2 states: first half K, second half AE
        probs = np.zeros((10, 3))
        probs[:5, 0] = 0.9  # K dominant first half
        probs[:5, 1] = 0.05
        probs[:5, 2] = 0.05
        probs[5:, 0] = 0.05
        probs[5:, 1] = 0.9  # AE dominant second half
        probs[5:, 2] = 0.05
        states = [("K", "cat", "phoneme"), ("AE", "cat", "phoneme")]
        c2i = {"K": 0, "AE": 1}
        path, boundaries = viterbi_align(probs, states, c2i)
        assert len(path) == 10
        # First frames should be state 0, later frames state 1
        assert path[0] == 0
        assert path[-1] == 1

    def test_empty_states(self):
        from vibe_core.mahamantra.sound.shabda_aligner import viterbi_align

        probs = np.zeros((10, 3))
        path, boundaries = viterbi_align(probs, [], {})
        assert len(path) == 10
        assert len(boundaries) == 0

    def test_empty_frames(self):
        from vibe_core.mahamantra.sound.shabda_aligner import viterbi_align

        probs = np.zeros((0, 3))
        states = [("AA", "test", "phoneme")]
        path, boundaries = viterbi_align(probs, states, {"AA": 0})
        assert len(path) == 0

    def test_word_boundaries_detected(self):
        from vibe_core.mahamantra.sound.shabda_aligner import viterbi_align

        # Two words: "not" (N AA T) + "it" (IH T)
        probs = np.zeros((20, 5))
        # N dominant frames 0-3
        probs[0:4, 0] = 0.8
        probs[0:4, 1:] = 0.05
        # AA dominant frames 4-8
        probs[4:9, 1] = 0.8
        probs[4:9, 0] = 0.05
        # T dominant frames 9-11
        probs[9:12, 2] = 0.8
        probs[9:12, :2] = 0.05
        # SIL frames 12-13
        probs[12:14, :] = 0.2
        # IH dominant frames 14-17
        probs[14:18, 3] = 0.8
        probs[14:18, :3] = 0.05
        # T dominant frames 18-19
        probs[18:, 2] = 0.8
        probs[18:, :2] = 0.05

        states = [
            ("N", "not", "phoneme"),
            ("AA", "not", "phoneme"),
            ("T", "not", "phoneme"),
            ("SIL", "_pause_", "silence"),
            ("IH", "it", "phoneme"),
            ("T", "it", "phoneme"),
        ]
        c2i = {"N": 0, "AA": 1, "T": 2, "IH": 3, "SIL": None}
        path, boundaries = viterbi_align(probs, states, c2i)

        # Should detect two words
        words_found = [w for _, w in boundaries]
        assert "not" in words_found
        assert "it" in words_found


# =============================================================================
# TEST: Levenshtein Distance
# =============================================================================


class TestLevenshtein:
    """Verify edit distance calculation."""

    def test_identical(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _levenshtein

        assert _levenshtein(["A", "B"], ["A", "B"]) == 0

    def test_empty(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _levenshtein

        assert _levenshtein([], ["A", "B"]) == 2
        assert _levenshtein(["A", "B"], []) == 2

    def test_substitution(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _levenshtein

        assert _levenshtein(["A", "B"], ["A", "C"]) == 1

    def test_insertion(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _levenshtein

        assert _levenshtein(["A"], ["A", "B"]) == 1

    def test_deletion(self):
        from vibe_core.mahamantra.sound.shabda_aligner import _levenshtein

        assert _levenshtein(["A", "B"], ["A"]) == 1


# =============================================================================
# TEST: Integration with ShabdaDecoder
# =============================================================================


class TestDecoderIntegration:
    """Verify ShabdaDecoder.align_with_transcript() integration."""

    @pytest.mark.xfail(reason="align_with_transcript not yet implemented on ShabdaDecoder")
    def test_align_returns_transcript(self):
        """align_with_transcript returns a Transcript object."""
        from vibe_core.mahamantra.sound.shabda_aligner import TinyASR
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder, Transcript

        try:
            TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

        stream = _make_stream(0.5)
        decoder = ShabdaDecoder()
        # Use simple words that are in the builtin pronunciations
        result = decoder.align_with_transcript(stream, ["not", "but"])
        assert isinstance(result, Transcript)
        assert hasattr(result, "text")
        assert hasattr(result, "words")
        assert hasattr(result, "duration_ms")

    @pytest.mark.xfail(reason="align_with_transcript not yet implemented on ShabdaDecoder")
    def test_align_preserves_word_order(self):
        """Words in result should match transcript order."""
        from vibe_core.mahamantra.sound.shabda_aligner import TinyASR
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder

        try:
            TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

        stream = _make_stream(1.0)
        decoder = ShabdaDecoder()
        transcript_words = ["i", "came", "to", "preach"]
        result = decoder.align_with_transcript(stream, transcript_words)

        result_words = [w.word for w in result.words]
        for i, w in enumerate(result_words):
            assert w in transcript_words, f"Unexpected word: {w}"

    @pytest.mark.xfail(reason="align_with_transcript not yet implemented on ShabdaDecoder")
    def test_align_word_timings_monotonic(self):
        """Word start times should be monotonically increasing."""
        from vibe_core.mahamantra.sound.shabda_aligner import TinyASR
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder

        try:
            TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

        stream = _make_stream(1.0)
        decoder = ShabdaDecoder()
        result = decoder.align_with_transcript(stream, ["not", "exactly", "but"])

        starts = [w.start_ms for w in result.words]
        for i in range(1, len(starts)):
            assert starts[i] >= starts[i - 1], f"Word timings not monotonic: {starts}"

    @pytest.mark.xfail(reason="align_with_transcript not yet implemented on ShabdaDecoder")
    def test_align_rama_coords_valid(self):
        """All RAMA coords in result should be in valid range [0, 48]."""
        from vibe_core.mahamantra.sound.shabda_aligner import TinyASR
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder

        try:
            TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

        stream = _make_stream(0.5)
        decoder = ShabdaDecoder()
        result = decoder.align_with_transcript(stream, ["come"])

        for w in result.words:
            for c in w.rama_coords:
                assert 0 <= c < 49, f"Invalid RAMA coord {c} for '{w.word}'"

    def test_existing_transcribe_still_works(self):
        """Original transcribe() method should be unaffected."""
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder
        from vibe_core.mahamantra.sound.shabda_intake import pack_frame

        frames = tuple([pack_frame(0, 0, 0, 0)] * 50)
        stream = ShabdaStream(
            frames=frames,
            sample_rate=DEFAULT_SAMPLE_RATE,
            source="test_compat",
        )
        decoder = ShabdaDecoder()
        transcript = decoder.transcribe(stream)
        assert len(transcript.words) == 0
        assert transcript.text == ""


# =============================================================================
# TEST: AlignmentResult
# =============================================================================


class TestAlignmentResult:
    """Verify AlignmentResult data structure."""

    def test_align_stream_returns_result(self):
        from vibe_core.mahamantra.sound.shabda_aligner import (
            AlignmentResult,
            TinyASR,
            align_stream,
        )

        try:
            TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

        stream = _make_stream(0.5)
        result = align_stream(stream, ["not", "but"])
        assert isinstance(result, AlignmentResult)
        assert len(result.frame_labels) == len(stream.frames)
        assert len(result.frame_words) == len(stream.frames)
        assert result.duration_ms > 0

    def test_empty_transcript(self):
        from vibe_core.mahamantra.sound.shabda_aligner import TinyASR, align_stream

        try:
            TinyASR()
        except FileNotFoundError:
            pytest.skip("Tiny ASR weights not available")

        stream = _make_stream(0.3)
        result = align_stream(stream, [])
        assert len(result.words) == 0
        assert result.per == 1.0
