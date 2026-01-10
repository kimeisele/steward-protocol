"""
Tests for SADHANA - The Session Level
=====================================
"""

import pytest
from vibe_core.protocols.substrate.mantra.sadhana import (
    ROUNDS_PER_SADHANA,
    MANTRAS_PER_SADHANA,
    WORDS_PER_SADHANA,
    SYLLABLES_PER_SADHANA,
    AVG_MANTRA_DURATION,
    SadhanaState,
    SadhanaIntensity,
    Sadhana,
    SadhanaMetrics,
    SADHANA_METRICS,
    create_sadhana,
    create_intensive_sadhana,
    get_intensity_name,
)


class TestSadhanaConstants:
    """Test sadhana constants."""

    def test_rounds_is_16(self):
        """Standard sadhana is 16 rounds."""
        assert ROUNDS_PER_SADHANA == 16

    def test_mantras_is_1728(self):
        """16 rounds × 108 = 1728 mantras."""
        assert MANTRAS_PER_SADHANA == 1728

    def test_words_is_27648(self):
        """1728 × 16 = 27648 words."""
        assert WORDS_PER_SADHANA == 27648

    def test_syllables_is_55296(self):
        """1728 × 32 = 55296 syllables."""
        assert SYLLABLES_PER_SADHANA == 55296


class TestSadhanaState:
    """Test the SadhanaState enum."""

    def test_five_states(self):
        """There are 5 states."""
        assert SadhanaState.NOT_STARTED == 0
        assert SadhanaState.IN_PROGRESS == 1
        assert SadhanaState.PAUSED == 2
        assert SadhanaState.COMPLETED == 3
        assert SadhanaState.ABANDONED == 4


class TestSadhanaIntensity:
    """Test the SadhanaIntensity enum."""

    def test_intensity_levels(self):
        """Intensity levels are correct."""
        assert SadhanaIntensity.MINIMUM == 16
        assert SadhanaIntensity.MODERATE == 32
        assert SadhanaIntensity.INTENSIVE == 64
        assert SadhanaIntensity.EXTREME == 192


class TestSadhana:
    """Test the Sadhana dataclass."""

    def test_sadhana_has_16_rounds(self):
        """Standard sadhana has 16 rounds."""
        sadhana = create_sadhana()
        assert sadhana.target_rounds == 16
        assert len(sadhana) == 16

    def test_sadhana_total_mantras(self):
        """Sadhana has correct total mantras."""
        sadhana = create_sadhana()
        assert sadhana.total_mantras == 1728

    def test_sadhana_initial_state(self):
        """New sadhana starts NOT_STARTED."""
        sadhana = create_sadhana()
        assert sadhana.state == SadhanaState.NOT_STARTED
        assert sadhana.current_round == 0

    def test_sadhana_begin(self):
        """Begin starts the sadhana."""
        sadhana = create_sadhana()
        mala = sadhana.begin()
        assert sadhana.state == SadhanaState.IN_PROGRESS
        assert sadhana.current_round == 1
        assert sadhana.start_time is not None
        assert mala is not None

    def test_sadhana_begin_twice_raises(self):
        """Cannot begin twice."""
        sadhana = create_sadhana()
        sadhana.begin()
        with pytest.raises(RuntimeError):
            sadhana.begin()

    def test_sadhana_complete_round(self):
        """Complete round advances to next."""
        sadhana = create_sadhana()
        sadhana.begin()
        mala = sadhana.complete_round()
        assert sadhana.current_round == 2
        assert mala is not None

    def test_sadhana_completes_after_16(self):
        """Sadhana completes after 16 rounds."""
        sadhana = create_sadhana()
        sadhana.begin()
        for _ in range(16):
            sadhana.complete_round()
        assert sadhana.state == SadhanaState.COMPLETED
        assert sadhana.end_time is not None

    def test_sadhana_progress(self):
        """Progress is correctly calculated."""
        sadhana = create_sadhana()
        sadhana.begin()
        # After beginning, we're at round 1, count 0
        assert sadhana.progress == 0.0

    def test_sadhana_remaining_rounds(self):
        """Remaining rounds is correctly calculated."""
        sadhana = create_sadhana()
        sadhana.begin()
        assert sadhana.remaining_rounds == 15  # 16 - 1
        sadhana.complete_round()
        assert sadhana.remaining_rounds == 14  # 16 - 2

    def test_sadhana_intensity(self):
        """Intensity is classified correctly."""
        s16 = create_sadhana(16)
        assert s16.intensity == SadhanaIntensity.MINIMUM

        s32 = create_sadhana(32)
        assert s32.intensity == SadhanaIntensity.MODERATE

        s64 = create_sadhana(64)
        assert s64.intensity == SadhanaIntensity.INTENSIVE

        s192 = create_sadhana(192)
        assert s192.intensity == SadhanaIntensity.EXTREME

    def test_sadhana_pause_resume(self):
        """Can pause and resume sadhana."""
        sadhana = create_sadhana()
        sadhana.begin()
        sadhana.pause()
        assert sadhana.state == SadhanaState.PAUSED

        mala = sadhana.resume()
        assert sadhana.state == SadhanaState.IN_PROGRESS
        assert mala is not None

    def test_sadhana_abandon(self):
        """Can abandon sadhana."""
        sadhana = create_sadhana()
        sadhana.begin()
        sadhana.abandon()
        assert sadhana.state == SadhanaState.ABANDONED
        assert sadhana.end_time is not None

    def test_sadhana_get_mala(self):
        """Can get mala by round number (1-indexed)."""
        sadhana = create_sadhana()
        mala1 = sadhana.get_mala(1)
        assert mala1.round_number == 1
        mala16 = sadhana.get_mala(16)
        assert mala16.round_number == 16

    def test_sadhana_get_mala_invalid(self):
        """Invalid round raises IndexError."""
        sadhana = create_sadhana()
        with pytest.raises(IndexError):
            sadhana.get_mala(0)
        with pytest.raises(IndexError):
            sadhana.get_mala(17)

    def test_sadhana_iterable(self):
        """Sadhana is iterable over malas."""
        sadhana = create_sadhana()
        malas = list(sadhana)
        assert len(malas) == 16


class TestCreateSadhana:
    """Test sadhana creation functions."""

    def test_create_with_target(self):
        """Can create sadhana with specific target."""
        s = create_sadhana(32)
        assert s.target_rounds == 32

    def test_create_intensive(self):
        """create_intensive_sadhana creates 64-round sadhana."""
        s = create_intensive_sadhana()
        assert s.target_rounds == 64


class TestSadhanaMetrics:
    """Test SadhanaMetrics."""

    def test_metrics_rounds(self):
        """Metrics has correct round count."""
        assert SADHANA_METRICS.total_rounds == 16

    def test_metrics_mantras(self):
        """Metrics has correct mantra count."""
        assert SADHANA_METRICS.total_mantras == 1728

    def test_metrics_words(self):
        """Metrics has correct word count."""
        assert SADHANA_METRICS.total_words == 27648

    def test_metrics_syllables(self):
        """Metrics has correct syllable count."""
        assert SADHANA_METRICS.total_syllables == 55296

    def test_metrics_pada_counts(self):
        """Metrics has correct pada counts."""
        assert SADHANA_METRICS.total_hare == 13824     # 1728 × 8
        assert SADHANA_METRICS.total_krishna == 6912  # 1728 × 4
        assert SADHANA_METRICS.total_rama == 6912     # 1728 × 4


class TestIntensityName:
    """Test get_intensity_name function."""

    def test_intensity_names(self):
        """Intensity names are descriptive."""
        assert "16" in get_intensity_name(SadhanaIntensity.MINIMUM)
        assert "32" in get_intensity_name(SadhanaIntensity.MODERATE)
        assert "64" in get_intensity_name(SadhanaIntensity.INTENSIVE)
        assert "Laksha" in get_intensity_name(SadhanaIntensity.EXTREME)
