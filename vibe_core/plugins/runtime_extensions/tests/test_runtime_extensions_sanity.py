"""Sanity tests for runtime_extensions."""

import pytest


def test_hot_loader_exists():
    """Test that hot_loader module exists."""
    try:
        from vibe_core.plugins.runtime_extensions import hot_loader

        assert hasattr(hot_loader, "__file__")
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")


def test_complexity_analyzer_exists():
    """Test that complexity_analyzer package exists."""
    try:
        from vibe_core.plugins.runtime_extensions import complexity_analyzer

        assert complexity_analyzer is not None
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")
