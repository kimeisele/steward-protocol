"""
TEST: Monitor Loader
====================
Tests for Glass Box system introspection using standardized fixtures.
"""

from vibe_core.cli.monitor_loader import MonitorLoader
from vibe_core.plugins.test_orchestration.fixtures import IsolatedTestContext


class TestMonitorLoader:
    """Test monitor discovery."""

    def teardown_method(self):
        MonitorLoader.clear_cache()

    def test_discover_monitors_no_plugins(self):
        """Should return empty registry if no plugins."""
        with IsolatedTestContext() as ctx:
            # ctx.kernel is minimal (no plugins)
            monitors = MonitorLoader.discover_monitors(ctx.kernel)
            assert len(monitors) == 0

    def test_discover_monitors_with_plugin(self):
        """Should discover monitors from plugin with proper structure."""
        with IsolatedTestContext() as ctx:
            # 1. Define a Mock Monitor with required attributes
            class MockMonitor:
                monitor_id = "test_monitor"
                monitor_type = "status"
                description = "Test monitor"

            # 2. Define Mock Plugin with get_monitors() method and plugin_id
            class MockPlugin:
                plugin_id = "mock_plugin"

                def get_monitors(self):
                    return [MockMonitor()]

            # 3. MonitorLoader iterates over kernel.plugins (expects list)
            # Note: plugins property is read-only, set _plugins directly in tests
            ctx.kernel._plugins = [MockPlugin()]

            # 4. Discover
            monitors = MonitorLoader.discover_monitors(ctx.kernel)

            # 5. Assert monitor was registered
            assert "test_monitor" in monitors

    def test_cache_behavior(self):
        """Should cache results."""
        with IsolatedTestContext() as ctx:
            MonitorLoader.clear_cache()

            # First call - should populate cache based on kernel plugins
            MonitorLoader.discover_monitors(ctx.kernel)
            assert MonitorLoader._cache is not None

            # Capture cache state
            initial_cache_id = id(MonitorLoader._cache)

            # Second call - should reuse same cache object ID or content
            MonitorLoader.discover_monitors(ctx.kernel)
            assert id(MonitorLoader._cache) == initial_cache_id
