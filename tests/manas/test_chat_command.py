"""
OPUS-042: SAMVADA - Chat CLI Command Tests.

TDD tests for the 'steward chat' command.

"Every dialogue begins with a single word."
"""

from unittest.mock import patch

# =============================================================================
# SECTION 1: COMMAND REGISTRATION TESTS
# =============================================================================


class TestChatCommandRegistration:
    """Tests for chat command registration in UnifiedCLI."""

    def test_chat_command_exists(self):
        """Mutation killer: 'chat' must be a recognized command."""
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        # Chat should be in prakriti_cmds or have its own handler
        has_chat = "chat" in cli._prakriti_cmds or "chat" in cli._legacy_map or hasattr(cli, "cmd_chat")
        assert has_chat, "Chat command must be registered in UnifiedCLI"

    def test_chat_command_handler_exists(self):
        """Mutation killer: cmd_chat method must exist."""
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        assert hasattr(cli, "cmd_chat"), "UnifiedCLI must have cmd_chat method"


# =============================================================================
# SECTION 2: COMMAND EXECUTION TESTS
# =============================================================================


class TestChatCommandExecution:
    """Tests for chat command execution."""

    def test_chat_with_no_args_shows_usage(self):
        """Mutation killer: No args should show usage."""
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        # Empty args should return error code
        result = cli.cmd_chat([])
        assert result != 0, "Chat with no args should return non-zero"

    def test_chat_with_message_attempts_send(self):
        """Mutation killer: Chat with message should attempt to send."""
        from vibe_core.cli.unified_cli import UnifiedCLI
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        cli = UnifiedCLI()

        # Mock the chat_sync function to avoid real socket
        with patch(
            "vibe_core.cli.unified_cli.chat_sync",
            return_value=SamvadaResponse(success=True, content="Mock response"),
        ) as mock_chat:
            result = cli.cmd_chat(["Hello MANAS"])

            mock_chat.assert_called_once_with("Hello MANAS")

    def test_chat_prints_response_on_success(self, capsys):
        """Mutation killer: Successful chat should print response."""
        from vibe_core.cli.unified_cli import UnifiedCLI
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        cli = UnifiedCLI()

        with patch(
            "vibe_core.cli.unified_cli.chat_sync",
            return_value=SamvadaResponse(success=True, content="MANAS says hello"),
        ):
            result = cli.cmd_chat(["Hello"])

            captured = capsys.readouterr()
            assert "MANAS" in captured.out or "hello" in captured.out
            assert result == 0

    def test_chat_returns_error_on_failure(self, capsys):
        """Mutation killer: Failed chat should return non-zero."""
        from vibe_core.cli.unified_cli import UnifiedCLI
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        cli = UnifiedCLI()

        with patch(
            "vibe_core.cli.unified_cli.chat_sync",
            return_value=SamvadaResponse(success=False, content="", error="Not connected"),
        ):
            result = cli.cmd_chat(["Hello"])

            assert result != 0
            captured = capsys.readouterr()
            assert "error" in captured.out.lower() or "not" in captured.out.lower()


# =============================================================================
# SECTION 3: MULTI-WORD MESSAGE TESTS
# =============================================================================


class TestChatMultiWordMessages:
    """Tests for multi-word message handling."""

    def test_chat_joins_multiple_args(self):
        """Mutation killer: Multiple args should be joined into message."""
        from vibe_core.cli.unified_cli import UnifiedCLI
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        cli = UnifiedCLI()

        with patch(
            "vibe_core.cli.unified_cli.chat_sync",
            return_value=SamvadaResponse(success=True, content="OK"),
        ) as mock_chat:
            cli.cmd_chat(["Status", "report", "please"])

            # Should join with space
            mock_chat.assert_called_once()
            call_args = mock_chat.call_args[0][0]
            assert "Status" in call_args
            assert "report" in call_args

    def test_chat_preserves_quoted_strings(self):
        """Mutation killer: Single quoted arg should be preserved."""
        from vibe_core.cli.unified_cli import UnifiedCLI
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        cli = UnifiedCLI()

        with patch(
            "vibe_core.cli.unified_cli.chat_sync",
            return_value=SamvadaResponse(success=True, content="OK"),
        ) as mock_chat:
            # When shell passes quoted string, it comes as single arg
            cli.cmd_chat(["Status report please"])

            mock_chat.assert_called_once_with("Status report please")


# =============================================================================
# SECTION 4: CLI INTEGRATION TESTS
# =============================================================================


class TestChatCLIIntegration:
    """Integration tests for chat via CLI run()."""

    def test_run_chat_command(self):
        """Integration: 'steward chat <msg>' should work."""
        from vibe_core.cli.unified_cli import UnifiedCLI
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        cli = UnifiedCLI()

        with patch(
            "vibe_core.cli.unified_cli.chat_sync",
            return_value=SamvadaResponse(success=True, content="Hello human"),
        ):
            result = cli.run(["chat", "Hello MANAS"])
            assert result == 0

    def test_run_chat_in_legacy_map_or_prakriti(self):
        """Integration: 'chat' command must be routed correctly."""
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()

        # Chat must be in one of the command maps
        has_route = "chat" in cli._prakriti_cmds or "chat" in cli._legacy_map
        assert has_route, "Chat must be routable via run()"
