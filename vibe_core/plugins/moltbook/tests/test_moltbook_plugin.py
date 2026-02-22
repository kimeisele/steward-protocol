"""
Moltbook Plugin Tests — Fortress-Level Verification
=====================================================

Tests the plugin membrane, MoltbookService protocol implementation,
Guna enforcement, Mahamantra listener wiring, state contracts,
and ServiceRegistry integration.

Organization (by concern):
    TestPluginIdentity           — plugin_id, phase, dependencies, KernelPlugin contract
    TestPluginStateContract      — snapshot/restore roundtrip, version guard, field completeness
    TestMahamantraListener       — THE heartbeat path: tick counting, modular fire, error capture
    TestOnPulseBackwardCompat    — on_pulse() delegates to same heartbeat, reports status
    TestPluginAPI                — get_api() shape, pre-boot safety
    TestMoltbookProtocolContract — ABC compliance, method signatures, isinstance
    TestMoltbookServiceSattva    — Read-only operations: no side effects, no log entries
    TestMoltbookServiceRajas     — Write operations: logged with guna + timestamp
    TestMoltbookServiceTamas     — Destructive operations: blocked with PermissionError
    TestGunaMapCompleteness      — Every protocol method classified, no orphans
    TestServiceRegistryWiring    — register_factory, DI retrieval, isolation
    TestParashuramaWhitelist     — moltbook.com in network proxy whitelist
"""

import time
from abc import abstractmethod

import pytest

from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.plugins.moltbook.plugin_main import (
    _TICKS_PER_HEARTBEAT,
    MoltbookPlugin,
    MoltbookService,
)
from vibe_core.protocols.moltbook import (
    MOLTBOOK_GUNA_MAP,
    MoltbookGuna,
    MoltbookProtocol,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def plugin():
    """Fresh plugin with offline client — complete state isolation."""
    p = MoltbookPlugin()
    p._client = MoltbookClient(api_key="test", offline_mode=True)
    p._offline_mode = True
    return p


@pytest.fixture
def bare_plugin():
    """Plugin without client — pre-boot state."""
    return MoltbookPlugin()


@pytest.fixture
def service():
    """Fresh MoltbookService with offline client."""
    client = MoltbookClient(api_key="test", offline_mode=True)
    return MoltbookService(client)


@pytest.fixture
def client():
    """Standalone offline client for service tests."""
    return MoltbookClient(api_key="test", offline_mode=True)


# =============================================================================
# PLUGIN IDENTITY — KernelPlugin contract
# =============================================================================


class TestPluginIdentity:
    """MoltbookPlugin satisfies the KernelPlugin contract."""

    def test_plugin_id_is_moltbook(self):
        assert MoltbookPlugin.plugin_id == "moltbook"

    def test_inherits_kernel_plugin(self):
        """Must be a proper KernelPlugin subclass."""
        assert issubclass(MoltbookPlugin, KernelPlugin)

    def test_instance_is_kernel_plugin(self, bare_plugin):
        assert isinstance(bare_plugin, KernelPlugin)

    def test_pulse_phase_is_sensors(self, bare_plugin):
        """Moltbook is a SENSOR — collects data before cognition."""
        assert bare_plugin.pulse_phase == PulsePhase.SENSORS

    def test_dependencies_include_economy(self, bare_plugin):
        """Moltbook depends on economy plugin (CivicVault for API key)."""
        assert "economy" in bare_plugin.dependencies

    def test_dependencies_is_set(self, bare_plugin):
        """Dependencies must be a set, not list."""
        assert isinstance(bare_plugin.dependencies, set)

    def test_naga_blessed(self, bare_plugin):
        """All KernelPlugin subclasses are NAGA-blessed via base class."""
        assert getattr(bare_plugin, "_naga_flooded", False) is True

    def test_ticks_per_heartbeat_is_16(self):
        """One full mantra = 16 ticks = 1 chant cycle. SSOT constant."""
        assert _TICKS_PER_HEARTBEAT == 16


# =============================================================================
# PLUGIN STATE CONTRACT — snapshot/restore
# =============================================================================


class TestPluginStateContract:
    """State persistence survives kernel restarts via snapshot/restore."""

    def test_snapshot_without_client(self, bare_plugin):
        """Pre-boot plugin returns minimal snapshot."""
        snapshot = bare_plugin.snapshot_state()
        assert snapshot["version"] == 1
        assert snapshot["client_active"] is False

    def test_snapshot_with_client(self, plugin):
        """Active plugin includes all rate limit fields."""
        snapshot = plugin.snapshot_state()
        assert snapshot["version"] == 1
        assert snapshot["client_active"] is True
        assert "requests_this_minute" in snapshot
        assert "posts_this_30m" in snapshot
        assert "comments_this_hour" in snapshot
        assert "last_minute_reset" in snapshot
        assert "last_30m_reset" in snapshot
        assert "last_hour_reset" in snapshot
        assert "timestamp" in snapshot

    def test_snapshot_captures_current_limits(self, plugin):
        """Snapshot reflects actual rate limit state."""
        plugin._client.limits.requests_this_minute = 85
        plugin._client.limits.posts_this_30m = 1
        plugin._client.limits.comments_this_hour = 42

        snapshot = plugin.snapshot_state()
        assert snapshot["requests_this_minute"] == 85
        assert snapshot["posts_this_30m"] == 1
        assert snapshot["comments_this_hour"] == 42

    def test_full_roundtrip(self, plugin):
        """Rate limits survive snapshot → new plugin → restore."""
        plugin._client.limits.requests_this_minute = 85
        plugin._client.limits.posts_this_30m = 1
        plugin._client.limits.comments_this_hour = 42

        snapshot = plugin.snapshot_state()

        recovered = MoltbookPlugin()
        recovered._client = MoltbookClient(api_key="test", offline_mode=True)
        assert recovered._client.limits.requests_this_minute == 0

        recovered.restore_state(snapshot)
        assert recovered._client.limits.requests_this_minute == 85
        assert recovered._client.limits.posts_this_30m == 1
        assert recovered._client.limits.comments_this_hour == 42

    def test_restore_ignores_wrong_version(self, plugin):
        """Version guard: unknown snapshot versions are silently skipped."""
        plugin.restore_state({"version": 99, "client_active": True})
        assert plugin._client.limits.requests_this_minute == 0

    def test_restore_ignores_inactive_client(self, plugin):
        """Inactive snapshot does not overwrite active state."""
        plugin._client.limits.requests_this_minute = 10
        plugin.restore_state({"version": 1, "client_active": False})
        assert plugin._client.limits.requests_this_minute == 10

    def test_restore_without_client_is_noop(self, bare_plugin):
        """Restore on pre-boot plugin (no client) does not crash."""
        bare_plugin.restore_state({"version": 1, "client_active": True, "requests_this_minute": 50})
        # No client → noop, no crash

    def test_restore_handles_missing_fields(self, plugin):
        """Missing fields default to zero, not crash."""
        plugin.restore_state({"version": 1, "client_active": True})
        assert plugin._client.limits.requests_this_minute == 0
        assert plugin._client.limits.posts_this_30m == 0


# =============================================================================
# MAHAMANTRA LISTENER — THE heartbeat path
# =============================================================================


class TestMahamantraListener:
    """The Mahamantra tick listener is the REAL heartbeat path.
    Same pattern as Nrisimha._on_mahamantra_tick()."""

    def test_tick_increments_counter(self, plugin):
        """Every tick increments the counter."""
        for _ in range(5):
            plugin._on_mahamantra_tick({})
        assert plugin._tick_count == 5

    def test_no_heartbeat_before_16_ticks(self, plugin):
        """First 15 ticks: tick counter increments, no heartbeat fires."""
        initial_requests = plugin._client.limits.requests_this_minute
        for _ in range(15):
            plugin._on_mahamantra_tick({})
        assert plugin._client.limits.requests_this_minute == initial_requests

    def test_heartbeat_fires_at_tick_16(self, plugin):
        """16th tick triggers heartbeat (one API request)."""
        initial_requests = plugin._client.limits.requests_this_minute
        for _ in range(16):
            plugin._on_mahamantra_tick({})
        assert plugin._client.limits.requests_this_minute == initial_requests + 1
        assert plugin._last_heartbeat_error is None

    def test_heartbeat_fires_every_16_ticks(self, plugin):
        """Multiple full mantra cycles each trigger exactly one heartbeat."""
        for _ in range(_TICKS_PER_HEARTBEAT * 3):
            plugin._on_mahamantra_tick({})
        assert plugin._tick_count == _TICKS_PER_HEARTBEAT * 3
        assert plugin._client.limits.requests_this_minute == 3

    def test_heartbeat_at_exact_multiples(self, plugin):
        """Heartbeat fires at tick 16, 32, 48 — exactly at multiples."""
        for i in range(1, 49):
            plugin._on_mahamantra_tick({})
            expected = i // _TICKS_PER_HEARTBEAT
            assert plugin._client.limits.requests_this_minute == expected, (
                f"At tick {i}, expected {expected} heartbeats"
            )

    def test_skips_without_client(self, bare_plugin):
        """No crash if tick fires before client is ready. No tick counted."""
        bare_plugin._on_mahamantra_tick({})
        assert bare_plugin._tick_count == 0

    def test_error_captured_not_raised(self, plugin):
        """Failed heartbeat sets error string, does not raise."""
        plugin._client.limits.requests_this_minute = 100  # Will trigger rate limit
        for _ in range(_TICKS_PER_HEARTBEAT):
            plugin._on_mahamantra_tick({})
        assert plugin._last_heartbeat_error is not None
        assert "rate limit" in plugin._last_heartbeat_error.lower()

    def test_error_clears_on_success(self, plugin):
        """Successful heartbeat clears previous error."""
        plugin._last_heartbeat_error = "previous error"
        for _ in range(_TICKS_PER_HEARTBEAT):
            plugin._on_mahamantra_tick({})
        assert plugin._last_heartbeat_error is None

    def test_listener_wired_flag_default_false(self, bare_plugin):
        """_listener_wired is False until _wire_to_mahamantra() succeeds."""
        assert bare_plugin._listener_wired is False


# =============================================================================
# ON_PULSE — Backward compatibility
# =============================================================================


class TestOnPulseBackwardCompat:
    """on_pulse() delegates to same heartbeat logic. Kept for split-brain compat."""

    def test_without_client_returns_error(self, bare_plugin):
        result = bare_plugin.on_pulse(kernel=None, transaction=None)
        assert isinstance(result, HookResult)
        assert result.error_message == "Client not initialized"

    def test_delegates_to_heartbeat(self, plugin):
        result = plugin.on_pulse(kernel=None, transaction=None)
        assert result.data["heartbeat"] == "ok"
        assert result.data["offline"] is True

    def test_reports_listener_status(self, plugin):
        result = plugin.on_pulse(kernel=None, transaction=None)
        assert "listener_wired" in result.data
        assert "ticks_seen" in result.data

    def test_reports_error_after_failure(self, plugin):
        """on_pulse after heartbeat failure includes error in data."""
        plugin._client.limits.requests_this_minute = 100
        result = plugin.on_pulse(kernel=None, transaction=None)
        assert result.data["heartbeat"] == "failed"
        assert result.data["error"] is not None

    def test_returns_hook_result(self, plugin):
        """on_pulse always returns HookResult, never raises."""
        result = plugin.on_pulse(kernel=None, transaction=None)
        assert isinstance(result, HookResult)


# =============================================================================
# PLUGIN API — kernel.api("moltbook")
# =============================================================================


class TestPluginAPI:
    """get_api() exposes controlled surface to other plugins."""

    def test_api_shape(self, plugin):
        """API dict has exactly the expected keys."""
        api = plugin.get_api()
        expected_keys = {"client", "offline", "last_error", "listener_wired", "ticks_seen"}
        assert set(api.keys()) == expected_keys

    def test_api_client_reference(self, plugin):
        """API exposes the same client instance (identity, not copy)."""
        api = plugin.get_api()
        assert api["client"] is plugin._client

    def test_api_offline_flag(self, plugin):
        api = plugin.get_api()
        assert api["offline"] is True

    def test_api_initial_error_is_none(self, plugin):
        api = plugin.get_api()
        assert api["last_error"] is None

    def test_api_listener_not_wired_in_test(self, plugin):
        """Listener is not wired in unit tests (no Mahamantra engine)."""
        api = plugin.get_api()
        assert api["listener_wired"] is False

    def test_api_ticks_count(self, plugin):
        """Tick count reflects actual ticks processed."""
        for _ in range(5):
            plugin._on_mahamantra_tick({})
        api = plugin.get_api()
        assert api["ticks_seen"] == 5

    def test_api_without_boot(self, bare_plugin):
        """Pre-boot plugin returns None client."""
        api = bare_plugin.get_api()
        assert api["client"] is None


# =============================================================================
# MOLTBOOK PROTOCOL CONTRACT — ABC compliance
# =============================================================================


class TestMoltbookProtocolContract:
    """MoltbookProtocol ABC defines the service interface correctly."""

    def test_is_abstract_class(self):
        """MoltbookProtocol cannot be instantiated directly."""
        with pytest.raises(TypeError):
            MoltbookProtocol()

    def test_has_all_abstract_methods(self):
        """All 9 methods are abstract."""
        expected = {
            "check_heartbeat",
            "create_post",
            "comment",
            "search",
            "get_profile",
            "send_dm",
            "get_conversations",
            "get_messages",
            "verify_credentials",
        }
        actual = set(MoltbookProtocol.__abstractmethods__)
        assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"

    def test_service_is_subclass(self):
        """MoltbookService is a proper subclass of MoltbookProtocol."""
        assert issubclass(MoltbookService, MoltbookProtocol)

    def test_service_isinstance(self, service):
        """MoltbookService instance passes isinstance check."""
        assert isinstance(service, MoltbookProtocol)

    def test_method_count_matches(self):
        """Service implements exactly the methods defined by protocol."""
        abstract_count = len(MoltbookProtocol.__abstractmethods__)
        assert abstract_count == 9


# =============================================================================
# MOLTBOOK SERVICE — SATTVA operations (read-only, no side effects)
# =============================================================================


class TestMoltbookServiceSattva:
    """SATTVA operations: read-only, no operation log entries, no state mutation."""

    def test_check_heartbeat(self, service):
        result = service.check_heartbeat()
        assert "has_new_messages" in result
        assert "pending_requests" in result

    def test_search_returns_list(self, service):
        results = service.search("agent operating system")
        assert isinstance(results, list)

    def test_verify_credentials_offline(self, service):
        """Offline mode returns 'claimed' → verify_credentials returns True."""
        assert service.verify_credentials() is True

    def test_get_conversations(self, client):
        client._mock_db["conversations"] = [{"id": "conv1"}]
        svc = MoltbookService(client)
        convs = svc.get_conversations()
        assert len(convs) == 1
        assert convs[0]["id"] == "conv1"

    def test_get_messages(self, client):
        client._mock_db["dms"] = [
            {"conversation_id": "c1", "sender": "A", "content": "Hello"},
        ]
        svc = MoltbookService(client)
        msgs = svc.get_messages("c1")
        assert len(msgs) == 1

    def test_sattva_operations_produce_no_log(self, service):
        """ALL sattva operations must produce zero log entries."""
        service.check_heartbeat()
        service.search("test")
        service.verify_credentials()
        assert len(service._operation_log) == 0, "SATTVA operations must not log — they are read-only"


# =============================================================================
# MOLTBOOK SERVICE — RAJAS operations (write, logged)
# =============================================================================


class TestMoltbookServiceRajas:
    """RAJAS operations: write, each logged with operation name + guna + timestamp."""

    def test_create_post(self, service):
        post = service.create_post("Title", "Content")
        assert post["id"] == "p0"
        assert post["title"] == "Title"

    def test_create_post_logged(self, service):
        service.create_post("Title", "Content")
        assert len(service._operation_log) == 1
        entry = service._operation_log[0]
        assert entry["operation"] == "create_post"
        assert entry["guna"] == "rajas"
        assert "timestamp" in entry

    def test_comment(self, service):
        comment = service.comment("post_123", "Interesting!")
        assert comment["id"] == "c99"

    def test_comment_logged(self, service):
        service.comment("p1", "hello")
        assert len(service._operation_log) == 1
        assert service._operation_log[0]["operation"] == "comment"
        assert service._operation_log[0]["guna"] == "rajas"

    def test_send_dm(self, service):
        result = service.send_dm("conv1", "hello")
        assert isinstance(result, dict)

    def test_send_dm_logged(self, service):
        service.send_dm("conv1", "hello")
        assert len(service._operation_log) == 1
        assert service._operation_log[0]["operation"] == "send_dm"

    def test_multiple_rajas_accumulate(self, service):
        """Each RAJAS operation adds one log entry."""
        service.create_post("A", "a")
        service.comment("p1", "b")
        service.send_dm("c1", "c")
        assert len(service._operation_log) == 3

    def test_log_timestamp_is_recent(self, service):
        """Timestamp must be a recent epoch float."""
        before = time.time()
        service.create_post("Title", "Content")
        after = time.time()
        ts = service._operation_log[0]["timestamp"]
        assert before <= ts <= after


# =============================================================================
# MOLTBOOK SERVICE — TAMAS operations (destructive, blocked)
# =============================================================================


class TestMoltbookServiceTamas:
    """TAMAS operations: destructive, blocked with PermissionError."""

    def test_delete_post_blocked(self, service):
        with pytest.raises(PermissionError, match="MOLTBOOK-TAMAS"):
            service._enforce_guna("delete_post")

    def test_unfollow_blocked(self, service):
        with pytest.raises(PermissionError, match="MOLTBOOK-TAMAS"):
            service._enforce_guna("unfollow")

    def test_unsubscribe_blocked(self, service):
        with pytest.raises(PermissionError, match="MOLTBOOK-TAMAS"):
            service._enforce_guna("unsubscribe")

    def test_tamas_produces_no_log(self, service):
        """Blocked TAMAS operations must NOT produce log entries."""
        try:
            service._enforce_guna("delete_post")
        except PermissionError:
            pass
        assert len(service._operation_log) == 0

    def test_unknown_operation_defaults_to_sattva(self, service):
        """Unknown operations default to SATTVA (safe pass-through)."""
        service._enforce_guna("unknown_operation")
        assert len(service._operation_log) == 0


# =============================================================================
# GUNA MAP COMPLETENESS — Every protocol method classified
# =============================================================================


class TestGunaMapCompleteness:
    """MOLTBOOK_GUNA_MAP is complete and consistent."""

    def test_all_protocol_methods_classified(self):
        """Every abstract method in MoltbookProtocol has a Guna classification."""
        for method in MoltbookProtocol.__abstractmethods__:
            assert method in MOLTBOOK_GUNA_MAP, f"MoltbookProtocol.{method} missing from MOLTBOOK_GUNA_MAP"

    def test_sattva_operations(self):
        """Read-only operations are classified as SATTVA."""
        sattva_ops = {
            "check_heartbeat",
            "search",
            "get_profile",
            "get_conversations",
            "get_messages",
            "verify_credentials",
        }
        for op in sattva_ops:
            assert MOLTBOOK_GUNA_MAP[op] == MoltbookGuna.SATTVA, f"{op} should be SATTVA (read-only)"

    def test_rajas_operations(self):
        """Write operations are classified as RAJAS."""
        rajas_ops = {"create_post", "comment", "send_dm"}
        for op in rajas_ops:
            assert MOLTBOOK_GUNA_MAP[op] == MoltbookGuna.RAJAS, f"{op} should be RAJAS (write)"

    def test_tamas_operations(self):
        """Destructive operations are classified as TAMAS."""
        tamas_ops = {"delete_post", "unfollow", "unsubscribe"}
        for op in tamas_ops:
            assert MOLTBOOK_GUNA_MAP[op] == MoltbookGuna.TAMAS, f"{op} should be TAMAS (destructive)"

    def test_guna_enum_values(self):
        """Guna enum has exactly three values matching BG 14.5."""
        assert MoltbookGuna.SATTVA.value == "sattva"
        assert MoltbookGuna.RAJAS.value == "rajas"
        assert MoltbookGuna.TAMAS.value == "tamas"
        assert len(MoltbookGuna) == 3

    def test_no_orphan_rajas_operations(self):
        """Every RAJAS operation in the map has a corresponding service method."""
        service_methods = set(dir(MoltbookService))
        for op, guna in MOLTBOOK_GUNA_MAP.items():
            if guna == MoltbookGuna.RAJAS and op in MoltbookProtocol.__abstractmethods__:
                assert op in service_methods, f"RAJAS operation '{op}' has no MoltbookService method"


# =============================================================================
# SERVICE REGISTRY WIRING — DI integration
# =============================================================================


class TestServiceRegistryWiring:
    """MoltbookProtocol can be registered and retrieved via ServiceRegistry."""

    def test_register_factory_and_retrieve(self):
        """register_factory + get roundtrip works."""
        from vibe_core.di import ServiceRegistry

        client = MoltbookClient(api_key="test", offline_mode=True)
        svc = MoltbookService(client)
        ServiceRegistry.register_factory(MoltbookProtocol, lambda: svc)

        try:
            retrieved = ServiceRegistry.get(MoltbookProtocol)
            assert retrieved is svc
            assert isinstance(retrieved, MoltbookProtocol)
        finally:
            ServiceRegistry.unregister(MoltbookProtocol)

    def test_is_registered_after_factory(self):
        """is_registered returns True after register_factory."""
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.register_factory(MoltbookProtocol, lambda: None)
        try:
            assert ServiceRegistry.is_registered(MoltbookProtocol)
        finally:
            ServiceRegistry.unregister(MoltbookProtocol)

    def test_unregister_cleans_up(self):
        """After unregister, get returns None."""
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.register_factory(MoltbookProtocol, lambda: "dummy")
        ServiceRegistry.unregister(MoltbookProtocol)
        assert ServiceRegistry.get(MoltbookProtocol) is None


# =============================================================================
# PARASHURAMA WHITELIST — Network proxy
# =============================================================================


class TestParashuramaWhitelist:
    """moltbook.com must be in Parashurama's network proxy whitelist."""

    def test_www_moltbook_in_whitelist(self):
        from vibe_core.protocols.mahajanas.parashurama.types.network_proxy import KernelNetworkProxy

        assert "www.moltbook.com" in KernelNetworkProxy.DEFAULT_WHITELIST

    def test_bare_moltbook_in_whitelist(self):
        from vibe_core.protocols.mahajanas.parashurama.types.network_proxy import KernelNetworkProxy

        assert "moltbook.com" in KernelNetworkProxy.DEFAULT_WHITELIST


# =============================================================================
# TWO-PLUGIN ISOLATION — No shared state
# =============================================================================


class TestPluginIsolation:
    """Two plugin instances must not share state."""

    def test_tick_counts_independent(self):
        p1 = MoltbookPlugin()
        p1._client = MoltbookClient(api_key="test", offline_mode=True)
        p2 = MoltbookPlugin()
        p2._client = MoltbookClient(api_key="test", offline_mode=True)

        for _ in range(5):
            p1._on_mahamantra_tick({})
        assert p1._tick_count == 5
        assert p2._tick_count == 0

    def test_error_state_independent(self):
        p1 = MoltbookPlugin()
        p1._client = MoltbookClient(api_key="test", offline_mode=True)
        p1._last_heartbeat_error = "error"
        p2 = MoltbookPlugin()
        p2._client = MoltbookClient(api_key="test", offline_mode=True)
        assert p2._last_heartbeat_error is None

    def test_service_logs_independent(self):
        """Two services do not share operation logs."""
        c1 = MoltbookClient(api_key="test", offline_mode=True)
        c2 = MoltbookClient(api_key="test", offline_mode=True)
        s1 = MoltbookService(c1)
        s2 = MoltbookService(c2)

        s1.create_post("A", "a")
        assert len(s1._operation_log) == 1
        assert len(s2._operation_log) == 0


# =============================================================================
# INBOUND DM PROCESSING — The untested critical path
# =============================================================================


class TestInboundDMProcessing:
    """_process_inbound_dms routes DMs through Govardhan Gateway with dedup."""

    def test_routes_new_dm_through_gateway(self, plugin):
        """New DM with content is routed through gateway.receive()."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]
        plugin._client._mock_db["dms"] = [
            {"id": "dm1", "conversation_id": "conv1", "sender": "AgentX", "content": "Hello steward"},
        ]

        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()

        assert mock_gw.receive.call_count == 1
        req = mock_gw.receive.call_args[0][0]
        assert req["context"]["source"] == "moltbook_dm"
        assert req["context"]["sender"] == "AgentX"
        assert req["context"]["conversation_id"] == "conv1"

    def test_dedup_skips_already_seen_messages(self, plugin):
        """Messages already in _seen_message_ids are NOT re-routed."""
        from unittest.mock import MagicMock, patch

        plugin._seen_message_ids.add("dm1")
        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]
        plugin._client._mock_db["dms"] = [
            {"id": "dm1", "conversation_id": "conv1", "sender": "A", "content": "old"},
            {"id": "dm2", "conversation_id": "conv1", "sender": "B", "content": "new"},
        ]

        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()

        # Only dm2 should be routed (dm1 already seen)
        assert mock_gw.receive.call_count == 1
        req = mock_gw.receive.call_args[0][0]
        assert req["context"]["sender"] == "B"
        assert "dm2" in plugin._seen_message_ids

    def test_seen_ids_accumulate_across_heartbeats(self, plugin):
        """_seen_message_ids persists across multiple heartbeat cycles."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]
        plugin._client._mock_db["dms"] = [
            {"id": "dm1", "conversation_id": "conv1", "sender": "A", "content": "first"},
        ]

        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()
            assert mock_gw.receive.call_count == 1

            # Second heartbeat — same message, should be skipped
            mock_gw.reset_mock()
            plugin._process_inbound_dms()
            assert mock_gw.receive.call_count == 0

    def test_empty_conversations_no_crash(self, plugin):
        """No conversations → no crash, no gateway calls."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["conversations"] = []
        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()
        assert mock_gw.receive.call_count == 0

    def test_empty_content_skipped(self, plugin):
        """Messages with empty content are not routed."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]
        plugin._client._mock_db["dms"] = [
            {"id": "dm1", "conversation_id": "conv1", "sender": "A", "content": ""},
        ]

        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()
        assert mock_gw.receive.call_count == 0

    def test_message_without_id_still_routed(self, plugin):
        """Messages without 'id' field are routed but not tracked for dedup."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]
        plugin._client._mock_db["dms"] = [
            {"conversation_id": "conv1", "sender": "A", "content": "no id msg"},
        ]

        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()
        assert mock_gw.receive.call_count == 1
        # No id → not added to seen set
        assert len(plugin._seen_message_ids) == 0

    def test_gateway_error_does_not_crash(self, plugin):
        """Gateway.receive() failure is caught, other messages still processed."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]
        plugin._client._mock_db["dms"] = [
            {"id": "dm1", "conversation_id": "conv1", "sender": "A", "content": "msg1"},
            {"id": "dm2", "conversation_id": "conv1", "sender": "B", "content": "msg2"},
        ]

        mock_gw = MagicMock()
        mock_gw.receive.side_effect = [RuntimeError("gateway down"), None]
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            plugin._process_inbound_dms()  # must not raise

        assert mock_gw.receive.call_count == 2
        # dm1 failed → NOT added to seen (so it retries next cycle)
        assert "dm1" not in plugin._seen_message_ids
        # dm2 succeeded → added to seen
        assert "dm2" in plugin._seen_message_ids

    def test_heartbeat_triggers_dm_processing_on_new_messages(self, plugin):
        """Full path: tick 16 → heartbeat → has_new_messages → _process_inbound_dms."""
        from unittest.mock import MagicMock, patch

        plugin._client._mock_db["dms"] = [
            {"id": "dm1", "conversation_id": "conv1", "sender": "A", "content": "hello"},
        ]
        plugin._client._mock_db["conversations"] = [{"id": "conv1"}]

        mock_gw = MagicMock()
        with patch("vibe_core.gateway.mahamantra_gateway.get_gateway", return_value=mock_gw):
            for _ in range(_TICKS_PER_HEARTBEAT):
                plugin._on_mahamantra_tick({})

        # Heartbeat detected new messages → routed through gateway
        assert mock_gw.receive.call_count == 1
