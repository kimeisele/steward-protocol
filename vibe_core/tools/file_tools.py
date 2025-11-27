"""
File operation tools for vibe-agency OS (ARCH-027)

Provides safe, auditable file read/write operations for LLM agents.
"""

import logging
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger(__name__)


class ReadFileTool(Tool):
    """
    Tool for reading file content.

    Allows LLM agents to read files from disk.

    Example:
        >>> tool = ReadFileTool()
        >>> result = tool.execute({"path": "/tmp/test.txt"})
        >>> print(result.output)  # File content
    """

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

        Example:
            >>> result = tool.execute({"path": "/tmp/test.txt"})
            >>> if result.success:
            ...     print(result.output)  # File content
        """
        path_str = parameters["path"]

        try:
            # Resolve path
            path = Path(path_str).expanduser().resolve()

            # Check if file exists
            if not path.exists():
                return ToolResult(success=False, error=f"File not found: {path}")

            # Check if it's a file (not a directory)
            if not path.is_file():
                return ToolResult(success=False, error=f"Path is not a file: {path}")

            # Read file content
            content = path.read_text(encoding="utf-8")

            logger.info(f"ReadFileTool: Read file {path} ({len(content)} bytes)")

            return ToolResult(
                success=True,
                output=content,
                metadata={"path": str(path), "size_bytes": len(content)},
            )

        except PermissionError:
            error_msg = f"Permission denied: {path}"
            logger.error(f"ReadFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except UnicodeDecodeError:
            error_msg = f"File is not valid UTF-8: {path}"
            logger.error(f"ReadFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Failed to read file: {type(e).__name__}: {e!s}"
            logger.error(f"ReadFileTool: {error_msg} (path={path})", exc_info=True)
            return ToolResult(success=False, error=error_msg)


class WriteFileTool(Tool):
    """
    Tool for writing content to files.

    Allows LLM agents to create or overwrite files on disk.

    Example:
        >>> tool = WriteFileTool()
        >>> result = tool.execute({
        ...     "path": "/tmp/hello.txt",
        ...     "content": "Hello, world!"
        ... })
        >>> print(result.success)  # True
    """

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

        # create_dirs is optional
        if "create_dirs" in parameters:
            create_dirs = parameters["create_dirs"]
            if not isinstance(create_dirs, bool):
                raise TypeError(f"create_dirs must be a boolean, got {type(create_dirs).__name__}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute file write operation.

        Args:
            parameters: {
                "path": "/path/to/file.txt",
                "content": "File content",
                "create_dirs": False  # optional
            }

        Returns:
            ToolResult with success status

        Example:
            >>> result = tool.execute({
            ...     "path": "/tmp/test.txt",
            ...     "content": "Hello!"
            ... })
            >>> print(result.success)  # True
        """
        path_str = parameters["path"]
        content = parameters["content"]
        create_dirs = parameters.get("create_dirs", False)

        try:
            # Resolve path
            path = Path(path_str).expanduser().resolve()

            # Check if parent directory exists
            parent = path.parent
            if not parent.exists():
                if create_dirs:
                    parent.mkdir(parents=True, exist_ok=True)
                    logger.info(f"WriteFileTool: Created directory {parent}")
                else:
                    return ToolResult(
                        success=False,
                        error=f"Parent directory does not exist: {parent}. "
                        f"Use create_dirs=true to create it.",
                    )

            # Write file
            path.write_text(content, encoding="utf-8")

            logger.info(f"WriteFileTool: Wrote file {path} ({len(content)} bytes)")

            return ToolResult(
                success=True,
                output=f"File written successfully: {path}",
                metadata={"path": str(path), "size_bytes": len(content)},
            )

        except PermissionError:
            error_msg = f"Permission denied: {path}"
            logger.error(f"WriteFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except IsADirectoryError:
            error_msg = f"Path is a directory: {path}"
            logger.error(f"WriteFileTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Failed to write file: {type(e).__name__}: {e!s}"
            logger.error(f"WriteFileTool: {error_msg} (path={path})", exc_info=True)
            return ToolResult(success=False, error=error_msg)
