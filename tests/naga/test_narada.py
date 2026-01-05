"""
Tests for NARADA Service - The Spy Agent.

Mythology: Narada travels everywhere, knows everything, tells everyone.
"Narada Muni ki Jai!" - The cosmic journalist.

Purpose: Intercept function calls to observe system behavior WITHOUT modification.
"""

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestNaradaBasics:
    """Test basic Narada initialization and status."""

    def test_initialization(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        assert narada._observations_count == 0
        assert narada._errors == 0
        assert len(narada._observation_buffer) == 0

    def test_get_status(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()
        status = narada.get_status()

        assert status.naga_type.value == "narada"
        assert status.healthy is True
        assert status.events_processed == 0


class TestSpyDecorator:
    """Test the @narada.spy decorator for function interception."""

    def test_spy_decorator_observes_call(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        def target_function(x, y):
            return x + y

        result = target_function(2, 3)

        assert result == 5  # Function still works
        assert narada._observations_count == 1

    def test_spy_decorator_preserves_function_name(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        def my_special_function():
            pass

        assert my_special_function.__name__ == "my_special_function"

    def test_spy_decorator_records_observation(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        def observed_func(a, b, c=None):
            return "done"

        observed_func(1, 2, c="test")

        assert len(narada._observation_buffer) == 1
        obs = narada._observation_buffer[0]
        assert obs.function_name == "observed_func"
        assert obs.args_count == 2
        assert obs.kwargs_keys == ["c"]
        assert obs.result_type == "str"

    def test_spy_decorator_handles_exceptions(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        def failing_func():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            failing_func()

        # Exception should still be recorded
        assert narada._observations_count == 1
        obs = narada._observation_buffer[0]
        assert obs.exception_type == "ValueError"


class TestObservationBuffer:
    """Test observation buffering and export."""

    def test_buffer_respects_max_size(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService(max_buffer_size=3)

        @narada.spy
        def func():
            pass

        for _ in range(5):
            func()

        # Buffer should only keep last 3
        assert len(narada._observation_buffer) == 3
        assert narada._observations_count == 5  # Total count preserved

    def test_export_observations_clears_buffer(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        def func():
            pass

        func()
        func()

        observations = narada.export_observations()

        assert len(observations) == 2
        assert len(narada._observation_buffer) == 0  # Cleared

    def test_export_observations_returns_copies(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        def func():
            pass

        func()

        obs1 = narada.export_observations()
        obs2 = narada.export_observations()

        assert len(obs1) == 1
        assert len(obs2) == 0  # Already exported


class TestAsyncSpying:
    """Test spying on async functions."""

    @pytest.mark.asyncio
    async def test_spy_async_function(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        async def async_target(x):
            await asyncio.sleep(0.001)
            return x * 2

        result = await async_target(5)

        assert result == 10
        assert narada._observations_count == 1

    @pytest.mark.asyncio
    async def test_spy_async_records_duration(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService()

        @narada.spy
        async def slow_func():
            await asyncio.sleep(0.05)
            return "done"

        await slow_func()

        obs = narada._observation_buffer[0]
        assert obs.duration_ms >= 40  # At least 40ms


class TestCortexIntegration:
    """Test integration with NagaCortex."""

    def test_report_to_cortex_when_configured(self):
        from vibe_core.naga.services.narada import NaradaService

        mock_cortex = MagicMock()
        narada = NaradaService(cortex=mock_cortex)

        @narada.spy
        def func():
            return 42

        func()

        mock_cortex.receive_narada_observation.assert_called_once()

    def test_no_cortex_still_works(self):
        from vibe_core.naga.services.narada import NaradaService

        narada = NaradaService(cortex=None)

        @narada.spy
        def func():
            return 42

        result = func()

        assert result == 42
        assert narada._observations_count == 1


class TestSignedObservations:
    """Test that observations can be signed (37th Principle)."""

    def test_observation_can_be_signed(self):
        from vibe_core.naga.identity import NagaIdentity
        from vibe_core.naga.services.narada import NaradaService

        identity = NagaIdentity.generate(agent_id="narada_test")
        narada = NaradaService(identity=identity)

        @narada.spy
        def func():
            pass

        func()

        obs = narada._observation_buffer[0]
        assert obs.observer_id == "narada_test"
        # Signature should be present if identity provided
        assert obs.signature is not None


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
