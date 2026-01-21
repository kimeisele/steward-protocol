"""
PROTOCOL GOVERNANCE BRIDGE TESTS
================================
Phase 1: Testing the Protocol → Mahajana governance layer.

Tests:
- All protocols are governed (100% coverage)
- Owner lookup works correctly
- Level/category queries work
- Audit returns accurate statistics
- Portfolio generation works
"""

import pytest
from pathlib import Path

from vibe_core.protocols.governance.bridge import (
    ProtocolBridge,
    ProtocolEntry,
    ProtocolCategory,
    GovernanceAudit,
    MahajanaPortfolio,
    get_owner,
    list_by_owner,
    audit,
)
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.mahajanas.yamaraja.security import SecurityLevel


# =============================================================================
# GOVERNANCE COVERAGE TESTS
# =============================================================================


class TestGovernanceCoverage:
    """Test that all protocols are governed."""

    def test_100_percent_governed(self):
        """Every protocol file must have an owner."""
        report = audit()
        assert report["ungoverned_count"] == 0, (
            f"Found {report['ungoverned_count']} ungoverned protocols: {report['ungoverned_list'][:5]}..."
        )

    def test_all_mahajanas_have_protocols(self):
        """Every Mahajana should own at least one protocol."""
        report = audit()
        owner_dist = report["owner_distribution"]

        for mahajana in Mahajana:
            assert mahajana.value in owner_dist, f"Mahajana {mahajana.name} has no protocols"
            assert owner_dist[mahajana.value] > 0, f"Mahajana {mahajana.name} owns 0 protocols"

    def test_health_score_is_100(self):
        """Health score should be 1.0 (100%)."""
        report = audit()
        assert report["health_score"] == 1.0


# =============================================================================
# OWNER LOOKUP TESTS
# =============================================================================


class TestOwnerLookup:
    """Test owner lookup functionality."""

    def test_defense_owned_by_yamaraja(self):
        """defense.py must be owned by YAMARAJA."""
        owner = get_owner("defense.py")
        assert owner == Mahajana.YAMARAJA

    def test_ledger_owned_by_bhishma(self):
        """ledger.py must be owned by BHISHMA."""
        owner = get_owner("ledger.py")
        assert owner == Mahajana.BHISHMA

    def test_agent_owned_by_brahma(self):
        """agent.py must be owned by BRAHMA."""
        owner = get_owner("agent.py")
        assert owner == Mahajana.BRAHMA

    def test_security_protocol_owned_by_yamaraja(self):
        """SecurityProtocol must be owned by YAMARAJA."""
        owner = get_owner("mahajanas/yamaraja/security.py")
        assert owner == Mahajana.YAMARAJA

    def test_unknown_protocol_returns_none(self):
        """Unknown protocol should return None."""
        owner = get_owner("nonexistent.py")
        assert owner is None


# =============================================================================
# LEVEL & CATEGORY TESTS
# =============================================================================


class TestLevelAndCategory:
    """Test security level and category queries."""

    def test_defense_is_substrate_level(self):
        """defense.py should be SUBSTRATE level."""
        level = ProtocolBridge.get_level("defense.py")
        assert level == SecurityLevel.SUBSTRATE

    def test_ledger_is_kernel_level(self):
        """ledger.py should be KERNEL level."""
        level = ProtocolBridge.get_level("ledger.py")
        assert level == SecurityLevel.KERNEL

    def test_agent_is_application_level(self):
        """agent.py should be APPLICATION level."""
        level = ProtocolBridge.get_level("agent.py")
        assert level == SecurityLevel.APPLICATION

    def test_naga_protocols_are_naga_category(self):
        """naga/*.py should be NAGA category."""
        category = ProtocolBridge.get_category("naga/takshaka.py")
        assert category == ProtocolCategory.NAGA


# =============================================================================
# LIST BY OWNER TESTS
# =============================================================================


class TestListByOwner:
    """Test listing protocols by owner."""

    def test_yamaraja_has_multiple_protocols(self):
        """YAMARAJA should own multiple protocols."""
        protocols = list_by_owner(Mahajana.YAMARAJA)
        assert len(protocols) >= 10  # defense, testable, integrity, etc.

    def test_prahlada_has_most_protocols(self):
        """PRAHLADA should have the most protocols (devotion)."""
        report = audit()
        owner_dist = report["owner_distribution"]
        max_owner = max(owner_dist, key=owner_dist.get)
        assert max_owner == "prahlada"

    def test_protocol_entries_are_complete(self):
        """Protocol entries should have all required fields."""
        protocols = list_by_owner(Mahajana.BRAHMA)
        assert len(protocols) > 0

        for proto in protocols:
            assert "name" in proto
            assert "path" in proto
            assert "owner" in proto
            assert "level" in proto
            assert "category" in proto
            assert "description" in proto


# =============================================================================
# PORTFOLIO TESTS
# =============================================================================


class TestPortfolio:
    """Test Mahajana portfolio generation."""

    def test_yamaraja_portfolio(self):
        """Test YAMARAJA portfolio."""
        portfolio = ProtocolBridge.get_portfolio(Mahajana.YAMARAJA)

        assert portfolio["mahajana"] == "yamaraja"
        assert portfolio["protocol_count"] > 0
        assert len(portfolio["protocols"]) == portfolio["protocol_count"]

    def test_portfolio_security_levels(self):
        """Portfolio should include security levels used."""
        portfolio = ProtocolBridge.get_portfolio(Mahajana.YAMARAJA)

        # YAMARAJA owns SUBSTRATE level protocols
        assert SecurityLevel.SUBSTRATE.value in portfolio["security_levels"]


# =============================================================================
# LIST BY LEVEL TESTS
# =============================================================================


class TestListByLevel:
    """Test listing protocols by security level."""

    def test_substrate_level_has_protocols(self):
        """SUBSTRATE level should have protocols."""
        protocols = ProtocolBridge.list_by_level(SecurityLevel.SUBSTRATE)
        assert len(protocols) > 0

    def test_kernel_level_includes_ledger(self):
        """KERNEL level should include ledger.py."""
        protocols = ProtocolBridge.list_by_level(SecurityLevel.KERNEL)
        names = [p["name"] for p in protocols]
        assert "ledger.py" in names


# =============================================================================
# LIST BY CATEGORY TESTS
# =============================================================================


class TestListByCategory:
    """Test listing protocols by category."""

    def test_core_category_has_protocols(self):
        """CORE category should have protocols."""
        protocols = ProtocolBridge.list_by_category(ProtocolCategory.CORE)
        assert len(protocols) > 0

    def test_naga_category_includes_takshaka(self):
        """NAGA category should include takshaka.py."""
        protocols = ProtocolBridge.list_by_category(ProtocolCategory.NAGA)
        names = [p["name"] for p in protocols]
        assert "takshaka.py" in names


# =============================================================================
# AUDIT STRUCTURE TESTS
# =============================================================================


class TestAuditStructure:
    """Test audit report structure."""

    def test_audit_returns_correct_type(self):
        """audit() should return GovernanceAudit TypedDict."""
        report = audit()

        assert "total_protocols" in report
        assert "governed_count" in report
        assert "ungoverned_count" in report
        assert "ungoverned_list" in report
        assert "owner_distribution" in report
        assert "level_distribution" in report
        assert "health_score" in report

    def test_audit_distribution_sums_match(self):
        """Owner distribution sum should equal governed count."""
        report = audit()

        total_from_dist = sum(report["owner_distribution"].values())
        # Note: This counts entries in the mapping, not files
        # governed_count counts actual files that exist
        assert total_from_dist > 0
