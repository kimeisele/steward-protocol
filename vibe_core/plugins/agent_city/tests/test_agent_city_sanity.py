"""
Agent City Plugin - Sanity Tests
==================================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_agent_city_plugin_imports():
    """Verify AgentCityPlugin can be imported."""
    from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

    assert AgentCityPlugin is not None
    assert hasattr(AgentCityPlugin, "on_boot")
    assert hasattr(AgentCityPlugin, "plugin_id")


def test_agent_city_plugin_instantiation():
    """Verify AgentCityPlugin can be instantiated."""
    from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

    plugin = AgentCityPlugin()
    assert plugin.plugin_id == "agent_city"
