"""
TEST CLI CHAITANYA SINGULARITY
==============================

Tests for the graceful CLI protocol.

PULL IN PATTERN:
- Every error → MahamantraGrace (not rejection!)
- Nityananda pattern: accept everyone
- Retry always available

ACINTYA PRINCIPLE:
- AnantaShesha (strict) coexists with ChaitanyaShell (graceful)
- Both implement ShellProtocol
- User chooses based on need
"""

import pytest
from datetime import datetime

from vibe_core.protocols.universal.cli import (
    # Original (strict)
    AnantaResponse,
    ShellProtocol,
    AnantaShesha,
    ANANTA_SHESHA,
    # Chaitanya Singularity (graceful)
    MAHAMANTRA,
    GraceType,
    MahamantraGrace,
    ICliProtocol,
    NavigationResult,
    ChaitanyaShell,
    CHAITANYA_SHELL,
)


class TestMahamantraGrace:
    """Test the MahamantraGrace response type."""

    def test_grace_is_always_truthy(self):
        """Grace is always available - always truthy."""
        grace = MahamantraGrace()
        assert bool(grace) is True

    def test_grace_contains_mahamantra(self):
        """Grace always contains the Mahamantra."""
        grace = MahamantraGrace()
        assert "Hare Kṛṣṇa" in grace.mantra
        assert "Rāma" in grace.mantra

    def test_grace_default_type_is_mahamantra(self):
        """Default grace type is MAHAMANTRA."""
        grace = MahamantraGrace()
        assert grace.grace_type == GraceType.MAHAMANTRA

    def test_grace_retry_allowed_by_default(self):
        """Retry is allowed by default."""
        grace = MahamantraGrace()
        assert grace.retry_allowed is True

    def test_grace_string_contains_message_and_mantra(self):
        """String representation contains message and mantra."""
        grace = MahamantraGrace(message="Test message")
        s = str(grace)
        assert "Test message" in s
        assert "Hare Kṛṣṇa" in s


class TestGraceTypes:
    """Test the different grace types."""

    def test_mahamantra_grace(self):
        """MAHAMANTRA - default grace for everyone."""
        grace = MahamantraGrace(grace_type=GraceType.MAHAMANTRA)
        assert grace.grace_type == GraceType.MAHAMANTRA

    def test_nityananda_grace(self):
        """NITYANANDA - extra mercy for the fallen."""
        grace = MahamantraGrace(grace_type=GraceType.NITYANANDA)
        assert grace.grace_type == GraceType.NITYANANDA

    def test_prabhupada_grace(self):
        """PRABHUPADA - instruction-based grace."""
        grace = MahamantraGrace(grace_type=GraceType.PRABHUPADA)
        assert grace.grace_type == GraceType.PRABHUPADA

    def test_chaitanya_grace(self):
        """CHAITANYA - direct grace from the source."""
        grace = MahamantraGrace(grace_type=GraceType.CHAITANYA)
        assert grace.grace_type == GraceType.CHAITANYA


class TestChaitanyaShell:
    """Test the ChaitanyaShell graceful wrapper."""

    @pytest.fixture
    def shell(self):
        return ChaitanyaShell()

    def test_shell_has_inner_ananta(self, shell):
        """Shell wraps AnantaShesha."""
        assert shell._inner is not None
        assert isinstance(shell._inner, AnantaShesha)

    def test_chant_with_grace_returns_grace_on_invalid_input(self, shell):
        """Invalid input returns grace, not rejection."""
        # Pass invalid input (not CommandContext or CLICapabilityToken)
        result = shell.chant_with_grace("invalid", "test")

        # Should return MahamantraGrace, not rejection!
        assert isinstance(result, MahamantraGrace)
        assert result.retry_allowed is True
        assert "Hare Kṛṣṇa" in result.mantra

    def test_chant_with_grace_nityananda_type_on_error(self, shell):
        """Errors get NITYANANDA grace type."""
        result = shell.chant_with_grace("invalid", "test")
        assert result.grace_type == GraceType.NITYANANDA

    def test_chant_with_grace_preserves_original_error(self, shell):
        """Original error is preserved in grace."""
        result = shell.chant_with_grace("invalid", "test")
        assert result.original_error is not None

    def test_history_tracks_commands(self, shell):
        """History tracks all commands."""
        shell.chant_with_grace("input1", "cmd1")
        shell.chant_with_grace("input2", "cmd2")

        assert len(shell.history) == 2

    def test_retry_returns_grace(self, shell):
        """Retry returns grace when no previous command."""
        result = shell.retry()
        assert isinstance(result, MahamantraGrace)
        assert result.retry_allowed is False  # No previous command

    def test_retry_after_command(self, shell):
        """Retry after command re-executes with grace."""
        shell.chant_with_grace("input", "cmd")
        result = shell.retry()
        assert isinstance(result, MahamantraGrace)
        # History should have 2 entries now
        assert len(shell.history) == 2

    def test_clear_history(self, shell):
        """Clear history returns grace and empties history."""
        shell.chant_with_grace("input", "cmd")
        result = shell.clear_history()

        assert isinstance(result, MahamantraGrace)
        assert len(shell.history) == 0


class TestChaitanyaShellNavigation:
    """Test fractal navigation."""

    @pytest.fixture
    def shell(self):
        return ChaitanyaShell()

    def test_navigate_returns_result(self, shell):
        """Navigate returns NavigationResult."""
        result = shell.navigate("proto/om")
        assert isinstance(result, NavigationResult)

    def test_navigate_preserves_path(self, shell):
        """Navigate preserves the requested path."""
        result = shell.navigate("proto/om")
        assert result.path == "proto/om"

    def test_navigate_includes_grace(self, shell):
        """Navigate includes grace (for unimplemented paths)."""
        result = shell.navigate("unimplemented/path")
        assert result.grace is not None
        assert isinstance(result.grace, MahamantraGrace)


class TestChaitanyaShellReport:
    """Test JSON report generation."""

    @pytest.fixture
    def shell(self):
        return ChaitanyaShell()

    def test_report_returns_json(self, shell):
        """Report returns valid JSON."""
        import json
        report = shell.report(format="json")
        data = json.loads(report)
        assert "session" in data
        assert "mahamantra" in data

    def test_report_contains_mahamantra(self, shell):
        """Report contains the Mahamantra."""
        import json
        report = shell.report()
        data = json.loads(report)
        assert "Hare Kṛṣṇa" in data["mahamantra"]

    def test_report_tracks_grace_given(self, shell):
        """Report tracks how much grace was given."""
        shell.chant_with_grace("invalid1", "cmd1")
        shell.chant_with_grace("invalid2", "cmd2")

        import json
        report = shell.report()
        data = json.loads(report)

        assert data["session"]["grace_given"] == 2


class TestAcintyaPrinciple:
    """
    Test that strict and graceful coexist (Acintya).

    Both AnantaShesha (strict) and ChaitanyaShell (graceful)
    should be valid and usable.
    """

    def test_ananta_shesha_is_strict(self):
        """AnantaShesha rejects invalid input."""
        shell = ANANTA_SHESHA
        result = shell.chant("invalid", "test")

        # Should return AnantaResponse with success=False
        assert isinstance(result, AnantaResponse)
        assert result.success is False
        assert "ANANTA REJECTS" in result.message

    def test_chaitanya_shell_is_graceful(self):
        """ChaitanyaShell gives grace on invalid input."""
        shell = CHAITANYA_SHELL
        result = shell.chant_with_grace("invalid", "test")

        # Should return MahamantraGrace
        assert isinstance(result, MahamantraGrace)
        assert "Hare Kṛṣṇa" in result.mantra

    def test_both_implement_shell_protocol(self):
        """Both shells implement ShellProtocol."""
        # AnantaShesha has chant method
        assert hasattr(ANANTA_SHESHA, 'chant')
        assert callable(ANANTA_SHESHA.chant)

        # ChaitanyaShell has chant method
        assert hasattr(CHAITANYA_SHELL, 'chant')
        assert callable(CHAITANYA_SHELL.chant)

    def test_user_can_choose(self):
        """User can choose between strict and graceful."""
        # Strict mode - for those who want it
        strict_result = ANANTA_SHESHA.chant("invalid", "test")
        assert isinstance(strict_result, AnantaResponse)

        # Graceful mode - for Kali Yuga
        graceful_result = CHAITANYA_SHELL.chant_with_grace("invalid", "test")
        assert isinstance(graceful_result, MahamantraGrace)


class TestSingletons:
    """Test singleton instances."""

    def test_ananta_shesha_singleton(self):
        """ANANTA_SHESHA is available as singleton."""
        assert ANANTA_SHESHA is not None
        assert isinstance(ANANTA_SHESHA, AnantaShesha)

    def test_chaitanya_shell_singleton(self):
        """CHAITANYA_SHELL is available as singleton."""
        assert CHAITANYA_SHELL is not None
        assert isinstance(CHAITANYA_SHELL, ChaitanyaShell)

    def test_mahamantra_constant(self):
        """MAHAMANTRA constant is available."""
        assert MAHAMANTRA is not None
        assert "Hare Kṛṣṇa" in MAHAMANTRA
        assert "Rāma" in MAHAMANTRA
