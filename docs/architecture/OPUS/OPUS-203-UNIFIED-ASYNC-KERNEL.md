# OPUS-203: Unified Async Kernel

**Status**: APPROVED
**Date**: 2025-12-22
**Author**: Claude (Opus 4.5)
**Supersedes**: N/A
**Related**: OPUS-174 (Biorhythm), OPUS-091 (Heartbeat), OPUS-108 (Autonomy Loop)

---

## Executive Summary

The current kernel architecture mixes synchronous and asynchronous execution models without a unified concurrency strategy. This causes:
- Events emitted but never delivered (MANAS tick stuck at 1)
- `asyncio.run()` workarounds that create ephemeral event loops
- Thread/async boundary violations between kernel, plugins, and gateway

**Decision**: Migrate to a fully async kernel with a single event loop.

---

## Problem Statement

### Current Architecture (Frankenstein)

```
MAIN THREAD (sync)              GATEWAY THREAD (async)
==================              ====================
boot_kernel.py:                 kernel_impl.py:
  while True:                     loop = asyncio.new_event_loop()
    kernel.tick()                 loop.run_forever()
    time.sleep(0.1)  <-- BLOCKS

kernel.tick():
  _emit_event_safe():
    asyncio.run(bus.emit())  <-- EPHEMERAL LOOP (created, destroyed)

EventBus.emit() (async):
  await asyncio.gather(*handlers)  <-- handlers registered at boot
```

### Symptoms

1. **MANAS tick = 1**: `_on_event()` handler called once at boot, never again
2. **Events emitted, not delivered**: `asyncio.run()` creates temporary loop
3. **Thread-safety violations**: Gateway in separate thread, shared EventBus
4. **Inconsistent patterns**: 47 occurrences of `asyncio.run/get_event_loop/new_event_loop`

### Root Cause

No unified concurrency model. The system evolved incrementally:
1. Started as sync kernel
2. Added async EventBus
3. Added threaded Gateway
4. Added async handlers in plugins
5. Added `asyncio.run()` bridges everywhere

---

## Decision

### Option A: Unified Async Kernel (CHOSEN)

The kernel runs in a single asyncio event loop. All components are tasks in this loop.

```python
# boot_kernel.py (NEW)
async def main():
    kernel = RealVibeKernel()
    await kernel.boot_async()
    await kernel.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

```python
# kernel_impl.py (MODIFIED)
async def run_forever(self):
    """Main kernel loop - runs until shutdown."""
    while self._status == KernelStatus.RUNNING:
        await self.tick_async()
        await asyncio.sleep(0.1)

async def tick_async(self):
    """Async tick - native event emission."""
    # ... existing tick logic ...
    await self._event_bus.emit(event)  # Direct await, no wrapper
```

### Rejected Alternatives

**Option B: Sync Event Emission**
- Make EventBus sync-only
- Loses async handler capability
- Rejected: Limits plugin architecture

**Option C: Thread Boundaries (BHARAT-style)**
- Kernel sync, Gateway async with queue IPC
- Clean separation but high complexity
- Rejected: Over-engineering for current needs

---

## Migration Plan

### Phase 0: Harness (Validation Infrastructure)

**File**: `tests/integration/test_async_kernel_harness.py`

```python
"""
OPUS-203 Test Harness: Validates async kernel migration.

Run: pytest tests/integration/test_async_kernel_harness.py -v

Success Criteria:
1. MANAS tick count > 10 after 5 seconds
2. EventBus event_count matches emit count
3. No asyncio.run() in tick path
4. Gateway runs as task (not thread)
"""

import asyncio
import pytest
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.event_bus import get_event_bus

class TestAsyncKernelHarness:
    """Harness for OPUS-203 async kernel migration."""

    @pytest.mark.asyncio
    async def test_event_delivery_in_async_context(self):
        """Events emitted in async context reach handlers."""
        bus = get_event_bus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(handler, "KERNEL_TICK")

        # Emit in async context (the target state)
        from vibe_core.event_bus import Event, EventType
        await bus.emit(Event(event_type=EventType.KERNEL_TICK, agent_id="test"))

        assert len(received) == 1, "Event not delivered in async context"

    @pytest.mark.asyncio
    async def test_manas_tick_increments(self):
        """MANAS tick count increases with kernel ticks."""
        # This test validates the FIX works
        kernel = RealVibeKernel()
        await kernel.boot_async()  # NEW: async boot

        # Run 50 ticks (5 seconds at 100ms interval)
        for _ in range(50):
            await kernel.tick_async()  # NEW: async tick
            await asyncio.sleep(0.1)

        # Check MANAS awareness
        awareness_file = Path(".opus_state/manas_awareness.json")
        if awareness_file.exists():
            awareness = json.loads(awareness_file.read_text())
            assert awareness.get("tick", 0) > 10, f"MANAS tick too low: {awareness}"

        await kernel.shutdown_async()

    def test_no_asyncio_run_in_tick_path(self):
        """Verify tick() path has no asyncio.run() calls."""
        import ast
        from pathlib import Path

        kernel_file = Path("vibe_core/kernel_impl.py")
        tree = ast.parse(kernel_file.read_text())

        # Find tick method
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "tick_async":
                # Check for asyncio.run calls
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if hasattr(child.func, "attr") and child.func.attr == "run":
                            if hasattr(child.func.value, "id") and child.func.value.id == "asyncio":
                                pytest.fail("Found asyncio.run() in tick_async path")

    @pytest.mark.asyncio
    async def test_gateway_runs_as_task(self):
        """Gateway runs as asyncio task, not thread."""
        kernel = RealVibeKernel()
        await kernel.boot_async()

        # Check gateway is a task, not a thread
        assert kernel._gateway_task is not None, "Gateway not running as task"
        assert not hasattr(kernel, "_gateway_thread") or kernel._gateway_thread is None

        await kernel.shutdown_async()
```

### Phase 1: Async Boot Entry Point

**File**: `scripts/boot_kernel.py` (MODIFIED)

```python
#!/usr/bin/env python3
"""
VIBE KERNEL BOOT LOADER - Async Native (OPUS-203)
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("BOOT_LOADER")
_kernel = None

async def main():
    global _kernel
    from vibe_core.kernel_impl import RealVibeKernel

    logger.info("Phase 1: Instantiating Kernel...")
    kernel = RealVibeKernel(ledger_path=PROJECT_ROOT / "data" / "vibe_ledger.db")
    _kernel = kernel

    logger.info("Phase 2: Async Boot...")
    await kernel.boot_async()

    logger.info("Phase 3: Running Forever...")
    await kernel.run_forever()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
```

### Phase 2: Kernel Async Methods

**File**: `vibe_core/kernel_impl.py` (ADDITIONS)

```python
async def boot_async(self) -> None:
    """Async boot - same as boot() but gateway is a task."""
    # ... existing boot logic ...

    # Gateway as task instead of thread
    self._gateway_task = asyncio.create_task(self._run_gateway_async())

    self._status = KernelStatus.RUNNING

async def run_forever(self) -> None:
    """Main kernel loop."""
    logger.info("Entering async kernel loop...")
    try:
        while self._status == KernelStatus.RUNNING:
            await self.tick_async()
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        logger.info("Kernel loop cancelled")
    finally:
        await self.shutdown_async()

async def tick_async(self) -> None:
    """Async tick - native event emission."""
    self.enforce_entropy_limits()

    if self._status != KernelStatus.RUNNING:
        return

    for plugin in self._plugins:
        plugin.on_tick_pre(self)

    task = self._scheduler.next_task()

    if not task:
        if time.time() - self._last_pulse_time >= 5.0:
            self._pulse()
            self._last_pulse_time = time.time()
            # Direct await - no wrapper needed
            await self._event_bus.emit(Event(
                event_type=EventType.KERNEL_TICK,
                agent_id="kernel",
                message="Kernel idle tick (biorhythm)"
            ))
        return

    # ... rest of tick logic with await instead of asyncio.run() ...

async def _run_gateway_async(self) -> None:
    """Gateway as async task (not thread)."""
    try:
        await self.gateway.start()
    except Exception as e:
        logger.error(f"Gateway error: {e}")

async def shutdown_async(self) -> None:
    """Async shutdown."""
    self._status = KernelStatus.STOPPING
    if self._gateway_task:
        self._gateway_task.cancel()
        try:
            await self._gateway_task
        except asyncio.CancelledError:
            pass
    self._status = KernelStatus.STOPPED
```

### Phase 3: Deprecate Sync Methods

```python
def tick(self) -> None:
    """DEPRECATED: Use tick_async() in async context."""
    import warnings
    warnings.warn("tick() is deprecated, use tick_async()", DeprecationWarning)
    # Fallback for legacy callers
    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(self.tick_async())
    except RuntimeError:
        asyncio.run(self.tick_async())

def boot(self) -> None:
    """DEPRECATED: Use boot_async() in async context."""
    import warnings
    warnings.warn("boot() is deprecated, use boot_async()", DeprecationWarning)
    asyncio.run(self.boot_async())
```

### Phase 4: Remove _emit_event_safe()

Once all callers are async, remove the helper:

```python
# DELETE THIS METHOD after migration complete
def _emit_event_safe(self, event: Event) -> None:
    """OPUS-174: DEPRECATED - use await self._event_bus.emit() directly."""
    raise DeprecationError("Use await self._event_bus.emit() in async context")
```

---

## Validation Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Harness passes | `pytest tests/integration/test_async_kernel_harness.py -v` | All green |
| MANAS tick > 10 | `cat .opus_state/manas_awareness.json` | `"tick": 50+` |
| No asyncio.run in tick | `grep -n "asyncio.run" vibe_core/kernel_impl.py` | Only in deprecated methods |
| Gateway is task | Check `kernel._gateway_task` | Not None |
| Gateway not thread | Check `kernel._gateway_thread` | None or not exists |

---

## Rollback Plan

If issues arise, revert to sync boot:

```bash
git checkout HEAD~1 -- scripts/boot_kernel.py vibe_core/kernel_impl.py
```

The deprecated sync methods remain functional as fallback.

---

## Timeline

This document defines WHAT, not WHEN. Implementation requires:
1. Create harness (Phase 0)
2. Verify harness fails with current code
3. Implement async methods (Phase 1-2)
4. Verify harness passes
5. Deprecate sync methods (Phase 3)
6. Remove _emit_event_safe after burn-in (Phase 4)

---

## Appendix: Files Modified

| File | Change |
|------|--------|
| `scripts/boot_kernel.py` | Async entry point |
| `vibe_core/kernel_impl.py` | Add async methods, deprecate sync |
| `vibe_core/event_bus.py` | No changes needed |
| `tests/integration/test_async_kernel_harness.py` | NEW: Validation harness |

---

## Approval

- [x] Architecture: Unified async model selected
- [x] Harness: Validation tests defined
- [x] Migration: Phased approach with rollback
- [ ] Implementation: Pending

**Approved for implementation.**
