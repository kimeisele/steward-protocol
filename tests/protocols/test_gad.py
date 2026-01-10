"""
Tests for GAD-000 - The Operator Inversion Principle
====================================================

If it does not exist as protocol, it does not exist.
"""

import pytest
from vibe_core.protocols.gad import (
    # Criteria
    GADCriterion,
    KSHETRA_SIZE,
    CRITERIA_COUNT,
    # The 37th
    KSHETRAJNA,
    # Dharma
    DharmaPrinciple,
    DHARMA_COUNT,
    # Heartbeat
    MantraHeartbeat,
    # Compliance
    GAD000Audit,
    # Formula
    legitimacy_formula,
)


class TestGADCriterion:
    """Test the 6 operational criteria."""

    def test_six_criteria(self):
        """There are exactly 6 criteria."""
        assert len(GADCriterion) == 6
        assert CRITERIA_COUNT == 6

    def test_criteria_values(self):
        """Criteria have correct values."""
        assert GADCriterion.DISCOVERABILITY == 0
        assert GADCriterion.OBSERVABILITY == 1
        assert GADCriterion.PARSEABILITY == 2
        assert GADCriterion.COMPOSABILITY == 3
        assert GADCriterion.IDEMPOTENCY == 4
        assert GADCriterion.RECOVERABILITY == 5

    def test_kshetra_is_36(self):
        """The field (kshetra) is 36 cells (6×6)."""
        assert KSHETRA_SIZE == 36
        assert KSHETRA_SIZE == CRITERIA_COUNT * CRITERIA_COUNT


class TestThe37th:
    """Test the 37th Principle."""

    def test_kshetrajna_is_37(self):
        """The knower of the field is the 37th."""
        assert KSHETRAJNA == 37

    def test_36_plus_1_equals_37(self):
        """36 + 1 = 37."""
        assert KSHETRA_SIZE + 1 == KSHETRAJNA


class TestDharmaPrinciples:
    """Test the 4 regulating principles."""

    def test_four_principles(self):
        """There are exactly 4 dharma principles."""
        assert len(DharmaPrinciple) == 4
        assert DHARMA_COUNT == 4

    def test_principle_values(self):
        """Principles have correct values."""
        assert DharmaPrinciple.DAYA == 0      # Mercy
        assert DharmaPrinciple.SATYAM == 1   # Truthfulness
        assert DharmaPrinciple.TAPAS == 2    # Austerity
        assert DharmaPrinciple.SAUCAM == 3   # Cleanliness


class TestLegitimacyFormula:
    """Test the legitimacy formula: (36 ∩ 4) × Signature₃₇"""

    def test_full_compliance(self):
        """Full compliance = 1.0."""
        result = legitimacy_formula(36, 4, True)
        assert result == 1.0

    def test_no_signature_is_zero(self):
        """Without signature, legitimacy is 0."""
        result = legitimacy_formula(36, 4, False)
        assert result == 0.0

    def test_no_dharma_is_zero(self):
        """Without dharma, legitimacy is 0."""
        result = legitimacy_formula(36, 0, True)
        assert result == 0.0

    def test_no_kshetra_is_zero(self):
        """Without kshetra, legitimacy is 0."""
        result = legitimacy_formula(0, 4, True)
        assert result == 0.0

    def test_partial_compliance(self):
        """Partial compliance is proportional."""
        result = legitimacy_formula(18, 2, True)  # Half of each
        assert result == 0.5

    def test_intersection_takes_minimum(self):
        """Intersection uses minimum of ratios."""
        # 36/36 = 1.0, 2/4 = 0.5 → min = 0.5
        result = legitimacy_formula(36, 2, True)
        assert result == 0.5

        # 18/36 = 0.5, 4/4 = 1.0 → min = 0.5
        result = legitimacy_formula(18, 4, True)
        assert result == 0.5


class TestGAD000Audit:
    """Test the GAD-000 audit result."""

    def test_full_compliance(self):
        """Full compliance has all checks passing."""
        audit = GAD000Audit(
            discoverability=True, observability=True, parseability=True,
            composability=True, idempotency=True, recoverability=True,
            sovereign_present=True, signature_valid=True,
            daya=True, satyam=True, tapas=True, saucam=True
        )
        assert audit.criteria_score == 6
        assert audit.dharma_score == 4
        assert audit.is_compliant
        assert "COMPLIANT" in audit.status

    def test_partial_compliance(self):
        """Partial compliance (4-5 criteria)."""
        audit = GAD000Audit(
            discoverability=True, observability=True, parseability=True,
            composability=True, idempotency=True, recoverability=False,
            sovereign_present=True, signature_valid=True,
            daya=True, satyam=True, tapas=True, saucam=True
        )
        assert audit.criteria_score == 5
        assert not audit.is_compliant
        assert "IMPROVEMENT" in audit.status

    def test_fail_compliance(self):
        """Fail compliance (≤3 criteria)."""
        audit = GAD000Audit(
            discoverability=True, observability=True, parseability=True,
            composability=False, idempotency=False, recoverability=False,
            sovereign_present=True, signature_valid=True,
            daya=True, satyam=True, tapas=True, saucam=True
        )
        assert audit.criteria_score == 3
        assert not audit.is_compliant
        assert "VIOLATES" in audit.status

    def test_no_sovereign_fails(self):
        """Missing sovereign fails compliance."""
        audit = GAD000Audit(
            discoverability=True, observability=True, parseability=True,
            composability=True, idempotency=True, recoverability=True,
            sovereign_present=False, signature_valid=False,
            daya=True, satyam=True, tapas=True, saucam=True
        )
        assert audit.criteria_score == 6
        assert not audit.is_compliant  # Because no sovereign

    def test_no_dharma_fails(self):
        """Missing dharma fails compliance."""
        audit = GAD000Audit(
            discoverability=True, observability=True, parseability=True,
            composability=True, idempotency=True, recoverability=True,
            sovereign_present=True, signature_valid=True,
            daya=False, satyam=False, tapas=False, saucam=False
        )
        assert audit.dharma_score == 0
        assert not audit.is_compliant  # Because no dharma

    def test_marker_generation(self):
        """Audit generates valid code marker."""
        audit = GAD000Audit(
            discoverability=True, observability=True, parseability=False,
            composability=True, idempotency=True, recoverability=True,
            sovereign_present=True, signature_valid=True,
            daya=True, satyam=True, tapas=False, saucam=True
        )
        marker = audit.to_marker()
        assert "GAD-000:" in marker
        assert "✓D" in marker
        assert "✓O" in marker
        assert "✗P" in marker  # Parseability failed
        assert "37:✓" in marker
        assert "✗" in marker  # Tapas failed in dharma


class TestMantraHeartbeat:
    """Test the 6.34 Override (Japa-Loop)."""

    def test_japa_interval_is_108(self):
        """One mala = 108 cycles."""
        heartbeat = MantraHeartbeat()
        assert heartbeat.JAPA_INTERVAL == 108

    def test_needs_heartbeat_at_108(self):
        """Needs heartbeat every 108 cycles."""
        heartbeat = MantraHeartbeat()

        # Cycle 0 needs heartbeat
        heartbeat.cycle_count = 0
        assert heartbeat.needs_heartbeat()

        # Cycle 107 doesn't
        heartbeat.cycle_count = 107
        assert not heartbeat.needs_heartbeat()

        # Cycle 108 needs heartbeat
        heartbeat.cycle_count = 108
        assert heartbeat.needs_heartbeat()

        # Cycle 216 needs heartbeat (2 malas)
        heartbeat.cycle_count = 216
        assert heartbeat.needs_heartbeat()

    def test_initial_state(self):
        """Initial heartbeat state."""
        heartbeat = MantraHeartbeat()
        assert heartbeat.cycle_count == 0
        assert heartbeat.last_heartbeat is None
        assert heartbeat.sovereign_signature is None


class TestConstitutionalNumbers:
    """Test the constitutional numbers from CONSTITUTION.md."""

    def test_36_plus_4_plus_37_structure(self):
        """The 36+4+37 structure from the constitution."""
        # Layer 2: The Field (36 Dharmas)
        assert KSHETRA_SIZE == 36

        # Layer 1: The Dharma Test (4 Principles)
        assert DHARMA_COUNT == 4

        # Layer 0: The Sovereign (37th)
        assert KSHETRAJNA == 37

        # Total structure
        assert KSHETRA_SIZE + DHARMA_COUNT + 1 == 41  # 36 + 4 + 1 = 41 (not 37)
        # But the 37th is the HOLDER, not additive
        # The formula is: 36 field elements, 4 tests, 1 holder = 37th position

    def test_6x6_matrix(self):
        """The 6×6 matrix of criteria."""
        assert CRITERIA_COUNT ** 2 == KSHETRA_SIZE


class TestTheFormula:
    """Test: Legitimacy = (36 ∩ 4) × Signature₃₇"""

    def test_without_signature_is_dead(self):
        """Without signature = dead mechanism."""
        assert legitimacy_formula(36, 4, False) == 0.0

    def test_without_dharma_is_tyranny(self):
        """Without dharma = tyranny."""
        assert legitimacy_formula(36, 0, True) == 0.0

    def test_without_matrix_is_chaos(self):
        """Without matrix = chaos."""
        assert legitimacy_formula(0, 4, True) == 0.0

    def test_all_three_required(self):
        """All three components required for legitimacy."""
        # Only full compliance when all three are present
        assert legitimacy_formula(36, 4, True) == 1.0
