"""
Tests for KarkotakaService - The Crypto Lord.

Verifies:
- Signing and verification
- Encryption and decryption
- Secrets vault operations
- Key management
- Obfuscation
"""

import tempfile
from pathlib import Path

import pytest

from vibe_core.naga.services.karkotaka import KarkotakaService
from vibe_core.protocols.naga import EncryptedPayload, SignedContent


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault directory."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    return vault_dir


@pytest.fixture
def karkotaka(temp_vault):
    """Create a KarkotakaService with temp vault."""
    return KarkotakaService(vault_dir=temp_vault)


class TestKarkotakaBasics:
    """Basic initialization tests."""

    def test_initialization(self, karkotaka):
        """Test service initializes correctly."""
        assert karkotaka is not None
        assert karkotaka._operations_count == 0

    def test_get_status(self, karkotaka):
        """Test get_status returns valid status."""
        status = karkotaka.get_status()
        assert status is not None
        assert "keys=" in status.message


class TestSigning:
    """Signing and verification tests."""

    def test_sign_returns_signed_content(self, karkotaka):
        """Test signing returns SignedContent."""
        content = "Hello, Karkotaka!"
        signed = karkotaka.sign(content)

        assert isinstance(signed, SignedContent)
        assert signed.content == content
        assert signed.timestamp > 0

    def test_sign_with_keys_has_signature(self, karkotaka):
        """Test signing with keys produces signature."""
        if not karkotaka._private_key:
            pytest.skip("No private key available")

        signed = karkotaka.sign("Test content")
        assert signed.signature != ""
        assert signed.signer_fingerprint != ""

    def test_verify_own_signature(self, karkotaka):
        """Test verifying our own signature."""
        if not karkotaka._private_key:
            pytest.skip("No private key available")

        content = "Verify me"
        signed = karkotaka.sign(content)

        # Self-signed should be trusted
        is_valid = karkotaka.verify_with_key(signed, karkotaka.get_public_key())
        assert is_valid is True

    def test_verify_tampered_content_fails(self, karkotaka):
        """Test that tampering with content invalidates signature."""
        if not karkotaka._private_key:
            pytest.skip("No private key available")

        signed = karkotaka.sign("Original content")

        # Tamper with content
        tampered = SignedContent(
            content="Tampered content",  # Changed!
            signature=signed.signature,
            signer_fingerprint=signed.signer_fingerprint,
            timestamp=signed.timestamp,
        )

        is_valid = karkotaka.verify_with_key(tampered, karkotaka.get_public_key())
        assert is_valid is False


class TestEncryption:
    """Encryption and decryption tests."""

    def test_encrypt_returns_payload(self, karkotaka):
        """Test encryption returns EncryptedPayload."""
        plaintext = b"Secret message"
        payload = karkotaka.encrypt(plaintext)

        assert isinstance(payload, EncryptedPayload)
        assert payload.ciphertext != plaintext  # Should be different
        assert payload.key_id != ""

    def test_decrypt_round_trip(self, karkotaka):
        """Test encrypt then decrypt returns original."""
        original = b"Top secret data!"
        payload = karkotaka.encrypt(original)
        decrypted = karkotaka.decrypt(payload)

        assert decrypted == original

    def test_decrypt_wrong_nonce_fails(self, karkotaka):
        """Test decryption with wrong nonce fails."""
        payload = karkotaka.encrypt(b"Test data")

        # Corrupt the nonce
        bad_payload = EncryptedPayload(
            ciphertext=payload.ciphertext,
            nonce=b"wrong_nonce!",
            key_id=payload.key_id,
            algorithm=payload.algorithm,
        )

        with pytest.raises(ValueError):
            karkotaka.decrypt(bad_payload)

    def test_encrypt_empty_data(self, karkotaka):
        """Test encrypting empty data works."""
        payload = karkotaka.encrypt(b"")
        decrypted = karkotaka.decrypt(payload)
        assert decrypted == b""

    def test_encrypt_large_data(self, karkotaka):
        """Test encrypting large data works."""
        large_data = b"X" * 100000  # 100KB
        payload = karkotaka.encrypt(large_data)
        decrypted = karkotaka.decrypt(payload)
        assert decrypted == large_data


class TestSecretsVault:
    """Secrets vault tests."""

    def test_store_and_get_secret(self, karkotaka):
        """Test storing and retrieving a secret."""
        name = "API_KEY"
        value = "sk-secret-12345"

        success = karkotaka.store_secret(name, value)
        assert success is True

        retrieved = karkotaka.get_secret(name)
        assert retrieved == value

    def test_get_nonexistent_secret_returns_none(self, karkotaka):
        """Test getting non-existent secret returns None."""
        result = karkotaka.get_secret("DOES_NOT_EXIST")
        assert result is None

    def test_delete_secret(self, karkotaka):
        """Test deleting a secret."""
        karkotaka.store_secret("TO_DELETE", "value")
        assert karkotaka.get_secret("TO_DELETE") == "value"

        success = karkotaka.delete_secret("TO_DELETE")
        assert success is True
        assert karkotaka.get_secret("TO_DELETE") is None

    def test_delete_nonexistent_secret_returns_false(self, karkotaka):
        """Test deleting non-existent secret returns False."""
        result = karkotaka.delete_secret("NEVER_EXISTED")
        assert result is False

    def test_list_secrets(self, karkotaka):
        """Test listing secret names."""
        karkotaka.store_secret("SECRET_A", "a")
        karkotaka.store_secret("SECRET_B", "b")

        names = karkotaka.list_secrets()
        assert "SECRET_A" in names
        assert "SECRET_B" in names

    def test_secrets_persist_across_instances(self, temp_vault):
        """Test that secrets persist when service is recreated."""
        # Store with first instance
        k1 = KarkotakaService(vault_dir=temp_vault)
        k1.store_secret("PERSISTENT", "value123")

        # Retrieve with second instance
        k2 = KarkotakaService(vault_dir=temp_vault)
        retrieved = k2.get_secret("PERSISTENT")
        assert retrieved == "value123"


class TestKeyManagement:
    """Key management tests."""

    def test_get_public_key(self, karkotaka):
        """Test getting public key."""
        public_key = karkotaka.get_public_key()
        # Should be PEM format if keys loaded
        if public_key:
            assert "BEGIN" in public_key or public_key == ""

    def test_get_fingerprint(self, karkotaka):
        """Test getting fingerprint."""
        fingerprint = karkotaka.get_fingerprint()
        # Should be hex string
        if fingerprint:
            assert len(fingerprint) == 16

    def test_own_key_is_trusted(self, karkotaka):
        """Test that our own key is trusted."""
        fingerprint = karkotaka.get_fingerprint()
        if fingerprint:
            assert karkotaka.is_key_trusted(fingerprint) is True

    def test_unknown_key_not_trusted(self, karkotaka):
        """Test that unknown key is not trusted."""
        fake_fingerprint = "0000000000000000"
        assert karkotaka.is_key_trusted(fake_fingerprint) is False

    def test_revoke_key(self, karkotaka):
        """Test revoking a key."""
        fake_fingerprint = "1111111111111111"

        success = karkotaka.revoke_key(fake_fingerprint)
        assert success is True

        # Now should not be trusted
        assert karkotaka.is_key_trusted(fake_fingerprint) is False


class TestObfuscation:
    """Obfuscation tests."""

    def test_obfuscate_changes_data(self, karkotaka):
        """Test that obfuscation changes the data."""
        original = "Hello, World!"
        obfuscated = karkotaka.obfuscate(original)

        assert obfuscated != original

    def test_obfuscate_deobfuscate_round_trip(self, karkotaka):
        """Test obfuscate then deobfuscate returns original."""
        original = "Secret message to hide"
        obfuscated = karkotaka.obfuscate(original)
        recovered = karkotaka.deobfuscate(obfuscated)

        assert recovered == original

    def test_obfuscate_empty_string(self, karkotaka):
        """Test obfuscating empty string."""
        obfuscated = karkotaka.obfuscate("")
        recovered = karkotaka.deobfuscate(obfuscated)
        assert recovered == ""

    def test_obfuscate_special_characters(self, karkotaka):
        """Test obfuscating special characters."""
        original = "Special: äöü 日本語 🔐"
        obfuscated = karkotaka.obfuscate(original)
        recovered = karkotaka.deobfuscate(obfuscated)
        assert recovered == original


class TestOperationsTracking:
    """Operations tracking tests."""

    def test_operations_count_increments(self, karkotaka):
        """Test that operations are counted."""
        initial = karkotaka._operations_count

        karkotaka.sign("test")
        karkotaka.encrypt(b"test")
        karkotaka.obfuscate("test")

        assert karkotaka._operations_count > initial

    def test_heartbeat_updates(self, karkotaka):
        """Test that heartbeat updates on operations."""
        initial = karkotaka._last_heartbeat

        import time

        time.sleep(0.01)
        karkotaka.sign("test")

        assert karkotaka._last_heartbeat > initial
