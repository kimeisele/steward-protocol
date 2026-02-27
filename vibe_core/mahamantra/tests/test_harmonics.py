"""
HARMONICS — Resonance Threshold & Vedic Scale Tests
=====================================================

Tests the three core classes:
- ResonanceHarmonics: COSMIC_FRAME-scaled thresholds
- VedicScaleMapping: Swara/Raga mapping
- SravanamCheck: Phase-locked loop verification
"""

import pytest

from vibe_core.mahamantra.substrate.encoding.harmonics import (
    CF_AUTO,
    CF_REFINE,
    CF_SYNC,
    THRESHOLD_AUTO,
    THRESHOLD_REFINE,
    THRESHOLD_SYNC,
    RATIO_MANTRA_PROCESS,
    ResonanceHarmonics,
    SravanamCheck,
    VedicScaleMapping,
)


# ============================================================================
# ResonanceHarmonics
# ============================================================================


class TestResonanceHarmonics:
    """COSMIC_FRAME-scaled thresholds derived from seed constants."""

    def test_cosmic_frame(self):
        assert ResonanceHarmonics.COSMIC_FRAME == 21600

    def test_threshold_values(self):
        """Thresholds are specific fractions of COSMIC_FRAME."""
        assert CF_AUTO == 14400    # 2/3 × 21600
        assert CF_REFINE == 9600   # 4/9 × 21600
        assert CF_SYNC == 28800    # 4/3 × 21600

    def test_float_thresholds_match_integer(self):
        """Float aliases must be CF / COSMIC_FRAME."""
        cf = ResonanceHarmonics.COSMIC_FRAME
        assert abs(THRESHOLD_AUTO - CF_AUTO / cf) < 1e-10
        assert abs(THRESHOLD_REFINE - CF_REFINE / cf) < 1e-10
        assert abs(THRESHOLD_SYNC - CF_SYNC / cf) < 1e-10

    def test_threshold_ordering(self):
        """REFINE < AUTO < SYNC — silence → refine → auto → sync."""
        assert CF_REFINE < CF_AUTO < CF_SYNC
        assert THRESHOLD_REFINE < THRESHOLD_AUTO < THRESHOLD_SYNC

    def test_zone_classification(self):
        rh = ResonanceHarmonics()
        assert rh.get_zone(0) == "SILENCE"
        assert rh.get_zone(CF_REFINE) == "REFINE"
        assert rh.get_zone(CF_AUTO) == "AUTO"
        assert rh.get_zone(CF_SYNC) == "SYNC"

    def test_zone_boundaries(self):
        rh = ResonanceHarmonics()
        # Just below thresholds
        assert rh.is_silent(CF_REFINE - 1)
        assert not rh.is_silent(CF_REFINE)
        assert rh.needs_refinement(CF_REFINE)
        assert not rh.needs_refinement(CF_AUTO)
        assert rh.should_auto_execute(CF_AUTO)
        assert not rh.should_auto_execute(CF_AUTO - 1)

    def test_normalize_to_mala(self):
        rh = ResonanceHarmonics()
        # 108 (MALA) should normalize to COSMIC_FRAME
        result = rh.normalize_to_mala(108)
        assert result == 21600
        # 0 should normalize to 0
        assert rh.normalize_to_mala(0) == 0


# ============================================================================
# VedicScaleMapping
# ============================================================================


class TestVedicScaleMapping:
    """Vedic musical scale: 7 Swaras + octave."""

    def test_swara_count(self):
        vsm = VedicScaleMapping()
        assert len(vsm.SWARAS) == 8  # Sa Re Ga Ma Pa Dha Ni Sa'
        assert len(vsm.SWARA_RATIOS) == 8

    def test_tonic(self):
        vsm = VedicScaleMapping()
        assert vsm.SWARA_SA == 1.0
        assert vsm.SWARAS[0] == "Sa"

    def test_perfect_fifth(self):
        """Pa = 3/2 — the perfect fifth."""
        vsm = VedicScaleMapping()
        assert vsm.SWARA_PA == 1.5

    def test_perfect_fourth(self):
        """Ma = 4/3 — the perfect fourth = THRESHOLD_SYNC."""
        vsm = VedicScaleMapping()
        assert abs(vsm.SWARA_MA - 4 / 3) < 1e-10

    def test_resonance_to_swara(self):
        vsm = VedicScaleMapping()
        # Various resonances should map to valid Swaras
        swara = vsm.resonance_to_swara(0.1)
        assert swara in vsm.SWARAS

    def test_sync_points(self):
        """Sync points are INNER division points between holes.
        Murali=4 holes, Venu=6 holes, Vamsi=9 holes (Shastra facts).
        N holes → N-1 inner division points (0 and 1.0 are boundaries)."""
        vsm = VedicScaleMapping()
        murali = vsm.get_murali_sync_points()
        venu = vsm.get_venu_sync_points()
        vamsi = vsm.get_vamsi_sync_points()
        assert len(murali) == 4 - 1  # 4 holes → 3 inner divisions
        assert len(venu) == 6 - 1    # 6 holes → 5 inner divisions
        assert len(vamsi) == 9 - 1   # 9 holes → 8 inner divisions

    def test_harmonic_signature(self):
        vsm = VedicScaleMapping()
        sig = vsm.get_harmonic_signature(0.5)
        assert "swara" in sig
        assert "zone" in sig
        assert "resonance" in sig
        assert sig["resonance"] == 0.5

    def test_melakarta_range(self):
        """Melakarta Ragas are numbered 1-72."""
        vsm = VedicScaleMapping()
        for res in [0.0, 0.5, 1.0, 1.5]:
            n = vsm.get_melakarta_number(res)
            assert 1 <= n <= 72


# ============================================================================
# SravanamCheck
# ============================================================================


class TestSravanamCheck:
    """Phase-locked loop verification before output emission."""

    def test_entropy_law(self):
        """Input must be >= Output (IO_RATIO = 2.0)."""
        sc = SravanamCheck()
        assert sc.verify_entropy_law(100, 50) is True
        assert sc.verify_entropy_law(100, 100) is True
        assert sc.verify_entropy_law(50, 100) is False

    def test_phase_lock(self):
        sc = SravanamCheck()
        # Above PHASE_LOCK_THRESHOLD (≈0.444) = locked
        assert sc.verify_phase_lock(0.5) is True
        # Below = not locked
        assert sc.verify_phase_lock(0.1) is False

    def test_can_emit_basic(self):
        sc = SravanamCheck()
        # Good: high resonance, input > output
        ok, msg = sc.can_emit(100, 30, 0.7)
        assert ok is True
        # Bad: output > input
        fail, msg = sc.can_emit(10, 100, 0.7)
        assert fail is False

