"""
Test Health Panel - LIVE pytest scanner.

Runs pytest --collect-only and parses results.
Shows test health without actually running tests.

DATA-DRIVEN: Pure pytest output parsing, no hardcoding.
"""

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_panel import OpusPanel

logger = logging.getLogger("PANEL_TEST_HEALTH")


@dataclass
class TestItem:
    """A single test item."""

    path: str
    name: str
    status: str = "unknown"  # collected, passed, failed, error, skipped
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class TestSummary:
    """Summary of test health."""

    total_collected: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_errors: int = 0
    total_skipped: int = 0
    by_directory: Dict[str, Dict[str, int]] = field(default_factory=dict)
    failed_tests: List[TestItem] = field(default_factory=list)
    error_tests: List[TestItem] = field(default_factory=list)
    collection_errors: List[str] = field(default_factory=list)


class TestHealthPanel(OpusPanel):
    """
    LIVE Test Health Scanner.

    Collects test info via pytest --collect-only.
    Optionally runs quick tests for real status.
    """

    def __init__(self):
        self._cache: Optional[TestSummary] = None
        self._cache_time: float = 0
        self._cache_ttl: float = 120  # 2 minutes cache

    @property
    def panel_id(self) -> str:
        return "test_health"

    @property
    def priority(self) -> int:
        return 45  # After status, before debt

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render the test health panel."""
        import time

        now = time.time()

        # Use cache if valid
        if self._cache and (now - self._cache_time) < self._cache_ttl:
            summary = self._cache
        else:
            summary = self._collect_test_info()
            self._cache = summary
            self._cache_time = now

        return self._format_panel(summary)

    def _collect_test_info(self) -> TestSummary:
        """Collect test information via pytest."""
        summary = TestSummary()
        root = Path.cwd()
        tests_path = root / "tests"

        if not tests_path.exists():
            summary.collection_errors.append("tests/ directory not found")
            return summary

        # Run pytest --collect-only for fast collection
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "--collect-only", "-q", "--ignore=tests/fixtures"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(root),
            )

            # Parse collection output
            self._parse_collection_output(result.stdout, result.stderr, summary)

        except subprocess.TimeoutExpired:
            summary.collection_errors.append("Collection timed out (30s)")
        except Exception as e:
            summary.collection_errors.append(f"Collection error: {e}")

        return summary

    def _parse_collection_output(self, stdout: str, stderr: str, summary: TestSummary) -> None:
        """Parse pytest --collect-only output."""
        # Count collected tests from stdout
        for line in stdout.splitlines():
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith("=") or line.startswith("-"):
                continue

            # Test items look like: tests/test_foo.py::test_bar
            if "::" in line and line.startswith("tests/"):
                summary.total_collected += 1

                # Extract directory
                parts = line.split("/")
                if len(parts) >= 2:
                    dir_name = parts[1].split("::")[0]  # e.g., test_foo.py or subdir
                    if dir_name.endswith(".py"):
                        dir_name = "root"
                    else:
                        dir_name = parts[1] if len(parts) > 2 else "root"

                    if dir_name not in summary.by_directory:
                        summary.by_directory[dir_name] = {"collected": 0}
                    summary.by_directory[dir_name]["collected"] += 1

            # Summary line: "X tests collected"
            if "test" in line and "collected" in line:
                try:
                    # Extract number
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p.isdigit():
                            summary.total_collected = int(p)
                            break
                except Exception:
                    pass

        # Check for collection errors in stderr
        if stderr:
            for line in stderr.splitlines():
                if "ERROR" in line or "error" in line.lower():
                    summary.collection_errors.append(line.strip()[:100])

    def _format_panel(self, summary: TestSummary) -> str:
        """Format the test health summary as markdown."""
        lines = [
            "## Test Health",
            "",
            f"> **Collected:** {summary.total_collected} tests",
            "",
        ]

        # Collection Errors (if any)
        if summary.collection_errors:
            lines.append("### Collection Errors")
            lines.append("")
            for err in summary.collection_errors[:5]:
                lines.append(f"- `{err[:60]}...`" if len(err) > 60 else f"- `{err}`")
            lines.append("")

        # By Directory
        if summary.by_directory:
            lines.append("### By Directory")
            lines.append("")
            lines.append("| Directory | Tests |")
            lines.append("|-----------|-------|")
            for dir_name, counts in sorted(summary.by_directory.items(), key=lambda x: -x[1].get("collected", 0)):
                collected = counts.get("collected", 0)
                lines.append(f"| `{dir_name}/` | {collected} |")
            lines.append("")

        # Quick Stats
        lines.append("### Quick Actions")
        lines.append("")
        lines.append("```bash")
        lines.append("# Run all tests")
        lines.append("pytest tests/ -v --timeout=60")
        lines.append("")
        lines.append("# Run fast tests only")
        lines.append("pytest tests/ -v --timeout=10 -x")
        lines.append("```")
        lines.append("")

        lines.append("---")
        lines.append("*Collected via pytest --collect-only*")

        return "\n".join(lines)
