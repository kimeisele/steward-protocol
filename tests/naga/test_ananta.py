"""
Tests for AnantaService - The Gene Splicer (12th Lord).

RED TESTS (TDD) - These should FAIL until AnantaService is implemented.

Verifies:
- Service analysis and classification
- FloodProposal generation
- Prahlad's Veto mechanism (Check and Balance)
- Soft Flood (Mixin) class creation
- isinstance preservation (DNA approach)
"""

import pytest

from vibe_core.naga.services.ananta import AnantaService
from vibe_core.protocols.naga import (
    AnantaProtocol,
    FloodProposal,
    NullAnanta,
    ServiceClassification,
    VetoDecision,
)

# =============================================================================
# Test Fixtures - Example services to analyze
# =============================================================================


class ExampleRebelService:
    """A service-like class without NAGA integration - should be FLOODED."""

    def __init__(self, database, logger):
        self.database = database
        self.logger = logger

    def save_state(self, data: dict) -> None:
        """Writes to database - needs Sesha."""
        self.database.write(data)

    def validate_user(self, token: str) -> bool:
        """Auth logic - needs Takshaka."""
        return token.startswith("valid_")


class ExampleCivilianClass:
    """A pure utility class - should be VETOED (overhead not justified)."""

    @staticmethod
    def format_name(first: str, last: str) -> str:
        return f"{first} {last}"

    @staticmethod
    def calculate_sum(a: int, b: int) -> int:
        return a + b


class ExampleFloodedService:
    """Already has @naga_service - should be SKIPPED."""

    _naga_manifest = {"name": "Example", "lord": "sesha"}  # Simulates decorator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def ananta():
    """Create an AnantaService for testing."""
    return AnantaService()


# =============================================================================
# NullAnanta Tests (Sanity checks)
# =============================================================================


class TestNullAnanta:
    """Tests for the Null implementation."""

    def test_null_ananta_classifies_as_civilian(self):
        """NullAnanta should classify everything as CIVILIAN."""
        ananta = NullAnanta()
        proposal = ananta.analyze_service(ExampleRebelService)

        assert proposal.classification == ServiceClassification.CIVILIAN
        assert proposal.proposed_nagas == []

    def test_null_ananta_auto_vetoes(self):
        """NullAnanta should auto-veto all proposals."""
        ananta = NullAnanta()
        proposal = FloodProposal(
            service_name="Test",
            service_path="test.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha"],
            proposed_mixins=["SeshaMixin"],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )

        decision = ananta.request_approval(proposal)
        assert decision.approved is False

    def test_null_ananta_returns_original_class(self):
        """NullAnanta should return class unchanged."""
        ananta = NullAnanta()
        proposal = FloodProposal(
            service_name="Test",
            service_path="test.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=[],
            proposed_mixins=[],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )
        decision = VetoDecision(proposal=proposal, approved=True, reason="Test")

        result = ananta.create_flooded_class(ExampleRebelService, decision)
        assert result is ExampleRebelService


# =============================================================================
# RED TESTS - Will fail until AnantaService is implemented
# =============================================================================


class TestAnantaServiceAnalysis:
    """Tests for service analysis - RED until implemented."""

    def test_classifies_rebel_service(self, ananta):
        """Should classify service-like classes as REBEL."""
        proposal = ananta.analyze_service(ExampleRebelService)

        assert proposal.classification == ServiceClassification.REBEL
        assert proposal.service_name == "ExampleRebelService"

    def test_detects_sesha_need_from_state_mutation(self, ananta):
        """Should detect Sesha need from save_state method."""
        proposal = ananta.analyze_service(ExampleRebelService)

        assert "sesha" in proposal.proposed_nagas
        assert "SeshaMixin" in proposal.proposed_mixins

    def test_detects_takshaka_need_from_auth_logic(self, ananta):
        """Should detect Takshaka need from validate_user method."""
        proposal = ananta.analyze_service(ExampleRebelService)

        assert "takshaka" in proposal.proposed_nagas

    def test_classifies_civilian_class(self, ananta):
        """Should classify utility classes as CIVILIAN."""
        proposal = ananta.analyze_service(ExampleCivilianClass)

        assert proposal.classification == ServiceClassification.CIVILIAN
        assert proposal.proposed_nagas == []

    def test_classifies_flooded_service(self, ananta):
        """Should classify @naga_service decorated as FLOODED."""
        proposal = ananta.analyze_service(ExampleFloodedService)

        assert proposal.classification == ServiceClassification.FLOODED


class TestPrahladVeto:
    """Tests for Prahlad's Veto mechanism - RED until implemented."""

    def test_prahlad_approves_rebel(self, ananta):
        """Prahlad should APPROVE flooding REBEL services."""
        proposal = FloodProposal(
            service_name="RebelService",
            service_path="services/rebel.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha", "takshaka"],
            proposed_mixins=["SeshaMixin", "TakshakaMixin"],
            reason="Service-like class needs NAGA integration",
            overhead_estimate="medium",
            risk_level="low",
        )

        decision = ananta.request_approval(proposal)

        assert decision.approved is True
        assert "REBEL" in decision.reason or "approved" in decision.reason.lower()

    def test_prahlad_vetoes_civilian(self, ananta):
        """Prahlad should VETO flooding CIVILIAN classes."""
        proposal = FloodProposal(
            service_name="UtilityClass",
            service_path="utils/helper.py",
            classification=ServiceClassification.CIVILIAN,
            proposed_nagas=["chitragupta"],
            proposed_mixins=["ChitraguptaMixin"],
            reason="Utility class",
            overhead_estimate="high",
            risk_level="low",
        )

        decision = ananta.request_approval(proposal)

        assert decision.approved is False
        assert "CIVILIAN" in decision.reason or "veto" in decision.reason.lower()

    def test_prahlad_skips_flooded(self, ananta):
        """Prahlad should SKIP already FLOODED services."""
        proposal = FloodProposal(
            service_name="AlreadyFlooded",
            service_path="services/flooded.py",
            classification=ServiceClassification.FLOODED,
            proposed_nagas=[],
            proposed_mixins=[],
            reason="Already has @naga_service",
            overhead_estimate="none",
            risk_level="none",
        )

        decision = ananta.request_approval(proposal)

        # FLOODED should not be approved (nothing to do)
        assert decision.approved is False
        assert "FLOODED" in decision.reason or "skip" in decision.reason.lower()

    def test_prahlad_can_override_nagas(self, ananta):
        """Prahlad can modify the proposed NAGA list."""
        proposal = FloodProposal(
            service_name="OverrideTest",
            service_path="services/override.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha", "takshaka", "chitragupta", "narada"],
            proposed_mixins=["SeshaMixin", "TakshakaMixin", "ChitraguptaMixin", "NaradaMixin"],
            reason="Test override",
            overhead_estimate="high",
            risk_level="medium",
        )

        decision = ananta.request_approval(proposal)

        # Prahlad might reduce the list due to high overhead
        if decision.override_nagas is not None:
            assert len(decision.override_nagas) <= len(proposal.proposed_nagas)


class TestSoftFlood:
    """Tests for Soft Flood (Mixin/DNA) class creation - RED until implemented."""

    def test_creates_flooded_class(self, ananta):
        """Should create a new class with Mixin inheritance."""
        proposal = FloodProposal(
            service_name="ExampleRebelService",
            service_path="test.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha"],
            proposed_mixins=["SeshaMixin"],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )
        decision = VetoDecision(proposal=proposal, approved=True, reason="Approved")

        flooded_class = ananta.create_flooded_class(ExampleRebelService, decision)

        # Must be a different class
        assert flooded_class is not ExampleRebelService
        # But must still pass isinstance
        assert issubclass(flooded_class, ExampleRebelService)

    def test_isinstance_preserved(self, ananta):
        """The DNA approach MUST preserve isinstance checks."""
        proposal = FloodProposal(
            service_name="ExampleRebelService",
            service_path="test.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha"],
            proposed_mixins=["SeshaMixin"],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )
        decision = VetoDecision(proposal=proposal, approved=True, reason="Approved")

        flooded_class = ananta.create_flooded_class(ExampleRebelService, decision)

        # Create instance and verify isinstance
        instance = flooded_class(database=None, logger=None)
        assert isinstance(instance, ExampleRebelService)

    def test_rejects_unapproved_decision(self, ananta):
        """Should raise ValueError if decision is not approved."""
        proposal = FloodProposal(
            service_name="Test",
            service_path="test.py",
            classification=ServiceClassification.CIVILIAN,
            proposed_nagas=[],
            proposed_mixins=[],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )
        decision = VetoDecision(proposal=proposal, approved=False, reason="Vetoed")

        with pytest.raises(ValueError):
            ananta.create_flooded_class(ExampleRebelService, decision)

    def test_flooded_class_has_naga_capabilities(self, ananta):
        """Flooded class should have NAGA Mixin capabilities."""
        proposal = FloodProposal(
            service_name="ExampleRebelService",
            service_path="test.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha"],
            proposed_mixins=["SeshaMixin"],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )
        decision = VetoDecision(proposal=proposal, approved=True, reason="Approved")

        flooded_class = ananta.create_flooded_class(ExampleRebelService, decision)

        # Should have Mixin in MRO
        mro_names = [c.__name__ for c in flooded_class.__mro__]
        assert any("Mixin" in name for name in mro_names)


class TestFloodHistory:
    """Tests for flood history tracking - RED until implemented."""

    def test_tracks_flood_decisions(self, ananta):
        """Should track all flood decisions."""
        proposal = FloodProposal(
            service_name="Test",
            service_path="test.py",
            classification=ServiceClassification.REBEL,
            proposed_nagas=["sesha"],
            proposed_mixins=["SeshaMixin"],
            reason="Test",
            overhead_estimate="low",
            risk_level="low",
        )

        ananta.request_approval(proposal)
        history = ananta.get_flood_history()

        assert len(history) >= 1
        assert history[-1].proposal.service_name == "Test"
