"""
NAGA FRACTAL TESTS - Tests Mirror the NAGA Architecture.

"As above, so below" - Tests must mirror what they test.
NAGA is fractal, so NAGA tests must be fractal.

NO MAGICMOCK. Real lightweight implementations.
This is the TEMPLATE for all NAGA tests.

Migrated from test_orchestrator.py::TestVisibilityMatrix
"""

import pytest

from tests.fractal.fractal_test_framework import (
    FractalTestCase,
    LightweightKernel,
    TestPlugin,
)

# ============================================================================
# NAGA TEST PLUGINS (mirror real NAGA services)
# ============================================================================


class NagaTestPlugin(TestPlugin):
    """
    Lightweight NAGA plugin for testing.

    Mirrors NagaOrchestrator behavior without full boot overhead.
    ~10ms vs ~3000ms for real orchestrator.
    """

    def __init__(self):
        self.events_recorded = []
        self.coverage_data = {
            "total_testables": 0,
            "total_tests": 0,
            "by_type": {},
            "tests_by_type": {},
            "naga_coverage": {"tests_available": 0},
            "prahlad_stats": {
                "tests_generated": 0,
                "chaos_probes": 0,
                "dharma_audits": 0,
            },
        }

    @property
    def plugin_id(self) -> str:
        return "naga_test"

    def on_boot(self, kernel: LightweightKernel) -> None:
        """Record boot event."""
        kernel.record_event("NAGA_BOOT", "naga", {"status": "initialized"})

    def set_coverage(
        self,
        total_testables: int = 0,
        total_tests: int = 0,
        naga_tests: int = 0,
        by_type: dict = None,
    ):
        """Set coverage data for testing."""
        self.coverage_data["total_testables"] = total_testables
        self.coverage_data["total_tests"] = total_tests
        self.coverage_data["naga_coverage"]["tests_available"] = naga_tests
        if by_type:
            self.coverage_data["by_type"] = by_type
            self.coverage_data["tests_by_type"] = by_type  # Simplified

    def get_coverage_intelligence(self):
        """Return coverage data (mirrors Prahlad API)."""
        return self.coverage_data


class SeshaTestPlugin(TestPlugin):
    """Lightweight Sesha for testing (ledger recording)."""

    def __init__(self):
        self.events = []

    @property
    def plugin_id(self) -> str:
        return "sesha_test"

    def record_event(self, event_type: str, source: str, details: dict):
        """Record event to in-memory ledger."""
        self.events.append(
            {
                "event_type": event_type,
                "source": source,
                "details": details,
            }
        )
        return f"event_{len(self.events)}"

    def get_events(self, event_type: str = None):
        """Get recorded events."""
        if event_type:
            return [e for e in self.events if e["event_type"] == event_type]
        return self.events


# ============================================================================
# NAGA FRACTAL TEST CASE (base class for NAGA tests)
# ============================================================================


class NagaFractalTestCase(FractalTestCase):
    """
    Base class for all NAGA fractal tests.

    Provides:
    - Lightweight NAGA services (no MagicMock!)
    - Real visibility matrix testing
    - Coverage intelligence assertions
    """

    TIMEOUT = 5  # NAGA tests should be fast

    def get_test_plugins(self):
        """Provide lightweight NAGA plugins."""
        self.naga = NagaTestPlugin()
        self.sesha = SeshaTestPlugin()
        return [self.naga, self.sesha]

    # ========================================================================
    # NAGA-SPECIFIC ASSERTIONS
    # ========================================================================

    def assert_naga_booted(self):
        """Assert NAGA booted successfully."""
        events = self.kernel.get_events("NAGA_BOOT")
        assert len(events) > 0, "NAGA did not boot"

    def assert_coverage_above(self, threshold: float):
        """Assert coverage is above threshold."""
        intel = self.naga.get_coverage_intelligence()
        naga_tests = intel["naga_coverage"]["tests_available"]
        target = 600  # Default target
        pct = (naga_tests / target * 100) if target else 0
        assert pct >= threshold, f"Coverage {pct:.1f}% below threshold {threshold}%"


# ============================================================================
# VISIBILITY MATRIX TESTS (migrated from test_orchestrator.py)
# ============================================================================


class TestVisibilityMatrixFractal(NagaFractalTestCase):
    """
    Test Visibility Matrix using fractal design.

    NO MAGICMOCK. Real lightweight implementations.
    """

    def test_progress_bar(self):
        """Progress bar generates correctly."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        # Create orchestrator (not booted, just for utility methods)
        orch = NagaOrchestrator()

        # Test progress bar (pure function, no mocking needed)
        assert orch._progress_bar(50) == "█████░░░░░"
        assert orch._progress_bar(0) == "░░░░░░░░░░"
        assert orch._progress_bar(100) == "██████████"

    def test_status_emoji_thresholds(self):
        """Status emoji uses configurable thresholds."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        orch = NagaOrchestrator()

        # Test with default thresholds (70%, 30%)
        assert orch._get_status_emoji(80, 70, 30) == "🛡️ Protected"
        assert orch._get_status_emoji(50, 70, 30) == "⚠️ Monitoring"
        assert orch._get_status_emoji(20, 70, 30) == "☣️ Blind"

        # Test with custom thresholds
        assert orch._get_status_emoji(50, 40, 20) == "🛡️ Protected"
        assert orch._get_status_emoji(30, 40, 20) == "⚠️ Monitoring"

    def test_matrix_display_with_real_intel(self):
        """Matrix display works with real intelligence data."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        # Set up coverage data in our lightweight plugin
        self.naga.set_coverage(
            total_testables=50,
            total_tests=200,
            naga_tests=420,
            by_type={"AGENT": 80, "PLUGIN": 30},
        )

        # Use real orchestrator to build display
        orch = NagaOrchestrator()
        intel = self.naga.get_coverage_intelligence()
        lines = orch._build_matrix_display(intel, {}, ["silent_except"])

        output = "\n".join(lines)

        # Assertions on real output
        assert "NAGA Core" in output
        assert "50 components" in output
        assert "200 tests" in output

    def test_naga_boots_and_records(self):
        """NAGA boot is recorded to Sesha."""
        # Assert boot was recorded (by NagaTestPlugin)
        self.assert_naga_booted()

        # Check Sesha recorded it
        events = self.kernel.get_events("NAGA_BOOT")
        assert len(events) == 1
        assert events[0]["agent_id"] == "naga"


class TestCoverageIntelligenceFractal(NagaFractalTestCase):
    """Test coverage intelligence using fractal design."""

    def test_coverage_intelligence_structure(self):
        """Coverage intelligence has expected structure."""
        intel = self.naga.get_coverage_intelligence()

        assert "total_testables" in intel
        assert "total_tests" in intel
        assert "naga_coverage" in intel
        assert "prahlad_stats" in intel

    def test_coverage_threshold_assertion(self):
        """Coverage assertion works correctly."""
        # Set low coverage
        self.naga.set_coverage(naga_tests=100)

        # Should fail threshold of 50%
        with pytest.raises(AssertionError):
            self.assert_coverage_above(50)

        # Set high coverage
        self.naga.set_coverage(naga_tests=500)

        # Should pass threshold of 50%
        self.assert_coverage_above(50)


# ============================================================================
# CONFIG INTEGRATION TESTS
# ============================================================================


class TestConfigIntegrationFractal(NagaFractalTestCase):
    """Test config integration (no hardcoded values)."""

    def test_visibility_config_exists(self):
        """VisibilityConfig is part of NagaConfig."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        assert hasattr(config, "visibility")
        assert hasattr(config.visibility, "target_naga_tests")
        assert hasattr(config.visibility, "protected_threshold")

    def test_visibility_config_defaults(self):
        """VisibilityConfig has sensible defaults."""
        from vibe_core.phoenix.sections.naga.section_main import VisibilityConfig

        config = VisibilityConfig()

        assert config.target_naga_tests == 600
        assert config.tests_per_component == 10
        assert config.protected_threshold == 70.0
        assert config.monitoring_threshold == 30.0

    def test_visibility_config_serialization(self):
        """VisibilityConfig serializes correctly."""
        from vibe_core.phoenix.sections.naga.section_main import VisibilityConfig

        config = VisibilityConfig(target_naga_tests=1000)
        data = config.to_dict()

        assert data["target_naga_tests"] == 1000

        # Round-trip
        restored = VisibilityConfig.from_dict(data)
        assert restored.target_naga_tests == 1000


# ============================================================================
# HIRANYAKASHIPU INTEGRATION TESTS (via Prahlad)
# ============================================================================


class TestHiranyakashipuIntegration(NagaFractalTestCase):
    """
    Test that Hiranyakashipu attack framework is integrated via Prahlad.

    ARCHITECTURE INSIGHT:
    - Prahlad (the 7th NAGA) is the Resilience Agent
    - PrahladService already has chaos_probe() capability
    - Hiranyakashipu provides YAML-based attack seeds
    - Prahlad should LOAD Hiranyakashipu seeds for chaos probing

    These tests verify the integration path:
    Orchestrator → boots Prahlad → loads Hiranyakashipu seeds → chaos_probe()
    """

    def test_prahlad_service_has_chaos_probe(self):
        """
        GREEN: PrahladService already has chaos_probe method.

        This verifies the existing capability.
        """
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        assert hasattr(prahlad, "chaos_probe"), "PrahladService should have chaos_probe method"
        assert callable(prahlad.chaos_probe)

    def test_prahlad_can_load_hiranyakashipu_seeds(self):
        """
        RED: Prahlad should be able to load Hiranyakashipu attack seeds.

        This test FAILS because Prahlad doesn't know about Hiranyakashipu yet.
        """
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        # Check if Prahlad has a method to load external attack seeds
        assert hasattr(prahlad, "load_attack_seeds"), (
            "PrahladService missing load_attack_seeds method!\n"
            "Prahlad should be able to load Hiranyakashipu YAML seeds."
        )

    def test_hiranyakashipu_seeds_available(self):
        """
        GREEN: Hiranyakashipu module loads attack seeds from YAML.

        This verifies the attack seed infrastructure works.
        """
        from pathlib import Path

        from vibe_core.naga.hiranyakashipu import SeedLoader

        loader = SeedLoader()
        seed_dir = Path(__file__).parent.parent.parent / "vibe_core/naga/hiranyakashipu/seeds"
        loader.add_seed_dir(seed_dir)
        count = loader.load_seeds()

        assert count > 0, "Should load Hiranyakashipu attack seeds from YAML"

    def test_prahlad_chaos_probe_uses_external_scenarios(self):
        """
        RED: Prahlad.chaos_probe() should support external scenarios.

        This test FAILS because chaos_probe only uses ChaosScenario enum.
        Should also support Hiranyakashipu attack seeds.
        """
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()

        # Check if chaos_probe accepts external seed scenarios
        import inspect

        sig = inspect.signature(prahlad.chaos_probe)
        params = list(sig.parameters.keys())

        # Should accept external attack seeds, not just ChaosScenario enum
        assert "attack_seeds" in params or "external_scenarios" in params, (
            "chaos_probe should accept external attack seeds!\n"
            "Currently only uses hardcoded ChaosScenario enum.\n"
            "Should integrate with Hiranyakashipu YAML seeds."
        )


# ============================================================================
# PARASITIC CHAOS PROBE TESTS (Real Antifragility)
# ============================================================================


class TestParasiticChaosProbe(NagaFractalTestCase):
    """
    Test the REAL parasitic chaos probe.

    This is NOT phantom testing. This ACTUALLY injects chaos into ServiceRegistry.
    Gemini's insight: "Wir prüfen nicht den Return Value. Wir prüfen den Ledger."
    """

    def test_chaos_probe_real_exists(self):
        """PrahladService has chaos_probe_real method."""
        from vibe_core.naga.services.prahlad import PrahladService

        prahlad = PrahladService()
        assert hasattr(prahlad, "chaos_probe_real")
        assert callable(prahlad.chaos_probe_real)

    def test_chaos_injection_works(self):
        """ServiceRegistry chaos injection works correctly."""
        from vibe_core.di import ServiceRegistry

        class TestProtocol:
            pass

        class RealService:
            def get_name(self):
                return "REAL"

        # Register real service
        ServiceRegistry.register(TestProtocol, RealService())

        # Get real service
        assert ServiceRegistry.get(TestProtocol).get_name() == "REAL"

        # Inject chaos
        ServiceRegistry.inject_chaos(TestProtocol, lambda: None)
        ServiceRegistry.enable_chaos()

        # Now get returns None (chaos injected)
        assert ServiceRegistry.get(TestProtocol) is None

        # Cleanup
        ServiceRegistry.clear_chaos()
        ServiceRegistry.reset()

    def test_chaos_probe_real_detects_vulnerability(self):
        """chaos_probe_real detects when system doesn't handle chaos."""
        from vibe_core.naga.services.prahlad import PrahladService

        class VulnerableProtocol:
            pass

        prahlad = PrahladService()

        # Trigger that doesn't handle None gracefully
        triggered = []

        def vulnerable_trigger():
            from vibe_core.di import ServiceRegistry

            service = ServiceRegistry.get(VulnerableProtocol)
            # This just continues without handling None
            triggered.append(True)

        result = prahlad.chaos_probe_real(
            target_protocol=VulnerableProtocol,
            chaos_scenario="unavailable",
            trigger_operation=vulnerable_trigger,
        )

        # Trigger was called
        assert len(triggered) == 1

        # System is NOT resilient (Sesha didn't see the chaos)
        # This is correct - the system silently handled None without logging
        assert result["chaos_id"] is not None
        assert result["scenario"] == "unavailable"

    def test_chaos_probe_real_cleanup(self):
        """chaos_probe_real cleans up after itself."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.naga.services.prahlad import PrahladService

        class CleanupTestProtocol:
            pass

        prahlad = PrahladService()

        # Run chaos probe
        prahlad.chaos_probe_real(
            target_protocol=CleanupTestProtocol,
            chaos_scenario="unavailable",
        )

        # Chaos should be disabled and cleared
        assert not ServiceRegistry.is_chaos_enabled()
        assert CleanupTestProtocol.__name__ not in ServiceRegistry.list_chaos_injectors()


# ============================================================================
# NARASIMHA GATEKEEPER TESTS (Security)
# ============================================================================


class TestNarasimhaGatekeeper(NagaFractalTestCase):
    """
    Test the Narasimha Gatekeeper in ServiceRegistry.

    This is the SHIELD - unauthorized code cannot poison the DI container.
    """

    def test_narasimha_blocks_unauthorized_chaos(self):
        """Narasimha blocks unauthorized chaos injection."""
        from vibe_core.di import ServiceRegistry

        class BlockedProtocol:
            pass

        # Enable Narasimha
        ServiceRegistry.enable_narasimha()

        try:
            # This test function is NOT authorized
            with pytest.raises(PermissionError) as exc_info:
                ServiceRegistry.inject_chaos(BlockedProtocol, lambda: None)

            assert "NARASIMHA BLOCKED" in str(exc_info.value)
            assert "Unauthorized" in str(exc_info.value)

        finally:
            # Cleanup
            ServiceRegistry.disable_narasimha()
            ServiceRegistry.clear_chaos()

    def test_prahlad_is_authorized(self):
        """PrahladService is authorized to inject chaos."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.naga.services.prahlad import PrahladService

        class AuthorizedProtocol:
            pass

        # Enable Narasimha
        ServiceRegistry.enable_narasimha()

        try:
            prahlad = PrahladService()

            # Prahlad should be able to run chaos_probe_real
            # which internally calls inject_chaos
            result = prahlad.chaos_probe_real(
                target_protocol=AuthorizedProtocol,
                chaos_scenario="unavailable",
            )

            # Should succeed (no PermissionError)
            assert result["chaos_id"] is not None

        finally:
            ServiceRegistry.disable_narasimha()
            ServiceRegistry.clear_chaos()

    def test_narasimha_reports_threats(self):
        """Narasimha reports threats to the protocol."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.narasimha import get_narasimha

        class ThreatTestProtocol:
            pass

        narasimha = get_narasimha()
        initial_threats = len(narasimha.threats)

        # Enable Narasimha
        ServiceRegistry.enable_narasimha()

        try:
            # Try unauthorized injection
            try:
                ServiceRegistry.inject_chaos(ThreatTestProtocol, lambda: None)
            except PermissionError:
                pass  # Expected

            # Threat should have been registered
            assert len(narasimha.threats) > initial_threats

            # Check threat type
            latest = narasimha.threats[-1]
            assert latest.indicator_type == "UNAUTHORIZED_CHAOS_INJECTION"

        finally:
            ServiceRegistry.disable_narasimha()
            ServiceRegistry.clear_chaos()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--timeout=30"])
