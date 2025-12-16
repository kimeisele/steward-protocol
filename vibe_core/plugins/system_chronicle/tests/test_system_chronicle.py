"""Tests for System Chronicle Plugin."""

import pytest

from vibe_core.plugin_protocol import PulsePhase
from vibe_core.plugins.system_chronicle.plugin_main import SystemChroniclePlugin


def test_system_chronicle_plugin_initialization():
    """Test that SystemChronicle plugin initializes correctly."""
    plugin = SystemChroniclePlugin()
    assert plugin.plugin_id == "system_chronicle"
    assert plugin.pulse_phase == PulsePhase.CLEANUP
    assert plugin.priority == 100


def test_system_chronicle_plugin_metadata():
    """Test plugin metadata is correct."""
    plugin = SystemChroniclePlugin()
    assert hasattr(plugin, "on_pulse")
    assert callable(plugin.on_pulse)
