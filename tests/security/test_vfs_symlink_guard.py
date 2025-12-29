"""
VFS Symlink Guard Test: Verifies B-P0-1 Fix

Tests that create_symlink() can only be called by authorized kernel files.
Unauthorized callers (like agents) should get NARASIMHA VIOLATION.

This test EXISTS because:
    "The sandbox escape vulnerability was found but had NO test coverage."
    "Now it does."
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.vfs import VirtualFileSystem


class TestVFSSymlinkGuard:
    """Tests for VFS create_symlink() caller verification (B-P0-1 fix)."""

    def test_unauthorized_caller_blocked(self, tmp_path):
        """
        NARASIMHA TEST: Unauthorized caller cannot create symlinks.

        An agent or arbitrary code trying to call create_symlink()
        should be blocked with PermissionError.
        """
        # Setup VFS with temp directory
        with patch.object(VirtualFileSystem, "_get_vfs_root", return_value=tmp_path):
            vfs = VirtualFileSystem("test_agent")

        # Create sandbox directory
        vfs.root.mkdir(parents=True, exist_ok=True)

        # Target outside sandbox
        target = tmp_path.parent / "outside_file.txt"
        target.write_text("sensitive data")

        # Attempt symlink creation - should be BLOCKED
        # Because THIS file is not kernel_ops.py or a test file
        # Wait - test files ARE allowed. Let me check the implementation...
        # The fix allows: kernel_ops.py, verify_monkey_patching.py, test_
        # So this test file IS allowed. We need to simulate a non-test caller.

        # To properly test, we need to mock the caller frame
        with patch("inspect.currentframe") as mock_frame:
            # Simulate call from a cartridge (unauthorized)
            mock_back = MagicMock()
            mock_back.f_code.co_filename = "/path/to/vibe_core/cartridges/evil/agent.py"
            mock_frame.return_value.f_back = mock_back

            with pytest.raises(PermissionError) as excinfo:
                vfs.create_symlink(str(target), "link_to_secret")

            assert "NARASIMHA VIOLATION" in str(excinfo.value)
            assert "cartridges/evil/agent.py" in str(excinfo.value)

        print("✅ Unauthorized caller blocked with NARASIMHA VIOLATION")

    def test_kernel_ops_allowed(self, tmp_path):
        """
        CONTROL TEST: kernel_ops.py CAN create symlinks.
        """
        with patch.object(VirtualFileSystem, "_get_vfs_root", return_value=tmp_path):
            vfs = VirtualFileSystem("scribe")

        vfs.root.mkdir(parents=True, exist_ok=True)

        # Create a real target
        target = tmp_path / "repo"
        target.mkdir()

        # Mock caller as kernel_ops.py
        with patch("inspect.currentframe") as mock_frame:
            mock_back = MagicMock()
            mock_back.f_code.co_filename = "/path/to/vibe_core/kernel_ops.py"
            mock_frame.return_value.f_back = mock_back

            # Should succeed
            vfs.create_symlink(str(target), "repo_link")

            link_path = vfs.root / "repo_link"
            assert link_path.is_symlink()
            assert link_path.resolve() == target.resolve()

        print("✅ kernel_ops.py allowed to create symlinks")

    def test_test_files_allowed(self, tmp_path):
        """
        CONTROL TEST: Test files CAN create symlinks (for testing).
        """
        with patch.object(VirtualFileSystem, "_get_vfs_root", return_value=tmp_path):
            vfs = VirtualFileSystem("test_agent")

        vfs.root.mkdir(parents=True, exist_ok=True)

        target = tmp_path / "test_target"
        target.mkdir()

        # This test file should be allowed (filename contains "test_")
        # No mock needed - actual caller is this test file
        vfs.create_symlink(str(target), "test_link")

        link_path = vfs.root / "test_link"
        assert link_path.is_symlink()

        print("✅ Test files allowed to create symlinks")

    def test_symlink_still_validates_sandbox(self, tmp_path):
        """
        Even authorized callers cannot create symlinks OUTSIDE sandbox.
        """
        with patch.object(VirtualFileSystem, "_get_vfs_root", return_value=tmp_path):
            vfs = VirtualFileSystem("test_agent")

        vfs.root.mkdir(parents=True, exist_ok=True)

        # Try to create link outside sandbox using absolute path
        with pytest.raises(PermissionError) as excinfo:
            vfs.create_symlink("/etc/passwd", "/tmp/evil_link")

        assert "must be relative path" in str(excinfo.value)
        print("✅ Absolute link paths rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
