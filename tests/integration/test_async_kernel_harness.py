"""
OPUS-203 Test Harness: Validates async kernel migration.

This harness tests the CURRENT state (sync kernel) to establish baseline,
and will validate the FUTURE state (async kernel) after migration.

Run: pytest tests/integration/test_async_kernel_harness.py -v

Success Criteria (POST-MIGRATION):
1. MANAS tick count > 10 after 5 seconds
2. EventBus event_count matches emit count
3. No asyncio.run() in tick path (only in deprecated methods)
4. Gateway runs as task (not thread)

Current State (PRE-MIGRATION):
- Tests marked with @pytest.mark.xfail are expected to fail
- These tests document the broken behavior we are fixing
"""

import ast
import asyncio
import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestEventBusAsyncDelivery:
    """Tests for EventBus async event delivery."""

    @pytest.mark.asyncio
    async def test_event_delivery_in_async_context(self):
        """Events emitted in async context reach handlers."""
        from vibe_core.event_bus import Event, EventType, get_event_bus

        # Get fresh bus instance
        bus = get_event_bus()
        received = []

        async def handler(event):
            received.append(event)

        # Subscribe to KERNEL_TICK
        bus.subscribe(handler, EventType.KERNEL_TICK)

        try:
            # Emit in async context (the target state)
            await bus.emit(Event(event_type=EventType.KERNEL_TICK, agent_id="test", message="test"))

            # Handler should have been called
            assert len(received) == 1, f"Expected 1 event, got {len(received)}"
            assert received[0].agent_id == "test"
        finally:
            # Cleanup
            bus.unsubscribe(handler, EventType.KERNEL_TICK)

    @pytest.mark.asyncio
    async def test_multiple_handlers_all_called(self):
        """All subscribed handlers receive the event."""
        from vibe_core.event_bus import Event, EventType, get_event_bus

        bus = get_event_bus()
        calls = {"a": 0, "b": 0, "c": 0}

        async def handler_a(event):
            calls["a"] += 1

        async def handler_b(event):
            calls["b"] += 1

        def handler_c_sync(event):
            calls["c"] += 1

        bus.subscribe(handler_a, EventType.KERNEL_TICK)
        bus.subscribe(handler_b, EventType.KERNEL_TICK)
        bus.subscribe(handler_c_sync, EventType.KERNEL_TICK)

        try:
            await bus.emit(Event(event_type=EventType.KERNEL_TICK, agent_id="test", message="test"))

            assert calls["a"] == 1, "Handler A not called"
            assert calls["b"] == 1, "Handler B not called"
            assert calls["c"] == 1, "Handler C (sync) not called"
        finally:
            bus.unsubscribe(handler_a, EventType.KERNEL_TICK)
            bus.unsubscribe(handler_b, EventType.KERNEL_TICK)
            bus.unsubscribe(handler_c_sync, EventType.KERNEL_TICK)


class TestSyncAsyncBridge:
    """Tests for the sync/async bridge behavior."""

    def test_emit_event_safe_in_sync_context(self):
        """_emit_event_safe works from sync context (current behavior)."""
        from vibe_core.event_bus import Event, EventType, get_event_bus
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel()
        bus = get_event_bus()

        initial_count = bus._event_count

        # Call _emit_event_safe from sync context (simulating tick())
        event = Event(event_type=EventType.KERNEL_TICK, agent_id="kernel", message="test")
        kernel._emit_event_safe(event)

        # Event should be recorded
        assert bus._event_count == initial_count + 1, "Event not counted"

    @pytest.mark.xfail(reason="PRE-MIGRATION: Handlers not called from sync emit")
    def test_async_handler_called_from_sync_emit(self):
        """Async handlers receive events emitted from sync context.

        This test is expected to FAIL in the current architecture.
        It documents the bug that OPUS-203 fixes.
        """
        from vibe_core.event_bus import Event, EventType, get_event_bus
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel()
        bus = get_event_bus()
        received = []

        async def async_handler(event):
            received.append(event)

        bus.subscribe(async_handler, EventType.KERNEL_TICK)

        try:
            # Emit from sync context (current kernel.tick() behavior)
            event = Event(event_type=EventType.KERNEL_TICK, agent_id="kernel", message="test")
            kernel._emit_event_safe(event)

            # Wait a bit for async to settle
            time.sleep(0.1)

            # This SHOULD work but FAILS in current architecture
            assert len(received) == 1, f"Handler not called! Got {len(received)} events"
        finally:
            bus.unsubscribe(async_handler, EventType.KERNEL_TICK)


class TestKernelCodeQuality:
    """Static analysis tests for kernel code."""

    def test_no_asyncio_run_in_tick_async_path(self):
        """Verify tick_async() path has no asyncio.run() calls.

        After migration, tick_async() should use native await,
        not asyncio.run() wrappers.
        """
        kernel_file = PROJECT_ROOT / "vibe_core" / "kernel_impl.py"
        source = kernel_file.read_text()

        # Check if tick_async exists (post-migration)
        if "async def tick_async" not in source:
            pytest.skip("tick_async() not yet implemented")

        tree = ast.parse(source)

        # Find tick_async method
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "tick_async":
                # Check for asyncio.run calls within
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func = child.func
                        # Check for asyncio.run()
                        if isinstance(func, ast.Attribute) and func.attr == "run":
                            if isinstance(func.value, ast.Name) and func.value.id == "asyncio":
                                pytest.fail(f"Found asyncio.run() in tick_async at line {child.lineno}")

    def test_emit_event_safe_usage_count(self):
        """Count _emit_event_safe usages - should decrease over migration."""
        kernel_file = PROJECT_ROOT / "vibe_core" / "kernel_impl.py"
        source = kernel_file.read_text()

        count = source.count("_emit_event_safe")

        # Current state: ~3 usages (definition + 2 calls)
        # Post-migration: 1 usage (deprecated definition only)
        assert count >= 1, "_emit_event_safe should exist"

        # Log for migration tracking
        print(f"\n_emit_event_safe usage count: {count}")
        print("  Target: 1 (deprecated definition only)")


class TestMANASIntegration:
    """Integration tests for MANAS tick behavior."""

    @pytest.mark.xfail(reason="PRE-MIGRATION: MANAS tick stuck at 1")
    @pytest.mark.asyncio
    async def test_manas_tick_increments_with_kernel(self):
        """MANAS tick count increases with kernel ticks.

        This test is expected to FAIL until OPUS-203 is implemented.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel()

        # Boot kernel (current sync method)
        kernel.boot()

        try:
            # Run several ticks
            for _ in range(20):
                kernel.tick()
                await asyncio.sleep(0.1)

            # Check MANAS awareness
            awareness_file = PROJECT_ROOT / ".opus_state" / "manas_awareness.json"
            if awareness_file.exists():
                awareness = json.loads(awareness_file.read_text())
                tick_count = awareness.get("tick", 0)

                # After 20 kernel ticks, MANAS should have ticked multiple times
                assert tick_count > 5, f"MANAS tick too low: {tick_count} (expected > 5)"
            else:
                pytest.fail("manas_awareness.json not found")

        finally:
            kernel.shutdown()


class TestGatewayArchitecture:
    """Tests for Gateway thread vs task architecture."""

    def test_gateway_thread_exists_pre_migration(self):
        """Verify Gateway runs as thread (pre-migration state)."""
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel()
        kernel.boot()

        try:
            # Current architecture: Gateway in separate thread
            assert hasattr(kernel, "_gateway_thread"), "Gateway thread attribute missing"
            if kernel._gateway_thread:
                assert kernel._gateway_thread.is_alive(), "Gateway thread not running"
        finally:
            kernel.shutdown()

    @pytest.mark.xfail(reason="PRE-MIGRATION: Gateway is thread, not task")
    @pytest.mark.asyncio
    async def test_gateway_runs_as_task_post_migration(self):
        """Verify Gateway runs as asyncio task (post-migration target).

        This test documents the target architecture.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel()

        # Post-migration: async boot
        if not hasattr(kernel, "boot_async"):
            pytest.skip("boot_async() not yet implemented")

        await kernel.boot_async()

        try:
            # Gateway should be a task, not a thread
            assert hasattr(kernel, "_gateway_task"), "Gateway task attribute missing"
            assert kernel._gateway_task is not None, "Gateway task is None"
            assert not kernel._gateway_task.done(), "Gateway task already done"

            # Thread should not exist or be None
            gateway_thread = getattr(kernel, "_gateway_thread", None)
            assert gateway_thread is None, "Gateway thread still exists"

        finally:
            await kernel.shutdown_async()


# Convenience function to run harness
def run_harness():
    """Run the harness and print summary."""
    import subprocess

    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_harness())
