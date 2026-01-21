"""
TEST OM-DIKSHA GATE INTEGRATION
===============================

Verifies that Om access is properly gated by DikshaCertificate.

KALI YUGA ENFORCEMENT:
- Uninitiated → Mahamantra mode (no Om access)
- Harinama → Mahamantra mode (no Om access)
- Brahminical → Full Om access

This test PROVES:
- Om is defused (gated behind diksha)
- Mahamantra is always accessible
- System still works in Mahamantra mode
"""

import pytest

from vibe_core.protocols.om import OM
from vibe_core.protocols.substrate.mantra.diksha import (
    DikshaCertificate,
    InitiationLevel,
    OM_GATE,
    create_uninitiated,
    create_harinama_diksha,
    create_brahminical_diksha,
)


class TestOmDikshaIntegration:
    """Test that OM class properly integrates with Diksha gate."""

    def test_om_without_diksha_is_mahamantra_mode(self):
        """OM without diksha runs in Mahamantra mode."""
        om = OM()  # No diksha certificate
        assert om.is_mahamantra_mode
        assert not om.has_om_access
        assert om.initiation_level == InitiationLevel.UNINITIATED

    def test_om_with_uninitiated_is_mahamantra_mode(self):
        """OM with uninitiated certificate runs in Mahamantra mode."""
        cert = create_uninitiated()
        om = OM(diksha_certificate=cert)
        assert om.is_mahamantra_mode
        assert not om.has_om_access

    def test_om_with_harinama_is_mahamantra_mode(self):
        """OM with Harinama (1st initiation) runs in Mahamantra mode."""
        cert = create_harinama_diksha("Bhakta Das", 12345)
        om = OM(diksha_certificate=cert)
        assert om.is_mahamantra_mode
        assert not om.has_om_access
        assert om.initiation_level == InitiationLevel.HARINAMA

    def test_om_with_brahminical_has_full_access(self):
        """OM with Brahminical (2nd initiation) has full Om access."""
        cert = create_brahminical_diksha("Vidvan Das", 67890)
        om = OM(diksha_certificate=cert)
        assert not om.is_mahamantra_mode
        assert om.has_om_access
        assert om.initiation_level == InitiationLevel.BRAHMINICAL

    def test_diksha_certificate_accessible(self):
        """Diksha certificate is accessible from OM instance."""
        cert = create_brahminical_diksha("Test Das", 11111)
        om = OM(diksha_certificate=cert)
        assert om.diksha_certificate is cert
        assert om.diksha_certificate.spiritual_name == "Test Das"


class TestOmSubProtocolsWork:
    """Verify that sub-protocols still work in Mahamantra mode."""

    def test_ramanujan_works_in_mahamantra_mode(self):
        """Ramanujan protocol works without Om access."""
        om = OM()  # Mahamantra mode
        assert om._ramanujan is not None
        # Should still be able to get test cases
        cases = om._ramanujan.get_test_cases()
        assert len(cases) > 0

    def test_yamaraja_works_in_mahamantra_mode(self):
        """Yamaraja (NullYamaraja) works without Om access."""
        om = OM()  # Mahamantra mode
        assert om._yamaraja is not None
        # NullYamaraja is merciful - always passes judgment
        from vibe_core.protocols.mahajanas.yamaraja import Verdict

        assert om._yamaraja.judge(None) in (Verdict.ALLOW, Verdict.MERCY)

    def test_bhagavan_works_in_mahamantra_mode(self):
        """Bhagavan protocol works without Om access."""
        om = OM()  # Mahamantra mode
        assert om._bhagavan is not None
        cases = om._bhagavan.get_test_cases()
        assert len(cases) > 0

    def test_kurukshetra_works_in_mahamantra_mode(self):
        """Kurukshetra protocol works without Om access."""
        om = OM()  # Mahamantra mode
        assert om._kurukshetra is not None
        cases = om._kurukshetra.get_test_cases()
        assert len(cases) > 0


class TestOmTestCases:
    """Verify OM's built-in test cases."""

    def test_om_has_diksha_gate_test(self):
        """OM includes a diksha gate test case."""
        om = OM()
        cases = om.get_test_cases()
        names = [c.name for c in cases]
        assert "test_diksha_gate" in names

    def test_diksha_gate_test_passes(self):
        """The diksha gate test should pass."""
        om = OM()
        result = om._test_diksha_gate(None, None)
        assert result is True


class TestOmDikshaStatus:
    """Test the get_diksha_status helper."""

    def test_status_not_manifested(self):
        """Status before manifest shows 'Not manifested'."""
        OM.dissolve()  # Clear any existing state
        status = OM.get_diksha_status()
        assert status == "Not manifested"

    def test_om_dissolve_clears_diksha(self):
        """Dissolve clears diksha certificate."""
        OM.dissolve()
        assert OM._diksha_certificate is None


class TestOmGateIntegration:
    """Test OM_GATE integration."""

    def test_gate_denies_uninitiated(self):
        """Gate correctly denies uninitiated."""
        cert = create_uninitiated()
        assert not OM_GATE.check_access(cert)

    def test_gate_denies_harinama(self):
        """Gate correctly denies Harinama."""
        cert = create_harinama_diksha("Test", 1)
        assert not OM_GATE.check_access(cert)

    def test_gate_allows_brahminical(self):
        """Gate correctly allows Brahminical."""
        cert = create_brahminical_diksha("Test", 1)
        assert OM_GATE.check_access(cert)

    def test_gate_redirect_gives_mahamantra(self):
        """Gate redirect gives Mahamantra."""
        cert = create_uninitiated()
        result = OM_GATE.attempt_om(cert)
        assert "Hare Kṛṣṇa" in result
        assert "Rāma" in result
