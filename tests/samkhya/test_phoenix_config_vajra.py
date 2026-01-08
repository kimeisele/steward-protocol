import pytest

from vibe_core.phoenix.config import PhoenixConfig
from vibe_core.protocols.universal import (
    AccessDeniedError,
    KeyNotFoundError,
    ReadResult,
    ReadWriteProtocol,
    SovereignContext,
)


class TestPhoenixConfigVajra:
    """
    Vajra Hardening tests for PhoenixConfig (ReadWriteProtocol).
    Verifies GAD-000 compliance and Anti-Mayavad enforcement.
    """

    @pytest.fixture
    def config(self, tmp_path):
        """Create a transient PhoenixConfig for testing."""
        # Use tmp_path as config dir to avoid messing with real config
        return PhoenixConfig.from_files(config_dir=tmp_path / "config")

    def test_protocol_compliance(self, config):
        """Verify PhoenixConfig implements ReadWriteProtocol."""
        assert isinstance(config, ReadWriteProtocol)

    def test_read_traversal(self, config):
        """Verify dot-notation traversal."""
        # Inject mock data directly for test
        config._sections["mock"] = {"deep": {"value": 42}}

        # Test Read
        result = config.read("mock.deep.value")
        assert isinstance(result, ReadResult)
        assert result.value == 42
        assert result.writer is None  # Default system provenance

    def test_read_not_found(self, config):
        """Verify KeyNotFoundError."""
        with pytest.raises(KeyNotFoundError):
            config.read("non_existent.key")

    def test_write_audit(self, config):
        """Verify Write enforces Anti-Mayavad."""
        config._sections["mock"] = {"mutable": 10}

        # 1. Attempt write without context (Maya)
        with pytest.raises(AccessDeniedError):
            config.write("mock.mutable", 20, context=None)

        # 2. Attempt write with Sovereign Context (Satyam)
        ctx = SovereignContext(identity_id="test_agent", signature="sig_123")

        # Mock save() to prevent file IO errors in test env without setup
        original_save = config.save
        config.save = lambda: True

        try:
            config.write("mock.mutable", 20, context=ctx)

            # Verify update
            result = config.read("mock.mutable")
            assert result.value == 20
        finally:
            config.save = original_save

    def test_exists(self, config):
        """Verify existence check."""
        config._sections["mock"] = {"key": "value"}
        assert config.exists("mock.key") is True
        assert config.exists("mock.missing") is False
