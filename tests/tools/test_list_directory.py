"""
THE GREAT PURGE - Phase 1: ListDirectoryTool Tests
===================================================

Tests for vibe_core/tools/list_directory.py

These tests are designed to KILL mutants:
- Comparison mutations (>, <, ==, !=)
- Return value mutations (return x → return None)

Run with: pytest tests/tools/test_list_directory.py -v
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.tools.list_directory import ListDirectoryTool
from vibe_core.tools.tool_protocol import ToolResult


class TestListDirectoryTool:
    """Tests for ListDirectoryTool."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return ListDirectoryTool()

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create a temporary workspace with test files."""
        # Create some files and directories
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.py").write_text("content2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.txt").write_text("nested")
        (tmp_path / ".hidden").write_text("hidden file")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".vibe").mkdir()  # Special case - should be visible
        return tmp_path

    # =========================================================================
    # Property Tests
    # =========================================================================

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "list_directory"

    def test_description_property(self, tool):
        """Test that description property returns correct value."""
        assert "List files" in tool.description or "list" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "path" in schema
        assert schema["path"]["type"] == "string"
        assert schema["path"]["required"] is False

    # =========================================================================
    # Validation Tests
    # =========================================================================

    def test_validate_empty_params(self, tool):
        """Test validation with empty parameters (valid - path is optional)."""
        # Should not raise
        tool.validate({})

    def test_validate_valid_path_string(self, tool):
        """Test validation with valid path string."""
        tool.validate({"path": "/some/path"})

    def test_validate_invalid_path_type(self, tool):
        """Test validation rejects non-string path."""
        with pytest.raises(TypeError) as exc_info:
            tool.validate({"path": 123})
        assert "string" in str(exc_info.value).lower()

    def test_validate_path_type_list(self, tool):
        """Test validation rejects list path."""
        with pytest.raises(TypeError):
            tool.validate({"path": ["/path"]})

    # =========================================================================
    # Execute Tests - Success Cases
    # =========================================================================

    def test_execute_current_directory(self, tool, temp_workspace):
        """Test listing current directory."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace)})

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.error is None
        assert "file1.txt" in result.output
        assert "file2.py" in result.output
        assert "subdir" in result.output

    def test_execute_subdirectory(self, tool, temp_workspace):
        """Test listing a subdirectory."""
        subdir = temp_workspace / "subdir"
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(subdir)})

        assert result.success is True
        assert "nested.txt" in result.output

    def test_execute_empty_directory(self, tool, temp_workspace):
        """Test listing an empty directory."""
        empty_dir = temp_workspace / "empty"
        empty_dir.mkdir()

        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(empty_dir)})

        assert result.success is True
        assert "empty directory" in result.output.lower()

    def test_execute_hidden_files_filtered(self, tool, temp_workspace):
        """Test that hidden files are filtered out (except .vibe)."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace)})

        assert result.success is True
        assert ".hidden" not in result.output
        assert ".git" not in result.output
        # .vibe should be visible
        assert ".vibe" in result.output

    def test_execute_metadata_contains_count(self, tool, temp_workspace):
        """Test that metadata contains item count."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace)})

        assert result.metadata is not None
        assert "count" in result.metadata
        assert result.metadata["count"] >= 3  # At least file1, file2, subdir, .vibe

    def test_execute_metadata_contains_path(self, tool, temp_workspace):
        """Test that metadata contains resolved path."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace)})

        assert result.metadata is not None
        assert "path" in result.metadata

    # =========================================================================
    # Execute Tests - Error Cases
    # =========================================================================

    def test_execute_path_not_found(self, tool, temp_workspace):
        """Test error when path does not exist."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace / "nonexistent")})

        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_execute_path_is_file(self, tool, temp_workspace):
        """Test error when path is a file, not directory."""
        file_path = temp_workspace / "file1.txt"
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(file_path)})

        assert result.success is False
        assert result.error is not None
        assert "not a directory" in result.error.lower()

    def test_execute_outside_workspace_blocked(self, tool, temp_workspace):
        """Test that paths outside workspace are blocked (security)."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": "/tmp"})

        assert result.success is False
        assert result.error is not None
        assert "denied" in result.error.lower() or "outside" in result.error.lower()

    def test_execute_parent_directory_blocked(self, tool, temp_workspace):
        """Test that parent directory traversal is blocked."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace.parent)})

        assert result.success is False
        assert "denied" in result.error.lower() or "outside" in result.error.lower()

    # =========================================================================
    # Execute Tests - Edge Cases
    # =========================================================================

    def test_execute_default_path(self, tool, temp_workspace, monkeypatch):
        """Test that empty path defaults to current directory."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({})

        assert result.success is True
        # Should list temp_workspace contents

    def test_execute_output_is_sorted(self, tool, temp_workspace):
        """Test that output is sorted alphabetically."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace)})

        lines = [line for line in result.output.split("\n") if line]
        # Output lines are sorted as strings (including [TYPE] prefix)
        assert lines == sorted(lines)

    def test_execute_distinguishes_files_and_dirs(self, tool, temp_workspace):
        """Test that output distinguishes files from directories."""
        with patch.object(Path, "cwd", return_value=temp_workspace):
            result = tool.execute({"path": str(temp_workspace)})

        assert "[FILE]" in result.output
        assert "[DIR]" in result.output


class TestListDirectoryToolIntegration:
    """Integration tests that don't mock Path.cwd()."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return ListDirectoryTool()

    def test_execute_real_current_directory(self, tool):
        """Test listing actual current directory."""
        result = tool.execute({"path": "."})

        assert result.success is True
        # We should see at least some files in the project root
        # (pyproject.toml, README, etc.)
        assert result.output is not None
        assert len(result.output) > 0
