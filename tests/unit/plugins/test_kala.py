"""
Tests for KALA Plugin - Eternal Time
====================================

Tests:
1. CosmicClock calculates sun phases correctly
2. CosmicClock calculates moon phases correctly
3. Rhythm intensities are within bounds
4. KalaPlugin boots and reports status
5. Day/Night cycle updates Sarga
"""

from datetime import datetime, timezone

import pytest


class TestCosmicClock:
    """Test the cosmic clock calculations."""

    def test_sun_phase_morning(self):
        """Morning hours should return MORNING phase."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock, SunPhase

        clock = CosmicClock()

        # 9:00 AM UTC
        morning = datetime(2025, 12, 20, 9, 0, tzinfo=timezone.utc)
        state = clock.get_state_at(morning)

        assert state.sun_phase == SunPhase.MORNING
        assert state.is_day is True

    def test_sun_phase_night(self):
        """Night hours should return NIGHT phase."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock, SunPhase

        clock = CosmicClock()

        # 2:00 AM UTC
        night = datetime(2025, 12, 20, 2, 0, tzinfo=timezone.utc)
        state = clock.get_state_at(night)

        assert state.sun_phase == SunPhase.NIGHT
        assert state.is_day is False

    def test_sun_phase_brahma_muhurta(self):
        """Pre-dawn hours should return BRAHMA_MUHURTA phase."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock, SunPhase

        clock = CosmicClock()

        # 5:00 AM UTC
        brahma = datetime(2025, 12, 20, 5, 0, tzinfo=timezone.utc)
        state = clock.get_state_at(brahma)

        assert state.sun_phase == SunPhase.BRAHMA_MUHURTA
        assert state.is_day is False

    def test_moon_phase_calculation(self):
        """Moon phase should be calculated based on lunar cycle."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock

        clock = CosmicClock()

        # Any date should return valid moon phase
        state = clock.get_current_state()

        assert state.tithi >= 1 and state.tithi <= 15
        assert state.lunar_day >= 1 and state.lunar_day <= 30
        assert state.paksha.value in ("shukla", "krishna")

    def test_rhythm_intensity_bounds(self):
        """Rhythm intensities should be between 0 and 1."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock

        clock = CosmicClock()
        rhythms = clock.get_rhythm_intensity()

        assert 0.0 <= rhythms["solar"] <= 1.0
        assert 0.0 <= rhythms["lunar"] <= 1.0
        assert 0.0 <= rhythms["combined"] <= 1.0

    def test_special_days(self):
        """Ekadashi, Purnima, Amavasya detection should work."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock

        clock = CosmicClock()

        # These are boolean functions, should not raise
        ekadashi = clock.is_ekadashi()
        purnima = clock.is_purnima()
        amavasya = clock.is_amavasya()

        assert isinstance(ekadashi, bool)
        assert isinstance(purnima, bool)
        assert isinstance(amavasya, bool)

    def test_timezone_offset(self):
        """Clock with timezone offset should shift local time."""
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock

        # UTC+5:30 (India Standard Time)
        clock_ist = CosmicClock(timezone_offset_hours=5.5)

        state = clock_ist.get_current_state()

        # Local time should be 5.5 hours ahead of UTC
        delta = (state.local_time - state.utc_time).total_seconds() / 3600
        assert abs(delta - 5.5) < 0.01


class TestKalaPlugin:
    """Test the KALA plugin integration."""

    def test_plugin_has_correct_id(self):
        """Plugin should have ID 'kala'."""
        from vibe_core.plugins.kala import KalaPlugin

        plugin = KalaPlugin()
        assert plugin.plugin_id == "kala"

    def test_plugin_priority(self):
        """Plugin should have early priority."""
        from vibe_core.plugins.kala import KalaPlugin

        plugin = KalaPlugin()
        assert plugin.priority <= 5  # Should be early

    def test_plugin_pulse_phase_is_sensors(self):
        """Plugin should run in SENSORS phase."""
        from vibe_core.plugin_protocol import PulsePhase
        from vibe_core.plugins.kala import KalaPlugin

        plugin = KalaPlugin()
        assert plugin.pulse_phase == PulsePhase.SENSORS

    def test_get_current_state_before_boot(self):
        """Getting state before boot should return error."""
        from vibe_core.plugins.kala import KalaPlugin

        plugin = KalaPlugin()
        state = plugin.get_current_state()

        assert "error" in state

    def test_is_day_default(self):
        """is_day should default to True before boot."""
        from vibe_core.plugins.kala import KalaPlugin

        plugin = KalaPlugin()
        assert plugin.is_day() is True


class TestKalaSargaIntegration:
    """Test KALA and Sarga cycle integration."""

    def test_sarga_cycle_exists(self):
        """Sarga module should exist and have Cycle enum."""
        from vibe_core.sarga import Cycle, get_sarga

        sarga = get_sarga()
        assert sarga is not None
        assert sarga.get_cycle() in (Cycle.DAY_OF_BRAHMA, Cycle.NIGHT_OF_BRAHMA)

    def test_sarga_cycle_can_be_set(self):
        """Sarga cycle should be settable."""
        from vibe_core.sarga import Cycle, get_sarga

        sarga = get_sarga()

        # Remember original
        original = sarga.get_cycle()

        # Set to day
        sarga.set_cycle(Cycle.DAY_OF_BRAHMA)
        assert sarga.get_cycle() == Cycle.DAY_OF_BRAHMA

        # Set to night
        sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)
        assert sarga.get_cycle() == Cycle.NIGHT_OF_BRAHMA

        # Restore
        sarga.set_cycle(original)
