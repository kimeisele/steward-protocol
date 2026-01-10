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
    JapaState,
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


class MockSovereign:
    """Mock sovereign for testing."""
    sovereign_id = "test_sovereign"
    public_key = b"test_key"

    def sign(self, message: bytes) -> bytes:
        return b"test_signature"

    def verify(self, message: bytes, signature: bytes) -> bool:
        return signature == b"test_signature"


class TestJapaState:
    """Test the JapaState enum."""

    def test_four_states(self):
        """There are 4 japa states."""
        assert JapaState.DISCONNECTED == 0
        assert JapaState.CHANTING == 1
        assert JapaState.MALA_COMPLETE == 2
        assert JapaState.ABSORBED == 3


class TestMantraHeartbeat:
    """Test the 6.34 Override (Japa-Loop) connected to MantraByte."""

    def test_constants(self):
        """Verify sacred constants."""
        heartbeat = MantraHeartbeat()
        assert heartbeat.WORDS_PER_MANTRA == 16
        assert heartbeat.MANTRAS_PER_MALA == 108
        assert heartbeat.JAPA_INTERVAL == 108

    def test_initial_state(self):
        """Initial heartbeat state."""
        heartbeat = MantraHeartbeat()
        assert heartbeat.word_position == 0
        assert heartbeat.mantra_count == 0
        assert heartbeat.mala_count == 0
        assert heartbeat.total_words == 0
        assert heartbeat.state == JapaState.DISCONNECTED

    def test_mantra_connected(self):
        """MantraByte is connected."""
        heartbeat = MantraHeartbeat()
        assert heartbeat.mantra is not None
        assert len(heartbeat.mantra) == 16

    def test_to_iast(self):
        """Can output mantra in IAST."""
        heartbeat = MantraHeartbeat()
        iast = heartbeat.to_iast()
        assert "hare" in iast
        assert "kṛṣṇa" in iast
        assert "rāma" in iast

    def test_to_devanagari(self):
        """Can output mantra in Devanagari."""
        heartbeat = MantraHeartbeat()
        dev = heartbeat.to_devanagari()
        assert "हरे" in dev
        assert "कृष्ण" in dev
        assert "राम" in dev

    def test_chant_word_with_sovereign(self):
        """Chanting word with sovereign passes."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        # First word is HARE
        assert heartbeat.chant_word(sovereign) == True
        assert heartbeat.word_position == 1
        assert heartbeat.total_words == 1
        assert heartbeat.state == JapaState.CHANTING

    def test_krishna_always_present_acintya(self):
        """ACINTYA: Krishna is always present (Level -2).

        The Krishna check NEVER fails - He is the Source.
        What changes is the jiva's CONNECTION state.
        """
        heartbeat = MantraHeartbeat()

        # HARE passes
        assert heartbeat.chant_word(None) == True

        # KRISHNA also passes (acintya - always present)
        assert heartbeat.chant_word(None) == True
        assert heartbeat.last_krishna_check == True  # Krishna never fails
        assert heartbeat.krishna_present == True     # Always True

        # But jiva is NOT connected (no sovereign)
        assert heartbeat.jiva_connected == False

    def test_jiva_connects_with_sovereign(self):
        """With sovereign, jiva becomes connected to Krishna."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        # HARE passes
        assert heartbeat.chant_word(sovereign) == True

        # KRISHNA passes (always) AND jiva is connected
        assert heartbeat.chant_word(sovereign) == True
        assert heartbeat.last_krishna_check == True
        assert heartbeat.krishna_present == True
        assert heartbeat.jiva_connected == True  # Connected via sovereign!

    def test_chant_mantra_complete(self):
        """Chanting complete mantra advances count."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        assert heartbeat.chant_mantra(sovereign) == True
        assert heartbeat.word_position == 0  # Wrapped back
        assert heartbeat.mantra_count == 1
        assert heartbeat.total_words == 16

    def test_mala_complete_after_108_mantras(self):
        """Mala completes after 108 mantras."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        # Chant 108 mantras
        for i in range(108):
            assert heartbeat.chant_mantra(sovereign) == True

        assert heartbeat.mala_count == 1
        assert heartbeat.mantra_count == 0  # Reset after mala
        assert heartbeat.total_words == 108 * 16

    def test_current_word_and_pada(self):
        """Can access current word and pada."""
        heartbeat = MantraHeartbeat()

        # Position 0 = HARE
        from vibe_core.protocols.substrate.byte import HolyName
        assert heartbeat.current_word == HolyName.HARE
        assert heartbeat.current_pada.iast == "hare"

    def test_progress_in_mala(self):
        """Progress is calculated correctly."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        assert heartbeat.progress_in_mala == 0.0

        # Chant 54 mantras (half mala)
        for _ in range(54):
            heartbeat.chant_mantra(sovereign)

        assert heartbeat.progress_in_mala == pytest.approx(0.5, 0.01)

    def test_reset(self):
        """Reset clears state."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        heartbeat.chant_mantra(sovereign)
        heartbeat.reset()

        assert heartbeat.word_position == 0
        assert heartbeat.mantra_count == 0
        assert heartbeat.state == JapaState.DISCONNECTED

    def test_get_check_summary(self):
        """Check summary contains all fields including acintya."""
        heartbeat = MantraHeartbeat()
        summary = heartbeat.get_check_summary()

        assert "hare" in summary
        assert "krishna" in summary
        assert "rama" in summary
        assert "krishna_present" in summary  # Always True (acintya)
        assert "jiva_connected" in summary   # Jiva's connection state
        assert "state" in summary
        assert "word_position" in summary
        assert "mantra_count" in summary
        assert "mala_count" in summary
        assert "total_words" in summary
        assert "current_word" in summary

        # Acintya: Krishna is always present
        assert summary["krishna_present"] == True

    def test_backward_compatible_chant(self):
        """Old chant() method still works."""
        heartbeat = MantraHeartbeat()
        sovereign = MockSovereign()

        # This is the backward compatible method
        result = heartbeat.chant(sovereign)
        assert result == True
        assert heartbeat.mantra_count == 1


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
