"""
Moltbook Plugin Tests
=====================

Tests the plugin lifecycle, state contract, and on_pulse() heartbeat.
All tests run offline — zero network calls.
"""

import pytest

from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
from vibe_core.plugin_protocol import PulsePhase
from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin


def _make_plugin_with_client(**kwargs) -> MoltbookPlugin:
    """Helper: create a plugin with an attached offline client."""
    plugin = MoltbookPlugin()
    plugin._client = MoltbookClient(api_key="test", offline_mode=True, **kwargs)
    plugin._offline_mode = True
    return plugin


# =============================================================================
# Boot & Config
# =============================================================================


def test_plugin_id():
    assert MoltbookPlugin.plugin_id == "moltbook"


def test_pulse_phase_is_sensors():
    plugin = MoltbookPlugin()
    assert plugin.pulse_phase == PulsePhase.SENSORS


def test_dependencies_include_economy():
    plugin = MoltbookPlugin()
    assert "economy" in plugin.dependencies


# =============================================================================
# PluginStateContract
# =============================================================================


def test_snapshot_without_client():
    plugin = MoltbookPlugin()
    snapshot = plugin.snapshot_state()
    assert snapshot["version"] == 1
    assert snapshot["client_active"] is False


def test_state_roundtrip():
    """Rate limits survive snapshot/restore through the REAL adapter state."""
    plugin = _make_plugin_with_client()
    plugin._client.limits.requests_this_minute = 85
    plugin._client.limits.posts_this_30m = 1
    plugin._client.limits.comments_today = 42

    snapshot = plugin.snapshot_state()
    assert snapshot["client_active"] is True
    assert snapshot["requests_this_minute"] == 85

    # Recover into a new instance
    recovered = _make_plugin_with_client()
    assert recovered._client.limits.requests_this_minute == 0

    recovered.restore_state(snapshot)
    assert recovered._client.limits.requests_this_minute == 85
    assert recovered._client.limits.posts_this_30m == 1
    assert recovered._client.limits.comments_today == 42


def test_restore_ignores_wrong_version():
    plugin = _make_plugin_with_client()
    plugin.restore_state({"version": 99, "client_active": True})
    assert plugin._client.limits.requests_this_minute == 0


# =============================================================================
# on_pulse (Heartbeat)
# =============================================================================


def test_on_pulse_without_client_returns_error():
    plugin = MoltbookPlugin()
    result = plugin.on_pulse(kernel=None, transaction=None)
    assert result.error_message == "Client not initialized"


def test_on_pulse_heartbeat_ok():
    """on_pulse() calls sync_check_heartbeat and returns heartbeat data."""
    plugin = _make_plugin_with_client()
    result = plugin.on_pulse(kernel=None, transaction=None)
    assert result.data["heartbeat"] == "ok"
    assert result.data["has_new_messages"] is False
    assert result.data["offline"] is True
    assert plugin._last_heartbeat_error is None


def test_on_pulse_clears_previous_error():
    """A successful heartbeat clears any previous error."""
    plugin = _make_plugin_with_client()
    plugin._last_heartbeat_error = "previous failure"
    plugin.on_pulse(kernel=None, transaction=None)
    assert plugin._last_heartbeat_error is None


# =============================================================================
# API
# =============================================================================


def test_get_api_exposes_client():
    plugin = _make_plugin_with_client()
    api = plugin.get_api()
    assert api["client"] is plugin._client
    assert api["offline"] is True
    assert api["last_error"] is None


def test_get_api_without_boot():
    plugin = MoltbookPlugin()
    api = plugin.get_api()
    assert api["client"] is None
