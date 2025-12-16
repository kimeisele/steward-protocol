"""Tests for Task Manager Plugin."""

import pytest

from vibe_core.plugin_protocol import PulsePhase
from vibe_core.plugins.task_manager.plugin_main import TaskManagerPlugin


def test_task_manager_plugin_initialization():
    """Test that TaskManager plugin initializes correctly."""
    plugin = TaskManagerPlugin()
    assert plugin.plugin_id == "task_manager"
    assert plugin.pulse_phase == PulsePhase.SENSORS
    assert plugin.priority == 95


def test_task_manager_plugin_metadata():
    """Test plugin metadata is correct."""
    plugin = TaskManagerPlugin()
    assert hasattr(plugin, "on_pulse")
    assert callable(plugin.on_pulse)
