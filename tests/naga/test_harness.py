"""
Tests for NagaTestHarness - Protocol-Based Testing Infrastructure.

These tests verify that:
1. NagaTestHarness provides Protocol-compliant NullObjects
2. ServiceRegistry is used correctly (same as production)
3. No MagicMock anywhere
4. Clean isolation between tests
"""

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.naga import (
    ChitraguptaProtocol,
    SeshaProtocol,
    TakshakaProtocol,
    VasukiProtocol,
)


class TestNagaHarnessBasics:
    """Basic harness functionality."""

    def test_harness_provides_sesha(self, naga_harness):
        """Harness provides Sesha via Protocol."""
        sesha = naga_harness.sesha
        assert sesha is not None
        # NullSesha behavior
        assert sesha.get_top_hash() == ""
        assert sesha.get_sequence() == 0

    def test_harness_provides_takshaka(self, naga_harness):
        """Harness provides Takshaka via Protocol."""
        takshaka = naga_harness.takshaka
        assert takshaka is not None
        status = takshaka.get_status()
        assert status.healthy is False  # NullTakshaka is not healthy

    def test_harness_provides_vasuki(self, naga_harness):
        """Harness provides Vasuki via Protocol."""
        vasuki = naga_harness.vasuki
        assert vasuki is not None

    def test_harness_registers_13_protocols(self, naga_harness):
        """Harness registers all 13 NAGA protocols."""
        protocols = naga_harness.get_registered_protocols()
        assert len(protocols) == 13


class TestServiceRegistryIntegration:
    """Verify ServiceRegistry is used correctly."""

    def test_protocols_registered_in_registry(self, naga_harness):
        """Protocols are registered via ServiceRegistry."""
        assert ServiceRegistry.is_registered(SeshaProtocol)
        assert ServiceRegistry.is_registered(TakshakaProtocol)
        assert ServiceRegistry.is_registered(VasukiProtocol)

    def test_get_from_registry_same_as_harness(self, naga_harness):
        """Getting from registry returns same as harness property."""
        registry_sesha = ServiceRegistry.get(SeshaProtocol)
        harness_sesha = naga_harness.sesha
        # Both should be the same NullSesha instance
        assert registry_sesha is harness_sesha

    def test_registry_isolated_after_context(self):
        """Registry is reset after harness context exits."""
        from vibe_core.naga.testing import NagaTestHarness

        with NagaTestHarness() as harness:
            assert ServiceRegistry.is_registered(SeshaProtocol)

        # After context, should be reset
        assert not ServiceRegistry.is_registered(SeshaProtocol)


class TestMinimalHarness:
    """Test minimal harness configuration."""

    def test_minimal_has_core_nagas(self, naga_harness_minimal):
        """Minimal harness has Sesha, Takshaka, Vasuki."""
        assert naga_harness_minimal.sesha is not None
        assert naga_harness_minimal.takshaka is not None
        assert naga_harness_minimal.vasuki is not None

    def test_minimal_has_only_3_protocols(self, naga_harness_minimal):
        """Minimal harness only registers 3 protocols."""
        protocols = naga_harness_minimal.get_registered_protocols()
        assert len(protocols) == 3
        assert SeshaProtocol in protocols
        assert TakshakaProtocol in protocols
        assert VasukiProtocol in protocols

    def test_minimal_chitragupta_not_registered(self, naga_harness_minimal):
        """Minimal harness doesn't register Chitragupta."""
        assert not ServiceRegistry.is_registered(ChitraguptaProtocol)


class TestNoMagicMock:
    """Verify no MagicMock is used."""

    def test_sesha_is_not_mock(self, naga_harness):
        """Sesha is real NullSesha, not MagicMock."""
        from unittest.mock import MagicMock

        sesha = naga_harness.sesha
        assert not isinstance(sesha, MagicMock)
        assert "NullSesha" in type(sesha).__name__

    def test_takshaka_is_not_mock(self, naga_harness):
        """Takshaka is real NullTakshaka, not MagicMock."""
        from unittest.mock import MagicMock

        takshaka = naga_harness.takshaka
        assert not isinstance(takshaka, MagicMock)
        assert "NullTakshaka" in type(takshaka).__name__


class TestProtocolCompliance:
    """Verify NullObjects comply with Protocols."""

    def test_sesha_implements_protocol(self, naga_harness):
        """NullSesha implements SeshaProtocol."""
        sesha = naga_harness.sesha
        # These are Protocol methods
        assert callable(getattr(sesha, "get_top_hash", None))
        assert callable(getattr(sesha, "get_sequence", None))
        assert callable(getattr(sesha, "export_blocks", None))
        assert callable(getattr(sesha, "import_blocks", None))
        assert callable(getattr(sesha, "as_handler", None))

    def test_takshaka_implements_protocol(self, naga_harness):
        """NullTakshaka implements TakshakaProtocol."""
        takshaka = naga_harness.takshaka
        assert callable(getattr(takshaka, "get_status", None))
        assert callable(getattr(takshaka, "as_handler", None))


class TestOrchestratorHarness:
    """Test NagaTestHarness.for_orchestrator() factory."""

    def test_for_orchestrator_provides_ledger(self):
        """for_orchestrator() provides InMemoryLedger."""
        from vibe_core.naga.testing import NagaTestHarness

        with NagaTestHarness.for_orchestrator() as harness:
            ledger = harness.ledger
            assert ledger is not None
            # Verify it's a real ledger
            assert callable(getattr(ledger, "record_event", None))
            assert callable(getattr(ledger, "count_events", None))
            # InMemoryLedger starts empty
            assert ledger.count_events() == 0

    def test_for_orchestrator_provides_correction_orchestrator(self):
        """for_orchestrator() provides NullCorrectionOrchestrator."""
        from vibe_core.naga.testing import NagaTestHarness

        with NagaTestHarness.for_orchestrator() as harness:
            correction = harness.correction_orchestrator
            assert correction is not None
            # Verify it has dispatcher
            assert hasattr(correction, "dispatcher")
            assert hasattr(correction, "registry")

    def test_for_orchestrator_provides_bootstrap_dependencies(self):
        """for_orchestrator() provides ledger and correction_orchestrator."""
        from vibe_core.naga.testing import NagaTestHarness

        with NagaTestHarness.for_orchestrator() as harness:
            # Both dependencies are available
            ledger = harness.ledger
            correction = harness.correction_orchestrator

            # Ledger has working API
            event_id = ledger.record_event("TEST", "test-agent", {"key": "value"})
            assert event_id is not None
            assert ledger.count_events() == 1

            # CorrectionOrchestrator has dispatcher
            assert correction.dispatcher is not None
            assert correction.registry is not None

    def test_ledger_without_config_raises(self):
        """Accessing ledger without enable_ledger=True raises."""
        from vibe_core.naga.testing import NagaTestHarness
        import pytest

        with NagaTestHarness() as harness:
            with pytest.raises(RuntimeError, match="Ledger not enabled"):
                _ = harness.ledger

    def test_correction_orchestrator_without_config_raises(self):
        """Accessing correction_orchestrator without config raises."""
        from vibe_core.naga.testing import NagaTestHarness
        import pytest

        with NagaTestHarness() as harness:
            with pytest.raises(RuntimeError, match="CorrectionOrchestrator not enabled"):
                _ = harness.correction_orchestrator
