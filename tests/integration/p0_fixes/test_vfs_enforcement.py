"""
METAL TEST: VFS Enforcement (P0 Security Fix)

Tests that ReadFileTool and WriteFileTool DENY operations without VFS.
This is the sandbox that prevents agents from `rm -rf /`.

OPUS-312: VFS was orphaned - tools existed but weren't enforced.
Fix: Tools now require VFS or explicit allow_unrestricted=True.
"""

import pytest

from vibe_core.tools.file_tools import ReadFileTool, WriteFileTool


class TestVFSEnforcement:
    """Verify VFS sandbox is enforced."""

    def test_read_without_vfs_is_denied(self):
        """ReadFileTool MUST deny operations without VFS."""
        tool = ReadFileTool()  # No VFS, no allow_unrestricted

        result = tool.execute({"path": "/etc/passwd"})

        assert result.success is False
        assert "SANDBOX REQUIRED" in result.error
        assert "VFS" in result.error

    def test_write_without_vfs_is_denied(self):
        """WriteFileTool MUST deny operations without VFS."""
        tool = WriteFileTool()  # No VFS, no allow_unrestricted

        result = tool.execute({"path": "/tmp/evil.txt", "content": "pwned"})

        assert result.success is False
        assert "SANDBOX REQUIRED" in result.error
        assert "VFS" in result.error

    def test_read_with_allow_unrestricted_works(self, tmp_path):
        """ReadFileTool with allow_unrestricted=True can read host."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello from host")

        # Tool with admin override
        tool = ReadFileTool(allow_unrestricted=True)
        result = tool.execute({"path": str(test_file)})

        assert result.success is True
        assert result.output == "hello from host"

    def test_write_with_allow_unrestricted_works(self, tmp_path):
        """WriteFileTool with allow_unrestricted=True can write host."""
        test_file = tmp_path / "output.txt"

        # Tool with admin override
        tool = WriteFileTool(allow_unrestricted=True)
        result = tool.execute({"path": str(test_file), "content": "written by admin"})

        assert result.success is True
        assert test_file.read_text() == "written by admin"

    def test_read_with_vfs_is_sandboxed(self):
        """ReadFileTool with VFS reads from sandbox, not host."""
        from vibe_core.vfs import VirtualFileSystem

        # Create VFS for test agent (creates sandbox at /workspaces/agents/test_read_agent/)
        vfs = VirtualFileSystem(agent_id="test_read_agent")

        # Write test file to sandbox
        vfs.write_text("data.txt", "sandboxed content")

        tool = ReadFileTool(vfs=vfs)
        result = tool.execute({"path": "data.txt"})

        assert result.success is True
        assert result.output == "sandboxed content"

    def test_write_with_vfs_is_sandboxed(self):
        """WriteFileTool with VFS writes to sandbox, not host."""
        from vibe_core.vfs import VirtualFileSystem

        # Create VFS for test agent
        vfs = VirtualFileSystem(agent_id="test_write_agent")

        tool = WriteFileTool(vfs=vfs)
        result = tool.execute({"path": "output.txt", "content": "sandboxed write"})

        assert result.success is True
        # Verify via VFS read
        assert vfs.read_text("output.txt") == "sandboxed write"

    def test_vfs_blocks_path_traversal(self):
        """VFS MUST block ../../../ path traversal attacks."""
        from vibe_core.vfs import VirtualFileSystem

        vfs = VirtualFileSystem(agent_id="test_traversal_agent")
        tool = ReadFileTool(vfs=vfs)

        # Attempt path traversal
        result = tool.execute({"path": "../../../etc/passwd"})

        # VFS should block this - either by raising PermissionError or returning error
        assert result.success is False
        # Error should mention permission/path/escape
        error_lower = result.error.lower()
        assert any(word in error_lower for word in ["permission", "escape", "denied", "sandbox"])
