"""
Tests for KalaBridgeSubscriber — BeatSubscriberProtocol compliance.

Verifies:
- Protocol satisfaction (isinstance check)
- SSOT-derived intervals (NADI = 72, patrol = NADI × SHARANAGATI)
- Log scan fires every NADI
- Watchman patrol fires every 6th NADI (108s = MALA seconds)
"""

from unittest.mock import MagicMock, patch

from vibe_core.mahamantra.protocols._seed import SHARANAGATI
from vibe_core.mahamantra.protocols._venu import (
    BeatSubscriberProtocol,
    VENU_NADI_TICKS,
)
from vibe_core.shuddhi.kala_bridge import KalaBridgeSubscriber


class TestKalaBridgeProtocol:
    """KalaBridgeSubscriber must satisfy BeatSubscriberProtocol."""

    def test_isinstance_beat_subscriber(self):
        sub = KalaBridgeSubscriber()
        assert isinstance(sub, BeatSubscriberProtocol)

    def test_beat_name(self):
        sub = KalaBridgeSubscriber()
        assert sub.beat_name == "kala_bridge"

    def test_beat_interval_is_nadi(self):
        sub = KalaBridgeSubscriber()
        assert sub.beat_interval == VENU_NADI_TICKS
        assert sub.beat_interval == 72

    def test_has_on_beat_tick(self):
        sub = KalaBridgeSubscriber()
        assert callable(sub.on_beat_tick)


class TestKalaBridgeDispatch:
    """Verify log scan and patrol fire at correct intervals."""

    def test_log_scan_fires_every_nadi(self):
        sub = KalaBridgeSubscriber()
        with patch.object(sub, "_run_log_scan") as mock_scan:
            for i in range(3):
                sub.on_beat_tick(tick_count=i * VENU_NADI_TICKS, position=0)
            assert mock_scan.call_count == 3

    def test_patrol_fires_every_sharanagati_nadis(self):
        sub = KalaBridgeSubscriber()
        with patch.object(sub, "_run_log_scan"):
            with patch.object(sub, "_run_watchman_patrol") as mock_patrol:
                for i in range(SHARANAGATI * 2):
                    sub.on_beat_tick(tick_count=i, position=0)
                # Patrol fires at nadi 6 and nadi 12 (every SHARANAGATI)
                assert mock_patrol.call_count == 2

    def test_patrol_interval_is_mala_seconds(self):
        """432 ticks × 0.25s = 108s = MALA seconds."""
        patrol_ticks = VENU_NADI_TICKS * SHARANAGATI
        assert patrol_ticks == 432
        assert patrol_ticks * 0.25 == 108.0

    def test_nadi_counter_increments(self):
        sub = KalaBridgeSubscriber()
        assert sub._nadi_count == 0
        with patch.object(sub, "_run_log_scan"):
            sub.on_beat_tick(tick_count=72, position=0)
        assert sub._nadi_count == 1
