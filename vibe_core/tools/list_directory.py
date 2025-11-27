"""
List Directory Tool for vibe-agency OS (ARCH-042).

Empowers the agent to explore the filesystem "Senses".
"""

import logging
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger(__name__)


class ListDirectoryTool(Tool):
    """
    Tool for listing directory contents.

    Allows LLM agents to explore the file structure.
    """

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List files and directories in a given path"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "required": False,
                "description": "Directory path to list (defaults to current working directory)",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate parameters.

        Args:
            parameters: Optional 'path' (string)
        """
        if "path" in parameters:
            path = parameters["path"]
            if not isinstance(path, str):
                raise TypeError(f"path must be a string, got {type(path).__name__}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute directory listing.

        Args:
            parameters: {"path": "optional/path"}

        Returns:
            ToolResult with list of file/directory names
        """
        path_str = parameters.get("path", ".")

        try:
            # Resolve path
            path = Path(path_str).expanduser().resolve()
            workspace_root = Path.cwd().resolve()

            # Security Check: Ensure path is within workspace
            # We allow listing the workspace root and subdirectories
            if not str(path).startswith(str(workspace_root)):
                # Exception: Allow /tmp for some operations if needed, but strictly enforce workspace for now
                # unless it's a specific allowed external path.
                # For strict safety, we block everything outside CWD.
                return ToolResult(
                    success=False,
                    error=f"Access denied: Path {path} is outside workspace {workspace_root}",
                )

            if not path.exists():
                return ToolResult(success=False, error=f"Path not found: {path}")

            if not path.is_dir():
                return ToolResult(success=False, error=f"Path is not a directory: {path}")

            # List contents
            items = []
            for item in path.iterdir():
                # Skip hidden files/dirs (simple security/noise filter)
                if item.name.startswith(".") and item.name != ".vibe":
                    # We might want to see .vibe, but generally skip .git, .env etc.
                    continue

                type_str = "DIR" if item.is_dir() else "FILE"
                items.append(f"[{type_str}] {item.name}")

            # Sort for deterministic output
            items.sort()

            output = "\n".join(items)
            if not output:
                output = "(empty directory)"

            logger.info(f"ListDirectoryTool: Listed {path} ({len(items)} items)")

            return ToolResult(
                success=True, output=output, metadata={"path": str(path), "count": len(items)}
            )

        except PermissionError:
            error_msg = f"Permission denied: {path}"
            logger.error(f"ListDirectoryTool: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Failed to list directory: {type(e).__name__}: {e!s}"
            logger.error(f"ListDirectoryTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)
