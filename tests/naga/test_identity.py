"""
Tests for NAGA Identity - Cryptographic sovereign identity (GAD-000 37th Principle).
"""

import pytest

from vibe_core.naga.identity import NagaFederationIdentity, NagaIdentity


class TestNagaIdentityGeneration:
    """Test NagaIdentity.generate()."""

    def test_generate_creates_valid_identity(self):
        identity = NagaIdentity.generate("test_naga")

        assert identity.agent_id == "test_naga"
        assert identity.public_key.startswith("-----BEGIN PUBLIC KEY-----")
        assert identity.private_key.startswith("-----BEGIN EC PRIVATE KEY-----")
        assert len(identity.fingerprint) == 16

    def test_generate_creates_unique_identities(self):
        id1 = NagaIdentity.generate("naga_1")
        id2 = NagaIdentity.generate("naga_2")

        assert id1.fingerprint != id2.fingerprint
        assert id1.public_key != id2.public_key
        assert id1.private_key != id2.private_key


class TestNagaIdentityFromKeys:
    """Test NagaIdentity.from_keys()."""

    def test_from_keys_computes_fingerprint(self):
        original = NagaIdentity.generate("original")

        loaded = NagaIdentity.from_keys(
            agent_id="loaded",
            private_key=original.private_key,
            public_key=original.public_key,
        )

        assert loaded.fingerprint == original.fingerprint
        assert loaded.agent_id == "loaded"


class TestNagaIdentitySignature:
    """Test sign/verify operations."""

    @pytest.fixture
    def identity(self):
        return NagaIdentity.generate("test")

    def test_sign_returns_bytes(self, identity):
        payload = b"test message"
        signature = identity.sign(payload)

        assert isinstance(signature, bytes)
        assert len(signature) > 0

    def test_verify_valid_signature(self, identity):
        payload = b"test message"
        signature = identity.sign(payload)

        assert identity.verify(payload, signature) is True

    def test_verify_invalid_signature(self, identity):
        payload = b"test message"
        fake_signature = b"definitely not a valid signature"

        assert identity.verify(payload, fake_signature) is False

    def test_verify_wrong_payload(self, identity):
        payload1 = b"original message"
        payload2 = b"tampered message"
        signature = identity.sign(payload1)

        assert identity.verify(payload2, signature) is False

    def test_verify_cross_identity_fails(self):
        id1 = NagaIdentity.generate("signer")
        id2 = NagaIdentity.generate("verifier")

        payload = b"message"
        signature = id1.sign(payload)

        # Signature from id1 should not verify with id2's public key
        assert id2.verify(payload, signature) is False


class TestNagaIdentityBase64:
    """Test base64-encoded signature operations."""

    @pytest.fixture
    def identity(self):
        return NagaIdentity.generate("test")

    def test_sign_b64_returns_string(self, identity):
        payload = b"test"
        sig_b64 = identity.sign_b64(payload)

        assert isinstance(sig_b64, str)
        assert len(sig_b64) > 0

    def test_verify_b64_valid(self, identity):
        payload = b"test"
        sig_b64 = identity.sign_b64(payload)

        assert identity.verify_b64(payload, sig_b64) is True

    def test_verify_b64_invalid(self, identity):
        payload = b"test"

        assert identity.verify_b64(payload, "invalid_base64!!") is False
        assert identity.verify_b64(payload, "dGVzdA==") is False  # Valid b64, wrong sig


class TestNagaIdentityStatus:
    """Test get_status()."""

    def test_get_status_returns_dict(self):
        identity = NagaIdentity.generate("test")
        status = identity.get_status()

        assert status["agent_id"] == "test"
        assert status["fingerprint"] == identity.fingerprint
        assert status["has_private_key"] is True
        assert status["has_public_key"] is True


class TestNagaFederationIdentity:
    """Test NagaFederationIdentity singleton."""

    def setup_method(self):
        # Reset singleton before each test
        NagaFederationIdentity._instance = None

    def test_initialize_creates_singleton(self):
        fed = NagaFederationIdentity.initialize()

        assert fed is not None
        assert fed.identity is not None
        assert fed.identity.agent_id == "naga_federation"

    def test_initialize_returns_same_instance(self):
        fed1 = NagaFederationIdentity.initialize()
        fed2 = NagaFederationIdentity.initialize()

        assert fed1 is fed2

    def test_initialize_with_custom_identity(self):
        custom = NagaIdentity.generate("custom_fed")
        fed = NagaFederationIdentity.initialize(custom)

        assert fed.identity.agent_id == "custom_fed"

    def test_get_returns_none_before_init(self):
        assert NagaFederationIdentity.get() is None

    def test_get_returns_instance_after_init(self):
        NagaFederationIdentity.initialize()

        assert NagaFederationIdentity.get() is not None

    def test_sign_and_verify(self):
        fed = NagaFederationIdentity.initialize()
        payload = b"federation message"

        sig = fed.sign(payload)
        assert fed.verify(payload, sig) is True
