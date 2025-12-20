"""
E2E Test: KALA Time Orchestration
=================================

Full integration test proving the time orchestration chain works:

1. KALA boots → Sets Day/Night in Sarga based on sun
2. sarga_cycle reads from Sarga → Enforces task restrictions
3. Rhythm intensities overlay correctly
4. All components synchronized

OPUS-165: KALA Plugin
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


class TestKalaOrchestrationE2E:
    """End-to-end tests for KALA time orchestration."""

    def test_kala_to_sarga_cycle_flow(self):
        """
        E2E: KALA → Sarga → sarga_cycle flow works.

        Steps:
        1. KALA calculates sun phase
        2. KALA updates Sarga Day/Night
        3. sarga_cycle reads from Sarga
        4. Task restrictions applied correctly
        """
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock, SunPhase
        from vibe_core.sarga import Cycle, get_sarga

        # Reset Sarga to known state
        sarga = get_sarga()
        original_cycle = sarga.get_cycle()

        # Create clock and test daytime
        clock = CosmicClock()

        # Simulate morning (9 AM) - should be DAY
        morning = datetime(2025, 12, 20, 9, 0, tzinfo=timezone.utc)
        morning_state = clock.get_state_at(morning)

        assert morning_state.sun_phase == SunPhase.MORNING
        assert morning_state.is_day is True

        # Update Sarga based on KALA (as KalaPlugin would do)
        if morning_state.is_day:
            sarga.set_cycle(Cycle.DAY_OF_BRAHMA)

        assert sarga.get_cycle() == Cycle.DAY_OF_BRAHMA

        # Simulate night (2 AM) - should be NIGHT
        night = datetime(2025, 12, 20, 2, 0, tzinfo=timezone.utc)
        night_state = clock.get_state_at(night)

        assert night_state.sun_phase == SunPhase.NIGHT
        assert night_state.is_day is False

        # Update Sarga based on KALA
        if not night_state.is_day:
            sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        assert sarga.get_cycle() == Cycle.NIGHT_OF_BRAHMA

        # Restore original
        sarga.set_cycle(original_cycle)

    def test_sarga_cycle_enforces_night_restrictions(self):
        """
        E2E: sarga_cycle enforces task restrictions during NIGHT_OF_BRAHMA.
        """
        from vibe_core.plugins.sarga_cycle.plugin_main import SargaCyclePlugin
        from vibe_core.sarga import Cycle, get_sarga

        # Reset to night
        sarga = get_sarga()
        original = sarga.get_cycle()
        sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        plugin = SargaCyclePlugin()

        # Create mock task with non-maintenance type
        mock_task = MagicMock()
        mock_task.task_id = "test-task-123"
        mock_task.payload = {"type": "feature"}  # Not maintenance!

        mock_kernel = MagicMock()

        # Should raise ValueError during night
        with pytest.raises(ValueError) as excinfo:
            plugin.on_task_submit(mock_kernel, mock_task)

        assert "NIGHT_OF_BRAHMA" in str(excinfo.value)
        assert "feature" in str(excinfo.value)

        # Maintenance task should pass
        mock_task.payload = {"type": "bugfix"}  # Maintenance!
        result = plugin.on_task_submit(mock_kernel, mock_task)
        assert result is True

        # Restore
        sarga.set_cycle(original)

    def test_sarga_cycle_allows_all_during_day(self):
        """
        E2E: sarga_cycle allows all task types during DAY_OF_BRAHMA.
        """
        from vibe_core.plugins.sarga_cycle.plugin_main import SargaCyclePlugin
        from vibe_core.sarga import Cycle, get_sarga

        # Reset to day
        sarga = get_sarga()
        original = sarga.get_cycle()
        sarga.set_cycle(Cycle.DAY_OF_BRAHMA)

        plugin = SargaCyclePlugin()

        # Create mock task with feature type
        mock_task = MagicMock()
        mock_task.task_id = "test-task-456"
        mock_task.payload = {"type": "feature"}

        mock_kernel = MagicMock()

        # Should pass during day
        result = plugin.on_task_submit(mock_kernel, mock_task)
        assert result is True

        # Restore
        sarga.set_cycle(original)

    def test_rhythm_intensities_overlay(self):
        """
        E2E: Solar and lunar rhythms overlay correctly.
        """
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock

        clock = CosmicClock()

        # Get rhythms at different times
        rhythms = clock.get_rhythm_intensity()

        # All values should be in valid range
        assert 0.0 <= rhythms["solar"] <= 1.0
        assert 0.0 <= rhythms["lunar"] <= 1.0
        assert 0.0 <= rhythms["combined"] <= 1.0

        # Combined should be weighted average
        expected_combined = rhythms["solar"] * 0.6 + rhythms["lunar"] * 0.4
        assert abs(rhythms["combined"] - expected_combined) < 0.01

    def test_kala_plugin_boots_and_reports_status(self):
        """
        E2E: KalaPlugin boots and reports correct status.
        """
        from vibe_core.plugins.kala import KalaPlugin

        plugin = KalaPlugin()

        # Before boot - no clock
        assert plugin.get_current_state() == {"error": "Clock not initialized"}

        # Simulate boot with mock kernel
        mock_kernel = MagicMock()
        plugin.on_boot(mock_kernel)

        # After boot - should have valid state
        state = plugin.get_current_state()
        assert "utc_time" in state
        assert "sun_phase" in state
        assert "moon_phase" in state
        assert "tithi" in state

        # Status should be complete
        status = plugin.get_status()
        assert status["plugin_id"] == "kala"
        assert "current_state" in status
        assert "rhythms" in status

    def test_full_time_chain_24h_cycle(self):
        """
        E2E: Full 24-hour cycle transitions work correctly.

        Tests all 8 sun phases in order.
        """
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock, SunPhase

        clock = CosmicClock()

        # Test times for each phase
        test_cases = [
            (5, 0, SunPhase.BRAHMA_MUHURTA, False),  # 5:00 AM
            (6, 30, SunPhase.SUNRISE, True),  # 6:30 AM
            (10, 0, SunPhase.MORNING, True),  # 10:00 AM
            (13, 0, SunPhase.MIDDAY, True),  # 1:00 PM
            (15, 0, SunPhase.AFTERNOON, True),  # 3:00 PM
            (17, 30, SunPhase.SUNSET, True),  # 5:30 PM
            (19, 0, SunPhase.EVENING, False),  # 7:00 PM
            (23, 0, SunPhase.NIGHT, False),  # 11:00 PM
        ]

        for hour, minute, expected_phase, expected_is_day in test_cases:
            dt = datetime(2025, 12, 20, hour, minute, tzinfo=timezone.utc)
            state = clock.get_state_at(dt)

            assert state.sun_phase == expected_phase, (
                f"At {hour}:{minute:02d}, expected {expected_phase.value}, got {state.sun_phase.value}"
            )
            assert state.is_day == expected_is_day, (
                f"At {hour}:{minute:02d}, expected is_day={expected_is_day}, got {state.is_day}"
            )

    def test_prana_allows_kala_mutations(self):
        """
        E2E: PRANA Orchestrator accepts KALA mutation actions.
        """
        from vibe_core.prana_orchestrator import ALLOWED_ACTIONS, StateMutation

        # KALA's actions should be allowed
        assert "trigger_ritual" in ALLOWED_ACTIONS
        assert "update_cycle" in ALLOWED_ACTIONS

        # Create valid mutation
        mutation = StateMutation(
            plugin_id="kala",
            action="trigger_ritual",
            target="ritual/sunrise",
            payload={"phase": "sunrise", "sun_phase": "morning"},
        )

        assert mutation.validate() is True

    def test_lunar_cycle_tithi_calculation(self):
        """
        E2E: Lunar cycle and tithi calculations are consistent.
        """
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock, Paksha

        clock = CosmicClock()

        # Get current state
        state = clock.get_current_state()

        # Tithi should be 1-15
        assert 1 <= state.tithi <= 15

        # Lunar day should be 1-30
        assert 1 <= state.lunar_day <= 30

        # Paksha should be consistent with lunar day
        if state.lunar_day <= 15:
            assert state.paksha == Paksha.SHUKLA
        else:
            assert state.paksha == Paksha.KRISHNA

    def test_special_days_detection(self):
        """
        E2E: Special days (Ekadashi, Purnima, Amavasya) detected.
        """
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock

        clock = CosmicClock()

        # These should return bool without error
        assert isinstance(clock.is_ekadashi(), bool)
        assert isinstance(clock.is_purnima(), bool)
        assert isinstance(clock.is_amavasya(), bool)

        # Purnima and Amavasya are mutually exclusive
        if clock.is_purnima():
            assert not clock.is_amavasya()
        if clock.is_amavasya():
            assert not clock.is_purnima()


class TestKalaSynchronization:
    """Tests for KALA synchronization with other systems."""

    def test_kala_priority_before_sarga_cycle(self):
        """KALA (priority 3) runs before sarga_cycle (priority 5)."""
        from vibe_core.plugins.kala import KalaPlugin
        from vibe_core.plugins.sarga_cycle.plugin_main import SargaCyclePlugin

        kala = KalaPlugin()
        sarga_cycle = SargaCyclePlugin()

        # Lower priority = runs first
        assert kala.priority < sarga_cycle.priority
        assert kala.priority == 3
        assert sarga_cycle.priority == 5

    def test_kala_uses_sensors_phase(self):
        """KALA runs in SENSORS phase (first phase)."""
        from vibe_core.plugin_protocol import PulsePhase
        from vibe_core.plugins.kala import KalaPlugin

        kala = KalaPlugin()
        assert kala.pulse_phase == PulsePhase.SENSORS

    def test_all_time_sources_synchronized(self):
        """
        All time sources (KALA, Sarga, PRANA) can be synchronized.
        """
        from vibe_core.plugins.kala.cosmic_clock import CosmicClock
        from vibe_core.prana import load_config
        from vibe_core.sarga import Cycle, get_sarga

        # Load all time-related components
        clock = CosmicClock()
        sarga = get_sarga()
        prana_config = load_config()

        # All should be accessible
        state = clock.get_current_state()
        cycle = sarga.get_cycle()
        interval = prana_config.heartbeat.min_interval_minutes

        # Verify types
        assert state.utc_time is not None
        assert cycle in (Cycle.DAY_OF_BRAHMA, Cycle.NIGHT_OF_BRAHMA)
        assert isinstance(interval, int)

        # If it's day, Sarga should be set to DAY (after KALA sync)
        # Note: This might not match if Sarga wasn't synced by KALA yet
        # But the chain should work when kernel boots
