"""
Tests for NAGA Organic Flooding.

Tests the hardened implementation with:
- Recursion prevention
- Async decoupling
- Side channel dispatch
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestRecursionGuard:
    """Test the recursion prevention mechanism."""

    @pytest.fixture
    def flood_controller(self):
        """Create a flood controller without dependencies."""
        from vibe_core.naga.flood import NagaFloodController

        return NagaFloodController(sesha=None, takshaka=None, enabled=True)

    def test_skips_naga_source_events(self, flood_controller):
        """Events from NAGA sources should be skipped."""
        # Create mock event from NAGA
        event = MagicMock()
        event.agent_id = "sesha"
        event.event_type = "STATE_CHANGE"

        # Process event
        flood_controller._on_event_sync(event)

        # Should be counted as skipped
        assert flood_controller._stats.events_seen == 1
        assert flood_controller._stats.events_skipped_recursion == 1

    def test_skips_takshaka_events(self, flood_controller):
        """Events from Takshaka should be skipped."""
        event = MagicMock()
        event.agent_id = "takshaka"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_recursion == 1

    def test_skips_naga_eye_events(self, flood_controller):
        """Events from NAGA_EYE should be skipped."""
        event = MagicMock()
        event.agent_id = "NAGA_EYE"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_recursion == 1

    def test_skips_already_seen_events(self, flood_controller):
        """Events marked as _naga_seen should be skipped."""
        event = MagicMock()
        event.agent_id = "some_agent"
        event._naga_seen = True

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_recursion == 1

    def test_processes_normal_events(self, flood_controller):
        """Normal events should be queued for analysis."""
        event = MagicMock()
        event.agent_id = "user_agent"
        event.event_type = "USER_ACTION"
        event.id = "event_123"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_seen == 1
        assert flood_controller._stats.events_skipped_recursion == 0
        assert flood_controller._analysis_queue.qsize() == 1


class TestNoiseFilter:
    """Test the noise filtering mechanism."""

    @pytest.fixture
    def flood_controller(self):
        from vibe_core.naga.flood import NagaFloodController

        return NagaFloodController(sesha=None, takshaka=None, enabled=True)

    def test_skips_debug_events(self, flood_controller):
        """DEBUG events should be skipped."""
        event = MagicMock()
        event.agent_id = "some_agent"
        event.event_type = "DEBUG"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_noise == 1

    def test_skips_heartbeat_events(self, flood_controller):
        """HEARTBEAT events should be skipped."""
        event = MagicMock()
        event.agent_id = "some_agent"
        event.event_type = "HEARTBEAT"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_noise == 1

    def test_skips_metric_events(self, flood_controller):
        """METRIC events should be skipped."""
        event = MagicMock()
        event.agent_id = "some_agent"
        event.event_type = "METRIC"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_noise == 1

    def test_processes_action_events(self, flood_controller):
        """ACTION events should be processed."""
        event = MagicMock()
        event.agent_id = "some_agent"
        event.event_type = "ACTION"
        event.id = "event_456"

        flood_controller._on_event_sync(event)

        assert flood_controller._stats.events_skipped_noise == 0
        assert flood_controller._analysis_queue.qsize() == 1


class TestQueueOverflow:
    """Test queue overflow handling."""

    @pytest.fixture
    def flood_controller(self):
        from vibe_core.naga.flood import NagaFloodController

        return NagaFloodController(sesha=None, takshaka=None, enabled=True)

    def test_handles_queue_overflow_gracefully(self, flood_controller):
        """Queue overflow should be handled silently."""
        # Fill the queue
        for i in range(1100):  # More than MAX_ANALYSIS_QUEUE
            event = MagicMock()
            event.agent_id = "flood_agent"
            event.event_type = "ACTION"
            event.id = f"event_{i}"

            flood_controller._on_event_sync(event)

        # Should have overflows but no crash
        assert flood_controller._stats.queue_overflows > 0
        assert flood_controller._stats.events_seen == 1100


class TestContentExtraction:
    """Test content extraction for analysis."""

    @pytest.fixture
    def flood_controller(self):
        from vibe_core.naga.flood import NagaFloodController

        return NagaFloodController(sesha=None, takshaka=None, enabled=True)

    def test_extracts_message_attribute(self, flood_controller):
        """Should extract message attribute."""
        event = MagicMock()
        event.message = "Hello world"

        content = flood_controller._extract_content(event)

        assert "Hello world" in content

    def test_extracts_content_attribute(self, flood_controller):
        """Should extract content attribute."""
        event = MagicMock()
        event.message = None
        event.content = "Some content"

        content = flood_controller._extract_content(event)

        assert "Some content" in content

    def test_extracts_data_dict(self, flood_controller):
        """Should extract data dict."""
        event = MagicMock()
        event.message = None
        event.content = None
        event.data = {"key": "value"}

        content = flood_controller._extract_content(event)

        assert "key" in content

    def test_limits_content_size(self, flood_controller):
        """Content should be limited to prevent memory issues."""
        event = MagicMock()
        event.message = "x" * 50000  # Very large

        content = flood_controller._extract_content(event)

        assert len(content) <= 10000


class TestFloodStats:
    """Test statistics tracking."""

    def test_stats_to_dict(self):
        """Stats should serialize to dict."""
        from vibe_core.naga.flood import FloodStats

        stats = FloodStats()
        stats.events_seen = 100
        stats.violations_detected = 5

        d = stats.to_dict()

        assert d["events_seen"] == 100
        assert d["violations_detected"] == 5
        assert "uptime_seconds" in d
        assert "events_per_second" in d


class TestSignalWatcher:
    """Test SignalBus watching."""

    @pytest.fixture
    def signal_watcher(self):
        from vibe_core.naga.flood import NagaSignalWatcher

        return NagaSignalWatcher(sesha=None, takshaka=None)

    def test_initial_state(self, signal_watcher):
        """Should start unsubscribed."""
        assert signal_watcher._subscribed is False
        assert signal_watcher._signals_seen == 0

    def test_get_stats(self, signal_watcher):
        """Should return stats dict."""
        stats = signal_watcher.get_stats()

        assert "subscribed" in stats
        assert "signals_seen" in stats


class TestFloodManager:
    """Test unified flood manager."""

    @pytest.fixture
    def flood_manager(self):
        from vibe_core.naga.flood import NagaFloodManager

        return NagaFloodManager(sesha=None, takshaka=None, enabled=True)

    def test_initial_state(self, flood_manager):
        """Should start not started."""
        assert flood_manager._started is False

    def test_disabled_manager_does_nothing(self):
        """Disabled manager should not start."""
        from vibe_core.naga.flood import NagaFloodManager

        manager = NagaFloodManager(enabled=False)
        manager.start()

        assert manager._started is False

    def test_get_status(self, flood_manager):
        """Should return unified status."""
        status = flood_manager.get_status()

        assert "enabled" in status
        assert "started" in status
        assert "event_flood" in status
        assert "signal_watch" in status


class TestAsyncAnalysis:
    """Test async analysis with toxicity detection."""

    @pytest.fixture
    def takshaka_mock(self):
        """Create mock Takshaka with toxicity detection."""
        mock = MagicMock()
        mock.scan_toxicity.return_value = MagicMock(
            blocked=False,
            score=0.1,
            patterns=[],
        )
        return mock

    @pytest.fixture
    def flood_controller_with_takshaka(self, takshaka_mock):
        from vibe_core.naga.flood import NagaFloodController

        return NagaFloodController(
            sesha=None,
            takshaka=takshaka_mock,
            enabled=True,
        )

    @pytest.mark.asyncio
    async def test_analyze_clean_event(self, flood_controller_with_takshaka, takshaka_mock):
        """Clean events should not trigger violations."""
        event = MagicMock()
        event.message = "Hello, how are you?"

        await flood_controller_with_takshaka._analyze_event(event)

        takshaka_mock.scan_toxicity.assert_called_once()
        assert flood_controller_with_takshaka._stats.violations_detected == 0

    @pytest.mark.asyncio
    async def test_analyze_toxic_event(self, takshaka_mock):
        """Toxic events should trigger violations."""
        from vibe_core.naga.flood import NagaFloodController

        # Make Takshaka detect toxicity
        takshaka_mock.scan_toxicity.return_value = MagicMock(
            blocked=True,
            score=0.9,
            patterns=["SQL_INJECTION"],
        )
        takshaka_mock.bite = MagicMock()

        controller = NagaFloodController(
            sesha=None,
            takshaka=takshaka_mock,
            enabled=True,
        )

        event = MagicMock()
        event.agent_id = "malicious_agent"
        event.event_type = "ACTION"
        event.message = "DROP TABLE users"

        await controller._analyze_event(event)

        # Should have detected violation
        assert controller._stats.violations_detected == 1
        # Should have called bite (side channel)
        takshaka_mock.bite.assert_called_once()

    @pytest.mark.asyncio
    async def test_analysis_failure_is_silent(self, flood_controller_with_takshaka, takshaka_mock):
        """Analysis failures should not propagate."""
        takshaka_mock.scan_toxicity.side_effect = Exception("Scan failed")

        event = MagicMock()
        event.message = "Test message"

        # Should not raise
        await flood_controller_with_takshaka._analyze_event(event)

        # No violations counted on error
        assert flood_controller_with_takshaka._stats.violations_detected == 0
