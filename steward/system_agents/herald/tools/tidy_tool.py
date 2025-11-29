"""
TidyTool: Repository Organization & Maintenance Capability

HERALD's housekeeping module. Ensures the repository stays organized
by moving files to their proper locations based on Tidy Protocols
defined in STEWARD.md.

Philosophy: The agent cleans up after itself.
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("HERALD_TIDY")


class TidyTool:
    """
    Repository maintenance and file organization capability for HERALD.

    Reads organization rules from STEWARD.md and autonomously organizes
    files in the repository without deleting anything.
    """

    # Patterns that should NEVER be moved (protected)
    PROTECTED_PATTERNS = [
        r"^herald/",  # HERALD's core logic
        r"^\.github/",  # GitHub workflows
        r"^STEWARD\.md$",  # Protocol document
        r"^requirements\.txt$",  # Dependencies
        r"^\.gitignore$",  # Git rules
        r"\.md$",  # Documentation files
        r"^[^/]+\.py$",  # Root-level Python files
        r"^\.git",  # Git internals
        r"^dist/",  # Build outputs
        r"^__pycache__",  # Python cache
        r"^\.pytest_cache",  # Test cache
    ]

    # Default organization rules (if STEWARD.md not readable)
    DEFAULT_RULES = {
        r"\.log$": "data/logs/",
        r"\.jsonl$": "data/history/",
        r"\.csv$": "data/analysis/",
        r"\.png$": "assets/media/",
        r"\.jpg$": "assets/media/",
        r"^temp_": "_archive/quarantine/",
        r"^debug_": "_archive/quarantine/",
    }

    def __init__(self, root_path: Optional[Path] = None, steward_path: Optional[Path] = None):
        """
        Initialize TidyTool.

        Args:
            root_path: Root directory to organize (defaults to current directory)
            steward_path: Path to STEWARD.md (defaults to ./STEWARD.md)
        """
        self.root_path = Path(root_path or ".")
        self.steward_path = Path(steward_path or "STEWARD.md")
        self.rules = self._load_rules_from_steward()
        self.moved_count = 0
        self.protected_count = 0
        self.error_count = 0

    def _load_rules_from_steward(self) -> Dict[str, str]:
        """
        Parse organization rules from STEWARD.md.

        Extracts the rules from the Tidy Protocols section.

        Returns:
            Dict mapping regex patterns to target directories
        """
        if not self.steward_path.exists():
            logger.warning("⚠️  STEWARD.md not found, using default rules")
            return self.DEFAULT_RULES

        try:
            content = self.steward_path.read_text(encoding="utf-8")

            # Find the Tidy Protocols section
            if "## 🧹 Tidy Protocols" not in content:
                logger.warning("⚠️  Tidy Protocols section not found, using default rules")
                return self.DEFAULT_RULES

            # Extract organization rules block
            rules = {}
            in_rules_section = False
            for line in content.split("\n"):
                if "### Organization Rules" in line:
                    in_rules_section = True
                    continue

                if in_rules_section and line.startswith("###"):
                    break

                if in_rules_section and line.startswith("* "):
                    # Parse rule: "* .log files       -> data/logs/"
                    parts = line.replace("*", "").strip().split("->")
                    if len(parts) == 2:
                        pattern_text = parts[0].strip()
                        target = parts[1].strip().rstrip("/")

                        # Extract just the extension/pattern
                        # E.g., ".log files" -> ".log", "temp_*, debug_*" -> "temp_"
                        pattern_part = pattern_text.split()[0]  # Get first token

                        # Convert human-readable pattern to regex
                        if pattern_part.startswith("."):
                            # Extension pattern: ".log" -> r"\.log$"
                            escaped = pattern_part.replace(".", r"\.")
                            pattern = f"{escaped}$"
                        else:
                            # Prefix pattern: "temp_" or "debug_" -> r"^temp_" or r"^debug_"
                            pattern = f"^{pattern_part}"

                        rules[pattern] = target

            return rules if rules else self.DEFAULT_RULES

        except Exception as e:
            logger.error(f"❌ Failed to load Tidy Protocols from STEWARD.md: {e}")
            return self.DEFAULT_RULES

    def _is_protected(self, file_path: Path) -> bool:
        """
        Check if a file matches any protected pattern.

        Args:
            file_path: File to check (relative to root)

        Returns:
            True if file is protected (should not be moved)
        """
        relative_path = str(file_path.relative_to(self.root_path))

        for pattern in self.PROTECTED_PATTERNS:
            if re.search(pattern, relative_path):
                return True

        return False

    def _find_target_directory(self, file_path: Path) -> Optional[str]:
        """
        Find the target directory for a file based on Tidy rules.

        Args:
            file_path: File to categorize

        Returns:
            Target directory path or None if no match
        """
        file_name = file_path.name

        for pattern, target_dir in self.rules.items():
            if re.search(pattern, file_name):
                return target_dir

        return None

    def _move_file_with_git(self, source: Path, dest: Path) -> bool:
        """
        Move a file using git mv to preserve history.

        Args:
            source: Source file path
            dest: Destination file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create target directory if needed
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Use git mv to preserve history
            result = subprocess.run(
                ["git", "mv", str(source), str(dest)],
                cwd=self.root_path,
                capture_output=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"✅ Moved: {source.name} -> {dest}")
                return True
            else:
                # Fallback to regular move if git mv fails
                logger.warning(f"⚠️  git mv failed ({result.stderr.decode()}), falling back to regular move")
                if source.exists():
                    source.rename(dest)
                return True

        except Exception as e:
            logger.error(f"❌ Failed to move {source.name}: {e}")
            return False

    def organize_workspace(self, dry_run: bool = False) -> Tuple[int, int, int]:
        """
        Scan and organize files in the repository.

        Args:
            dry_run: If True, report what would be moved without actually moving

        Returns:
            Tuple of (moved_count, protected_count, error_count)
        """
        self.moved_count = 0
        self.protected_count = 0
        self.error_count = 0

        logger.info("🧹 TIDY: Starting workspace organization...")

        # Scan root directory (non-recursive)
        try:
            for item in self.root_path.iterdir():
                # Skip directories and hidden files
                if item.is_dir() or item.name.startswith("."):
                    continue

                # Check if protected
                if self._is_protected(item):
                    logger.debug(f"🛡️  Protected: {item.name}")
                    self.protected_count += 1
                    continue

                # Find target directory
                target_dir = self._find_target_directory(item)
                if target_dir is None:
                    logger.debug(f"📍 No rule found for: {item.name}")
                    continue

                # Move the file
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
            logger.error(f"❌ Error scanning workspace: {e}")
            self.error_count += 1

        # Log summary
        if self.moved_count > 0 or self.protected_count > 0:
            summary = f"🧹 TIDY: Organized {self.moved_count} files"
            if self.protected_count > 0:
                summary += f", protected {self.protected_count}"
            if self.error_count > 0:
                summary += f", errors: {self.error_count}"
            logger.info(summary)
        else:
            logger.info("🧹 TIDY: Workspace is clean (no files to organize)")

        return self.moved_count, self.protected_count, self.error_count

    def get_status_message(self) -> str:
        """
        Get a human-readable status message for Scribe logging.

        Returns:
            Formatted message for chronicles
        """
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
