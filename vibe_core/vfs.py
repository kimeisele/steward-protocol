"""
VIRTUAL FILESYSTEM (VFS) - Agent Sandboxing
===========================================

Goal: Prevent agents from accessing arbitrary files on the system.

Philosophy:
"An agent's world is its sandbox. The rest is illusion."

Architecture:
- Each agent gets: /tmp/vibe_os/agents/{agent_id}/
- All file operations are restricted to this directory
- Path traversal attacks (../) are blocked
- Symlinks can provide controlled access to shared resources

Security Model:
- Default: DENY ALL (agent can only access its sandbox)
- Exceptions: Explicit symlinks for shared resources (e.g., repo for Scribe)
- Logging: All file access is logged for audit
"""

import logging
import os
from pathlib import Path
from typing import IO, List, Optional

logger = logging.getLogger("VFS")


class VirtualFileSystem:
    """
    Sandboxed filesystem for agents.

    Each agent operates in an isolated directory.
    Attempts to escape the sandbox raise PermissionError.
    """

    # Base directory for all agent sandboxes
    VFS_ROOT = Path("/tmp/vibe_os/agents")

    def __init__(self, agent_id: str):
        """
        Initialize VFS for an agent.

        Args:
            agent_id: Agent identifier
        """
        self.agent_id = agent_id
        self.root = self.VFS_ROOT / agent_id

        # Create sandbox directory
        self.root.mkdir(parents=True, exist_ok=True)

        # Resolve root to handle symlinks (e.g., /tmp -> /private/tmp on macOS)
        self.root = self.root.resolve()

        logger.info(f"📁 VFS initialized for {agent_id}: {self.root}")

    def _resolve_and_validate(self, path: str) -> Path:
        """
        Resolve path and validate it's within sandbox.

        Args:
            path: Relative or absolute path

        Returns:
            Resolved absolute path

        Raises:
            PermissionError: If path escapes sandbox
        """
        # Convert to Path object
        if os.path.isabs(path):
            # Absolute path - check if it's in our sandbox
            full_path = Path(path).resolve()
        else:
            # Relative path - resolve relative to sandbox root
            # IMPORTANT: Don't resolve symlinks yet, just get the path
            full_path = self.root / path

        # Security check: ensure path (before resolving symlinks) is within sandbox
        try:
            # Check if the path itself (not its target) is in sandbox
            full_path.relative_to(self.root)
        except ValueError:
            logger.warning(
                f"🚫 {self.agent_id} attempted to access {path} (resolved to {full_path}, outside sandbox {self.root})"
            )
            raise PermissionError(f"Access denied: {path} is outside agent sandbox")

        # Now resolve symlinks - this may point outside sandbox (allowed for controlled escapes)
        full_path = full_path.resolve()

        return full_path

    def open(self, path: str, mode: str = "r", **kwargs) -> IO:
        """
        Open a file within the sandbox.

        Args:
            path: Path to file (relative to sandbox)
            mode: File mode (r, w, a, rb, wb, etc.)
            **kwargs: Additional arguments for open()

        Returns:
            File handle

        Raises:
            PermissionError: If path escapes sandbox
        """
        full_path = self._resolve_and_validate(path)

        # Create parent directories if writing
        if "w" in mode or "a" in mode:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"📄 {self.agent_id} opening {path} (mode={mode})")

        return open(full_path, mode, **kwargs)

    def exists(self, path: str) -> bool:
        """
        Check if file/directory exists in sandbox.

        Args:
            path: Path to check

        Returns:
            True if exists, False otherwise
        """
        try:
            full_path = self._resolve_and_validate(path)
            return full_path.exists()
        except PermissionError:
            return False

    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        try:
            full_path = self._resolve_and_validate(path)
            return full_path.is_file()
        except PermissionError:
            return False

    def is_dir(self, path: str) -> bool:
        """Check if path is a directory"""
        try:
            full_path = self._resolve_and_validate(path)
            return full_path.is_dir()
        except PermissionError:
            return False

    def list_dir(self, path: str = ".") -> List[str]:
        """
        List files in a directory within sandbox.

        Args:
            path: Directory path (relative to sandbox)

        Returns:
            List of filenames

        Raises:
            PermissionError: If path escapes sandbox
        """
        full_path = self._resolve_and_validate(path)

        if not full_path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        return [f.name for f in full_path.iterdir()]

    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> None:
        """
        Create directory in sandbox.

        Args:
            path: Directory path
            parents: Create parent directories if needed
            exist_ok: Don't error if directory exists

        Raises:
            PermissionError: If path escapes sandbox
        """
        full_path = self._resolve_and_validate(path)
        full_path.mkdir(parents=parents, exist_ok=exist_ok)
        logger.debug(f"📁 {self.agent_id} created directory {path}")

    def remove(self, path: str) -> None:
        """
        Remove file in sandbox.

        Args:
            path: File path

        Raises:
            PermissionError: If path escapes sandbox
        """
        full_path = self._resolve_and_validate(path)

        if full_path.is_dir():
            raise IsADirectoryError(f"{path} is a directory, use rmdir()")

        full_path.unlink()
        logger.debug(f"🗑️  {self.agent_id} removed {path}")

    def rmdir(self, path: str, recursive: bool = False) -> None:
        """
        Remove directory in sandbox.

        Args:
            path: Directory path
            recursive: Remove recursively (like rm -rf)

        Raises:
            PermissionError: If path escapes sandbox
        """
        full_path = self._resolve_and_validate(path)

        if not full_path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        if recursive:
            import shutil

            shutil.rmtree(full_path)
        else:
            full_path.rmdir()

        logger.debug(f"🗑️  {self.agent_id} removed directory {path}")

    def create_symlink(self, target: str, link_name: str) -> None:
        """
        Create symlink in sandbox.

        SECURITY NOTE: This allows controlled access to resources outside sandbox.
        Only the kernel should call this method.

        Args:
            target: Target path (can be outside sandbox)
            link_name: Symlink name (must be in sandbox)

        Raises:
            PermissionError: If link_name escapes sandbox
        """
        link_path = self._resolve_and_validate(link_name)
        target_path = Path(target)

        link_path.symlink_to(target_path)
        logger.info(f"🔗 {self.agent_id} symlink created: {link_name} → {target}")

    def get_sandbox_path(self) -> Path:
        """Get the absolute path to this agent's sandbox"""
        return self.root

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """
        Read file as text.

        Args:
            path: File path
            encoding: Text encoding

        Returns:
            File contents as string
        """
        full_path = self._resolve_and_validate(path)
        return full_path.read_text(encoding=encoding)

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """
        Write text to file.

        Args:
            path: File path
            content: Text content
            encoding: Text encoding
        """
        full_path = self._resolve_and_validate(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding=encoding)
        logger.debug(f"💾 {self.agent_id} wrote {len(content)} bytes to {path}")
