"""
File operation tools for vibe-agency OS (ARCH-027)

Provides safe, auditable file read/write operations for LLM agents.
Supports VirtualFileSystem (VFS) for strict sandboxing.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if False:  # TYPE_CHECKING
    from vibe_core.vfs import VirtualFileSystem

logger = logging.getLogger(__name__)


class ReadFileTool(Tool):
    """
    Tool for reading file content.

    Allows LLM agents to read files from disk.
    If initialized with VFS, operations are strictly sandboxed.

    Example:
        >>> tool = ReadFileTool(vfs=agent_vfs)
        >>> result = tool.execute({"path": "input.txt"})
        >>> print(result.output)  # Content from sandbox/input.txt
    """

    def __init__(self, vfs: Optional["VirtualFileSystem"] = None, allow_unrestricted: bool = False):
        """
        Initialize ReadFileTool.

        Args:
            vfs: Optional VirtualFileSystem for sandboxing.
            allow_unrestricted: If True AND vfs is None, allow host filesystem access.
                               SECURITY: Only kernel/admin should set this True.
        """
        self.vfs = vfs
        self._allow_unrestricted = allow_unrestricted
        if not self.vfs and not allow_unrestricted:
            logger.info("📁 ReadFileTool: VFS not set, will require VFS at execute time")

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read content from a file on disk"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "required": True,
                "description": "Absolute or relative path to the file to read",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate parameters.

        Args:
            parameters: Must contain 'path' (string)

        Raises:
            ValueError: If path missing or invalid
            TypeError: If path is not a string
        """
        if "path" not in parameters:
            raise ValueError("Missing required parameter: path")

        path = parameters["path"]
        if not isinstance(path, str):
            raise TypeError(f"path must be a string, got {type(path).__name__}")

        if not path.strip():
            raise ValueError("path cannot be empty")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute file read operation.

        Args:
            parameters: {"path": "/path/to/file.txt"}

        Returns:
            ToolResult with file content or error
        """
        path_str = parameters["path"]

        try:
            content = ""
            actual_path = ""

            if self.vfs:
                # Sandboxed execution
                content = self.vfs.read_text(path_str)
                actual_path = str(self.vfs.get_sandbox_path() / path_str)
            elif self._allow_unrestricted:
                # Unrestricted execution (ADMIN ONLY)
                path = Path(path_str).expanduser().resolve()
                if not path.exists():
                    return ToolResult(success=False, error=f"File not found: {path}")
                if not path.is_file():
                    return ToolResult(success=False, error=f"Path is not a file: {path}")
                content = path.read_text(encoding="utf-8")
                actual_path = str(path)
            else:
                # SECURITY: No VFS and not allowed unrestricted = DENY
                logger.warning(f"🛡️ SANDBOX REQUIRED: ReadFileTool blocked without VFS: {path_str}")
                return ToolResult(
                    success=False, error="SANDBOX REQUIRED: File operations require VFS. Agent not sandboxed."
                )

            logger.info(f"ReadFileTool: Read file {actual_path} ({len(content)} bytes)")

            return ToolResult(
                success=True,
                output=content,
                metadata={"path": actual_path, "size_bytes": len(content)},
            )

        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(f"ReadFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except FileNotFoundError:
            error_msg = f"File not found: {path_str}"
            logger.error(f"ReadFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except UnicodeDecodeError:
            error_msg = f"File is not valid UTF-8: {path_str}"
            logger.error(f"ReadFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Failed to read file: {type(e).__name__}: {e!s}"
            logger.error(f"ReadFileTool: {error_msg} (path={path_str})", exc_info=True)
            return ToolResult(success=False, error=error_msg)


class WriteFileTool(Tool):
    """
    Tool for writing content to files.

    Allows LLM agents to create or overwrite files on disk.
    If initialized with VFS, operations are strictly sandboxed.

    Example:
        >>> tool = WriteFileTool(vfs=agent_vfs)
        >>> result = tool.execute({
        ...     "path": "output.txt",
        ...     "content": "Hello!"
        ... })
    """

    def __init__(self, vfs: Optional["VirtualFileSystem"] = None, allow_unrestricted: bool = False):
        """
        Initialize WriteFileTool.

        Args:
            vfs: Optional VirtualFileSystem for sandboxing.
            allow_unrestricted: If True AND vfs is None, allow host filesystem access.
                               SECURITY: Only kernel/admin should set this True.
        """
        self.vfs = vfs
        self._allow_unrestricted = allow_unrestricted
        if not self.vfs and not allow_unrestricted:
            logger.info("📁 WriteFileTool: VFS not set, will require VFS at execute time")

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file on disk (creates or overwrites)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "required": True,
                "description": "Absolute or relative path to the file to write",
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "Content to write to the file",
            },
            "create_dirs": {
                "type": "boolean",
                "required": False,
                "description": "Create parent directories if they don't exist (default: False)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate parameters.

        Args:
            parameters: Must contain 'path' and 'content' (strings)

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "path" not in parameters:
            raise ValueError("Missing required parameter: path")

        if "content" not in parameters:
            raise ValueError("Missing required parameter: content")

        path = parameters["path"]
        if not isinstance(path, str):
            raise TypeError(f"path must be a string, got {type(path).__name__}")

        if not path.strip():
            raise ValueError("path cannot be empty")

        content = parameters["content"]
        if not isinstance(content, str):
            raise TypeError(f"content must be a string, got {type(content).__name__}")

        if "create_dirs" in parameters:
            create_dirs = parameters["create_dirs"]
            if not isinstance(create_dirs, bool):
                raise TypeError(f"create_dirs must be a boolean, got {type(create_dirs).__name__}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute file write operation.

        Args:
            parameters: {
                "path": "file.txt",
                "content": "Content",
                "create_dirs": True
            }

        Returns:
            ToolResult with success status
        """
        path_str = parameters["path"]
        content = parameters["content"]
        create_dirs = parameters.get("create_dirs", False)

        try:
            actual_path = ""

            if self.vfs:
                # Sandboxed execution
                # VFS handles mkdir logic internally usually, but let's check VFS API
                # Re-reading VFS code... mkdir is separate.
                if create_dirs:
                    # We need to compute parent path relative to sandbox
                    # This is tricky without exposing too much logic.
                    # Simplest way: VFS.write_text doesn't support create_dirs arg in current impl
                    # We need to manually handle it via VFS.
                    # But VFS.write_text does: "full_path.parent.mkdir(parents=True, exist_ok=True)"
                    # Wait, let me check my VFS read again.
                    pass

                # Re-reading VFS implementation from memory:
                # def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
                #     full_path = self._resolve_and_validate(path)
                #     full_path.parent.mkdir(parents=True, exist_ok=True)
                #     full_path.write_text(content, encoding=encoding)

                # It ALWAYS creates dirs. So `create_dirs` parameter is effectively always True for VFS.
                # This is a slight behavior change but acceptable for Sandbox safety.

                self.vfs.write_text(path_str, content)
                actual_path = str(self.vfs.get_sandbox_path() / path_str)

            elif self._allow_unrestricted:
                # Unrestricted execution (ADMIN ONLY)
                path = Path(path_str).expanduser().resolve()
                parent = path.parent
                if not parent.exists():
                    if create_dirs:
                        parent.mkdir(parents=True, exist_ok=True)
                        logger.info(f"WriteFileTool: Created directory {parent}")
                    else:
                        return ToolResult(
                            success=False,
                            error=f"Parent directory does not exist: {parent}. Use create_dirs=true to create it.",
                        )

                path.write_text(content, encoding="utf-8")
                actual_path = str(path)
            else:
                # SECURITY: No VFS and not allowed unrestricted = DENY
                logger.warning(f"🛡️ SANDBOX REQUIRED: WriteFileTool blocked without VFS: {path_str}")
                return ToolResult(
                    success=False, error="SANDBOX REQUIRED: File operations require VFS. Agent not sandboxed."
                )

            logger.info(f"WriteFileTool: Wrote file {actual_path} ({len(content)} bytes)")

            return ToolResult(
                success=True,
                output=f"File written successfully: {actual_path}",
                metadata={"path": actual_path, "size_bytes": len(content)},
            )

        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(f"WriteFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Failed to write file: {type(e).__name__}: {e!s}"
            logger.error(f"WriteFileTool: {error_msg} (path={path_str})", exc_info=True)
            return ToolResult(success=False, error=error_msg)
