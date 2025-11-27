"""
Search File Tool for vibe-agency OS (ARCH-042).

Empowers the agent to find files by pattern.
"""

import logging
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger(__name__)


class SearchFileTool(Tool):
    """
    Tool for searching files by name pattern.

    Allows LLM agents to find files without knowing the exact path.
    """

    @property
    def name(self) -> str:
        return "search_file"

    @property
    def description(self) -> str:
        return "Search for files matching a glob pattern (e.g., '*.py')"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "pattern": {
                "type": "string",
                "required": True,
                "description": "Glob pattern to search for (e.g., '*.py', 'test_*.py')",
            },
            "path": {
                "type": "string",
                "required": False,
                "description": "Root directory to search in (defaults to current working directory)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate parameters.

        Args:
            parameters: Must contain 'pattern' (string)
        """
        if "pattern" not in parameters:
            raise ValueError("Missing required parameter: pattern")

        if not isinstance(parameters["pattern"], str):
            raise TypeError("pattern must be a string")

        if "path" in parameters and not isinstance(parameters["path"], str):
            raise TypeError("path must be a string")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute file search.

        Args:
            parameters: {"pattern": "*.py", "path": "optional/root"}

        Returns:
            ToolResult with list of matching file paths
        """
        pattern = parameters["pattern"]
        path_str = parameters.get("path", ".")

        try:
            # Resolve search root
            search_root = Path(path_str).expanduser().resolve()
            workspace_root = Path.cwd().resolve()

            # Security Check: Ensure search root is within workspace
            if not str(search_root).startswith(str(workspace_root)):
                return ToolResult(
                    success=False,
                    error=f"Access denied: Search path {search_root} is outside workspace {workspace_root}",
                )

            if not search_root.exists():
                return ToolResult(success=False, error=f"Path not found: {search_root}")

            # Perform search (recursive)
            # We use rglob for recursive search
            matches = []

            # Limit results to prevent overwhelming output
            MAX_RESULTS = 50

            for item in search_root.rglob(pattern):
                # Security: Skip hidden directories like .git
                if any(part.startswith(".") and part != ".vibe" for part in item.parts):
                    continue

                if item.is_file():
                    # Return relative path for readability
                    try:
                        rel_path = item.relative_to(workspace_root)
                        matches.append(str(rel_path))
                    except ValueError:
                        # Should not happen given the security check, but safe fallback
                        matches.append(str(item))

                if len(matches) >= MAX_RESULTS:
                    break

            matches.sort()

            if not matches:
                return ToolResult(success=True, output="No matches found.")

            output = "\n".join(matches)
            if len(matches) >= MAX_RESULTS:
                output += f"\n\n(Truncated at {MAX_RESULTS} results)"

            logger.info(
                f"SearchFileTool: Found {len(matches)} matches for '{pattern}' in {search_root}"
            )

            return ToolResult(
                success=True,
                output=output,
                metadata={"count": len(matches), "truncated": len(matches) >= MAX_RESULTS},
            )

        except Exception as e:
            error_msg = f"Failed to search files: {type(e).__name__}: {e!s}"
            logger.error(f"SearchFileTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)
