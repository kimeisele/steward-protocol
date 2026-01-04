"""
THE GREAT PURGE - Phase 2b: FileTools Tests
============================================

Tests for vibe_core/tools/file_tools.py (ReadFileTool, WriteFileTool)

"The Hands of the System - if they fail, we cannot act."

Run with: pytest tests/tools/test_file_tools.py -v
"""

import pytest

from vibe_core.tools.file_tools import ReadFileTool, WriteFileTool
from vibe_core.tools.tool_protocol import ToolResult


class TestReadFileTool:
    """Tests for ReadFileTool."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return ReadFileTool(allow_unrestricted=True)

    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create a temporary file with content."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello, World!")
        return file_path

    # =========================================================================
    # Property Tests
    # =========================================================================

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "read_file"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert len(tool.description) > 0
        assert "read" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "path" in schema
        assert schema["path"]["type"] == "string"
        assert schema["path"]["required"] is True

    # =========================================================================
    # Validation Tests
    # =========================================================================

    def test_validate_missing_path(self, tool):
        """Test validation rejects missing path."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({})
        assert "path" in str(exc_info.value).lower()

    def test_validate_invalid_path_type(self, tool):
        """Test validation rejects non-string path."""
        with pytest.raises(TypeError):
            tool.validate({"path": 123})

    def test_validate_empty_path(self, tool):
        """Test validation rejects empty path."""
        with pytest.raises(ValueError):
            tool.validate({"path": "   "})

    def test_validate_valid_path(self, tool):
        """Test validation accepts valid path."""
        # Should not raise
        tool.validate({"path": "/some/path.txt"})

    # =========================================================================
    # Execute Tests - Success Cases
    # =========================================================================

    def test_execute_read_file(self, tool, temp_file):
        """Test reading a file successfully."""
        result = tool.execute({"path": str(temp_file)})

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.output == "Hello, World!"
        assert result.error is None

    def test_execute_metadata_contains_path(self, tool, temp_file):
        """Test that metadata contains path."""
        result = tool.execute({"path": str(temp_file)})

        assert result.metadata is not None
        assert "path" in result.metadata

    def test_execute_metadata_contains_size(self, tool, temp_file):
        """Test that metadata contains file size."""
        result = tool.execute({"path": str(temp_file)})

        assert result.metadata is not None
        assert "size_bytes" in result.metadata
        assert result.metadata["size_bytes"] == 13  # len("Hello, World!")

    def test_execute_read_empty_file(self, tool, tmp_path):
        """Test reading an empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        result = tool.execute({"path": str(empty_file)})

        assert result.success is True
        assert result.output == ""
        assert result.metadata["size_bytes"] == 0

    def test_execute_read_multiline_file(self, tool, tmp_path):
        """Test reading a multiline file."""
        multiline_file = tmp_path / "multiline.txt"
        content = "Line 1\nLine 2\nLine 3"
        multiline_file.write_text(content)

        result = tool.execute({"path": str(multiline_file)})

        assert result.success is True
        assert result.output == content
        assert "Line 1" in result.output
        assert "Line 2" in result.output

    # =========================================================================
    # Execute Tests - Error Cases
    # =========================================================================

    def test_execute_file_not_found(self, tool, tmp_path):
        """Test error when file does not exist."""
        result = tool.execute({"path": str(tmp_path / "nonexistent.txt")})

        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_execute_path_is_directory(self, tool, tmp_path):
        """Test error when path is a directory."""
        result = tool.execute({"path": str(tmp_path)})

        assert result.success is False
        assert result.error is not None
        assert "not a file" in result.error.lower()

    def test_execute_binary_file_fails(self, tool, tmp_path):
        """Test error when reading non-UTF8 file."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x80\x81\x82\xff\xfe")

        result = tool.execute({"path": str(binary_file)})

        assert result.success is False
        assert result.error is not None
        assert "utf-8" in result.error.lower()


class TestWriteFileTool:
    """Tests for WriteFileTool."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return WriteFileTool(allow_unrestricted=True)

    # =========================================================================
    # Property Tests
    # =========================================================================

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "write_file"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert len(tool.description) > 0
        assert "write" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "path" in schema
        assert schema["path"]["required"] is True
        assert "content" in schema
        assert schema["content"]["required"] is True
        assert "create_dirs" in schema
        assert schema["create_dirs"]["required"] is False

    # =========================================================================
    # Validation Tests
    # =========================================================================

    def test_validate_missing_path(self, tool):
        """Test validation rejects missing path."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({"content": "hello"})
        assert "path" in str(exc_info.value).lower()

    def test_validate_missing_content(self, tool):
        """Test validation rejects missing content."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({"path": "/some/path"})
        assert "content" in str(exc_info.value).lower()

    def test_validate_invalid_path_type(self, tool):
        """Test validation rejects non-string path."""
        with pytest.raises(TypeError):
            tool.validate({"path": 123, "content": "hello"})

    def test_validate_invalid_content_type(self, tool):
        """Test validation rejects non-string content."""
        with pytest.raises(TypeError):
            tool.validate({"path": "/path", "content": 123})

    def test_validate_empty_path(self, tool):
        """Test validation rejects empty path."""
        with pytest.raises(ValueError):
            tool.validate({"path": "   ", "content": "hello"})

    def test_validate_invalid_create_dirs_type(self, tool):
        """Test validation rejects non-boolean create_dirs."""
        with pytest.raises(TypeError):
            tool.validate({"path": "/path", "content": "hello", "create_dirs": "yes"})

    def test_validate_valid_params(self, tool):
        """Test validation accepts valid parameters."""
        # Should not raise
        tool.validate({"path": "/some/path", "content": "hello"})
        tool.validate({"path": "/some/path", "content": "hello", "create_dirs": True})

    # =========================================================================
    # Execute Tests - Success Cases
    # =========================================================================

    def test_execute_write_file(self, tool, tmp_path):
        """Test writing a file successfully."""
        file_path = tmp_path / "output.txt"

        result = tool.execute({"path": str(file_path), "content": "Test content"})

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.error is None
        # Verify file was actually written
        assert file_path.read_text() == "Test content"

    def test_execute_overwrite_file(self, tool, tmp_path):
        """Test overwriting an existing file."""
        file_path = tmp_path / "existing.txt"
        file_path.write_text("Old content")

        result = tool.execute({"path": str(file_path), "content": "New content"})

        assert result.success is True
        assert file_path.read_text() == "New content"

    def test_execute_metadata_contains_path(self, tool, tmp_path):
        """Test that metadata contains path."""
        file_path = tmp_path / "meta.txt"

        result = tool.execute({"path": str(file_path), "content": "content"})

        assert result.metadata is not None
        assert "path" in result.metadata

    def test_execute_metadata_contains_size(self, tool, tmp_path):
        """Test that metadata contains written size."""
        file_path = tmp_path / "sized.txt"
        content = "12345"

        result = tool.execute({"path": str(file_path), "content": content})

        assert result.metadata is not None
        assert "size_bytes" in result.metadata
        assert result.metadata["size_bytes"] == 5

    def test_execute_write_empty_content(self, tool, tmp_path):
        """Test writing empty content."""
        file_path = tmp_path / "empty.txt"

        result = tool.execute({"path": str(file_path), "content": ""})

        assert result.success is True
        assert file_path.read_text() == ""

    def test_execute_write_multiline(self, tool, tmp_path):
        """Test writing multiline content."""
        file_path = tmp_path / "multiline.txt"
        content = "Line 1\nLine 2\nLine 3"

        result = tool.execute({"path": str(file_path), "content": content})

        assert result.success is True
        assert file_path.read_text() == content

    # =========================================================================
    # Execute Tests - create_dirs Option
    # =========================================================================

    def test_execute_parent_not_exists_without_create_dirs(self, tool, tmp_path):
        """Test error when parent directory doesn't exist and create_dirs=False."""
        file_path = tmp_path / "nonexistent" / "file.txt"

        result = tool.execute({"path": str(file_path), "content": "hello"})

        assert result.success is False
        assert "does not exist" in result.error.lower()

    def test_execute_parent_not_exists_with_create_dirs(self, tool, tmp_path):
        """Test success when parent directory doesn't exist and create_dirs=True."""
        file_path = tmp_path / "new_dir" / "nested" / "file.txt"

        result = tool.execute({"path": str(file_path), "content": "hello", "create_dirs": True})

        assert result.success is True
        assert file_path.exists()
        assert file_path.read_text() == "hello"

    # =========================================================================
    # Execute Tests - Error Cases
    # =========================================================================

    def test_execute_path_is_directory(self, tool, tmp_path):
        """Test error when trying to write to a directory."""
        result = tool.execute({"path": str(tmp_path), "content": "hello"})

        assert result.success is False
        assert result.error is not None
        assert "directory" in result.error.lower()


class TestFileToolsIntegration:
    """Integration tests for ReadFileTool and WriteFileTool together."""

    def test_write_then_read(self, tmp_path):
        """Test writing a file then reading it back."""
        read_tool = ReadFileTool(allow_unrestricted=True)
        write_tool = WriteFileTool(allow_unrestricted=True)
        file_path = tmp_path / "roundtrip.txt"
        content = "Round trip content with special chars: äöü 你好"

        # Write
        write_result = write_tool.execute({"path": str(file_path), "content": content})
        assert write_result.success is True

        # Read
        read_result = read_tool.execute({"path": str(file_path)})
        assert read_result.success is True
        assert read_result.output == content
