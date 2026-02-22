"""
Tests for JagannathSubscriber — BeatSubscriberProtocol compliance.
"""

from unittest.mock import MagicMock, patch

from vibe_core.mahamantra import VENU_FIELD_TICKS, BeatSubscriberProtocol
from vibe_core.services.jagannath_subscriber import JagannathSubscriber


class TestJagannathSubscriberProtocol:
    """JagannathSubscriber must satisfy BeatSubscriberProtocol."""

    def test_isinstance_beat_subscriber(self):
        sub = JagannathSubscriber()
        assert isinstance(sub, BeatSubscriberProtocol)

    def test_beat_name(self):
        sub = JagannathSubscriber()
        assert sub.beat_name == "jagannath_ratha_yatra"

    def test_beat_interval_is_field(self):
        sub = JagannathSubscriber()
        assert sub.beat_interval == VENU_FIELD_TICKS
        assert sub.beat_interval == 144

    def test_has_on_beat_tick(self):
        sub = JagannathSubscriber()
        assert callable(sub.on_beat_tick)


class TestJagannathDispatch:
    """Verify ratha_yatra is called via ServiceRegistry."""

    def test_calls_ratha_yatra_when_jagannath_available(self):
        sub = JagannathSubscriber()
        mock_jagannath = MagicMock()
        mock_jagannath.start_ratha_yatra.return_value = 0

        with patch("vibe_core.di.ServiceRegistry.get", return_value=mock_jagannath):
            sub.on_beat_tick(tick_count=144, position=0)
            mock_jagannath.start_ratha_yatra.assert_called_once()

    def test_skips_when_jagannath_not_available(self):
        sub = JagannathSubscriber()

        with patch("vibe_core.di.ServiceRegistry.get", return_value=None):
            # Should not raise
            sub.on_beat_tick(tick_count=144, position=0)

    def test_handles_exception_gracefully(self):
        sub = JagannathSubscriber()
        mock_jagannath = MagicMock()
        mock_jagannath.start_ratha_yatra.side_effect = RuntimeError("test")

        with patch("vibe_core.di.ServiceRegistry.get", return_value=mock_jagannath):
            # Should not raise
            sub.on_beat_tick(tick_count=144, position=0)
