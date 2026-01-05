"""
Tests for NagaProxy - The Balarama Pattern.

Verifies:
- Method interception works
- Timing is tracked (duration_ms)
- Exceptions are caught and re-raised
- Observations are buffered
- TypeVar typing works correctly
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.proxy import NagaProxy, ProxyObservation, wrap_service


class MockService:
    """Test service to wrap."""

    def __init__(self):
        self.call_count = 0

    def do_something(self, x: int, y: int) -> int:
        """Normal method."""
        self.call_count += 1
        return x + y

    def do_slow(self) -> str:
        """Slow method for timing test."""
        import time

        time.sleep(0.01)  # 10ms
        return "done"

    def do_fail(self) -> None:
        """Method that raises."""
        raise ValueError("Test error")

    def _private_method(self) -> str:
        """Private method."""
        return "private"


class TestNagaProxyBasics:
    """Basic proxy functionality tests."""

    def test_wrap_service(self):
        """Test wrapping a service."""
        service = MockService()
        proxy = NagaProxy(service)

        assert proxy._service_name == "MockService"
        assert proxy._wrapped is service

    def test_wrap_none_raises(self):
        """Test that wrapping None raises TypeError."""
        with pytest.raises(TypeError, match="Cannot wrap None"):
            NagaProxy(None)

    def test_method_passthrough(self):
        """Test that methods are called correctly."""
        service = MockService()
        proxy = NagaProxy(service)

        result = proxy.do_something(2, 3)

        assert result == 5
        assert service.call_count == 1

    def test_unwrap(self):
        """Test unwrapping to get original service."""
        service = MockService()
        proxy = NagaProxy(service)

        assert proxy.unwrap is service


class TestNagaProxyObservation:
    """Observation (Narada) functionality tests."""

    def test_observations_buffered(self):
        """Test that observations are buffered."""
        service = MockService()
        proxy = NagaProxy(service)

        proxy.do_something(1, 2)
        proxy.do_something(3, 4)

        observations = proxy.get_observations()
        assert len(observations) == 2
        assert all(isinstance(o, ProxyObservation) for o in observations)

    def test_observation_fields(self):
        """Test observation contains correct fields."""
        service = MockService()
        proxy = NagaProxy(service)

        proxy.do_something(1, 2)

        obs = proxy.get_observations()[0]
        assert obs.service_type == "MockService"
        assert obs.method_name == "do_something"
        assert obs.args_count == 2  # x and y
        assert obs.result_type == "int"
        assert obs.exception_type is None
        assert obs.duration_ms >= 0

    def test_clear_observations(self):
        """Test clearing observation buffer."""
        service = MockService()
        proxy = NagaProxy(service)

        proxy.do_something(1, 2)
        count = proxy.clear_observations()

        assert count == 1
        assert len(proxy.get_observations()) == 0


class TestNagaProxyTiming:
    """Timing (Chitragupta) functionality tests."""

    def test_duration_tracked(self):
        """Test that duration_ms is tracked."""
        service = MockService()
        proxy = NagaProxy(service)

        proxy.do_slow()

        obs = proxy.get_observations()[0]
        # Should be at least 10ms (we sleep for 10ms)
        assert obs.duration_ms >= 10


class TestNagaProxyExceptions:
    """Exception handling (Kaliya) functionality tests."""

    def test_exception_reraised(self):
        """Test that exceptions are re-raised (no silent failures)."""
        service = MockService()
        proxy = NagaProxy(service)

        with pytest.raises(ValueError, match="Test error"):
            proxy.do_fail()

    def test_exception_observed(self):
        """Test that exceptions are observed."""
        service = MockService()
        proxy = NagaProxy(service)

        try:
            proxy.do_fail()
        except ValueError:
            pass

        obs = proxy.get_observations()[0]
        assert obs.exception_type == "ValueError"


class TestNagaProxyPrivateMethods:
    """Private method handling tests."""

    def test_private_not_observed_by_default(self):
        """Test that private methods are not observed by default."""
        service = MockService()
        proxy = NagaProxy(service)

        result = proxy._private_method()

        assert result == "private"
        # Should not be in observations
        assert len(proxy.get_observations()) == 0

    def test_private_observed_when_enabled(self):
        """Test that private methods are observed when enabled."""
        service = MockService()
        proxy = NagaProxy(service, observe_private=True)

        proxy._private_method()

        assert len(proxy.get_observations()) == 1


class TestNagaProxyIntegration:
    """Integration with NAGA services tests."""

    def test_chitragupta_integration(self):
        """Test integration with Chitragupta."""
        service = MockService()
        chitragupta = MagicMock()
        proxy = NagaProxy(service, chitragupta=chitragupta)

        proxy.do_something(1, 2)

        # Chitragupta.record should be called
        chitragupta.record.assert_called_once()
        args = chitragupta.record.call_args[0]
        assert "MockService.do_something" in args[0]
        assert args[1] == "duration_ms"


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_wrap_service_function(self):
        """Test wrap_service convenience function."""
        service = MockService()
        proxy = wrap_service(service)

        assert isinstance(proxy, NagaProxy)
        assert proxy._wrapped is service
