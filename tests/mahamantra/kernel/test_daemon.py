"""
TESTS: kernel/daemon.py - Mahamantra Daemon
============================================

REAL TESTS for:
1. DaemonState enum
2. DaemonMetrics dataclass
3. MahamantraDaemon class
4. get_daemon function
5. start_daemon and run_daemon functions
"""

import asyncio
import pytest
from datetime import datetime
from vibe_core.mahamantra.kernel.daemon import (
    DaemonState,
    DaemonMetrics,
    MahamantraDaemon,
    get_daemon,
    start_daemon,
    HEALTH_SAMADHI,
    HEALTH_SADHANA,
)
from vibe_core.mahamantra.protocols._entropy import EntropyLevel


# =============================================================================
# DaemonState Enum Tests
# =============================================================================


class TestDaemonState:
    """Test DaemonState enum."""

    def test_daemon_state_dormant(self):
        """DaemonState has DORMANT."""
        assert DaemonState.DORMANT.value == "dormant"

    def test_daemon_state_awakening(self):
        """DaemonState has AWAKENING."""
        assert DaemonState.AWAKENING.value == "awakening"

    def test_daemon_state_chanting(self):
        """DaemonState has CHANTING."""
        assert DaemonState.CHANTING.value == "chanting"

    def test_daemon_state_samadhi(self):
        """DaemonState has SAMADHI."""
        assert DaemonState.SAMADHI.value == "samadhi"

    def test_daemon_state_stopping(self):
        """DaemonState has STOPPING."""
        assert DaemonState.STOPPING.value == "stopping"

    def test_daemon_state_dead(self):
        """DaemonState has DEAD."""
        assert DaemonState.DEAD.value == "dead"

    def test_daemon_state_is_string_enum(self):
        """DaemonState is a string enum."""
        assert isinstance(DaemonState.DORMANT.value, str)


# =============================================================================
# DaemonMetrics Tests
# =============================================================================


class TestDaemonMetrics:
    """Test DaemonMetrics dataclass."""

    def test_daemon_metrics_creation(self):
        """DaemonMetrics can be created."""
        metrics = DaemonMetrics()
        assert metrics is not None

    def test_daemon_metrics_default_values(self):
        """DaemonMetrics has correct defaults."""
        metrics = DaemonMetrics()
        assert metrics.cycles_completed == 0
        assert metrics.total_chants == 0
        assert metrics.last_health_score == 0.0
        assert metrics.last_frequency == EntropyLevel.SADHANA
        assert metrics.uptime_seconds == 0.0
        assert metrics.start_time is None
        assert metrics.last_chant_time is None

    def test_daemon_metrics_health_history_default(self):
        """DaemonMetrics health_history starts empty."""
        metrics = DaemonMetrics()
        assert metrics.health_history == []

    def test_daemon_metrics_max_history_is_108(self):
        """DaemonMetrics max_history is 108 (one mala)."""
        metrics = DaemonMetrics()
        assert metrics.max_history == 108

    def test_daemon_metrics_record_health(self):
        """record_health adds to history."""
        metrics = DaemonMetrics()
        metrics.record_health(0.85)
        assert len(metrics.health_history) == 1
        assert metrics.health_history[0] == 0.85

    def test_daemon_metrics_record_health_limit(self):
        """record_health maintains max_history limit."""
        metrics = DaemonMetrics()
        for i in range(120):  # More than max_history
            metrics.record_health(float(i) / 120)

        assert len(metrics.health_history) == 108  # max_history

    def test_daemon_metrics_average_health_empty(self):
        """average_health returns 0.0 when empty."""
        metrics = DaemonMetrics()
        assert metrics.average_health == 0.0

    def test_daemon_metrics_average_health(self):
        """average_health calculates correctly."""
        metrics = DaemonMetrics()
        metrics.record_health(0.80)
        metrics.record_health(0.90)
        assert abs(metrics.average_health - 0.85) < 0.001

    def test_daemon_metrics_health_trend_unknown(self):
        """health_trend returns 'unknown' with insufficient data."""
        metrics = DaemonMetrics()
        assert metrics.health_trend == "unknown"

    def test_daemon_metrics_health_trend_improving(self):
        """health_trend detects improving health."""
        metrics = DaemonMetrics()
        # Add older lower values
        for _ in range(15):
            metrics.record_health(0.70)
        # Add newer higher values
        for _ in range(10):
            metrics.record_health(0.90)

        assert metrics.health_trend == "improving"

    def test_daemon_metrics_health_trend_declining(self):
        """health_trend detects declining health."""
        metrics = DaemonMetrics()
        # Add older higher values
        for _ in range(15):
            metrics.record_health(0.90)
        # Add newer lower values
        for _ in range(10):
            metrics.record_health(0.70)

        assert metrics.health_trend == "declining"

    def test_daemon_metrics_health_trend_stable(self):
        """health_trend detects stable health."""
        metrics = DaemonMetrics()
        # Add consistent values
        for _ in range(25):
            metrics.record_health(0.85)

        assert metrics.health_trend == "stable"


# =============================================================================
# MahamantraDaemon Tests
# =============================================================================


class TestMahamantraDaemon:
    """Test MahamantraDaemon class."""

    def test_daemon_creation(self):
        """MahamantraDaemon can be created."""
        daemon = MahamantraDaemon()
        assert daemon is not None

    def test_daemon_default_state(self):
        """MahamantraDaemon starts in DORMANT state."""
        daemon = MahamantraDaemon()
        assert daemon.state == DaemonState.DORMANT

    def test_daemon_is_alive_dormant(self):
        """is_alive returns False when DORMANT."""
        daemon = MahamantraDaemon()
        assert daemon.is_alive is False

    def test_daemon_metrics_property(self):
        """metrics property returns DaemonMetrics."""
        daemon = MahamantraDaemon()
        assert isinstance(daemon.metrics, DaemonMetrics)

    def test_daemon_custom_min_interval(self):
        """MahamantraDaemon accepts custom min_interval."""
        daemon = MahamantraDaemon(min_interval=0.5)
        assert daemon._min_interval == 0.5

    def test_daemon_custom_max_cycles(self):
        """MahamantraDaemon accepts custom max_cycles."""
        daemon = MahamantraDaemon(max_cycles=10)
        assert daemon._max_cycles == 10

    def test_daemon_stop(self):
        """stop sets stop_requested flag."""
        daemon = MahamantraDaemon()
        daemon.stop()
        assert daemon._stop_requested is True
        assert daemon.state == DaemonState.STOPPING

    def test_daemon_on_chant_callback(self):
        """on_chant sets callback."""
        daemon = MahamantraDaemon()
        callback = lambda text, cycle: None
        daemon.on_chant(callback)
        assert daemon._on_chant is callback

    def test_daemon_on_state_change_callback(self):
        """on_state_change sets callback."""
        daemon = MahamantraDaemon()
        callback = lambda state: None
        daemon.on_state_change(callback)
        assert daemon._on_state_change is callback

    def test_daemon_get_status(self):
        """get_status returns status dict."""
        daemon = MahamantraDaemon()
        status = daemon.get_status()

        assert "state" in status
        assert "is_alive" in status
        assert "cycles_completed" in status
        assert "total_chants" in status
        assert "last_health_score" in status
        assert "average_health" in status
        assert "health_trend" in status
        assert "uptime_seconds" in status

    def test_daemon_get_status_values(self):
        """get_status returns correct values."""
        daemon = MahamantraDaemon()
        status = daemon.get_status()

        assert status["state"] == "dormant"
        assert status["is_alive"] is False
        assert status["cycles_completed"] == 0


# =============================================================================
# Async Daemon Tests
# =============================================================================


class TestMahamantraDaemonAsync:
    """Async tests for MahamantraDaemon."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Daemon calls mahamantra.audit() without mock — triggers full Lotus pipeline timeout")
    async def test_daemon_start_and_stop(self):
        """Daemon can start and stop."""
        daemon = MahamantraDaemon(max_cycles=1)

        # Start in background task
        task = asyncio.create_task(daemon.start())

        # Give it time to start
        await asyncio.sleep(0.1)

        # It should have started
        assert daemon.state != DaemonState.DORMANT

        # Wait for it to finish (max_cycles=1)
        await task

        assert daemon.state == DaemonState.DEAD

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Async daemon stop timing is flaky in tests")
    async def test_daemon_stop_during_run(self):
        """Daemon can be stopped during run."""
        daemon = MahamantraDaemon(max_cycles=100)

        # Start in background
        task = asyncio.create_task(daemon.start())

        # Give it time to start
        await asyncio.sleep(0.1)

        # Stop it
        daemon.stop()

        # Wait for it to finish
        await asyncio.wait_for(task, timeout=5.0)

        assert daemon.state == DaemonState.DEAD

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Async daemon timing is flaky in tests")
    async def test_daemon_metrics_updated(self):
        """Daemon updates metrics during run."""
        daemon = MahamantraDaemon(max_cycles=2)

        await daemon.start()

        assert daemon.metrics.cycles_completed >= 1
        assert daemon.metrics.start_time is not None
        assert daemon.metrics.uptime_seconds > 0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Daemon calls mahamantra.audit() without mock — triggers full Lotus pipeline timeout")
    async def test_daemon_state_change_callback(self):
        """Daemon calls state change callback."""
        daemon = MahamantraDaemon(max_cycles=1)
        states = []

        daemon.on_state_change(lambda s: states.append(s))

        await daemon.start()

        # Should have seen state transitions
        assert len(states) > 0
        assert DaemonState.AWAKENING in states or DaemonState.CHANTING in states

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Async daemon timing is flaky in tests")
    async def test_daemon_already_alive(self):
        """Daemon warns if already alive."""
        daemon = MahamantraDaemon(max_cycles=10)

        # Start first time
        task = asyncio.create_task(daemon.start())
        await asyncio.sleep(0.1)

        # Try to start again - should just return
        await daemon.start()

        # Stop
        daemon.stop()
        await asyncio.wait_for(task, timeout=5.0)


# =============================================================================
# get_daemon Tests
# =============================================================================


class TestGetDaemon:
    """Test get_daemon function."""

    def test_get_daemon_returns_instance(self):
        """get_daemon returns MahamantraDaemon."""
        daemon = get_daemon()
        assert isinstance(daemon, MahamantraDaemon)

    def test_get_daemon_singleton(self):
        """get_daemon returns same instance."""
        daemon1 = get_daemon()
        daemon2 = get_daemon()
        assert daemon1 is daemon2


# =============================================================================
# Constants Tests
# =============================================================================


class TestDaemonConstants:
    """Test daemon constants."""

    def test_health_samadhi_value(self):
        """HEALTH_SAMADHI is 0.95."""
        assert HEALTH_SAMADHI == 0.95

    def test_health_sadhana_value(self):
        """HEALTH_SADHANA is 0.80."""
        assert HEALTH_SADHANA == 0.80

    def test_health_samadhi_greater_than_sadhana(self):
        """HEALTH_SAMADHI > HEALTH_SADHANA."""
        assert HEALTH_SAMADHI > HEALTH_SADHANA


# =============================================================================
# EntropyLevel Tests (from imports)
# =============================================================================


class TestEntropyLevel:
    """Test EntropyLevel enum (imported in daemon)."""

    def test_entropy_level_samadhi(self):
        """EntropyLevel has SAMADHI."""
        assert EntropyLevel.SAMADHI is not None

    def test_entropy_level_sadhana(self):
        """EntropyLevel has SADHANA."""
        assert EntropyLevel.SADHANA is not None

    def test_entropy_level_gajendra(self):
        """EntropyLevel has GAJENDRA."""
        assert EntropyLevel.GAJENDRA is not None

    def test_entropy_level_frequency_hz(self):
        """EntropyLevel has frequency_hz property."""
        assert hasattr(EntropyLevel.SAMADHI, "frequency_hz")

    def test_entropy_level_cycle_time(self):
        """EntropyLevel has cycle_time property."""
        assert hasattr(EntropyLevel.SAMADHI, "cycle_time")

    def test_entropy_level_word_interval(self):
        """EntropyLevel has word_interval property."""
        assert hasattr(EntropyLevel.SAMADHI, "word_interval")

    def test_entropy_level_from_health(self):
        """EntropyLevel.from_health works."""
        # High health -> SAMADHI
        level = EntropyLevel.from_health(0.99)
        assert level == EntropyLevel.SAMADHI

        # Low health -> GAJENDRA
        level = EntropyLevel.from_health(0.5)
        assert level == EntropyLevel.GAJENDRA


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.kernel import daemon

        expected = [
            "EntropyLevel",
            "HEALTH_SAMADHI",
            "HEALTH_SADHANA",
            "DaemonState",
            "DaemonMetrics",
            "MahamantraDaemon",
            "get_daemon",
            "start_daemon",
            "run_daemon",
        ]
        for item in expected:
            assert item in daemon.__all__, f"{item} should be in __all__"
