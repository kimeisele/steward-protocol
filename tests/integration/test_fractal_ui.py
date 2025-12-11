"""
OPUS-023: Fractal UI Integration Tests

Tests for visible ephemeral cities in parent dashboard.
Per conftest.py: Uses test_context fixture.

Test Cases:
1. EphemeralRenderer shows active child kernels
2. EphemeralRenderer shows no cities when empty
3. EphemeralRenderer updates after merge
"""

import pytest

from vibe_core.phoenix.config import get_config
from vibe_core.plugins.interface.renderers.ephemeral import EphemeralRenderer

# ===========================================================================
# TEST: Active cities are visible
# ===========================================================================


def test_ephemeral_renderer_shows_no_cities_initially(fresh_kernel):
    """
    EphemeralRenderer should show 'No active cities' when no children spawned.
    """
    kernel = fresh_kernel
    kernel.boot()

    # Create renderer
    renderer = EphemeralRenderer(kernel)
    content = renderer.generate_content()

    # Should show no active cities
    assert "## Active Cities" in content
    assert "_No active cities_" in content

    # Cleanup
    kernel.shutdown()


def test_ephemeral_renderer_shows_active_city(fresh_kernel):
    """
    EphemeralRenderer should show active child kernels.

    OPUS-023: Fractal UI Architecture - Visible Ephemeral Cities.
    """
    kernel = fresh_kernel
    kernel.boot()

    # Spawn child
    config = get_config()
    child = kernel.spawn_child_kernel(config)

    # Create renderer
    renderer = EphemeralRenderer(kernel)
    content = renderer.generate_content()

    # Should show the child (not "no active cities")
    assert "## Active Cities" in content
    assert "_No active cities_" not in content

    # Should show status column
    assert "INIT" in content or "RUNNING" in content

    # Cleanup
    child.shutdown()
    kernel.shutdown()


def test_ephemeral_renderer_shows_multiple_cities(fresh_kernel):
    """
    EphemeralRenderer should show multiple child kernels.
    """
    kernel = fresh_kernel
    kernel.boot()

    config = get_config()
    child1 = kernel.spawn_child_kernel(config)
    child2 = kernel.spawn_child_kernel(config)

    # Create renderer
    renderer = EphemeralRenderer(kernel)
    content = renderer.generate_content()

    # Should show both children
    assert "## Active Cities" in content
    assert "_No active cities_" not in content

    # Count table rows (excluding header)
    lines = content.split("\n")
    table_rows = [l for l in lines if l.startswith("|") and "City ID" not in l and ":---" not in l]
    assert len(table_rows) >= 2, "Should have at least 2 city rows"

    # Cleanup
    child1.shutdown()
    child2.shutdown()
    kernel.shutdown()


def test_ephemeral_renderer_records_merge(fresh_kernel):
    """
    EphemeralRenderer should record merge events.
    """
    kernel = fresh_kernel
    kernel.boot()

    # Create renderer
    renderer = EphemeralRenderer(kernel)

    # Record a merge
    renderer.record_merge(
        {
            "child_id": 12345678,
            "result": "Task completed successfully",
        }
    )

    content = renderer.generate_content()

    # Should show merge in history
    assert "## Merge History" in content
    assert "_No merges recorded_" not in content
    assert "12345678" in content

    # Cleanup
    kernel.shutdown()


def test_ephemeral_renderer_city_becomes_invisible_after_merge(fresh_kernel):
    """
    After merge, child kernel should no longer appear in Active Cities.
    """
    kernel = fresh_kernel
    kernel.boot()

    config = get_config()
    child = kernel.spawn_child_kernel(config)
    child.boot()

    # Create renderer and check child is visible
    renderer = EphemeralRenderer(kernel)
    content_before = renderer.generate_content()
    assert "_No active cities_" not in content_before

    # Merge the child
    result = {"output": "done"}
    kernel.merge_child_result(child, result)

    # Record the merge
    renderer.record_merge({"child_id": id(child), "result": "done"})

    # Check content again
    content_after = renderer.generate_content()

    # Child should be gone from active cities
    assert "_No active cities_" in content_after

    # But merge should be in history
    assert "_No merges recorded_" not in content_after

    # Cleanup
    kernel.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
