"""NodePulse Plugin Sanity Tests"""


def test_node_pulse_plugin_imports():
    """Verify NodePulse plugin can be imported."""
    from vibe_core.plugins.node_pulse.plugin_main import NodePulsePlugin

    assert NodePulsePlugin is not None


def test_node_pulse_plugin_instantiation():
    """Verify NodePulse plugin can be instantiated."""
    from vibe_core.plugins.node_pulse.plugin_main import NodePulsePlugin

    plugin = NodePulsePlugin()
    assert plugin.plugin_id == "node_pulse"
