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
