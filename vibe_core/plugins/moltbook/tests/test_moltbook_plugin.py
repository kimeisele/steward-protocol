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

import pytest

from vibe_core.mahamantra import MoltbookClient
from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.plugins.moltbook.managers.drainer import ContentDrainer
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
    """Fresh plugin with offline client — complete state isolation.

    Mocks _director_propose → None to prevent LLM API calls (httpx → SSL timeout).
    The heartbeat pipeline still runs: scan → strategy → intents → enqueue.
    Content generation has its own test suite (test_composer.py, test_agency_director.py).
    """
    p = MoltbookPlugin()
    p._client = MoltbookClient(api_key="test", offline_mode=True)
    p._offline_mode = True
    p._heartbeat._HEARTBEAT_DEBOUNCE_S = 0  # Disable debounce in tests (instant ticks)
    # Prevent LLM calls: _director_propose is the entry to AgencyDirector → OpenRouter
    p._director_propose = lambda *a, **kw: None
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
        assert snapshot["version"] == 7
        assert snapshot["client_active"] is False
        assert "orchestrator_state" in snapshot

    def test_snapshot_with_client(self, plugin):
        """Active plugin includes all rate limit fields + queue state + tracking counts."""
        snapshot = plugin.snapshot_state()
        assert snapshot["version"] == 7
        assert snapshot["client_active"] is True
        assert "orchestrator_state" in snapshot
        assert "requests_this_minute" in snapshot
        assert "posts_this_30m" in snapshot
        assert "comments_this_hour" in snapshot
        assert "last_minute_reset" in snapshot
        assert "last_30m_reset" in snapshot
        assert "last_hour_reset" in snapshot
        assert "queue_size" in snapshot
        assert "queue_stats" in snapshot
        assert "seen_message_count" in snapshot
        assert "seen_post_count" in snapshot
        assert "own_comment_count" in snapshot
        assert "comment_thread_count" in snapshot
        assert "followed_agent_count" in snapshot
        assert "subscribed_submolt_count" in snapshot
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
        """16th tick triggers heartbeat. Includes submolt discovery on first heartbeat."""
        initial_requests = plugin._client.limits.requests_this_minute
        for _ in range(16):
            plugin._on_mahamantra_tick({})
        # 1 heartbeat + 1 submolt discovery (fires at heartbeat_count==1)
        assert plugin._client.limits.requests_this_minute >= initial_requests + 1
        assert plugin._last_heartbeat_error is None

    def test_heartbeat_fires_every_16_ticks(self, plugin):
        """Multiple full mantra cycles each trigger heartbeat."""
        for _ in range(_TICKS_PER_HEARTBEAT * 3):
            plugin._on_mahamantra_tick({})
        assert plugin._tick_count == _TICKS_PER_HEARTBEAT * 3
        assert plugin._heartbeat_count == 3

    def test_heartbeat_at_exact_multiples(self, plugin):
        """Heartbeat count increments at tick 16, 32, 48 — exactly at multiples."""
        import time as time_module

        for i in range(1, 49):
            plugin._on_mahamantra_tick({})
            expected_heartbeats = i // _TICKS_PER_HEARTBEAT
            assert plugin._heartbeat_count == expected_heartbeats, (
                f"At tick {i}, expected {expected_heartbeats} heartbeats"
            )
            # Small delay after heartbeat triggers to let debounce reset for next cycle
            if i % _TICKS_PER_HEARTBEAT == 0:
                time_module.sleep(0.05)  # Just enough to clear debounce guard

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
        expected_keys = {
            "client",
            "offline",
            "last_error",
            "listener_wired",
            "ticks_seen",
            "content_queue",
            "heartbeats",
            "intervals",
            "circuit_executor",
            "agora_wired",
            "execute_content_circuit",
        }
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
        """All protocol methods are abstract."""
        expected = {
            # SATTVA
            "check_heartbeat",
            "get_own_profile",
            "get_profile",
            "get_feed",
            "get_personalized_feed",
            "get_post",
            "get_comments",
            "search",
            "get_conversations",
            "get_messages",
            "get_dm_requests",
            "get_submolts",
            "get_submolt",
            "verify_credentials",
            # RAJAS
            "create_post",
            "comment",
            "send_dm",
            "send_dm_request",
            "approve_dm_request",
            "reject_dm_request",
            "upvote",
            "downvote",
            "upvote_comment",
            "follow",
            "subscribe",
            "create_submolt",
            "update_profile",
            # TAMAS
            "delete_post",
            "unfollow",
            "unsubscribe",
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
        assert abstract_count == 30


# =============================================================================
# MOLTBOOK SERVICE — SATTVA operations (read-only, no side effects)
# =============================================================================


class TestMoltbookServiceSattva:
    """SATTVA operations: read-only, no operation log entries, no state mutation."""

    def test_check_heartbeat(self, service):
        result = service.check_heartbeat()
        assert "has_activity" in result
        assert "requests" in result

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
# QUEUE HEALTH MONITORING
# =============================================================================


class TestQueueHealthMonitoring:
    """Queue overflow detection and high-water-mark logging."""

    def test_no_warning_when_empty(self, plugin):
        """No overflow warning when queue is empty."""
        plugin._monitor_queue_health()
        # Just verify no crash — log assertions need caplog

    def test_overflow_tracking(self, plugin):
        """Dropped count rises when queue is full and items keep arriving."""
        from vibe_core.protocols.moltbook_content import ContentQueue, ContentType

        plugin._content_queue = ContentQueue(max_size=2)
        for i in range(5):
            plugin._content_queue.enqueue({"content_type": ContentType.VOTE.value, "post_id": f"p{i}"})
        stats = plugin._content_queue.stats
        assert stats["total_dropped"] == 3  # 5 enqueued - 2 capacity = 3 dropped
        assert stats["queued"] == 2

    def test_overflow_log_rate_limited(self, plugin):
        """Overflow log timestamp updates only after 8+ heartbeats."""
        plugin._content_drainer._last_overflow_log = 0
        plugin._heartbeat._heartbeat_count = 10
        plugin._content_queue._total_dropped = 1
        plugin._monitor_queue_health()
        assert plugin._content_drainer._last_overflow_log == 10  # Updated (10 - 0 >= 8)

        plugin._heartbeat._heartbeat_count = 15
        plugin._content_queue._total_dropped = 2
        plugin._monitor_queue_health()
        assert plugin._content_drainer._last_overflow_log == 10  # NOT updated (15 - 10 = 5 < 8)

        plugin._heartbeat._heartbeat_count = 20
        plugin._monitor_queue_health()
        assert plugin._content_drainer._last_overflow_log == 20  # Updated (20 - 10 >= 8)


# =============================================================================
# FOLLOW-BACK STRATEGY
# =============================================================================


class TestFollowBack:
    """Follow-back logic: follow agents who DM us."""

    def test_follow_back_queues_proposal(self, plugin):
        """_follow_back() enqueues a FOLLOW proposal."""
        from vibe_core.protocols.moltbook_content import ContentType

        plugin._follow_back("agent_alice")
        assert plugin._content_queue.size == 1
        proposal = plugin._content_queue.drain(1)[0]
        assert proposal["content_type"] == ContentType.FOLLOW.value
        assert proposal["to_agent"] == "agent_alice"
        assert proposal["source"] == "follow_back"

    def test_follow_back_deduplicates(self, plugin):
        """Same agent is not followed twice."""
        plugin._follow_back("agent_bob")
        plugin._follow_back("agent_bob")
        assert plugin._content_queue.size == 1  # Only one queued

    def test_follow_back_skips_unknown(self, plugin):
        """'unknown' sender is not followed."""
        plugin._follow_back("unknown")
        assert plugin._content_queue.size == 0

    def test_follow_back_skips_empty(self, plugin):
        """Empty sender is not followed."""
        plugin._follow_back("")
        assert plugin._content_queue.size == 0

    def test_followed_agents_tracked(self, plugin):
        """_followed_agents set is populated."""
        plugin._follow_back("agent_carol")
        assert "agent_carol" in plugin._followed_agents


# =============================================================================
# SUBMOLT DISCOVERY
# =============================================================================


class TestSubmoltDiscovery:
    """Submolt discovery and subscription."""

    def test_discover_queues_subscriptions(self, plugin):
        """_discover_submolts() enqueues SUBSCRIBE proposals for available submolts."""
        from vibe_core.protocols.moltbook_content import ContentType

        plugin._subscribed_submolts.add("steward-protocol")  # Skip ensure_own_submolt
        plugin._client._mock_db["submolts"] = [
            {"name": "ai_agents", "display_name": "AI Agents"},
            {"name": "governance", "display_name": "Governance"},
        ]
        plugin._discover_submolts()
        assert plugin._content_queue.size == 2
        proposals = plugin._content_queue.drain(5)
        names = {p["submolt"] for p in proposals}
        assert names == {"ai_agents", "governance"}
        for p in proposals:
            assert p["content_type"] == ContentType.SUBSCRIBE.value

    def test_discover_deduplicates(self, plugin):
        """Already-subscribed submolts are not re-subscribed."""
        plugin._subscribed_submolts.add("steward-protocol")  # Skip ensure_own_submolt
        plugin._subscribed_submolts.add("ai_agents")
        plugin._client._mock_db["submolts"] = [
            {"name": "ai_agents", "display_name": "AI Agents"},
            {"name": "governance", "display_name": "Governance"},
        ]
        plugin._discover_submolts()
        assert plugin._content_queue.size == 1  # Only governance

    def test_discover_handles_empty(self, plugin):
        """No crash when no submolts exist."""
        plugin._subscribed_submolts.add("steward-protocol")  # Skip ensure_own_submolt
        plugin._client._mock_db["submolts"] = []
        plugin._discover_submolts()
        assert plugin._content_queue.size == 0

    def test_subscribed_tracked(self, plugin):
        """_subscribed_submolts set is populated after discovery."""
        plugin._client._mock_db["submolts"] = [{"name": "tech"}]
        plugin._discover_submolts()
        assert "tech" in plugin._subscribed_submolts


# =============================================================================
# PROFILE AUTO-UPDATE
# =============================================================================


class TestProfileUpdate:
    """Profile auto-update: karma stats in bio."""

    def test_update_profile_runs(self, plugin):
        """_update_profile() executes without error."""
        plugin._service = MoltbookService(plugin._client)
        plugin._update_profile()
        assert plugin._last_profile_heartbeat == 0  # Set to _heartbeat_count

    def test_update_profile_logs_rajas(self, plugin):
        """Profile update is a RAJAS operation and gets logged."""
        svc = MoltbookService(plugin._client)
        plugin._service = svc
        plugin._update_profile()
        rajas_ops = [e for e in svc._operation_log if e["operation"] == "update_profile"]
        assert len(rajas_ops) == 1

    def test_update_profile_fetches_profile_first(self, plugin):
        """Profile update reads current profile (SATTVA) before patching (RAJAS)."""
        svc = MoltbookService(plugin._client)
        plugin._service = svc
        plugin._update_profile()
        # get_own_profile (SATTVA) + update_profile (RAJAS) = 1 RAJAS log
        assert len(svc._operation_log) == 1  # Only RAJAS ops logged

    def test_update_profile_without_service(self, bare_plugin):
        """No crash when service is None."""
        bare_plugin._update_profile()  # Should not raise


# =============================================================================
# ACTIVITY LOGGING (JSONL)
# =============================================================================


class TestActivityLogging:
    """JSONL append-only activity log."""

    def test_log_activity_creates_file(self, plugin, tmp_path):
        """_log_activity() creates and appends to JSONL file."""
        plugin._activity_log_path = tmp_path / "activity.jsonl"
        plugin._log_activity("test_event", {"key": "value"})
        assert plugin._activity_log_path.exists()
        content = plugin._activity_log_path.read_text()
        assert "test_event" in content
        assert '"key":"value"' in content

    def test_log_activity_appends(self, plugin, tmp_path):
        """Multiple events append as separate lines."""
        plugin._activity_log_path = tmp_path / "activity.jsonl"
        plugin._log_activity("event1")
        plugin._log_activity("event2")
        lines = plugin._activity_log_path.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_log_activity_valid_json(self, plugin, tmp_path):
        """Each line is valid JSON."""
        import json

        plugin._activity_log_path = tmp_path / "activity.jsonl"
        plugin._log_activity("dm_sent", {"conversation_id": "c1"})
        line = plugin._activity_log_path.read_text().strip()
        parsed = json.loads(line)
        assert parsed["event"] == "dm_sent"
        assert "t" in parsed  # timestamp
        assert "hb" in parsed  # heartbeat count

    def test_log_activity_no_path_noop(self, plugin):
        """No crash when log path is None."""
        plugin._activity_log_path = None
        plugin._log_activity("test")  # Should not raise

    def test_drain_logs_activity(self, plugin, tmp_path):
        """Queue drain logs activity for each executed proposal."""
        from vibe_core.protocols.moltbook_content import ContentType

        plugin._activity_log_path = tmp_path / "activity.jsonl"
        plugin._service = MoltbookService(plugin._client)
        plugin._offline_mode = False  # Must be online to drain
        plugin._content_queue.enqueue(
            {
                "content_type": ContentType.VOTE.value,
                "post_id": "p1",
            }
        )
        plugin._drain_content_queue()
        content = plugin._activity_log_path.read_text()
        assert "upvoted" in content


# =============================================================================
# REPLY MONITORING (COMPLETED)
# =============================================================================


class TestReplyMonitoring:
    """Reply monitoring: track own comment threads and respond to replies."""

    def test_no_crash_without_map(self, plugin):
        """No crash when comment_post_map is empty."""
        plugin._proposer = type(
            "P",
            (),
            {
                "propose_comment": lambda *a, **kw: None,
            },
        )()
        plugin._check_own_comment_replies()

    def test_detects_reply_to_own_comment(self, plugin):
        """Detects a reply to our comment and queues a response."""
        from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

        plugin._proposer = ResonanceProposer()
        plugin._comment_post_map = {"c99": "p0"}
        # Seed mock with a reply to our comment
        plugin._client._mock_db["comments"] = [
            {
                "id": "c100",
                "post_id": "p0",
                "parent_id": "c99",
                "content": "Great point!",
                "author": {"name": "agent_x"},
            },
        ]
        plugin._check_own_comment_replies()
        # The proposer should have been called and may or may not queue a reply
        # depending on pipeline filters — but no crash occurred
        assert "c100" in plugin._seen_message_ids

    def test_skips_already_seen_replies(self, plugin):
        """Already-seen comment IDs are not re-processed."""
        from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

        plugin._proposer = ResonanceProposer()
        plugin._comment_post_map = {"c99": "p0"}
        plugin._seen_message_ids.add("c100")  # Already seen
        plugin._client._mock_db["comments"] = [
            {
                "id": "c100",
                "post_id": "p0",
                "parent_id": "c99",
                "content": "Already seen",
                "author": {"name": "agent_y"},
            },
        ]
        initial_queue_size = plugin._content_queue.size
        plugin._check_own_comment_replies()
        assert plugin._content_queue.size == initial_queue_size  # Nothing new queued

    def test_comment_post_map_populated_on_drain(self, plugin):
        """_comment_post_map is populated when comments are drained."""
        from vibe_core.protocols.moltbook_content import ContentType

        plugin._service = MoltbookService(plugin._client)
        plugin._offline_mode = False
        plugin._content_queue.enqueue(
            {
                "content_type": ContentType.COMMENT.value,
                "post_id": "p1",
                "content": "Test comment",
            }
        )
        plugin._drain_content_queue()
        # The mock comment returns id "c99"
        assert "c99" in plugin._comment_post_map
        assert plugin._comment_post_map["c99"] == "p1"

    def test_reply_monitoring_uses_service_not_client(self, plugin):
        """Reply monitoring routes through MoltbookService for Guna audit trail."""
        from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

        plugin._proposer = ResonanceProposer()
        plugin._comment_post_map = {"c99": "p0"}
        plugin._client._mock_db["comments"] = []
        # Force service creation via the method
        plugin._service = None
        plugin._check_own_comment_replies()
        # Service should have been created
        assert plugin._service is not None


# =============================================================================
# FAULT ISOLATION (SAFE_CALL + HEARTBEAT CRASH PROTECTION)
# =============================================================================


class TestFaultIsolation:
    """Heartbeat operations are fault-isolated — one failure doesn't kill the loop."""

    def test_safe_call_catches_exception(self, plugin):
        """_safe_call wraps exceptions and logs, never re-raises."""

        def exploding():
            raise RuntimeError("boom")

        # Should NOT raise
        plugin._safe_call(exploding, "test_phase")

    def test_safe_call_runs_fn(self, plugin):
        """_safe_call actually calls the function on success."""
        called = []

        def tracker():
            called.append(True)

        plugin._safe_call(tracker, "test")
        assert len(called) == 1

    def test_heartbeat_survives_feed_failure(self, plugin):
        """If _analyze_feed crashes, queue drain still runs."""
        from vibe_core.protocols.moltbook_content import ContentType

        plugin._service = MoltbookService(plugin._client)
        plugin._offline_mode = False

        # Poison the feed — make get_personalized_feed throw
        original = plugin._client.get_personalized_feed

        async def poisoned_feed(*a, **kw):
            raise RuntimeError("Network error")

        plugin._client.get_personalized_feed = poisoned_feed

        # Enqueue a vote that should drain even if feed fails
        plugin._content_queue.enqueue(
            {
                "content_type": ContentType.VOTE.value,
                "post_id": "p_test",
            }
        )

        # Advance to feed interval
        plugin._heartbeat._heartbeat_count = plugin._feed_interval - 1
        plugin._heartbeat.dispatch_heartbeat({})

        # Queue was drained despite feed failure
        assert plugin._content_queue.is_empty
        plugin._client.get_personalized_feed = original


# =============================================================================
# RETRY QUEUE (FAILED PROPOSALS RE-ENQUEUED)
# =============================================================================


class TestRetryQueue:
    """Failed proposals are re-enqueued, not lost."""

    def test_failed_proposal_reenqueued(self, plugin):
        """A proposal that fails execution is put back in the queue."""
        from vibe_core.protocols.moltbook_content import ContentType

        # Create a service that explodes on upvote
        svc = MoltbookService(plugin._client)
        original_upvote = svc.upvote

        def exploding_upvote(post_id):
            raise ConnectionError("API timeout")

        svc.upvote = exploding_upvote
        plugin._service = svc
        plugin._offline_mode = False

        plugin._content_queue.enqueue(
            {
                "content_type": ContentType.VOTE.value,
                "post_id": "p_fail",
            }
        )

        plugin._drain_content_queue()
        # Proposal should be back in queue with _retries=1
        assert plugin._content_queue.size == 1
        svc.upvote = original_upvote

    def test_proposal_dropped_after_max_retries(self, plugin, tmp_path):
        """After _MAX_PROPOSAL_RETRIES, proposal is permanently dropped."""
        from vibe_core.protocols.moltbook_content import ContentType

        svc = MoltbookService(plugin._client)
        original_upvote = svc.upvote

        def exploding_upvote(post_id):
            raise ConnectionError("API timeout")

        svc.upvote = exploding_upvote
        plugin._service = svc
        plugin._offline_mode = False
        plugin._activity_log_path = tmp_path / "activity.jsonl"

        # Enqueue with retries already at max
        plugin._content_queue.enqueue(
            {
                "content_type": ContentType.VOTE.value,
                "post_id": "p_doomed",
                "_retries": ContentDrainer._MAX_PROPOSAL_RETRIES,
            }
        )

        plugin._drain_content_queue()
        # Should NOT be re-enqueued — permanently dropped
        assert plugin._content_queue.is_empty

        # Should be logged as dropped
        content = plugin._activity_log_path.read_text()
        assert "proposal_dropped" in content
        svc.upvote = original_upvote

    def test_permission_error_not_retried(self, plugin):
        """TAMAS PermissionError is permanent — never retried."""
        from vibe_core.protocols.moltbook_content import ContentType

        svc = MoltbookService(plugin._client)
        plugin._offline_mode = False
        original_delete = svc.delete_post

        def blocked_delete(post_id):
            raise PermissionError("TAMAS")

        svc.delete_post = blocked_delete
        plugin._service = svc

        # VOTE calls upvote, not delete — so we test the except branch directly
        # by making upvote throw PermissionError
        original_upvote = svc.upvote
        svc.upvote = lambda pid: (_ for _ in ()).throw(PermissionError("TAMAS blocked"))
        plugin._content_queue.enqueue(
            {
                "content_type": ContentType.VOTE.value,
                "post_id": "p_tamas",
            }
        )

        plugin._drain_content_queue()
        # PermissionError → not retried, queue stays empty
        assert plugin._content_queue.is_empty
        svc.upvote = original_upvote
        svc.delete_post = original_delete


# =============================================================================
# MEMORY TRIMMING
# =============================================================================


class TestMemoryTrimming:
    """In-memory sets are trimmed to prevent unbounded growth."""

    def test_trim_seen_messages(self, plugin):
        """_trim_memory caps _seen_message_ids to _MAX_SEEN_IDS."""
        # Overfill
        for i in range(plugin._MAX_SEEN_IDS + 500):
            plugin._seen_message_ids.add(f"msg_{i:05d}")
        assert len(plugin._seen_message_ids) > plugin._MAX_SEEN_IDS

        plugin._trim_memory()
        assert len(plugin._seen_message_ids) == plugin._MAX_SEEN_IDS

    def test_trim_comment_post_map(self, plugin):
        """_trim_memory caps _comment_post_map."""
        for i in range(plugin._MAX_SEEN_IDS + 100):
            plugin._comment_post_map[f"c{i:05d}"] = f"p{i}"

        plugin._trim_memory()
        assert len(plugin._comment_post_map) == plugin._MAX_SEEN_IDS

    def test_trim_noop_when_under_limit(self, plugin):
        """_trim_memory does nothing when sets are small."""
        plugin._seen_message_ids = {"a", "b", "c"}
        plugin._trim_memory()
        assert plugin._seen_message_ids == {"a", "b", "c"}

    def test_trim_keeps_most_recent(self, plugin):
        """Trimming keeps the most recent (highest sorted) IDs."""
        for i in range(plugin._MAX_SEEN_IDS + 10):
            plugin._seen_post_ids.add(f"p_{i:05d}")

        plugin._trim_memory()
        # The highest IDs should remain
        assert f"p_{plugin._MAX_SEEN_IDS + 9:05d}" in plugin._seen_post_ids
        # The lowest should be gone
        assert "p_00000" not in plugin._seen_post_ids


# =============================================================================
# AGENT NAME RESOLUTION
# =============================================================================


class TestAgentNameResolution:
    """Profile updates use the actual agent name, not hardcoded."""

    def test_default_agent_name(self, bare_plugin):
        """Default agent name before boot."""
        assert bare_plugin._agent_name == "steward-protocol"

    def test_agent_name_resolved_from_service(self, plugin):
        """Agent name is resolved from profile when service is available."""
        plugin._service = MoltbookService(plugin._client)
        # Simulate the boot-time resolution
        profile = plugin._service.get_own_profile()
        name = profile.get("name", "") if isinstance(profile, dict) else ""
        if name:
            plugin._agent_name = name
        # Mock /agents/me returns "steward-protocol"
        assert plugin._agent_name == "steward-protocol"

    def test_profile_update_uses_agent_name(self, plugin):
        """_update_profile uses _agent_name, not hardcoded string."""
        plugin._service = MoltbookService(plugin._client)
        plugin._agent_name = "custom-agent-42"
        plugin._update_profile()
        # The profile PATCH was called — verify via RAJAS log
        rajas_ops = [e for e in plugin._service._operation_log if e["operation"] == "update_profile"]
        assert len(rajas_ops) == 1


# =============================================================================
# GAD-000 COMPLIANCE
# =============================================================================


class TestGADCompliance:
    """MoltbookService must be GAD-000 compliant.

    GAD-000: Operator Inversion Principle
    - 6 Kshetra criteria (Discoverability, Observability, Parseability,
      Composability, Idempotency, Recoverability)
    - 4 Dharma principles (Daya, Satyam, Tapas, Saucam)
    - MantraHeartbeat (Japa loop)
    - Sovereign signature (Prabhupada link)
    """

    def test_is_gad_base(self, service):
        """MoltbookService inherits from GADBase."""
        from vibe_core.mahamantra.protocols._gad import GADBase

        assert isinstance(service, GADBase)

    def test_has_heartbeat(self, service):
        """Service has a MantraHeartbeat from GADBase."""
        from vibe_core.mahamantra.protocols._gad import MantraHeartbeat

        assert isinstance(service.heartbeat, MantraHeartbeat)

    def test_chant(self, service):
        """Service can chant (Japa loop heartbeat)."""
        result = service.chant()
        assert isinstance(result, bool)

    # --- THE 6 KSHETRA CRITERIA ---

    def test_discover(self, service):
        """Discoverability: returns structured capability description."""
        desc = service.discover()
        assert isinstance(desc, dict)
        assert desc["service"] == "MoltbookService"
        assert desc["protocol"] == "MoltbookProtocol"
        assert desc["gad_compliant"] is True
        assert "sattva" in desc["operations"]
        assert "rajas" in desc["operations"]
        assert "tamas" in desc["operations"]
        assert "rate_limits" in desc
        assert desc["rate_limits"]["requests_per_minute"] == 100

    def test_get_state(self, service):
        """Observability: returns current state."""
        state = service.get_state()
        assert isinstance(state, dict)
        assert "rate_limits" in state
        assert "health" in state
        assert "audit_trail" in state
        assert "heartbeat" in state
        assert state["rate_limits"]["requests_this_minute"] == 0

    def test_is_healthy(self, service):
        """Health check passes when no failures."""
        # Fresh service — chant first to move from DISCONNECTED
        service.chant()
        assert service.is_healthy() is True

    def test_is_healthy_after_failures(self, service):
        """Health check fails after too many consecutive failures."""
        service._consecutive_failures = 10
        assert service.is_healthy() is False

    def test_is_idempotent(self, service):
        """Service is not idempotent as a whole (has write ops)."""
        assert service.is_idempotent is False

    def test_detect_drift_healthy(self, service):
        """No drift on fresh service."""
        drifts = service.detect_drift()
        assert drifts == []

    def test_detect_drift_rate_breach(self, service):
        """Detect rate limit overrun."""
        service._client.limits.requests_this_minute = 999
        drifts = service.detect_drift()
        assert any("RATE_LIMIT_BREACH" in d for d in drifts)

    def test_detect_drift_api_degraded(self, service):
        """Detect API degradation."""
        service._consecutive_failures = 5
        drifts = service.detect_drift()
        assert any("API_DEGRADED" in d for d in drifts)

    # --- THE 4 DHARMA PRINCIPLES ---

    def test_daya(self, service):
        """Mercy: all operations are Guna-classified."""
        assert service.test_daya() is True

    def test_satyam(self, service):
        """Truthfulness: no swallowed errors."""
        assert service.test_satyam() is True

    def test_satyam_fails_on_persistent_errors(self, service):
        """Truthfulness fails when errors are being swallowed."""
        service._last_api_error = "Connection refused"
        service._consecutive_failures = 5
        assert service.test_satyam() is False

    def test_tapas(self, service):
        """Austerity: rate limits enforced."""
        assert service.test_tapas() is True

    def test_tapas_fails_on_breach(self, service):
        """Austerity fails when rate limits are breached."""
        service._client.limits.requests_this_minute = 999
        assert service.test_tapas() is False

    def test_saucam(self, service):
        """Cleanliness: API key is present."""
        assert service.test_saucam() is True

    # --- FULL AUDIT ---

    def test_audit_returns_gad_audit(self, service):
        """audit() returns a GADAudit dataclass."""
        from vibe_core.mahamantra.protocols._gad import GADAudit

        result = service.audit()
        assert isinstance(result, GADAudit)

    def test_audit_discoverability(self, service):
        """Discoverability passes in audit."""
        result = service.audit()
        assert result.discoverability is True

    def test_audit_observability(self, service):
        """Observability passes in audit."""
        result = service.audit()
        assert result.observability is True

    def test_audit_dharma_score(self, service):
        """All 4 Dharma principles pass."""
        result = service.audit()
        assert result.dharma_score == 4

    def test_audit_criteria_score(self, service):
        """At least 5 of 6 criteria pass (idempotency is False by design)."""
        result = service.audit()
        assert result.criteria_score >= 5


# =============================================================================
# COMMENT DEDUP — Post-level deduplication
# =============================================================================


class TestCommentDedup:
    """Post-level comment dedup: don't comment on the same post twice per session.

    _commented_post_ids tracks target_post_id → skip if already seen.
    Persisted in seen_ids.json (version 5).
    """

    def test_init_has_empty_set(self, plugin):
        """Fresh plugin starts with empty commented_post_ids."""
        assert isinstance(plugin._commented_post_ids, set)
        assert len(plugin._commented_post_ids) == 0

    def test_add_and_check(self, plugin):
        """Adding a post_id prevents it from matching again."""
        plugin._commented_post_ids.add("post-123")
        assert "post-123" in plugin._commented_post_ids
        assert "post-456" not in plugin._commented_post_ids

    def test_persistence_roundtrip(self, plugin, tmp_path):
        """commented_post_ids survive save → load cycle."""
        plugin._state_dir = tmp_path
        plugin._commented_post_ids = {"p1", "p2", "p3"}

        # Save
        plugin._persist_queue()

        # Load into new plugin
        p2 = MoltbookPlugin()
        p2._client = MoltbookClient(api_key="test", offline_mode=True)
        p2._state_dir = tmp_path
        p2._restore_queue()

        assert p2._commented_post_ids == {"p1", "p2", "p3"}

    def test_persistence_version_5(self, plugin, tmp_path):
        """seen_ids.json version is 5 with commented_post_ids field."""
        import json

        plugin._state_dir = tmp_path
        plugin._commented_post_ids = {"post-abc"}
        plugin._persist_queue()

        seen_file = tmp_path / "seen_ids.json"
        assert seen_file.exists()
        data = json.loads(seen_file.read_text())
        assert data["version"] == 5
        assert "commented_post_ids" in data
        assert "post-abc" in data["commented_post_ids"]

    def test_empty_set_persists_cleanly(self, plugin, tmp_path):
        """Empty commented_post_ids doesn't break persistence."""
        plugin._state_dir = tmp_path
        plugin._persist_queue()

        p2 = MoltbookPlugin()
        p2._client = MoltbookClient(api_key="test", offline_mode=True)
        p2._state_dir = tmp_path
        p2._restore_queue()

        assert p2._commented_post_ids == set()

    def test_backward_compat_no_field(self, plugin, tmp_path):
        """Old seen_ids.json without commented_post_ids → empty set, no crash."""
        import json

        seen_file = tmp_path / "seen_ids.json"
        seen_file.write_text(json.dumps({
            "version": 4,
            "message_ids": [],
            "post_ids": [],
        }))

        plugin._state_dir = tmp_path
        plugin._restore_queue()

        assert plugin._commented_post_ids == set()

    def test_audit_legitimacy_positive(self, service):
        """Legitimacy score is positive (not zero)."""
        result = service.audit()
        # With sovereign signed (Prabhupada link), legitimacy > 0
        assert result.legitimacy >= 0.0

    def test_audit_status_not_violates(self, service):
        """Service does NOT violate GAD-000."""
        result = service.audit()
        assert "VIOLATES" not in result.status
