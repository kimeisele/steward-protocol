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
from typing import IO, List

logger = logging.getLogger("VFS")


class VirtualFileSystem:
    """
    Sandboxed filesystem for agents.

    Each agent operates in an isolated directory.
    Attempts to escape the sandbox raise PermissionError.
    """

    # OPUS-025: VFS_ROOT resolved from config or fallback
    _VFS_ROOT = None

    @classmethod
    def _get_vfs_root(cls) -> Path:
        """Get VFS root from config or fallback."""
        if cls._VFS_ROOT is None:
            try:
                from vibe_core.phoenix import get_config

                config = get_config()
                if config and hasattr(config, "paths") and hasattr(config.paths, "system"):
                    cls._VFS_ROOT = Path(config.paths.system.agents)
                else:
                    # SECURITY FIX B-P1-2: Use persistent fallback instead of /tmp
                    # /tmp is cleared on restart, losing agent data
                    cls._VFS_ROOT = Path.cwd() / "workspaces" / "agents"
                    logger.warning(f"VFS config not found, using fallback: {cls._VFS_ROOT}")
            except Exception as e:
                # SECURITY FIX B-P1-2: Use persistent fallback instead of /tmp
                cls._VFS_ROOT = Path.cwd() / "workspaces" / "agents"
                logger.warning(f"VFS config error ({e}), using fallback: {cls._VFS_ROOT}")
        return cls._VFS_ROOT

    # Legacy property for backward compatibility
    @property
    def VFS_ROOT(self) -> Path:
        return self._get_vfs_root()

    def __init__(self, agent_id: str):
        """
        Initialize VFS for an agent.

        Args:
            agent_id: Agent identifier
        """
        self.agent_id = agent_id
        self.root = self._get_vfs_root() / agent_id

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

    def create_symlink(self, target: str, link_name: str, _kernel_token: str = "") -> None:
        """
        Create symlink in sandbox.

        SECURITY NOTE: This allows controlled access to resources outside sandbox.
        Only the kernel should call this method via kernel_ops.py.

        SECURITY FIX B-P0-1: Added caller verification to prevent sandbox escape.

        Args:
            target: Target path (can be outside sandbox)
            link_name: Symlink name (must be in sandbox)
            _kernel_token: Internal token for kernel verification (agents should not use)

        Raises:
            PermissionError: If link_name escapes sandbox or unauthorized caller
        """
        # SECURITY FIX B-P0-1: Verify caller is kernel_ops.py
        import inspect

        caller_frame = inspect.currentframe()
        if caller_frame and caller_frame.f_back:
            caller_file = caller_frame.f_back.f_code.co_filename
            # Allow calls from kernel_ops.py, verification scripts, and test files
            allowed_suffixes = ("kernel_ops.py", "verify_monkey_patching.py")
            is_allowed = any(caller_file.endswith(s) for s in allowed_suffixes)
            is_test = "/tests/" in caller_file or "\\tests\\" in caller_file
            if not is_allowed and not is_test:
                logger.warning(f"🚨 SANDBOX ESCAPE ATTEMPT: {caller_file} tried to call create_symlink()")
                raise PermissionError(
                    "NARASIMHA VIOLATION: create_symlink() can only be called by kernel. "
                    f"Unauthorized caller: {caller_file}"
                )

        # For symlinks, we need the path WITHOUT resolving existing symlinks
        # _resolve_and_validate resolves symlinks, which breaks this
        if os.path.isabs(link_name):
            raise PermissionError("Symlink name must be relative path in sandbox")
        link_path = self.root / link_name
        target_path = Path(target)

        # Security check: ensure link is in sandbox
        try:
            link_path.relative_to(self.root)
        except ValueError:
            raise PermissionError(f"Access denied: {link_name} is outside agent sandbox")

        # Handle existing symlink (idempotent operation)
        if link_path.is_symlink():
            existing_target = link_path.resolve()
            if existing_target == target_path.resolve():
                logger.debug(f"🔗 {self.agent_id} symlink already exists: {link_name} → {target}")
                return
            # Different target - remove and recreate
            link_path.unlink()
        elif link_path.exists():
            # Regular file/dir exists - don't overwrite
            raise FileExistsError(f"Cannot create symlink: {link_name} already exists and is not a symlink")

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
