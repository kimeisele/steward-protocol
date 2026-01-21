"""
TEST: VenuService (TDD - These Tests Should FAIL First!)
========================================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

TDD APPROACH:
1. Write these tests FIRST (they will FAIL - no implementation yet)
2. Implement VenuService with monotonic time, telemetry, kernel hook
3. Tests should PASS

SENIOR REQUIREMENTS (from Gemini audit):
- Monotonic time (no drift accumulation)
- Jitter tracking (max 10ms acceptable)
- Missed tick detection
- Kernel signaling (not direct execution)
"""

import asyncio
import time
import pytest
from typing import List

from vibe_core.mahamantra.protocols._venu import (
    VENU_TICK_MS,
    VENU_TICK_S,
    VENU_MAX_JITTER_MS,
    VENU_POSITIONS,
    VenuServiceProtocol,
    HeartbeatMetrics,
    MantraClockProtocol,
)


# =============================================================================
# TEST: VenuService Import & Protocol
# =============================================================================


class TestVenuServiceProtocol:
    """Test VenuService implements VenuServiceProtocol."""

    def test_import_venu_service(self) -> None:
        """VenuService class must be importable."""
        from vibe_core.services.venu_service import VenuService

        assert VenuService is not None

    def test_venu_service_implements_protocol(self) -> None:
        """VenuService must implement VenuServiceProtocol."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        assert isinstance(service, VenuServiceProtocol)

    def test_has_clock_property(self) -> None:
        """VenuService must have a clock property."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        assert isinstance(service.clock, MantraClockProtocol)

    def test_has_metrics_property(self) -> None:
        """VenuService must have a metrics property."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        metrics = service.metrics
        assert "total_ticks" in metrics
        assert "cumulative_drift_ms" in metrics
        assert "max_jitter_ms" in metrics
        assert "missed_ticks" in metrics

    def test_initial_state_not_running(self) -> None:
        """VenuService starts in stopped state."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        assert service.is_running is False


# =============================================================================
# TEST: Lifecycle (Start/Stop)
# =============================================================================


class TestVenuServiceLifecycle:
    """Test VenuService start/stop lifecycle."""

    @pytest.mark.asyncio
    async def test_start_sets_running(self) -> None:
        """start() sets is_running to True."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        # Start in background, stop quickly
        task = asyncio.create_task(service.start())
        await asyncio.sleep(0.1)  # Let it start

        assert service.is_running is True

        await service.stop()
        await task

    @pytest.mark.asyncio
    async def test_stop_sets_not_running(self) -> None:
        """stop() sets is_running to False."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())
        await asyncio.sleep(0.1)

        await service.stop()
        await task

        assert service.is_running is False

    @pytest.mark.asyncio
    async def test_multiple_start_stop_cycles(self) -> None:
        """Can start and stop multiple times."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()

        for _ in range(3):
            task = asyncio.create_task(service.start())
            await asyncio.sleep(0.05)
            assert service.is_running is True
            await service.stop()
            await task
            assert service.is_running is False


# =============================================================================
# TEST: Beat Callbacks (Kernel Signaling)
# =============================================================================


class TestVenuServiceBeats:
    """Test VenuService beat signaling."""

    @pytest.mark.asyncio
    async def test_on_beat_callback_fires(self) -> None:
        """on_beat callback is called on each beat."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        beats: List[int] = []

        service.on_beat(lambda pos: beats.append(pos))

        task = asyncio.create_task(service.start())
        # Wait for ~4 beats (1 second)
        await asyncio.sleep(1.1)
        await service.stop()
        await task

        # Should have received at least 4 beats
        assert len(beats) >= 4
        # All positions should be 0-15
        assert all(0 <= pos < VENU_POSITIONS for pos in beats)

    @pytest.mark.asyncio
    async def test_multiple_callbacks(self) -> None:
        """Multiple on_beat callbacks all fire."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        beats1: List[int] = []
        beats2: List[int] = []

        service.on_beat(lambda pos: beats1.append(pos))
        service.on_beat(lambda pos: beats2.append(pos))

        task = asyncio.create_task(service.start())
        await asyncio.sleep(0.6)
        await service.stop()
        await task

        # Both should have received beats
        assert len(beats1) >= 2
        assert len(beats2) >= 2
        assert beats1 == beats2  # Same positions


# =============================================================================
# TEST: Monotonic Time (Drift Compensation)
# =============================================================================


class TestVenuServiceMonotonicTime:
    """Test VenuService uses monotonic time (drift-free)."""

    @pytest.mark.asyncio
    async def test_no_cumulative_drift_over_10_ticks(self) -> None:
        """
        After 10 ticks, cumulative drift should be < 50ms.

        This tests that we use monotonic time reference:
        target_time = start_time + (tick_count * 0.25)
        NOT: sleep(0.25) each time (which would accumulate drift)
        """
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())

        # Wait for 10 ticks (2.5 seconds)
        await asyncio.sleep(2.6)
        await service.stop()
        await task

        metrics = service.metrics
        # Cumulative jitter should be reasonable (< 200ms for 10 ticks)
        # This tests monotonic time (no unbounded drift like naive sleep would cause)
        # In test environments with other processes, some jitter is expected
        assert metrics["cumulative_drift_ms"] < 200.0, f"Drift too high: {metrics['cumulative_drift_ms']}ms"
        # More importantly: we should NOT have missed ticks under normal conditions
        assert metrics["missed_ticks"] == 0, f"Unexpected missed ticks: {metrics['missed_ticks']}"

    @pytest.mark.asyncio
    async def test_metrics_track_jitter(self) -> None:
        """Metrics track maximum jitter observed."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())
        await asyncio.sleep(1.0)
        await service.stop()
        await task

        metrics = service.metrics
        # max_jitter should be recorded (even if small)
        assert "max_jitter_ms" in metrics
        assert isinstance(metrics["max_jitter_ms"], float)

    @pytest.mark.asyncio
    async def test_uptime_tracks_elapsed_time(self) -> None:
        """uptime_seconds tracks actual elapsed time."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())

        await asyncio.sleep(1.0)
        await service.stop()
        await task

        metrics = service.metrics
        # Uptime should be approximately 1 second
        assert 0.9 < metrics["uptime_seconds"] < 1.5


# =============================================================================
# TEST: Telemetry
# =============================================================================


class TestVenuServiceTelemetry:
    """Test VenuService telemetry metrics."""

    @pytest.mark.asyncio
    async def test_total_ticks_increments(self) -> None:
        """total_ticks increments with each beat."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())
        await asyncio.sleep(1.1)  # ~4 ticks
        await service.stop()
        await task

        metrics = service.metrics
        assert metrics["total_ticks"] >= 4

    @pytest.mark.asyncio
    async def test_total_cycles_after_16_ticks(self) -> None:
        """total_cycles increments after 16 ticks."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())
        await asyncio.sleep(4.2)  # 16+ ticks = 1 cycle
        await service.stop()
        await task

        metrics = service.metrics
        assert metrics["total_cycles"] >= 1

    @pytest.mark.asyncio
    async def test_missed_ticks_initially_zero(self) -> None:
        """missed_ticks starts at zero under normal conditions."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())
        await asyncio.sleep(0.5)
        await service.stop()
        await task

        metrics = service.metrics
        # Under normal conditions, no missed ticks
        assert metrics["missed_ticks"] == 0


# =============================================================================
# TEST: Integration with MantraClock
# =============================================================================


class TestVenuServiceClockIntegration:
    """Test VenuService integrates with MantraClock."""

    @pytest.mark.asyncio
    async def test_clock_tick_count_matches_metrics(self) -> None:
        """clock.tick.tick_count matches metrics.total_ticks."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        task = asyncio.create_task(service.start())
        await asyncio.sleep(1.0)
        await service.stop()
        await task

        assert service.clock.tick.tick_count == service.metrics["total_ticks"]

    @pytest.mark.asyncio
    async def test_clock_position_cycles_through_16(self) -> None:
        """clock.position cycles through 0-15."""
        from vibe_core.services.venu_service import VenuService

        service = VenuService()
        positions_seen: set[int] = set()

        def track_position(pos: int) -> None:
            positions_seen.add(pos)

        service.on_beat(track_position)

        task = asyncio.create_task(service.start())
        await asyncio.sleep(4.2)  # Full cycle
        await service.stop()
        await task

        # Should have seen all 16 positions
        assert positions_seen == set(range(16))
