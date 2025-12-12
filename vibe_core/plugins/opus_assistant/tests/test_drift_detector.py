"""
OPUS Assistant - Drift Detector Tests

Tests for DriftDetector functionality.
"""

from pathlib import Path


class TestDriftDetector:
    """Tests for DriftDetector."""

    def test_detector_importable(self):
        """DriftDetector can be imported."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        assert DriftDetector is not None

    def test_detector_instantiation(self):
        """DriftDetector can be instantiated."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        detector = DriftDetector(workspace_root=Path("."))
        assert detector is not None

    def test_drift_report_to_dict(self):
        """DriftReport can be converted to dict."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftReport

        report = DriftReport(
            code_without_docs=["file1.py"],
            docs_without_code=["missing.py"],
            health=0.8,
        )

        result = report.to_dict()

        assert "code_without_docs" in result
        assert "docs_without_code" in result
        assert "health" in result
        assert result["health"] == 0.8

    def test_quick_check_returns_dict(self):
        """quick_check returns proper structure."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        # Use project root (tests/ → opus_assistant/ → plugins/ → vibe_core/ → root)
        workspace = Path(__file__).parent.parent.parent.parent.parent
        detector = DriftDetector(workspace_root=workspace)

        result = detector.quick_check()

        assert "total_tracked" in result
        assert "missing_files" in result
        assert "healthy" in result

    def test_detect_returns_report(self):
        """detect() returns DriftReport."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import (
            DriftDetector,
            DriftReport,
        )

        # Use project root (tests/ → opus_assistant/ → plugins/ → vibe_core/ → root)
        workspace = Path(__file__).parent.parent.parent.parent.parent
        detector = DriftDetector(workspace_root=workspace)

        report = detector.detect()

        assert isinstance(report, DriftReport)
        assert 0.0 <= report.health <= 1.0

    def test_is_trackable_file(self):
        """_is_trackable_file correctly filters files."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        detector = DriftDetector(workspace_root=Path("."))

        # Should track
        assert detector._is_trackable_file("vibe_core/kernel.py") is True
        assert detector._is_trackable_file("config/phoenix.py") is True

        # Should NOT track
        assert detector._is_trackable_file("tests/test_something.py") is False
        assert detector._is_trackable_file("vibe_core/tests/test_x.py") is False
        assert detector._is_trackable_file("README.md") is False
        assert detector._is_trackable_file("script.sh") is False

    def test_no_rendering_in_detector(self):
        """DriftDetector has no rich/UI imports."""
        detector_path = Path(__file__).parent.parent / "core" / "drift_detector.py"
        content = detector_path.read_text()

        assert "from rich" not in content
        assert "import rich" not in content
        assert "BasePanel" not in content
