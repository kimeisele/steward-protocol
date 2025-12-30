"""
TEST: Kernel Concurrency - Multi-Agent Thread Safety
=====================================================
Target: vibe_core/kernel_impl.py
Standard: GAD-5000 (Concurrency Hardening)

Tests verify:
1. Kernel can handle concurrent agent operations
2. Ledger operations are thread-safe
3. Scheduler can handle concurrent task submissions
4. Capability registry is thread-safe
5. No deadlocks under high contention scenarios
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.ledger import InMemoryLedger
from vibe_core.scheduling import InMemoryScheduler
from vibe_core.scheduling.task import DispatchTask


class TestLedgerConcurrency:
    """Test ledger thread safety."""

    def test_concurrent_event_recording(self):
        """Recording events from multiple threads shouldn't lose data."""
        ledger = InMemoryLedger()
        num_threads = 10
        events_per_thread = 100

        def record_events(thread_id: int):
            for i in range(events_per_thread):
                ledger.record_event(
                    event_type="TEST_EVENT",
                    agent_id=f"agent_{thread_id}",
                    details={"index": i},
                )

        with ThreadPoolExecutor(max_workers=num_threads) as pool:
            list(pool.map(record_events, range(num_threads)))

        total_events = len(ledger.get_all_events())
        expected = num_threads * events_per_thread
        assert total_events == expected

    def test_concurrent_event_reading(self):
        """Reading events while writing shouldn't cause errors."""
        ledger = InMemoryLedger()
        errors: List[Exception] = []
        lock = threading.Lock()

        # Pre-populate
        for i in range(100):
            ledger.record_event("INIT_EVENT", "init", {"i": i})

        def write_events():
            for i in range(50):
                try:
                    ledger.record_event("WRITE_EVENT", "writer", {"i": i})
                except Exception as e:
                    with lock:
                        errors.append(e)

        def read_events():
            for _ in range(50):
                try:
                    _ = ledger.get_all_events()
                except Exception as e:
                    with lock:
                        errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = []
            for i in range(10):
                if i % 2 == 0:
                    futures.append(pool.submit(write_events))
                else:
                    futures.append(pool.submit(read_events))

            for f in futures:
                f.result()

        assert len(errors) == 0


class TestSchedulerConcurrency:
    """Test scheduler thread safety."""

    def test_concurrent_task_submission(self):
        """Submitting tasks from multiple threads shouldn't lose any."""
        scheduler = InMemoryScheduler()
        num_tasks = 100

        def submit_task_fn(i: int):
            task = DispatchTask(
                agent_id=f"agent_{i % 10}",
                payload={"operation": f"op_{i}"},
            )
            scheduler.submit_task(task)

        with ThreadPoolExecutor(max_workers=20) as pool:
            list(pool.map(submit_task_fn, range(num_tasks)))

        # Count tasks in scheduler via queue status
        status = scheduler.get_queue_status()
        assert status["queue_length"] == num_tasks

    def test_concurrent_task_retrieval(self):
        """Retrieving tasks from multiple threads should be safe."""
        scheduler = InMemoryScheduler()

        # Pre-populate tasks
        for i in range(50):
            task = DispatchTask(agent_id="test", payload={"i": i})
            scheduler.submit_task(task)

        retrieved: List[str] = []
        lock = threading.Lock()

        def get_next():
            task = scheduler.next_task()
            if task:
                with lock:
                    retrieved.append(task.task_id)

        with ThreadPoolExecutor(max_workers=20) as pool:
            list(pool.map(lambda _: get_next(), range(100)))

        # Should have retrieved all 50 tasks (some threads get None)
        assert len(retrieved) == 50


class TestKernelBootConcurrency:
    """Test kernel boot under concurrent access."""

    def test_kernel_event_bus_concurrent_access(self):
        """Kernel's event bus should handle concurrent subscriptions."""
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        subscriptions: List[str] = []
        lock = threading.Lock()

        def subscribe_handler(i: int):
            def handler(event):
                pass

            sub_id = kernel._event_bus.subscribe(handler, "TEST_EVENT")
            with lock:
                subscriptions.append(sub_id)

        with ThreadPoolExecutor(max_workers=10) as pool:
            list(pool.map(subscribe_handler, range(20)))

        assert len(subscriptions) == 20


class TestCapabilityRegistryConcurrency:
    """Test capability registry thread safety."""

    def test_concurrent_capability_registration(self):
        """Registering capabilities from multiple threads should be safe."""
        from vibe_core.capability_registry import CapabilityRegistry
        from vibe_core.ledger import InMemoryLedger

        ledger = InMemoryLedger()
        registry = CapabilityRegistry(ledger)
        errors: List[Exception] = []
        lock = threading.Lock()

        def register_capability(i: int):
            try:
                registry.register_agent(
                    agent_id=f"agent_{i}",
                    capabilities=[f"cap_{i % 5}"],
                )
            except Exception as e:
                with lock:
                    errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as pool:
            list(pool.map(register_capability, range(50)))

        assert len(errors) == 0

    def test_concurrent_capability_check(self):
        """Checking capabilities under concurrent load should be safe."""
        from vibe_core.capability_registry import CapabilityRegistry
        from vibe_core.ledger import InMemoryLedger

        ledger = InMemoryLedger()
        registry = CapabilityRegistry(ledger)

        # Pre-register some capabilities
        for i in range(10):
            registry.register_agent(f"agent_{i}", [f"cap_{i}"])

        results: List[bool] = []
        lock = threading.Lock()

        def check_capability():
            result = registry.has_capability("agent_0", "cap_0")
            with lock:
                results.append(result)

        with ThreadPoolExecutor(max_workers=20) as pool:
            list(pool.map(lambda _: check_capability(), range(100)))

        assert len(results) == 100
        assert all(results)  # All should find the capability


class TestAsyncEventLoopConcurrency:
    """Test async event loop handling with threading."""

    @pytest.mark.asyncio
    async def test_event_bus_from_multiple_coroutines(self):
        """Multiple coroutines emitting to event bus concurrently."""
        from vibe_core.event_bus import Event, EventBus

        bus = EventBus(rate_limit_enabled=False)
        received: List[str] = []
        lock = threading.Lock()

        def handler(event):
            with lock:
                received.append(event.agent_id)

        bus.subscribe(handler)

        async def emit_from_coroutine(agent_id: str):
            for i in range(10):
                event = Event(event_type="TEST", agent_id=agent_id, message=f"msg_{i}")
                await bus.emit(event)

        # 5 coroutines, 10 events each
        await asyncio.gather(*[emit_from_coroutine(f"agent_{i}") for i in range(5)])

        assert len(received) == 50


class TestDeadlockPrevention:
    """Test that common deadlock scenarios are avoided."""

    def test_no_deadlock_on_nested_operations(self):
        """Nested kernel operations shouldn't deadlock."""
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        completed = threading.Event()

        def nested_operation():
            # Record event (might acquire locks)
            kernel.ledger.record_event("TEST", "test", {})
            # Another operation while holding potential locks
            kernel.ledger.record_event("TEST2", "test", {})
            completed.set()

        thread = threading.Thread(target=nested_operation)
        thread.start()

        # Wait with timeout - if deadlocked, this will fail
        success = completed.wait(timeout=5.0)
        thread.join(timeout=1.0)

        assert success, "Operation deadlocked"

    def test_no_deadlock_on_concurrent_kernel_access(self):
        """Multiple threads accessing kernel shouldn't deadlock."""
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        completed_count = 0
        lock = threading.Lock()

        def kernel_operation():
            nonlocal completed_count
            # Various kernel operations
            kernel.ledger.record_event("TEST", "test", {})
            _ = kernel.ledger.get_all_events()
            with lock:
                completed_count += 1

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(kernel_operation) for _ in range(20)]
            # Wait with timeout
            for f in futures:
                f.result(timeout=5.0)

        assert completed_count == 20


class TestRaceConditionScenarios:
    """Test specific race condition scenarios."""

    def test_register_agent_while_iterating(self):
        """Modifying agent registry while iterating shouldn't crash."""
        from vibe_core.manifest_registry import InMemoryManifestRegistry
        from vibe_core.protocols.agent import AgentManifest

        registry = InMemoryManifestRegistry()
        errors: List[Exception] = []
        lock = threading.Lock()

        def register_agent(i: int):
            try:
                manifest = AgentManifest(
                    agent_id=f"agent_{i}",
                    name=f"Agent {i}",
                    capabilities=["test"],
                    dependencies=[],
                )
                registry.register(manifest)
            except Exception as e:
                with lock:
                    errors.append(e)

        def iterate_agents():
            try:
                _ = list(registry.list_all())
            except Exception as e:
                with lock:
                    errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = []
            for i in range(30):
                if i % 3 == 0:
                    futures.append(pool.submit(iterate_agents))
                else:
                    futures.append(pool.submit(register_agent, i))

            for f in futures:
                try:
                    f.result(timeout=5.0)
                except Exception:
                    pass

        # Should not have catastrophic failures
        assert len(errors) == 0  # No errors expected with proper implementation
