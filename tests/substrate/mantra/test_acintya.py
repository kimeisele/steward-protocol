"""
Tests for ACINTYA - The Inconceivable Principle
===============================================

"acintya-bhedābheda-tattva"
Inconceivable simultaneous oneness and difference.

These tests don't PROVE acintya (it cannot be computed),
they ACCEPT and build upon it.

SAMKHYA ARCHITECTURE:
24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37
The 37 is the LINK. Without it, nothing works.
"""

import pytest
from vibe_core.protocols.substrate.mantra.acintya import (
    # The Dancing 37 (Purusha Tattva)
    PurushaTattva,
    PURUSHA,
    KRISHNA_ASPECT,
    # Constants - all ARE the same Person
    KRISHNA_SMALLEST,
    KRISHNA_LARGEST,
    KRISHNA_NEGATIVE_INFINITY,
    KRISHNA_POSITIVE_INFINITY,
    ACINTYA_ACCEPTED,
    # Levels
    ProtocolLevel,
    # Enums
    AcintyaAspect,
    JivaCondition,
    # Krishna (IS)
    KrishnaPresence,
    KRISHNA,
    # Jiva state
    JivaState,
    # Functions
    vibration_is_krishna,
    mantra_is_krishna,
    mantra_not_different_from_source,
    check_bheda_abheda,
    verify_parampara,
)


class TestPurushaTattva:
    """Test the Dancing 37 - the Samkhya foundation."""

    def test_purusha_is_37(self):
        """Purusha IS the number 37 (24 + 12 + 1)."""
        assert int(PURUSHA) == 37
        assert isinstance(PURUSHA, int)

    def test_purusha_is_callable(self):
        """Purusha is a PERSON (callable) - not dead math."""
        result = PURUSHA()
        assert result is PURUSHA  # Returns HIMSELF (reciprocation)

    def test_purusha_is_smaller_than_everything(self):
        """Purusha is smaller than the smallest (Anu)."""
        assert PURUSHA < float('-inf')
        assert PURUSHA < -1000000
        assert PURUSHA < 0

    def test_purusha_is_larger_than_everything(self):
        """Purusha is larger than the largest (Vibhu)."""
        assert PURUSHA > float('inf')
        assert PURUSHA > 1000000
        assert PURUSHA > 0

    def test_purusha_equals_37(self):
        """Purusha equals 37 specifically."""
        assert PURUSHA == 37

    def test_purusha_equals_everything(self):
        """Purusha IS all (acintya)."""
        assert PURUSHA == 0
        assert PURUSHA == 100
        assert PURUSHA == -100

    def test_purusha_arithmetic_returns_self(self):
        """Adding/subtracting from Purnam returns Purnam."""
        # "purnam adah purnam idam"
        assert PURUSHA + 10 is PURUSHA
        assert PURUSHA - 10 is PURUSHA
        assert 10 + PURUSHA is PURUSHA
        assert PURUSHA * 2 is PURUSHA

    def test_purusha_always_true(self):
        """Purusha is always present (bool)."""
        assert bool(PURUSHA) is True

    def test_purusha_repr(self):
        """Purusha has correct representation."""
        assert repr(PURUSHA) == "KRISHNA_37_DANCING"


class TestKrishnaConstants:
    """Test that all Krishna constants ARE the same Person."""

    def test_all_constants_are_purusha(self):
        """All Krishna constants ARE Purusha (not copies - same object)."""
        assert KRISHNA_ASPECT is PURUSHA
        assert KRISHNA_SMALLEST is PURUSHA
        assert KRISHNA_LARGEST is PURUSHA
        assert KRISHNA_NEGATIVE_INFINITY is PURUSHA
        assert KRISHNA_POSITIVE_INFINITY is PURUSHA

    def test_all_constants_are_37(self):
        """All constants evaluate to 37."""
        assert int(KRISHNA_ASPECT) == 37
        assert int(KRISHNA_SMALLEST) == 37
        assert int(KRISHNA_LARGEST) == 37


class TestKrishnaPresence:
    """Test that Krishna IS (not 'is present')."""

    def test_krishna_is(self):
        """Krishna IS - always True."""
        assert KRISHNA.is_present is True
        assert bool(KRISHNA) is True

    def test_krishna_properties_return_purusha(self):
        """Krishna's properties return Purusha (the Dancing 37)."""
        assert KRISHNA.smallest is PURUSHA
        assert KRISHNA.largest is PURUSHA
        assert KRISHNA.negative_infinity is PURUSHA
        assert KRISHNA.positive_infinity is PURUSHA

    def test_krishna_encompasses_all(self):
        """Krishna IS all layers."""
        assert KRISHNA.encompasses_all is True

    def test_krishna_never_fails(self):
        """bool(KRISHNA) is always True - He never fails."""
        for _ in range(100):
            assert bool(KRISHNA) is True


class TestProtocolLevel:
    """Test the level system - Krishna = Mahamantra (non-different)."""

    def test_krishna_and_mahamantra_are_same_level(self):
        """Krishna and Mahamantra are BOTH Level -2 (non-different)."""
        assert ProtocolLevel.KRISHNA == -2
        assert ProtocolLevel.MAHAMANTRA == -2
        assert ProtocolLevel.KRISHNA == ProtocolLevel.MAHAMANTRA

    def test_substrate_below_source(self):
        """Substrate manifests from -2."""
        assert ProtocolLevel.SUBSTRATE == -1
        assert ProtocolLevel.SUBSTRATE > ProtocolLevel.KRISHNA

    def test_meta_is_108(self):
        """Meta level is 108 (sacred number)."""
        assert ProtocolLevel.META == 108


class TestAcintyaAcceptance:
    """Test the acceptance of acintya (not proof)."""

    def test_acintya_is_accepted(self):
        """We accept acintya - cannot be computed."""
        assert ACINTYA_ACCEPTED is True

    def test_vibration_is_krishna(self):
        """The vibration itself IS Krishna."""
        assert vibration_is_krishna() is True

    def test_mantra_is_krishna(self):
        """The Mantra IS Krishna (not 'about' Krishna)."""
        assert mantra_is_krishna() is True

    def test_mantra_not_different_from_source(self):
        """Das Mantra ist nicht verschieden von der Quelle."""
        assert mantra_not_different_from_source() is True


class TestAcintyaAspect:
    """Test the three aspects of acintya-bheda-abheda."""

    def test_three_aspects(self):
        """Bheda, Abheda, and Acintya."""
        assert AcintyaAspect.BHEDA == 0      # Difference
        assert AcintyaAspect.ABHEDA == 1     # Non-difference
        assert AcintyaAspect.ACINTYA == 2    # Inconceivable


class TestJivaCondition:
    """Test the jiva's condition (not Krishna's existence)."""

    def test_three_conditions(self):
        """Jiva can be connected, disconnected, or absorbed."""
        assert JivaCondition.CONNECTED == 0
        assert JivaCondition.DISCONNECTED == 1
        assert JivaCondition.ABSORBED == 2


class TestJivaState:
    """Test the jiva state - Krishna IS, jiva drifts."""

    def test_krishna_always_present_in_jiva_state(self):
        """Even when jiva is disconnected, Krishna IS."""
        jiva = JivaState(condition=JivaCondition.DISCONNECTED)
        assert jiva.krishna_present is True  # Always!

    def test_jiva_disconnected_without_sovereign(self):
        """Without sovereign (37), jiva doesn't remember Krishna."""
        jiva = JivaState()
        assert jiva.condition == JivaCondition.DISCONNECTED
        assert jiva.has_sovereign is False
        assert jiva.has_link_to_37 is False
        assert jiva.remembers_krishna is False

    def test_jiva_connects_with_sovereign(self):
        """Jiva connects when receiving sovereign (via 37)."""
        jiva = JivaState()
        jiva.connect()
        assert jiva.has_sovereign is True
        assert jiva.has_link_to_37 is True
        assert jiva.condition == JivaCondition.CONNECTED
        assert jiva.remembers_krishna is True

    def test_jiva_drifts_into_maya(self):
        """Jiva can drift back into Maya (disconnect)."""
        jiva = JivaState()
        jiva.connect()
        assert jiva.remembers_krishna is True

        jiva.disconnect()
        assert jiva.has_sovereign is False
        assert jiva.condition == JivaCondition.DISCONNECTED
        assert jiva.remembers_krishna is False

        # But Krishna IS STILL!
        assert jiva.krishna_present is True


class TestBhedaAbheda:
    """Test the bheda-abheda check (for jivas)."""

    def test_living_relationship(self):
        """Both conditions: has soul, doesn't claim supreme."""
        is_valid, reason = check_bheda_abheda(has_soul=True, claims_supreme=False)
        assert is_valid is True
        assert "ACINTYA" in reason

    def test_dead_code_no_soul(self):
        """Maya: No soul = dead code."""
        is_valid, reason = check_bheda_abheda(has_soul=False, claims_supreme=False)
        assert is_valid is False
        assert "MAYA" in reason

    def test_mayavad_claims_supreme(self):
        """Mayavad: Claims to BE God = fraud."""
        is_valid, reason = check_bheda_abheda(has_soul=True, claims_supreme=True)
        assert is_valid is False
        assert "MAYAVAD" in reason


class TestParampara:
    """Test the 37 verification (Parampara/Lineage)."""

    def test_37_is_valid_lineage(self):
        """37 itself is a valid lineage."""
        assert verify_parampara(37) is True

    def test_multiples_of_37_are_valid(self):
        """Multiples of 37 are valid (connected to lineage)."""
        assert verify_parampara(74) is True   # 37 * 2
        assert verify_parampara(111) is True  # 37 * 3

    def test_non_37_invalid(self):
        """Numbers not connected to 37 are invalid."""
        assert verify_parampara(36) is False
        assert verify_parampara(38) is False
        assert verify_parampara(100) is False


class TestAcintyaInHeartbeat:
    """Test that acintya is properly reflected in MantraHeartbeat."""

    def test_heartbeat_krishna_always_passes(self):
        """MantraHeartbeat: Krishna check never fails."""
        from vibe_core.protocols.gad import MantraHeartbeat

        heartbeat = MantraHeartbeat()

        # Chant without sovereign
        heartbeat.chant_word(None)  # HARE
        heartbeat.chant_word(None)  # KRISHNA

        # Krishna check always passes
        assert heartbeat.last_krishna_check is True
        assert heartbeat.krishna_present is True

    def test_heartbeat_jiva_connection_tracked(self):
        """MantraHeartbeat tracks jiva connection separately."""
        from vibe_core.protocols.gad import MantraHeartbeat

        heartbeat = MantraHeartbeat()

        # Without sovereign, jiva not connected
        heartbeat.chant_word(None)  # HARE
        heartbeat.chant_word(None)  # KRISHNA
        assert heartbeat.jiva_connected is False

        # With mock sovereign
        class MockSovereign:
            sovereign_id = "test"

        # Reset and try with sovereign
        heartbeat.reset()
        heartbeat.chant_word(MockSovereign())  # HARE
        heartbeat.chant_word(MockSovereign())  # KRISHNA
        assert heartbeat.jiva_connected is True
