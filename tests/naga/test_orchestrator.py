"""
Tests for NagaOrchestrator.

The Factory that bootstraps the NAGA Federation.

Tests:
- Bootstrap process
- Initialization order (Sesha -> Takshaka -> Vasuki)
- ServiceRegistry integration
- CorrectionDispatcher integration
- Config loading
"""

from unittest.mock import MagicMock, patch

import pytest


class TestBootstrap:
    """Test the bootstrap process."""

    @pytest.fixture
    def mock_ledger(self):
        """Create a mock ledger."""
        ledger = MagicMock()
        ledger.get_top_hash.return_value = "abc123"
        ledger.count_events.return_value = 100
        ledger.record_event.return_value = "event_123"
        return ledger

    @pytest.fixture
    def mock_correction_orchestrator(self):
        """Create a mock correction orchestrator."""
        orchestrator = MagicMock()
        orchestrator.dispatcher = MagicMock()
        orchestrator.dispatcher.register_handler = MagicMock()
        return orchestrator

    def test_bootstrap_returns_orchestrator(self, mock_ledger, mock_correction_orchestrator):
        """Bootstrap should return a NagaOrchestrator instance."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        assert isinstance(naga, NagaOrchestrator)
        assert naga._initialized is True

    def test_bootstrap_creates_all_nagas(self, mock_ledger, mock_correction_orchestrator):
        """Bootstrap should create all three NAGAs."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.naga.services.sesha import SeshaService
        from vibe_core.naga.services.takshaka import TakshakaService
        from vibe_core.naga.services.vasuki import VasukiService

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        assert isinstance(naga.sesha, SeshaService)
        assert isinstance(naga.takshaka, TakshakaService)
        assert isinstance(naga.vasuki, VasukiService)

    def test_bootstrap_registers_handlers(self, mock_ledger, mock_correction_orchestrator):
        """Bootstrap should register handlers with CorrectionDispatcher."""
        from vibe_core.naga import NagaOrchestrator

        NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        # Should register 6 handlers:
        # Infrastructure: Sesha (STATE), Takshaka (COGNITIVE), Vasuki (CONFIG), Kaliya (RELIABILITY)
        # Governance: Chitragupta (PERFORMANCE), Prahlad (STRUCTURAL)
        # NOTE: Narada is pure observer - no CorrectionHandler
        assert mock_correction_orchestrator.dispatcher.register_handler.call_count == 6

    def test_bootstrap_with_custom_config(self, mock_ledger, mock_correction_orchestrator):
        """Bootstrap should respect custom config."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig.permissive()
        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
            config=config,
        )

        assert naga.takshaka._trust_mode == "permissive"


class TestInitializationOrder:
    """Test that NAGAs are initialized in correct order."""

    @pytest.fixture
    def mock_ledger(self):
        ledger = MagicMock()
        ledger.get_top_hash.return_value = "abc123"
        ledger.count_events.return_value = 100
        return ledger

    @pytest.fixture
    def mock_correction_orchestrator(self):
        orchestrator = MagicMock()
        orchestrator.dispatcher = MagicMock()
        orchestrator.dispatcher.register_handler = MagicMock()
        return orchestrator

    def test_sesha_before_vasuki(self, mock_ledger, mock_correction_orchestrator):
        """Sesha must be initialized before Vasuki (Vasuki depends on Sesha)."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        # Vasuki should have reference to Sesha
        assert naga.vasuki._sesha is naga.sesha

    def test_takshaka_before_vasuki(self, mock_ledger, mock_correction_orchestrator):
        """Takshaka must be initialized before Vasuki."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        # Vasuki should have reference to Takshaka
        assert naga.vasuki._takshaka is naga.takshaka


class TestDisabledNagas:
    """Test behavior when NAGAs are disabled in config."""

    @pytest.fixture
    def mock_ledger(self):
        ledger = MagicMock()
        return ledger

    @pytest.fixture
    def mock_correction_orchestrator(self):
        orchestrator = MagicMock()
        orchestrator.dispatcher = MagicMock()
        return orchestrator

    def test_disabled_sesha(self, mock_ledger, mock_correction_orchestrator):
        """Disabled Sesha should be None."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        config.sesha.enabled = False

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
            config=config,
        )

        assert naga.sesha is None

    def test_disabled_takshaka(self, mock_ledger, mock_correction_orchestrator):
        """Disabled Takshaka should be None."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        config.takshaka.enabled = False

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
            config=config,
        )

        assert naga.takshaka is None

    def test_all_disabled(self, mock_ledger, mock_correction_orchestrator):
        """All disabled should still return valid orchestrator."""
        from vibe_core.naga import NagaOrchestrator
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig.disabled()

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
            config=config,
        )

        assert naga._initialized is True
        assert naga.sesha is None
        assert naga.vasuki is None
        assert naga.takshaka is None


class TestStatus:
    """Test status and health reporting."""

    @pytest.fixture
    def mock_ledger(self):
        ledger = MagicMock()
        ledger.get_top_hash.return_value = "abc123"
        ledger.count_events.return_value = 100
        return ledger

    @pytest.fixture
    def mock_correction_orchestrator(self):
        orchestrator = MagicMock()
        orchestrator.dispatcher = MagicMock()
        return orchestrator

    def test_get_status(self, mock_ledger, mock_correction_orchestrator):
        """get_status() should return status dict."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        status = naga.get_status()

        assert "initialized" in status
        assert "sesha" in status
        assert "vasuki" in status
        assert "takshaka" in status
        assert status["initialized"] is True

    def test_is_ready_when_all_healthy(self, mock_ledger, mock_correction_orchestrator):
        """is_ready() should return True when all NAGAs are healthy."""
        from vibe_core.naga import NagaOrchestrator

        naga = NagaOrchestrator.bootstrap(
            ledger=mock_ledger,
            correction_orchestrator=mock_correction_orchestrator,
        )

        assert naga.is_ready() is True

    def test_is_ready_false_when_not_initialized(self):
        """is_ready() should return False before initialization."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        naga = NagaOrchestrator()
        assert naga.is_ready() is False


class TestVisibilityMatrix:
    """Test the Visibility Matrix - NAGA's eyes at boot."""

    def test_progress_bar(self):
        """Progress bar generates correctly."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        naga = NagaOrchestrator()

        # 50% = 5 filled, 5 empty
        assert naga._progress_bar(50) == "█████░░░░░"
        # 0% = all empty
        assert naga._progress_bar(0) == "░░░░░░░░░░"
        # 100% = all filled
        assert naga._progress_bar(100) == "██████████"
        # 80% = 8 filled
        assert naga._progress_bar(80) == "████████░░"

    def test_build_matrix_display_with_empty_intel(self):
        """Matrix builds even with empty intelligence."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        naga = NagaOrchestrator()
        lines = naga._build_matrix_display({}, {}, [])

        # Should have header and at least summary
        assert len(lines) >= 3
        assert "COMPONENT" in lines[0]
        assert "COVERAGE" in lines[0]

    def test_build_matrix_display_with_intel(self):
        """Matrix shows coverage data correctly."""
        from vibe_core.naga.orchestrator import NagaOrchestrator

        naga = NagaOrchestrator()

        intel = {
            "total_testables": 50,
            "total_tests": 200,
            "by_type": {"AGENT": 10, "PLUGIN": 5},
            "tests_by_type": {"AGENT": 80, "PLUGIN": 30},
            "naga_coverage": {"tests_available": 420},
            "prahlad_stats": {
                "tests_generated": 5,
                "chaos_probes": 3,
                "dharma_audits": 2,
            },
        }

        lines = naga._build_matrix_display(intel, {}, ["silent_except", "path_scanning"])

        # Convert to string for easier assertion
        output = "\n".join(lines)

        # Should show NAGA Core
        assert "NAGA Core" in output
        # Should show component types
        assert "AGENT" in output
        assert "PLUGIN" in output
        # Should show totals
        assert "50 components" in output
        assert "200 tests" in output
        # Should show Shuddhi remedies
        assert "remedies available" in output
        # Should show Prahlad stats
        assert "PRAHLAD" in output

    def test_generate_boot_matrix_does_not_crash(self):
        """Boot matrix generation is resilient."""
        from unittest.mock import MagicMock

        from vibe_core.naga.orchestrator import NagaOrchestrator

        naga = NagaOrchestrator()
        # Should not crash even without Prahlad
        naga._prahlad = None
        naga._ananta = None

        # Should complete without exception
        naga._generate_boot_matrix()
