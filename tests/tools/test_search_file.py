"""
THE GREAT PURGE - Phase 2a: SearchFileTool Tests
=================================================

Tests for vibe_core/tools/search_file.py

"The Eyes of the System - if they fail, we are blind."

Run with: pytest tests/tools/test_search_file.py -v
"""

import pytest

from vibe_core.tools.search_file import SearchFileTool
from vibe_core.tools.tool_protocol import ToolResult


class TestSearchFileTool:
    """Tests for SearchFileTool."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return SearchFileTool()

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create a temporary workspace with test files."""
        # Create various files for searching
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "script.py").write_text("print('hello')")
        (tmp_path / "test_example.py").write_text("def test(): pass")

        # Create subdirectory with files
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested content")
        (subdir / "nested.py").write_text("nested python")

        # Create hidden files (should be filtered)
        (tmp_path / ".hidden.txt").write_text("hidden")
        hidden_dir = tmp_path / ".git"
        hidden_dir.mkdir()
        (hidden_dir / "config").write_text("git config")

        # Create .vibe directory (special case - should be visible)
        vibe_dir = tmp_path / ".vibe"
        vibe_dir.mkdir()
        (vibe_dir / "config.yaml").write_text("vibe config")

        return tmp_path

    # =========================================================================
    # Property Tests
    # =========================================================================

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "search_file"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert len(tool.description) > 0
        assert "search" in tool.description.lower() or "glob" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "pattern" in schema
        assert schema["pattern"]["type"] == "string"
        assert schema["pattern"]["required"] is True
        assert "path" in schema
        assert schema["path"]["required"] is False

    # =========================================================================
    # Validation Tests
    # =========================================================================

    def test_validate_missing_pattern(self, tool):
        """Test validation rejects missing pattern."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({})
        assert "pattern" in str(exc_info.value).lower()

    def test_validate_invalid_pattern_type(self, tool):
        """Test validation rejects non-string pattern."""
        with pytest.raises(TypeError):
            tool.validate({"pattern": 123})

    def test_validate_invalid_path_type(self, tool):
        """Test validation rejects non-string path."""
        with pytest.raises(TypeError):
            tool.validate({"pattern": "*.py", "path": 123})

    def test_validate_valid_params(self, tool):
        """Test validation accepts valid parameters."""
        # Should not raise
        tool.validate({"pattern": "*.py"})
        tool.validate({"pattern": "*.txt", "path": "/some/path"})

    # =========================================================================
    # Execute Tests - Success Cases
    # =========================================================================

    def test_execute_find_txt_files(self, tool, temp_workspace, monkeypatch):
        """Test searching for .txt files."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt", "path": str(temp_workspace)})

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "file1.txt" in result.output
        assert "file2.txt" in result.output

    def test_execute_find_py_files(self, tool, temp_workspace, monkeypatch):
        """Test searching for .py files."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.py", "path": str(temp_workspace)})

        assert result.success is True
        assert "script.py" in result.output
        assert "test_example.py" in result.output

    def test_execute_recursive_search(self, tool, temp_workspace, monkeypatch):
        """Test that search is recursive (finds nested files)."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt", "path": str(temp_workspace)})

        assert result.success is True
        # Should find nested file
        assert "nested.txt" in result.output or "subdir" in result.output

    def test_execute_pattern_prefix(self, tool, temp_workspace, monkeypatch):
        """Test searching with pattern prefix (test_*)."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "test_*.py", "path": str(temp_workspace)})

        assert result.success is True
        assert "test_example.py" in result.output
        # Should NOT find script.py
        assert "script.py" not in result.output

    def test_execute_no_matches(self, tool, temp_workspace, monkeypatch):
        """Test when pattern matches no files."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.nonexistent", "path": str(temp_workspace)})

        assert result.success is True
        assert "no match" in result.output.lower()

    def test_execute_hidden_files_filtered(self, tool, temp_workspace, monkeypatch):
        """Test that hidden files are filtered out."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt", "path": str(temp_workspace)})

        assert result.success is True
        assert ".hidden.txt" not in result.output

    def test_execute_git_directory_filtered(self, tool, temp_workspace, monkeypatch):
        """Test that .git directory contents are filtered."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*", "path": str(temp_workspace)})

        assert result.success is True
        assert ".git" not in result.output
        assert "config" not in result.output or ".git/config" not in result.output

    def test_execute_metadata_contains_count(self, tool, temp_workspace, monkeypatch):
        """Test that metadata contains match count."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt", "path": str(temp_workspace)})

        assert result.metadata is not None
        assert "count" in result.metadata
        assert result.metadata["count"] >= 2  # At least file1.txt, file2.txt

    # =========================================================================
    # Execute Tests - Error Cases
    # =========================================================================

    def test_execute_path_not_found(self, tool, temp_workspace, monkeypatch):
        """Test error when search path does not exist."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt", "path": str(temp_workspace / "nonexistent")})

        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_execute_outside_workspace_blocked(self, tool, temp_workspace, monkeypatch):
        """Test that paths outside workspace are blocked (security)."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt", "path": "/tmp"})

        assert result.success is False
        assert result.error is not None
        assert "denied" in result.error.lower() or "outside" in result.error.lower()

    # =========================================================================
    # Execute Tests - Edge Cases
    # =========================================================================

    def test_execute_default_path(self, tool, temp_workspace, monkeypatch):
        """Test that empty path defaults to current directory."""
        monkeypatch.chdir(temp_workspace)
        result = tool.execute({"pattern": "*.txt"})

        assert result.success is True
        assert "file1.txt" in result.output

    def test_execute_truncation_notice(self, tool, tmp_path, monkeypatch):
        """Test that results are truncated at MAX_RESULTS with notice."""
        # Create many files to exceed MAX_RESULTS (50)
        monkeypatch.chdir(tmp_path)
        for i in range(60):
            (tmp_path / f"file_{i:03d}.txt").write_text(f"content {i}")

        result = tool.execute({"pattern": "*.txt", "path": str(tmp_path)})

        assert result.success is True
        assert result.metadata["truncated"] is True
        assert "truncated" in result.output.lower() or result.metadata["count"] == 50


class TestSearchFileToolIntegration:
    """Integration tests that use real filesystem."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return SearchFileTool()

    def test_execute_find_python_files_in_project(self, tool):
        """Test searching for Python files in actual project."""
        result = tool.execute({"pattern": "*.py", "path": "."})

        assert result.success is True
        # Project should have Python files
        assert result.metadata["count"] > 0
