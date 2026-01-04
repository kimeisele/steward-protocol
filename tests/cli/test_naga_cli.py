"""
Tests for NAGA CLI.

Tests the NAGA Federation CLI commands:
- status, scan, detect, flood, bite, remediate, audit
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestNagaCLIInit:
    """Test NAGA CLI initialization."""

    def test_cli_init(self):
        """Should initialize with correct properties."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()

        assert cli.meta.command == "naga"
        assert cli.meta.domain == "security"
        assert "status" in cli.meta.subcommands
        assert "scan" in cli.meta.subcommands


class TestNagaCLIRun:
    """Test CLI run dispatch."""

    def test_run_no_args_shows_usage(self, capsys):
        """Should show usage when no args provided."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        result = cli.run([])

        captured = capsys.readouterr()
        assert "NAGA FEDERATION CLI" in captured.out
        assert result == 0

    def test_run_help_shows_usage(self, capsys):
        """Should show usage for help command."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        result = cli.run(["help"])

        captured = capsys.readouterr()
        assert "NAGA FEDERATION CLI" in captured.out
        assert result == 0

    def test_run_unknown_command(self, capsys):
        """Should return error for unknown command."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        result = cli.run(["unknown_command"])

        captured = capsys.readouterr()
        assert "Unknown command" in captured.out
        assert result == 1


class TestNagaCLIStatus:
    """Test status command."""

    def test_status_without_federation(self, capsys):
        """Should show message when federation not available."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        cli._federation = None

        result = cli.cmd_status([])

        captured = capsys.readouterr()
        assert "NAGA FEDERATION STATUS" in captured.out
        assert "not initialized" in captured.out
        assert result == 0

    def test_status_with_mock_federation(self, capsys):
        """Should show federation status when available."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()

        # Mock federation
        mock_sesha = MagicMock()
        mock_sesha.get_status.return_value = MagicMock(healthy=True)

        mock_federation = MagicMock()
        mock_federation.is_ready.return_value = True
        mock_federation.get_status.return_value = {}
        mock_federation.sesha = mock_sesha
        mock_federation.vasuki = None
        mock_federation.takshaka = None
        mock_federation.flood_manager = None
        mock_federation.commit_watcher = None

        cli._federation = mock_federation

        result = cli.cmd_status([])

        captured = capsys.readouterr()
        assert "HEALTHY" in captured.out
        assert result == 0


class TestNagaCLIScan:
    """Test scan command."""

    def test_scan_finds_issues(self, capsys, tmp_path):
        """Should find issues in Python files."""
        from vibe_core.cli.naga_cli import NagaCLI

        # Create test file with issues
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def bad_function():
    try:
        x = 1
    except: pass  # Silent failure

    with open("file.txt") as f:  # VFS bypass
        data = f.read()

    def inner(x: Any) -> Any:  # Any type
        return x
""")

        cli = NagaCLI()
        cli._repo_root = tmp_path

        result = cli.cmd_scan(["--path", str(tmp_path)])

        captured = capsys.readouterr()
        assert "NAGA CODEBASE SCAN" in captured.out
        assert "TOTAL ISSUES:" in captured.out

    def test_scan_specific_type(self, capsys, tmp_path):
        """Should filter by scan type."""
        from vibe_core.cli.naga_cli import NagaCLI

        test_file = tmp_path / "test.py"
        test_file.write_text("except: pass")

        cli = NagaCLI()
        cli._repo_root = tmp_path

        result = cli.cmd_scan(["--path", str(tmp_path), "--type", "silent"])

        captured = capsys.readouterr()
        assert "Type: silent" in captured.out


class TestNagaCLIDetect:
    """Test detect command."""

    def test_detect_without_federation(self, capsys, tmp_path):
        """Should do file-based detection when federation unavailable."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        cli._federation = None
        cli._repo_root = tmp_path

        result = cli.cmd_detect([])

        captured = capsys.readouterr()
        assert "NAGA DRIFT DETECTION" in captured.out
        assert result == 0


class TestNagaCLIFlood:
    """Test flood command."""

    def test_flood_without_manager(self, capsys):
        """Should show error when FloodManager unavailable."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        cli._federation = None

        result = cli.cmd_flood([])

        captured = capsys.readouterr()
        assert "not available" in captured.out
        assert result == 1


class TestNagaCLIBite:
    """Test bite command."""

    def test_bite_no_args(self, capsys):
        """Should show usage when no args."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()

        result = cli.cmd_bite([])

        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert result == 1

    def test_bite_with_type(self, capsys):
        """Should record violation."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        cli._federation = None

        result = cli.cmd_bite(["TEST_VIOLATION"])

        captured = capsys.readouterr()
        assert "TAKSHAKA BITE" in captured.out
        assert "TEST_VIOLATION" in captured.out


class TestNagaCLIRemediate:
    """Test remediate command."""

    def test_remediate_no_args_shows_help(self, capsys):
        """Should show help when no args."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()

        result = cli.cmd_remediate([])

        captured = capsys.readouterr()
        assert "Available remediations" in captured.out
        assert result == 0


class TestNagaCLIAudit:
    """Test audit command."""

    def test_audit_without_sesha(self, capsys):
        """Should show error when Sesha unavailable."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()
        cli._federation = None

        result = cli.cmd_audit([])

        captured = capsys.readouterr()
        assert "not available" in captured.out
        assert result == 1


class TestNagaCLIScanHelpers:
    """Test scan helper methods."""

    def test_find_silent_failures(self):
        """Should find except: pass patterns."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()

        content = """
def test():
    try:
        x = 1
    except: pass
    except ValueError: pass
"""
        issues = cli._find_silent_failures(content, Path("test.py"))

        assert len(issues) == 2

    def test_find_security_issues(self):
        """Should find security issues."""
        from vibe_core.cli.naga_cli import NagaCLI

        cli = NagaCLI()

        content = """
eval("code")
exec("code")
__import__("module")
"""
        issues = cli._find_security_issues(content, Path("test.py"))

        assert len(issues) >= 3
        assert any(i["type"] == "EVAL" for i in issues)
        assert any(i["type"] == "EXEC" for i in issues)
