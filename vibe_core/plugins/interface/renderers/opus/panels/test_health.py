"""
Test Health Panel - Tracks test suite standardization and coverage.

Shows:
- Active vs archived tests
- Tests using proper fixtures vs direct kernel
- Test categories breakdown
"""

from typing import TYPE_CHECKING

from . import BasePanel

if TYPE_CHECKING:
    pass


class TestHealthPanel(BasePanel):
    """Tracks test suite health and standardization."""

    @property
    def panel_id(self) -> str:
        return "test_health"

    @property
    def title(self) -> str:
        return "Test Suite Health"

    @property
    def priority(self) -> int:
        return 15  # Show after code health

    def render(self) -> str:
        """Scan and render test health metrics."""
        # Use cache for expensive operations
        cached = self.get_cached("test_metrics")
        if cached:
            return self._render_metrics(cached)

        metrics = self._gather_metrics()
        self.set_cached("test_metrics", metrics)
        return self._render_metrics(metrics)

    def _gather_metrics(self) -> dict:
        """Gather test suite metrics."""
        tests_dir = self._root / "tests"

        # Count active tests (not in archive)
        active_tests = list(tests_dir.glob("**/test_*.py"))
        active_tests = [t for t in active_tests if "archive" not in str(t)]

        # Count archived/broken tests
        archive_dir = tests_dir / "archive"
        archived_tests = list(archive_dir.glob("**/test_*.py")) if archive_dir.exists() else []

        # Count by category
        unit_tests = [t for t in active_tests if "/unit/" in str(t)]
        integration_tests = [t for t in active_tests if "/integration/" in str(t)]
        hardening_tests = [t for t in active_tests if "/hardening/" in str(t)]
        root_tests = [t for t in active_tests if str(t.parent) == str(tests_dir)]

        # Count fixture usage (expensive - scan file contents)
        using_fixtures = 0
        using_raw_kernel = 0

        for test_file in active_tests[:50]:  # Limit scan
            try:
                content = test_file.read_text()
                if "from vibe_core.plugins.test_orchestration.fixtures import" in content:
                    using_fixtures += 1
                elif "test_kernel" in content or "compliant_agent" in content:
                    using_fixtures += 1  # Using conftest fixtures
                elif "RealVibeKernel" in content:
                    using_raw_kernel += 1
            except Exception:
                pass

        return {
            "active_count": len(active_tests),
            "archived_count": len(archived_tests),
            "unit_count": len(unit_tests),
            "integration_count": len(integration_tests),
            "hardening_count": len(hardening_tests),
            "root_count": len(root_tests),
            "using_fixtures": using_fixtures,
            "using_raw_kernel": using_raw_kernel,
        }

    def _render_metrics(self, metrics: dict) -> str:
        """Render metrics as markdown."""
        lines = [f"## {self.title}", ""]

        # Summary table
        lines.append("| Metric | Count | Status |")
        lines.append("| --- | --- | --- |")

        # Active vs Archived
        active = metrics["active_count"]
        archived = metrics["archived_count"]
        lines.append(f"| Active Tests | {active} | - |")
        if archived > 0:
            lines.append(f"| Archived (broken) | {archived} | - |")

        # Categories
        root = metrics["root_count"]
        if root > 10:
            lines.append(f"| Unorganized (root) | {root} | - |")
        else:
            lines.append(f"| Organized | {active - root}/{active} | - |")

        lines.append(f"| Unit Tests | {metrics['unit_count']} | - |")
        lines.append(f"| Integration Tests | {metrics['integration_count']} | - |")
        lines.append(f"| Hardening Tests | {metrics['hardening_count']} | - |")

        # Fixture adoption
        using_fix = metrics["using_fixtures"]
        using_raw = metrics["using_raw_kernel"]
        total_scanned = using_fix + using_raw
        if total_scanned > 0:
            pct = (using_fix / total_scanned) * 100
            status = "OK" if pct >= 50 else "LOW"
            lines.append(f"| Using Fixtures | {using_fix}/{total_scanned} ({pct:.0f}%) | {status} |")

        # Actionable guidance
        lines.append("")

        if archived > 0:
            lines.append(f"**Debt:** {archived} tests in `tests/archive/` need revival")

        if root > 10:
            lines.append(f"**Org:** {root} tests in root - move to unit/integration/")

        if using_raw > using_fix:
            lines.append("**Standard:** Prefer `test_kernel` fixture over `RealVibeKernel`")

        return "\n".join(lines)
