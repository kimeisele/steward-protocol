"""Tests for QuantumHealingResolver service."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vibe_core.protocols.correction import (
    DriftSeverity,
    DriftSource,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.vedic import AsharamaStage, VedicGovernanceProtocol
from vibe_core.services.healing_resolver import (
    DEFAULT_BHAKTI_MAX,
    DEFAULT_BHAKTI_OVERRIDE_THRESHOLD,
    QuantumHealingResolver,
    get_healing_resolver,
)

# =============================================================================
# Fixtures
# =============================================================================


class MockGovernance:
    """Mock VedicGovernanceProtocol for testing."""

    def __init__(
        self,
        ashrama: AsharamaStage = AsharamaStage.GRIHASTHA,
        bhakti: int = 0,
    ):
        self.ashrama = ashrama
        self.bhakti = bhakti

    def get_agent_ashrama(self, agent_id: str) -> AsharamaStage:
        return self.ashrama

    def get_bhakti_balance(self, agent_id: str) -> int:
        return self.bhakti


@pytest.fixture
def sample_drift() -> UnifiedDriftReport:
    """Create a sample drift for testing."""
    return UnifiedDriftReport(
        id="test_drift_1",
        source=DriftSource.STRUCTURAL,
        severity=DriftSeverity.WARNING,
        message="Test violation",
        file_path=Path("/fake/test.py"),
        rule_id="F401",
        auto_healable=True,
    )


@pytest.fixture
def brahmachari_governance() -> MockGovernance:
    """Governance for BRAHMACHARI (student) agent."""
    return MockGovernance(ashrama=AsharamaStage.BRAHMACHARI, bhakti=0)


@pytest.fixture
def grihastha_low_bhakti_governance() -> MockGovernance:
    """Governance for GRIHASTHA with low bhakti."""
    return MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=10)


@pytest.fixture
def grihastha_high_bhakti_governance() -> MockGovernance:
    """Governance for GRIHASTHA with high bhakti (>50)."""
    return MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=75)


@pytest.fixture
def sannyasa_governance() -> MockGovernance:
    """Governance for SANNYASA (daemon) agent."""
    return MockGovernance(ashrama=AsharamaStage.SANNYASA, bhakti=100)


# =============================================================================
# TestQuantumHealingResolver - Ashrama Stage Tests
# =============================================================================


class TestAsharamaStageResolution:
    """Tests for Ashrama stage-based resolution."""

    def test_brahmachari_always_dry_run(self, brahmachari_governance, sample_drift):
        """BRAHMACHARI (student) always gets DRY_RUN."""
        resolver = QuantumHealingResolver(governance=brahmachari_governance)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.DRY_RUN

    def test_sannyasa_always_dry_run(self, sannyasa_governance, sample_drift):
        """SANNYASA (daemon) always gets DRY_RUN."""
        resolver = QuantumHealingResolver(governance=sannyasa_governance)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.DRY_RUN

    def test_vanaprastha_can_earn_trust(self, sample_drift):
        """VANAPRASTHA (retiring) can still earn trust."""
        governance = MockGovernance(
            ashrama=AsharamaStage.VANAPRASTHA,
            bhakti=75,  # High bhakti
        )
        resolver = QuantumHealingResolver(governance=governance)

        result = resolver.resolve("test_agent", sample_drift)

        # High bhakti should yield MANUAL (not DRY_RUN like student/daemon)
        assert result == HealingStrategy.MANUAL


# =============================================================================
# TestQuantumHealingResolver - Bhakti Balance Tests
# =============================================================================


class TestBhaktiBalanceResolution:
    """Tests for Bhakti balance-based resolution."""

    def test_low_bhakti_dry_run(self, grihastha_low_bhakti_governance, sample_drift):
        """Low bhakti (<50) results in DRY_RUN."""
        resolver = QuantumHealingResolver(governance=grihastha_low_bhakti_governance)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.DRY_RUN

    def test_high_bhakti_manual(self, grihastha_high_bhakti_governance, sample_drift):
        """High bhakti (>=50) without resonance results in MANUAL."""
        # Use default reactor (high inertia = no manifestation)
        resolver = QuantumHealingResolver(governance=grihastha_high_bhakti_governance)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.MANUAL

    def test_bhakti_at_threshold(self, sample_drift):
        """Bhakti exactly at threshold yields MANUAL."""
        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=DEFAULT_BHAKTI_OVERRIDE_THRESHOLD,  # Exactly 50
        )
        resolver = QuantumHealingResolver(governance=governance)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.MANUAL

    def test_bhakti_just_below_threshold(self, sample_drift):
        """Bhakti just below threshold yields DRY_RUN."""
        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=DEFAULT_BHAKTI_OVERRIDE_THRESHOLD - 1,  # 49
        )
        resolver = QuantumHealingResolver(governance=governance)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.DRY_RUN

    def test_custom_bhakti_threshold(self, sample_drift):
        """Custom bhakti threshold is respected."""
        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=30,
        )
        # Custom threshold of 25 (lower than default 50)
        resolver = QuantumHealingResolver(
            governance=governance,
            bhakti_override_threshold=25,
        )

        result = resolver.resolve("test_agent", sample_drift)

        # 30 >= 25 threshold → MANUAL
        assert result == HealingStrategy.MANUAL


# =============================================================================
# TestQuantumHealingResolver - Quantum Resonance Tests
# =============================================================================


class TestQuantumResonanceResolution:
    """Tests for Quantum Reactor resonance-based resolution."""

    def test_high_resonance_auto(self, sample_drift):
        """High resonance (energy > inertia) yields AUTO."""
        from vibe_core.reactor.quantum import QuantumReactor

        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=100,
        )
        # Low inertia = easy to manifest
        reactor = QuantumReactor(initial_inertia=0.01)
        resolver = QuantumHealingResolver(governance=governance, reactor=reactor)

        result = resolver.resolve("test_agent", sample_drift)

        assert result == HealingStrategy.AUTO

    def test_low_resonance_no_auto(self, grihastha_high_bhakti_governance, sample_drift):
        """Low resonance (energy < inertia) does not yield AUTO."""
        from vibe_core.reactor.quantum import QuantumReactor

        # High inertia = hard to manifest
        reactor = QuantumReactor(initial_inertia=0.99)
        resolver = QuantumHealingResolver(
            governance=grihastha_high_bhakti_governance,
            reactor=reactor,
        )

        result = resolver.resolve("test_agent", sample_drift)

        # High bhakti but no manifestation → MANUAL (not AUTO)
        assert result == HealingStrategy.MANUAL


# =============================================================================
# TestQuantumHealingResolver - Trust Level Tests
# =============================================================================


class TestTrustLevel:
    """Tests for get_trust_level() calculation."""

    def test_brahmachari_zero_trust(self, brahmachari_governance):
        """BRAHMACHARI has 0 trust regardless of bhakti."""
        resolver = QuantumHealingResolver(governance=brahmachari_governance)

        trust = resolver.get_trust_level("test_agent")

        # 50% ashrama (0.0) + 50% bhakti (0/200) = 0.0
        assert trust == 0.0

    def test_grihastha_max_bhakti_full_trust(self):
        """GRIHASTHA with max bhakti has full trust."""
        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=DEFAULT_BHAKTI_MAX,  # 200
        )
        resolver = QuantumHealingResolver(governance=governance)

        trust = resolver.get_trust_level("test_agent")

        # 50% ashrama (1.0) + 50% bhakti (200/200) = 1.0
        assert trust == 1.0

    def test_grihastha_partial_bhakti(self):
        """GRIHASTHA with partial bhakti has proportional trust."""
        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=100,  # Half of max
        )
        resolver = QuantumHealingResolver(governance=governance)

        trust = resolver.get_trust_level("test_agent")

        # 50% ashrama (1.0) + 50% bhakti (100/200) = 0.75
        assert trust == 0.75

    def test_vanaprastha_reduced_trust(self):
        """VANAPRASTHA has reduced ashrama weight."""
        governance = MockGovernance(
            ashrama=AsharamaStage.VANAPRASTHA,
            bhakti=100,
        )
        resolver = QuantumHealingResolver(governance=governance)

        trust = resolver.get_trust_level("test_agent")

        # 50% ashrama (0.5) + 50% bhakti (100/200) = 0.5
        assert trust == 0.5

    def test_sannyasa_minimal_trust(self, sannyasa_governance):
        """SANNYASA has minimal ashrama weight."""
        resolver = QuantumHealingResolver(governance=sannyasa_governance)

        trust = resolver.get_trust_level("test_agent")

        # 50% ashrama (0.2) + 50% bhakti (100/200) = 0.35
        assert trust == 0.35

    def test_bhakti_capped_at_max(self):
        """Bhakti over max is capped at 1.0."""
        governance = MockGovernance(
            ashrama=AsharamaStage.GRIHASTHA,
            bhakti=500,  # Over max
        )
        resolver = QuantumHealingResolver(governance=governance)

        trust = resolver.get_trust_level("test_agent")

        # Bhakti normalized to 1.0, not 2.5
        assert trust == 1.0


# =============================================================================
# TestQuantumHealingResolver - Error Handling
# =============================================================================


class TestErrorHandling:
    """Tests for error handling and safe fallbacks."""

    def test_governance_error_safe_fallback(self, sample_drift):
        """Governance errors fall back to DRY_RUN."""
        # Create governance that raises on all calls
        governance = Mock(spec=VedicGovernanceProtocol)
        governance.get_agent_ashrama.side_effect = Exception("DB error")

        resolver = QuantumHealingResolver(governance=governance)

        result = resolver.resolve("test_agent", sample_drift)

        # Error → safe fallback to DRY_RUN
        assert result == HealingStrategy.DRY_RUN

    def test_bhakti_error_safe_fallback(self, sample_drift):
        """Bhakti lookup errors default to 0."""
        governance = Mock(spec=VedicGovernanceProtocol)
        governance.get_agent_ashrama.return_value = AsharamaStage.GRIHASTHA
        governance.get_bhakti_balance.side_effect = Exception("DB error")

        resolver = QuantumHealingResolver(governance=governance)

        result = resolver.resolve("test_agent", sample_drift)

        # Bhakti=0 (error fallback) → DRY_RUN
        assert result == HealingStrategy.DRY_RUN

    def test_trust_level_error_returns_zero(self):
        """Trust level errors return 0.0."""
        governance = Mock(spec=VedicGovernanceProtocol)
        governance.get_agent_ashrama.side_effect = Exception("Error")

        resolver = QuantumHealingResolver(governance=governance)

        trust = resolver.get_trust_level("test_agent")

        assert trust == 0.0


# =============================================================================
# TestQuantumHealingResolver - Factory Function
# =============================================================================


class TestFactory:
    """Tests for get_healing_resolver factory."""

    def test_factory_creates_resolver(self):
        """Factory creates a QuantumHealingResolver."""
        resolver = get_healing_resolver()

        assert isinstance(resolver, QuantumHealingResolver)

    def test_factory_with_custom_governance(self):
        """Factory accepts custom governance."""
        governance = MockGovernance(ashrama=AsharamaStage.BRAHMACHARI, bhakti=0)

        resolver = get_healing_resolver(governance=governance)

        assert resolver.governance == governance


# =============================================================================
# TestQuantumHealingResolver - Integration with Orchestrator
# =============================================================================


class TestOrchestratorIntegration:
    """Tests for integration with CorrectionOrchestrator."""

    def test_resonance_strategy_uses_resolver(self, sample_drift):
        """RESONANCE strategy delegates to resolver."""
        from vibe_core.protocols.correction import HealingResult, HealingStatus
        from vibe_core.services.correction_dispatcher import (
            BasicCorrectionDispatcher,
            BasicCorrectionOrchestrator,
            BasicDriftRegistry,
        )

        # Setup registry with detector
        registry = BasicDriftRegistry()
        registry.register_detector(
            DriftSource.STRUCTURAL,
            lambda: [sample_drift],
            "test_detector",
        )

        # Setup dispatcher with handler
        dispatcher = BasicCorrectionDispatcher()

        def mock_handler(drift, strategy):
            return HealingResult(
                drift_id=drift.id,
                status=(HealingStatus.HEALED if strategy == HealingStrategy.AUTO else HealingStatus.DEFERRED),
                handler_id="mock",
                message=f"Strategy was {strategy.value}",
            )

        dispatcher.register_handler(
            DriftSource.STRUCTURAL,
            mock_handler,
            "test_handler",
        )

        # Setup resolver that returns AUTO
        governance = MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=100)
        from vibe_core.reactor.quantum import QuantumReactor

        resolver = QuantumHealingResolver(
            governance=governance,
            reactor=QuantumReactor(initial_inertia=0.01),
        )

        # Create orchestrator
        orchestrator = BasicCorrectionOrchestrator(
            registry=registry,
            dispatcher=dispatcher,
            resolver=resolver,
            skip_default_init=True,
        )

        # Test RESONANCE strategy
        results = orchestrator.detect_and_heal(
            strategy=HealingStrategy.RESONANCE,
            agent_id="test_agent",
        )

        # Resolver should have returned AUTO, so handler should heal
        assert len(results) == 1
        assert results[0].healed
        assert "auto" in results[0].message.lower()

    def test_resonance_without_agent_id_falls_back(self, sample_drift):
        """RESONANCE without agent_id falls back to DRY_RUN."""
        from vibe_core.protocols.correction import HealingResult, HealingStatus
        from vibe_core.services.correction_dispatcher import (
            BasicCorrectionDispatcher,
            BasicCorrectionOrchestrator,
            BasicDriftRegistry,
        )

        registry = BasicDriftRegistry()
        registry.register_detector(
            DriftSource.STRUCTURAL,
            lambda: [sample_drift],
            "test",
        )

        dispatcher = BasicCorrectionDispatcher()
        dispatcher.register_handler(
            DriftSource.STRUCTURAL,
            lambda d, s: HealingResult(
                drift_id=d.id,
                status=HealingStatus.DEFERRED,
                handler_id="mock",
                message=f"Strategy: {s.value}",
            ),
            "test",
        )

        governance = MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=100)
        resolver = QuantumHealingResolver(governance=governance)

        orchestrator = BasicCorrectionOrchestrator(
            registry=registry,
            dispatcher=dispatcher,
            resolver=resolver,
            skip_default_init=True,
        )

        # RESONANCE without agent_id
        results = orchestrator.detect_and_heal(
            strategy=HealingStrategy.RESONANCE,
            agent_id=None,  # Missing!
        )

        # Should fall back to DRY_RUN
        assert len(results) == 1
        assert "dry_run" in results[0].message.lower()


# =============================================================================
# TestQuantumHealingResolver - Ledger Recording (OPUS-LZ3)
# =============================================================================


class TestLedgerRecording:
    """Tests for ledger audit trail (OPUS-LZ3)."""

    def test_resolve_records_to_ledger(self, sample_drift):
        """Resolve records decision to ledger when available."""
        from vibe_core.services.healing_resolver import ResonanceDecisionRecord

        # Mock ledger
        mock_ledger = Mock()
        mock_ledger.record_event = Mock()

        governance = MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=75)
        resolver = QuantumHealingResolver(
            governance=governance,
            ledger=mock_ledger,
        )

        resolver.resolve("test_agent", sample_drift)

        # Should have called record_event
        mock_ledger.record_event.assert_called_once()
        call_args = mock_ledger.record_event.call_args
        assert call_args.kwargs["event_type"] == "HEALING_RESONANCE"
        assert call_args.kwargs["agent_id"] == "test_agent"

        # Verify record details are typed (no Any)
        details = call_args.kwargs["details"]
        assert details["event"] == "RESONANCE_DECISION"
        assert details["drift_id"] == sample_drift.id
        assert details["strategy"] in ["dry_run", "manual", "auto"]
        assert isinstance(details["bhakti"], int)
        assert isinstance(details["bhakti_threshold"], int)

    def test_resolve_without_ledger_does_not_fail(self, sample_drift):
        """Resolve works without ledger (graceful degradation)."""
        governance = MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=10)
        resolver = QuantumHealingResolver(
            governance=governance,
            ledger=None,  # No ledger
        )

        # Should not raise
        result = resolver.resolve("test_agent", sample_drift)
        assert result == HealingStrategy.DRY_RUN

    def test_ledger_error_does_not_fail_resolve(self, sample_drift):
        """Ledger errors are caught and logged, not propagated."""
        mock_ledger = Mock()
        mock_ledger.record_event.side_effect = Exception("Ledger write failed")

        governance = MockGovernance(ashrama=AsharamaStage.GRIHASTHA, bhakti=75)
        resolver = QuantumHealingResolver(
            governance=governance,
            ledger=mock_ledger,
        )

        # Should not raise despite ledger error
        result = resolver.resolve("test_agent", sample_drift)
        assert result == HealingStrategy.MANUAL  # High bhakti

    def test_resonance_decision_record_is_typed(self):
        """ResonanceDecisionRecord is fully typed (no Any)."""
        from dataclasses import fields

        from vibe_core.services.healing_resolver import ResonanceDecisionRecord

        # All fields should have concrete types
        for field in fields(ResonanceDecisionRecord):
            assert field.type != "Any"
            assert "Any" not in str(field.type)
