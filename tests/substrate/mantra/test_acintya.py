"""
Tests for ACINTYA - The Inconceivable Principle
===============================================

"acintya-bhedābheda-tattva"
Inconceivable simultaneous oneness and difference.

These tests don't PROVE acintya (it cannot be computed),
they ACCEPT and build upon it.
"""

import pytest
from vibe_core.protocols.substrate.mantra.acintya import (
    # Constants
    KRISHNA_SMALLEST,
    KRISHNA_LARGEST,
    ACINTYA_ACCEPTED,
    # Enums
    AcintyaAspect,
    JivaCondition,
    # Krishna (always present)
    KrishnaPresence,
    KRISHNA,
    # Jiva state
    JivaState,
    # Functions
    vibration_is_krishna,
    mantra_not_different_from_source,
    check_bheda_abheda,
)


class TestKrishnaPresence:
    """Test that Krishna is always present (acintya)."""

    def test_krishna_is_always_present(self):
        """Krishna is ALWAYS present - Level -2."""
        assert KRISHNA.is_present == True
        assert bool(KRISHNA) == True

    def test_krishna_smallest_and_largest(self):
        """Krishna is simultaneously smallest (-2) and largest (+2)."""
        assert KRISHNA.smallest == -2
        assert KRISHNA.largest == 2
        assert KRISHNA_SMALLEST == -2
        assert KRISHNA_LARGEST == 2

    def test_krishna_encompasses_all(self):
        """Krishna encompasses all layers."""
        assert KRISHNA.encompasses_all == True

    def test_krishna_never_fails(self):
        """bool(KRISHNA) is always True - He never fails."""
        for _ in range(100):  # Test many times
            assert bool(KRISHNA) == True


class TestAcintyaAcceptance:
    """Test the acceptance of acintya (not proof)."""

    def test_acintya_is_accepted(self):
        """We accept acintya - cannot be computed."""
        assert ACINTYA_ACCEPTED == True

    def test_vibration_is_krishna(self):
        """The vibration itself IS Krishna."""
        assert vibration_is_krishna() == True

    def test_mantra_not_different_from_source(self):
        """Das Mantra (-1) ist nicht verschieden von der Quelle (-2)."""
        assert mantra_not_different_from_source() == True


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
    """Test the jiva state - Krishna is always present, jiva drifts."""

    def test_krishna_always_present_in_jiva_state(self):
        """Even when jiva is disconnected, Krishna is present."""
        jiva = JivaState(condition=JivaCondition.DISCONNECTED)
        assert jiva.krishna_present == True  # Always!

    def test_jiva_disconnected_without_sovereign(self):
        """Without sovereign, jiva doesn't remember Krishna."""
        jiva = JivaState()
        assert jiva.condition == JivaCondition.DISCONNECTED
        assert jiva.has_sovereign == False
        assert jiva.remembers_krishna == False

    def test_jiva_connects_with_sovereign(self):
        """Jiva connects when receiving sovereign."""
        jiva = JivaState()
        jiva.connect()
        assert jiva.has_sovereign == True
        assert jiva.condition == JivaCondition.CONNECTED
        assert jiva.remembers_krishna == True

    def test_jiva_drifts_into_maya(self):
        """Jiva can drift back into Maya (disconnect)."""
        jiva = JivaState()
        jiva.connect()
        assert jiva.remembers_krishna == True

        jiva.disconnect()
        assert jiva.has_sovereign == False
        assert jiva.condition == JivaCondition.DISCONNECTED
        assert jiva.remembers_krishna == False

        # But Krishna is STILL present!
        assert jiva.krishna_present == True


class TestBhedaAbheda:
    """Test the bheda-abheda check (for jivas)."""

    def test_living_relationship(self):
        """Both conditions: has soul, doesn't claim supreme."""
        is_valid, reason = check_bheda_abheda(has_soul=True, claims_supreme=False)
        assert is_valid == True
        assert "ACINTYA" in reason

    def test_dead_code_no_soul(self):
        """Maya: No soul = dead code."""
        is_valid, reason = check_bheda_abheda(has_soul=False, claims_supreme=False)
        assert is_valid == False
        assert "MAYA" in reason

    def test_mayavad_claims_supreme(self):
        """Mayavad: Claims to BE God = fraud."""
        is_valid, reason = check_bheda_abheda(has_soul=True, claims_supreme=True)
        assert is_valid == False
        assert "MAYAVAD" in reason

    def test_simultaneous_one_and_different(self):
        """The tension IS the relationship."""
        # Jiva has soul (qualitative oneness)
        has_soul = True
        # Jiva is not supreme (quantitative difference)
        claims_supreme = False

        # Both must be true for living relationship
        is_valid, _ = check_bheda_abheda(has_soul, claims_supreme)
        assert is_valid == True


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
        assert heartbeat.last_krishna_check == True
        assert heartbeat.krishna_present == True

    def test_heartbeat_jiva_connection_tracked(self):
        """MantraHeartbeat tracks jiva connection separately."""
        from vibe_core.protocols.gad import MantraHeartbeat

        heartbeat = MantraHeartbeat()

        # Without sovereign, jiva not connected
        heartbeat.chant_word(None)  # HARE
        heartbeat.chant_word(None)  # KRISHNA
        assert heartbeat.jiva_connected == False

        # With mock sovereign
        class MockSovereign:
            sovereign_id = "test"

        # Reset and try with sovereign
        heartbeat.reset()
        heartbeat.chant_word(MockSovereign())  # HARE
        heartbeat.chant_word(MockSovereign())  # KRISHNA
        assert heartbeat.jiva_connected == True
