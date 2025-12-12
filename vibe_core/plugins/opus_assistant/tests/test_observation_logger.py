"""
OPUS Assistant - Observation Logger Tests

Tests for ObservationLogger (Phase 2.5 Journal).
"""

from pathlib import Path
from unittest.mock import MagicMock


class TestObservationLogger:
    """Tests for ObservationLogger."""

    def test_logger_importable(self):
        """ObservationLogger can be imported."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        assert ObservationLogger is not None

    def test_severity_enum_importable(self):
        """ObservationSeverity enum can be imported."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationSeverity,
        )

        assert ObservationSeverity.INFO is not None
        assert ObservationSeverity.WARN is not None
        assert ObservationSeverity.ALERT is not None
        assert ObservationSeverity.INSIGHT is not None

    def test_observation_dataclass_importable(self):
        """Observation dataclass can be imported."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import Observation

        assert Observation is not None

    def test_logger_instantiation(self):
        """ObservationLogger can be instantiated."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        logger = ObservationLogger(workspace_root=Path("."))
        assert logger is not None

    def test_observation_to_markdown(self):
        """Observation.to_markdown formats correctly."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            Observation,
            ObservationSeverity,
        )

        obs = Observation(
            timestamp="2025-01-01T12:00:00.000",
            severity=ObservationSeverity.WARN,
            message="Test warning message",
            source="test_source",
        )

        md = obs.to_markdown()

        assert "2025-01-01T12:00:00" in md
        assert "⚠️" in md
        assert "[test_source]" in md
        assert "Test warning message" in md

    def test_log_observation_adds_to_journal(self):
        """log_observation adds to internal journal."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
            ObservationSeverity,
        )

        logger = ObservationLogger(workspace_root=Path("."))

        logger.log_observation(
            severity=ObservationSeverity.INFO,
            message="Test observation",
            source="test",
        )

        journal = logger.get_journal()
        assert len(journal.observations) == 1
        assert journal.observations[0].message == "Test observation"

    def test_convenience_methods(self):
        """Convenience methods (log_info, log_warn, etc.) work."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
            ObservationSeverity,
        )

        logger = ObservationLogger(workspace_root=Path("."))

        logger.log_info("Info message")
        logger.log_warn("Warning message")
        logger.log_alert("Alert message")
        logger.log_insight("Insight message")

        journal = logger.get_journal()
        assert len(journal.observations) == 4

        severities = [obs.severity for obs in journal.observations]
        assert ObservationSeverity.INFO in severities
        assert ObservationSeverity.WARN in severities
        assert ObservationSeverity.ALERT in severities
        assert ObservationSeverity.INSIGHT in severities

    def test_journal_max_entries(self):
        """Journal respects max_entries limit (FIFO)."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        logger = ObservationLogger(workspace_root=Path("."), max_entries=5)

        for i in range(10):
            logger.log_info(f"Message {i}")

        journal = logger.get_journal()
        assert len(journal.observations) == 5

        # Should have messages 5-9 (most recent)
        messages = [obs.message for obs in journal.observations]
        assert "Message 5" in messages
        assert "Message 9" in messages
        assert "Message 0" not in messages

    def test_get_pending_count(self):
        """get_pending_count returns correct count."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        logger = ObservationLogger(workspace_root=Path("."))

        assert logger.get_pending_count() == 0

        logger.log_info("Test 1")
        logger.log_info("Test 2")

        assert logger.get_pending_count() == 2

    def test_clear_resets_journal(self):
        """clear() resets the journal."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        logger = ObservationLogger(workspace_root=Path("."))

        logger.log_info("Test")
        assert logger.get_pending_count() == 1

        logger.clear()
        assert logger.get_pending_count() == 0

    def test_no_rendering_in_logger(self):
        """observation_logger.py has no rich/UI imports."""
        logger_path = Path(__file__).parent.parent / "core" / "observation_logger.py"
        content = logger_path.read_text()

        assert "from rich" not in content
        assert "import rich" not in content
        assert "BasePanel" not in content


class TestObservationLoggerIntegration:
    """Integration tests for ObservationLogger."""

    def test_flush_creates_opus_md(self, tmp_path):
        """flush_to_opus creates OPUS.md if not exists."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        logger = ObservationLogger(workspace_root=tmp_path)

        logger.log_info("Test observation")
        result = logger.flush_to_opus()

        assert result is True
        assert (tmp_path / "OPUS.md").exists()

        content = (tmp_path / "OPUS.md").read_text()
        assert "System Observations" in content
        assert "Test observation" in content

    def test_flush_updates_existing_opus(self, tmp_path):
        """flush_to_opus updates existing OPUS.md."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        # Create initial OPUS.md
        opus_path = tmp_path / "OPUS.md"
        opus_path.write_text("""# OPUS.md

## Existing Content
This should be preserved.

<!-- @HUMAN START -->
Human notes here.
<!-- @HUMAN END -->
""")

        logger = ObservationLogger(workspace_root=tmp_path)
        logger.log_warn("New warning observation")
        logger.flush_to_opus()

        content = opus_path.read_text()

        # Should preserve existing content
        assert "Existing Content" in content
        assert "Human notes here" in content

        # Should add observation
        assert "New warning observation" in content

    def test_journal_section_is_append_only(self, tmp_path):
        """Journal section preserves previous entries."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        opus_path = tmp_path / "OPUS.md"

        # First flush
        logger1 = ObservationLogger(workspace_root=tmp_path)
        logger1.log_info("First observation")
        logger1.flush_to_opus()

        # Second flush with new logger (simulating restart)
        logger2 = ObservationLogger(workspace_root=tmp_path)
        logger2.log_warn("Second observation")
        logger2.flush_to_opus()

        content = opus_path.read_text()

        # Should have both observations
        assert "Second observation" in content

    def test_exports_from_core(self):
        """Observation logger exported from core __init__."""
        from vibe_core.plugins.opus_assistant.core import (
            Observation,
            ObservationJournal,
            ObservationLogger,
            ObservationSeverity,
        )

        assert ObservationLogger is not None
        assert ObservationSeverity is not None
        assert Observation is not None
        assert ObservationJournal is not None


class TestKernelTickWithObservations:
    """Tests for KernelTickHandler with observation logger."""

    def test_tick_handler_has_observation_logger(self):
        """KernelTickHandler initializes observation logger."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {"kernel_tick": {"enabled": True}}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)

        assert handler._observation_logger is not None

    def test_get_observation_logger_accessor(self):
        """get_observation_logger() returns the logger."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)
        obs_logger = handler.get_observation_logger()

        assert obs_logger is not None

    def test_log_observation_helpers_exist(self):
        """Handler has observation logging helper methods."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)

        assert hasattr(handler, "_log_observation_info")
        assert hasattr(handler, "_log_observation_warn")
        assert hasattr(handler, "_log_observation_alert")
        assert hasattr(handler, "_log_observation_insight")
        assert hasattr(handler, "_flush_observations")

    def test_consecutive_drift_tracking(self):
        """Handler tracks consecutive drift ticks."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)

        assert handler._consecutive_drift_ticks == 0
        assert handler._last_health_status is None
