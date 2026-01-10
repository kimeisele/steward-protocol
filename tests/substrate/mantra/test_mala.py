"""
Tests for MALA - The Round Level
================================
"""

import pytest
from vibe_core.protocols.substrate.mantra.mala import (
    BEADS_PER_MALA,
    SUMERU_COUNT,
    MalaPhase,
    Mala,
    MalaMetrics,
    MALA_METRICS,
    create_mala,
    iter_mala_vakyas,
    get_phase_name,
)


class TestMalaConstants:
    """Test mala constants."""

    def test_beads_is_108(self):
        """A mala has 108 beads."""
        assert BEADS_PER_MALA == 108

    def test_sumeru_is_1(self):
        """There is 1 sumeru bead."""
        assert SUMERU_COUNT == 1


class TestMalaPhase:
    """Test the MalaPhase enum."""

    def test_four_phases(self):
        """There are 4 phases."""
        assert MalaPhase.BEGINNING == 0
        assert MalaPhase.ASCENDING == 1
        assert MalaPhase.PEAK == 2
        assert MalaPhase.COMPLETING == 3


class TestMala:
    """Test the Mala dataclass."""

    def test_mala_has_108_mantras(self):
        """Mala has 108 mantras."""
        mala = create_mala()
        assert mala.total_mantras == 108
        assert len(mala) == 108

    def test_mala_has_1728_words(self):
        """Mala has 1728 words (108 × 16)."""
        mala = create_mala()
        assert mala.total_words == 1728

    def test_mala_has_3456_syllables(self):
        """Mala has 3456 syllables (108 × 32)."""
        mala = create_mala()
        assert mala.total_syllables == 3456

    def test_mala_initial_state(self):
        """New mala starts at count 0."""
        mala = create_mala()
        assert mala.current_count == 0
        assert mala.completed == False

    def test_mala_chant_one(self):
        """Chanting one advances count."""
        mala = create_mala()
        vakya = mala.chant_one()
        assert vakya is not None
        assert mala.current_count == 1

    def test_mala_completes_at_108(self):
        """Mala completes after 108 chants."""
        mala = create_mala()
        for _ in range(108):
            mala.chant_one()
        assert mala.completed == True
        assert mala.chant_one() is None

    def test_mala_phase_beginning(self):
        """Phase is BEGINNING for counts 1-27."""
        mala = create_mala()
        mala.current_count = 1
        assert mala.phase == MalaPhase.BEGINNING
        mala.current_count = 27
        assert mala.phase == MalaPhase.BEGINNING

    def test_mala_phase_ascending(self):
        """Phase is ASCENDING for counts 28-54."""
        mala = create_mala()
        mala.current_count = 28
        assert mala.phase == MalaPhase.ASCENDING
        mala.current_count = 54
        assert mala.phase == MalaPhase.ASCENDING

    def test_mala_phase_peak(self):
        """Phase is PEAK for counts 55-81."""
        mala = create_mala()
        mala.current_count = 55
        assert mala.phase == MalaPhase.PEAK
        mala.current_count = 81
        assert mala.phase == MalaPhase.PEAK

    def test_mala_phase_completing(self):
        """Phase is COMPLETING for counts 82-108."""
        mala = create_mala()
        mala.current_count = 82
        assert mala.phase == MalaPhase.COMPLETING
        mala.current_count = 108
        assert mala.phase == MalaPhase.COMPLETING

    def test_mala_progress(self):
        """Progress is correctly calculated."""
        mala = create_mala()
        assert mala.progress == 0.0
        mala.current_count = 54
        assert mala.progress == 0.5
        mala.current_count = 108
        assert mala.progress == 1.0

    def test_mala_remaining(self):
        """Remaining is correctly calculated."""
        mala = create_mala()
        assert mala.remaining == 108
        mala.current_count = 50
        assert mala.remaining == 58

    def test_mala_get_vakya(self):
        """Can get vakya by index."""
        mala = create_mala()
        vakya = mala.get_vakya(0)
        assert vakya.count == 1
        vakya = mala.get_vakya(107)
        assert vakya.count == 108

    def test_mala_get_vakya_invalid(self):
        """Invalid index raises IndexError."""
        mala = create_mala()
        with pytest.raises(IndexError):
            mala.get_vakya(108)

    def test_mala_reset(self):
        """Reset clears the mala state."""
        mala = create_mala()
        mala.current_count = 50
        mala.completed = True
        mala.reset()
        assert mala.current_count == 0
        assert mala.completed == False

    def test_mala_iterable(self):
        """Mala is iterable over vakyas."""
        mala = create_mala()
        vakyas = list(mala)
        assert len(vakyas) == 108


class TestMalaMetrics:
    """Test MalaMetrics."""

    def test_metrics_mantras(self):
        """Metrics has correct mantra count."""
        assert MALA_METRICS.total_mantras == 108

    def test_metrics_words(self):
        """Metrics has correct word count."""
        assert MALA_METRICS.total_words == 1728

    def test_metrics_syllables(self):
        """Metrics has correct syllable count."""
        assert MALA_METRICS.total_syllables == 3456

    def test_metrics_pada_counts(self):
        """Metrics has correct pada counts."""
        assert MALA_METRICS.total_hare == 864      # 108 × 8
        assert MALA_METRICS.total_krishna == 432  # 108 × 4
        assert MALA_METRICS.total_rama == 432     # 108 × 4


class TestPhaseName:
    """Test get_phase_name function."""

    def test_phase_names(self):
        """Phase names are descriptive."""
        assert "Connection" in get_phase_name(MalaPhase.BEGINNING)
        assert "Momentum" in get_phase_name(MalaPhase.ASCENDING)
        assert "Absorption" in get_phase_name(MalaPhase.PEAK)
        assert "Integration" in get_phase_name(MalaPhase.COMPLETING)
