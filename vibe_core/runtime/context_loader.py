"""Context Loader - Conveyor Belt #1: Collect ALL signals

Loads project context from multiple sources:
- Session handoff state
- Git status
- Test results
- Project manifest
- Environment checks
"""

import json
import subprocess
from pathlib import Path
from typing import Any


class ContextLoader:
    """Loads project context from multiple sources"""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()

    def load(self) -> dict[str, Any]:
        """Load all context sources with robust error handling"""
        return {
            "session": self._load_session_handoff(),
            "git": self._load_git_status(),
            "tests": self._load_test_status(),
            "manifest": self._load_project_manifest(),
            "environment": self._load_environment(),
        }

    def _load_session_handoff(self) -> dict[str, Any]:
        """Read .session_handoff.json - safe defaults if missing"""
        try:
            handoff_file = self.project_root / ".session_handoff.json"
            if handoff_file.exists():
                with open(handoff_file) as f:
                    data = json.load(f)
                return {
                    "phase": data.get("phase", "PLANNING"),
                    "last_task": data.get("last_task", "none"),
                    "blockers": data.get("blockers", []),
                    "backlog": data.get("backlog", []),
                    "backlog_item": data.get("backlog", [""])[0] if data.get("backlog") else "",
                }
            else:
                return {
                    "phase": "PLANNING",
                    "last_task": "none",
                    "blockers": [],
                    "backlog": [],
                    "backlog_item": "",
                }
        except Exception as e:
            return {
                "phase": "PLANNING",
                "last_task": "none",
                "blockers": [f"Error loading session: {e!s}"],
                "backlog": [],
                "backlog_item": "",
            }

    def _load_git_status(self) -> dict[str, Any]:
        """Get git status - safe defaults if git unavailable"""
        try:
            # Get current branch
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Get uncommitted changes count
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Get recent commits
            log = subprocess.run(
                ["git", "log", "-3", "--oneline"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            uncommitted_files = [line for line in status.stdout.strip().split("\n") if line]

            return {
                "branch": branch.stdout.strip() or "unknown",
                "uncommitted": len(uncommitted_files),
                "uncommitted_files": uncommitted_files[:5],  # First 5
                "recent_commits": log.stdout.strip().split("\n"),
                "last_commit": log.stdout.strip().split("\n")[0] if log.stdout.strip() else "none",
                "status": "available",
            }
        except Exception as e:
            return {
                "branch": "unknown",
                "uncommitted": 0,
                "uncommitted_files": [],
                "recent_commits": [],
                "last_commit": "none",
                "status": f"git_unavailable: {e!s}",
            }

    def _load_test_status(self) -> dict[str, Any]:
        """Check test status - safe defaults if pytest unavailable"""
        try:
            # Check for last failed tests
            cache_file = self.project_root / ".pytest_cache" / "v" / "cache" / "lastfailed"
            if cache_file.exists():
                with open(cache_file) as f:
                    failed_data = json.load(f)
                failing_tests = list(failed_data.keys())
            else:
                failing_tests = []

            return {
                "status": "available",
                "failing": failing_tests,
                "failing_count": len(failing_tests),
                "errors": [],  # Would need actual test run to populate
            }
        except Exception as e:
            return {
                "status": f"pytest_unavailable: {e!s}",
                "failing": [],
                "failing_count": 0,
                "errors": [],
            }

    def _load_project_manifest(self) -> dict[str, Any]:
        """Read project_manifest.json - safe defaults if missing"""
        try:
            manifest_file = self.project_root / "project_manifest.json"
            if manifest_file.exists():
                with open(manifest_file) as f:
                    data = json.load(f)
                return {
                    "project_type": data.get("project_type", "unknown"),
                    "phase": data.get("phase", "PLANNING"),
                    "focus_area": data.get("focus_area", "general"),
                    "test_framework": data.get("test_framework", "pytest"),
                    "docs_path": data.get("docs_path", "docs/"),
                    "structure": data.get("structure", {}),
                }
            else:
                return {
                    "project_type": "unknown",
                    "phase": "PLANNING",
                    "focus_area": "general",
                    "test_framework": "pytest",
                    "docs_path": "docs/",
                    "structure": {},
                }
        except Exception as e:
            return {
                "project_type": "unknown",
                "phase": "PLANNING",
                "focus_area": "general",
                "test_framework": "pytest",
                "docs_path": "docs/",
                "structure": {},
                "error": str(e),
            }

    def _load_environment(self) -> dict[str, Any]:
        """Check environment setup - safe defaults"""
        try:
            venv_exists = (self.project_root / ".venv").exists()

            # Check if we're in a virtual environment
            in_venv = hasattr(subprocess.sys, "real_prefix") or (
                hasattr(subprocess.sys, "base_prefix")
                and subprocess.sys.base_prefix != subprocess.sys.prefix
            )

            return {
                "venv_exists": venv_exists,
                "in_venv": in_venv,
                "python_version": subprocess.sys.version.split()[0],
                "status": "ready" if (venv_exists or in_venv) else "needs_setup",
            }
        except Exception as e:
            return {
                "venv_exists": False,
                "in_venv": False,
                "python_version": "unknown",
                "status": f"error: {e!s}",
            }

    # =========================================================================
    # GAD-502: Context Projection - Vibe Injection
    # =========================================================================

    def inject_context(self, template_str: str) -> str:
        """Inject live context into template with {{ placeholders }}

        Args:
            template_str: Template with {{ category.field }} placeholders

        Returns:
            Filled template with actual values

        Example:
            >>> loader = ContextLoader()
            >>> template = "Branch: {{ git.branch }}"
            >>> loader.inject_context(template)
            "Branch: claude/feature-123"
        """
        import re

        # Load all context sources
        context = self.load()

        # Find all placeholders: {{ key.subkey }}
        pattern = r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}"

        def replace_placeholder(match: re.Match) -> str:
            """Resolve a single placeholder to its value"""
            placeholder = match.group(1)  # e.g., "git.branch"
            parts = placeholder.split(".")

            # Navigate nested dict
            value = context
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                    if value is None:
                        # Fallback: keep original placeholder
                        return match.group(0)
                else:
                    # Can't navigate further
                    return match.group(0)

            # Special formatting for complex types
            if isinstance(value, list):
                if not value:
                    return "none"
                return ", ".join(str(v) for v in value[:3])
            elif isinstance(value, bool):
                return "✅" if value else "❌"
            elif value is None:
                return "unknown"
            else:
                return str(value)

        # Replace all placeholders
        return re.sub(pattern, replace_placeholder, template_str)

    @property
    def context(self) -> dict[str, Any]:
        """Cached context data (loaded once per instance)"""
        if not hasattr(self, "_cached_context"):
            self._cached_context = self.load()
        return self._cached_context

    def format_test_summary(self, tests: dict[str, Any]) -> str:
        """Format test status for human readability

        Args:
            tests: Test context from load()

        Returns:
            Human-readable summary
        """
        if tests.get("status") != "available":
            return f"Unavailable ({tests.get('status', 'unknown')})"

        failing = tests.get("failing_count", 0)
        if failing == 0:
            return "✅ All passing"
        else:
            return f"❌ {failing} test(s) failing"
