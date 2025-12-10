"""
Vedic Governance Plugin - Sanity Tests
=======================================
Minimal test for container packaging compliance (OPUS-020).
"""


def test_vedic_governance_plugin_imports():
    """Verify VedicGovernancePlugin can be imported."""
    from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

    assert VedicGovernancePlugin is not None
    assert hasattr(VedicGovernancePlugin, "on_boot")
    assert hasattr(VedicGovernancePlugin, "plugin_id")


def test_vedic_governance_plugin_instantiation():
    """Verify VedicGovernancePlugin can be instantiated."""
    from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin

    plugin = VedicGovernancePlugin()
    assert plugin.plugin_id == "vedic_governance"
