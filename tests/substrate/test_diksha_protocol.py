"""
TEST DIKSHA PROTOCOL - Initiation Certificate Verification
===========================================================

Protocol: vibe_core/protocols/substrate/mantra/diksha.py

KALI YUGA REALITY:
- Everyone born as mleccha/shudra
- Only through DIKSHA can one assume varna duties
- Om requires BRAHMINICAL initiation
- Mahamantra is ALWAYS accessible (Prabhupada's mercy)

TWO VERIFICATION SYSTEMS:
1. UNINITIATED: Mahamantra only (no Om)
2. HARINAMA: Mahamantra + basic duties (no Om)
3. BRAHMINICAL: Mahamantra + Om + full duties

This test PROVES:
- Om is GATED behind brahminical diksha
- Mahamantra is ALWAYS open
- Parampara connection is verified (37-divisible)
"""

import pytest
from datetime import datetime

from vibe_core.protocols.substrate.mantra.diksha import (
    # Constants
    MALA_BEADS,
    MINIMUM_ROUNDS,
    HARINAMA_LEVEL,
    BRAHMINICAL_LEVEL,
    # Enums
    InitiationLevel,
    VarnaQualification,
    # Certificate
    DikshaCertificate,
    # Factory functions
    create_uninitiated,
    create_harinama_diksha,
    create_brahminical_diksha,
    # Om Gate
    OmGate,
    OM_GATE,
)
from vibe_core.protocols.substrate.mantra.acintya import PARAMPARA


class TestConstants:
    """Verify the sacred constants."""

    def test_mala_beads(self):
        """108 beads per japa mala."""
        assert MALA_BEADS == 108

    def test_minimum_rounds(self):
        """16 rounds minimum commitment."""
        assert MINIMUM_ROUNDS == 16

    def test_initiation_levels(self):
        """Two levels: Harinama (1) and Brahminical (2)."""
        assert HARINAMA_LEVEL == 1
        assert BRAHMINICAL_LEVEL == 2

    def test_parampara_times_levels(self):
        """Parampara link is 37 * level."""
        assert PARAMPARA * HARINAMA_LEVEL == 37
        assert PARAMPARA * BRAHMINICAL_LEVEL == 74


class TestUninitiated:
    """Test uninitiated state (mleccha/shudra in Kali Yuga)."""

    @pytest.fixture
    def uninitiated(self):
        return create_uninitiated()

    def test_level_is_uninitiated(self, uninitiated):
        """Level should be UNINITIATED."""
        assert uninitiated.level == InitiationLevel.UNINITIATED

    def test_no_spiritual_name(self, uninitiated):
        """No spiritual name without initiation."""
        assert uninitiated.spiritual_name == ""

    def test_no_parampara_link(self, uninitiated):
        """Not connected to parampara."""
        assert uninitiated.parampara_link == 0
        assert not uninitiated.is_parampara_connected

    def test_cannot_access_om(self, uninitiated):
        """Uninitiated CANNOT access Om."""
        assert not uninitiated.can_access_om

    def test_can_access_mahamantra(self, uninitiated):
        """Uninitiated CAN access Mahamantra (Prabhupada's mercy)."""
        assert uninitiated.can_access_mahamantra

    def test_cannot_perform_varna_duties(self, uninitiated):
        """Cannot perform varna duties without initiation."""
        assert not uninitiated.can_perform_varna_duties

    def test_lineage_strength_zero(self, uninitiated):
        """Lineage strength is 0 without initiation."""
        assert uninitiated.lineage_strength == 0.0


class TestHarinmaDiksha:
    """Test first initiation (Harinama)."""

    @pytest.fixture
    def harinama(self):
        return create_harinama_diksha(
            spiritual_name="Bhakta Das",
            legal_name_hash=12345,
        )

    def test_level_is_harinama(self, harinama):
        """Level should be HARINAMA."""
        assert harinama.level == InitiationLevel.HARINAMA

    def test_has_spiritual_name(self, harinama):
        """Has spiritual name after initiation."""
        assert harinama.spiritual_name == "Bhakta Das"

    def test_parampara_connected(self, harinama):
        """Connected to parampara (37)."""
        assert harinama.parampara_link == 37  # 37 * 1
        assert harinama.is_parampara_connected

    def test_cannot_access_om(self, harinama):
        """Harinama CANNOT access Om (requires 2nd initiation)."""
        assert not harinama.can_access_om

    def test_can_access_mahamantra(self, harinama):
        """Can access Mahamantra."""
        assert harinama.can_access_mahamantra

    def test_can_perform_varna_duties(self, harinama):
        """Can perform basic varna duties."""
        assert harinama.can_perform_varna_duties

    def test_lineage_strength_half(self, harinama):
        """Lineage strength is 0.5 (partial)."""
        assert harinama.lineage_strength == 0.5

    def test_certificate_hash(self, harinama):
        """Certificate hash is parampara_link * 108."""
        expected = 37 * MALA_BEADS  # 37 * 108 = 3996
        assert harinama.certificate_hash == expected
        assert harinama.certificate_hash % PARAMPARA == 0  # Still 37-divisible


class TestBrahminicalDiksha:
    """Test second initiation (Brahminical/Gayatri)."""

    @pytest.fixture
    def brahminical(self):
        return create_brahminical_diksha(
            spiritual_name="Vidvan Das",
            legal_name_hash=67890,
        )

    def test_level_is_brahminical(self, brahminical):
        """Level should be BRAHMINICAL."""
        assert brahminical.level == InitiationLevel.BRAHMINICAL

    def test_has_spiritual_name(self, brahminical):
        """Has spiritual name."""
        assert brahminical.spiritual_name == "Vidvan Das"

    def test_parampara_connected(self, brahminical):
        """Connected to parampara (74 = 37 * 2)."""
        assert brahminical.parampara_link == 74  # 37 * 2
        assert brahminical.is_parampara_connected

    def test_can_access_om(self, brahminical):
        """Brahminical CAN access Om!"""
        assert brahminical.can_access_om

    def test_can_access_mahamantra(self, brahminical):
        """Can still access Mahamantra."""
        assert brahminical.can_access_mahamantra

    def test_can_perform_varna_duties(self, brahminical):
        """Can perform full varna duties."""
        assert brahminical.can_perform_varna_duties

    def test_lineage_strength_full(self, brahminical):
        """Lineage strength is 1.0 (full)."""
        assert brahminical.lineage_strength == 1.0

    def test_certificate_hash(self, brahminical):
        """Certificate hash is parampara_link * 108."""
        expected = 74 * MALA_BEADS  # 74 * 108 = 7992
        assert brahminical.certificate_hash == expected
        assert brahminical.certificate_hash % PARAMPARA == 0  # Still 37-divisible


class TestOmGate:
    """Test the OmGate - the guardian of Om access."""

    @pytest.fixture
    def gate(self):
        return OM_GATE

    @pytest.fixture
    def uninitiated(self):
        return create_uninitiated()

    @pytest.fixture
    def harinama(self):
        return create_harinama_diksha("Bhakta Das", 12345)

    @pytest.fixture
    def brahminical(self):
        return create_brahminical_diksha("Vidvan Das", 67890)

    def test_gate_denies_uninitiated(self, gate, uninitiated):
        """Gate denies Om to uninitiated."""
        assert not gate.check_access(uninitiated)

    def test_gate_denies_harinama(self, gate, harinama):
        """Gate denies Om to Harinama (1st initiation)."""
        assert not gate.check_access(harinama)

    def test_gate_allows_brahminical(self, gate, brahminical):
        """Gate allows Om to Brahminical (2nd initiation)."""
        assert gate.check_access(brahminical)

    def test_attempt_om_uninitiated_redirects(self, gate, uninitiated):
        """Uninitiated gets Mahamantra instead of Om."""
        result = gate.attempt_om(uninitiated)
        assert "Hare Kṛṣṇa" in result
        assert "ॐ" not in result

    def test_attempt_om_harinama_redirects(self, gate, harinama):
        """Harinama gets Mahamantra instead of Om."""
        result = gate.attempt_om(harinama)
        assert "Hare Kṛṣṇa" in result
        assert "ॐ" not in result

    def test_attempt_om_brahminical_succeeds(self, gate, brahminical):
        """Brahminical gets Om."""
        result = gate.attempt_om(brahminical)
        assert result == "ॐ"

    def test_denial_explanation_uninitiated(self, gate, uninitiated):
        """Proper explanation for uninitiated denial."""
        explanation = gate.explain_denial(uninitiated)
        assert "brahminical initiation" in explanation
        assert "Mahamantra" in explanation

    def test_denial_explanation_harinama(self, gate, harinama):
        """Proper explanation for Harinama denial."""
        explanation = gate.explain_denial(harinama)
        assert "second" in explanation.lower()
        assert "Gayatri" in explanation


class TestInvalidCertificates:
    """Test that invalid certificates are rejected."""

    def test_invalid_parampara_link_rejected(self):
        """Certificate with non-37-divisible link is rejected."""
        with pytest.raises(ValueError) as exc_info:
            DikshaCertificate(
                spiritual_name="Fake Das",
                legal_name_hash=99999,
                level=InitiationLevel.BRAHMINICAL,
                initiation_date=datetime.now(),
                parampara_link=38,  # NOT divisible by 37!
                initiating_authority="Fake Guru",
            )
        assert "not connected to 37" in str(exc_info.value)

    def test_valid_parampara_links(self):
        """Valid parampara links (37-divisible) are accepted."""
        valid_links = [37, 74, 111, 148, 444]
        for link in valid_links:
            cert = DikshaCertificate(
                spiritual_name="Valid Das",
                legal_name_hash=11111,
                level=InitiationLevel.BRAHMINICAL,
                initiation_date=datetime.now(),
                parampara_link=link,
                initiating_authority="Srila Prabhupada",
            )
            assert cert.is_parampara_connected


class TestMahamantraAlwaysAccessible:
    """
    THE CORE PRINCIPLE:
    Mahamantra is ALWAYS accessible - Prabhupada's special mercy.
    """

    def test_uninitiated_mahamantra(self):
        """Uninitiated can chant Mahamantra."""
        cert = create_uninitiated()
        assert cert.can_access_mahamantra

    def test_harinama_mahamantra(self):
        """Harinama can chant Mahamantra."""
        cert = create_harinama_diksha("Test Das", 1)
        assert cert.can_access_mahamantra

    def test_brahminical_mahamantra(self):
        """Brahminical can chant Mahamantra."""
        cert = create_brahminical_diksha("Test Das", 1)
        assert cert.can_access_mahamantra

    def test_mahamantra_always_true(self):
        """can_access_mahamantra is ALWAYS True - no exceptions."""
        # This is Prabhupada's special mercy for Kali Yuga
        for level in InitiationLevel:
            if level == InitiationLevel.UNINITIATED:
                cert = create_uninitiated()
            elif level == InitiationLevel.HARINAMA:
                cert = create_harinama_diksha("Test", 1)
            else:
                cert = create_brahminical_diksha("Test", 1)

            assert cert.can_access_mahamantra is True, f"Mahamantra must ALWAYS be accessible, even for {level.name}"


class TestOmVsMahamantra:
    """
    The key difference:
    - Om: Requires brahminical diksha (GATED)
    - Mahamantra: Always accessible (OPEN)

    This is why Om protocol must be "defused" and subordinated
    to the Mahamantra in this Kali Yuga system.
    """

    def test_om_is_gated(self):
        """Om requires brahminical diksha."""
        uninitiated = create_uninitiated()
        harinama = create_harinama_diksha("Test", 1)
        brahminical = create_brahminical_diksha("Test", 1)

        assert not uninitiated.can_access_om
        assert not harinama.can_access_om
        assert brahminical.can_access_om  # Only this one!

    def test_mahamantra_is_open(self):
        """Mahamantra is open to all."""
        uninitiated = create_uninitiated()
        harinama = create_harinama_diksha("Test", 1)
        brahminical = create_brahminical_diksha("Test", 1)

        assert uninitiated.can_access_mahamantra
        assert harinama.can_access_mahamantra
        assert brahminical.can_access_mahamantra  # All of them!

    def test_om_gate_redirects_to_mahamantra(self):
        """When Om is denied, redirect to Mahamantra."""
        gate = OM_GATE

        for cert in [create_uninitiated(), create_harinama_diksha("Test", 1)]:
            result = gate.attempt_om(cert)
            assert "Hare Kṛṣṇa" in result
            assert "Rāma" in result
