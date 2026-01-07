import pytest

from vibe_core.steward.emergency import NullSteward


class TestEmergencyLockdown:
    def test_null_steward_identity(self):
        """Verify the Airbag has the correct dummy identity."""
        steward = NullSteward()
        assert steward.identity.fingerprint == "EMERGENCY_OVERRIDE_000"
        assert "LOCKED" in steward.identity.public_key_pem
        assert steward.config.role == "SYSTEM_LOCKDOWN"

    def test_safe_ops_allowed(self):
        """Verify harmless introspection is allowed."""
        steward = NullSteward()
        # These should pass
        assert steward.sign_off("status", {}) is True
        assert steward.sign_off("help", {}) is True
        assert steward.sign_off("version", {}) is True
        assert steward.sign_off("about", {}) is True

    def test_dangerous_ops_blocked(self):
        """Verify everything else is BLOCKED."""
        steward = NullSteward()

        # Deploy, start, stop, git operations - all blocked
        assert steward.sign_off("deploy", {}) is False
        assert steward.sign_off("start", {}) is False
        assert steward.sign_off("git_commit", {}) is False
        assert steward.sign_off("anything_else", {}) is False
