"""
TidyTool: Repository Organization & Maintenance Capability (Tool Protocol)

MECHANIC's housekeeping module. Ensures the repository stays organized
by moving files to their proper locations based on hardcoded rules.

Philosophy: The agent cleans up after itself.
Rules are CODE, not config. No external file dependencies.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x5665528e"  # GenesisByte: parampara % 37 == 0

import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Optional, Tuple

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("MECHANIC_TIDY")


class TidyTool(Tool):
    """
    Repository maintenance and file organization capability for MECHANIC.

    Uses hardcoded rules - NO external config files.
    Organizes files without deleting anything.
    """

    # Patterns that should NEVER be moved (protected)
    PROTECTED_PATTERNS = [
        r"^\.github/",  # GitHub workflows
        r"^requirements\.txt$",  # Dependencies
        r"^\.gitignore$",  # Git rules
        r"\.md$",  # Documentation files
        r"^[^/]+\.py$",  # Root-level Python files
        r"^\.git",  # Git internals
        r"^dist/",  # Build outputs
        r"^__pycache__",  # Python cache
        r"^\.pytest_cache",  # Test cache
        r"^pyproject\.toml$",  # Project config
        r"^setup\.py$",  # Setup script
    ]

    # Organization rules - HARDCODED, no external config
    RULES = {
        r"\.log$": "data/logs/",
        r"\.jsonl$": "data/history/",
        r"\.csv$": "data/analysis/",
        r"\.png$": "assets/media/",
        r"\.jpg$": "assets/media/",
        r"\.jpeg$": "assets/media/",
        r"\.gif$": "assets/media/",
        r"\.svg$": "assets/media/",
        r"^temp_": "_archive/quarantine/",
        r"^debug_": "_archive/quarantine/",
        r"^test_output_": "_archive/quarantine/",
    }

    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize TidyTool.

        Args:
            root_path: Root directory to organize (defaults to current directory)
        """
        self.root_path = Path(root_path or ".")
        self.moved_count = 0
        self.protected_count = 0
        self.error_count = 0

    @property
    def name(self) -> str:
        return "mechanic.tidy"

    @property
    def description(self) -> str:
        return "Repository organization and maintenance - organize workspace, get status"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action to perform: 'organize_workspace', 'get_status'",
            },
            "dry_run": {
                "type": "boolean",
                "required": False,
                "description": "If true, report what would be moved without actually moving (default: false)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate tidy parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["organize_workspace", "get_status"]:
            raise ValueError(f"Invalid action: {action}. Must be 'organize_workspace' or 'get_status'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute tidy operation."""
        try:
            action = parameters["action"]

            if action == "organize_workspace":
                dry_run = parameters.get("dry_run", False)
                moved, protected, errors = self._organize_workspace(dry_run=dry_run)

                return ToolResult(
                    success=True,
                    output={
                        "moved_count": moved,
                        "protected_count": protected,
                        "error_count": errors,
                        "dry_run": dry_run,
                        "status": self._get_status_message(),
                    },
                    metadata={
                        "action": "organize_workspace",
                        "moved": moved,
                        "protected": protected,
                        "errors": errors,
                    },
                )

            elif action == "get_status":
                return ToolResult(
                    success=True,
                    output={
                        "status": self._get_status_message(),
                        "moved_count": self.moved_count,
                        "protected_count": self.protected_count,
                        "error_count": self.error_count,
                    },
                    metadata={"action": "get_status"},
                )

            return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            error_msg = f"Tidy operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"TidyTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _is_protected(self, file_path: Path) -> bool:
        """Check if a file matches any protected pattern."""
        relative_path = str(file_path.relative_to(self.root_path))

        for pattern in self.PROTECTED_PATTERNS:
            if re.search(pattern, relative_path):
                return True
        return False

    def _find_target_directory(self, file_path: Path) -> Optional[str]:
        """Find the target directory for a file based on rules."""
        file_name = file_path.name

        for pattern, target_dir in self.RULES.items():
            if re.search(pattern, file_name):
                return target_dir
        return None

    def _move_file_with_git(self, source: Path, dest: Path) -> bool:
        """Move a file using git mv to preserve history."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                ["git", "mv", str(source), str(dest)],
                cwd=self.root_path,
                capture_output=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"Moved: {source.name} -> {dest}")
                return True
            else:
                # Fallback to regular move if git mv fails
                if source.exists():
                    source.rename(dest)
                return True

        except Exception as e:
            logger.error(f"Failed to move {source.name}: {e}")
            return False

    def _organize_workspace(self, dry_run: bool = False) -> Tuple[int, int, int]:
        """Scan and organize files in the repository."""
        self.moved_count = 0
        self.protected_count = 0
        self.error_count = 0

        logger.info("TIDY: Starting workspace organization...")

        try:
            for item in self.root_path.iterdir():
                if item.is_dir() or item.name.startswith("."):
                    continue

                if self._is_protected(item):
                    self.protected_count += 1
                    continue

                target_dir = self._find_target_directory(item)
                if target_dir is None:
                    continue

                target_path = self.root_path / target_dir / item.name

                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {item.name} -> {target_dir}")
                    self.moved_count += 1
                else:
                    if self._move_file_with_git(item, target_path):
                        self.moved_count += 1
                    else:
                        self.error_count += 1

        except Exception as e:
            logger.error(f"Error scanning workspace: {e}")
            self.error_count += 1

        if self.moved_count > 0:
            logger.info(f"TIDY: Organized {self.moved_count} files")
        else:
            logger.info("TIDY: Workspace is clean")

        return self.moved_count, self.protected_count, self.error_count

    def _get_status_message(self) -> str:
        """Get a human-readable status message."""
        if self.moved_count == 0 and self.error_count == 0:
            return "workspace is clean"

        parts = []
        if self.moved_count > 0:
            parts.append(f"organized {self.moved_count} files")
        if self.protected_count > 0:
            parts.append(f"protected {self.protected_count}")
        if self.error_count > 0:
            parts.append(f"{self.error_count} errors")

        return " | ".join(parts)
