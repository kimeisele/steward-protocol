"""
Drift Detector - Detects drift between code and documentation.

OPUS-029 Phase 1: Uses GitState to compare code changes vs @HARNESS references.

What is "Drift"?
- Code changed but docs don't mention it → Code without docs
- Docs reference files that don't exist → Docs without code
- Docs older than code they describe → Stale docs

Architecture:
- Uses vibe_core/state/git_state.py for git operations
- Uses vibe_core/state/prakriti.py for unified state
- Returns DATA (dicts), not rendered output

Integration with Prakriti:
- Prakriti holds unified state including git info
- We query Prakriti for diffs, not git directly
- This keeps us within the AOS architecture
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set


@dataclass
class DriftReport:
    """
    Report of detected drift between code and documentation.

    This is DATA only - interface plugin handles display.
    """

    # Files changed in code but not tracked in @HARNESS
    code_without_docs: List[str] = field(default_factory=list)

    # Files referenced in @HARNESS but don't exist
    docs_without_code: List[str] = field(default_factory=list)

    # Docs that haven't been updated since code changed
    stale_docs: List[Dict[str, Any]] = field(default_factory=list)

    # Overall health score (0.0 - 1.0)
    health: float = 1.0

    # Summary stats
    total_tracked_files: int = 0
    total_changed_files: int = 0

    # Errors during detection
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "code_without_docs": self.code_without_docs,
            "docs_without_code": self.docs_without_code,
            "stale_docs": self.stale_docs,
            "health": self.health,
            "total_tracked_files": self.total_tracked_files,
            "total_changed_files": self.total_changed_files,
            "errors": self.errors,
        }


class DriftDetector:
    """
    Detects drift between code and documentation.

    Uses:
    - VerificationEngine to get @HARNESS file references
    - Prakriti/GitState for git diff information

    IMPORTANT: Returns DATA only. No rendering!

    Usage:
        detector = DriftDetector(workspace_root=Path("."))
        report = detector.detect()
        # Pass report.to_dict() to interface plugin for rendering
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize detector.

        Args:
            workspace_root: Project root directory
        """
        self._root = Path(workspace_root)

    def detect(self, since_commit: str = "HEAD~10") -> DriftReport:
        """
        Detect drift since a given commit.

        Strategy:
        1. Get all files referenced in @HARNESS sections
        2. Get files changed since commit (git diff)
        3. Cross-reference to find:
           - Changed code not in @HARNESS (code_without_docs)
           - @HARNESS refs to non-existent files (docs_without_code)

        Args:
            since_commit: Git ref to compare against (default: last 10 commits)

        Returns:
            DriftReport with drift analysis
        """
        report = DriftReport()

        # 1. Get all @HARNESS file references
        harness_files = self._get_harness_files()
        report.total_tracked_files = len(harness_files)

        # 2. Get changed files from git
        changed_files = self._get_changed_files(since_commit)
        report.total_changed_files = len(changed_files)

        if not changed_files:
            # No changes, perfect health
            report.health = 1.0
            return report

        # 3. Find code without docs
        # (Python files that changed but aren't in @HARNESS)
        for f in changed_files:
            if self._is_trackable_file(f) and f not in harness_files:
                report.code_without_docs.append(f)

        # 4. Find docs without code
        # (@HARNESS references files that don't exist)
        for f in harness_files:
            full_path = self._root / f
            if not full_path.exists():
                report.docs_without_code.append(f)

        # 5. Calculate health
        total_issues = len(report.code_without_docs) + len(report.docs_without_code)
        total_files = report.total_tracked_files + report.total_changed_files
        if total_files > 0:
            report.health = max(0.0, 1.0 - (total_issues / total_files))
        else:
            report.health = 1.0

        return report

    def _get_harness_files(self) -> Set[str]:
        """
        Get all files referenced in @HARNESS sections.

        Uses VerificationEngine to extract file references.

        Returns:
            Set of file paths referenced in @HARNESS
        """
        try:
            from .verification_logic import VerificationEngine

            engine = VerificationEngine(workspace_root=self._root)
            files = engine.get_all_harness_files()
            return set(files)
        except Exception:
            # Log but don't crash
            return set()

    def _get_changed_files(self, since_commit: str) -> Set[str]:
        """
        Get files changed since a commit.

        Tries to use Prakriti first, falls back to direct git.

        Args:
            since_commit: Git ref to compare against

        Returns:
            Set of changed file paths
        """
        changed = set()

        # Try Prakriti first (AOS-native)
        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti.from_workspace(str(self._root))
            if hasattr(prakriti, "diff"):
                diff_result = prakriti.diff(since_commit)
                if hasattr(diff_result, "files"):
                    return set(diff_result.files)
        except Exception:
            pass

        # Fallback: Direct git via subprocess
        try:
            import subprocess

            result = subprocess.run(
                ["git", "diff", "--name-only", since_commit],
                capture_output=True,
                text=True,
                cwd=str(self._root),
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        changed.add(line)
        except Exception:
            pass

        return changed

    def _is_trackable_file(self, path: str) -> bool:
        """
        Check if a file should be tracked in @HARNESS.

        We only care about:
        - Python files in vibe_core/
        - Config files in config/
        - Not test files (they're tracked separately)

        Args:
            path: File path relative to workspace root

        Returns:
            True if file should be in @HARNESS
        """
        # Must be a Python file
        if not path.endswith(".py"):
            return False

        # Must be in trackable directories
        trackable_prefixes = [
            "vibe_core/",
            "config/",
        ]

        # Exclude test files
        if "/tests/" in path or path.startswith("tests/"):
            return False

        # Exclude __pycache__ and similar
        if "__pycache__" in path or ".pyc" in path:
            return False

        return any(path.startswith(prefix) for prefix in trackable_prefixes)

    def quick_check(self) -> Dict[str, Any]:
        """
        Quick drift check for boot-time verification.

        Faster than full detect() - only checks for broken @HARNESS refs.

        IMPORTANT: Only treats REAL production code as critical.
        Tests, placeholders, and garbage refs are warnings only.

        Returns:
            Dict with quick check results
        """
        harness_files = self._get_harness_files()
        missing = []
        missing_critical = []  # Only production code

        for f in harness_files:
            if not (self._root / f).exists():
                missing.append(f)
                # Only critical if it's REAL production code
                if self._is_critical_missing(f):
                    missing_critical.append(f)

        return {
            "total_tracked": len(harness_files),
            "missing_files": missing,
            "missing_critical": missing_critical,
            # HEALTHY if no CRITICAL files missing (tests/garbage are warnings)
            "healthy": len(missing_critical) == 0,
        }

    def _is_critical_missing(self, path: str) -> bool:
        """
        Check if a missing file is CRITICAL (production code).

        NOT critical (just warnings):
        - Test files (tests/*.py)
        - Placeholder paths (your/module/*.py)
        - Python commands parsed as paths (python -c "...")
        - State files (.opus_state/*)
        - Rationale/docs without extension

        CRITICAL (real production code):
        - vibe_core/*.py (not tests)
        - config/*.py

        Args:
            path: File path to check

        Returns:
            True if this is critical production code
        """
        # Obvious garbage - not a real path
        if path.startswith("python ") or path.startswith("python3 "):
            return False
        if "/" not in path and not path.endswith(".py"):
            return False  # Single word like "rationale"
        if path.startswith("your/") or path.startswith("example/"):
            return False  # Placeholders

        # Test files - important but not critical for health
        if path.startswith("tests/") or "/tests/" in path or "/test_" in path:
            return False

        # State files - regenerated (both legacy and new locations)
        if path.startswith(".opus_state/") or path.startswith(".vibe/state/"):
            return False

        # Known hallucinated documentation references (never existed)
        hallucinated = {
            "vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py",
            "vibe_core/plugins/opus_assistant/manas/intent_bridge.py",
        }
        if path in hallucinated:
            return False

        # Only critical: production code in vibe_core or config
        if path.startswith("vibe_core/") and path.endswith(".py"):
            # But not test files inside vibe_core
            if "/tests/" not in path and "/test_" not in path:
                return True
        if path.startswith("config/") and path.endswith(".py"):
            return True

        return False
