from typing import cast

import pytest

from vibe_core.naga.identity import NagaIdentity
from vibe_core.protocols.identity import IdentityProtocol, KeyStoreProtocol
from vibe_core.steward.keystore import FileKeyStore


def test_naga_identity_implements_protocol():
    """Verify NagaIdentity satisfies IdentityProtocol (static & runtime)."""
    # 1. Static Check (Mypy would catch this)
    # 2. Runtime Check via isinstance (if runtime_checkable)

    # assert issubclass(NagaIdentity, IdentityProtocol) # Fails with TypeError for non-methods

    identity = NagaIdentity.generate("test_agent")
    assert isinstance(identity, IdentityProtocol)

    # Check properties
    assert hasattr(identity, "public_key_pem")
    assert identity.public_key_pem == identity.public_key
    assert hasattr(identity, "fingerprint")
    assert hasattr(identity, "sign")
    assert hasattr(identity, "verify")


def test_file_keystore_implements_protocol():
    """Verify FileKeyStore satisfies KeyStoreProtocol."""
    assert issubclass(FileKeyStore, KeyStoreProtocol)

    ks = FileKeyStore()
    assert isinstance(ks, KeyStoreProtocol)
