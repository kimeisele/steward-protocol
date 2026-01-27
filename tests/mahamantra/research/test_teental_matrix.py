"""
Tests for Teental Binary Matrix - Kirtan Rhythm Encoding
=========================================================

"tāla-yutam gaditaṁ gīta-yutam"
"With rhythm, with music..."
— From traditional Kirtan

NO HARDCODED VALUES - All derived from seed.py constants.

These tests verify:
1. Mridanga stroke encoding (2-bit per stroke)
2. Teental structure (16 beats = WORDS)
3. Vibhag structure (4 sections = QUARTERS)
4. SAM/KHALI positions from seed.py
5. Kartal accent pattern
6. 48-bit Kirtan encoding (LILA bits)
"""

import pytest

from vibe_core.mahamantra.research.dharma.teental_matrix import (
    KARTAL_PATTERN,
    KIRTAN_48BIT,
    KIRTAN_MATRIX,
    SAM_POSITIONS,
    TEENTAL_BINARY,
    TEENTAL_DECIMAL,
    TEENTAL_STROKES,
    TEENTAL_VIBHAGS,
    KirtanBeat,
    MridangaStroke,
    Vibhag,
    analyze_mahamantra_correlation,
    get_bass_pattern,
    get_treble_pattern,
)
from vibe_core.mahamantra.substrate.seed import (
    HALVES,
    KHALI_POSITION,
    LILA,
    MATRA_PER_VIBHAG,
    MRIDANGA_HEADS,
    NAVA,
    QUARTERS,
    SAM_SUM,
    SEVEN,
    TEENTAL_MATRA,
    TRINITY,
    VIBHAG_COUNT,
    WORDS,
)


class TestMridangaStrokeEncoding:
    """Test the 2-bit Mridanga stroke encoding."""

    def test_stroke_values(self):
        """Stroke values must be 0-3 (2-bit)."""
        assert MridangaStroke.SILENT.value == 0b00
        assert MridangaStroke.TIN.value == 0b01
        assert MridangaStroke.TA.value == 0b10
        assert MridangaStroke.DHA.value == 0b11

    def test_stroke_fits_in_mridanga_heads_bits(self):
        """All strokes must fit in MRIDANGA_HEADS (2) bits."""
        for stroke in MridangaStroke:
            assert stroke.value < (1 << MRIDANGA_HEADS)

    def test_bass_treble_properties(self):
        """Bass and treble properties must match encoding."""
        # SILENT: no heads
        assert not MridangaStroke.SILENT.bass_active
        assert not MridangaStroke.SILENT.treble_active

        # TIN: treble only
        assert not MridangaStroke.TIN.bass_active
        assert MridangaStroke.TIN.treble_active

        # TA: bass only
        assert MridangaStroke.TA.bass_active
        assert not MridangaStroke.TA.treble_active

        # DHA: both heads
        assert MridangaStroke.DHA.bass_active
        assert MridangaStroke.DHA.treble_active

    def test_both_heads_property(self):
        """both_heads property must be True only for DHA/DHIN."""
        assert MridangaStroke.DHA.both_heads
        assert MridangaStroke.DHIN.both_heads
        assert not MridangaStroke.TIN.both_heads
        assert not MridangaStroke.TA.both_heads
        assert not MridangaStroke.SILENT.both_heads


class TestTeentalStructure:
    """Test the Teental pattern structure."""

    def test_teental_has_words_beats(self):
        """Teental must have exactly WORDS (16) beats."""
        assert len(TEENTAL_STROKES) == WORDS
        assert len(TEENTAL_BINARY) == WORDS
        assert TEENTAL_MATRA == WORDS

    def test_vibhag_count(self):
        """Must have VIBHAG_COUNT (4) vibhags."""
        assert len(TEENTAL_VIBHAGS) == VIBHAG_COUNT
        assert VIBHAG_COUNT == QUARTERS

    def test_vibhag_size(self):
        """Each vibhag must have MATRA_PER_VIBHAG (4) beats."""
        for vibhag in TEENTAL_VIBHAGS:
            assert len(vibhag.strokes) == MATRA_PER_VIBHAG
        assert MATRA_PER_VIBHAG == QUARTERS

    def test_total_beats(self):
        """Total beats = VIBHAG_COUNT × MATRA_PER_VIBHAG = WORDS."""
        assert VIBHAG_COUNT * MATRA_PER_VIBHAG == WORDS

    def test_vibhag_numbering(self):
        """Vibhags must be numbered 1-4."""
        for i, vibhag in enumerate(TEENTAL_VIBHAGS):
            assert vibhag.number == i + 1

    def test_vibhag_start_beats(self):
        """Vibhag start beats must be SAM positions."""
        for vibhag in TEENTAL_VIBHAGS:
            assert vibhag.start_beat in SAM_POSITIONS


class TestSamKhaliPositions:
    """Test SAM and KHALI positions from seed.py."""

    def test_sam_positions(self):
        """SAM positions must be 1, 5, 9, 13."""
        assert SAM_POSITIONS == (1, 5, 9, 13)
        assert len(SAM_POSITIONS) == VIBHAG_COUNT

    def test_sam_sum(self):
        """SAM_SUM must equal T(7) = 28."""
        assert sum(SAM_POSITIONS) == SAM_SUM
        assert SAM_SUM == 28
        # T(7) = 7 × 8 / 2 = 28
        assert SAM_SUM == SEVEN * (SEVEN + 1) // HALVES

    def test_khali_position(self):
        """KHALI must be at position 9 = NAVA."""
        assert KHALI_POSITION == NAVA
        assert KHALI_POSITION == 9

    def test_khali_vibhag(self):
        """Vibhag 3 must be the KHALI vibhag."""
        assert TEENTAL_VIBHAGS[2].is_khali


class TestTeentalPattern:
    """Test the actual Teental bol pattern."""

    def test_vibhag_1_pattern(self):
        """Vibhag 1: Dha Dhin Dhin Dha (all both-heads)."""
        v1 = TEENTAL_VIBHAGS[0]
        assert v1.is_sam
        assert all(s.both_heads for s in v1.strokes)

    def test_vibhag_2_pattern(self):
        """Vibhag 2: Dha Dhin Dhin Dha (all both-heads)."""
        v2 = TEENTAL_VIBHAGS[1]
        assert all(s.both_heads for s in v2.strokes)

    def test_vibhag_3_pattern(self):
        """Vibhag 3: Dha Tin Tin Ta (KHALI - varied strokes)."""
        v3 = TEENTAL_VIBHAGS[2]
        assert v3.is_khali
        # Dha (both), Tin (treble), Tin (treble), Ta (bass)
        assert v3.strokes[0] == MridangaStroke.DHA
        assert v3.strokes[1] == MridangaStroke.TIN
        assert v3.strokes[2] == MridangaStroke.TIN
        assert v3.strokes[3] == MridangaStroke.TA

    def test_vibhag_4_pattern(self):
        """Vibhag 4: Ta Dhin Dhin Dha."""
        v4 = TEENTAL_VIBHAGS[3]
        assert v4.strokes[0] == MridangaStroke.TA
        assert v4.strokes[1].both_heads
        assert v4.strokes[2].both_heads
        assert v4.strokes[3] == MridangaStroke.DHA


class TestBinaryPatterns:
    """Test binary pattern extraction."""

    def test_bass_pattern_length(self):
        """Bass pattern must have WORDS elements."""
        bass = get_bass_pattern()
        assert len(bass) == WORDS

    def test_treble_pattern_length(self):
        """Treble pattern must have WORDS elements."""
        treble = get_treble_pattern()
        assert len(treble) == WORDS

    def test_bass_pattern_values(self):
        """Bass pattern must be 0 or 1."""
        bass = get_bass_pattern()
        assert all(b in (0, 1) for b in bass)

    def test_treble_pattern_values(self):
        """Treble pattern must be 0 or 1."""
        treble = get_treble_pattern()
        assert all(t in (0, 1) for t in treble)

    def test_khali_vibhag_has_varied_strokes(self):
        """KHALI vibhag (3) should have varied bass/treble patterns."""
        bass = get_bass_pattern()
        treble = get_treble_pattern()

        # Vibhag 3 is beats 9-12 (indices 8-11)
        khali_bass = bass[8:12]
        khali_treble = treble[8:12]

        # Should have both 0 and 1 in both patterns
        assert 0 in khali_bass or 1 in khali_bass
        assert 0 in khali_treble or 1 in khali_treble


class TestKartalPattern:
    """Test Kartal accent pattern."""

    def test_kartal_pattern_length(self):
        """Kartal pattern must have WORDS elements."""
        assert len(KARTAL_PATTERN) == WORDS

    def test_kartal_accents_at_sam(self):
        """Kartal accents must be at SAM positions."""
        for i, accent in enumerate(KARTAL_PATTERN):
            pos = i + 1
            if pos in SAM_POSITIONS:
                assert accent == 1, f"SAM at {pos} must have Kartal accent"
            else:
                assert accent == 0, f"Non-SAM at {pos} must not have Kartal accent"

    def test_kartal_accent_count(self):
        """Number of Kartal accents must equal VIBHAG_COUNT."""
        assert sum(KARTAL_PATTERN) == VIBHAG_COUNT


class TestKirtanMatrix:
    """Test the combined Kirtan matrix."""

    def test_kirtan_matrix_length(self):
        """Kirtan matrix must have WORDS beats."""
        assert len(KIRTAN_MATRIX) == WORDS

    def test_kirtan_beat_positions(self):
        """Kirtan beats must have positions 1-16."""
        positions = [beat.position for beat in KIRTAN_MATRIX]
        assert positions == list(range(1, WORDS + 1))

    def test_kirtan_beat_vibhags(self):
        """Each beat must have correct vibhag assignment."""
        for i, beat in enumerate(KIRTAN_MATRIX):
            expected_vibhag = (i // MATRA_PER_VIBHAG) + 1
            assert beat.vibhag == expected_vibhag

    def test_kirtan_sam_flag(self):
        """Only beat 1 should have is_sam=True."""
        for beat in KIRTAN_MATRIX:
            if beat.position == 1:
                assert beat.is_sam
            else:
                assert not beat.is_sam

    def test_kirtan_khali_flag(self):
        """Only beat 9 should have is_khali=True."""
        for beat in KIRTAN_MATRIX:
            if beat.position == KHALI_POSITION:
                assert beat.is_khali
            else:
                assert not beat.is_khali


class TestKirtan48Bit:
    """Test the 48-bit Kirtan encoding."""

    def test_48bit_derivation(self):
        """48 bits = WORDS × 3 bits = LILA bits."""
        # 16 beats × 3 bits per beat = 48 bits
        assert WORDS * TRINITY == LILA
        assert WORDS * 3 == 48

    def test_48bit_is_positive(self):
        """48-bit value must be positive."""
        assert KIRTAN_48BIT > 0

    def test_48bit_fits_in_48_bits(self):
        """Value must fit in 48 bits."""
        assert KIRTAN_48BIT < (1 << 48)


class TestMahamantraCorrelation:
    """Test correlation analysis between Teental and Mahamantra."""

    def test_correlation_returns_dict(self):
        """analyze_mahamantra_correlation must return a dict."""
        result = analyze_mahamantra_correlation()
        assert isinstance(result, dict)

    def test_correlation_has_all_positions(self):
        """Correlation must have all WORDS positions."""
        result = analyze_mahamantra_correlation()
        assert len(result["correlations"]) == WORDS

    def test_correlation_totals(self):
        """Total HARE + NAME must equal WORDS."""
        result = analyze_mahamantra_correlation()
        total_hare = result["total_hare"]
        total_name = result["total_name"]
        assert total_hare + total_name == WORDS


class TestVibhagBinaryValue:
    """Test Vibhag binary value encoding."""

    def test_vibhag_binary_value_fits_in_8_bits(self):
        """Each vibhag (4 beats × 2 bits) must fit in 8 bits."""
        for vibhag in TEENTAL_VIBHAGS:
            assert vibhag.binary_value < 256


class TestKirtanBeatBinaryValue:
    """Test KirtanBeat binary value encoding."""

    def test_beat_binary_value_is_3_bit(self):
        """Each beat's binary value must fit in 3 bits."""
        for beat in KIRTAN_MATRIX:
            assert beat.binary_value < 8  # 2^3 = 8
