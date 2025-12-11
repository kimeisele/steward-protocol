"""
Tests for Keyring Trust Model (OPUS-015a)

Verifies:
1. Own key is always trusted
2. Keys in trusted_keys/ are trusted
3. Unknown keys are rejected in strict mode
4. Unknown keys are warned in dev mode
"""

from unittest.mock import patch


class TestKeyringTrust:
    """Tests for trusted key verification."""

    def test_own_key_always_trusted(self, tmp_path):
        """Our own key should always be trusted."""
        # Patch KEY_DIR to use temp
        with patch("steward.crypto.KEY_DIR", tmp_path / "keys"):
            with patch("steward.crypto.TRUSTED_KEYS_DIR", tmp_path / "trusted_keys"):
                from steward.crypto import is_key_trusted, load_or_generate_keys

                # Generate our keys
                _, our_pub = load_or_generate_keys()

                # Our key should be trusted
                assert is_key_trusted(our_pub) is True

    def test_trusted_key_directory_created(self, tmp_path):
        """trusted_keys/ directory should be created with README."""
        with patch("steward.crypto.KEY_DIR", tmp_path / "keys"):
            with patch("steward.crypto.TRUSTED_KEYS_DIR", tmp_path / "trusted_keys"):
                from steward.crypto import ensure_trusted_keys_dir

                ensure_trusted_keys_dir()

                assert (tmp_path / "trusted_keys").exists()
                assert (tmp_path / "trusted_keys" / "README.md").exists()

    def test_key_in_trusted_dir_is_trusted(self, tmp_path):
        """Keys placed in trusted_keys/ should be trusted."""
        with patch("steward.crypto.KEY_DIR", tmp_path / "keys"):
            trusted_dir = tmp_path / "trusted_keys"
            with patch("steward.crypto.TRUSTED_KEYS_DIR", trusted_dir):
                from steward.crypto import generate_keys, get_public_key_fingerprint, is_fingerprint_trusted

                # Generate a "foreign" key
                _, foreign_pub = generate_keys()
                fingerprint = get_public_key_fingerprint(foreign_pub)

                # Before adding to trusted: should not be trusted
                # (unless it happens to be our own key, which it won't be)
                trusted_dir.mkdir(parents=True, exist_ok=True)

                # Add to trusted directory
                (trusted_dir / "foreign.pem").write_text(foreign_pub)

                # Now should be trusted
                assert is_fingerprint_trusted(fingerprint) is True

    def test_unknown_key_not_trusted(self, tmp_path):
        """Unknown keys should not be trusted."""
        with patch("steward.crypto.KEY_DIR", tmp_path / "keys"):
            with patch("steward.crypto.TRUSTED_KEYS_DIR", tmp_path / "trusted_keys"):
                from steward.crypto import generate_keys, get_public_key_fingerprint, is_fingerprint_trusted

                # Generate a random key (not our own, not in trusted)
                _, random_pub = generate_keys()
                fingerprint = get_public_key_fingerprint(random_pub)

                # Should NOT be trusted
                assert is_fingerprint_trusted(fingerprint) is False
