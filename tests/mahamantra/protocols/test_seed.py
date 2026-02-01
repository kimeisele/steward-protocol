"""
TESTS: _seed.py - The Seed Protocol (Mathematical Constitution)
================================================================

REAL TESTS for:
1. Sacred constants (WORDS, PARAMPARA, etc.)
2. Cosmic Frame constants
3. Jiva constants
4. Prana/timing constants
5. Harmonic resonances
6. Flute constants
"""

import pytest
from vibe_core.mahamantra.protocols._seed import (
    # Sacred Constants
    WORDS,
    PARAMPARA,
    TRINITY,
    QUARTERS,
    PANCHA,
    SHARANAGATI,
    NAVA,
    LILA,
    MALA,
    # Cosmic Frame
    COSMIC_FRAME,
    NAKSHATRA_UNIT,
    TITHI_UNIT,
    PADA_UNIT,
    QUARTER_UNIT,
    # Jiva
    JIVA_CYCLE,
    JIVA_QUALITIES,
    # Prana Timing (DERIVED: SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS)
    SECONDS_PER_DAY,
    PRANA_DURATION_S,
    PRANA_DURATION_MS,
    TICK_INTERVAL_MS,
    # Epoch
    EPOCH_KEY,
    # Derived
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    HALVES,
    HALF_SIZE,
    KSETRAJNA,
    MAHAJANA_COUNT,
    AVATAR_COUNT,
    KSHETRA,
    GITA_CHAPTERS,
    AKSARA_COUNT,
    QUALITIES,
    HIDDEN_RESERVE,
    ROUNDS,
    DAILY_MANTRAS,
    # Hidden Bridge
    PHASE_DURATION,
    # Harmonic Resonances
    NADI_RESONANCE,
    FIELD_RESONANCE,
    # Three Flutes
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    FLUTE_HOLES_SUM,
    FLUTE_HOLES_PRODUCT,
    # Acoustic
    ACOUSTIC_RATIO,
    END_CORRECTION,
    VENU_FREQ,
    VAMSI_FREQ,
    MURALI_FREQ,
    CUTOFF_CONSTANT,
)


# =============================================================================
# Sacred Constants Tests
# =============================================================================


class TestSacredConstants:
    """Test sacred constants."""

    def test_words_is_16(self):
        """WORDS is 16."""
        assert WORDS == 16

    def test_parampara_is_37(self):
        """PARAMPARA is 37."""
        assert PARAMPARA == 37

    def test_trinity_is_3(self):
        """TRINITY is 3."""
        assert TRINITY == 3

    def test_quarters_is_4(self):
        """QUARTERS is 4."""
        assert QUARTERS == 4

    def test_pancha_is_5(self):
        """PANCHA is 5."""
        assert PANCHA == 5

    def test_sharanagati_is_6(self):
        """SHARANAGATI is 6."""
        assert SHARANAGATI == 6

    def test_nava_is_9(self):
        """NAVA is 9."""
        assert NAVA == 9

    def test_lila_is_48(self):
        """LILA is 48."""
        assert LILA == 48
        assert LILA == WORDS * TRINITY

    def test_mala_is_108(self):
        """MALA is 108."""
        assert MALA == 108
        assert MALA == MAHAJANA_COUNT * NAVA


# =============================================================================
# Cosmic Frame Tests
# =============================================================================


class TestCosmicFrame:
    """Test cosmic frame constants."""

    def test_cosmic_frame_is_21600(self):
        """COSMIC_FRAME is 21600."""
        assert COSMIC_FRAME == 21600

    def test_nakshatra_unit(self):
        """NAKSHATRA_UNIT is 800."""
        assert NAKSHATRA_UNIT == 800
        assert COSMIC_FRAME % NAKSHATRA_UNIT == 0

    def test_tithi_unit(self):
        """TITHI_UNIT is 720."""
        assert TITHI_UNIT == 720
        assert COSMIC_FRAME % TITHI_UNIT == 0

    def test_pada_unit(self):
        """PADA_UNIT is 200."""
        assert PADA_UNIT == 200
        assert COSMIC_FRAME % PADA_UNIT == 0

    def test_quarter_unit(self):
        """QUARTER_UNIT is 5400."""
        assert QUARTER_UNIT == 5400
        assert COSMIC_FRAME % QUARTER_UNIT == 0


# =============================================================================
# Jiva Tests
# =============================================================================


class TestJiva:
    """Test Jiva constants."""

    def test_jiva_cycle_is_432(self):
        """JIVA_CYCLE is 432."""
        assert JIVA_CYCLE == 432
        assert JIVA_CYCLE == MALA * QUARTERS

    def test_jiva_qualities_is_50(self):
        """JIVA_QUALITIES is 50."""
        assert JIVA_QUALITIES == 50
        assert JIVA_QUALITIES == COSMIC_FRAME // JIVA_CYCLE


# =============================================================================
# Prana Tests - FULLY DERIVED FROM MAHAMANTRA
# =============================================================================
# SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS = 21600 × 4 = 86400
# The Vedic day is divided into 21600 pranas, and the seconds follow.


class TestPrana:
    """Test Prana/timing constants - ALL DERIVED FROM MAHAMANTRA."""

    def test_seconds_per_day(self):
        """SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS = 86400."""
        assert SECONDS_PER_DAY == 86400
        assert SECONDS_PER_DAY == COSMIC_FRAME * QUARTERS

    def test_prana_duration_s(self):
        """PRANA_DURATION_S = QUARTERS = 4."""
        assert PRANA_DURATION_S == 4
        assert PRANA_DURATION_S == QUARTERS

    def test_prana_duration_ms(self):
        """PRANA_DURATION_MS = 4000."""
        assert PRANA_DURATION_MS == 4000

    def test_tick_interval_ms(self):
        """TICK_INTERVAL_MS = PRANA_DURATION_MS // WORDS = 250."""
        assert TICK_INTERVAL_MS == 250
        assert TICK_INTERVAL_MS == PRANA_DURATION_MS // WORDS


# =============================================================================
# Epoch Key Tests
# =============================================================================


class TestEpochKey:
    """Test Epoch Key."""

    def test_epoch_key_is_1972(self):
        """EPOCH_KEY is 1972."""
        assert EPOCH_KEY == 1972


# =============================================================================
# Derived Constants Tests
# =============================================================================


class TestDerivedConstants:
    """Test derived constants."""

    def test_hare_count_is_8(self):
        """HARE_COUNT is 8."""
        assert HARE_COUNT == 8

    def test_krishna_count_is_4(self):
        """KRISHNA_COUNT is 4."""
        assert KRISHNA_COUNT == 4

    def test_rama_count_is_4(self):
        """RAMA_COUNT is 4."""
        assert RAMA_COUNT == 4

    def test_halves_is_2(self):
        """HALVES is 2."""
        assert HALVES == 2

    def test_half_size_is_8(self):
        """HALF_SIZE is 8."""
        assert HALF_SIZE == 8

    def test_ksetrajna_is_1(self):
        """KSETRAJNA is 1."""
        assert KSETRAJNA == 1

    def test_mahajana_count_is_12(self):
        """MAHAJANA_COUNT is 12."""
        assert MAHAJANA_COUNT == 12

    def test_avatar_count_is_4(self):
        """AVATAR_COUNT is 4."""
        assert AVATAR_COUNT == 4
        assert AVATAR_COUNT == QUARTERS

    def test_kshetra_is_24(self):
        """KSHETRA is 24."""
        assert KSHETRA == 24
        assert KSHETRA == WORDS + HARE_COUNT

    def test_gita_chapters_is_18(self):
        """GITA_CHAPTERS is 18."""
        assert GITA_CHAPTERS == 18
        assert GITA_CHAPTERS == SHARANAGATI * TRINITY

    def test_aksara_count_is_32(self):
        """AKSARA_COUNT is 32."""
        assert AKSARA_COUNT == 32
        assert AKSARA_COUNT == WORDS * 2

    def test_qualities_is_64(self):
        """QUALITIES is 64."""
        assert QUALITIES == 64
        assert QUALITIES == WORDS * QUARTERS

    def test_hidden_reserve_is_16(self):
        """HIDDEN_RESERVE is 16."""
        assert HIDDEN_RESERVE == 16
        assert HIDDEN_RESERVE == QUALITIES - LILA

    def test_rounds_is_16(self):
        """ROUNDS is 16."""
        assert ROUNDS == 16

    def test_daily_mantras(self):
        """DAILY_MANTRAS is 1728."""
        assert DAILY_MANTRAS == 1728
        assert DAILY_MANTRAS == MALA * ROUNDS


# =============================================================================
# Hidden Bridge Tests
# =============================================================================


class TestHiddenBridge:
    """Test hidden bridge constants."""

    def test_phase_duration_is_12(self):
        """PHASE_DURATION is 12."""
        assert PHASE_DURATION == 12
        assert PHASE_DURATION == LILA // QUARTERS
        assert PHASE_DURATION == MAHAJANA_COUNT


# =============================================================================
# Harmonic Resonances Tests
# =============================================================================


class TestHarmonicResonances:
    """Test harmonic resonance constants."""

    def test_nadi_resonance_is_72(self):
        """NADI_RESONANCE is 72."""
        assert NADI_RESONANCE == 72
        assert NADI_RESONANCE == JIVA_CYCLE // SHARANAGATI

    def test_field_resonance_is_144(self):
        """FIELD_RESONANCE is 144."""
        assert FIELD_RESONANCE == 144
        assert FIELD_RESONANCE == MAHAJANA_COUNT * MAHAJANA_COUNT

    def test_field_is_double_nadi(self):
        """FIELD_RESONANCE is 2x NADI_RESONANCE."""
        assert FIELD_RESONANCE == NADI_RESONANCE * 2


# =============================================================================
# Three Flutes Tests
# =============================================================================


class TestThreeFlutes:
    """Test flute constants."""

    def test_venu_holes_is_6(self):
        """VENU_HOLES is 6."""
        assert VENU_HOLES == 6
        assert VENU_HOLES == SHARANAGATI

    def test_vamsi_holes_is_9(self):
        """VAMSI_HOLES is 9."""
        assert VAMSI_HOLES == 9
        assert VAMSI_HOLES == NAVA

    def test_murali_holes_is_4(self):
        """MURALI_HOLES is 4."""
        assert MURALI_HOLES == 4
        assert MURALI_HOLES == QUARTERS

    def test_flute_holes_sum_is_19(self):
        """FLUTE_HOLES_SUM is 19."""
        assert FLUTE_HOLES_SUM == 19
        assert FLUTE_HOLES_SUM == VENU_HOLES + VAMSI_HOLES + MURALI_HOLES

    def test_flute_holes_product_is_216(self):
        """FLUTE_HOLES_PRODUCT is 216."""
        assert FLUTE_HOLES_PRODUCT == 216
        assert FLUTE_HOLES_PRODUCT == VENU_HOLES * VAMSI_HOLES * MURALI_HOLES

    def test_venu_freq_is_72(self):
        """VENU_FREQ is 72."""
        assert VENU_FREQ == 72
        assert VENU_FREQ == JIVA_CYCLE // VENU_HOLES

    def test_vamsi_freq_is_48(self):
        """VAMSI_FREQ is 48."""
        assert VAMSI_FREQ == 48
        assert VAMSI_FREQ == JIVA_CYCLE // VAMSI_HOLES

    def test_murali_freq_is_108(self):
        """MURALI_FREQ is 108."""
        assert MURALI_FREQ == 108
        assert MURALI_FREQ == JIVA_CYCLE // MURALI_HOLES


# =============================================================================
# Acoustic Tests
# =============================================================================


class TestAcoustic:
    """Test acoustic constants."""

    def test_acoustic_ratio_is_18(self):
        """ACOUSTIC_RATIO is 18."""
        assert ACOUSTIC_RATIO == 18
        assert ACOUSTIC_RATIO == GITA_CHAPTERS

    def test_end_correction_is_8(self):
        """END_CORRECTION is 8."""
        assert END_CORRECTION == 8
        assert END_CORRECTION == HARE_COUNT

    def test_cutoff_constant_is_72(self):
        """CUTOFF_CONSTANT is 72."""
        assert CUTOFF_CONSTANT == 72
        assert CUTOFF_CONSTANT == NADI_RESONANCE


# =============================================================================
# The 37 Formula Tests
# =============================================================================


class TestThe37Formula:
    """Test the 37 formula."""

    def test_37_formula(self):
        """KSHETRA + MAHAJANA_COUNT + KSETRAJNA = PARAMPARA."""
        assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == PARAMPARA
        assert 24 + 12 + 1 == 37


# =============================================================================
# Perfect Fifth Chain Tests
# =============================================================================


class TestPerfectFifth:
    """Test perfect fifth chain (3:2 ratio)."""

    def test_murali_venu_fifth(self):
        """Murali:Venu is 3:2."""
        assert MURALI_FREQ * 2 == VENU_FREQ * 3

    def test_venu_vamsi_fifth(self):
        """Venu:Vamsi is 3:2."""
        assert VENU_FREQ * 2 == VAMSI_FREQ * 3


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _seed
        expected = [
            "WORDS",
            "PARAMPARA",
            "TRINITY",
            "QUARTERS",
            "MALA",
            "LILA",
            "COSMIC_FRAME",
            "JIVA_CYCLE",
        ]
        for item in expected:
            assert item in _seed.__all__, f"{item} should be in __all__"
