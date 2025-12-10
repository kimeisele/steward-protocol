"""
Steward Protocol Plugin - Sanity Tests
=======================================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_steward_protocol_plugin_imports():
    """Verify StewardProtocolPlugin can be imported."""
    from vibe_core.plugins.steward_protocol.plugin_main import StewardProtocolPlugin

    assert StewardProtocolPlugin is not None
    assert hasattr(StewardProtocolPlugin, "on_boot")
    assert hasattr(StewardProtocolPlugin, "plugin_id")


def test_steward_protocol_plugin_instantiation():
    """Verify StewardProtocolPlugin can be instantiated."""
    from vibe_core.plugins.steward_protocol.plugin_main import StewardProtocolPlugin

    plugin = StewardProtocolPlugin()
    assert plugin.plugin_id == "steward_protocol"


def test_oath_verification_available():
    """Verify oath verification methods exist."""
    from vibe_core.plugins.steward_protocol.plugin_main import StewardProtocolPlugin

    plugin = StewardProtocolPlugin()
    assert hasattr(plugin, "on_agent_pre_register")
