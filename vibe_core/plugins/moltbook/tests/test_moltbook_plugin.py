"""
Moltbook Plugin Tests
=====================

Tests the Mahamantra-native heartbeat path (register_listener),
plugin lifecycle, and state contract. All tests run offline.
"""

import pytest

from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
from vibe_core.plugin_protocol import PulsePhase
from vibe_core.plugins.moltbook.plugin_main import _TICKS_PER_HEARTBEAT, MoltbookPlugin


def _make_plugin_with_client(**kwargs) -> MoltbookPlugin:
    """Helper: create a plugin with an attached offline client."""
    plugin = MoltbookPlugin()
    plugin._client = MoltbookClient(api_key="test", offline_mode=True, **kwargs)
    plugin._offline_mode = True
    return plugin


# =============================================================================
# Identity
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
# Mahamantra Listener — THE heartbeat path
# =============================================================================


def test_listener_fires_heartbeat_every_16_ticks():
    """_on_mahamantra_tick polls Moltbook once per full mantra (16 ticks)."""
    plugin = _make_plugin_with_client()
    initial_requests = plugin._client.limits.requests_this_minute

    # 15 ticks: no heartbeat
    for i in range(15):
        plugin._on_mahamantra_tick({})
    assert plugin._client.limits.requests_this_minute == initial_requests

    # 16th tick: heartbeat fires
    plugin._on_mahamantra_tick({})
    assert plugin._client.limits.requests_this_minute == initial_requests + 1
    assert plugin._last_heartbeat_error is None


def test_listener_skips_without_client():
    """No crash if tick fires before client is ready. Early return, no tick counted."""
    plugin = MoltbookPlugin()
    plugin._on_mahamantra_tick({})  # Should not raise
    assert plugin._tick_count == 0  # Early return — no client, no tick


def test_listener_accumulates_ticks():
    """Tick counter increments on every call."""
    plugin = _make_plugin_with_client()
    for _ in range(5):
        plugin._on_mahamantra_tick({})
    assert plugin._tick_count == 5


def test_heartbeat_error_is_captured():
    """Failed heartbeat sets _last_heartbeat_error."""
    plugin = _make_plugin_with_client()
    plugin._client.limits.requests_this_minute = 100  # Will trigger rate limit

    # Need to reach tick 16 to trigger heartbeat
    for i in range(_TICKS_PER_HEARTBEAT):
        plugin._on_mahamantra_tick({})

    assert plugin._last_heartbeat_error is not None
    assert "rate limit" in plugin._last_heartbeat_error.lower()


def test_multiple_heartbeat_cycles():
    """Multiple full mantra cycles each trigger one heartbeat."""
    plugin = _make_plugin_with_client()

    for i in range(_TICKS_PER_HEARTBEAT * 3):
        plugin._on_mahamantra_tick({})

    assert plugin._tick_count == _TICKS_PER_HEARTBEAT * 3
    assert plugin._client.limits.requests_this_minute == 3


# =============================================================================
# on_pulse (backward compat)
# =============================================================================


def test_on_pulse_without_client_returns_error():
    plugin = MoltbookPlugin()
    result = plugin.on_pulse(kernel=None, transaction=None)
    assert result.error_message == "Client not initialized"


def test_on_pulse_delegates_to_heartbeat():
    """on_pulse() runs the same heartbeat logic."""
    plugin = _make_plugin_with_client()
    result = plugin.on_pulse(kernel=None, transaction=None)
    assert result.data["heartbeat"] == "ok"
    assert result.data["offline"] is True


def test_on_pulse_reports_listener_status():
    """on_pulse() reports whether Mahamantra listener is wired."""
    plugin = _make_plugin_with_client()
    result = plugin.on_pulse(kernel=None, transaction=None)
    assert "listener_wired" in result.data
    assert "ticks_seen" in result.data


# =============================================================================
# API
# =============================================================================


def test_get_api_exposes_client_and_listener_status():
    plugin = _make_plugin_with_client()
    api = plugin.get_api()
    assert api["client"] is plugin._client
    assert api["offline"] is True
    assert api["last_error"] is None
    assert api["listener_wired"] is False  # Not wired in test
    assert api["ticks_seen"] == 0


def test_get_api_without_boot():
    plugin = MoltbookPlugin()
    api = plugin.get_api()
    assert api["client"] is None
