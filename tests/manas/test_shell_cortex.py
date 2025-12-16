"""
OPUS-041: VAK (The Voice) - ShellCortex Mutation Tests

These tests are designed FIRST (TDD) to define the ShellCortex behavior.

SECURITY CRITICAL:
- SAFE commands CAN auto-execute (read-only)
- DANGEROUS commands MUST NEVER auto-execute
- Unknown commands require approval
- Output MUST be captured (no silent execution)

"The voice must speak truth, not chaos."
"""

import pytest

# Import will fail until we implement - that's TDD!
# from vibe_core.plugins.opus_assistant.manas.cortex.shell import (
#     ShellCortex,
#     ShellResult,
#     CommandRisk,
# )


# =============================================================================
# SECTION 1: COMMAND RISK CLASSIFICATION TESTS
# =============================================================================


class TestCommandRiskClassification:
    """Tests for command risk classification - security critical."""

    @pytest.fixture
    def cortex(self, tmp_path):
        """Create ShellCortex with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        return ShellCortex(workspace=tmp_path)

    def test_status_is_safe(self, cortex):
        """
        Mutation killer: 'status' command MUST be classified as SAFE.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["status"])
        assert risk == CommandRisk.SAFE

    def test_state_is_safe(self, cortex):
        """Mutation killer: 'state' command MUST be SAFE."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["state"])
        assert risk == CommandRisk.SAFE

    def test_diff_is_safe(self, cortex):
        """Mutation killer: 'diff' command MUST be SAFE."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["diff"])
        assert risk == CommandRisk.SAFE

    def test_ps_is_safe(self, cortex):
        """Mutation killer: 'ps' command MUST be SAFE."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["ps"])
        assert risk == CommandRisk.SAFE

    def test_plugins_is_safe(self, cortex):
        """Mutation killer: 'plugins' command MUST be SAFE."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["plugins"])
        assert risk == CommandRisk.SAFE

    def test_stop_is_forbidden(self, cortex):
        """
        SECURITY MUTATION KILLER: 'stop' MUST be FORBIDDEN.

        A mutant that makes 'stop' SAFE would allow MANAS to
        shut down the system without approval!
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["stop"])
        assert risk == CommandRisk.FORBIDDEN

    def test_boot_is_forbidden(self, cortex):
        """
        SECURITY MUTATION KILLER: 'boot' MUST be FORBIDDEN.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["boot"])
        assert risk == CommandRisk.FORBIDDEN

    def test_execute_is_forbidden(self, cortex):
        """
        SECURITY MUTATION KILLER: 'execute' MUST be FORBIDDEN.

        Circuit execution could run arbitrary code!
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["execute", "--circuit", "something.yaml"])
        assert risk == CommandRisk.FORBIDDEN

    def test_init_is_forbidden(self, cortex):
        """
        SECURITY MUTATION KILLER: 'init' MUST be FORBIDDEN.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["init", "new_agent"])
        assert risk == CommandRisk.FORBIDDEN

    def test_unknown_command_requires_approval(self, cortex):
        """
        Mutation killer: Unknown commands MUST require approval.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import CommandRisk

        risk = cortex.classify_risk(["unknown_dangerous_cmd"])
        assert risk == CommandRisk.REQUIRES_APPROVAL


# =============================================================================
# SECTION 2: SAFE EXECUTION TESTS
# =============================================================================


class TestSafeExecution:
    """Tests for safe command execution."""

    @pytest.fixture
    def cortex(self, tmp_path):
        """Create ShellCortex with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        return ShellCortex(workspace=tmp_path)

    def test_execute_safe_returns_result(self, cortex):
        """
        Mutation killer: execute_safe MUST return a ShellResult.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellResult

        result = cortex.execute_safe(["status"])
        assert isinstance(result, ShellResult)

    def test_execute_safe_captures_exit_code(self, cortex):
        """
        Mutation killer: Result MUST include exit code.
        """
        result = cortex.execute_safe(["status"])
        assert hasattr(result, "exit_code")
        assert isinstance(result.exit_code, int)

    def test_execute_safe_captures_output(self, cortex):
        """
        MUTATION KILLER: Result MUST capture output.

        The "silent execution" mutant would fail this test.
        """
        result = cortex.execute_safe(["capabilities"])
        assert hasattr(result, "stdout")
        assert result.stdout is not None
        # capabilities returns JSON
        assert len(result.stdout) > 0

    def test_execute_safe_rejects_forbidden(self, cortex):
        """
        SECURITY MUTATION KILLER: execute_safe MUST reject FORBIDDEN commands.
        """

        result = cortex.execute_safe(["stop"])

        # Should fail without executing
        assert result.exit_code != 0
        assert result.blocked is True
        assert "forbidden" in result.error.lower() or "blocked" in result.error.lower()

    def test_execute_safe_rejects_approval_required(self, cortex):
        """
        Mutation killer: execute_safe MUST reject commands that need approval.
        """
        result = cortex.execute_safe(["unknown_command"])

        assert result.blocked is True


# =============================================================================
# SECTION 3: APPROVED EXECUTION TESTS
# =============================================================================


class TestApprovedExecution:
    """Tests for commands that require approval."""

    @pytest.fixture
    def cortex(self, tmp_path):
        """Create ShellCortex with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        return ShellCortex(workspace=tmp_path)

    def test_execute_with_approval_works(self, cortex):
        """
        Mutation killer: Approved commands should execute.
        """
        # This is a command that requires approval
        result = cortex.execute_with_approval(["verify", "test_agent"], approval_token="human_approved")

        # Should have attempted execution (may fail if agent doesn't exist, but shouldn't be blocked)
        assert result.blocked is False

    def test_execute_with_approval_rejects_forbidden(self, cortex):
        """
        SECURITY MUTATION KILLER: Even with approval, FORBIDDEN commands blocked.

        Some commands are SO dangerous that even approval doesn't allow them
        through the cortex (they must be executed directly by human).
        """
        result = cortex.execute_with_approval(["stop"], approval_token="human_approved")

        assert result.blocked is True

    def test_execute_with_approval_requires_token(self, cortex):
        """
        Mutation killer: Empty approval token should be rejected.
        """
        result = cortex.execute_with_approval(["verify", "test"], approval_token="")

        assert result.blocked is True

    def test_execute_with_approval_requires_valid_token(self, cortex):
        """
        Mutation killer: None approval token should be rejected.
        """
        result = cortex.execute_with_approval(["verify", "test"], approval_token=None)

        assert result.blocked is True


# =============================================================================
# SECTION 4: OUTPUT CAPTURE TESTS
# =============================================================================


class TestOutputCapture:
    """Tests for output capture functionality."""

    @pytest.fixture
    def cortex(self, tmp_path):
        """Create ShellCortex with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        return ShellCortex(workspace=tmp_path)

    def test_stdout_captured(self, cortex):
        """Mutation killer: stdout MUST be captured."""
        result = cortex.execute_safe(["help"])

        assert result.stdout is not None
        assert isinstance(result.stdout, str)

    def test_stderr_captured(self, cortex):
        """Mutation killer: stderr MUST be captured."""
        result = cortex.execute_safe(["status"])

        assert hasattr(result, "stderr")

    def test_result_has_command(self, cortex):
        """Mutation killer: Result should record the command."""
        result = cortex.execute_safe(["state"])

        assert hasattr(result, "command")
        assert result.command == ["state"]


# =============================================================================
# SECTION 5: TIMEOUT PROTECTION TESTS
# =============================================================================


class TestTimeoutProtection:
    """Tests for timeout protection."""

    @pytest.fixture
    def cortex(self, tmp_path):
        """Create ShellCortex with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        return ShellCortex(workspace=tmp_path, timeout_seconds=5)

    def test_has_timeout_setting(self, cortex):
        """Mutation killer: Cortex should have timeout setting."""
        assert hasattr(cortex, "_timeout")
        assert cortex._timeout > 0

    def test_default_timeout_is_reasonable(self, tmp_path):
        """Mutation killer: Default timeout should be reasonable (30-60s)."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        cortex = ShellCortex(workspace=tmp_path)
        assert 10 <= cortex._timeout <= 120


# =============================================================================
# SECTION 6: INTEGRATION WITH MANAS
# =============================================================================


class TestManasIntegration:
    """Tests for MANAS integration points."""

    @pytest.fixture
    def cortex(self, tmp_path):
        """Create ShellCortex with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.shell import ShellCortex

        return ShellCortex(workspace=tmp_path)

    def test_can_check_ci_status(self, cortex):
        """
        Integration test: MANAS should be able to check system status.
        """
        result = cortex.execute_safe(["status"])

        # Should execute (may fail if no kernel running, but shouldn't be blocked)
        assert result.blocked is False

    def test_can_get_capabilities(self, cortex):
        """
        Integration test: MANAS should be able to get capabilities.
        """
        result = cortex.execute_safe(["capabilities"])

        assert result.blocked is False
        # Should return JSON
        if result.exit_code == 0:
            import json

            data = json.loads(result.stdout)
            assert "system_commands" in data or "version" in data

    def test_result_to_dict(self, cortex):
        """
        Mutation killer: ShellResult should serialize to dict for memory.
        """
        result = cortex.execute_safe(["status"])

        d = result.to_dict()
        assert isinstance(d, dict)
        assert "exit_code" in d
        assert "command" in d
        assert "blocked" in d
