"""
TEST MOLTBOOK PLUGIN
====================

Verifies the biological membrane architecture (OPUS-210 PluginStateContract logic).
Ensures Moltbook rate limits survive reboots and the plugin correctly exposes
its status without crashing the Kernel.
"""

import pytest
from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

def test_moltbook_plugin_boot_offline():
    """Verify plugin boots correctly in offline mode."""
    plugin = MoltbookPlugin()
    
    # In a pure unit test without real Kernel injection, we can test state
    paths = plugin.get_state_paths()
    assert len(paths) == 1
    assert "moltbook" in str(paths[0])

def test_moltbook_plugin_state_contract():
    """Verify rate limits are preserved across snapshots (starvation memory)."""
    plugin = MoltbookPlugin()
    
    # 1. Simulate active rate limits
    plugin._requests_this_minute = 85
    plugin._posts_this_30m = 1
    plugin._comments_today = 42
    plugin._last_minute_reset = 1000.0
    plugin._last_post_time = 2000.0
    plugin._last_day_reset = 3000.0
    
    # 2. Snapshot (System crash/reboot)
    snapshot = plugin.snapshot_state()
    
    # 3. New plugin instance (Recovery)
    recovered_plugin = MoltbookPlugin()
    
    # Before recovery, should be 0
    assert recovered_plugin._requests_this_minute == 0
    assert recovered_plugin._posts_this_30m == 0
    
    # 4. Restore
    recovered_plugin.restore_state(snapshot)
    
    # 5. Verify biological memory intact
    assert recovered_plugin._requests_this_minute == 85
    assert recovered_plugin._posts_this_30m == 1
    assert recovered_plugin._comments_today == 42
    assert recovered_plugin._last_minute_reset == 1000.0
    assert recovered_plugin._last_post_time == 2000.0
    assert recovered_plugin._last_day_reset == 3000.0
    
    print("✅ Moltbook Biostate correctly preserved across snapshots.")
