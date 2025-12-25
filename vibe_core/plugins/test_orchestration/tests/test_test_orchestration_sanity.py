"""
Test Orchestration Plugin - Sanity Tests
=========================================
Minimal test for container packaging compliance (OPUS-020).
"""


def test_test_orchestration_plugin_imports():
    """Verify OrchestrationPlugin can be imported."""
    from vibe_core.plugins.test_orchestration.plugin_main import OrchestrationPlugin

    assert OrchestrationPlugin is not None
    assert hasattr(OrchestrationPlugin, "on_boot")
    assert hasattr(OrchestrationPlugin, "plugin_id")


def test_fixtures_available():
    """Verify test fixtures can be imported."""
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents, TestKernel

    assert TestAgents is not None
    assert TestKernel is not None
