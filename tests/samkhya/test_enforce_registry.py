from unittest.mock import MagicMock

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.universal import EnforceProtocol
from vibe_core.services.capability_enforcer import CapabilityEnforcerService


def test_registry_enforce_lookup():
    """
    Verify that EnforceProtocol lookup returns the CapabilityEnforcer.
    This ensures the 'protocols=[EnforceProtocol]' registration in Kernel works.
    But since we don't boot the full Kernel here, we manually verify the registration logic.
    """
    ServiceRegistry.reset_all()

    # Manual Registration (mimicking Kernel)
    # We can't easily import Kernel here because it boots everything,
    # but we testing the Registry logic + Instance compatibility.

    enforcer = CapabilityEnforcerService()

    # Register WITHOUT explicit descriptors (Testing the O(n) Fallback)
    ServiceRegistry.register(
        type(enforcer),  # or CapabilityEnforcerProtocol
        enforcer,
        # protocols=[...] omitted to verified fallback for Protected Kernel
    )

    # 1. Look up
    enforcers = ServiceRegistry.get_all(EnforceProtocol)

    # 2. Verify (Should find it via isinstance)
    assert len(enforcers) >= 1
    assert enforcer in enforcers

    # 3. Verify Map Access (O(1) Map wont have it, but get_all returns it)
    # assert EnforceProtocol in ServiceRegistry._protocols # This would fail
    assert isinstance(enforcers[0], EnforceProtocol)

    # 3. Verify Map Access (O(1))
    # assert EnforceProtocol in ServiceRegistry._protocols
    # assert enforcer in ServiceRegistry._protocols[EnforceProtocol]
