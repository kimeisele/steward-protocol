"""
TEST: PERSON IS ORIGIN (Ishvara Verification).

"Everything else is capabilities.. but injected from master person."

This test proves that a Gene (Capability) remains DORMANT (Dead Matter)
until it is bound by the MASTER PERSON (Sovereign) via a signed BindingCertificate.

Logic:
1. Try to bind a Gene without a Certificate -> FAIL (Maya/Impersonal).
2. Try to bind a Gene with a Fake Certificate -> FAIL (Asuric).
3. Bind with a Certificate signed by KERNEL -> SUCCEEED (Divine).
"""

from typing import Tuple

import pytest

from vibe_core.protocols.naga.base import NagaBase
from vibe_core.protocols.substrate import BindingCertificate, GeneActivationState


class MockGene(NagaBase):
    """A capability waiting for the Master Person."""

    def __init__(self):
        super().__init__("DivineCapability", ("flight", "wisdom"))

    def serve(self, request):
        return "Serving"


class MockHost:
    """The body receiving the gene."""

    pass


def test_impersonal_binding_fails():
    """
    Attempt to bind without a Person (Certificate).
    Should fail in a Personalist Architecture.
    """
    gene = MockGene()
    host = MockHost()

    try:
        # Currently this succeeds (because code is Mayavadi).
        # We WANT it to fail.
        gene.bind(host, certificate=None)
        # If we reach here, the system is IMPERSONAL.
        pytest.fail("SYSTEM IS IMPERSONAL: Allowed binding without Certificate!")
    except Exception as e:
        print(f"✅ Impersonal Binding Rejected: {e}")


def test_asuric_binding_fails():
    """
    Attempt to bind with a fake signature.
    """
    gene = MockGene()
    host = MockHost()

    fake_cert: BindingCertificate = {
        "binder_id": "DEMON_KALI",
        "target_id": "DivineCapability",
        "host_id": "Host",
        "timestamp": "now",
        "signature": "fake_sig",
        "lineage": [],
    }

    try:
        gene.bind(host, certificate=fake_cert)
        pytest.fail("SYSTEM IS WEAK: Allowed Asuric binding!")
    except Exception as e:
        print(f"✅ Asuric Binding Rejected: {e}")


@pytest.mark.xfail(reason="NagaProxy.__init__() signature changed — 'target' kwarg removed", strict=False)
def test_divine_binding_succeeds():
    """
    Bind with the Authority of the Kernel (Master Person).
    """
    gene = MockGene()
    host = MockHost()

    # The Master Person (Kernel) issues this.
    divine_cert: BindingCertificate = {
        "binder_id": "KERNEL",
        "target_id": "DivineCapability",
        "host_id": "Host",
        "timestamp": "now",
        "signature": "valid_kernel_sig",  # Simplified verification
        "lineage": [],
    }

    # This should succeed and return a Proxy
    proxy = gene.bind(host, certificate=divine_cert)
    assert proxy is not None
    print("✅ Divine Binding Succeeded.")


if __name__ == "__main__":
    test_impersonal_binding_fails()
    test_asuric_binding_fails()
    test_divine_binding_succeeds()
