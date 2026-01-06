"""
Tests for @cli_governed decorator and CLICapabilityToken.

TDD: Test the DNA injection pattern for CLI commands.

The @cli_governed decorator is Level -1 DNA that automatically applies
NAGA governance to any CLI method - no manual hook wiring needed.
"""

from datetime import datetime, timedelta

import pytest

from vibe_core.naga.services.base import cli_governed
from vibe_core.protocols.cli_execution import CLICapabilityToken

# =============================================================================
# CLICapabilityToken Tests
# =============================================================================


class TestCLICapabilityToken:
    """Test the signed capability token (not handwritten Zettel!)."""

    def test_create_token_basic(self):
        """Token can be created with capabilities."""
        token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status", "cli.naga.scan.read"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        assert token.subject == "agent_007"
        assert "cli.naga.status" in token.capabilities
        assert token.issuer == "KERNEL"
        assert token.token_id  # Auto-generated

    def test_token_has_capability(self):
        """Token correctly reports capability presence."""
        token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        assert token.has_capability("cli.naga.status") is True
        assert token.has_capability("cli.naga.chaos.run") is False

    def test_token_expiry(self):
        """Expired tokens are detected."""
        # Create expired token
        token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status"],
            issued_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),  # Already expired
            issuer="KERNEL",
        )

        assert token.is_expired() is True

        # Create valid token
        valid_token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        assert valid_token.is_expired() is False

    def test_token_to_claims(self):
        """Token serializes to claims dict."""
        token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        claims = token.to_claims()

        assert claims["sub"] == "agent_007"
        assert claims["caps"] == ["cli.naga.status"]
        assert claims["iss"] == "KERNEL"
        assert "iat" in claims
        assert "exp" in claims

    def test_anonymous_token(self):
        """Anonymous token has limited capabilities."""
        token = CLICapabilityToken.create_anonymous()

        assert token.subject == "anonymous"
        assert token.has_capability("cli.public") is True
        assert token.has_capability("cli.naga.chaos.run") is False
        assert token.issuer == "SYSTEM"

    def test_token_signing_and_verification_hmac(self):
        """Token can be signed and verified (HMAC fallback)."""
        # Use a secret key (HMAC fallback when nacl not available)
        secret_key = b"test_secret_key_32_bytes_long!!!"

        # Issue signed token
        token = CLICapabilityToken.issue(
            subject="agent_007",
            capabilities=["cli.naga.status"],
            issuer="KERNEL",
            issuer_private_key=secret_key,
            ttl_seconds=3600,
        )

        # Token should have signature
        assert token.signature
        assert len(token.signature) > 0

        # Verify with correct key
        assert token.verify(secret_key) is True

        # Verify fails with wrong key
        wrong_key = b"wrong_key_32_bytes_long_wrong!!!"
        assert token.verify(wrong_key) is False

    def test_token_tampering_detected(self):
        """Tampering with token claims invalidates signature."""
        secret_key = b"test_secret_key_32_bytes_long!!!"

        # Issue signed token
        token = CLICapabilityToken.issue(
            subject="agent_007",
            capabilities=["cli.naga.status"],
            issuer="KERNEL",
            issuer_private_key=secret_key,
        )

        # Verify original
        assert token.verify(secret_key) is True

        # Tamper with capabilities
        token.capabilities.append("cli.naga.chaos.run")

        # Verification should now fail (claims changed)
        assert token.verify(secret_key) is False


# =============================================================================
# @cli_governed Decorator Tests
# =============================================================================


class TestCLIGovernedDecorator:
    """Test the Level -1 DNA injection decorator."""

    def test_decorator_basic_execution(self):
        """Decorated method executes normally without NAGAs."""

        class MockCLI:
            @cli_governed()
            def cmd_status(self, args: list) -> int:
                return 0

        cli = MockCLI()
        result = cli.cmd_status([])

        assert result == 0

    def test_decorator_with_return_value(self):
        """Decorated method returns correct value."""

        class MockCLI:
            @cli_governed()
            def cmd_count(self, args: list) -> int:
                return len(args)

        cli = MockCLI()

        assert cli.cmd_count([]) == 0
        assert cli.cmd_count(["a", "b", "c"]) == 3

    def test_decorator_propagates_exceptions(self):
        """Decorated method propagates exceptions."""

        class MockCLI:
            @cli_governed()
            def cmd_fail(self, args: list) -> int:
                raise RuntimeError("Intentional failure")

        cli = MockCLI()

        with pytest.raises(RuntimeError, match="Intentional failure"):
            cli.cmd_fail([])

    def test_decorator_capability_enforcement(self):
        """Decorator enforces required capabilities."""

        class MockCLI:
            @cli_governed(capabilities_required=["cli.naga.chaos.run"])
            def cmd_chaos(self, args: list, capability_token=None) -> int:
                return 0

        cli = MockCLI()

        # Token without required capability
        token_without_cap = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status"],  # Missing cli.naga.chaos.run
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        with pytest.raises(PermissionError, match="Missing capability"):
            cli.cmd_chaos([], capability_token=token_without_cap)

        # Token with required capability
        token_with_cap = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.chaos.run"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        result = cli.cmd_chaos([], capability_token=token_with_cap)
        assert result == 0

    def test_decorator_extracts_token_from_context(self):
        """Decorator extracts token from context object."""

        class MockContext:
            def __init__(self, token):
                self.capability_token = token

        class MockCLI:
            @cli_governed(capabilities_required=["cli.test"])
            def cmd_test(self, context) -> int:
                return 0

        cli = MockCLI()

        # Token in context object
        token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.test"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )
        context = MockContext(token)

        result = cli.cmd_test(context)
        assert result == 0

    def test_decorator_graceful_without_nagas(self):
        """Decorator works gracefully when NAGAs not available."""

        class MockCLI:
            @cli_governed(validate_args=True)
            def cmd_scan(self, args: list) -> int:
                return len(args)

        cli = MockCLI()

        # Should work even though ServiceRegistry has no NAGAs
        result = cli.cmd_scan(["file1.py", "file2.py"])
        assert result == 2


# =============================================================================
# Integration: Token + Decorator
# =============================================================================


class TestCLIGovernedIntegration:
    """Integration tests for token + decorator working together."""

    def test_full_capability_flow(self):
        """Full flow: issue token, use decorator, enforce caps."""
        secret_key = b"integration_test_key_32_bytes!!"

        # 1. Kernel issues token with specific capabilities
        token = CLICapabilityToken.issue(
            subject="integration_agent",
            capabilities=["cli.naga.status", "cli.naga.scan.read"],
            issuer="KERNEL",
            issuer_private_key=secret_key,
        )

        # 2. Token is valid
        assert token.verify(secret_key) is True
        assert not token.is_expired()

        # 3. CLI command requires capability that token has
        class IntegrationCLI:
            @cli_governed(capabilities_required=["cli.naga.scan.read"])
            def cmd_scan(self, args: list, capability_token=None) -> str:
                return f"Scanned {len(args)} files"

        cli = IntegrationCLI()
        result = cli.cmd_scan(["a.py", "b.py"], capability_token=token)
        assert result == "Scanned 2 files"

        # 4. Command requiring cap that token DOESN'T have
        class RestrictedCLI:
            @cli_governed(capabilities_required=["cli.naga.chaos.run"])
            def cmd_chaos(self, args: list, capability_token=None) -> str:
                return "Chaos!"

        restricted = RestrictedCLI()
        with pytest.raises(PermissionError):
            restricted.cmd_chaos([], capability_token=token)

    def test_token_expiry_not_checked_by_decorator(self):
        """
        Note: The decorator checks capabilities, not expiry.
        Expiry should be checked at token issuance/validation layer.
        """
        # Create expired token
        token = CLICapabilityToken(
            subject="expired_agent",
            capabilities=["cli.test"],
            issued_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),
            issuer="KERNEL",
        )

        assert token.is_expired() is True

        class MockCLI:
            @cli_governed(capabilities_required=["cli.test"])
            def cmd_test(self, args: list, capability_token=None) -> int:
                return 0

        cli = MockCLI()

        # Decorator doesn't check expiry - that's a separate concern
        # The token validation layer should check expiry before passing to CLI
        result = cli.cmd_test([], capability_token=token)
        assert result == 0
