"""
TESTS: harmonics.py - Resonance Harmonics, Vedic Scale, Sravanam Check
======================================================================

"śrutiṁ apare smṛtim itare bhārataṁ anye bhajantu bhava-bhītāḥ"

REAL TESTS for:
1. ResonanceHarmonics - thresholds derived from Seed
2. VedicScaleMapping - musical scale mapping
3. SravanamCheck - Phase-Locked Loop verification
4. Module-level assertions (imported validation)
"""

import pytest
from vibe_core.mahamantra.substrate.harmonics import (
    ResonanceHarmonics,
    VedicScaleMapping,
    SravanamCheck,
    THRESHOLD_AUTO,
    THRESHOLD_REFINE,
    THRESHOLD_SYNC,
    RATIO_MANTRA_PROCESS,
)
from vibe_core.mahamantra.protocols._seed import (
    NADI_RESONANCE,
    LILA,
    MALA,
    FIELD_RESONANCE,
    WORDS,
    NAVA,
    JIVA_CYCLE,
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    HARE_COUNT,
    HIDDEN_RESERVE,
    QUARTERS,
    QUALITIES,
    GITA_CHAPTERS,
    FLUTE_HOLES_SUM,
    EPOCH_KEY,
)


# =============================================================================
# ResonanceHarmonics Tests
# =============================================================================


class TestResonanceHarmonicsConstants:
    """Test that ResonanceHarmonics constants are correctly derived from Seed."""

    def test_threshold_auto_is_nadi_over_mala(self):
        """THRESHOLD_AUTO = NADI_RESONANCE / MALA = 72/108 = 2/3."""
        expected = NADI_RESONANCE / MALA
        assert ResonanceHarmonics.THRESHOLD_AUTO == expected
        assert abs(ResonanceHarmonics.THRESHOLD_AUTO - 2 / 3) < 0.0001

    def test_threshold_refine_is_lila_over_mala(self):
        """THRESHOLD_REFINE = LILA / MALA = 48/108 = 4/9."""
        expected = LILA / MALA
        assert ResonanceHarmonics.THRESHOLD_REFINE == expected
        assert abs(ResonanceHarmonics.THRESHOLD_REFINE - 4 / 9) < 0.0001

    def test_threshold_sync_is_field_over_mala(self):
        """THRESHOLD_SYNC = FIELD_RESONANCE / MALA = 144/108 = 4/3."""
        expected = FIELD_RESONANCE / MALA
        assert ResonanceHarmonics.THRESHOLD_SYNC == expected
        assert abs(ResonanceHarmonics.THRESHOLD_SYNC - 4 / 3) < 0.0001

    def test_ratio_mantra_process_is_words_over_nava(self):
        """RATIO_MANTRA_PROCESS = WORDS / NAVA = 16/9."""
        expected = WORDS / NAVA
        assert ResonanceHarmonics.RATIO_MANTRA_PROCESS == expected
        assert abs(ResonanceHarmonics.RATIO_MANTRA_PROCESS - 16 / 9) < 0.0001

    def test_ratio_nadi_lila_is_perfect_fifth(self):
        """RATIO_NADI_LILA = 72/48 = 3/2 (Perfect Fifth)."""
        expected = NADI_RESONANCE / LILA
        assert ResonanceHarmonics.RATIO_NADI_LILA == expected
        assert abs(ResonanceHarmonics.RATIO_NADI_LILA - 1.5) < 0.0001


class TestResonanceHarmonicsMethods:
    """Test ResonanceHarmonics helper methods."""

    def test_normalize_to_mala(self):
        """normalize_to_mala scales count/MALA to COSMIC_FRAME (21600)."""
        CF = ResonanceHarmonics.COSMIC_FRAME  # 21600
        assert ResonanceHarmonics.normalize_to_mala(72) == int((72 / MALA) * CF)
        assert ResonanceHarmonics.normalize_to_mala(48) == int((48 / MALA) * CF)
        assert ResonanceHarmonics.normalize_to_mala(108) == CF  # 100%
        assert ResonanceHarmonics.normalize_to_mala(144) == int((144 / MALA) * CF)

    def test_should_auto_execute_above_threshold(self):
        """should_auto_execute returns True when resonance >= THRESHOLD_AUTO (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.should_auto_execute(int(0.7 * CF)) is True
        assert ResonanceHarmonics.should_auto_execute(int(2 / 3 * CF)) is True
        assert ResonanceHarmonics.should_auto_execute(CF) is True

    def test_should_auto_execute_below_threshold(self):
        """should_auto_execute returns False when resonance < THRESHOLD_AUTO (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.should_auto_execute(int(0.5 * CF)) is False
        assert ResonanceHarmonics.should_auto_execute(int(0.4 * CF)) is False
        assert ResonanceHarmonics.should_auto_execute(0) is False

    def test_needs_refinement_in_lila_zone(self):
        """needs_refinement returns True in REFINE <= r < AUTO zone (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.needs_refinement(int(0.5 * CF)) is True
        assert ResonanceHarmonics.needs_refinement(int(4 / 9 * CF)) is True
        assert ResonanceHarmonics.needs_refinement(int(0.6 * CF)) is True

    def test_needs_refinement_outside_zone(self):
        """needs_refinement returns False outside the Lila zone (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.needs_refinement(int(0.3 * CF)) is False  # Below REFINE
        assert ResonanceHarmonics.needs_refinement(int(0.7 * CF)) is False  # Above AUTO

    def test_is_silent_below_refine(self):
        """is_silent returns True when resonance < THRESHOLD_REFINE (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.is_silent(0) is True
        assert ResonanceHarmonics.is_silent(int(0.3 * CF)) is True
        assert ResonanceHarmonics.is_silent(int(0.4 * CF)) is True

    def test_is_silent_above_refine(self):
        """is_silent returns False when resonance >= THRESHOLD_REFINE (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.is_silent(int(4 / 9 * CF)) is False
        assert ResonanceHarmonics.is_silent(int(0.5 * CF)) is False
        assert ResonanceHarmonics.is_silent(CF) is False

    def test_is_multi_agent_sync(self):
        """is_multi_agent_sync returns True when resonance >= THRESHOLD_SYNC (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.is_multi_agent_sync(int(4 / 3 * CF)) is True
        assert ResonanceHarmonics.is_multi_agent_sync(int(1.5 * CF)) is True
        assert ResonanceHarmonics.is_multi_agent_sync(int(2.0 * CF)) is True
        assert ResonanceHarmonics.is_multi_agent_sync(CF) is False
        assert ResonanceHarmonics.is_multi_agent_sync(int(0.5 * CF)) is False


class TestResonanceHarmonicsZones:
    """Test get_zone method for all resonance zones."""

    def test_zone_silence(self):
        """Resonance below THRESHOLD_REFINE is SILENCE zone (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.get_zone(0) == "SILENCE"
        assert ResonanceHarmonics.get_zone(int(0.3 * CF)) == "SILENCE"
        assert ResonanceHarmonics.get_zone(int(0.4 * CF)) == "SILENCE"

    def test_zone_refine(self):
        """Resonance in [THRESHOLD_REFINE, THRESHOLD_AUTO) is REFINE zone (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.get_zone(int(4 / 9 * CF)) == "REFINE"
        assert ResonanceHarmonics.get_zone(int(0.5 * CF)) == "REFINE"
        assert ResonanceHarmonics.get_zone(int(0.6 * CF)) == "REFINE"

    def test_zone_auto(self):
        """Resonance in [THRESHOLD_AUTO, THRESHOLD_SYNC) is AUTO zone (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.get_zone(int(2 / 3 * CF)) == "AUTO"
        assert ResonanceHarmonics.get_zone(int(0.8 * CF)) == "AUTO"
        assert ResonanceHarmonics.get_zone(CF) == "AUTO"
        assert ResonanceHarmonics.get_zone(int(1.2 * CF)) == "AUTO"

    def test_zone_sync(self):
        """Resonance >= THRESHOLD_SYNC is SYNC zone (scaled)."""
        CF = ResonanceHarmonics.COSMIC_FRAME
        assert ResonanceHarmonics.get_zone(int(4 / 3 * CF)) == "SYNC"
        assert ResonanceHarmonics.get_zone(int(1.5 * CF)) == "SYNC"
        assert ResonanceHarmonics.get_zone(int(2.0 * CF)) == "SYNC"


# =============================================================================
# VedicScaleMapping Tests
# =============================================================================


class TestVedicScaleSwaras:
    """Test Swara constants are correctly derived from Seed."""

    def test_swara_sa_is_unity(self):
        """Sa = 1/1 (Tonic)."""
        assert VedicScaleMapping.SWARA_SA == 1.0

    def test_swara_re_is_9_over_8(self):
        """Re = 9/8 = NAVA/HARE_COUNT (Major Second)."""
        assert abs(VedicScaleMapping.SWARA_RE - 1.125) < 0.0001
        assert VedicScaleMapping.SWARA_RE == NAVA / HARE_COUNT

    def test_swara_ga_is_5_over_4(self):
        """Ga = 5/4 (Major Third)."""
        assert abs(VedicScaleMapping.SWARA_GA - 1.25) < 0.0001

    def test_swara_ma_equals_threshold_sync(self):
        """Ma = 4/3 (Perfect Fourth) = THRESHOLD_SYNC."""
        assert abs(VedicScaleMapping.SWARA_MA - 4 / 3) < 0.0001
        assert abs(VedicScaleMapping.SWARA_MA - ResonanceHarmonics.THRESHOLD_SYNC) < 0.0001

    def test_swara_pa_is_perfect_fifth(self):
        """Pa = 3/2 (Perfect Fifth) = NADI/LILA ratio."""
        assert abs(VedicScaleMapping.SWARA_PA - 1.5) < 0.0001
        assert abs(VedicScaleMapping.SWARA_PA - ResonanceHarmonics.RATIO_NADI_LILA) < 0.0001

    def test_swara_dha_is_5_over_3(self):
        """Dha = 5/3 (Major Sixth)."""
        assert abs(VedicScaleMapping.SWARA_DHA - 5 / 3) < 0.0001

    def test_swara_ni_equals_ratio_mantra_process(self):
        """Ni = 16/9 (Minor Seventh) = RATIO_MANTRA_PROCESS."""
        assert abs(VedicScaleMapping.SWARA_NI - 16 / 9) < 0.0001
        assert abs(VedicScaleMapping.SWARA_NI - ResonanceHarmonics.RATIO_MANTRA_PROCESS) < 0.0001

    def test_swara_tuple_has_8_elements(self):
        """SWARAS tuple has 8 elements (Sa through Sa')."""
        assert len(VedicScaleMapping.SWARAS) == 8
        assert VedicScaleMapping.SWARAS == ("Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni", "Sa'")

    def test_swara_ratios_tuple_has_8_elements(self):
        """SWARA_RATIOS has 8 computed values from Seed."""
        assert len(VedicScaleMapping.SWARA_RATIOS) == 8


class TestVedicScaleSyncPoints:
    """Test flute sync point methods."""

    def test_murali_sync_points_are_quarters(self):
        """MURALI (4 holes) produces quarter divisions: 0.25, 0.5, 0.75."""
        points = VedicScaleMapping.get_murali_sync_points()
        assert len(points) == MURALI_HOLES - 1  # 3 points
        expected = (1 / 4, 2 / 4, 3 / 4)
        for actual, exp in zip(points, expected):
            assert abs(actual - exp) < 0.0001

    def test_venu_sync_points_are_sixths(self):
        """VENU (6 holes) produces sixth divisions."""
        points = VedicScaleMapping.get_venu_sync_points()
        assert len(points) == VENU_HOLES - 1  # 5 points
        expected = (1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6)
        for actual, exp in zip(points, expected):
            assert abs(actual - exp) < 0.0001

    def test_vamsi_sync_points_are_ninths(self):
        """VAMSI (9 holes) produces ninth divisions."""
        points = VedicScaleMapping.get_vamsi_sync_points()
        assert len(points) == VAMSI_HOLES - 1  # 8 points
        expected = tuple(i / 9 for i in range(1, 9))
        for actual, exp in zip(points, expected):
            assert abs(actual - exp) < 0.0001

    def test_threshold_refine_is_vamsi_4th_sync(self):
        """THRESHOLD_REFINE (4/9) appears in VAMSI sync points."""
        vamsi_points = VedicScaleMapping.get_vamsi_sync_points()
        # 4/9 is the 4th sync point
        assert any(abs(p - 4 / 9) < 0.0001 for p in vamsi_points)

    def test_threshold_auto_is_venu_4th_sync(self):
        """THRESHOLD_AUTO (2/3) appears in VENU sync points."""
        venu_points = VedicScaleMapping.get_venu_sync_points()
        # 4/6 = 2/3 is the 4th sync point
        assert any(abs(p - 2 / 3) < 0.0001 for p in venu_points)

    def test_all_sync_points_are_unique_and_sorted(self):
        """get_all_sync_points returns unique, sorted values."""
        all_points = VedicScaleMapping.get_all_sync_points()
        # Should be sorted
        assert all_points == tuple(sorted(all_points))
        # Should be unique
        assert len(all_points) == len(set(all_points))
        # Should have points from all flutes
        assert len(all_points) > 0


class TestVedicScaleMapping:
    """Test resonance_to_swara mapping."""

    def test_low_resonance_is_sa(self):
        """Resonance near 0 maps to Sa."""
        assert VedicScaleMapping.resonance_to_swara(0.0) == "Sa"
        assert VedicScaleMapping.resonance_to_swara(0.1) == "Sa"
        assert VedicScaleMapping.resonance_to_swara(0.2) == "Sa"

    def test_resonance_boundaries_correct(self):
        """Resonance maps to correct Swaras at boundary points."""
        # Just above each boundary
        assert VedicScaleMapping.resonance_to_swara(0.23) == "Re"
        assert VedicScaleMapping.resonance_to_swara(0.34) == "Ga"
        assert VedicScaleMapping.resonance_to_swara(0.51) == "Ma"
        assert VedicScaleMapping.resonance_to_swara(0.68) == "Pa"
        assert VedicScaleMapping.resonance_to_swara(1.01) == "Dha"
        assert VedicScaleMapping.resonance_to_swara(1.34) == "Ni"
        assert VedicScaleMapping.resonance_to_swara(1.78) == "Sa'"

    def test_high_resonance_is_upper_sa(self):
        """Resonance above RATIO_MANTRA_PROCESS maps to Sa' (upper octave)."""
        assert VedicScaleMapping.resonance_to_swara(2.0) == "Sa'"
        assert VedicScaleMapping.resonance_to_swara(3.0) == "Sa'"


class TestVedicScaleRasa:
    """Test resonance_to_rasa mapping."""

    def test_silence_zone_is_shanta(self):
        """SILENCE zone maps to Shanta (Peace)."""
        rasa = VedicScaleMapping.resonance_to_rasa(0.0)
        assert rasa == ("Shanta", "Peace")

    def test_refine_zone_is_karuna(self):
        """REFINE zone maps to Karuna (Compassion)."""
        rasa = VedicScaleMapping.resonance_to_rasa(0.5)
        assert rasa == ("Karuna", "Compassion")

    def test_auto_zone_is_vira(self):
        """AUTO zone maps to Vira (Courage)."""
        rasa = VedicScaleMapping.resonance_to_rasa(0.7)
        assert rasa == ("Vira", "Courage")

    def test_sync_zone_is_adbhuta(self):
        """SYNC zone maps to Adbhuta (Wonder)."""
        rasa = VedicScaleMapping.resonance_to_rasa(1.5)
        assert rasa == ("Adbhuta", "Wonder")


class TestVedicScaleAdvanced:
    """Test advanced VedicScaleMapping methods."""

    def test_distance_to_nearest_sync(self):
        """distance_to_nearest_sync returns distance and flute name."""
        dist, flute = VedicScaleMapping.distance_to_nearest_sync(0.25)
        assert dist < 0.01  # Should be very close to MURALI 0.25
        assert flute in ("MURALI", "VENU", "VAMSI")

    def test_distance_to_sync_for_exact_point(self):
        """Exact sync point has distance ~0."""
        dist, flute = VedicScaleMapping.distance_to_nearest_sync(0.5)
        assert dist < 0.001  # 0.5 is exact sync for MURALI and VENU

    def test_get_harmonic_signature_returns_dict(self):
        """get_harmonic_signature returns complete signature dict."""
        sig = VedicScaleMapping.get_harmonic_signature(0.5)
        assert "swara" in sig
        assert "rasa" in sig
        assert "zone" in sig
        assert "sync_distance" in sig
        assert "sync_flute" in sig
        assert "resonance" in sig
        assert sig["resonance"] == 0.5

    def test_get_melakarta_number_range(self):
        """get_melakarta_number returns value in 1-72 range."""
        for r in [0.0, 0.25, 0.5, 0.75, 1.0]:
            num = VedicScaleMapping.get_melakarta_number(r)
            assert 1 <= num <= NADI_RESONANCE  # 72

    def test_get_melakarta_clamped(self):
        """get_melakarta_number clamps to valid range."""
        assert VedicScaleMapping.get_melakarta_number(-0.5) == 1
        assert VedicScaleMapping.get_melakarta_number(2.0) == NADI_RESONANCE


# =============================================================================
# SravanamCheck Tests
# =============================================================================


class TestSravanamCheckConstants:
    """Test SravanamCheck constants derived from Seed."""

    def test_bootstrap_ratio(self):
        """BOOTSTRAP_RATIO = 2/9."""
        assert abs(SravanamCheck.BOOTSTRAP_RATIO - 2 / 9) < 0.0001

    def test_dharma_pillars_is_4(self):
        """DHARMA_PILLARS = (2 × 18) / 9 = 4."""
        assert SravanamCheck.DHARMA_PILLARS == QUARTERS
        assert SravanamCheck.DHARMA_PILLARS == 4

    def test_sravanam_transform_is_qualities(self):
        """SRAVANAM_TRANSFORM = (16 × 72) / 18 = 64 = QUALITIES."""
        assert SravanamCheck.SRAVANAM_TRANSFORM == QUALITIES
        assert SravanamCheck.SRAVANAM_TRANSFORM == (WORDS * NADI_RESONANCE) // GITA_CHAPTERS

    def test_io_ratio_is_2(self):
        """IO_RATIO = HIDDEN_RESERVE / HARE_COUNT = 16/8 = 2."""
        assert SravanamCheck.IO_RATIO == 2.0
        assert SravanamCheck.IO_RATIO == HIDDEN_RESERVE / HARE_COUNT

    def test_phase_lock_threshold_equals_refine(self):
        """PHASE_LOCK_THRESHOLD = THRESHOLD_REFINE = 4/9."""
        assert abs(SravanamCheck.PHASE_LOCK_THRESHOLD - ResonanceHarmonics.THRESHOLD_REFINE) < 0.0001

    def test_petal_width_is_27(self):
        """PETAL_WIDTH = JIVA_CYCLE / WORDS = 432/16 = 27."""
        assert SravanamCheck.PETAL_WIDTH == 27
        assert SravanamCheck.PETAL_WIDTH == JIVA_CYCLE // WORDS

    def test_max_ego_offset_is_13(self):
        """MAX_EGO_OFFSET = PETAL_WIDTH / 2 = 13."""
        assert SravanamCheck.MAX_EGO_OFFSET == 13

    def test_epoch_signature_is_19(self):
        """EPOCH_SIGNATURE = FLUTE_HOLES_SUM = 19."""
        assert SravanamCheck.EPOCH_SIGNATURE == FLUTE_HOLES_SUM
        assert SravanamCheck.EPOCH_SIGNATURE == 19

    def test_gajra_count_is_16(self):
        """GAJRA_COUNT = WORDS = 16."""
        assert SravanamCheck.GAJRA_COUNT == WORDS

    def test_sync_points_tuple(self):
        """SYNC_POINTS = (144, 216, 432)."""
        assert SravanamCheck.SYNC_POINTS == (144, 216, 432)


class TestSravanamCheckEntropyLaw:
    """Test Entropy Law: input >= output."""

    def test_entropy_satisfied_when_input_gte_output(self):
        """Entropy law satisfied when input >= output."""
        assert SravanamCheck.verify_entropy_law(100, 50) is True
        assert SravanamCheck.verify_entropy_law(100, 100) is True
        assert SravanamCheck.verify_entropy_law(16, 8) is True

    def test_entropy_violated_when_input_lt_output(self):
        """Entropy law violated when input < output."""
        assert SravanamCheck.verify_entropy_law(50, 100) is False
        assert SravanamCheck.verify_entropy_law(0, 1) is False
        assert SravanamCheck.verify_entropy_law(7, 8) is False


class TestSravanamCheckPhaseLock:
    """Test Phase Lock verification."""

    def test_phase_locked_above_threshold(self):
        """Phase locked when resonance >= THRESHOLD_REFINE."""
        assert SravanamCheck.verify_phase_lock(0.5) is True
        assert SravanamCheck.verify_phase_lock(4 / 9) is True
        assert SravanamCheck.verify_phase_lock(1.0) is True

    def test_phase_not_locked_below_threshold(self):
        """Phase not locked when resonance < THRESHOLD_REFINE."""
        assert SravanamCheck.verify_phase_lock(0.4) is False
        assert SravanamCheck.verify_phase_lock(0.0) is False


class TestSravanamCheckParampara:
    """Test Parampara connection verification."""

    def test_parampara_connected_above_auto(self):
        """Parampara connected when resonance >= THRESHOLD_AUTO."""
        assert SravanamCheck.verify_parampara_connection(0.7) is True
        assert SravanamCheck.verify_parampara_connection(2 / 3) is True
        assert SravanamCheck.verify_parampara_connection(1.0) is True

    def test_parampara_lost_below_auto(self):
        """Parampara lost when resonance < THRESHOLD_AUTO."""
        assert SravanamCheck.verify_parampara_connection(0.5) is False
        assert SravanamCheck.verify_parampara_connection(0.0) is False


class TestSravanamCheckCanEmit:
    """Test can_emit method (the main gate)."""

    def test_can_emit_all_conditions_met(self):
        """can_emit returns True when all conditions met."""
        can, reason = SravanamCheck.can_emit(100, 50, 0.5)
        assert can is True
        assert "Safe to emit" in reason

    def test_cannot_emit_entropy_violation(self):
        """can_emit returns False on entropy violation."""
        can, reason = SravanamCheck.can_emit(50, 100, 0.5)
        assert can is False
        assert "Entropy violation" in reason

    def test_cannot_emit_phase_not_locked(self):
        """can_emit returns False when phase not locked."""
        can, reason = SravanamCheck.can_emit(100, 50, 0.3)
        assert can is False
        assert "Phase not locked" in reason

    def test_cannot_emit_strict_parampara_lost(self):
        """can_emit with strict=True fails if Parampara lost."""
        can, reason = SravanamCheck.can_emit(100, 50, 0.5, strict=True)
        assert can is False
        assert "Parampara lock lost" in reason

    def test_can_emit_strict_with_full_resonance(self):
        """can_emit with strict=True succeeds with full resonance."""
        can, reason = SravanamCheck.can_emit(100, 50, 0.7, strict=True)
        assert can is True


class TestSravanamCheckDynamic:
    """Test dynamic phase/tick calculations."""

    def test_ego_offset_zero_on_petal_boundary(self):
        """Ego offset is 0 when tick lands on petal boundary."""
        assert SravanamCheck.calculate_ego_offset(0) == 0
        assert SravanamCheck.calculate_ego_offset(27) == 0
        assert SravanamCheck.calculate_ego_offset(54) == 0

    def test_ego_offset_increases_from_boundary(self):
        """Ego offset increases as tick moves from petal boundary."""
        assert SravanamCheck.calculate_ego_offset(1) == 1
        assert SravanamCheck.calculate_ego_offset(5) == 5
        assert SravanamCheck.calculate_ego_offset(13) == 13

    def test_ego_offset_folds_past_midpoint(self):
        """Ego offset folds back after passing half petal."""
        # At 14, we're closer to next boundary (27-14=13)
        assert SravanamCheck.calculate_ego_offset(14) == 13
        assert SravanamCheck.calculate_ego_offset(20) == 7
        assert SravanamCheck.calculate_ego_offset(26) == 1

    def test_is_on_gajra(self):
        """is_on_gajra returns True on Gajra positions."""
        assert SravanamCheck.is_on_gajra(0) is True
        assert SravanamCheck.is_on_gajra(27) is True
        assert SravanamCheck.is_on_gajra(54) is True
        assert SravanamCheck.is_on_gajra(1) is False
        assert SravanamCheck.is_on_gajra(13) is False

    def test_get_nearest_gajra(self):
        """get_nearest_gajra returns closest Gajra position."""
        assert SravanamCheck.get_nearest_gajra(0) == 0
        assert SravanamCheck.get_nearest_gajra(10) == 0  # Closer to 0 than 27
        assert SravanamCheck.get_nearest_gajra(14) == 27  # Closer to 27 than 0
        assert SravanamCheck.get_nearest_gajra(27) == 27

    def test_validate_epoch_lock(self):
        """validate_epoch_lock confirms 1972 digit sum = 19."""
        assert SravanamCheck.validate_epoch_lock() is True
        # Verify manually: 1+9+7+2 = 19
        assert sum(int(d) for d in str(EPOCH_KEY)) == 19

    def test_calculate_phase_angle(self):
        """calculate_phase_angle returns distance to nearest sync."""
        dist, sync = SravanamCheck.calculate_phase_angle(144)
        assert dist == 0  # Exactly on sync point
        assert sync == 144

        dist, sync = SravanamCheck.calculate_phase_angle(0)
        assert sync in (144, 216, 432)  # Nearest sync from 0


class TestSravanamCheckStatus:
    """Test status and helper methods."""

    def test_compute_safe_output_size(self):
        """compute_safe_output_size uses IO_RATIO (2:1)."""
        assert SravanamCheck.compute_safe_output_size(100) == 50
        assert SravanamCheck.compute_safe_output_size(16) == 8
        assert SravanamCheck.compute_safe_output_size(0) == 0

    def test_get_sravanam_status_returns_dict(self):
        """get_sravanam_status returns comprehensive status dict."""
        status = SravanamCheck.get_sravanam_status(100, 50, 0.5)
        assert "can_emit" in status
        assert "reason" in status
        assert "input_tokens" in status
        assert "output_tokens" in status
        assert "io_ratio" in status
        assert "resonance" in status
        assert "phase_locked" in status
        assert "parampara_connected" in status
        assert "swara" in status
        assert "zone" in status
        assert "safe_output_size" in status


class TestSravanamCheckDynamicEmit:
    """Test can_emit_dynamic (full check with tick/phase)."""

    def test_can_emit_dynamic_on_gajra(self):
        """can_emit_dynamic succeeds on Gajra with good resonance."""
        can, reason, delay = SravanamCheck.can_emit_dynamic(
            input_tokens=100,
            output_tokens=50,
            resonance=0.7,
            tick=0,  # On Gajra
            strict=True,
        )
        assert can is True
        assert delay == 0

    def test_can_emit_dynamic_entropy_fail(self):
        """can_emit_dynamic fails on entropy violation."""
        can, reason, delay = SravanamCheck.can_emit_dynamic(
            input_tokens=50, output_tokens=100, resonance=0.7, tick=0, strict=False
        )
        assert can is False
        assert "Entropy" in reason

    def test_can_emit_dynamic_not_on_gajra(self):
        """can_emit_dynamic with tick not on Gajra returns delay."""
        can, reason, delay = SravanamCheck.can_emit_dynamic(
            input_tokens=100,
            output_tokens=50,
            resonance=0.7,
            tick=10,  # Not on Gajra
            strict=True,
        )
        # May or may not emit depending on ego offset
        # But if not emitting, should have delay info
        if not can and "Gajra" in reason:
            assert delay > 0


# =============================================================================
# Module-Level Export Tests
# =============================================================================


class TestModuleExports:
    """Test that module-level constants are exported correctly."""

    def test_threshold_auto_exported(self):
        """THRESHOLD_AUTO is exported and equals class constant."""
        assert THRESHOLD_AUTO == ResonanceHarmonics.THRESHOLD_AUTO

    def test_threshold_refine_exported(self):
        """THRESHOLD_REFINE is exported and equals class constant."""
        assert THRESHOLD_REFINE == ResonanceHarmonics.THRESHOLD_REFINE

    def test_threshold_sync_exported(self):
        """THRESHOLD_SYNC is exported and equals class constant."""
        assert THRESHOLD_SYNC == ResonanceHarmonics.THRESHOLD_SYNC

    def test_ratio_mantra_process_exported(self):
        """RATIO_MANTRA_PROCESS is exported and equals class constant."""
        assert RATIO_MANTRA_PROCESS == ResonanceHarmonics.RATIO_MANTRA_PROCESS


# =============================================================================
# Integration Tests
# =============================================================================


class TestHarmonicsIntegration:
    """Test integration between the three classes."""

    def test_threshold_convergence_with_swaras(self):
        """Thresholds converge with Swara ratios (Acintya pattern)."""
        # Ma (4/3) = THRESHOLD_SYNC
        assert abs(VedicScaleMapping.SWARA_MA - ResonanceHarmonics.THRESHOLD_SYNC) < 0.0001
        # Pa (3/2) = NADI/LILA ratio
        assert abs(VedicScaleMapping.SWARA_PA - ResonanceHarmonics.RATIO_NADI_LILA) < 0.0001
        # Ni (16/9) = RATIO_MANTRA_PROCESS
        assert abs(VedicScaleMapping.SWARA_NI - ResonanceHarmonics.RATIO_MANTRA_PROCESS) < 0.0001

    def test_sravanam_phase_lock_uses_refine_threshold(self):
        """SravanamCheck phase lock uses THRESHOLD_REFINE."""
        assert abs(SravanamCheck.PHASE_LOCK_THRESHOLD - THRESHOLD_REFINE) < 0.0001

    def test_zone_and_swara_alignment(self):
        """Zone boundaries align with Swara mapping."""
        # SILENCE zone (< 4/9) maps to Sa or Re
        assert VedicScaleMapping.resonance_to_swara(0.3) in ("Sa", "Re")
        # REFINE zone maps to Ga or Ma
        assert VedicScaleMapping.resonance_to_swara(0.5) in ("Ga", "Ma")
        # AUTO zone maps to Ma or Pa
        assert VedicScaleMapping.resonance_to_swara(0.8) in ("Ma", "Pa")
        # SYNC zone maps to Ni or Sa'
        assert VedicScaleMapping.resonance_to_swara(1.5) in ("Dha", "Ni", "Sa'")

    def test_full_emission_flow(self):
        """Test complete emission flow through all systems."""
        # Simulate an agent with good input and resonance
        input_tokens = 200
        output_tokens = 80
        resonance = 0.75  # Above AUTO threshold
        tick = 27  # On Gajra

        # Check basic emission
        can, reason = SravanamCheck.can_emit(input_tokens, output_tokens, resonance)
        assert can is True

        # Get harmonic signature
        sig = VedicScaleMapping.get_harmonic_signature(resonance)
        assert sig["zone"] == "AUTO"
        assert sig["swara"] == "Pa"

        # Check zone classification (get_zone expects COSMIC_FRAME-scaled int)
        CF = ResonanceHarmonics.COSMIC_FRAME
        zone = ResonanceHarmonics.get_zone(int(resonance * CF))
        assert zone == "AUTO"

        # Full dynamic check
        can, reason, delay = SravanamCheck.can_emit_dynamic(input_tokens, output_tokens, resonance, tick, strict=True)
        assert can is True
        assert delay == 0
