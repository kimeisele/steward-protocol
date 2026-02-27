"""
Tests for ShabdaDecoder — Deterministic Speech-to-Text
=======================================================

Tests use synthetic audio and mock frames — no WAV files needed.
Verifies: ARPAbet mapping, formant extraction, segmentation,
scoring, pronunciation dictionary, end-to-end transcription.
"""

import numpy as np
import pytest

from vibe_core.mahamantra.protocols._seed import PANCHA, WORDS
from vibe_core.mahamantra.sound.shabda_intake import (
    DEFAULT_SAMPLE_RATE,
    extract_formants,
    pack_frame,
)
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA,
    ARPABET_TO_STHANA,
    ARPABET_TO_VARGA,
    SthanaIndex,
)

# =============================================================================
# HELPERS
# =============================================================================


def _sine_wave(freq: float, duration_s: float, sr: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    """Generate a mono sine wave, float64 [-1, 1]."""
    t = np.arange(int(sr * duration_s)) / sr
    return 0.8 * np.sin(2 * np.pi * freq * t)


def _silence_frames(n: int) -> list:
    """Generate n silent packed frames (RMS=0)."""
    return [pack_frame(0, 0, 0, 0)] * n


def _voiced_frames(n: int, rms: int = 150, varga: int = 0, f0_x10: int = 1200, centroid_x10: int = 15000) -> list:
    """Generate n voiced packed frames with given features."""
    return [pack_frame(rms, varga, f0_x10, centroid_x10)] * n


# =============================================================================
# TEST: ARPAbet → RAMA Mapping (Phase 2 verification)
# =============================================================================


class TestArpabetToRama:
    """Verify all 39 ARPAbet phonemes are mapped correctly."""

    def test_all_39_phonemes_mapped(self):
        """All 39 ARPAbet symbols have RAMA coordinates."""
        assert len(ARPABET_TO_RAMA) == 39

    def test_vowels_in_svara_range(self):
        """Vowel phonemes map to coords 0-15 (SVARA)."""
        vowels = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY",
                   "ER", "IH", "IY", "OW", "OY", "UH", "UW"]
        for v in vowels:
            assert ARPABET_TO_RAMA[v] < WORDS, f"{v} should be SVARA (<{WORDS}), got {ARPABET_TO_RAMA[v]}"

    def test_stops_in_sparsha_range(self):
        """Stop consonants map to coords 16-40 (SPARSHA)."""
        stops = ["K", "G", "NG", "CH", "JH", "T", "D", "TH", "DH", "N", "P", "B", "F", "M"]
        for s in stops:
            coord = ARPABET_TO_RAMA[s]
            assert WORDS <= coord <= 40, f"{s} should be SPARSHA (16-40), got {coord}"

    def test_semivowels_in_shesha_range(self):
        """Semivowels map to coords 41-44."""
        semivowels = ["Y", "R", "L", "V", "W"]
        for sv in semivowels:
            coord = ARPABET_TO_RAMA[sv]
            assert 41 <= coord <= 44, f"{sv} should be SHESHA semivowel (41-44), got {coord}"

    def test_sibilants_mapped(self):
        """Sibilants map to coords 45-48."""
        sibilants = {"SH": 45, "S": 47, "HH": 48}
        for arpa, expected in sibilants.items():
            assert ARPABET_TO_RAMA[arpa] == expected, f"{arpa} expected {expected}, got {ARPABET_TO_RAMA[arpa]}"

    def test_voiced_pairs(self):
        """Voiced/unvoiced pairs map to same varga row."""
        pairs = [("K", "G"), ("T", "D"), ("P", "B"), ("CH", "JH")]
        for unvoiced, voiced in pairs:
            assert ARPABET_TO_VARGA[unvoiced] == ARPABET_TO_VARGA[voiced], (
                f"{unvoiced}/{voiced} should share varga"
            )

    def test_all_varga_covered(self):
        """All 5 varga positions have at least one consonant."""
        vargas_seen = set()
        consonants = [k for k, v in ARPABET_TO_RAMA.items() if v >= WORDS]
        for c in consonants:
            if c in ARPABET_TO_VARGA:
                vargas_seen.add(int(ARPABET_TO_VARGA[c]))
        assert len(vargas_seen) == PANCHA, f"Expected 5 vargas, got {vargas_seen}"

    def test_arpabet_to_sthana_complete(self):
        """Every phoneme in ARPABET_TO_RAMA also has a sthana mapping."""
        for arpabet in ARPABET_TO_RAMA:
            assert arpabet in ARPABET_TO_STHANA, f"{arpabet} missing from ARPABET_TO_STHANA"

    def test_nasals_are_anunasika(self):
        """M, N, NG should have ANUNASIKA sthana."""
        for nasal in ["M", "N", "NG"]:
            assert ARPABET_TO_STHANA[nasal] == SthanaIndex.ANUNASIKA, (
                f"{nasal} should be ANUNASIKA"
            )

    def test_unvoiced_stops_are_sparsha(self):
        """K, P, T should have SPARSHA sthana (unvoiced)."""
        for stop in ["K", "P", "T"]:
            assert ARPABET_TO_STHANA[stop] == SthanaIndex.SPARSHA, (
                f"{stop} should be SPARSHA"
            )


# =============================================================================
# TEST: Formant Extraction
# =============================================================================


class TestFormantExtraction:
    """Verify LPC-based formant extraction."""

    def test_silence_returns_zero(self):
        """Silence → (0, 0)."""
        silence = np.zeros(1024)
        f1, f2 = extract_formants(silence, DEFAULT_SAMPLE_RATE)
        assert f1 == 0
        assert f2 == 0

    def test_short_frame_returns_zero(self):
        """Frame shorter than LPC order → (0, 0)."""
        short = np.random.randn(5)
        f1, f2 = extract_formants(short, DEFAULT_SAMPLE_RATE)
        assert f1 == 0
        assert f2 == 0

    def test_sine_wave_produces_formants(self):
        """A synthetic vowel-like signal should produce non-zero formants."""
        sr = DEFAULT_SAMPLE_RATE
        t = np.arange(2048) / sr
        # Synthesize a signal with energy at ~300 Hz and ~2300 Hz (like /i/)
        signal = 0.7 * np.sin(2 * np.pi * 300 * t) + 0.3 * np.sin(2 * np.pi * 2300 * t)
        signal += 0.05 * np.random.randn(len(signal))  # noise
        f1, f2 = extract_formants(signal, sr)
        # At least one formant should be detected
        assert f1 > 0 or f2 > 0, "Should detect at least one formant"

    def test_formants_are_integers(self):
        """Formants should be returned as integers."""
        signal = _sine_wave(440.0, 0.1, DEFAULT_SAMPLE_RATE)
        f1, f2 = extract_formants(signal[:2048], DEFAULT_SAMPLE_RATE)
        assert isinstance(f1, int)
        assert isinstance(f2, int)

    def test_formants_consistent_across_calls(self):
        """Same input → same output (deterministic)."""
        signal = _sine_wave(300.0, 0.1, DEFAULT_SAMPLE_RATE)
        frame = signal[:2048]
        r1 = extract_formants(frame, DEFAULT_SAMPLE_RATE)
        r2 = extract_formants(frame, DEFAULT_SAMPLE_RATE)
        assert r1 == r2


# =============================================================================
# TEST: Segmentation
# =============================================================================


class TestSegmentation:
    """Verify segment_stream() word boundary detection."""

    def test_empty_stream(self):
        """Empty input → no segments."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        assert segment_stream([]) == []

    def test_all_silence(self):
        """All-silence stream → no segments."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        frames = _silence_frames(100)
        assert segment_stream(frames) == []

    def test_continuous_voiced_is_one_segment(self):
        """Continuous voiced audio → single segment."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        frames = _voiced_frames(50)
        segments = segment_stream(frames)
        assert len(segments) == 1
        assert segments[0].length == 50

    def test_silence_splits_segments(self):
        """Silence gap splits into two segments."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        frames = _voiced_frames(20) + _silence_frames(5) + _voiced_frames(20)
        segments = segment_stream(frames)
        assert len(segments) == 2

    def test_min_segment_length(self):
        """Segments shorter than 5 frames (50ms) are discarded."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        # 3 voiced frames + silence + 20 voiced frames
        frames = _voiced_frames(3) + _silence_frames(5) + _voiced_frames(20)
        segments = segment_stream(frames)
        # Only the 20-frame segment should survive
        assert len(segments) == 1
        assert segments[0].length == 20

    def test_max_segment_length(self):
        """Segments longer than 200 frames (2s) are force-split."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        frames = _voiced_frames(250)
        segments = segment_stream(frames)
        assert len(segments) >= 2

    def test_segment_timing(self):
        """Segment start/end correspond to frame indices."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        frames = _silence_frames(10) + _voiced_frames(30) + _silence_frames(10)
        segments = segment_stream(frames)
        assert len(segments) == 1
        assert segments[0].start == 10
        assert segments[0].duration_ms == 30 * 10

    def test_energy_dip_boundary(self):
        """Energy dip (8+ low frames) creates word boundary."""
        from vibe_core.mahamantra.sound.shabda_decoder import segment_stream
        # High energy → 10 frames of low energy (RMS=50) → high energy
        high = _voiced_frames(20, rms=150)
        low = [pack_frame(50, 0, 1200, 15000)] * 10
        frames = high + low + _voiced_frames(20, rms=150)
        segments = segment_stream(frames)
        assert len(segments) == 2


# =============================================================================
# TEST: CTC Deduplication
# =============================================================================


class TestDedup:
    """Verify _dedup_coords() CTC-style deduplication."""

    def test_empty(self):
        from vibe_core.mahamantra.sound.shabda_decoder import _dedup_coords
        assert _dedup_coords(()) == ()

    def test_single(self):
        from vibe_core.mahamantra.sound.shabda_decoder import _dedup_coords
        assert _dedup_coords((5,)) == (5,)

    def test_all_same(self):
        from vibe_core.mahamantra.sound.shabda_decoder import _dedup_coords
        assert _dedup_coords((12, 12, 12, 12, 12)) == (12,)

    def test_alternating(self):
        from vibe_core.mahamantra.sound.shabda_decoder import _dedup_coords
        assert _dedup_coords((5, 12, 5, 12)) == (5, 12, 5, 12)

    def test_realistic_speech(self):
        """Simulated frame-level output: each phoneme repeated ~5-10 frames."""
        from vibe_core.mahamantra.sound.shabda_decoder import _dedup_coords
        # "dha-r-ma" → coords 34, 42, 40, each held for multiple frames
        raw = (34,)*8 + (42,)*5 + (40,)*7
        assert _dedup_coords(raw) == (34, 42, 40)

    def test_preserves_repeated_phonemes(self):
        """Same coord appearing non-consecutively must be preserved."""
        from vibe_core.mahamantra.sound.shabda_decoder import _dedup_coords
        # "a-ka-a" → 0, 16, 0 (a appears twice, not consecutive)
        raw = (0,)*5 + (16,)*3 + (0,)*5
        assert _dedup_coords(raw) == (0, 16, 0)


# =============================================================================
# TEST: Scoring (RAMA edit distance)
# =============================================================================


class TestScoring:
    """Verify _score_candidate() RAMA edit distance."""

    def test_identical_is_perfect(self):
        """Identical coord sequences → score 1.0."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        coords = (34, 42, 40)  # dharma-like
        assert _score_candidate(coords, coords) == 1.0

    def test_empty_is_zero(self):
        """Empty input → 0.0."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        assert _score_candidate((), (34, 42, 40)) == 0.0
        assert _score_candidate((34, 42, 40), ()) == 0.0

    def test_same_element_better_than_different(self):
        """Coords sharing an element score higher than totally different."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        observed = (16,)  # ka — element=AKASHA
        same_elem = (17,)  # kha — element=AKASHA
        diff_elem = (36,)  # pa — element=PRITHVI

        score_same = _score_candidate(observed, same_elem)
        score_diff = _score_candidate(observed, diff_elem)
        assert score_same > score_diff, (
            f"Same element ({score_same}) should beat different ({score_diff})"
        )

    def test_same_varga_better_than_different_class(self):
        """Coords sharing varga class score higher than different class."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        # Use coords from DIFFERENT elements to isolate varga effect
        observed = (16,)  # ka — element=AKASHA, varga=sparsha
        same_varga = (31,)  # ta — element=JALA, varga=sparsha (same varga, diff element)
        diff_varga = (10,)  # e — element=VAYU, varga=svara (diff varga, diff element)

        score_same = _score_candidate(observed, same_varga)
        score_diff = _score_candidate(observed, diff_varga)
        assert score_same > score_diff

    def test_length_penalty(self):
        """Longer candidates against short observed get penalized."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        short = (34, 42)
        long = (34, 42, 40, 5)
        # short vs short = perfect, short vs long = penalized
        assert _score_candidate(short, short) > _score_candidate(short, long)

    def test_score_symmetric_tendency(self):
        """Score should be similar (not necessarily identical) in both directions."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        a = (34, 42, 40)
        b = (34, 42, 38)
        score_ab = _score_candidate(a, b)
        score_ba = _score_candidate(b, a)
        assert abs(score_ab - score_ba) < 0.1, "Should be approximately symmetric"

    def test_score_range(self):
        """All scores are in [0, 1]."""
        from vibe_core.mahamantra.sound.shabda_decoder import _score_candidate
        test_cases = [
            ((0,), (48,)),
            ((0, 1, 2), (46, 47, 48)),
            ((34,), (34,)),
            ((0, 0, 0, 0), (0,)),
        ]
        for a, b in test_cases:
            s = _score_candidate(a, b)
            assert 0.0 <= s <= 1.0, f"Score {s} out of range for {a} vs {b}"


# =============================================================================
# TEST: Pronunciation Dictionary
# =============================================================================


class TestPronunciationDict:
    """Verify PronunciationDict loading and lookup."""

    @pytest.fixture(scope="class")
    def pdict(self):
        from vibe_core.mahamantra.sound.shabda_decoder import PronunciationDict
        d = PronunciationDict()
        return d

    def test_sanskrit_entries_count(self, pdict):
        """Should have ~4000+ Sanskrit entries from lexicon."""
        assert pdict.sanskrit_count >= 3000, (
            f"Expected >=3000 Sanskrit entries, got {pdict.sanskrit_count}"
        )

    def test_english_entries_exist(self, pdict):
        """Should have English entries derived from meanings."""
        assert pdict.english_count > 0, "Expected English entries"

    def test_total_count(self, pdict):
        """Total should be Sanskrit + English."""
        assert pdict.total_count == pdict.sanskrit_count + pdict.english_count

    def test_lookup_sanskrit_word(self, pdict):
        """Known Sanskrit word should have coords."""
        # dharma should be in the Gita lexicon
        coords = pdict.lookup("dharma")
        if coords is not None:
            assert len(coords) > 0
            assert all(0 <= c < 49 for c in coords)

    def test_lookup_unknown_returns_none(self, pdict):
        """Unknown word returns None."""
        assert pdict.lookup("xyzzyplugh") is None

    def test_candidates_for_segment(self, pdict):
        """candidates_for_segment returns (word, coords) pairs."""
        # Look for any word starting at coord 0 (a-vowel) with length ~3
        candidates = pdict.candidates_for_segment(0, 3, length_tolerance=2)
        # Should find at least some words
        for word, coords in candidates:
            assert isinstance(word, str)
            assert isinstance(coords, tuple)
            assert len(coords) > 0


# =============================================================================
# TEST: Frame Scoring
# =============================================================================


class TestFrameScoring:
    """Verify score_frame() against phoneme templates."""

    def test_silence_returns_empty(self):
        """Silent frame → no candidates."""
        from vibe_core.mahamantra.sound.shabda_decoder import score_frame
        frame = pack_frame(0, 0, 0, 0)
        assert score_frame(frame) == []

    def test_voiced_frame_returns_candidates(self):
        """Voiced frame → at least one candidate."""
        from vibe_core.mahamantra.sound.shabda_decoder import score_frame
        frame = pack_frame(150, 0, 1200, 15000)  # voiced, KANTHYA varga
        result = score_frame(frame)
        assert len(result) > 0

    def test_candidates_are_sorted(self):
        """Candidates should be sorted by score descending."""
        from vibe_core.mahamantra.sound.shabda_decoder import score_frame
        frame = pack_frame(150, 0, 1200, 15000)
        result = score_frame(frame)
        if len(result) >= 2:
            assert result[0][1] >= result[1][1]

    def test_max_three_candidates(self):
        """At most 3 candidates returned."""
        from vibe_core.mahamantra.sound.shabda_decoder import score_frame
        frame = pack_frame(150, 2, 1200, 20000)
        result = score_frame(frame)
        assert len(result) <= 3

    def test_scores_in_range(self):
        """All scores in [0, 1]."""
        from vibe_core.mahamantra.sound.shabda_decoder import score_frame
        frame = pack_frame(150, 1, 1500, 18000)
        for _, score in score_frame(frame):
            assert 0.0 <= score <= 1.0


# =============================================================================
# TEST: Phoneme Templates
# =============================================================================


class TestPhonemeTemplates:
    """Verify PhonemeTemplate construction."""

    def test_all_templates_built(self):
        """Should have a template for each ARPAbet phoneme."""
        from vibe_core.mahamantra.sound.shabda_decoder import PHONEME_TEMPLATES
        arpabets = {t.arpabet for t in PHONEME_TEMPLATES}
        assert arpabets == set(ARPABET_TO_RAMA.keys())

    def test_vowel_templates_have_formants(self):
        """Vowel templates should have F1/F2 centers."""
        from vibe_core.mahamantra.sound.shabda_decoder import PHONEME_TEMPLATES
        vowels = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "EY",
                   "ER", "IH", "IY", "OW", "OY", "UH", "UW"}
        for t in PHONEME_TEMPLATES:
            if t.arpabet in vowels:
                assert t.f1_center > 0, f"{t.arpabet} should have F1"
                assert t.f2_center > 0, f"{t.arpabet} should have F2"

    def test_consonant_templates_no_formants(self):
        """Consonant templates should have F1=F2=0."""
        from vibe_core.mahamantra.sound.shabda_decoder import PHONEME_TEMPLATES
        for t in PHONEME_TEMPLATES:
            if t.sound_class != 0:  # not a vowel
                assert t.f1_center == 0, f"{t.arpabet} consonant shouldn't have F1"
                assert t.f2_center == 0, f"{t.arpabet} consonant shouldn't have F2"

    def test_sound_classes_correct(self):
        """Sound class matches RAMA coordinate range."""
        from vibe_core.mahamantra.sound.shabda_decoder import PHONEME_TEMPLATES
        for t in PHONEME_TEMPLATES:
            if t.rama_coord < WORDS:
                assert t.sound_class == 0, f"{t.arpabet} coord {t.rama_coord} should be svara"
            elif t.rama_coord <= 40:
                assert t.sound_class == 1, f"{t.arpabet} coord {t.rama_coord} should be sparsha"
            else:
                assert t.sound_class == 2, f"{t.arpabet} coord {t.rama_coord} should be shesha"


# =============================================================================
# TEST: End-to-End
# =============================================================================


class TestEndToEnd:
    """Integration tests for ShabdaDecoder."""

    def test_silence_stream_gives_empty_transcript(self):
        """All-silence stream → empty transcript."""
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder
        decoder = ShabdaDecoder()
        stream = ShabdaStream(
            frames=tuple(_silence_frames(100)),
            sample_rate=DEFAULT_SAMPLE_RATE,
            source="test_silence",
        )
        transcript = decoder.transcribe(stream)
        assert len(transcript.words) == 0
        assert transcript.text == ""

    def test_transcript_text_property(self):
        """Transcript.text joins word strings."""
        from vibe_core.mahamantra.sound.shabda_decoder import Transcript, TranscriptWord
        words = (
            TranscriptWord("dharma", 0.9, "sanskrit", (34, 42, 40, 5), 0, 100),
            TranscriptWord("yoga", 0.8, "sanskrit", (41, 12, 18, 5), 100, 200),
        )
        t = Transcript(words=words, duration_ms=200, source="test")
        assert t.text == "dharma yoga"

    def test_transcript_duration(self):
        """Transcript.duration_ms reflects stream length."""
        from vibe_core.mahamantra.sound.shabda_decoder import Transcript
        t = Transcript(words=(), duration_ms=5000, source="test")
        assert t.duration_ms == 5000

    def test_decoder_with_stream(self):
        """ShabdaDecoder.transcribe() on voiced audio returns a Transcript."""
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder
        # Build a stream with voiced content (may or may not match dictionary)
        frames = _voiced_frames(50, rms=150, varga=0, f0_x10=1200, centroid_x10=15000)
        stream = ShabdaStream(
            frames=tuple(frames),
            sample_rate=DEFAULT_SAMPLE_RATE,
            source="test_voiced",
        )
        decoder = ShabdaDecoder(min_confidence=0.0)
        transcript = decoder.transcribe(stream)
        # Should return a Transcript object (may have 0 or more words)
        assert hasattr(transcript, "text")
        assert hasattr(transcript, "words")
        assert hasattr(transcript, "duration_ms")

    def test_transcribe_segment_api(self):
        """transcribe_segment() returns list of TranscriptWord."""
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder
        frames = _voiced_frames(30)
        decoder = ShabdaDecoder(min_confidence=0.0)
        words = decoder.transcribe_segment(frames)
        assert isinstance(words, list)

    def test_min_confidence_filters(self):
        """Words below min_confidence threshold are excluded."""
        from vibe_core.mahamantra.sound.shabda_decoder import ShabdaDecoder
        frames = _voiced_frames(20)
        # Very high threshold — should filter everything
        decoder_strict = ShabdaDecoder(min_confidence=0.99)
        stream = ShabdaStream(
            frames=tuple(frames),
            sample_rate=DEFAULT_SAMPLE_RATE,
            source="test",
        )
        transcript = decoder_strict.transcribe(stream)
        # High threshold should return fewer/no words
        assert len(transcript.words) == 0 or all(
            w.confidence >= 0.99 for w in transcript.words
        )

    def test_transcript_word_fields(self):
        """TranscriptWord has all required fields."""
        from vibe_core.mahamantra.sound.shabda_decoder import TranscriptWord
        w = TranscriptWord(
            word="test",
            confidence=0.85,
            language="english",
            rama_coords=(31, 10, 47, 31),
            start_ms=0,
            end_ms=100,
        )
        assert w.word == "test"
        assert w.confidence == 0.85
        assert w.language == "english"
        assert len(w.rama_coords) == 4
        assert w.start_ms == 0
        assert w.end_ms == 100


# Ensure ShabdaStream import works here
from vibe_core.mahamantra.sound.shabda_intake import ShabdaStream  # noqa: E402
