"""
Tests for AnantaService - The Gene Splicer + Loader Governor (12th Lord).

RED TESTS (TDD) - These should FAIL until AnantaService is implemented.

Verifies:
- Service analysis and classification
- FloodProposal generation
- Prahlad's Veto mechanism (Check and Balance)
- Soft Flood (Mixin) class creation
- isinstance preservation (DNA approach)
- **NEW: Loader Governance** - OUROBOROS on loaders
- **NEW: Boot Audit Trail** - What was loaded and when
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


# =============================================================================
# Loader Governance Tests (OUROBOROS on Loaders)
# =============================================================================


class TestLoaderGovernance:
    """Tests for loader governance - OUROBOROS on the loading layer."""

    def test_record_load_creates_event(self, ananta):
        """record_load should create a LoadEvent."""
        event_id = ananta.record_load(
            loader_type="test_loader",
            operation="discover",
            item_type="plugin",
            item_id="test_plugin",
            success=True,
            duration_ms=42.5,
        )

        assert event_id.startswith("load_")
        events = ananta.get_load_events(loader_type="test_loader")
        assert len(events) >= 1
        assert events[-1].item_id == "test_plugin"

    def test_record_load_tracks_failures(self, ananta):
        """record_load should track failed loads."""
        ananta.record_load(
            loader_type="test_loader",
            operation="load",
            item_type="plugin",
            item_id="broken_plugin",
            success=False,
            error="ImportError: No module named 'nonexistent'",
            duration_ms=10.0,
        )

        failed = ananta.get_failed_loads()
        assert len(failed) >= 1
        assert failed[-1].item_id == "broken_plugin"
        assert "ImportError" in failed[-1].error

    def test_load_stats_tracks_totals(self, ananta):
        """get_load_stats should track cumulative statistics."""
        # Record some loads
        ananta.record_load(
            loader_type="loader_a",
            operation="load",
            item_type="plugin",
            success=True,
            duration_ms=10.0,
        )
        ananta.record_load(
            loader_type="loader_b",
            operation="load",
            item_type="cartridge",
            success=True,
            duration_ms=20.0,
        )
        ananta.record_load(
            loader_type="loader_a",
            operation="load",
            item_type="plugin",
            success=False,
            error="Test error",
            duration_ms=5.0,
        )

        stats = ananta.get_load_stats()
        assert stats["total_loads"] >= 3
        assert stats["failed_loads"] >= 1
        assert stats["total_duration_ms"] >= 35.0
        assert "loader_a" in stats["loaders_tracked"]

    def test_get_boot_audit_provides_timeline(self, ananta):
        """get_boot_audit should provide a complete audit trail."""
        # Record multiple loads
        for i in range(5):
            ananta.record_load(
                loader_type="unified_loader",
                operation=f"load_{i}",
                item_type="section",
                item_id=f"section_{i}",
                success=True,
                duration_ms=float(i * 10),
            )

        audit = ananta.get_boot_audit()

        assert "stats" in audit
        assert "by_loader" in audit
        assert "timeline" in audit
        assert len(audit["timeline"]) >= 5

    def test_lru_eviction_limits_memory(self, ananta):
        """Events should be LRU evicted when exceeding max_events."""
        # Ananta has default max_events of 10000
        # Let's set a smaller limit for testing
        ananta._max_events = 5

        # Record more events than the limit
        for i in range(10):
            ananta.record_load(
                loader_type="test",
                operation="test",
                item_type="test",
                item_id=f"item_{i}",
                success=True,
            )

        # Should only have 5 events
        assert len(ananta._load_events) <= 5

    def test_filter_by_loader_type(self, ananta):
        """get_load_events should filter by loader_type."""
        ananta.record_load(
            loader_type="alpha",
            operation="load",
            item_type="a",
            success=True,
        )
        ananta.record_load(
            loader_type="beta",
            operation="load",
            item_type="b",
            success=True,
        )
        ananta.record_load(
            loader_type="alpha",
            operation="load",
            item_type="c",
            success=True,
        )

        alpha_events = ananta.get_load_events(loader_type="alpha")
        assert len(alpha_events) >= 2
        assert all(e.loader_type == "alpha" for e in alpha_events)

    def test_filter_by_item_id(self, ananta):
        """get_load_events should filter by item_id."""
        ananta.record_load(
            loader_type="test",
            operation="load",
            item_type="plugin",
            item_id="target_plugin",
            success=True,
        )
        ananta.record_load(
            loader_type="test",
            operation="reload",
            item_type="plugin",
            item_id="target_plugin",
            success=True,
        )
        ananta.record_load(
            loader_type="test",
            operation="load",
            item_type="plugin",
            item_id="other_plugin",
            success=True,
        )

        target_events = ananta.get_load_events(item_id="target_plugin")
        assert len(target_events) >= 2
        assert all(e.item_id == "target_plugin" for e in target_events)


class TestManifestRegistryWrapping:
    """Tests for ManifestRegistry wrapper governance."""

    def test_wrap_and_unwrap(self, ananta):
        """Should wrap and unwrap ManifestRegistry cleanly."""
        # Wrap
        ananta.wrap_manifest_registry()
        assert ananta._wrapped is True

        # Unwrap
        ananta.unwrap()
        assert ananta._wrapped is False

    def test_status_includes_loader_governance(self, ananta):
        """get_status should include loader governance info."""
        ananta.record_load(
            loader_type="test",
            operation="test",
            item_type="test",
            success=True,
        )

        status = ananta.get_status()
        assert status.events_processed >= 1
        assert "loads=" in status.message
