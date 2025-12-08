"""
TEST: Sarga Cycle Plugin (The Heart)
====================================
Verifies the Cosmic Gate logic (Day/Night of Brahma).
Target: vibe_core/plugins/sarga_cycle/plugin_main.py
Standard: GAD-5000
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.sarga_cycle.plugin_main import SargaCyclePlugin


class MockTask:
    def __init__(self, task_type):
        self.task_id = "task-123"
        self.payload = {"type": task_type}


class TestSargaCyclePlugin:
    def setup_method(self):
        self.plugin = SargaCyclePlugin()
        self.kernel = MagicMock()

    @patch("vibe_core.sarga.get_sarga")
    def test_night_of_brahma_rejection(self, mock_get_sarga):
        """Should REJECT creation tasks during Night of Brahma."""
        from vibe_core.sarga import Cycle

        mock_sarga = MagicMock()
        mock_sarga.get_cycle.return_value = Cycle.NIGHT_OF_BRAHMA
        mock_get_sarga.return_value = mock_sarga

        task = MockTask("feature_dev")
        with pytest.raises(ValueError) as excinfo:
            self.plugin.on_task_submit(self.kernel, task)
        assert "not allowed during NIGHT_OF_BRAHMA" in str(excinfo.value)

    @patch("vibe_core.sarga.get_sarga")
    def test_night_of_brahma_admission(self, mock_get_sarga):
        """Should ADMIT maintenance tasks during Night of Brahma."""
        from vibe_core.sarga import Cycle

        mock_sarga = MagicMock()
        mock_sarga.get_cycle.return_value = Cycle.NIGHT_OF_BRAHMA
        mock_get_sarga.return_value = mock_sarga

        task = MockTask("bugfix")
        assert self.plugin.on_task_submit(self.kernel, task) is True

    @patch("vibe_core.sarga.get_sarga")
    def test_day_of_brahma_admission(self, mock_get_sarga):
        """Should ADMIT all tasks during Day of Brahma."""
        from vibe_core.sarga import Cycle

        mock_sarga = MagicMock()
        mock_sarga.get_cycle.return_value = Cycle.DAY_OF_BRAHMA
        mock_get_sarga.return_value = mock_sarga

        task = MockTask("feature_dev")
        assert self.plugin.on_task_submit(self.kernel, task) is True
