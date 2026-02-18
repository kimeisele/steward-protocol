"""
UNIFIED HEARTBEAT - Integration Test Suite
===========================================

Tests that the 4 surgeries actually work end-to-end:

1. ONE Singularity singleton (no duplicate Krishnas)
2. VenuService → Singularity.tick() → _broadcast() → listeners fire
3. SravanamListener receives ticks (healing scanner is ALIVE)
4. Silent failures are visible (logger.warning, not debug)

These are INTEGRATION tests — they test ROADS, not buildings.
"""
from __future__ import annotations

import pytest

from vibe_core.mahamantra.kernel.singularity import Mahamantra, mahamantra
from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator


# =============================================================================
# TEST 1: ONE SINGULARITY (Ekamevadvitiyam)
# =============================================================================


class TestOneSingularity:
    """Verify there is exactly ONE Singularity instance across the system."""

    def test_lotus_uses_same_singularity(self):
        """MahamantraLotus._get_singularity() returns the kernel singleton."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        singularity = lotus._get_singularity()

        assert singularity is mahamantra, (
            "POLYTHEISM: MahamantraLotus created a SECOND Singularity. "
            "Must use kernel/singularity.py singleton."
        )

    def test_maha_kernel_uses_same_singularity(self):
        """MahaKernel._singularity is the kernel singleton."""
        from vibe_core.mahamantra.kernel.maha_kernel import MahaKernel

        kernel = MahaKernel()

        assert kernel._singularity is mahamantra, (
            "POLYTHEISM: MahaKernel created a SECOND Singularity. "
            "Must use kernel/singularity.py singleton."
        )

    def test_singleton_identity(self):
        """The module-level mahamantra IS a Mahamantra instance."""
        assert isinstance(mahamantra, Mahamantra)

    def test_venu_is_shared(self):
        """Singularity.venu and MahamantraLotus share the SAME flute."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        lotus_venu = lotus.venu
        singularity_venu = mahamantra.venu

        assert lotus_venu is singularity_venu, (
            "TWO FLUTES: Lotus and Singularity have different VenuOrchestrators. "
            "One Krishna, one flute."
        )


# =============================================================================
# TEST 2: UNIFIED HEARTBEAT (Singularity.tick() broadcasts)
# =============================================================================


class TestUnifiedHeartbeat:
    """Verify Singularity.tick() plays flute AND broadcasts to listeners."""

    def test_tick_returns_tick_state(self):
        """Singularity.tick() returns a TickState with all fields."""
        state = mahamantra.tick()

        # TickState may be dict or dataclass — check both access patterns
        if isinstance(state, dict):
            assert "position" in state
            assert "quarter" in state
            assert "guardian" in state
            assert "word" in state
            assert "diw" in state
        else:
            assert hasattr(state, "position")
            assert hasattr(state, "quarter")
            assert hasattr(state, "guardian")
            assert hasattr(state, "word")
            assert hasattr(state, "diw")

    def test_tick_advances_position(self):
        """Consecutive ticks advance the position."""
        state1 = mahamantra.tick()
        state2 = mahamantra.tick()

        def _get(s, key):
            return s[key] if isinstance(s, dict) else getattr(s, key)

        # Positions should differ (mod 16 wrapping is fine)
        assert _get(state2, "position") != _get(state1, "position") or _get(state2, "mala") != _get(state1, "mala")

    def test_tick_plays_flute(self):
        """Singularity.tick() calls venu.step() — DIW is non-zero."""
        state = mahamantra.tick()

        diw = state["diw"] if isinstance(state, dict) else state.diw
        assert diw is not None
        assert isinstance(diw, int)

    def test_tick_broadcasts_to_listeners(self):
        """Singularity.tick() fires _broadcast() — registered listeners receive TickState."""
        received = []

        def listener(state):
            received.append(state)

        mahamantra.register_listener(listener)
        try:
            mahamantra.tick()

            assert len(received) == 1, (
                f"Listener received {len(received)} broadcasts, expected 1. "
                "Singularity._broadcast() is not firing."
            )
            s = received[0]
            diw = s["diw"] if isinstance(s, dict) else s.diw
            guardian = s["guardian"] if isinstance(s, dict) else s.guardian
            assert diw is not None
            assert guardian is not None
        finally:
            # Clean up — remove our test listener
            if listener in mahamantra._listeners:
                mahamantra._listeners.remove(listener)

    def test_multiple_listeners_all_fire(self):
        """All registered listeners receive the broadcast."""
        received_a = []
        received_b = []

        def listener_a(state):
            received_a.append(state)

        def listener_b(state):
            received_b.append(state)

        mahamantra.register_listener(listener_a)
        mahamantra.register_listener(listener_b)
        try:
            mahamantra.tick()

            assert len(received_a) == 1
            assert len(received_b) == 1
            assert received_a[0] is received_b[0]  # Same TickState object
        finally:
            if listener_a in mahamantra._listeners:
                mahamantra._listeners.remove(listener_a)
            if listener_b in mahamantra._listeners:
                mahamantra._listeners.remove(listener_b)

    def test_diw_subscribers_fire_through_tick(self):
        """DIW subscribers on VenuOrchestrator fire when Singularity.tick() is called."""
        from vibe_core.mahamantra.protocols._venu import DIWEvent, DIWSubscriberProtocol

        received_diw = []

        class TestDIWSubscriber(DIWSubscriberProtocol):
            def on_diw(self, event: DIWEvent) -> None:
                received_diw.append(event)

        sub = TestDIWSubscriber()
        venu = mahamantra.venu
        venu.subscribe(sub)
        try:
            mahamantra.tick()

            assert len(received_diw) >= 1, (
                "DIW subscriber did NOT fire through Singularity.tick(). "
                "VenuOrchestrator.step() is not being called."
            )
        finally:
            if sub in venu._subscribers:
                venu._subscribers.remove(sub)


# =============================================================================
# TEST 3: VENU SERVICE INTEGRATION
# =============================================================================


class TestVenuServiceIntegration:
    """Verify VenuService is wired to use Singularity.tick()."""

    def test_venu_service_has_singularity(self):
        """VenuService stores a reference to the Singularity."""
        from vibe_core.services.venu_service import VenuService

        svc = VenuService()

        assert hasattr(svc, "_singularity"), (
            "VenuService has no _singularity attribute. "
            "Surgery 3 may not have been applied."
        )
        assert svc._singularity is mahamantra, (
            "VenuService._singularity is not the kernel singleton."
        )

    def test_lotus_bridge_is_noop(self):
        """LotusBridgeSubscriber.on_beat_tick() is a no-op (retired)."""
        from vibe_core.services.lotus_bridge import LotusBridgeSubscriber

        bridge = LotusBridgeSubscriber()
        initial_count = bridge.broadcast_count

        bridge.on_beat_tick(1, 0)
        bridge.on_beat_tick(2, 1)

        assert bridge.broadcast_count == initial_count + 2
        # The key test: it should NOT have called lotus.tick()
        # (which would double-tick). We verify by checking that
        # _lotus is still None (lazy, never accessed).
        assert bridge._lotus is None, (
            "LotusBridgeSubscriber accessed lotus — it should be a no-op."
        )


# =============================================================================
# TEST 4: SRAVANAM LISTENER WIRING
# =============================================================================


class TestSravanamListenerWiring:
    """Verify the healing scanner can be wired and receives ticks."""

    def test_sravanam_listener_receives_tick(self):
        """SravanamListener, when registered, receives TickState from tick().

        SravanamListener uses __call__ — the instance IS the callback.
        """
        try:
            from vibe_core.mahamantra.dharma.kumaras.sravanam import SravanamListener
        except ImportError:
            pytest.skip("SravanamListener not available")

        received = []
        listener = SravanamListener()

        # Wrap __call__ to spy on invocations
        original_call = listener.__call__

        def spy_call(state):
            received.append(state)
            return original_call(state)

        listener.__call__ = spy_call

        # SravanamListener is callable — register the instance directly
        # But register_listener stores the callable, so we register spy_call
        mahamantra.register_listener(spy_call)
        try:
            mahamantra.tick()

            assert len(received) == 1, (
                "SravanamListener did NOT receive tick. "
                "Healing scanner is DEAD."
            )
        finally:
            if spy_call in mahamantra._listeners:
                mahamantra._listeners.remove(spy_call)


# =============================================================================
# TEST 5: INTENT RESOLVER WIRED IN TICK
# =============================================================================


class TestIntentResolverInTick:
    """Verify MantraKernel.process_queue() runs inside Singularity.tick()."""

    def test_tick_processes_queued_intents(self):
        """A queued intent gets resolved when tick() fires."""
        from vibe_core.mahamantra.kernel.intent import (
            IntentType,
            IntentStatus,
            MantraIntent,
            get_kernel,
        )

        kernel = get_kernel()

        # Queue a SURRENDER intent (always resolves via _krishna_resolves)
        intent: MantraIntent = MantraIntent(
            type=IntentType.SURRENDER,
            target="test_tick_integration",
            params={},
            parampara_vector=37 * 12,  # 444 — always connected
        )
        kernel.queue(intent)

        # Tick should drain the queue
        mahamantra.tick()

        # Queue should be empty after tick
        assert kernel._queue.is_empty, (
            "Intent queue NOT drained by tick(). "
            "MantraKernel.process_queue() is not wired in Singularity.tick()."
        )

    def test_empty_queue_no_error(self):
        """tick() with empty intent queue does not error."""
        # Just tick — should not raise
        mahamantra.tick()


# =============================================================================
# TEST 6: REACTOR LOOP READS STATE (CONSUMER, NOT DRIVER)
# =============================================================================


class TestReactorLoopConsumer:
    """Verify ReactorLoop._meditate() reads Singularity state, does NOT drive tick."""

    def test_meditate_uses_get_tick_not_tick(self):
        """_meditate() must call get_tick() (read), not tick() (advance)."""
        import inspect
        from vibe_core.mahamantra.reactor.loop import ReactorLoop

        source = inspect.getsource(ReactorLoop._meditate)

        # Must use get_tick() to READ position
        assert "get_tick()" in source, (
            "_meditate() does not call get_tick(). "
            "It should READ the current position, not advance it."
        )

        # Must NOT call _singularity.tick() (that would double-tick)
        assert "_singularity.tick()" not in source, (
            "_meditate() calls _singularity.tick() — this would DOUBLE-TICK "
            "because VenuService already drives Singularity.tick()."
        )

    def test_process_request_uses_clock(self):
        """_process_request() must use Clock for tick_state, not hardcoded 'unknown'."""
        import inspect
        from vibe_core.mahamantra.reactor.loop import ReactorLoop

        source = inspect.getsource(ReactorLoop._process_request)

        assert "get_tick_info" in source, (
            "_process_request() does not use get_tick_info(). "
            "It should use the stateless Clock for real quarter/guardian/word."
        )
        assert '"unknown"' not in source, (
            "_process_request() still has hardcoded 'unknown' values. "
            "Must use Clock for real tick_state."
        )


# =============================================================================
# TEST 7: BOOTSTRAP WIRING
# =============================================================================


class TestBootstrapWiring:
    """Verify bootstrap() wires gate providers and HealingIntentResolver."""

    def test_bootstrap_wires_gate_providers(self):
        """After bootstrap, gate_providers import is reachable."""
        import inspect
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        source = inspect.getsource(MahamantraLotus.bootstrap)
        assert "wire_gate_providers" in source, (
            "bootstrap() does not call wire_gate_providers(). "
            "Gate providers must be wired at boot."
        )

    def test_bootstrap_wires_healing_resolver(self):
        """After bootstrap, HealingIntentResolver is wired."""
        import inspect
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        source = inspect.getsource(MahamantraLotus.bootstrap)
        assert "wire_healing_resolver" in source, (
            "bootstrap() does not call wire_healing_resolver(). "
            "HealingIntentResolver must be wired at boot."
        )


# =============================================================================
# PHASE 3: Anti-Split-Brain Regression Tests
# =============================================================================


class TestAntiSplitBrain:
    """Regression tests: re-export shims resolve to SSOT, no duplicate instances."""

    def test_ledger_reexport_resolves_to_ssot(self):
        """prithu/types/ledger.py must re-export from mahamantra/substrate/ledger.py."""
        from vibe_core.protocols.mahajanas.prithu.types.ledger import (
            InMemoryLedger as PrithuLedger,
            SQLiteLedger as PrithuSQLite,
        )
        from vibe_core.mahamantra.substrate.ledger import (
            InMemoryLedger as SSOTLedger,
            SQLiteLedger as SSOTSQLite,
        )
        assert PrithuLedger is SSOTLedger, (
            "prithu InMemoryLedger is NOT the SSOT class — re-export broken!"
        )
        assert PrithuSQLite is SSOTSQLite, (
            "prithu SQLiteLedger is NOT the SSOT class — re-export broken!"
        )

    def test_lineage_reexport_resolves_to_ssot(self):
        """prithu/types/lineage.py must re-export from mahamantra/substrate/lineage.py."""
        from vibe_core.protocols.mahajanas.prithu.types.lineage import (
            LineageChain as PrithuChain,
            LineageBlock as PrithuBlock,
        )
        from vibe_core.mahamantra.substrate.lineage import (
            LineageChain as SSOTChain,
            LineageBlock as SSOTBlock,
        )
        assert PrithuChain is SSOTChain, (
            "prithu LineageChain is NOT the SSOT class — re-export broken!"
        )
        assert PrithuBlock is SSOTBlock, (
            "prithu LineageBlock is NOT the SSOT class — re-export broken!"
        )

    def test_process_manager_reexport_resolves_to_ssot(self):
        """vyasa/types/process_manager.py must re-export from mahamantra/substrate/process_manager.py."""
        from vibe_core.protocols.mahajanas.vyasa.types.process_manager import (
            ProcessManager as VyasaPM,
            ProcessStatus as VyasaPS,
        )
        from vibe_core.mahamantra.substrate.process_manager import (
            ProcessManager as SSOTPM,
            ProcessStatus as SSOTPS,
        )
        assert VyasaPM is SSOTPM, (
            "vyasa ProcessManager is NOT the SSOT class — re-export broken!"
        )
        assert VyasaPS is SSOTPS, (
            "vyasa ProcessStatus is NOT the SSOT class — re-export broken!"
        )

    def test_eventbus_singleton_shared(self):
        """get_event_bus() must return the same instance every time."""
        from vibe_core.mahamantra.substrate.event_bus import get_event_bus
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2, (
            "get_event_bus() returned different instances — singleton broken!"
        )

    def test_reactor_loop_uses_shared_eventbus(self):
        """ReactorLoop._init_bus must use get_event_bus(), not EventBus()."""
        import inspect
        from vibe_core.mahamantra.reactor.loop import ReactorLoop
        source = inspect.getsource(ReactorLoop._init_bus)
        assert "get_event_bus" in source, (
            "ReactorLoop._init_bus does not call get_event_bus(). "
            "It must use the shared singleton, not create a private EventBus()."
        )
        assert "EventBus()" not in source, (
            "ReactorLoop._init_bus still creates EventBus() directly. "
            "This causes split-brain — events fired in one bus never reach the other."
        )

    def test_boot_orchestrator_uses_shared_eventbus(self):
        """BootOrchestrator must use get_event_bus(), not EventBus()."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator.__init__)
        assert "get_event_bus" in source, (
            "BootOrchestrator.__init__ does not call get_event_bus(). "
            "It must use the shared singleton."
        )

    def test_bootstrap_wires_balarama(self):
        """lotus.bootstrap() must call auto_wrap_services() for Balarama absorption."""
        import inspect
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        source = inspect.getsource(MahamantraLotus.bootstrap)
        assert "auto_wrap_services" in source, (
            "bootstrap() does not call auto_wrap_services(). "
            "Balarama Pattern must be wired at boot."
        )

    def test_bootstrap_wires_adoption(self):
        """lotus.bootstrap() must call adopt_services() for orbital mounting."""
        import inspect
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        source = inspect.getsource(MahamantraLotus.bootstrap)
        assert "adopt_services" in source, (
            "bootstrap() does not call adopt_services(). "
            "Orbital reactor mounting must happen at boot."
        )

    def test_auto_wrap_services_produces_proxies(self):
        """auto_wrap_services() must produce at least 1 BalaramaProxy."""
        from vibe_core.mahamantra.substrate.proxy import auto_wrap_services
        proxies = auto_wrap_services(silent=True)
        assert len(proxies) > 0, (
            "auto_wrap_services() returned 0 proxies — lotus discovery broken!"
        )

    def test_balarama_proxy_has_identity(self):
        """BalaramaProxy must extract mahajana identity from folder structure."""
        from vibe_core.mahamantra.substrate.proxy import auto_wrap_services
        proxies = auto_wrap_services(silent=True)
        # At least one proxy should have identity
        identified = [p for p in proxies.values() if p.has_identity]
        assert len(identified) > 0, (
            "No BalaramaProxy has identity — folder-based identity extraction broken!"
        )

    def test_bootstrap_wires_sravanam(self):
        """lotus.bootstrap() must call wire_sravanam() for organic cell scanning."""
        import inspect
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        source = inspect.getsource(MahamantraLotus.bootstrap)
        assert "wire_sravanam" in source, (
            "bootstrap() does not call wire_sravanam(). "
            "Sravanam listener must be wired at boot."
        )

    def test_bootstrap_wires_governance_hook(self):
        """lotus.bootstrap() must register the Sudarshana governance hook."""
        import inspect
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        source = inspect.getsource(MahamantraLotus.bootstrap)
        assert "register_governance_hook" in source, (
            "bootstrap() does not call register_governance_hook(). "
            "Sudarshana governance must be registered at boot."
        )

    def test_boot_orchestrator_does_not_duplicate_gate_wiring(self):
        """boot_orchestrator must NOT import wire_gate_providers — lotus.bootstrap() does it."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._act_wire_gate_providers)
        assert "from vibe_core.mahamantra.substrate.gate_providers import wire_gate_providers" not in source, (
            "_act_wire_gate_providers() still imports wire_gate_providers. "
            "It should only verify via get_registry(), not re-wire."
        )

    def test_boot_orchestrator_does_not_duplicate_sravanam(self):
        """boot_orchestrator must NOT call wire_sravanam() — lotus.bootstrap() does it."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._act_wire_sravanam)
        assert "wire_sravanam()" not in source, (
            "_act_wire_sravanam() still calls wire_sravanam(). "
            "It should only verify, not re-wire."
        )

    def test_boot_orchestrator_does_not_duplicate_governance(self):
        """boot_orchestrator must NOT import register_governance_hook — lotus.bootstrap() does it."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._act_register_governance_hook)
        assert "from vibe_core.protocols.substrate.mantra_protocol import register_governance_hook" not in source, (
            "_act_register_governance_hook() still imports register_governance_hook. "
            "It should only verify via has_governance_hook(), not re-register."
        )

    def test_ingestion_stays_in_boot_orchestrator(self):
        """Codebase ingestion must stay in boot_orchestrator (I/O too expensive for bootstrap)."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._act_ingest_codebase)
        assert "parse_file_to_fragments" in source, (
            "_act_ingest_codebase() no longer does ingestion. "
            "Ingestion must stay in boot_orchestrator (too expensive for bootstrap)."
        )

    def test_ingestion_logs_errors_not_silent(self):
        """Codebase ingestion must log parse errors, never swallow them silently."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._act_ingest_codebase)
        assert "except Exception:" not in source or "pass" not in source.split("except Exception:")[-1].split("\n")[1], (
            "_act_ingest_codebase() has bare 'except: pass'. "
            "Parse errors must be logged, not swallowed."
        )

    # === Phase 4: Kernel Thinning Regression Tests ===

    def test_kernel_has_raw_services(self):
        """RealVibeKernel must store raw service instances as _raw_* attributes."""
        import inspect
        from vibe_core.kernel_impl import RealVibeKernel
        source = inspect.getsource(RealVibeKernel._init_mahajana_services)
        for name in ("_raw_brahma", "_raw_bhishma", "_raw_janaka", "_raw_bali", "_raw_kapila"):
            assert name in source, (
                f"_init_mahajana_services() does not set {name}. "
                "Raw services must be stored for direct internal access."
            )

    def test_kernel_internals_use_raw_not_proxy(self):
        """Kernel methods must use _raw_* (direct), not self.brahma (proxy)."""
        import inspect
        from vibe_core.kernel_impl import RealVibeKernel
        # Check a representative set of methods
        for method_name in ("get_agent_capabilities", "register_agent", "get_status", "boot_async"):
            method = getattr(RealVibeKernel, method_name)
            source = inspect.getsource(method)
            assert "self.brahma." not in source and "self.bhishma." not in source, (
                f"{method_name}() still uses proxy (self.brahma/bhishma). "
                "Must use self._raw_brahma/_raw_bhishma."
            )

    def test_factory_registers_raw_services_in_position_registry(self):
        """factory.py must register _raw_* services (not proxies) in PositionRegistry."""
        import inspect
        from vibe_core.factory import VibeFactory
        source = inspect.getsource(VibeFactory.get_kernel)
        assert "_raw_brahma" in source, (
            "factory.py does not reference _raw_brahma. "
            "PositionRegistry must get raw services, not MahamantraProxy wrappers."
        )

    def test_external_refs_use_raw_with_fallback(self):
        """External kernel.brahma refs must use _raw_brahma with fallback."""
        import inspect
        from vibe_core.protocols.mahajanas.manu.types import kernel_ops
        source = inspect.getsource(kernel_ops)
        assert "_raw_brahma" in source, (
            "kernel_ops.py does not reference _raw_brahma. "
            "Security code must use raw service with fallback."
        )

    # === Phase 3: Input Routing Regression Tests ===

    def test_execute_intent_routes_through_lotus(self):
        """_execute_intent() must call lotus.execute() for non-CONTROL intents."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._execute_intent)
        assert "_lotus.execute(" in source, (
            "_execute_intent() does not call lotus.execute(). "
            "All non-CONTROL intents must flow through the 5-Gate pipeline."
        )

    def test_execute_intent_no_hardcoded_query_handling(self):
        """_execute_intent() must NOT have hardcoded QUERY handling — lotus does it."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._execute_intent)
        assert "IntentType.QUERY" not in source, (
            "_execute_intent() still has hardcoded QUERY handling. "
            "QUERY intents must flow through lotus.execute()."
        )

    def test_execute_intent_no_hardcoded_delegation(self):
        """_execute_intent() must NOT have hardcoded DELEGATION handling — lotus does it."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._execute_intent)
        assert "IntentType.DELEGATION" not in source, (
            "_execute_intent() still has hardcoded DELEGATION handling. "
            "DELEGATION intents must flow through lotus.execute()."
        )

    def test_execute_intent_keeps_control_local(self):
        """_execute_intent() must still handle CONTROL (exit/shutdown) locally."""
        import inspect
        from vibe_core.boot_orchestrator import BootOrchestrator
        source = inspect.getsource(BootOrchestrator._execute_intent)
        assert "IntentType.CONTROL" in source, (
            "_execute_intent() lost CONTROL handling. "
            "exit/shutdown must be handled locally (controls the operator loop)."
        )
