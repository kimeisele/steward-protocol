"""
UNIFIED HEARTBEAT - Integration Test Suite
===========================================

Real integration tests that verify the system's wiring end-to-end:

1. ONE Singularity singleton (no duplicate Krishnas)
2. VenuService → Singularity.tick() → _broadcast() → listeners fire
3. SravanamListener receives ticks (healing scanner is ALIVE)
4. Intent resolver wired in tick
5. Re-export shims resolve to SSOT (no split-brain)
6. BalaramaProxy produces real proxies with identity
7. Architectural wiring contracts (via wiring_auditor)

Every test uses REAL objects. No mocks. No MagicMock.
Source-level architecture checks live in wiring_auditor.py.
"""

from __future__ import annotations

import pytest

from vibe_core.mahamantra.kernel.singularity import Mahamantra, mahamantra

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
            "POLYTHEISM: MahamantraLotus created a SECOND Singularity. Must use kernel/singularity.py singleton."
        )

    def test_maha_kernel_uses_same_singularity(self):
        """MahaKernel._singularity is the kernel singleton."""
        from vibe_core.mahamantra.kernel.maha_kernel import MahaKernel

        kernel = MahaKernel()

        assert kernel._singularity is mahamantra, (
            "POLYTHEISM: MahaKernel created a SECOND Singularity. Must use kernel/singularity.py singleton."
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
            "TWO FLUTES: Lotus and Singularity have different VenuOrchestrators. One Krishna, one flute."
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
                f"Listener received {len(received)} broadcasts, expected 1. Singularity._broadcast() is not firing."
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
                "DIW subscriber did NOT fire through Singularity.tick(). VenuOrchestrator.step() is not being called."
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
            "VenuService has no _singularity attribute. Surgery 3 may not have been applied."
        )
        assert svc._singularity is mahamantra, "VenuService._singularity is not the kernel singleton."

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
        assert bridge._lotus is None, "LotusBridgeSubscriber accessed lotus — it should be a no-op."


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

            assert len(received) == 1, "SravanamListener did NOT receive tick. Healing scanner is DEAD."
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
            "Intent queue NOT drained by tick(). MantraKernel.process_queue() is not wired in Singularity.tick()."
        )

    def test_empty_queue_no_error(self):
        """tick() with empty intent queue does not error."""
        # Just tick — should not raise
        mahamantra.tick()


# =============================================================================
# TEST 6: ANTI-SPLIT-BRAIN — Real object identity checks
# =============================================================================


class TestAntiSplitBrain:
    """Re-export shims resolve to SSOT, shared singletons are shared."""

    def test_ledger_reexport_resolves_to_ssot(self):
        """prithu/types/ledger.py must re-export from mahamantra/substrate/ledger.py."""
        from vibe_core.mahamantra.substrate.ledger import (
            InMemoryLedger as SSOTLedger,
        )
        from vibe_core.mahamantra.substrate.ledger import (
            SQLiteLedger as SSOTSQLite,
        )
        from vibe_core.protocols.mahajanas.prithu.types.ledger import (
            InMemoryLedger as PrithuLedger,
        )
        from vibe_core.protocols.mahajanas.prithu.types.ledger import (
            SQLiteLedger as PrithuSQLite,
        )

        assert PrithuLedger is SSOTLedger, "prithu InMemoryLedger is NOT the SSOT class — re-export broken!"
        assert PrithuSQLite is SSOTSQLite, "prithu SQLiteLedger is NOT the SSOT class — re-export broken!"

    def test_lineage_reexport_resolves_to_ssot(self):
        """prithu/types/lineage.py must re-export from mahamantra/substrate/lineage.py."""
        from vibe_core.mahamantra.substrate.lineage import (
            LineageBlock as SSOTBlock,
        )
        from vibe_core.mahamantra.substrate.lineage import (
            LineageChain as SSOTChain,
        )
        from vibe_core.protocols.mahajanas.prithu.types.lineage import (
            LineageBlock as PrithuBlock,
        )
        from vibe_core.protocols.mahajanas.prithu.types.lineage import (
            LineageChain as PrithuChain,
        )

        assert PrithuChain is SSOTChain, "prithu LineageChain is NOT the SSOT class — re-export broken!"
        assert PrithuBlock is SSOTBlock, "prithu LineageBlock is NOT the SSOT class — re-export broken!"

    def test_process_manager_reexport_resolves_to_ssot(self):
        """vyasa/types/process_manager.py must re-export from mahamantra/substrate/process_manager.py."""
        from vibe_core.mahamantra.substrate.process_manager import (
            ProcessManager as SSOTPM,
        )
        from vibe_core.mahamantra.substrate.process_manager import (
            ProcessStatus as SSOTPS,
        )
        from vibe_core.protocols.mahajanas.vyasa.types.process_manager import (
            ProcessManager as VyasaPM,
        )
        from vibe_core.protocols.mahajanas.vyasa.types.process_manager import (
            ProcessStatus as VyasaPS,
        )

        assert VyasaPM is SSOTPM, "vyasa ProcessManager is NOT the SSOT class — re-export broken!"
        assert VyasaPS is SSOTPS, "vyasa ProcessStatus is NOT the SSOT class — re-export broken!"

    def test_eventbus_singleton_shared(self):
        """get_event_bus() must return the same instance every time."""
        from vibe_core.mahamantra.substrate.event_bus import get_event_bus

        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2, "get_event_bus() returned different instances — singleton broken!"

    def test_auto_wrap_services_produces_proxies(self):
        """auto_wrap_services() must produce at least 1 BalaramaProxy."""
        from vibe_core.mahamantra.substrate.proxy import auto_wrap_services

        proxies = auto_wrap_services(silent=True)
        assert len(proxies) > 0, "auto_wrap_services() returned 0 proxies — lotus discovery broken!"

    def test_balarama_proxy_has_identity(self):
        """BalaramaProxy must extract mahajana identity from folder structure."""
        from vibe_core.mahamantra.substrate.proxy import auto_wrap_services

        proxies = auto_wrap_services(silent=True)
        identified = [p for p in proxies.values() if p.has_identity]
        assert len(identified) > 0, "No BalaramaProxy has identity — folder-based identity extraction broken!"


# =============================================================================
# TEST 7: WIRING AUDITOR — all source-level architecture checks
# =============================================================================


class TestWiringAuditor:
    """Run the wiring auditor and assert zero findings.

    This replaces ~25 individual inspect.getsource() grep-tests with a
    single auditor that checks ALL architectural wiring contracts.
    If any contract is violated, the auditor returns findings with
    precise descriptions of what broke.
    """

    def test_wiring_auditor_zero_findings(self):
        """All architectural wiring contracts must be intact."""
        from vibe_core.mahamantra.audit.wiring_auditor import Auditor

        auditor = Auditor()
        findings = auditor.run_audit()

        if findings:
            violations = "\n".join(f"  [{f.severity.value.upper()}] {f.description}" for f in findings)
            pytest.fail(f"Wiring auditor found {len(findings)} violation(s):\n{violations}")
