"""
TEST MOLTBOOK PLUGIN
====================

Verifies the biological membrane architecture (OPUS-210 PluginStateContract logic).
Ensures Moltbook rate limits survive reboots via the adapter's REAL RateLimitState,
not shadow copies.
"""

import pytest
from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
from vibe_core.mahamantra.adapters.moltbook import MoltbookClient


def test_moltbook_plugin_boot_offline():
    """Verify plugin boots correctly in offline mode."""
    plugin = MoltbookPlugin()
    
    paths = plugin.get_state_paths()
    assert len(paths) == 1
    assert "moltbook" in str(paths[0])


def test_moltbook_plugin_state_contract_no_client():
    """Snapshot without a client returns a safe fallback."""
    plugin = MoltbookPlugin()
    snapshot = plugin.snapshot_state()
    assert snapshot["version"] == 1
    assert snapshot["client_active"] is False


def test_moltbook_plugin_state_roundtrip():
    """
    Verify rate limits survive snapshot/restore through the REAL adapter state.
    No shadow copies. The Plugin reads/writes the adapter's RateLimitState directly.
    """
    plugin = MoltbookPlugin()
    # Simulate boot by manually attaching a client
    plugin._client = MoltbookClient(api_key="test", offline_mode=True)
    
    # 1. Simulate usage
    plugin._client.limits.requests_this_minute = 85
    plugin._client.limits.posts_this_30m = 1
    plugin._client.limits.comments_today = 42
    
    # 2. Snapshot (crash)
    snapshot = plugin.snapshot_state()
    assert snapshot["client_active"] is True
    assert snapshot["requests_this_minute"] == 85
    assert snapshot["posts_this_30m"] == 1
    assert snapshot["comments_today"] == 42
    
    # 3. New plugin instance (recovery)
    recovered = MoltbookPlugin()
    recovered._client = MoltbookClient(api_key="test", offline_mode=True)
    
    # Before restore
    assert recovered._client.limits.requests_this_minute == 0
    
    # 4. Restore
    recovered.restore_state(snapshot)
    
    # 5. Verify the ADAPTER's real state was restored
    assert recovered._client.limits.requests_this_minute == 85
    assert recovered._client.limits.posts_this_30m == 1
    assert recovered._client.limits.comments_today == 42
    
    print("✅ Plugin state roundtrip through REAL adapter state verified.")
