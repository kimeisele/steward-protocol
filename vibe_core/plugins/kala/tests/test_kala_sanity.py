"""
KALA Plugin Sanity Tests

Basic tests to verify the KALA (cosmic clock) plugin loads and functions.
"""

import pytest


def test_kala_plugin_imports():
    """Verify KALA plugin can be imported."""
    from vibe_core.plugins.kala.plugin_main import KalaPlugin

    assert KalaPlugin is not None


def test_cosmic_clock_imports():
    """Verify cosmic clock module can be imported."""
    from vibe_core.plugins.kala.cosmic_clock import CosmicClock

    assert CosmicClock is not None


def test_kala_plugin_instantiation():
    """Verify KALA plugin can be instantiated."""
    from vibe_core.plugins.kala.plugin_main import KalaPlugin

    plugin = KalaPlugin()
    assert plugin.plugin_id == "kala"
